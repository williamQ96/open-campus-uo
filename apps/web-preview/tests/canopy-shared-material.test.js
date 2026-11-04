import test from "node:test";
import assert from "node:assert/strict";
import * as T from "three";
import { applyCanopyTone } from "../src/canopy-tone.js";
test("canopy tone does not mutate a leaf material shared by other planting", () => {
  const root = new T.Group(),
    canopies = new T.Group();
  canopies.name = "vegetation";
  root.add(canopies);
  const records = [];
  let shared;
  for (let i = 0; i < 3; i++) {
    const geo = new T.BufferGeometry();
    geo.setAttribute(
      "position",
      new T.Float32BufferAttribute([0, 0, 0, 1, 1, 1, 2, 0, 2], 3),
    );
    const mat = new T.MeshStandardMaterial({ color: 0x658b54 });
    mat.name = "leaf" + i;
    const mesh = new T.Mesh(geo, mat);
    mesh.name = "canopy" + i;
    canopies.add(mesh);
    records.push({
      name: mesh.name,
      material: mat.name,
      color: mat.color.getHexString(),
      vertices: 3,
    });
    if (i === 0) shared = mat;
  }
  const shrub = new T.Mesh(new T.BoxGeometry(), shared);
  shrub.name = "planting";
  root.add(shrub);
  const spec = {
    version: 1,
    operation: "canopy-tone-v1",
    base_asset_sha256: "source",
    target_name: "vegetation",
    strength: 0.18,
    meshes: records,
  };
  applyCanopyTone(root, spec, "source");
  assert.equal(shrub.material, shared);
  assert.equal(shared.vertexColors, false);
  assert.equal(shrub.geometry.hasAttribute("color"), false);
  assert.notEqual(canopies.children[0].material, shared);
  assert.equal(canopies.children[0].material.vertexColors, true);
  assert.equal(canopies.children[0].geometry.attributes.color.count, 3);
});
