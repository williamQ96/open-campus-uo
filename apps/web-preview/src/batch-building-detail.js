// SPDX-License-Identifier: Apache-2.0
// Merge a source-pinned static facade into its registered context batch.
import { mergeBuildingDetailIntoSource } from "./exterior-detail.js";
export function mergeBatchBuildingDetail(root, detail, spec) {
  const bounds = spec.merge_batch_bounds;
  if (
    typeof spec.merge_batch_target !== "string" ||
    !spec.merge_batch_target ||
    !Array.isArray(bounds) ||
    bounds.length !== 6 ||
    !bounds.every(Number.isFinite) ||
    bounds.some((v) => Math.abs(v) > 2000) ||
    bounds[0] >= bounds[3] ||
    bounds[1] >= bounds[4] ||
    bounds[2] >= bounds[5] ||
    bounds[3] - bounds[0] > 50 ||
    bounds[4] - bounds[1] > 50 ||
    bounds[5] - bounds[2] > 50 ||
    spec.trim_source_min_y !== undefined ||
    spec.trim_source_expected_triangles !== undefined
  )
    throw Error("Invalid batch detail bounds.");
  const matches = root.children.filter(
    (o) =>
      o.isMesh &&
      o.name === spec.merge_batch_target &&
      o.userData.asset_kind === "context-building-batch" &&
      Array.isArray(o.userData.asset_ids) &&
      o.userData.asset_ids.includes(spec.building_id),
  );
  if (
    matches.length !== 1 ||
    detail.parent !== root ||
    detail.children.length !== 1 ||
    !detail.children[0].isMesh
  )
    throw Error("Ambiguous batch detail target.");
  const mesh = matches[0],
    part = detail.children[0];
  part.geometry.computeBoundingBox();
  const b = part.geometry.boundingBox;
  if (
    !b ||
    b.min.x < bounds[0] ||
    b.min.y < bounds[1] ||
    b.min.z < bounds[2] ||
    b.max.x > bounds[3] ||
    b.max.y > bounds[4] ||
    b.max.z > bounds[5]
  )
    throw Error("Batch detail exceeds bounds.");
  // Reuse the existing strict material, topology and static-transform checks. The
  // temporary identity is synchronous and always restored, including on failure.
  const oldName = mesh.name,
    oldKind = mesh.userData.asset_kind,
    hadId = Object.hasOwn(mesh.userData, "asset_id"),
    oldId = mesh.userData.asset_id;
  try {
    mesh.name = spec.building_id;
    mesh.userData.asset_kind = "building";
    mesh.userData.asset_id = spec.building_id;
    mergeBuildingDetailIntoSource(root, detail, spec);
  } finally {
    mesh.name = oldName;
    mesh.userData.asset_kind = oldKind;
    if (hadId) mesh.userData.asset_id = oldId;
    else delete mesh.userData.asset_id;
  }
}
