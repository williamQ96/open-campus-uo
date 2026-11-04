import { test } from "node:test";
import assert from "node:assert/strict";
import { Box3 } from "three";
import { createCampusProp } from "../src/props.js";
test("bicycle geometry stays inside its previous visual envelope", () => {
  const m = createCampusProp("bicycle"),
    b = new Box3().setFromObject(m),
    lo = [-0.311978, -0.000001, -0.970001],
    hi = [0.311978, 2.030001, 0.970001];
  for (let i = 0; i < 3; i++) {
    assert.ok(b.min.getComponent(i) >= lo[i]);
    assert.ok(b.max.getComponent(i) <= hi[i]);
  }
  assert.ok([...m.geometry.attributes.position.array].every(Number.isFinite));
  m.geometry.dispose();
  m.material.dispose();
});
