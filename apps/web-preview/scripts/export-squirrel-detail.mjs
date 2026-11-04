// SPDX-License-Identifier: Apache-2.0
// Export the source-pinned runtime squirrel and verify a binary roundtrip.
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
  throw Error("Supply one new GLB output; no overwrite");
const sha = (b) => createHash("sha256").update(b).digest("hex");
const source = "public/animals/campus-squirrel.glb",
  code = "src/squirrel-detail.js";
const bytes = fs.readFileSync(source),
  generator = fs.readFileSync(code);
const expected =
  "30d716fa7a576d68ebbe445d1bdfdb0f9282c9c3eced17d39505210c044b4e68";
if (sha(bytes) !== expected) throw Error("Unexpected squirrel source hash");
const browser = await chromium.launch({
  channel: "chrome",
  headless: true,
  args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
try {
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:5173/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const result = await page.evaluate(
    async ({ expected, codeHash }) => {
      const { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
      const { GLTFExporter } =
        await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js");
      const { addSquirrelEyes } = await import("/src/squirrel-detail.js");
      const loader = new GLTFLoader(),
        asset = await loader.loadAsync("/animals/campus-squirrel.glb");
      const info = addSquirrelEyes(asset.scene);
      asset.scene.userData = {
        source_sha256: expected,
        generator_sha256: codeHash,
        scope: "generic squirrel with illustrative eye accents",
      };
      const raw = await new GLTFExporter().parseAsync(asset.scene, {
        binary: true,
        copyright: "Innerscene CC0 source; Open Campus adaptation CC BY 4.0",
      });
      const round = await loader.parseAsync(raw, "");
      let copy;
      round.scene.traverse((o) => {
        if (o.isMesh) copy = o;
      });
      const stats = {};
      for (const key of ["position", "normal", "color"]) {
        const a = info.mesh.geometry.attributes[key],
          b = copy.geometry.attributes[key];
        if (!a || !b || a.count !== b.count)
          throw Error("Attribute count changed");
        let max = 0;
        for (let i = 0; i < a.array.length; i++)
          max = Math.max(max, Math.abs(a.array[i] - b.array[i]));
        if (max > 1e-6) throw Error("Attribute changed");
        stats[key] = { count: a.count, max };
      }
      if (
        !copy.material.vertexColors ||
        copy.material.color.getHexString() !==
          info.mesh.material.color.getHexString()
      )
        throw Error("Material mismatch");
      return {
        bytes: Array.from(new Uint8Array(raw)),
        stats,
        originalVertices: info.originalVertices,
        addedVertices: info.addedVertices,
      };
    },
    { expected, codeHash: sha(generator) },
  );
  if (
    sha(fs.readFileSync(source)) !== expected ||
    sha(fs.readFileSync(code)) !== sha(generator)
  )
    throw Error("Inputs changed during export");
  const out = Buffer.from(result.bytes);
  fs.writeFileSync(output, out, { flag: "wx" });
  console.log(
    JSON.stringify({
      output,
      sha256: sha(out),
      size: out.length,
      stats: result.stats,
      originalVertices: result.originalVertices,
      addedVertices: result.addedVertices,
    }),
  );
} finally {
  await browser.close();
}
