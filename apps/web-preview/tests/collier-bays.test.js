import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (p) => JSON.parse(readFileSync(new URL(p, import.meta.url)));
const current = read("../public/scene/collier-house-detail.json");
const old = read(
  "../../../assets/exterior-refinement/collier-before-bays-2026-11-04.json",
);
test("Collier upper bay projections preserve anchor and collision and produce tapered surfaces", () => {
  assert.equal(current.building_id, old.building_id);
  assert.deepEqual(current.collision_boxes_enu_m, old.collision_boxes_enu_m);
  const bays = current.objects.filter(
    (x) => x.shape === "bay-prism" && x.position[1] > 10,
  );
  assert.equal(bays.length, 2);
  const spec = {
    version: 1,
    base_asset_sha256: current.base_asset_sha256,
    building_id: current.building_id,
    objects: bays,
  };
  const root = createExteriorDetail(
    spec,
    spec.base_asset_sha256,
    new Set([spec.building_id]),
  );
  root.updateMatrixWorld(true);
  const ray = new THREE.Raycaster();
  for (const bay of bays) {
    const [x, y, z] = bay.position;
    ray.set(new THREE.Vector3(x, y, z - 5), new THREE.Vector3(0, 0, 1));
    let hit = ray.intersectObject(root, true)[0];
    assert.ok(hit);
    assert.ok(Math.abs(hit.point.z - (z - bay.size[2] / 2)) < 1e-4);
    assert.ok(y - bay.size[1] / 2 >= 9.4);
  }
});

test("Collier lower bays align with upper bays and retain conservative collision", () => {
  const upper = current.objects.filter(
    (x) => x.shape === "bay-prism" && x.position[1] === 11.4,
  );
  const lower = current.objects.filter(
    (x) => x.shape === "bay-prism" && x.position[1] === 7.4,
  );
  assert.equal(lower.length, 2);
  assert.equal(upper.length, 2);
  for (const b of lower) {
    const top = upper.find((u) => u.position[0] === b.position[0]);
    assert.ok(top);
    assert.equal(b.position[2], top.position[2]);
    assert.deepEqual(b.size, top.size);
  }
  assert.deepEqual(current.collision_boxes_enu_m, old.collision_boxes_enu_m);
  const porch = current.objects.find(
    (x) =>
      x.shape === "box" &&
      x.material === "roof-slate" &&
      x.position[0] === -345 &&
      x.position[1] === 9.35,
  );
  assert.ok(porch);
  assert.equal(porch.size[0], 6.6);
});
