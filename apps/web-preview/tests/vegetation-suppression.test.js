import { test } from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import { applyVegetationPatch } from "../src/vegetation-patch.js";
test("suppression collapses only the source-matched vertices and rejects ambiguous transforms", () => {
  const root = new THREE.Group(),
    target = new THREE.Group();
  target.name = "vegetation";
  root.add(target);
  const g = new THREE.BufferGeometry();
  g.setAttribute(
    "position",
    new THREE.Float32BufferAttribute([0, 1, 2, 0, 1, 2, 5, 6, 7], 3),
  );
  target.add(new THREE.Mesh(g));
  const p = {
    version: 1,
    base_asset_sha256: "base",
    target_name: "vegetation",
    positions_gltf: [[0, 1, 2]],
    collapse_gltf: [3, 4, 5],
    tolerance_m: 0.0001,
    expected_matches: 2,
  };
  assert.throws(() =>
    applyVegetationPatch(root, { ...p, delta_gltf: [0, 0, 0] }, "base"),
  );
  assert.deepEqual(
    [...g.attributes.position.array],
    [0, 1, 2, 0, 1, 2, 5, 6, 7],
  );
  assert.equal(applyVegetationPatch(root, p, "base"), 2);
  assert.deepEqual(
    [...g.attributes.position.array],
    [3, 4, 5, 3, 4, 5, 5, 6, 7],
  );
});
