// SPDX-License-Identifier: Apache-2.0
import { BufferAttribute } from "three";

// Apply a source-pinned local vertex edit atomically; no building geometry changes.
export function applyVegetationPatch(root, patch, assetSha) {
  if (patch.version !== 1 || patch.base_asset_sha256 !== assetSha)
    throw new Error("Vegetation patch does not match the presentation asset.");
  const target = root.getObjectByName(patch.target_name);
  const translate = Array.isArray(patch.delta_gltf);
  const collapse = Array.isArray(patch.collapse_gltf);
  const vector = translate ? patch.delta_gltf : patch.collapse_gltf;
  if (
    !target ||
    !Array.isArray(patch.positions_gltf) ||
    !patch.positions_gltf.length ||
    translate === collapse ||
    !Array.isArray(vector) ||
    vector.length !== 3 ||
    !vector.every(Number.isFinite) ||
    !(patch.tolerance_m > 0 && patch.tolerance_m <= 0.001)
  )
    throw new Error("Invalid vegetation patch.");
  const expected = patch.positions_gltf;
  if (
    !expected.every(
      (p) => Array.isArray(p) && p.length === 3 && p.every(Number.isFinite),
    )
  )
    throw new Error("Invalid vegetation positions.");
  const lo = [0, 1, 2].map(
    (i) => Math.min(...expected.map((p) => p[i])) - patch.tolerance_m,
  );
  const hi = [0, 1, 2].map(
    (i) => Math.max(...expected.map((p) => p[i])) + patch.tolerance_m,
  );
  const hits = [],
    seen = new Set(),
    tol2 = patch.tolerance_m ** 2;
  target.traverse((mesh) => {
    const pos = mesh.isMesh && mesh.geometry.attributes.position;
    if (!pos) return;
    for (let i = 0; i < pos.count; i++) {
      const point = [pos.getX(i), pos.getY(i), pos.getZ(i)];
      if (point.some((v, k) => v < lo[k] || v > hi[k])) continue;
      const found = expected.findIndex(
        (p) => p.reduce((sum, v, k) => sum + (v - point[k]) ** 2, 0) < tol2,
      );
      if (found >= 0) {
        hits.push([mesh.geometry, pos, i, point]);
        seen.add(found);
      }
    }
  });
  if (hits.length !== patch.expected_matches || seen.size !== expected.length)
    throw new Error(
      `Vegetation patch selection changed (${hits.length} vertices, ${seen.size} positions).`,
    );
  const geometries = new Set();
  for (const [geometry, pos, i, point] of hits) {
    pos.setXYZ(i, ...(collapse ? vector : point.map((v, k) => v + vector[k])));
    pos.needsUpdate = true;
    geometries.add(geometry);
  }
  for (const geometry of geometries) {
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();
  }
  return hits.length;
}

export function applyPilotTreeClearance(root, spec, assetSha, expectedTrees) {
  if (
    spec.version !== 1 ||
    spec.operation !== "pilot-tree-triangle-suppression-v1" ||
    spec.base_asset_sha256 !== assetSha ||
    !Number.isInteger(expectedTrees) ||
    expectedTrees < 1 ||
    spec.suppressed_trees !== expectedTrees ||
    !Array.isArray(spec.meshes) ||
    !spec.meshes.length ||
    new Set(spec.meshes.map(({ name }) => name)).size !== spec.meshes.length
  )
    throw new Error("Invalid pilot tree clearance.");

  const updates = spec.meshes.map(
    ({ group, name, vertices, triangles, spans }) => {
      if (!["vegetation", "understory"].includes(group))
        throw new Error("Invalid pilot tree source group.");
      const mesh = root.getObjectByName(group)?.getObjectByName(name);
      const geo = mesh?.geometry;
      const index = geo?.index;
      if (
        !mesh?.isMesh ||
        geo.groups.length ||
        geo.getAttribute("position")?.count !== vertices ||
        !index ||
        index.count !== triangles * 3 ||
        !Array.isArray(spans) ||
        !spans.length
      )
        throw new Error("Pilot tree clearance source changed.");

      let last = 0;
      let remove = 0;
      for (const span of spans) {
        if (
          !Array.isArray(span) ||
          span.length !== 5 ||
          !span.every(Number.isInteger)
        )
          throw new Error("Invalid pilot tree triangle span.");
        const [a, b, first, middle, end] = span;
        const from = a * 3;
        const to = b * 3;
        if (
          from < last ||
          to <= from ||
          to > index.count ||
          index.getX(from) !== first ||
          index.getX(from + Math.floor((to - from) / 2)) !== middle ||
          index.getX(to - 1) !== end
        )
          throw new Error(
            "Pilot tree clearance spans no longer match the source.",
          );
        remove += to - from;
        last = to;
      }
      if (remove >= index.count)
        throw new Error("Pilot tree clearance would remove a whole mesh.");
      const next = new index.array.constructor(index.count - remove);
      let read = 0;
      let write = 0;
      for (const [a, b] of spans) {
        const kept = index.array.subarray(read, a * 3);
        next.set(kept, write);
        write += kept.length;
        read = b * 3;
      }
      next.set(index.array.subarray(read), write);
      return { geo, replacement: new BufferAttribute(next, 1) };
    },
  );
  for (const { geo, replacement } of updates) geo.setIndex(replacement);
  return expectedTrees;
}

export function applyRegisteredPilotTrees(root, spec, assetSha, expectedTrees) {
  const vector = (value) =>
    Array.isArray(value) && value.length === 3 && value.every(Number.isFinite);
  if (
    spec.version !== 1 ||
    spec.operation !== "registered-pilot-tree-fit-v1" ||
    spec.base_asset_sha256 !== assetSha ||
    !Number.isInteger(expectedTrees) ||
    expectedTrees < 1 ||
    !Array.isArray(spec.trees) ||
    spec.trees.length !== expectedTrees ||
    new Set(spec.trees.map(({ index }) => index)).size !== expectedTrees
  )
    throw new Error("Invalid registered pilot tree recipe.");

  const group = root.getObjectByName("vegetation");
  const selected = new Map();
  const updates = [];
  for (const { origin, target, scale, parts } of spec.trees) {
    if (
      !vector(origin) ||
      !vector(target) ||
      !vector(scale) ||
      scale.some((value) => value <= 0 || value > 3) ||
      !Array.isArray(parts) ||
      parts.length !== 2 ||
      parts[0].name === parts[1].name
    )
      throw new Error("Invalid pilot tree fit.");
    for (const { name, vertices, runs, anchors } of parts) {
      const mesh = group?.getObjectByName(name);
      const geometry = mesh?.geometry;
      const position = geometry?.getAttribute("position");
      const normal = geometry?.getAttribute("normal");
      if (
        !mesh?.isMesh ||
        position?.count !== vertices ||
        normal?.count !== vertices ||
        !Array.isArray(runs) ||
        !runs.length ||
        !Array.isArray(anchors) ||
        anchors.length !== 3
      )
        throw new Error("Registered pilot tree source changed.");
      if (!selected.has(geometry)) selected.set(geometry, new Set());
      const used = selected.get(geometry);
      const local = new Set();
      for (const [start, end] of runs) {
        if (
          !Number.isInteger(start) ||
          !Number.isInteger(end) ||
          start < 0 ||
          start >= end ||
          end > vertices
        )
          throw new Error("Invalid pilot tree vertex run.");
        for (let i = start; i < end; i++) {
          if (used.has(i)) throw new Error("Overlapping pilot tree edits.");
          local.add(i);
          used.add(i);
        }
      }
      for (const [i, ...point] of anchors) {
        if (
          !local.has(i) ||
          !vector(point) ||
          [position.getX(i), position.getY(i), position.getZ(i)].some(
            (value, axis) => Math.abs(value - point[axis]) > 0.001,
          )
        )
          throw new Error("Registered pilot tree anchors changed.");
      }
      updates.push({ position, normal, origin, target, scale, local });
    }
  }

  for (const { position, normal, origin, target, scale, local } of updates) {
    for (const i of local) {
      const point = [position.getX(i), position.getY(i), position.getZ(i)];
      position.setXYZ(
        i,
        ...point.map(
          (value, axis) => target[axis] + (value - origin[axis]) * scale[axis],
        ),
      );
      const x = normal.getX(i) / scale[0];
      const y = normal.getY(i) / scale[1];
      const z = normal.getZ(i) / scale[2];
      const length = Math.hypot(x, y, z) || 1;
      normal.setXYZ(i, x / length, y / length, z / length);
    }
    position.needsUpdate = true;
    normal.needsUpdate = true;
  }
  for (const geometry of selected.keys()) {
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();
  }
  return expectedTrees;
}
