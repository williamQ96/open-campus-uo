import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
const data = JSON.parse(
  readFileSync(
    new URL("../public/scene/johnson-rear-detail.json", import.meta.url),
  ),
);
test("gable-on-hip roof has supported ridge, slopes and attached markers", () => {
  const roof = data.objects.find((o) => o.shape === "gable-hip");
  assert.ok(roof);
  const spec = {
    version: 1,
    base_asset_sha256: data.base_asset_sha256,
    building_id: data.building_id,
    objects: [roof],
  };
  const root = createExteriorDetail(
    spec,
    spec.base_asset_sha256,
    new Set([spec.building_id]),
  );
  root.updateMatrixWorld(true);
  const ray = new THREE.Raycaster();
  const sample = (x, z) => {
    ray.set(new THREE.Vector3(x, 100, z), new THREE.Vector3(0, -1, 0));
    const hit = ray.intersectObject(root, true)[0];
    assert.ok(hit);
    return hit.point.y;
  };
  const center = sample(-401, 42.5),
    edge = sample(-401, 54.5),
    end = sample(-413, 42.5);
  assert.ok(center > edge + 0.9);
  assert.ok(center > end + 0.7);
  assert.ok(Math.abs(center - 17.76) < 1e-5);
  for (const item of data.objects.slice(128, 134)) {
    const [x, y, z] = item.position,
      theta = item.rotation?.[2] || 0,
      half = item.size[0] / 2;
    for (const dx of [-half, half]) {
      const worldX = x + dx * Math.cos(theta),
        bottom =
          y + dx * Math.sin(theta) - (item.size[1] / 2) * Math.cos(theta),
        roofY = sample(worldX, z);
      const expected = item.material === "roof" ? 0 : 0.12;
      assert.ok(
        Math.abs(bottom - roofY - expected) < 0.005,
        `marker ${x} ${item.material} dx=${dx} delta=${bottom - roofY}`,
      );
    }
  }
  const invalid = structuredClone(spec);
  invalid.objects[0].size = [20, 1, 30];
  assert.throws(
    () =>
      createExteriorDetail(
        invalid,
        invalid.base_asset_sha256,
        new Set([invalid.building_id]),
      ),
    /width greater/,
  );
});
