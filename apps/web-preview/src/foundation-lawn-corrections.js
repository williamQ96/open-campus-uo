// SPDX-License-Identifier: Apache-2.0
import { Vector3 } from "three";
import spec from "../data/foundation-lawn-corrections.json" with { type: "json" };

export function uncoverUniversityDistrictParking(root, sourceSha256) {
  const correction = spec.universityDistrictParking;
  if (sourceSha256 !== correction.sourceSha256) return;

  const lawn = root.getObjectByName("campus-lawn-extension");
  const geometry = lawn?.geometry;
  const position = geometry?.getAttribute("position");
  const index = geometry?.getIndex();
  if (!lawn?.isMesh || !position || !index || geometry.groups.length)
    throw new Error("University District parking lawn source changed.");

  lawn.updateWorldMatrix(true, false);
  const [west, south, east, north] = correction.boundsEnuM;
  const inside = new Uint8Array(position.count);
  const point = new Vector3();
  for (let i = 0; i < position.count; i++) {
    point.fromBufferAttribute(position, i).applyMatrix4(lawn.matrixWorld);
    inside[i] =
      point.x >= west &&
      point.x <= east &&
      -point.z >= south &&
      -point.z <= north;
  }

  // Remove only complete triangles within the verified paved interior.
  const retained = [];
  for (let i = 0; i < index.count; i += 3) {
    const a = index.getX(i),
      b = index.getX(i + 1),
      c = index.getX(i + 2);
    if (!(inside[a] && inside[b] && inside[c])) retained.push(a, b, c);
  }
  if (index.count - retained.length !== correction.expectedTriangles * 3)
    throw new Error("University District parking lawn triangles changed.");
  geometry.setIndex(retained);
}

function lawnWeight(e, n, ring) {
  let inside = false,
    distance = Infinity;
  for (let i = 0; i < ring.length; i++) {
    const [x, y] = ring[i],
      [X, Y] = ring[(i + 1) % ring.length];
    const dx = X - x,
      dy = Y - y;
    if (y > n !== Y > n && e < x + (dx * (n - y)) / dy) inside = !inside;
    const t = Math.max(
      0,
      Math.min(1, ((e - x) * dx + (n - y) * dy) / (dx * dx + dy * dy)),
    );
    distance = Math.min(distance, Math.hypot(e - x - t * dx, n - y - t * dy));
  }
  // Keep marked pavement outside each lawn and soften transitions over one cell.
  return inside ? Math.min(1, (distance + 0.75) / 4) : 0;
}

const lawns = spec.lawns.map(({ ring }) => {
  const east = ring.map(([e]) => e),
    north = ring.map(([, n]) => n);
  return {
    ring,
    west: Math.min(...east),
    east: Math.max(...east),
    south: Math.min(...north),
    north: Math.max(...north),
  };
});

export function restoreFoundationLawns(geometry) {
  const position = geometry.getAttribute("position");
  const colors = geometry.getAttribute("color");
  if (!colors || colors.count !== position.count) return 0;
  let changed = 0;
  for (let i = 0; i < position.count; i++) {
    const e = position.getX(i),
      n = -position.getZ(i);
    let blend = 0;
    for (const lawn of lawns) {
      if (
        e >= lawn.west &&
        e <= lawn.east &&
        n >= lawn.south &&
        n <= lawn.north
      )
        blend = Math.max(blend, lawnWeight(e, n, lawn.ring));
    }
    if (!blend) continue;
    const r = colors.getX(i),
      g = colors.getY(i),
      b = colors.getZ(i);
    if (g >= 0.33 && g - r > 0.08) continue;
    // L2 ground materials use linear vertex colors. Lift the aerial shadow
    // estimate into the neighboring lawn palette without touching light maps.
    colors.setXYZ(
      i,
      r + (0.244 - r) * blend,
      g + (0.356 - g) * blend,
      b + (0.152 - b) * blend,
    );
    changed++;
  }
  if (changed) colors.needsUpdate = true;
  return changed;
}
