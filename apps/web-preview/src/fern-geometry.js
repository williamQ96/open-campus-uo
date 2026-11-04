// SPDX-License-Identifier: Apache-2.0
// Original faceted fern-like fronds; dimensions are normalized for instancing.
import * as THREE from "three";
export function createFernGeometry() {
  const vertices = [];
  for (let f = 0; f < 10; f++) {
    // Fixed, bounded variation avoids ten identical radial blades while keeping
    // this component deterministic and inside the existing clearance screen.
    const lengths = [1, 0.86, 0.95, 0.9, 0.98, 0.84, 0.93, 0.89, 0.97, 0.87],
      heights = [1, 0.91, 0.96, 0.9, 0.98, 0.94, 0.92, 0.97, 0.9, 0.95],
      angle = (2 * Math.PI * f) / 10 + 0.035 * Math.sin(f * 2.4),
      ux = Math.cos(angle),
      uz = Math.sin(angle),
      vx = -uz,
      vz = ux;
    const center = (t) => [
      ux * t * lengths[f],
      0.02 + 0.98 * heights[f] * Math.sin(t * Math.PI * 0.7),
      uz * t * lengths[f],
    ];
    for (let i = 0; i < 8; i++) {
      const a = center(i / 8),
        b = center((i + 1) / 8),
        w = 0.012;
      const left = [a[0] - vx * w, a[1], a[2] - vz * w],
        right = [a[0] + vx * w, a[1], a[2] + vz * w];
      const tipL = [b[0] - vx * w, b[1], b[2] - vz * w],
        tipR = [b[0] + vx * w, b[1], b[2] + vz * w];
      vertices.push(...left, ...right, ...tipL, ...right, ...tipR, ...tipL);
      vertices.push(...tipL, ...right, ...left, ...tipL, ...tipR, ...right);
    }
    for (let i = 1; i <= 9; i++) {
      const t = i / 11,
        a = center(t),
        b = center(Math.min(1, t + 0.09));
      const width = 0.18 * Math.sin(Math.PI * t);
      for (const side of [-1, 1]) {
        const tip = [
          a[0] + side * vx * width + ux * 0.045,
          a[1] - 0.035,
          a[2] + side * vz * width + uz * 0.045,
        ];
        vertices.push(...a, ...tip, ...b);
        vertices.push(...b, ...tip, ...a);
      }
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(vertices, 3),
  );
  geometry.computeVertexNormals();
  return geometry;
}
