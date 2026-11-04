// SPDX-License-Identifier: Apache-2.0
// Post-process only the generated context trunk vertices, never the canopy.
import * as THREE from "three";
export function varyContextTrunks(root, spec, assetSha) {
  if (
    spec?.version !== 1 ||
    spec.base_asset_sha256 !== assetSha ||
    spec.target_name !== "campus-trees" ||
    spec.count !== 300 ||
    spec.top_ratio !== 0.78 ||
    spec.color_range !== 0.06
  )
    throw Error("Invalid trunk variation specification");
  const matches = [];
  root.traverse((o) => {
    if (o.isMesh && o.name === spec.target_name) matches.push(o);
  });
  if (matches.length !== 1) throw Error("Trunk target missing or ambiguous");
  const mesh = matches[0],
    g = mesh.geometry,
    p = g.attributes.position,
    n = g.attributes.normal,
    c = g.attributes.color,
    idx = g.index;
  if (
    mesh.userData.asset_kind !== "landscape-detail" ||
    mesh.userData.contextTrunkVariation ||
    !mesh.matrix.equals(new THREE.Matrix4()) ||
    !p ||
    !n ||
    !c ||
    !idx ||
    p.count !== 55200 ||
    n.count !== 55200 ||
    c.count !== 55200 ||
    idx.count !== 72000
  )
    throw Error("Trunk variation source changed");
  const groups = [];
  for (let t = 0; t < 300; t++) {
    const start = 45600 + t * 32,
      centerX = (p.getX(start) + p.getX(start + 16)) / 2,
      centerZ = (p.getZ(start) + p.getZ(start + 16)) / 2,
      y0 = p.getY(start),
      y1 = p.getY(start + 2);
    if (![centerX, centerZ, y0, y1].every(Number.isFinite) || y1 - y0 < 0.01)
      throw Error("Invalid trunk bounds");
    for (let side = 0; side < 8; side++) {
      const k = start + side * 4;
      for (let q = 0; q < 4; q++) {
        const i = k + q,
          x = p.getX(i),
          y = p.getY(i),
          z = p.getZ(i),
          rad = Math.hypot(x - centerX, z - centerZ);
        if (
          ![
            x,
            y,
            z,
            n.getX(i),
            n.getY(i),
            n.getZ(i),
            c.getX(i),
            c.getY(i),
            c.getZ(i),
          ].every(Number.isFinite) ||
          Math.abs(rad - 0.15) > 0.0003 ||
          Math.abs(y - (q < 2 ? y0 : y1)) > 0.0003 ||
          Math.abs(c.getX(i) - 0.18447499) > 0.0001 ||
          Math.abs(c.getY(i) - 0.12477182) > 0.0001 ||
          Math.abs(c.getZ(i) - 0.07818742) > 0.0001
        )
          throw Error("Trunk vertex contract changed");
      }
      const i = idx.array.subarray(
        t * 240 + 192 + side * 6,
        t * 240 + 198 + side * 6,
      );
      if (![k, k + 2, k + 1, k, k + 3, k + 2].every((v, j) => i[j] === v))
        throw Error("Trunk topology changed");
    }
    groups.push({ start, centerX, centerZ, y0, y1 });
  }
  const next = g.clone(),
    pos = next.attributes.position,
    nor = next.attributes.normal,
    col = next.attributes.color;
  for (let t = 0; t < groups.length; t++) {
    const { start, centerX, centerZ, y0, y1 } = groups[t],
      slope = (0.15 * (1 - spec.top_ratio) * Math.cos(Math.PI / 8)) / (y1 - y0),
      scale = 1 + ((((t * 73) % 101) / 100) * 2 - 1) * spec.color_range;
    for (let j = 0; j < 32; j++) {
      const i = start + j;
      if (j % 4 >= 2)
        pos.setXYZ(
          i,
          centerX + (pos.getX(i) - centerX) * spec.top_ratio,
          pos.getY(i),
          centerZ + (pos.getZ(i) - centerZ) * spec.top_ratio,
        );
      const len = Math.hypot(nor.getX(i), slope, nor.getZ(i));
      nor.setXYZ(i, nor.getX(i) / len, slope / len, nor.getZ(i) / len);
      col.setXYZ(
        i,
        col.getX(i) * scale,
        col.getY(i) * scale,
        col.getZ(i) * scale,
      );
    }
  }
  pos.needsUpdate = nor.needsUpdate = col.needsUpdate = true;
  next.computeBoundingBox();
  next.computeBoundingSphere();
  mesh.geometry = next;
  mesh.userData = { ...mesh.userData, contextTrunkVariation: true };
  return groups.length;
}
