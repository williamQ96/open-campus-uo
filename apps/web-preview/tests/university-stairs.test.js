import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (url) => JSON.parse(readFileSync(new URL(url, import.meta.url)));
test("Both University Hall stairs retain old components and gain grounded sloping wings and rails", () => {
  const old = read(
    "../../../assets/exterior-refinement/university-before-entry-stairs-2026-11-04.json",
  );
  const data = read("../public/scene/university-hall-detail.json");
  assert.deepEqual(data.objects.slice(0, old.objects.length), old.objects);
  assert.equal(data.objects.length, old.objects.length + 10);
  assert.equal(data.collision_boxes_enu_m.length, 6);
  const added = data.objects.slice(-10);
  assert.equal(added.filter((o) => o.shape === "stair-wing").length, 4);
  for (const wing of added.filter((o) => o.shape === "stair-wing")) {
    const spec = {
      version: 1,
      building_id: data.building_id,
      base_asset_sha256: data.base_asset_sha256,
      objects: [wing],
    };
    const root = createExteriorDetail(
      spec,
      spec.base_asset_sha256,
      new Set([spec.building_id]),
    );
    root.updateMatrixWorld(true);
    const ray = new THREE.Raycaster();
    function top(x) {
      ray.set(
        new THREE.Vector3(x, 20, wing.position[2]),
        new THREE.Vector3(0, -1, 0),
      );
      const hit = ray.intersectObject(root, true)[0];
      assert.ok(hit);
      return hit.point.y;
    }
    const left = top(wing.position[0] - 0.9),
      right = top(wing.position[0] + 0.9);
    assert.ok(wing.position[0] < -450 ? right > left : left > right);
    assert.ok(Math.min(left, right) > 4.7 && Math.max(left, right) < 6.1);
    assert.ok(wing.position[1] - wing.size[1] / 2 <= 4.1 + 1e-6);
  }
  assert.equal(added.filter((o) => o.material === "metal").length, 6);
});
