import test from "node:test";
import assert from "node:assert/strict";
import * as T from "three";
import { readFileSync } from "node:fs";
import { markPavingJoints, applyPavingJoints } from "../src/paving-joints.js";
const spec = JSON.parse(
  readFileSync(
    new URL("../public/scene/pilot-paving-joints.json", import.meta.url),
  ),
);
test("EMU radial paving is bounded and rejects invalid parameters before mutation", () => {
  const root = new T.Group(),
    g = new T.BufferGeometry();
  g.setAttribute(
    "position",
    new T.BufferAttribute(new Float32Array(5088 * 3), 3),
  );
  const mesh = new T.Mesh(g, new T.MeshStandardMaterial({ color: 0xcdbb9f }));
  mesh.name = "landscape-paving";
  mesh.userData.asset_kind = "landscape-surface";
  root.add(mesh);
  for (const radial of [
    { ...spec.radial, radius_m: 13 },
    { ...spec.radial, center_xz: [-500, 31] },
    { ...spec.radial, ring_spacing_m: 0 },
  ]) {
    assert.throws(() =>
      markPavingJoints(root, { ...spec, radial }, spec.base_asset_sha256),
    );
    assert.equal(mesh.userData.paving_joints, undefined);
  }
  markPavingJoints(root, spec, spec.base_asset_sha256);
  assert.equal(mesh.geometry, g);
  assert.deepEqual(mesh.userData.paving_joints.radial, spec.radial);
});
test("radial paving composes as a local material treatment with a distinct shader key", () => {
  const m = new T.MeshStandardMaterial(),
    style = {
      spacing_m: spec.spacing_m,
      width_m: spec.width_m,
      strength: spec.strength,
      radial: spec.radial,
    };
  applyPavingJoints(m, style);
  const shader = {
    vertexShader: "#include <begin_vertex>",
    fragmentShader: "#include <color_fragment>",
  };
  m.onBeforeCompile(shader, {});
  assert.match(shader.fragmentShader, /radialMask/);
  assert.match(shader.fragmentShader, /mix\(existingJoint/);
  assert.match(shader.fragmentShader, /brickLine/);
  assert.match(m.customProgramCacheKey(), /radial-/);
});
