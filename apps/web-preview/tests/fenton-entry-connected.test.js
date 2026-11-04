import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (p) => JSON.parse(readFileSync(new URL(p, import.meta.url)));
const data = read("../public/scene/fenton-south-detail.json"),
  before = read(
    "../../../assets/exterior-refinement/fenton-before-entry-connection-2026-11-04.json",
  );
test("Fenton entry arch frames a visible rectangular door and supports its balustrade", () => {
  assert.equal(data.building_id, before.building_id);
  assert.equal(data.objects.length, before.objects.length + 40);
  for (let i = 0; i < before.objects.length; i++) {
    if (i === 6) {
      assert.deepEqual(
        { ...data.objects[i], material: "dark" },
        before.objects[i],
      );
      continue;
    }
    assert.deepEqual(data.objects[i], before.objects[i]);
  }
  assert.equal(data.objects[6].material, "brick");
  const support = data.objects[155],
    bottomRail = data.objects[145],
    cornice = data.objects[3];
  assert.ok(
    Math.abs(
      support.position[1] +
        support.size[1] / 2 -
        (bottomRail.position[1] - bottomRail.size[1] / 2),
    ) < 0.001,
  );
  assert.ok(
    Math.abs(
      support.position[1] -
        support.size[1] / 2 -
        (cornice.position[1] + cornice.size[1] / 2),
    ) < 0.001,
  );
  const spec = {
    version: 1,
    base_asset_sha256: data.base_asset_sha256,
    building_id: data.building_id,
    objects: [
      data.objects[5],
      data.objects[6],
      data.objects[7],
      data.objects[9],
      ...data.objects.slice(156),
    ],
  };
  const root = createExteriorDetail(
    spec,
    spec.base_asset_sha256,
    new Set([spec.building_id]),
  );
  root.updateMatrixWorld(true);
  let ray = new THREE.Raycaster(
    new THREE.Vector3(-430, 7.3, -30.35),
    new THREE.Vector3(-1, 0, 0),
  );
  let hit = ray.intersectObject(root, true)[0];
  assert.ok(hit);
  assert.ok(hit.point.x > -435.1);
});
