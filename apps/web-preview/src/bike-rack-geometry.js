// SPDX-License-Identifier: Apache-2.0
// Original faceted hoop-style bike rack. Units are meters; not a brand replica.
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
export function createBikeRackGeometry({ hoops = 3 } = {}) {
  if (!Number.isInteger(hoops) || hoops < 2 || hoops > 8)
    throw new Error("Bike rack requires 2-8 hoops");
  const width = 0.4572,
    height = 0.9144,
    spacing = 0.9144,
    tube = 0.047625 / 2,
    radius = (width - 2 * tube) / 2,
    spring = height - radius - tube,
    pieces = [];
  for (let i = 0; i < hoops; i++) {
    const x = (i - (hoops - 1) / 2) * spacing;
    for (const side of [-1, 1]) {
      const leg = new THREE.CylinderGeometry(tube, tube, spring, 8);
      leg.translate(x, spring / 2, side * radius);
      pieces.push(leg);
    }
    const curve = new THREE.TorusGeometry(radius, tube, 8, 16, Math.PI);
    curve.rotateY(Math.PI / 2);
    curve.translate(x, spring, 0);
    pieces.push(curve);
  }
  const length = (hoops - 1) * spacing + 0.24;
  for (const side of [-1, 1]) {
    const rail = new THREE.BoxGeometry(length, 0.0254, 0.0508);
    rail.translate(0, 0.0127, side * radius);
    pieces.push(rail);
  }
  const geometry = mergeGeometries(pieces);
  pieces.forEach((p) => p.dispose());
  if (!geometry) throw new Error("Could not merge bike rack geometry");
  return geometry;
}
