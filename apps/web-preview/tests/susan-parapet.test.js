import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (p) => JSON.parse(readFileSync(new URL(p, import.meta.url)));
const d = read(
    "../../../assets/exterior-refinement/susan-before-courtyard-2026-11-04.json",
  ),
  old = read(
    "../../../assets/exterior-refinement/susan-before-parapet-2026-11-04.json",
  );
function make(objects) {
  const s = {
    version: 1,
    base_asset_sha256: d.base_asset_sha256,
    building_id: d.building_id,
    objects,
  };
  const r = createExteriorDetail(
    s,
    s.base_asset_sha256,
    new Set([s.building_id]),
  );
  r.updateMatrixWorld(true);
  return r;
}
test("Susan parapets connect to roof, expose their glazing and preserve unrelated components", () => {
  assert.equal(d.building_id, old.building_id);
  assert.deepEqual(d.collision_boxes_enu_m, old.collision_boxes_enu_m);
  assert.equal(d.objects.length, old.objects.length + 2);
  const affected = new Set([
    182, 183, 184, 185, 202, 203, 204, 205, 406, 407, 408, 409, 426, 427, 428,
    429,
  ]);
  for (let i = 0; i < old.objects.length; i++)
    if (!affected.has(i)) assert.deepEqual(d.objects[i], old.objects[i]);
  const ray = new THREE.Raycaster(),
    roof = make([d.objects[2]]);
  for (const [x, i, bodyIndex] of [
    [-455, 182, 458],
    [-435, 202, 459],
  ]) {
    const body = d.objects[bodyIndex],
      frame = d.objects[i],
      glass = d.objects[i + 1],
      cap = d.objects[i + 3];
    assert.equal(body.position[0], x);
    assert.ok(
      body.position[1] + body.size[1] / 2 >=
        cap.position[1] - cap.size[1] / 2 - 0.1,
    );
    ray.set(new THREE.Vector3(x, 30, 167.3), new THREE.Vector3(0, -1, 0));
    const hit = ray.intersectObject(roof, true)[0];
    assert.ok(hit);
    assert.ok(
      hit.point.y > body.position[1] - body.size[1] / 2 &&
        hit.point.y < body.position[1] + body.size[1] / 2,
    );
    const group = make([body, frame, glass]);
    ray.set(
      new THREE.Vector3(x + 0.18, 16.25, 175),
      new THREE.Vector3(0, 0, -1),
    );
    const front = ray.intersectObject(group, true)[0];
    assert.ok(front);
    assert.ok(
      Math.abs(front.point.z - (glass.position[2] + glass.size[2] / 2)) < 0.001,
    );
  }
});
