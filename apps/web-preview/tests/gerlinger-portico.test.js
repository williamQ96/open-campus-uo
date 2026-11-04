import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (u) => JSON.parse(readFileSync(new URL(u, import.meta.url)));
test("Gerlinger entry canopy preserves existing geometry and keeps door glazing visible", () => {
  const d = read("../public/scene/gerlinger-east-detail.json"),
    old = read(
      "../../../assets/exterior-refinement/gerlinger-before-portico-2026-11-04.json",
    );
  assert.deepEqual(d.objects.slice(0, old.objects.length), old.objects);
  assert.equal(d.objects.length, old.objects.length + 10);
  const added = d.objects.slice(-10),
    columns = added.filter((o) => o.shape === "column");
  assert.equal(columns.length, 2);
  assert.deepEqual(
    columns.map((o) => o.position[2]),
    [208.15, 211.85],
  );
  const header = added.at(-1),
    upper = d.objects[39];
  assert.ok(
    header.position[1] + header.size[1] / 2 <
      upper.position[1] - upper.size[1] / 2,
  );
  const spec = {
    version: 1,
    base_asset_sha256: d.base_asset_sha256,
    building_id: d.building_id,
    objects: d.objects.filter((o) => o.kind === "building"),
  };
  const root = createExteriorDetail(
    spec,
    spec.base_asset_sha256,
    new Set([spec.building_id]),
  );
  root.updateMatrixWorld(true);
  const ray = new THREE.Raycaster(
    new THREE.Vector3(-340, 11, 210),
    new THREE.Vector3(-1, 0, 0),
  );
  const hits = ray.intersectObject(root, true);
  assert.ok(hits.length);
  assert.ok(hits[0].point.x < -358 && hits[0].point.x > -359);
});
