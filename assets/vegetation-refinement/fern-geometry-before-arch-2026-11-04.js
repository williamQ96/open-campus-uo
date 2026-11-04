// SPDX-License-Identifier: Apache-2.0
// Original faceted fern-like fronds; dimensions are normalized for instancing.
import * as THREE from "three";
export function createFernGeometry() {
  const vertices = [];
  for (let f = 0; f < 9; f++) {
    const angle = 2 * Math.PI * f / 9, ux = Math.cos(angle), uz = Math.sin(angle), vx = -uz, vz = ux;
    const center = (t) => [ux * t, 0.02 + 0.98 * Math.sin(t * Math.PI / 2), uz * t];
    for (let i = 0; i < 6; i++) {
      const a = center(i / 6), b = center((i + 1) / 6), w = 0.012;
      const left = [a[0] - vx * w, a[1], a[2] - vz * w], right = [a[0] + vx * w, a[1], a[2] + vz * w];
      const tipL = [b[0] - vx * w, b[1], b[2] - vz * w], tipR = [b[0] + vx * w, b[1], b[2] + vz * w];
      vertices.push(...left, ...right, ...tipL, ...right, ...tipR, ...tipL);
      vertices.push(...tipL, ...right, ...left, ...tipL, ...tipR, ...right);
    }
    for (let i = 1; i <= 5; i++) {
      const t = i / 6, a = center(t), b = center(Math.min(1, t + 0.17));
      const width = 0.24 * Math.sin(Math.PI * t);
      for (const side of [-1, 1]) {
        const tip = [a[0] + side * vx * width + ux * 0.08, a[1] - 0.06, a[2] + side * vz * width + uz * 0.08];
        vertices.push(...a, ...tip, ...b);
        vertices.push(...b, ...tip, ...a);
      }
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(vertices, 3));
  geometry.computeVertexNormals();
  return geometry;
}
