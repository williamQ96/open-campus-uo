// SPDX-License-Identifier: Apache-2.0
// Reversible source-pinned deformation of the existing top of a building mesh.
import * as THREE from "three";
export function applyBuildingRoofSlope(root, spec, assetSha) {
  if (
    spec.version !== 1 ||
    spec.base_asset_sha256 !== assetSha ||
    typeof spec.building_id !== "string" ||
    !Number.isInteger(spec.expected_vertex_count) ||
    !Number.isInteger(spec.expected_selected_vertices) ||
    !Number.isFinite(spec.minimum_y) ||
    !Number.isFinite(spec.origin_x) ||
    !Number.isFinite(spec.slope) ||
    Math.abs(spec.slope) > 0.05 ||
    !Number.isFinite(spec.max_displacement_m) ||
    spec.max_displacement_m <= 0 ||
    spec.max_displacement_m > 1 ||
    !Array.isArray(spec.roof_feature_rgb8) ||
    spec.roof_feature_rgb8.length !== 3 ||
    !spec.roof_feature_rgb8.every(
      (v) => Number.isInteger(v) && v >= 0 && v <= 255,
    )
  )
    throw new Error("Invalid source-pinned roof slope.");
  const targets = root.children.filter(
    (o) =>
      o.isMesh &&
      o.name === spec.building_id &&
      o.userData.asset_kind === "building" &&
      o.userData.asset_id === spec.building_id,
  );
  if (targets.length !== 1) throw new Error("Ambiguous roof slope target.");
  const target = targets[0],
    g = target.geometry,
    p = g.attributes.position,
    c = g.attributes.color,
    n = g.attributes.normal,
    m = target.material;
  target.updateMatrix();
  if (
    !target.matrix.equals(new THREE.Matrix4()) ||
    !p ||
    !c ||
    !n ||
    p.itemSize !== 3 ||
    c.itemSize !== 3 ||
    n.itemSize !== 3 ||
    p.count !== spec.expected_vertex_count ||
    c.count !== p.count ||
    n.count !== p.count ||
    Array.isArray(m) ||
    !m.isMeshStandardMaterial ||
    !m.vertexColors ||
    m.color.getHexString() !== "ffffff" ||
    m.map ||
    m.transparent ||
    m.side !== THREE.DoubleSide ||
    Math.abs(m.roughness - 0.9) > 0.001
  )
    throw new Error("Roof source geometry or material changed.");
  const selected = [];
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i),
      y = p.getY(i),
      z = p.getZ(i),
      rgb = [c.getX(i), c.getY(i), c.getZ(i)].map((v) => Math.round(v * 255));
    if (![x, y, z, ...rgb].every(Number.isFinite))
      throw new Error("Invalid roof vertex.");
    const feature = rgb.every((v, k) => v === spec.roof_feature_rgb8[k]);
    if (y >= spec.minimum_y || feature) {
      const dy = spec.slope * (x - spec.origin_x);
      if (Math.abs(dy) > spec.max_displacement_m)
        throw new Error("Roof slope exceeds displacement bound.");
      selected.push([i, dy]);
    }
  }
  if (selected.length !== spec.expected_selected_vertices)
    throw new Error("Roof vertex selection changed.");
  const replacement = g.clone(),
    pos = replacement.attributes.position,
    oldNormals = n.array.slice(),
    chosen = new Uint8Array(p.count);
  for (const [i, dy] of selected) {
    pos.setY(i, p.getY(i) + dy);
    chosen[i] = 1;
  }
  replacement.computeVertexNormals();
  for (let i = 0; i < p.count; i++)
    if (!chosen[i])
      replacement.attributes.normal.setXYZ(
        i,
        oldNormals[i * 3],
        oldNormals[i * 3 + 1],
        oldNormals[i * 3 + 2],
      );
  replacement.computeBoundingBox();
  replacement.computeBoundingSphere();
  target.geometry = replacement;
  return selected.length;
}
