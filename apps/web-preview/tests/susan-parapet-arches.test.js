import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
const oldBytes = readFileSync(
  new URL(
    "../../../assets/exterior-refinement/susan-before-parapet-arches-2026-11-10.json",
    import.meta.url,
  ),
);
const old = JSON.parse(oldBytes);
const d = JSON.parse(
  readFileSync(
    new URL("../public/scene/susan-roof-detail.json", import.meta.url),
  ),
);
test("Susan arch additions preserve all 463 prior components and collision contracts", () => {
  assert.equal(
    createHash("sha256").update(oldBytes).digest("hex"),
    "0e303860273701f0e7bb2b0c31487116b774d607e5b76b02acb50876f525c14a",
  );
  assert.equal(d.objects.length, 471);
  assert.deepEqual(d.objects.slice(0, 463), old.objects);
  assert.deepEqual(d.collision_boxes_enu_m, old.collision_boxes_enu_m);
  assert.equal(d.building_id, old.building_id);
  assert.equal(d.base_asset_sha256, old.base_asset_sha256);
  const make = (s) =>
    createExteriorDetail(s, s.base_asset_sha256, new Set([s.building_id]));
  assert.equal(make(d).children.length, make(old).children.length);
});
test("Susan arched motifs fit brick band without covering old glass or cap", () => {
  const extra = d.objects.slice(463);
  for (const o of extra) {
    assert.ok(o.position[1] - o.size[1] / 2 > 17.275);
    assert.ok(o.position[1] + o.size[1] / 2 < 18.58);
    assert.ok(o.position[2] - o.size[2] / 2 >= 168.62);
    assert.ok(o.position[2] + o.size[2] / 2 < 168.85);
  }
  const s = { ...d, objects: extra };
  const g = createExteriorDetail(
    s,
    s.base_asset_sha256,
    new Set([s.building_id]),
  );
  g.updateMatrixWorld(true);
  for (const x of [-455, -435]) {
    const ray = new THREE.Raycaster(
      new THREE.Vector3(x, 18.0, 170),
      new THREE.Vector3(0, 0, -1),
    );
    assert.ok(ray.intersectObject(g, true).length > 0);
  }
  for (const v of g.children[0].geometry.attributes.position.array)
    assert.ok(Number.isFinite(v));
});
