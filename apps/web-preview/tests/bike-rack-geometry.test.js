import test from "node:test";
import assert from "node:assert/strict";
import { createBikeRackGeometry } from "../src/bike-rack-geometry.js";
test("generic hoop rack has bounded dimensions and reproducible finite geometry", () => {
  const a = createBikeRackGeometry(),
    b = createBikeRackGeometry();
  a.computeBoundingBox();
  const min = a.boundingBox.min,
    max = a.boundingBox.max;
  assert.ok(Math.abs(max.y - 0.9144) < 1e-5);
  assert.ok(min.y >= -1e-6);
  assert.ok(max.x - min.x < 2.1);
  assert.ok(max.z - min.z < 0.47);
  assert.deepEqual(
    [...a.attributes.position.array],
    [...b.attributes.position.array],
  );
  assert.ok([...a.attributes.position.array].every(Number.isFinite));
  assert.equal(a.index.count % 3, 0);
  assert.throws(() => createBikeRackGeometry({ hoops: 1 }));
  assert.throws(() => createBikeRackGeometry({ hoops: 9 }));
  a.dispose();
  b.dispose();
});
