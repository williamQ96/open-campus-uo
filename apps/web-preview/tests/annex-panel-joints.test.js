import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
const bytes = readFileSync(
  new URL(
    "../../../assets/exterior-refinement/annex-before-panel-joints-2026-11-10.json",
    import.meta.url,
  ),
);
const old = JSON.parse(bytes),
  d = JSON.parse(
    readFileSync(
      new URL(
        "../public/scene/gerlinger-annex-correction.json",
        import.meta.url,
      ),
    ),
  );
const make = (s) =>
  createExteriorDetail(s, s.base_asset_sha256, new Set([s.building_id]));
test("Annex joints preserve other 83 objects, envelope and merged budget", () => {
  assert.equal(
    createHash("sha256").update(bytes).digest("hex"),
    "debbf767b3995a149757264323bd8ce8e7d6e50097c48d53007d0aa54215954c",
  );
  assert.equal(d.objects.length, 91);
  for (let i = 0; i < 84; i++)
    if (i !== 2) assert.deepEqual(d.objects[i], old.objects[i]);
  assert.deepEqual(d.collision_boxes_enu_m, old.collision_boxes_enu_m);
  assert.equal(d.building_id, old.building_id);
  assert.equal(d.replace_building, true);
  assert.equal(d.base_asset_sha256, old.base_asset_sha256);
  assert.equal(make(d).children.length, make(old).children.length);
  const part = { ...d, objects: [d.objects[2], ...d.objects.slice(84)] },
    before = { ...old, objects: [old.objects[2]] };
  const a = new THREE.Box3().setFromObject(make(part)),
    b = new THREE.Box3().setFromObject(make(before));
  for (const axis of ["x", "y", "z"]) {
    assert.ok(Math.abs(a.min[axis] - b.min[axis]) < 0.0001);
    assert.ok(Math.abs(a.max[axis] - b.max[axis]) < 0.0001);
  }
});
test("Annex joints are real 30mm recesses and retained face is unchanged", () => {
  const g = make(d);
  g.updateMatrixWorld(true);
  const hit = (x, y) => {
    const r = new THREE.Raycaster(
      new THREE.Vector3(x, y, 230),
      new THREE.Vector3(0, 0, 1),
    );
    return r.intersectObject(g, true)[0].point.z;
  };
  for (const x of [-473.88, -470.08, -466.28, -462.48, -458.68]) {
    assert.ok(Math.abs(hit(x, 19) - 241.75) < 0.0001);
    assert.ok(Math.abs(hit(x + 0.12, 19) - 241.72) < 0.0001);
    assert.ok(Math.abs(hit(x, 16.55) - 241.72) < 0.0001);
  }
  for (const o of [d.objects[2], ...d.objects.slice(84)])
    assert.equal(o.material, "concrete");
  for (const c of g.children)
    for (const v of c.geometry.attributes.position.array)
      assert.ok(Number.isFinite(v));
});
