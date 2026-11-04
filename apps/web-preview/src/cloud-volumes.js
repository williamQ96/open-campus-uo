// SPDX-License-Identifier: Apache-2.0
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
export function shapeCloudVolumes(scene) {
  const list = [];
  scene.traverse((o) => {
    if (o.isMesh && o.name === "Rounded voxel cloud layer") list.push(o);
  });
  if (list.length !== 1) throw Error("Cloud target missing or ambiguous");
  const cloud = list[0],
    old = cloud.geometry,
    p = old.attributes.position;
  if (
    cloud.userData.volumeRefined ||
    !p ||
    p.count !== 81000 ||
    old.index ||
    !cloud.material.isMeshBasicMaterial ||
    !cloud.material.vertexColors
  )
    throw Error("Cloud source changed");
  const bounds = [];
  for (let l = 0; l < 90; l++) {
    let min = [Infinity, Infinity, Infinity],
      max = [-Infinity, -Infinity, -Infinity];
    for (let j = 0; j < 900; j++) {
      let i = l * 900 + j,
        v = [p.getX(i), p.getY(i), p.getZ(i)];
      if (!v.every(Number.isFinite)) throw Error("Bad positions");
      for (let k = 0; k < 3; k++) {
        min[k] = Math.min(min[k], v[k]);
        max[k] = Math.max(max[k], v[k]);
      }
    }
    let d = max.map((x, k) => x - min[k]);
    if (
      d[0] < 80 ||
      d[0] > 650 ||
      d[1] < 26 ||
      d[1] > 90 ||
      d[2] < 80 ||
      d[2] > 650
    )
      throw Error("Cloud bounds changed");
    bounds.push({ min, max, d });
  }
  const parts = [];
  for (let l = 0; l < 90; l++) {
    const { min, max, d } = bounds[l],
      geo = new THREE.SphereGeometry(1, 10, 6).toNonIndexed(),
      pos = geo.attributes.position,
      colors = [],
      scale = l % 5 === 2 ? 1.35 : l % 5 === 1 || l % 5 === 3 ? 1.15 : 1.0;
    for (let i = 0; i < pos.count; i++) {
      const y = Math.max(-0.65, pos.getY(i)),
        t = (y + 0.65) / 1.65;
      pos.setY(i, y);
      colors.push(0.72 + 0.28 * t, 0.8 + 0.2 * t, 0.87 + 0.13 * t);
    }
    geo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    geo.computeVertexNormals();
    geo.scale(d[0] * 0.5, (d[1] * scale) / 1.65, d[2] * 0.5);
    geo.translate(
      (min[0] + max[0]) / 2,
      min[1] + (d[1] * scale * 0.65) / 1.65,
      (min[2] + max[2]) / 2,
    );
    parts.push(geo);
  }
  const next = mergeGeometries(parts, false);
  if (!next) throw Error("Cloud merge failed");
  parts.forEach((x) => x.dispose());
  next.computeBoundingBox();
  next.computeBoundingSphere();
  cloud.geometry = next;
  cloud.userData = { ...cloud.userData, volumeRefined: true };
  return bounds.length;
}
