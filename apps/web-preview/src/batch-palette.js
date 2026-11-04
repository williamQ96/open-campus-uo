// SPDX-License-Identifier: Apache-2.0
// Apply a source-pinned palette to bounded vertices of a registered static batch.
import * as THREE from "three";
export function applyBatchPalette(root, spec, assetSha) {
  const b = spec?.bounds,
    groups = spec?.groups;
  if (
    spec?.version !== 1 ||
    spec.base_asset_sha256 !== assetSha ||
    typeof spec.building_id !== "string" ||
    !spec.building_id ||
    typeof spec.target_name !== "string" ||
    !spec.target_name ||
    !Number.isInteger(spec.expected_vertices) ||
    spec.expected_vertices < 1 ||
    !Array.isArray(b) ||
    b.length !== 6 ||
    !b.every(Number.isFinite) ||
    b.some((v) => Math.abs(v) > 2000) ||
    b[0] >= b[3] ||
    b[1] >= b[4] ||
    b[2] >= b[5] ||
    b[3] - b[0] > 50 ||
    b[4] - b[1] > 50 ||
    b[5] - b[2] > 50 ||
    !Array.isArray(groups) ||
    !groups.length ||
    groups.length > 8
  )
    throw Error("Invalid batch palette contract.");
  const signatures = new Set();
  for (const g of groups) {
    if (
      !Array.isArray(g?.source_linear_4dp) ||
      g.source_linear_4dp.length !== 3 ||
      !g.source_linear_4dp.every(
        (v) =>
          Number.isFinite(v) &&
          v >= 0 &&
          v <= 1 &&
          Math.abs(v * 10000 - Math.round(v * 10000)) < 1e-6,
      ) ||
      !Number.isInteger(g.expected_vertices) ||
      g.expected_vertices < 1 ||
      !/^#[0-9a-f]{6}$/.test(g.target_srgb)
    )
      throw Error("Invalid palette group.");
    const signature = g.source_linear_4dp.join(",");
    if (signatures.has(signature)) throw Error("Duplicate palette group.");
    signatures.add(signature);
  }
  const meshes = [];
  root.traverse((o) => {
    if (
      o.isMesh &&
      o.name === spec.target_name &&
      o.userData.asset_kind === "context-building-batch" &&
      Array.isArray(o.userData.asset_ids) &&
      o.userData.asset_ids.includes(spec.building_id)
    )
      meshes.push(o);
  });
  if (meshes.length !== 1)
    throw Error("Batch palette target missing or ambiguous.");
  const mesh = meshes[0],
    g = mesh.geometry,
    p = g.attributes.position,
    c = g.attributes.color,
    m = mesh.material;
  mesh.updateMatrix();
  if (
    !mesh.matrix.equals(new THREE.Matrix4()) ||
    !p ||
    !c ||
    p.isInterleavedBufferAttribute ||
    c.isInterleavedBufferAttribute ||
    p.itemSize !== 3 ||
    c.itemSize !== 3 ||
    p.count !== spec.expected_vertices ||
    c.count !== p.count ||
    Array.isArray(m) ||
    !m.isMeshStandardMaterial ||
    !m.vertexColors ||
    m.map ||
    m.color.getHexString() !== "ffffff"
  )
    throw Error("Batch palette source changed.");
  const selections = groups.map(() => []);
  for (let i = 0; i < p.count; i++) {
    const pos = [p.getX(i), p.getY(i), p.getZ(i)];
    if (!pos.every(Number.isFinite)) throw Error("Invalid source position.");
    if (pos.some((v, k) => v < b[k] || v > b[k + 3])) continue;
    const rgb = [c.getX(i), c.getY(i), c.getZ(i)];
    if (!rgb.every(Number.isFinite)) throw Error("Invalid source color.");
    const rounded = rgb.map((v) => Math.round(v * 10000) / 10000);
    groups.forEach((group, j) => {
      if (group.source_linear_4dp.every((v, k) => v === rounded[k]))
        selections[j].push(i);
    });
  }
  if (selections.some((list, i) => list.length !== groups[i].expected_vertices))
    throw Error("Batch palette source selection changed.");
  const next = g.clone(),
    dst = next.attributes.color;
  for (let i = 0; i < groups.length; i++) {
    const color = new THREE.Color(groups[i].target_srgb);
    for (const j of selections[i]) dst.setXYZ(j, color.r, color.g, color.b);
  }
  dst.needsUpdate = true;
  mesh.geometry = next;
  return selections.map((a) => a.length);
}
