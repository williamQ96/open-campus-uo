import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { addSquirrelEyes } from "../src/squirrel-detail.js";
async function fixture() {
  const d = await readFile(
    new URL("../public/animals/campus-squirrel.glb", import.meta.url),
  );
  return (
    await new GLTFLoader().parseAsync(
      d.buffer.slice(d.byteOffset, d.byteOffset + d.byteLength),
      "",
    )
  ).scene;
}
test("squirrel accents preserve geometry, bounds, batching and fur masks", async () => {
  const scene = await fixture(),
    source = scene.getObjectByName("Campus_squirrel_-_CC0_source"),
    original = source.geometry,
    material = source.material,
    expected = original.toNonIndexed();
  const info = addSquirrelEyes(scene),
    result = info.mesh.geometry;
  assert.equal(info.originalVertices, 2700);
  assert.equal(info.addedVertices, 480);
  for (const k of ["position", "normal"])
    assert.deepEqual(
      result.attributes[k].array.slice(0, expected.attributes[k].array.length),
      expected.attributes[k].array,
    );
  result.computeBoundingBox();
  assert.deepEqual(result.boundingBox, original.boundingBox);
  assert.equal(result.groups.length, 0);
  assert.equal(info.mesh.material.vertexColors, true);
  assert.equal(material.vertexColors, false);
  assert.notEqual(info.mesh.material, material);
  let light = 0,
    dark = 0;
  const colors = result.attributes.color;
  for (let i = 0; i < 2700; i++) {
    for (let c = 0; c < 3; c++)
      assert.ok(
        Number.isFinite(colors.array[i * 3 + c]) &&
          colors.array[i * 3 + c] >= 0.119 &&
          colors.array[i * 3 + c] <= 1.000001,
      );
    const r = colors.getX(i);
    if (r > 0.84) light++;
    if (r < 0.5) {
      dark++;
      assert.ok(
        result.attributes.position.getY(i) > 0.19,
        "nose must not darken paws",
      );
    }
  }
  assert.ok(light > 0 && dark > 0);
  for (let i = 2700; i < colors.count; i++)
    assert.ok(Math.abs(colors.getX(i) - 0.035) < 1e-7);
  assert.throws(
    () => addSquirrelEyes(scene),
    /source geometry or material changed/,
  );
  expected.dispose();
  result.dispose();
  info.mesh.material.dispose();
  original.dispose();
  material.dispose();
});
test("temporary geometry disposed without disposing caller-owned source", async () => {
  const scene = await fixture(),
    original = scene.getObjectByName("Campus_squirrel_-_CC0_source").geometry,
    disposed = [],
    dispose = THREE.BufferGeometry.prototype.dispose;
  THREE.BufferGeometry.prototype.dispose = function () {
    disposed.push(this);
    return dispose.call(this);
  };
  try {
    const info = addSquirrelEyes(scene);
    assert.equal(disposed.length, 3);
    assert.ok(!disposed.includes(original));
    assert.ok(!disposed.includes(info.mesh.geometry));
  } finally {
    THREE.BufferGeometry.prototype.dispose = dispose;
  }
});
test("missing or ambiguous squirrel sources rejected", async () => {
  assert.throws(
    () => addSquirrelEyes(new THREE.Group()),
    /missing or ambiguous/,
  );
  const s = await fixture();
  s.add(s.getObjectByName("Campus_squirrel_-_CC0_source").clone());
  assert.throws(() => addSquirrelEyes(s), /missing or ambiguous/);
});
