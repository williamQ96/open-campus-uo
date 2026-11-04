import test from "node:test";
import assert from "node:assert/strict";
import {
  createEntranceFrameGeometry,
  createEntranceDoorGeometry,
} from "../src/entrances.js";
test("shared portal remains within its prior envelope and has readable trim on both faces", () => {
  const frame = createEntranceFrameGeometry(),
    door = createEntranceDoorGeometry();
  assert.equal(frame.index.count / 3, 48);
  frame.computeBoundingBox();
  door.computeBoundingBox();
  const { min, max } = frame.boundingBox;
  assert.ok(min.x >= -0.976 && max.x <= 0.976);
  assert.ok(min.y >= 0 && max.y <= 2.881);
  assert.ok(min.z >= -0.121 && max.z <= 0.121);
  const p = frame.attributes.position;
  const front = [],
    back = [];
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i),
      y = p.getY(i),
      z = p.getZ(i);
    if (Math.abs(x) < 0.18 && y > 1 && y < 1.5) {
      if (z > 0.06) front.push(x);
      if (z < -0.06) back.push(x);
    }
  }
  assert.ok(front.some((x) => x < 0) && front.some((x) => x > 0));
  assert.ok(back.some((x) => x < 0) && back.some((x) => x > 0));
  assert.ok(door.boundingBox.min.y >= 0 && door.boundingBox.max.y < 2.7);
  frame.dispose();
  door.dispose();
});
