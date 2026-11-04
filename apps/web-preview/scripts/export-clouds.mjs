// SPDX-License-Identifier: Apache-2.0
// Export the current procedural cloud mesh, excluding the camera-following sky dome.
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
  throw Error("Usage: node scripts/export-clouds.mjs <new-output.glb>");
const sha = (b) => createHash("sha256").update(b).digest("hex"),
  files = ["src/sky.js", "src/npc-templates.js"],
  hashes = Object.fromEntries(files.map((p) => [p, sha(fs.readFileSync(p))]));
const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:5173/");
  const result = await page.evaluate(async (hashes) => {
    const T = await import("/node_modules/three/build/three.module.js"),
      { createSky } = await import("/src/sky.js"),
      { GLTFExporter } =
        await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js"),
      { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const scene = new T.Scene();
    createSky(scene);
    const original = scene.getObjectByName("Rounded voxel cloud layer");
    if (!original?.isMesh) throw Error("Cloud source missing");
    const mesh = original.clone();
    mesh.name = "procedural-cloud-layer";
    mesh.userData = {
      source_sha256: hashes["src/sky.js"],
      random_source_sha256: hashes["src/npc-templates.js"],
      scope: "cloud-mesh-only-no-dome-or-drift",
    };
    const raw = await new GLTFExporter().parseAsync(mesh, {
        binary: true,
        copyright:
          "Copyright 2026 Zhongyi William Qiu and Open Campus contributors; original model output CC BY 4.0.",
      }),
      g = await new GLTFLoader().parseAsync(raw, "");
    g.scene.updateMatrixWorld(true);
    const meshes = [];
    g.scene.traverse((o) => {
      if (o.isMesh) meshes.push(o);
    });
    if (
      meshes.length !== 1 ||
      !meshes[0].matrixWorld.equals(new T.Matrix4()) ||
      meshes[0].userData.source_sha256 !== hashes["src/sky.js"] ||
      meshes[0].userData.random_source_sha256 !== hashes["src/npc-templates.js"]
    )
      throw Error("Export identity/provenance mismatch");
    const stats = {};
    for (const k of ["position", "normal", "color"]) {
      const a = mesh.geometry.attributes[k],
        b = meshes[0].geometry.attributes[k];
      if (!a || !b || a.count !== b.count || a.itemSize !== b.itemSize)
        throw Error("Attribute layout mismatch");
      let e = 0;
      for (let i = 0; i < a.array.length; i++)
        e = Math.max(e, Math.abs(a.array[i] - b.array[i]));
      if (e > 1e-6) throw Error("Attribute values mismatch");
      stats[k] = { count: a.count, max_abs_error: e };
    }
    if (
      !meshes[0].material.transparent ||
      Math.abs(meshes[0].material.opacity - mesh.material.opacity) > 1e-6
    )
      throw Error("Opacity mismatch");
    return {
      bytes: Array.from(new Uint8Array(raw)),
      stats,
      opacity: meshes[0].material.opacity,
    };
  }, hashes);
  for (const f of files)
    if (sha(fs.readFileSync(f)) !== hashes[f])
      throw Error("Source changed during export");
  const bytes = Buffer.from(result.bytes);
  fs.writeFileSync(output, bytes, { flag: "wx" });
  console.log(
    JSON.stringify({
      sources: hashes,
      output,
      output_sha256: sha(bytes),
      bytes: bytes.length,
      verification: result.stats,
      opacity: result.opacity,
    }),
  );
} finally {
  await browser.close();
}
