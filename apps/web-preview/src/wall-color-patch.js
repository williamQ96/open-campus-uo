// SPDX-License-Identifier: Apache-2.0
// Recolor only the source-matched vertical wall vertices of one authored building.
import * as THREE from "three";
export function applyWallColorPatch(root, patch, assetSha) {
  if (
    patch?.version !== 1 ||
    patch.base_asset_sha256 !== assetSha ||
    typeof patch.building_id !== "string" ||
    !Array.isArray(patch.source_rgb8) ||
    patch.source_rgb8.length !== 3 ||
    !patch.source_rgb8.every(
      (x) => Number.isInteger(x) && x >= 0 && x <= 255,
    ) ||
    !/^#[0-9a-f]{6}$/.test(patch.target_srgb) ||
    !Number.isInteger(patch.expected_vertices) ||
    patch.expected_vertices < 1 ||
    typeof patch.normal_y_abs_max !== "number" ||
    patch.normal_y_abs_max <= 0 ||
    patch.normal_y_abs_max > 0.5
  )
    throw new Error("Invalid wall color patch.");
  const matches = [];
  root.traverse((o) => {
    if (
      o.isMesh &&
      o.userData.asset_kind === "building" &&
      o.userData.asset_id === patch.building_id
    )
      matches.push(o);
  });
  if (matches.length !== 1)
    throw new Error("Wall color target missing or ambiguous.");
  const mesh = matches[0],
    geo = mesh.geometry,
    color = geo.attributes.color,
    normal = geo.attributes.normal;
  if (!color || !normal || color.count !== normal.count || color.itemSize !== 3)
    throw new Error("Wall color attributes changed.");
  const indices = [];
  for (let i = 0; i < color.count; i++) {
    const rgb = [color.getX(i), color.getY(i), color.getZ(i)].map((x) =>
      Math.round(x * 255),
    );
    if (
      Math.abs(normal.getY(i)) < patch.normal_y_abs_max &&
      rgb.every((v, k) => v === patch.source_rgb8[k])
    )
      indices.push(i);
  }
  if (indices.length !== patch.expected_vertices)
    throw new Error("Wall color vertex match changed.");
  const copy = geo.clone(),
    dst = copy.attributes.color,
    target = new THREE.Color(patch.target_srgb);
  for (const i of indices) dst.setXYZ(i, target.r, target.g, target.b);
  dst.needsUpdate = true;
  mesh.geometry = copy;
}
