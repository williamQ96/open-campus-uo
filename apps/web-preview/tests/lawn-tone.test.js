import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as T from "three";
import { markLawnTone, applyLawnTone } from "../src/lawn-tone.js";
const read = (n) =>
  readFileSync(new URL(`../public/scene/${n}`, import.meta.url));
const config = JSON.parse(read("presentation.json")),
  bytes = read("pilot-lawn-tone.json"),
  spec = JSON.parse(bytes);
test("lawn tone is source pinned and rejects unrelated or ambiguous geometry atomically", () => {
  assert.equal(
    createHash("sha256").update(bytes).digest("hex"),
    config.lawn_tone_sha256,
  );
  assert.equal(spec.base_asset_sha256, config.asset_sha256);
  const root = new T.Group(),
    geo = new T.BufferGeometry();
  geo.setAttribute(
    "position",
    new T.BufferAttribute(new Float32Array(30659 * 3), 3),
  );
  const mesh = new T.Mesh(geo, new T.MeshStandardMaterial({ color: 0x91b66f }));
  mesh.name = "landscape-lawn";
  mesh.userData.asset_kind = "landscape-surface";
  root.add(mesh);
  const extensionGeometry = new T.BufferGeometry();
  extensionGeometry.setAttribute(
    "position",
    new T.BufferAttribute(new Float32Array(47699 * 3), 3),
  );
  extensionGeometry.setAttribute(
    "color",
    new T.BufferAttribute(new Float32Array(47699 * 3), 3),
  );
  const extension = new T.Mesh(
    extensionGeometry,
    new T.MeshStandardMaterial({ vertexColors: true }),
  );
  extension.name = "campus-lawn-extension";
  extension.userData.asset_kind = "landscape-surface";
  root.add(extension);
  extension.material.vertexColors = false;
  assert.throws(() => markLawnTone(root, spec, config.asset_sha256));
  assert.equal(mesh.userData.lawn_tone, undefined);
  extension.material.vertexColors = true;
  assert.throws(() => markLawnTone(root, spec, "changed"));
  assert.equal(mesh.userData.lawn_tone, undefined);
  markLawnTone(root, spec, config.asset_sha256);
  assert.equal(mesh.userData.lawn_tone.strength, 0.07);
  assert.equal(extension.userData.lawn_tone.strength, 0.07);
  assert.equal(extension.geometry, extensionGeometry);
  assert.equal(mesh.geometry, geo);
  const clone = mesh.clone();
  root.add(clone);
  delete mesh.userData.lawn_tone;
  assert.throws(() => markLawnTone(root, spec, config.asset_sha256));
  assert.equal(mesh.userData.lawn_tone, undefined);
});
test("lawn tone composes with a prior shader callback and has an independent program key", () => {
  const mat = new T.MeshStandardMaterial(),
    called = [];
  mat.onBeforeCompile = () => called.push("previous");
  applyLawnTone(mat, { strength: 0.07 });
  const shader = {
    vertexShader: "#include <begin_vertex>",
    fragmentShader: "#include <color_fragment>",
  };
  mat.onBeforeCompile(shader, {});
  assert.deepEqual(called, ["previous"]);
  assert.match(shader.vertexShader, /lawnWorld/);
  assert.match(shader.fragmentShader, /lawnFade/);
  assert.match(mat.customProgramCacheKey(), /lawn-tone-0.07/);
  assert.throws(() => applyLawnTone(mat, spec));
});
