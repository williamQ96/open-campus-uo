import test from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import { applyBatchPalette } from "../src/batch-palette.js";
function fixture() {
  const g = new THREE.BufferGeometry();
  g.setAttribute(
    "position",
    new THREE.Float32BufferAttribute([0, 0, 0, 1, 0, 0, 30, 0, 0], 3),
  );
  g.setAttribute(
    "color",
    new THREE.Float32BufferAttribute(
      [0.5, 0.4, 0.3, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3],
      3,
    ),
  );
  const m = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      vertexColors: true,
    }),
    mesh = new THREE.Mesh(g, m),
    root = new THREE.Group();
  mesh.name = "batch";
  mesh.userData = {
    asset_kind: "context-building-batch",
    asset_ids: ["roof-test"],
  };
  root.add(mesh);
  const spec = {
    version: 1,
    base_asset_sha256: "source",
    building_id: "roof-test",
    target_name: "batch",
    expected_vertices: 3,
    bounds: [-1, -1, -1, 2, 1, 1],
    groups: [
      {
        source_linear_4dp: [0.5, 0.4, 0.3],
        expected_vertices: 1,
        target_srgb: "#654d3b",
      },
      {
        source_linear_4dp: [0.2, 0.3, 0.4],
        expected_vertices: 1,
        target_srgb: "#526649",
      },
    ],
  };
  return { root, mesh, g, spec };
}
test("batch palette validates before cloning and changes only bounded source colors", () => {
  const { root, mesh, g, spec } = fixture(),
    original = Array.from(g.attributes.color.array),
    positions = Array.from(g.attributes.position.array);
  assert.deepEqual(applyBatchPalette(root, spec, "source"), [1, 1]);
  assert.notEqual(mesh.geometry, g);
  assert.deepEqual(Array.from(g.attributes.color.array), original);
  assert.deepEqual(
    Array.from(mesh.geometry.attributes.position.array),
    positions,
  );
  const c = mesh.geometry.attributes.color,
    target = new THREE.Color("#654d3b");
  assert.ok(Math.abs(c.getX(0) - target.r) < 1e-6);
  assert.deepEqual(Array.from(c.array.slice(6, 9)), original.slice(6, 9));
});
test("batch palette rejects wrong source, targets, counts and duplicated groups atomically", () => {
  for (const change of [
    (s) => (s.base_asset_sha256 = "other"),
    (s) => (s.building_id = "wrong"),
    (s) => (s.groups[0].expected_vertices = 2),
    (s) => s.groups.push({ ...s.groups[0] }),
  ]) {
    const { root, mesh, g, spec } = fixture();
    change(spec);
    assert.throws(() => applyBatchPalette(root, spec, "source"));
    assert.equal(mesh.geometry, g);
  }
});
