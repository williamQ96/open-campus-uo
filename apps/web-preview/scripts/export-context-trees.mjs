// SPDX-License-Identifier: Apache-2.0
// Export the source-pinned inferred campus tree batch with its runtime trunk refinement.
import { chromium } from "@playwright/test";
import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
const [output] = process.argv.slice(2);
if (
  process.argv.length !== 3 ||
  !output ||
  path.extname(output).toLowerCase() !== ".glb" ||
  fs.existsSync(output)
)
  throw Error("Usage: node scripts/export-context-trees.mjs <new-output.glb>");
const sha = (b) => createHash("sha256").update(b).digest("hex");
const basePath = "public/scene/campus-expanded.glb",
  configPath = "public/scene/presentation.json",
  specPath = "public/scene/context-trunks.json",
  sourcePath = "src/context-trunks.js";
const base = fs.readFileSync(basePath),
  configBytes = fs.readFileSync(configPath),
  specBytes = fs.readFileSync(specPath),
  source = fs.readFileSync(sourcePath),
  config = JSON.parse(configBytes),
  spec = JSON.parse(specBytes);
const hashes = {
  base: sha(base),
  config: sha(configBytes),
  spec: sha(specBytes),
  source: sha(source),
};
if (
  hashes.base !== config.asset_sha256 ||
  hashes.spec !== config.context_trunks_sha256 ||
  spec.base_asset_sha256 !== hashes.base
)
  throw Error("Source pins mismatch");
const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:5173/");
  const result = await page.evaluate(
    async ({ hashes, spec }) => {
      const T = await import("/node_modules/three/build/three.module.js"),
        { GLTFLoader } =
          await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js"),
        { GLTFExporter } =
          await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js"),
        { refineContextTrunks } = await import("/src/context-trunks.js");
      const root = await new GLTFLoader().loadAsync(
        "/scene/campus-expanded.glb",
      );
      root.scene.updateMatrixWorld(true);
      const count = refineContextTrunks(root.scene, spec, hashes.base),
        src = root.scene.getObjectByName("campus-trees");
      if (count !== 300 || !src.matrixWorld.equals(new T.Matrix4()))
        throw Error("Unexpected tree count or transform");
      const mesh = new T.Mesh(src.geometry, src.material);
      mesh.name = "context-trees-refined";
      mesh.userData = {
        source_glb_sha256: hashes.base,
        source_spec_sha256: hashes.spec,
        source_code_sha256: hashes.source,
        scope: "300-inferred-context-trees",
        coordinate_frame: "project glTF coordinates",
        tree_count: count,
      };
      const raw = await new GLTFExporter().parseAsync(mesh, {
        binary: true,
        copyright:
          "Copyright 2026 Zhongyi William Qiu and Open Campus contributors; original model output CC BY 4.0.",
      });
      const loaded = await new GLTFLoader().parseAsync(raw, ""),
        items = [];
      loaded.scene.updateMatrixWorld(true);
      loaded.scene.traverse((o) => {
        if (o.isMesh) items.push(o);
      });
      if (
        items.length !== 1 ||
        !items[0].matrixWorld.equals(new T.Matrix4()) ||
        items[0].userData.source_glb_sha256 !== hashes.base ||
        !items[0].material.vertexColors
      )
        throw Error("Export provenance or material mismatch");
      const dst = items[0],
        stats = {};
      for (const key of ["position", "normal", "color"]) {
        const a = mesh.geometry.attributes[key],
          b = dst.geometry.attributes[key];
        if (a.count !== b.count || a.itemSize !== b.itemSize)
          throw Error("Attribute count mismatch");
        let max = 0;
        for (let i = 0; i < a.array.length; i++)
          max = Math.max(max, Math.abs(a.array[i] - b.array[i]));
        if (max > 1e-6) throw Error("Attribute mismatch");
        stats[key] = { count: a.count, max_abs_error: max };
      }
      const a = mesh.geometry.index,
        b = dst.geometry.index;
      if (a.count !== b.count || a.array.some((v, i) => v !== b.array[i]))
        throw Error("Index mismatch");
      return {
        bytes: Array.from(new Uint8Array(raw)),
        stats,
        indices: a.count,
        trees: count,
      };
    },
    { hashes, spec },
  );
  for (const [file, key] of [
    [basePath, "base"],
    [configPath, "config"],
    [specPath, "spec"],
    [sourcePath, "source"],
  ])
    if (sha(fs.readFileSync(file)) !== hashes[key])
      throw Error("Source changed during export");
  const bytes = Buffer.from(result.bytes);
  fs.writeFileSync(output, bytes, { flag: "wx" });
  console.log(
    JSON.stringify({
      output,
      output_sha256: sha(bytes),
      bytes: bytes.length,
      hashes,
      verification: result.stats,
      indices: result.indices,
      trees: result.trees,
    }),
  );
} finally {
  await browser.close();
}
