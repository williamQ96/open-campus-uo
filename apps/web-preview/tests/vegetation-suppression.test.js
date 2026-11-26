import { test } from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import {
  applyPilotTreeClearance,
  applyRegisteredPilotTrees,
  applyVegetationPatch,
} from "../src/vegetation-patch.js";
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

test("registration transforms only selected tree vertices and normals after all anchors match", () => {
  const group = new THREE.Group();
  group.name = "vegetation";
  const points = [0, 0, 0, 0, 2, 0, 2, 1, 0, 8, 8, 8];
  const parts = ["stem", "crown"].map((name) => {
    const geometry = new THREE.BufferGeometry();
    geometry.setIndex([0, 1, 2, 1, 2, 3]);
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(points, 3),
    );
    geometry.setAttribute(
      "normal",
      new THREE.Float32BufferAttribute([1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], 3),
    );
    const mesh = new THREE.Mesh(geometry);
    mesh.name = name;
    group.add(mesh);
    return {
      name,
      vertices: 4,
      runs: [[0, 3]],
      anchors: [
        [0, 0, 0, 0],
        [1, 0, 2, 0],
        [2, 2, 1, 0],
      ],
    };
  });
  const spec = {
    version: 1,
    operation: "registered-pilot-tree-fit-v1",
    base_asset_sha256: "base",
    trees: [
      {
        index: 9,
        origin: [0, 0, 0],
        target: [4, 3, 5],
        scale: [2, 0.5, 2],
        parts,
      },
    ],
  };
  parts[1].anchors[1][2] = 3;
  assert.throws(
    () => applyRegisteredPilotTrees(group, spec, "base", 1),
    /anchors/,
  );
  for (const { geometry } of group.children)
    assert.deepEqual([...geometry.getAttribute("position").array], points);
  parts[1].anchors[1][2] = 2;
  assert.equal(applyRegisteredPilotTrees(group, spec, "base", 1), 1);
  for (const { geometry } of group.children) {
    assert.deepEqual(
      [...geometry.getAttribute("position").array],
      [4, 3, 5, 4, 4, 5, 8, 3.5, 5, 8, 8, 8],
    );
    assert.deepEqual([...geometry.index.array], [0, 1, 2, 1, 2, 3]);
    const normal = geometry.getAttribute("normal");
    assert.ok(Math.abs(normal.getY(0) - 2 / Math.hypot(0.5, 2)) < 1e-6);
    assert.deepEqual(geometry.boundingBox.min.toArray(), [4, 3, 5]);
  }
});

test("pilot tree triangle suppression is atomic across foliage and understory", () => {
  const root = new THREE.Group();
  function plant(groupName) {
    const group = new THREE.Group();
    group.name = groupName;
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(new Float32Array(18), 3),
    );
    geometry.setIndex([0, 1, 2, 3, 4, 5]);
    const mesh = new THREE.Mesh(geometry);
    mesh.name = groupName + "_1";
    group.add(mesh);
    root.add(group);
    return geometry;
  }
  const tree = plant("vegetation");
  const shrub = plant("understory");
  const entry = (group, last) => ({
    group,
    name: group + "_1",
    vertices: 6,
    triangles: 2,
    spans: [[0, 1, 0, 1, last]],
  });
  const spec = {
    version: 1,
    operation: "pilot-tree-triangle-suppression-v1",
    base_asset_sha256: "base",
    suppressed_trees: 1,
    meshes: [entry("vegetation", 2), entry("understory", 5)],
  };
  assert.throws(() => applyPilotTreeClearance(root, spec, "base", 1), /spans/);
  assert.equal(tree.index.count, 6);
  assert.equal(shrub.index.count, 6);
  spec.meshes[1] = entry("understory", 2);
  assert.equal(applyPilotTreeClearance(root, spec, "base", 1), 1);
  assert.deepEqual([...tree.index.array], [3, 4, 5]);
  assert.deepEqual([...shrub.index.array], [3, 4, 5]);
});
