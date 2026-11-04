// SPDX-License-Identifier: Apache-2.0
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
