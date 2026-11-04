// SPDX-License-Identifier: Apache-2.0
// Conservative movement envelopes supplied by a source-pinned exterior replacement.
export function collisionBoxesForDetail(spec) {
  const boxes = spec.collision_boxes_enu_m ?? [];
  if (
    !Array.isArray(boxes) ||
    boxes.length > 16 ||
    (boxes.length && spec.replace_building !== true)
  )
    throw new Error("Invalid exterior collision boxes");
  for (const box of boxes) {
    if (
      !Array.isArray(box) ||
      box.length !== 4 ||
      !box.every(Number.isFinite) ||
      box.some((n) => Math.abs(n) > 2000) ||
      box[0] >= box[2] ||
      box[1] >= box[3] ||
      box[2] - box[0] > 100 ||
      box[3] - box[1] > 100
    )
      throw new Error("Invalid exterior collision box");
  }
  return boxes;
}
// Thin ground-level facade overlays only; replacement envelopes retain their existing contract.
export function overlayCollisionBoxesForDetail(spec) {
  const boxes = spec.overlay_collision_boxes_enu_m ?? [];
  if (
    !Array.isArray(boxes) ||
    boxes.length > 8 ||
    (boxes.length &&
      (spec.replace_building !== false || spec.scope === "environment"))
  )
    throw new Error("Invalid overlay collision boxes");
  for (const b of boxes) {
    if (
      !Array.isArray(b) ||
      b.length !== 4 ||
      !b.every(Number.isFinite) ||
      b.some((n) => Math.abs(n) > 2000) ||
      b[0] >= b[2] ||
      b[1] >= b[3] ||
      Math.min(b[2] - b[0], b[3] - b[1]) > 1.5 ||
      Math.max(b[2] - b[0], b[3] - b[1]) > 25
    )
      throw new Error("Invalid overlay collision box");
  }
  return boxes;
}
function distanceToRing(x, y, ring) {
  let best = Infinity;
  for (let i = 0; i < ring.length; i++) {
    const [ax, ay] = ring[i],
      [bx, by] = ring[(i + 1) % ring.length],
      dx = bx - ax,
      dy = by - ay;
    const t = Math.max(
      0,
      Math.min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy || 1)),
    );
    best = Math.min(best, Math.hypot(x - (ax + t * dx), y - (ay + t * dy)));
  }
  return best;
}
export function attachCollisionBoxes(buildings, supplements) {
  const byId = new Map(buildings.map((b) => [b.id, b]));
  const pending = new Map(),
    all = [];
  for (const { buildingId, boxes, overlay = false } of supplements) {
    if (!byId.has(buildingId) || pending.has(buildingId))
      throw new Error("Invalid exterior collision target");
    if (overlay) {
      const ring = byId.get(buildingId).footprint_enu_m;
      if (
        !Array.isArray(ring) ||
        ring.length < 3 ||
        boxes.some(([x0, y0, x1, y1]) =>
          [
            [x0, y0],
            [x0, y1],
            [x1, y0],
            [x1, y1],
          ].some(([x, y]) => distanceToRing(x, y, ring) > 1.5),
        )
      )
        throw new Error(
          "Overlay collision is not adjacent to building footprint",
        );
    }
    const rings = boxes.map(([x0, n0, x1, n1]) => [
      [x0, n0],
      [x1, n0],
      [x1, n1],
      [x0, n1],
    ]);
    pending.set(buildingId, rings);
    all.push(...boxes);
  }
  for (const [id, rings] of pending) byId.get(id).collision_extra_enu_m = rings;
  return all;
}
// Exact segment vs expanded axis-aligned rectangle, ENU coordinates.
export function segmentHitsBoxes(a, b, boxes, margin = 0) {
  return boxes.some(([x0, n0, x1, n1]) => {
    let lo = 0,
      hi = 1;
    for (const [p, q, min, max] of [
      [a[0], b[0], x0 - margin, x1 + margin],
      [a[1], b[1], n0 - margin, n1 + margin],
    ]) {
      const d = q - p;
      if (Math.abs(d) < 1e-12) {
        if (p < min || p > max) return false;
        continue;
      }
      let t0 = (min - p) / d,
        t1 = (max - p) / d;
      if (t0 > t1) [t0, t1] = [t1, t0];
      lo = Math.max(lo, t0);
      hi = Math.min(hi, t1);
      if (lo > hi) return false;
    }
    return true;
  });
}
