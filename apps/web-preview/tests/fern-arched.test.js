import test from "node:test";
import assert from "node:assert/strict";
import { createFernGeometry } from "../src/fern-geometry.js";
test("regional fern geometry arches while remaining inside the prior clearance screen", () => {
  const g = createFernGeometry(),
    p = g.attributes.position;
  let radius = 0,
    highest = -Infinity,
    outerHighest = -Infinity;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i),
      y = p.getY(i),
      z = p.getZ(i),
      r = Math.hypot(x, z);
    assert.ok([x, y, z].every(Number.isFinite));
    radius = Math.max(radius, r);
    highest = Math.max(highest, y);
    if (r > 0.98) outerHighest = Math.max(outerHighest, y);
  }
  assert.ok(radius * 1.08 < 1.35);
  assert.ok(highest > 0.97);
  assert.ok(outerHighest < highest - 0.1);
  g.dispose();
});
