import test from "node:test";
import assert from "node:assert/strict";
import { sampleGround, isBlocked, movePlayer } from "../src/world.js";

// Non-symmetric elevations expose north/south flips and unit errors.
const field = {
  nx: 3,
  ny: 3,
  spacing_m: 10,
  min_east_m: -10,
  min_north_m: -10,
  heights_m: [0, 10, 20, 20, 30, 40, 40, 50, 60],
};
test("ENU height samples convert south-facing glTF z correctly", () => {
  assert.equal(sampleGround(field, -10, 10), 0);
  assert.ok(Math.abs(sampleGround(field, 0, -10) - 50) < 0.0001);
  assert.equal(sampleGround(field, 5, -5), 45);
});
const buildings = [
  {
    footprint_enu_m: [
      [2, -3],
      [4, -3],
      [4, 3],
      [2, 3],
    ],
  },
];
test("non-coplanar cell follows the exported triangles rather than a curved bilinear patch", () => {
  const terrain = {
    nx: 2,
    ny: 2,
    spacing_m: 1,
    min_east_m: 0,
    min_north_m: 0,
    heights_m: [0, 0, 0, 10],
  };
  assert.equal(sampleGround(terrain, 0.75, -0.25), 2.5);
  assert.equal(sampleGround(terrain, 0.25, -0.75), 2.5);
});
test("circle collision and AOI boundary stop high-speed tunnelling", () => {
  assert.equal(isBlocked(3, 0, buildings, 10), true);
  assert.equal(isBlocked(1.7, 0, buildings, 10), true);
  assert.equal(isBlocked(9.8, 0, [], 10), true);
  const p = { x: 0, y: 0, z: 0 };
  movePlayer(p, { x: 8, z: 0 }, buildings, 10, field);
  assert.ok(p.x < 1.6);
  assert.ok(p.x > 1.3);
});
test("diagonal movement slides along wall and follows terrain", () => {
  const p = { x: 1.5, y: 0, z: 0 };
  movePlayer(p, { x: 1, z: 1 }, buildings, 10, field);
  assert.ok(p.x < 1.6);
  assert.equal(p.z, 1);
  assert.equal(p.y, sampleGround(field, p.x, p.z));
});
