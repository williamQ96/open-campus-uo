// SPDX-License-Identifier: Apache-2.0
// Export a pinned, box-only exterior overlay with runtime rotations baked in.
// Start the local Vite server first. Output is an overlay, not a whole building.
import { chromium } from "@playwright/test";
import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const [name, output] = process.argv.slice(2);
if (
  !name ||
  !output ||
  process.argv.length !== 4 ||
  !/^[A-Za-z0-9_.-]+\.json$/.test(name)
) {
  throw new Error(
    "Usage: node scripts/export-exterior-detail.mjs <scene-json-name> <new-output.glb>",
  );
}
if (path.extname(output).toLowerCase() !== ".glb" || fs.existsSync(output)) {
  throw new Error(
    "Output must be a new .glb file; existing files are never overwritten.",
  );
}
const scene = path.resolve("public/scene");
const source = path.join(scene, name),
  presentation = path.join(scene, "presentation.json");
const sourceBytes = fs.readFileSync(source),
  configBytes = fs.readFileSync(presentation);
const spec = JSON.parse(sourceBytes),
  config = JSON.parse(configBytes);
const sha = (v) => createHash("sha256").update(v).digest("hex");
const digest = sha(sourceBytes),
  pin = config.exterior_details?.find((x) => x.url === name);
if (
  !pin ||
  pin.sha256 !== digest ||
  spec.base_asset_sha256 !== config.asset_sha256 ||
  spec.replace_building !== false ||
  !spec.building_id ||
  !Array.isArray(spec.objects) ||
  spec.objects.some((o) => o.kind !== "building" || o.shape !== "box")
) {
  throw new Error(
    "Expected a pinned, non-replacing building overlay containing boxes only.",
  );
}
const base = fs.readFileSync(path.join(scene, "campus-expanded.glb"));
if (sha(base) !== config.asset_sha256)
  throw new Error("Base GLB does not match the source pin.");
const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:5173/");
  const exported = await page.evaluate(
    async ({ spec, digest }) => {
      const { createExteriorDetail } = await import("/src/exterior-detail.js");
      const { GLTFExporter } =
        await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js");
      const { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
      const detail = createExteriorDetail(
        spec,
        spec.base_asset_sha256,
        new Set([spec.building_id]),
      );
      if (detail.children.length !== 1 || !detail.children[0].isMesh)
        throw new Error("Expected one building mesh.");
      const mesh = detail.children[0];
      mesh.userData = {
        ...mesh.userData,
        source_overlay_sha256: digest,
        base_asset_sha256: spec.base_asset_sha256,
        scope: "exterior-overlay-only",
      };
      const raw = await new GLTFExporter().parseAsync(detail, {
        binary: true,
        copyright:
          "Copyright 2026 Zhongyi William Qiu and Open Campus contributors; original model output CC BY 4.0.",
      });
      const roundtrip = await new GLTFLoader().parseAsync(raw, "");
      roundtrip.scene.updateMatrixWorld(true);
      const meshes = [];
      roundtrip.scene.traverse((o) => {
        if (o.isMesh) meshes.push(o);
      });
      if (meshes.length !== 1)
        throw new Error("Export must reimport as exactly one mesh.");
      const copy = meshes[0];
      if (
        !copy.matrixWorld.equals(
          new (
            await import("/node_modules/three/build/three.module.js")
          ).Matrix4(),
        )
      )
        throw new Error("Unexpected export transform.");
      if (
        copy.userData.source_overlay_sha256 !== digest ||
        copy.userData.asset_id !== spec.building_id
      )
        throw new Error("Export provenance lost.");
      const stats = {};
      for (const name of ["position", "normal", "color"]) {
        const a = mesh.geometry.attributes[name],
          b = copy.geometry.attributes[name];
        if (!a || !b || a.count !== b.count || a.itemSize !== b.itemSize)
          throw new Error(`${name} layout mismatch`);
        let max = 0;
        for (let i = 0; i < a.array.length; i++)
          max = Math.max(max, Math.abs(a.array[i] - b.array[i]));
        if (max > 1e-6) throw new Error(`${name} mismatch: ${max}`);
        stats[name] = { count: a.count, max_abs_error: max };
      }
      return { bytes: Array.from(new Uint8Array(raw)), stats };
    },
    { spec, digest },
  );
  if (
    sha(fs.readFileSync(source)) !== digest ||
    sha(fs.readFileSync(presentation)) !== sha(configBytes) ||
    sha(fs.readFileSync(path.join(scene, "campus-expanded.glb"))) !==
      config.asset_sha256
  )
    throw new Error("Inputs changed during export; no output written.");
  fs.writeFileSync(output, Buffer.from(exported.bytes), { flag: "wx" });
  console.log(
    JSON.stringify({
      source: name,
      source_sha256: digest,
      base_sha256: config.asset_sha256,
      output,
      output_sha256: sha(Buffer.from(exported.bytes)),
      bytes: exported.bytes.length,
      verification: exported.stats,
    }),
  );
} finally {
  await browser.close();
}
