import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import {
  createExteriorDetail,
  mergeEnvironmentDetail,
} from "../src/exterior-detail.js";
const read = (n) =>
    readFileSync(new URL("../public/scene/" + n, import.meta.url)),
  cfg = JSON.parse(read("presentation.json")),
  bytes = read("pilot-lamp-detail.json"),
  spec = JSON.parse(bytes);
test("eight reusable lamp detail sets retain source pin and do not impersonate buildings", () => {
  assert.equal(spec.objects.length, 40);
  assert.equal(
    new Set(spec.objects.map((o) => `${o.position[0]},${o.position[2]}`)).size,
    8,
  );
  assert.ok(
    spec.objects.every(
      (o) =>
        o.kind === "prop" &&
        o.material === "lamp-metal" &&
        o.shape === "column",
    ),
  );
  assert.equal(
    createHash("sha256").update(bytes).digest("hex"),
    cfg.exterior_details.find((e) => e.url === "pilot-lamp-detail.json").sha256,
  );
  assert.throws(() => createExteriorDetail(spec, "wrong", new Set()));
});
test("lamp components merge only into the verified metal furniture batch", () => {
  const root = new THREE.Group(),
    f = new THREE.Group();
  f.name = "furniture";
  root.add(f);
  const g = new THREE.BufferGeometry();
  g.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(new Float32Array(960 * 3), 3),
  );
  g.setAttribute(
    "normal",
    new THREE.Float32BufferAttribute(new Float32Array(960 * 3), 3),
  );
  const target = new THREE.Mesh(
    g,
    new THREE.MeshStandardMaterial({ color: 0x3f514b }),
  );
  target.name = "furniture_2";
  f.add(target);
  const layer = createExteriorDetail(spec, cfg.asset_sha256, new Set());
  root.add(layer);
  assert.throws(() =>
    mergeEnvironmentDetail(root, layer, {
      ...spec,
      merge_target: "furniture_1",
    }),
  );
  assert.equal(layer.parent, root);
  mergeEnvironmentDetail(root, layer, spec);
  assert.equal(layer.parent, null);
  assert.ok(target.geometry.attributes.position.count > 960);
});
