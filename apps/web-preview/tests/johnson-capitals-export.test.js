import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { createExteriorDetail } from "../src/exterior-detail.js";
const root = new URL("../../../", import.meta.url);
const sha = (x) => createHash("sha256").update(x).digest("hex");
for (const layer of ["capitals"])
  test(`Johnson standalone ${layer} matches local generator and receipt exactly`, async () => {
    const data = fs.readFileSync(
      new URL(
        `assets/exterior-refinement/johnson-north-${layer}-2026-11-10.glb`,
        root,
      ),
    );
    const receipt = JSON.parse(
      fs.readFileSync(
        new URL(
          `assets/exterior-refinement/johnson-north-${layer}-2026-11-10.glb.evidence.json`,
          root,
        ),
      ),
    );
    assert.equal(sha(data), receipt.output_sha256);
    const source = fs.readFileSync(
      new URL("../public/scene/" + receipt.source, import.meta.url),
    );
    assert.equal(sha(source), receipt.source_sha256);
    const spec = JSON.parse(source),
      local = createExteriorDetail(
        spec,
        receipt.base_sha256,
        new Set(["roof-906c030e"]),
      );
    const gltf = await new GLTFLoader().parseAsync(
      data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength),
      "",
    );
    const meshes = [];
    gltf.scene.traverse((o) => {
      if (o.isMesh) meshes.push(o);
    });
    assert.equal(meshes.length, 1);
    const a = local.children[0],
      b = meshes[0];
    assert.equal(b.userData.asset_id, "roof-906c030e");
    assert.equal(b.userData.source_overlay_sha256, receipt.source_sha256);
    assert.equal(b.userData.base_asset_sha256, receipt.base_sha256);
    assert.deepEqual(b.userData.generator_sha256, receipt.generator_sha256);
    assert.equal(b.userData.scope, "exterior-overlay-only");
    for (const key of ["position", "normal", "color"])
      assert.deepEqual(
        b.geometry.attributes[key].array,
        a.geometry.attributes[key].array,
      );
    for (const key of [
      "vertexColors",
      "roughness",
      "metalness",
      "side",
      "transparent",
      "opacity",
    ])
      assert.equal(b.material[key], a.material[key]);
    assert.ok(b.material.color.equals(a.material.color));
    assert.equal(b.geometry.index, null);
    a.geometry.dispose();
    a.material.dispose();
    b.geometry.dispose();
    b.material.dispose();
  });
test("Johnson exporter refuses remote URL, non-Johnson input and overwrite before browser work", () => {
  for (const args of [
    [
      "johnson-north-capitals.json",
      "unused.glb",
      "--base-url",
      "https://example.com:443/",
    ],
    ["other.json", "unused.glb"],
    [
      "johnson-north-capitals.json",
      "../../assets/exterior-refinement/johnson-north-capitals-2026-11-10.glb",
    ],
  ]) {
    const r = spawnSync(
      process.execPath,
      ["scripts/export-johnson-capitals.mjs", ...args],
      { cwd: new URL("../", import.meta.url), encoding: "utf8" },
    );
    assert.notEqual(r.status, 0);
    assert.match(r.stderr, /localhost|Usage|never overwritten/);
  }
});
