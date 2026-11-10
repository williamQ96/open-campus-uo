import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
const bytes = readFileSync(
    new URL(
      "../../../assets/exterior-refinement/chapman-before-west-frieze-2026-11-10.json",
      import.meta.url,
    ),
  ),
  old = JSON.parse(bytes),
  d = JSON.parse(
    readFileSync(
      new URL("../public/scene/chapman-west-detail.json", import.meta.url),
    ),
  );
const make = (s) =>
  createExteriorDetail(s, s.base_asset_sha256, new Set([s.building_id]));
test("Chapman west relief preserves all 144 objects and merged budget", () => {
  assert.equal(
    createHash("sha256").update(bytes).digest("hex"),
    "c517238075ef611d80920f99a0036e7e711c65d69fe9b6b74408cc937ff27009",
  );
  assert.equal(d.objects.length, 265);
  assert.deepEqual(d.objects.slice(0, 144), old.objects);
  assert.deepEqual(d.collision_boxes_enu_m, old.collision_boxes_enu_m);
  assert.equal(d.base_asset_sha256, old.base_asset_sha256);
  assert.equal(d.building_id, old.building_id);
  assert.equal(d.replace_building, false);
  assert.equal(make(d).children.length, make(old).children.length);
});
test("Chapman relief fits wall with open arch centers and clears glazing", () => {
  const g = make(d),
    b = make(old);
  g.updateMatrixWorld(true);
  b.updateMatrixWorld(true);
  const hit = (root, y, z) =>
    new THREE.Raycaster(
      new THREE.Vector3(-530, y, z),
      new THREE.Vector3(1, 0, 0),
    ).intersectObject(root, true)[0]?.point.x;
  for (let i = 0; i < 12; i++) {
    const z = 21.875 + i * 0.75;
    assert.ok(Math.abs(hit(g, 15.25, z - 0.22) + 523.21) < 0.001);
    assert.ok(Math.abs(hit(g, 15.25, z) + 523.17) < 0.001);
  }
  for (const z of [24.65, 26, 27.35])
    assert.equal(hit(g, 12, z), hit(b, 12, z));
  const extra = make({ ...d, objects: d.objects.slice(144) }),
    bounds = new THREE.Box3().setFromObject(extra);
  assert.ok(bounds.min.y > 13.9);
  assert.ok(bounds.max.y < 15.825);
  assert.ok(bounds.min.z >= 21 && bounds.max.z <= 31);
  assert.ok(bounds.max.x > -523.06);
  for (const c of g.children)
    for (const v of c.geometry.attributes.position.array)
      assert.ok(Number.isFinite(v));
});
