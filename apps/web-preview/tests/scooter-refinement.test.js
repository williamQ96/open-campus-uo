import { test } from "node:test";
import assert from "node:assert/strict";
import { Box3 } from "three";
import { createCampusProp } from "../src/props.js";
test("scooter geometry stays inside its previous visual envelope", () => {
  const m = createCampusProp("scooter"),
    box = new Box3().setFromObject(m);
  const lo = [-0.313032, 0.00783, -0.740001],
    hi = [0.313032, 2.030001, 0.740001];
  for (let i = 0; i < 3; i++) {
    assert.ok(box.min.getComponent(i) >= lo[i]);
    assert.ok(box.max.getComponent(i) <= hi[i]);
  }
  assert.ok([...m.geometry.attributes.position.array].every(Number.isFinite));
  m.geometry.dispose();
  m.material.dispose();
});
