import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import { createFernGeometry } from "../src/fern-geometry.js";
import {
  createExteriorDetail,
  mergeEnvironmentDetail,
} from "../src/exterior-detail.js";
const read = (n) =>
  readFileSync(new URL("../public/scene/" + n, import.meta.url));
const cfg = JSON.parse(read("presentation.json")),
  p = read("pilot-fern-suppression.json"),
  patch = JSON.parse(p),
  d = read("pilot-fern-detail.json"),
  spec = JSON.parse(d);
test("fern geometry is finite, bounded and source-pinned to three existing positions", () => {
  const geo = createFernGeometry();
  geo.computeBoundingBox();
  assert.ok([...geo.attributes.position.array].every(Number.isFinite));
  assert.ok(geo.boundingBox.min.x >= -1.24 && geo.boundingBox.max.x <= 1.24);
  assert.ok(geo.boundingBox.min.z >= -1.24 && geo.boundingBox.max.z <= 1.24);
  assert.equal(spec.objects.length, 3);
  assert.equal(patch.positions_gltf.length, 192);
  assert.equal(patch.expected_matches, 720);
  assert.equal(
    createHash("sha256").update(p).digest("hex"),
    cfg.fern_patch_sha256,
  );
  assert.equal(
    createHash("sha256").update(d).digest("hex"),
    cfg.exterior_details.find((x) => x.url === "pilot-fern-detail.json").sha256,
  );
  assert.throws(() => createExteriorDetail(spec, "changed", new Set()));
});
test("fern foliage merges only into the source-matched understory material", () => {
  const root = new THREE.Group(),
    under = new THREE.Group();
  under.name = "understory";
  root.add(under);
  const g = new THREE.BufferGeometry();
  g.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(new Float32Array(264 * 3), 3),
  );
  g.setAttribute(
    "normal",
    new THREE.Float32BufferAttribute(new Float32Array(264 * 3), 3),
  );
  const target = new THREE.Mesh(
    g,
    new THREE.MeshStandardMaterial({ color: 0x829e59 }),
  );
  target.name = "understory_2";
  under.add(target);
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
  assert.ok(target.geometry.attributes.position.count > 264);
});
