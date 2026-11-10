// SPDX-License-Identifier: Apache-2.0
// Export only the two source-pinned additive Knight Library layers.
// Start the local Vite server first. Output is an overlay, not a whole building.
import { chromium } from "@playwright/test";
import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { createExteriorDetail } from "../src/exterior-detail.js";

const [name, output, flag, requestedUrl] = process.argv.slice(2);
const baseUrl = new URL(
  requestedUrl ||
    process.env.KNIGHT_EXPORT_BASE_URL ||
    "http://127.0.0.1:5195/",
);
if (
  baseUrl.protocol !== "http:" ||
  !["127.0.0.1", "localhost", "[::1]"].includes(baseUrl.hostname) ||
  baseUrl.username ||
  baseUrl.password ||
  baseUrl.pathname !== "/" ||
  baseUrl.search ||
  baseUrl.hash ||
  !baseUrl.port
)
  throw Error("Use an explicit localhost HTTP port only");
if (
  !name ||
  !output ||
  ![4, 6].includes(process.argv.length) ||
  (flag && flag !== "--base-url") ||
  ![
    "knight-library-balcony-detail.json",
    "knight-library-window-reveals.json",
  ].includes(name)
) {
  throw new Error(
    "Usage: node scripts/export-knight-detail.mjs <knight-layer.json> <new-output.glb> [--base-url http://127.0.0.1:PORT/]",
  );
}
if (
  path.extname(output).toLowerCase() !== ".glb" ||
  fs.existsSync(output) ||
  fs.existsSync(output + ".evidence.json")
) {
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
  spec.building_id !== "roof-6684e091" ||
  !Array.isArray(spec.objects) ||
  spec.objects.some(
    (o) => o.kind !== "building" || !["box", "hip"].includes(o.shape),
  )
) {
  throw new Error(
    "Expected a pinned, non-replacing building overlay containing supported box/hip shapes.",
  );
}
const base = fs.readFileSync(path.join(scene, "campus-expanded.glb"));
if (sha(base) !== config.asset_sha256)
  throw new Error("Base GLB does not match the source pin.");
const exporterBytes = fs.readFileSync(new URL(import.meta.url));
const exporterHash = sha(exporterBytes);
const generatorFiles = ["src/exterior-detail.js", "src/fern-geometry.js"];
const generatorHashes = Object.fromEntries(
  generatorFiles.map((f) => [f, sha(fs.readFileSync(f))]),
);
const localDetail = createExteriorDetail(
  spec,
  config.asset_sha256,
  new Set(["roof-6684e091"]),
);
if (localDetail.children.length !== 1) throw Error("Expected one local mesh");
const expectedAttributes = Object.fromEntries(
  ["position", "normal", "color"].map((key) => [
    key,
    Array.from(localDetail.children[0].geometry.attributes[key].array),
  ]),
);
localDetail.children[0].geometry.dispose();
localDetail.children[0].material.dispose();
const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage();
  await page.goto(baseUrl.href);
  const servedSpec = await page.request.get(
    new URL("scene/" + name, baseUrl).href,
  );
  const servedBase = await page.request.get(
    new URL("scene/campus-expanded.glb", baseUrl).href,
  );
  if (
    !servedSpec.ok() ||
    sha(await servedSpec.body()) !== digest ||
    !servedBase.ok() ||
    sha(await servedBase.body()) !== config.asset_sha256
  )
    throw Error("Server sources do not match local source pins");
  const exported = await page.evaluate(
    async ({ spec, digest, generatorHashes, expectedAttributes }) => {
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
      for (const [key, expected] of Object.entries(expectedAttributes)) {
        const actual = mesh.geometry.attributes[key]?.array;
        if (
          !actual ||
          actual.length !== expected.length ||
          expected.some(
            (v, i) => !Number.isFinite(actual[i]) || v !== actual[i],
          )
        )
          throw Error("Server generator differs from local: " + key);
      }
      mesh.userData = {
        ...mesh.userData,
        source_overlay_sha256: digest,
        base_asset_sha256: spec.base_asset_sha256,
        scope: "exterior-overlay-only",
        generator_sha256: generatorHashes,
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
      for (const key of [
        "vertexColors",
        "roughness",
        "metalness",
        "side",
        "transparent",
        "opacity",
      ])
        if (copy.material[key] !== mesh.material[key])
          throw Error("Material mismatch: " + key);
      if (!copy.material.color.equals(mesh.material.color) || copy.material.map)
        throw Error("Material color/map mismatch");
      if (copy.geometry.index !== null || mesh.geometry.index !== null)
        throw Error("Unexpected indexed detail geometry");
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
    { spec, digest, generatorHashes, expectedAttributes },
  );
  if (
    sha(fs.readFileSync(new URL(import.meta.url))) !== exporterHash ||
    generatorFiles.some(
      (f) => sha(fs.readFileSync(f)) !== generatorHashes[f],
    ) ||
    sha(fs.readFileSync(source)) !== digest ||
    sha(fs.readFileSync(presentation)) !== sha(configBytes) ||
    sha(fs.readFileSync(path.join(scene, "campus-expanded.glb"))) !==
      config.asset_sha256
  )
    throw new Error("Inputs changed during export; no output written.");
  fs.writeFileSync(output, Buffer.from(exported.bytes), { flag: "wx" });
  const evidence = {
    generated_at: new Date().toISOString(),
    exporter_sha256: exporterHash,
    building_id: spec.building_id,
    generator_sha256: generatorHashes,
    scope:
      "additive layer only; no original building, collision or Blender scene",
    source: name,
    source_sha256: digest,
    base_sha256: config.asset_sha256,
    output,
    output_sha256: sha(Buffer.from(exported.bytes)),
    bytes: exported.bytes.length,
    verification: exported.stats,
    material_verified: true,
  };
  fs.writeFileSync(
    output + ".evidence.json",
    JSON.stringify(evidence, null, 2) + "\n",
    { flag: "wx" },
  );
  console.log(JSON.stringify(evidence));
} finally {
  await browser.close();
}
