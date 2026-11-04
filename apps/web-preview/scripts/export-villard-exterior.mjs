// SPDX-License-Identifier: Apache-2.0
// Export the source-pinned Villard Hall replacement (including its eight illustrative shrubs).
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
  throw Error("Supply one new GLB output; no overwrite.");
const sha = (b) => createHash("sha256").update(b).digest("hex");
const dir = "public/scene/",
  name = "villard-east-detail.json",
  specBytes = fs.readFileSync(dir + name),
  configBytes = fs.readFileSync(dir + "presentation.json"),
  spec = JSON.parse(specBytes),
  cfg = JSON.parse(configBytes);
const pin = cfg.exterior_details.find((x) => x.url === name);
if (
  !pin ||
  pin.sha256 !== sha(specBytes) ||
  spec.base_asset_sha256 !== cfg.asset_sha256 ||
  !spec.replace_building ||
  spec.building_id !== "roof-399c648e" ||
  sha(fs.readFileSync(dir + "campus-expanded.glb")) !== cfg.asset_sha256
)
  throw Error("Villard sources changed.");
const code = fs.readFileSync("src/exterior-detail.js");
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
    async ({ spec, digest, codeHash }) => {
      const { createExteriorDetail } = await import("/src/exterior-detail.js");
      const { GLTFExporter } =
        await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js");
      const { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
      const group = createExteriorDetail(
        spec,
        spec.base_asset_sha256,
        new Set([spec.building_id]),
      );
      group.name = "villard-hall-exterior";
      group.userData = {
        source_sha256: digest,
        generator_sha256: codeHash,
        base_asset_sha256: spec.base_asset_sha256,
        scope: "villard-replacement-including-eight-illustrative-shrubs",
      };
      if (group.children.length !== 2 || group.children.some((x) => !x.isMesh))
        throw Error("Unexpected detail output");
      const originals = group.children;
      originals.forEach((x, i) => (x.name = `villard-part-${i}`));
      const raw = await new GLTFExporter().parseAsync(group, {
        binary: true,
        copyright: "Original Open Campus model output CC BY 4.0",
      });
      const copy = await new GLTFLoader().parseAsync(raw, "");
      let stats = {};
      for (const mesh of originals) {
        const dest = copy.scene.getObjectByName(mesh.name);
        if (!dest?.isMesh) throw Error("Missing mesh");
        for (const key of ["position", "normal", "color"]) {
          const a = mesh.geometry.attributes[key],
            b = dest.geometry.attributes[key];
          if (!a || !b || a.count !== b.count)
            throw Error("Attribute count changed");
          let max = 0;
          for (let i = 0; i < a.array.length; i++)
            max = Math.max(max, Math.abs(a.array[i] - b.array[i]));
          if (max > 1e-6) throw Error("Attribute changed");
          stats[`${mesh.name}-${key}`] = { count: a.count, max };
        }
        if (
          dest.material.color.getHexString() !==
          mesh.material.color.getHexString()
        )
          throw Error("Material changed");
      }
      return { bytes: Array.from(new Uint8Array(raw)), stats };
    },
    { spec, digest: sha(specBytes), codeHash: sha(code) },
  );
  if (
    sha(fs.readFileSync(dir + name)) !== sha(specBytes) ||
    sha(fs.readFileSync(dir + "presentation.json")) !== sha(configBytes) ||
    sha(fs.readFileSync("src/exterior-detail.js")) !== sha(code)
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
    }),
  );
} finally {
  await browser.close();
}
