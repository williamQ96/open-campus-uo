import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (p) => JSON.parse(readFileSync(new URL(p, import.meta.url)));
const data = read("../public/scene/villard-east-detail.json");
const before = read(
  "../../../assets/exterior-refinement/villard-before-mansard-2026-11-04.json",
);
test("Villard roof refinement changes only five bounded roof profiles", () => {
  assert.equal(data.building_id, before.building_id);
  assert.deepEqual(data.collision_boxes_enu_m, before.collision_boxes_enu_m);
  assert.equal(data.objects.length, before.objects.length);
  const indices = new Set([1, 85, 88, 91, 94]);
  for (let i = 0; i < data.objects.length; i++) {
    if (!indices.has(i)) {
      assert.deepEqual(data.objects[i], before.objects[i]);
      continue;
    }
    assert.equal(before.objects[i].shape, "hip");
    assert.equal(data.objects[i].shape, "mansard");
    assert.deepEqual({ ...data.objects[i], shape: "hip" }, before.objects[i]);
    const roof = data.objects[i],
      spec = {
        version: 1,
        base_asset_sha256: data.base_asset_sha256,
        building_id: data.building_id,
        objects: [roof],
      };
    let root = createExteriorDetail(
      spec,
      spec.base_asset_sha256,
      new Set([spec.building_id]),
    );
    root.updateMatrixWorld(true);
    let ray = new THREE.Raycaster(),
      [x, y, z] = roof.position,
      [w, h] = roof.size;
    const sample = (dx) => {
      ray.set(new THREE.Vector3(x + dx, y + h, z), new THREE.Vector3(0, -1, 0));
      let hit = ray.intersectObject(root, true)[0];
      assert.ok(hit);
      return hit.point.y;
    };
    const top = sample(0),
      upper = sample(w * 0.34),
      lower = sample(w * 0.46);
    assert.ok(top > upper && upper > lower);
    assert.ok(Math.abs(top - (y + h / 2)) < 0.0001);
  }
});
