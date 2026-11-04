import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { applySourceTrianglePatch } from "../src/source-triangle-patch.js";
const read = (p) => readFileSync(new URL(p, import.meta.url));
const spec = JSON.parse(read("../public/scene/fenton-south-detail.json"));
const bytes = read("../public/scene/campus-expanded.glb");
async function load() {
  const data = bytes.buffer.slice(
    bytes.byteOffset,
    bytes.byteOffset + bytes.byteLength,
  );
  return (await new GLTFLoader().parseAsync(data, "")).scene;
}
function target(root) {
  let result;
  root.traverse((o) => {
    if (o.isMesh && o.userData.asset_id === spec.building_id) result = o;
  });
  return result;
}
test("Fenton source patch verifies every triangle and preserves all other indices and attributes", async () => {
  const root = await load(),
    mesh = target(root),
    old = mesh.geometry,
    original = Array.from(old.index.array),
    patch = spec.source_triangle_patch;
  assert.equal(
    createHash("sha256").update(bytes).digest("hex"),
    spec.base_asset_sha256,
  );
  assert.equal(patch.triangles.length, 168);
  const removed = new Set(patch.triangles.map((x) => x[0]));
  const result = applySourceTrianglePatch(root, spec, spec.base_asset_sha256);
  assert.equal(result.original, old);
  assert.equal(result.removed, 168);
  assert.notEqual(mesh.geometry, old);
  const expected = original.filter((_, i) => !removed.has(Math.floor(i / 3)));
  assert.deepEqual(Array.from(mesh.geometry.index.array), expected);
  for (const key of ["position", "normal", "color"])
    assert.deepEqual(
      Array.from(mesh.geometry.attributes[key].array),
      Array.from(old.attributes[key].array),
    );
  assert.deepEqual(Array.from(old.index.array), original);
});
test("Fenton source patch rejects source hash, changed vertices, changed indices, ambiguous and duplicate targets atomically", async () => {
  const root = await load(),
    mesh = target(root),
    original = mesh.geometry;
  assert.throws(() => applySourceTrianglePatch(root, spec, "changed"));
  assert.equal(mesh.geometry, original);
  const vertex = spec.source_triangle_patch.vertices[0][0];
  original.attributes.position.setX(
    vertex,
    original.attributes.position.getX(vertex) + 1,
  );
  assert.throws(() =>
    applySourceTrianglePatch(root, spec, spec.base_asset_sha256),
  );
  assert.equal(mesh.geometry, original);
  original.attributes.position.setX(
    vertex,
    spec.source_triangle_patch.vertices[0][1],
  );
  const tri = spec.source_triangle_patch.triangles[0][0];
  const previous = original.index.getX(tri * 3);
  original.index.setX(tri * 3, previous + 1);
  assert.throws(() =>
    applySourceTrianglePatch(root, spec, spec.base_asset_sha256),
  );
  assert.equal(mesh.geometry, original);
  original.index.setX(tri * 3, previous);
  const duplicate = mesh.clone();
  root.add(duplicate);
  assert.throws(() =>
    applySourceTrianglePatch(root, spec, spec.base_asset_sha256),
  );
  assert.equal(mesh.geometry, original);
  root.remove(duplicate);
  const invalid = structuredClone(spec);
  invalid.source_triangle_patch.triangles.push(
    invalid.source_triangle_patch.triangles[0],
  );
  assert.throws(() =>
    applySourceTrianglePatch(root, invalid, spec.base_asset_sha256),
  );
  assert.equal(mesh.geometry, original);
});
