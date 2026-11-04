import test from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import { createCampusProp } from "../src/props.js";
const limits = {
  car: [1.09, 1.7, 2.195],
  suv: [1.09, 2.025, 2.195],
  van: [1.09, 2.175, 2.435],
  pickup: [1.09, 1.7, 2.195],
};
test("generic road vehicles fit their previous visible envelopes and keep bounded finite geometry", () => {
  for (const [kind, [x, y, z]] of Object.entries(limits)) {
    const mesh = createCampusProp(kind);
    mesh.geometry.computeBoundingBox();
    const box = mesh.geometry.boundingBox;
    assert.ok(box.min.x >= -x - 1e-5 && box.max.x <= x + 1e-5);
    assert.ok(box.min.z >= -z - 1e-5 && box.max.z <= z + 1e-5);
    assert.ok(box.min.y >= 0 && box.max.y <= y + 1e-5);
    assert.ok(mesh.geometry.attributes.position.count <= 2300);
    assert.ok(
      [...mesh.geometry.attributes.position.array].every(Number.isFinite),
    );
    assert.equal(mesh.userData.kind, kind);
  }
});
test("pickup windshield is visible in front of the cab surface", () => {
  const geo = createCampusProp("pickup").geometry,
    pos = geo.attributes.position,
    col = geo.attributes.color,
    c = new THREE.Color(0x69958e);
  let count = 0;
  for (let i = 0; i < pos.count; i++)
    if (
      pos.getZ(i) > 1.26 &&
      pos.getZ(i) < 1.28 &&
      Math.abs(col.getX(i) - c.r) < 1e-5 &&
      Math.abs(col.getY(i) - c.g) < 1e-5 &&
      Math.abs(col.getZ(i) - c.b) < 1e-5
    )
      count++;
  assert.ok(count >= 6);
});
