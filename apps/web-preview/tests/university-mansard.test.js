import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
const data = JSON.parse(
  readFileSync(
    new URL("../public/scene/university-hall-detail.json", import.meta.url),
  ),
);
const previous = JSON.parse(
  readFileSync(
    new URL(
      "../../../assets/exterior-refinement/university-before-mansard-2026-11-04.json",
      import.meta.url,
    ),
  ),
);
test("Mansard revision preserves all earlier non-roof components", () => {
  const affected = new Set([1, 3, 6, 160, 161, 162, 163, 164, 165, 166, 167]);
  assert.equal(data.objects.length, previous.objects.length + 10);
  for (let i = 0; i < previous.objects.length; i++)
    if (!affected.has(i))
      assert.deepEqual(data.objects[i], previous.objects[i]);
});
function render(objects) {
  let s = {
    version: 1,
    base_asset_sha256: data.base_asset_sha256,
    building_id: data.building_id,
    objects,
  };
  let root = createExteriorDetail(
    s,
    s.base_asset_sha256,
    new Set([s.building_id]),
  );
  root.updateMatrixWorld(true);
  return root;
}
test("University mansard has two distinct slopes and attached visible tower dormers", () => {
  const roofs = [data.objects[1], data.objects[3], data.objects[6]];
  assert.ok(roofs.every((o) => o.shape === "mansard"));
  let roof = render([roofs[0]]),
    ray = new THREE.Raycaster();
  function roofY(z) {
    ray.set(new THREE.Vector3(-457, 50, -125 + z), new THREE.Vector3(0, -1, 0));
    let h = ray.intersectObject(roof, true)[0];
    assert.ok(h);
    return h.point.y;
  }
  assert.ok(Math.abs(roofY(0) - 19.2) < 1e-4);
  let upper = roofY(6),
    lower = roofY(8);
  assert.ok(upper > lower && lower > 16);
  assert.ok((upper - lower) / 2 > (19.2 - upper) / 6);
  for (let i of [160, 162, 164, 166]) {
    let frame = data.objects[i],
      glass = data.objects[i + 1],
      tower = roofs.find((x) => x.position[0] === frame.position[0]);
    assert.ok(tower);
    let sign = Math.sign(frame.position[2] + 125);
    let surface =
      4.15 *
      (1 - (1 - 0.82) * ((frame.position[1] - (21.8 - 1.9)) / (0.75 * 3.8)));
    assert.ok(
      Math.abs(frame.position[2] + 125) - frame.size[2] / 2 < surface &&
        Math.abs(frame.position[2] + 125) + frame.size[2] / 2 > surface,
    );
    let group = render([tower, frame, glass]);
    ray.set(
      new THREE.Vector3(frame.position[0], frame.position[1], -125 + sign * 12),
      new THREE.Vector3(0, 0, -sign),
    );
    let hit = ray.intersectObject(group, true)[0];
    assert.ok(hit);
    assert.ok(Math.abs(hit.point.z - glass.position[2]) < 0.1);
  }
});
