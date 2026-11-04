// SPDX-License-Identifier: Apache-2.0
// Bounded variation of existing inferred shrub crowns; never expands their source boxes.
import * as THREE from "three";
export function varyPlanting(root, spec, sha) {
  if (
    spec?.version !== 1 ||
    spec.base_asset_sha256 !== sha ||
    spec.target_name !== "planting" ||
    spec.vertices_per_group !== 216 ||
    spec.indices_per_group !== 324 ||
    spec.material !== "leaf" ||
    spec.color !== "658b54" ||
    !Array.isArray(spec.groups) ||
    spec.groups.length !== 40
  )
    throw Error("Invalid planting variation");
  const meshes = [];
  root.traverse((o) => {
    if (o.isMesh && o.name === "planting") meshes.push(o);
  });
  if (meshes.length !== 1) throw Error("Planting mesh missing or ambiguous");
  const mesh = meshes[0],
    g = mesh.geometry,
    p = g.attributes.position,
    m = mesh.material,
    idx = g.index;
  if (
    mesh.userData.asset_kind !== "landscape-detail" ||
    !mesh.matrix.equals(new THREE.Matrix4()) ||
    Array.isArray(m) ||
    !m.isMeshStandardMaterial ||
    m.name !== spec.material ||
    m.color.getHexString() !== spec.color ||
    m.vertexColors ||
    m.map ||
    !p ||
    p.count !== 8640 ||
    p.itemSize !== 3 ||
    g.attributes.color ||
    !idx ||
    idx.count !== 12960
  )
    throw Error("Planting source contract changed");
  const actual = [];
  for (let i = 0; i < 40; i++) {
    const r = spec.groups[i],
      lo = [Infinity, Infinity, Infinity],
      hi = [-Infinity, -Infinity, -Infinity];
    if (
      !Array.isArray(r?.min) ||
      !Array.isArray(r?.max) ||
      r.min.length !== 3 ||
      r.max.length !== 3 ||
      ![...r.min, ...r.max].every(Number.isFinite)
    )
      throw Error("Invalid shrub bounds");
    for (let j = 0; j < 216; j++) {
      const k = i * 216 + j,
        xyz = [p.getX(k), p.getY(k), p.getZ(k)];
      if (!xyz.every(Number.isFinite)) throw Error("Invalid shrub vertex");
      for (let axis = 0; axis < 3; axis++) {
        lo[axis] = Math.min(lo[axis], xyz[axis]);
        hi[axis] = Math.max(hi[axis], xyz[axis]);
      }
    }
    if (
      lo.some(
        (x, a) =>
          Math.abs(x - r.min[a]) > 0.001 ||
          Math.abs(hi[a] - r.max[a]) > 0.001 ||
          hi[a] <= lo[a],
      )
    )
      throw Error("Shrub source bounds changed");
    for (let j = 0; j < 324; j++) {
      const k = idx.getX(i * 324 + j);
      if (k < i * 216 || k >= (i + 1) * 216)
        throw Error("Shrub topology changed");
    }
    actual.push({ lo, hi });
  }
  const next = g.clone(),
    q = next.attributes.position,
    colors = new Float32Array(p.count * 3);
  for (let i = 0; i < 40; i++) {
    const { lo, hi } = actual[i],
      cx = (lo[0] + hi[0]) / 2,
      cz = (lo[2] + hi[2]) / 2,
      hs = 0.72 + (0.24 * ((i * 7) % 13)) / 12,
      tone = 0.84 + (0.16 * ((i * 11) % 17)) / 16;
    for (let j = 0; j < 216; j++) {
      const k = i * 216 + j,
        x = p.getX(k),
        y = p.getY(k),
        z = p.getZ(k),
        angle = Math.atan2(z - cz, x - cx),
        radial = 0.84 + 0.13 * (0.5 + 0.5 * Math.sin(angle * 3 + i * 0.9));
      q.setXYZ(
        k,
        cx + (x - cx) * radial,
        lo[1] + (y - lo[1]) * hs,
        cz + (z - cz) * radial,
      );
      colors.set([tone, tone, tone], k * 3);
    }
  }
  next.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  next.computeVertexNormals();
  const normals = next.attributes.normal,
    originalNormals = g.attributes.normal;
  if (!originalNormals || originalNormals.count !== p.count)
    throw Error("Planting normals changed");
  for (let i = 0; i < p.count; i++) {
    const nx = normals.getX(i),
      ny = normals.getY(i),
      nz = normals.getZ(i);
    if (!Number.isFinite(nx + ny + nz)) throw Error("Invalid varied normal");
    if (Math.hypot(nx, ny, nz) < 0.5) {
      const x = originalNormals.getX(i),
        y = originalNormals.getY(i),
        z = originalNormals.getZ(i);
      if (![x, y, z].every(Number.isFinite) || Math.hypot(x, y, z) < 0.9)
        throw Error("Invalid source normal");
      normals.setXYZ(i, x, y, z);
    }
  }
  next.computeBoundingBox();
  next.computeBoundingSphere();
  const material = m.clone();
  material.vertexColors = true;
  material.needsUpdate = true;
  mesh.geometry = next;
  mesh.material = material;
  return actual.length;
}
