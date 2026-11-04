import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as T from "three";
import { markPavingJoints, applyPavingJoints } from "../src/paving-joints.js";
const read = (n) =>
  readFileSync(new URL(`../public/scene/${n}`, import.meta.url));
const config = JSON.parse(read("presentation.json")),
  bytes = read("pilot-paving-joints.json"),
  spec = JSON.parse(bytes);
test("paving treatment is source pinned and rejects unrelated or ambiguous geometry atomically", () => {
  assert.equal(
    createHash("sha256").update(bytes).digest("hex"),
    config.paving_joints_sha256,
  );
  assert.equal(spec.base_asset_sha256, config.asset_sha256);
  const root = new T.Group(),
    geo = new T.BufferGeometry();
  geo.setAttribute(
    "position",
    new T.BufferAttribute(new Float32Array(5088 * 3), 3),
  );
  const mesh = new T.Mesh(geo, new T.MeshStandardMaterial({ color: 0xcdbb9f }));
  mesh.name = "landscape-paving";
  mesh.userData.asset_kind = "landscape-surface";
  root.add(mesh);
  assert.throws(() => markPavingJoints(root, spec, "changed"));
  assert.equal(mesh.userData.paving_joints, undefined);
  markPavingJoints(root, spec, config.asset_sha256);
  assert.equal(mesh.userData.paving_joints.spacing_m, 2.5);
  assert.equal(mesh.geometry, geo);
  const clone = mesh.clone();
  root.add(clone);
  delete mesh.userData.paving_joints;
  assert.throws(() => markPavingJoints(root, spec, config.asset_sha256));
  assert.equal(mesh.userData.paving_joints, undefined);
});
test("paving composes with prior material callback and preserves shader cache distinctions", () => {
  const mat = new T.MeshStandardMaterial(),
    called = [];
  mat.onBeforeCompile = () => called.push("previous");
  applyPavingJoints(mat, { spacing_m: 2.5, width_m: 0.025, strength: 0.12 });
  const shader = {
    vertexShader: "#include <begin_vertex>",
    fragmentShader: "#include <color_fragment>",
  };
  mat.onBeforeCompile(shader, {});
  assert.deepEqual(called, ["previous"]);
  assert.match(shader.vertexShader, /pavingWorld/);
  assert.match(shader.fragmentShader, /pavingFade/);
  assert.match(mat.customProgramCacheKey(), /paving-joints-2.5-0.025-0.12/);
  assert.throws(() => applyPavingJoints(mat, spec));
});
