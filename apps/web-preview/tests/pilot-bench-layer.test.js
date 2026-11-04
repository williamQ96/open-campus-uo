import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import { applyVegetationPatch } from "../src/vegetation-patch.js";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (n) =>
  readFileSync(new URL("../public/scene/" + n, import.meta.url));
const cfg = JSON.parse(read("presentation.json"));
const bytes = read("pilot-bench-back-suppression.json"),
  patch = JSON.parse(bytes),
  detailBytes = read("pilot-bench-detail.json"),
  detail = JSON.parse(detailBytes);
test("nine source-pinned bench backs are selected atomically and non-target geometry remains", () => {
  assert.equal(
    createHash("sha256").update(bytes).digest("hex"),
    cfg.furniture_patch_sha256,
  );
  assert.equal(patch.positions_gltf.length, 72);
  assert.equal(patch.expected_matches, 216);
  const target = new THREE.Group();
  target.name = "furniture";
  const points = patch.positions_gltf.flatMap((p) => [...p, ...p, ...p]);
  points.push(777, 777, 777);
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(points, 3));
  target.add(new THREE.Mesh(g, new THREE.MeshBasicMaterial()));
  const root = new THREE.Group();
  root.add(target);
  const before = Array.from(g.attributes.position.array);
  assert.throws(
    () => applyVegetationPatch(root, patch, "wrong"),
    /does not match/,
  );
  assert.deepEqual(Array.from(g.attributes.position.array), before);
  assert.equal(applyVegetationPatch(root, patch, cfg.asset_sha256), 216);
  const p = g.attributes.position;
  assert.deepEqual([p.getX(216), p.getY(216), p.getZ(216)], [777, 777, 777]);
});
test("environment details reject building impersonation and retain their source hash", () => {
  const rec = cfg.exterior_details.find(
    (x) => x.url === "pilot-bench-detail.json",
  );
  assert.equal(
    rec.sha256,
    createHash("sha256").update(detailBytes).digest("hex"),
  );
  const ids = new Set();
  const group = createExteriorDetail(detail, cfg.asset_sha256, ids);
  assert.ok(group.children.every((x) => x.userData.asset_kind === "prop"));
  assert.throws(() =>
    createExteriorDetail(
      { ...detail, building_id: "anything" },
      cfg.asset_sha256,
      ids,
    ),
  );
  assert.throws(() =>
    createExteriorDetail(
      { ...detail, replace_building: true },
      cfg.asset_sha256,
      ids,
    ),
  );
  assert.throws(() =>
    createExteriorDetail(
      { ...detail, objects: [{ ...detail.objects[0], kind: "building" }] },
      cfg.asset_sha256,
      ids,
    ),
  );
});
import { mergeEnvironmentDetail } from "../src/exterior-detail.js";
test("bench batch merges into the verified original material without another draw object", () => {
  const root = new THREE.Group(),
    furniture = new THREE.Group();
  furniture.name = "furniture";
  root.add(furniture);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(new Float32Array(432 * 3), 3),
  );
  geo.setAttribute(
    "normal",
    new THREE.Float32BufferAttribute(new Float32Array(432 * 3), 3),
  );
  const target = new THREE.Mesh(
    geo,
    new THREE.MeshStandardMaterial({ color: 0x77634f }),
  );
  target.name = "furniture_1";
  furniture.add(target);
  const layer = createExteriorDetail(detail, cfg.asset_sha256, new Set());
  root.add(layer);
  assert.throws(() =>
    mergeEnvironmentDetail(root, layer, { ...detail, merge_target: "other" }),
  );
  assert.equal(layer.parent, root);
  assert.equal(target.geometry.attributes.position.count, 432);
  mergeEnvironmentDetail(root, layer, detail);
  assert.equal(layer.parent, null);
  assert.ok(target.geometry.attributes.position.count > 432);
  assert.equal(target.material.color.getHexString(), "77634f");
});
