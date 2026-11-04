import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (url) => JSON.parse(readFileSync(new URL(url, import.meta.url)));
test("Tykeson upper frontage remains pinned and retains canopy and planting", () => {
  const old = read(
    "../../../assets/exterior-refinement/tykeson-before-upper-frontage-2026-11-04.json",
  );
  const bytes = readFileSync(
    new URL("../public/scene/tykeson-north-detail.json", import.meta.url),
  );
  const d = JSON.parse(bytes),
    presentation = read("../public/scene/presentation.json");
  assert.equal(
    presentation.exterior_details.find(
      (x) => x.url === "tykeson-north-detail.json",
    ).sha256,
    createHash("sha256").update(bytes).digest("hex"),
  );
  assert.equal(d.building_id, old.building_id);
  assert.equal(d.replace_building, false);
  assert.equal(d.objects.length, old.objects.length + 12);
  assert.deepEqual(d.objects.slice(34, 40), old.objects.slice(34, 40));
  for (const i of [3]) assert.deepEqual(d.objects[i], old.objects[i]);
  const upper = d.objects.slice(40);
  assert.equal(upper.length, 12);
  assert.ok(upper.every((o) => o.position[1] === 16.85));
  const spec = {
    version: 1,
    base_asset_sha256: d.base_asset_sha256,
    building_id: d.building_id,
    objects: d.objects.filter((o) => o.kind === "building"),
  };
  const group = createExteriorDetail(
    spec,
    spec.base_asset_sha256,
    new Set([spec.building_id]),
  );
  group.updateMatrixWorld(true);
  for (const y of [16.85, 20.45]) {
    const ray = new THREE.Raycaster(
      new THREE.Vector3(-463, y, 20),
      new THREE.Vector3(0, 0, 1),
    );
    const hits = ray.intersectObject(group, true);
    assert.ok(hits.length && hits[0].point.z < 30);
  }
});
