// SPDX-License-Identifier: Apache-2.0
// Remove an explicitly verified set of source triangles without modifying the GLB.
export function applySourceTrianglePatch(root, spec, assetSha) {
  const patch = spec?.source_triangle_patch;
  if (
    !patch ||
    spec.replace_building !== false ||
    spec.base_asset_sha256 !== assetSha ||
    !Array.isArray(patch.triangles) ||
    !patch.triangles.length ||
    !Array.isArray(patch.vertices) ||
    !Number.isInteger(patch.vertex_count) ||
    !Number.isInteger(patch.triangle_count)
  )
    throw new Error("Invalid source triangle patch or source hash.");
  const matches = [];
  root.traverse((o) => {
    if (
      o.isMesh &&
      o.userData.asset_kind === "building" &&
      o.userData.asset_id === spec.building_id
    )
      matches.push(o);
  });
  if (matches.length !== 1)
    throw new Error("Source triangle patch target ambiguous.");
  const mesh = matches[0],
    geo = mesh.geometry,
    idx = geo.index;
  const attrs = [
    geo.attributes.position,
    geo.attributes.normal,
    geo.attributes.color,
  ];
  if (
    !idx ||
    idx.count !== patch.triangle_count * 3 ||
    attrs.some(
      (a) =>
        !a ||
        a.itemSize !== 3 ||
        a.count !== patch.vertex_count ||
        a.isInterleavedBufferAttribute,
    )
  )
    throw new Error("Source triangle topology changed.");
  const expected = new Map();
  for (const row of patch.vertices) {
    if (
      !Array.isArray(row) ||
      row.length !== 10 ||
      !Number.isInteger(row[0]) ||
      row[0] < 0 ||
      row[0] >= patch.vertex_count ||
      expected.has(row[0]) ||
      !row.slice(1).every(Number.isFinite)
    )
      throw new Error("Invalid source vertex signature.");
    const [vertex, ...values] = row;
    for (let a = 0; a < 3; a++)
      if (
        attrs[a].getX(vertex) !== values[a * 3] ||
        attrs[a].getY(vertex) !== values[a * 3 + 1] ||
        attrs[a].getZ(vertex) !== values[a * 3 + 2]
      )
        throw new Error("Source vertex signature changed.");
    expected.set(vertex, true);
  }
  const removed = new Set(),
    used = new Set();
  for (const row of patch.triangles) {
    if (
      !Array.isArray(row) ||
      row.length !== 4 ||
      !Number.isInteger(row[0]) ||
      row[0] < 0 ||
      row[0] >= patch.triangle_count ||
      removed.has(row[0])
    )
      throw new Error("Invalid source triangle signature.");
    for (let j = 0; j < 3; j++) {
      if (
        !Number.isInteger(row[j + 1]) ||
        !expected.has(row[j + 1]) ||
        idx.getX(row[0] * 3 + j) !== row[j + 1]
      )
        throw new Error("Source triangle signature changed.");
      used.add(row[j + 1]);
    }
    removed.add(row[0]);
  }
  if (used.size !== expected.size || removed.size >= patch.triangle_count)
    throw new Error("Invalid source triangle coverage.");
  const keep = [];
  for (let i = 0; i < patch.triangle_count; i++)
    if (!removed.has(i))
      keep.push(idx.getX(i * 3), idx.getX(i * 3 + 1), idx.getX(i * 3 + 2));
  const copy = geo.clone();
  copy.setIndex(keep);
  mesh.geometry = copy;
  return { mesh, original: geo, removed: removed.size };
}
