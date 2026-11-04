import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import { applyBuildingRoofSlope } from "../src/building-roof-slope.js";
const read = (n) =>
  readFileSync(new URL("../public/scene/" + n, import.meta.url));
const c = JSON.parse(read("presentation.json")),
  raw = read("clinical-roof-slope.json"),
  spec = JSON.parse(raw);
function fixture() {
  let root = new THREE.Group(),
    g = new THREE.BufferGeometry();
  g.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(
      [-670, 15.5, 0, -672, 15, 0, -675, 14, 0, -673, 12, 1],
      3,
    ),
  );
  g.setAttribute(
    "normal",
    new THREE.Float32BufferAttribute([0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], 3),
  );
  const f = spec.roof_feature_rgb8.map((v) => v / 255);
  g.setAttribute(
    "color",
    new THREE.Float32BufferAttribute(
      [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, ...f, 0.5, 0.5, 0.5],
      3,
    ),
  );
  g.setIndex([0, 1, 3, 0, 3, 2]);
  let m = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      vertexColors: true,
      roughness: 0.9,
      side: THREE.DoubleSide,
    }),
    mesh = new THREE.Mesh(g, m);
  mesh.name = spec.building_id;
  mesh.userData = { asset_kind: "building", asset_id: spec.building_id };
  root.add(mesh);
  return { root, mesh };
}
test("roof patch is hash-pinned, bounded and preserves below-roof geometry", () => {
  assert.equal(
    c.building_roof_patches.find((e) => e.url === "clinical-roof-slope.json")
      .sha256,
    createHash("sha256").update(raw).digest("hex"),
  );
  assert.equal(spec.base_asset_sha256, c.asset_sha256);
  const { root, mesh } = fixture(),
    old = mesh.geometry,
    oldP = old.attributes.position,
    oldN = old.attributes.normal,
    s = { ...spec, expected_vertex_count: 4, expected_selected_vertices: 2 };
  assert.equal(applyBuildingRoofSlope(root, s, c.asset_sha256), 2);
  const p = mesh.geometry.attributes.position,
    n = mesh.geometry.attributes.normal;
  for (let i = 0; i < 4; i++) {
    assert.equal(p.getX(i), oldP.getX(i));
    assert.equal(p.getZ(i), oldP.getZ(i));
    assert.ok(Math.abs(p.getY(i) - oldP.getY(i)) <= s.max_displacement_m);
  }
  for (let i of [1, 3]) {
    assert.equal(p.getY(i), oldP.getY(i));
    for (let j = 0; j < 3; j++)
      assert.equal(n.array[i * 3 + j], oldN.array[i * 3 + j]);
  }
  assert.ok([...n.array].every(Number.isFinite));
});
test("roof patch rejects bad source and selection before any mutation", () => {
  const { root, mesh } = fixture(),
    old = mesh.geometry,
    s = { ...spec, expected_vertex_count: 4, expected_selected_vertices: 3 };
  assert.throws(() => applyBuildingRoofSlope(root, s, c.asset_sha256));
  assert.equal(mesh.geometry, old);
  assert.throws(() =>
    applyBuildingRoofSlope(
      root,
      { ...s, expected_selected_vertices: 2 },
      "bad",
    ),
  );
  assert.equal(mesh.geometry, old);
});
