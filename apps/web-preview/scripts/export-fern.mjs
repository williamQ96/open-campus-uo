// SPDX-License-Identifier: Apache-2.0
// Export one normalized reusable fern; never overwrite an existing asset.
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
  throw new Error("Usage: node scripts/export-fern.mjs <new-output.glb>");
const source = "src/fern-geometry.js",
  sha = (b) => createHash("sha256").update(b).digest("hex"),
  digest = sha(fs.readFileSync(source));
const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:5173/");
  const result = await page.evaluate(async (digest) => {
    const THREE = await import("/node_modules/three/build/three.module.js");
    const { createFernGeometry } = await import("/src/fern-geometry.js");
    const { GLTFExporter } =
      await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js");
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const mesh = new THREE.Mesh(
      createFernGeometry(),
      new THREE.MeshStandardMaterial({ color: "#829e59", roughness: 0.87 }),
    );
    mesh.name = "normalized-fern";
    mesh.userData = {
      source_sha256: digest,
      scope: "normalized-reusable-fern",
    };
    const data = await new GLTFExporter().parseAsync(mesh, {
      binary: true,
      copyright:
        "Copyright 2026 Zhongyi William Qiu and Open Campus contributors; original model output CC BY 4.0.",
    });
    const roundtrip = await new GLTFLoader().parseAsync(data, ""),
      meshes = [];
    roundtrip.scene.updateMatrixWorld(true);
    roundtrip.scene.traverse((o) => {
      if (o.isMesh) meshes.push(o);
    });
    if (
      meshes.length !== 1 ||
      !meshes[0].matrixWorld.equals(new THREE.Matrix4()) ||
      meshes[0].userData.source_sha256 !== digest
    )
      throw Error("Export identity or provenance mismatch");
    const stats = {};
    for (const key of ["position", "normal"]) {
      const a = mesh.geometry.attributes[key],
        b = meshes[0].geometry.attributes[key];
      if (!a || !b || a.count !== b.count || a.itemSize !== b.itemSize)
        throw Error(`${key} layout mismatch`);
      let max = 0;
      for (let i = 0; i < a.array.length; i++)
        max = Math.max(max, Math.abs(a.array[i] - b.array[i]));
      if (max > 1e-6) throw Error(`${key} mismatch ${max}`);
      stats[key] = { count: a.count, max_abs_error: max };
    }
    if (
      mesh.material.color
        .toArray()
        .some(
          (v, i) => Math.abs(v - meshes[0].material.color.toArray()[i]) > 1e-6,
        )
    )
      throw Error("Material mismatch");
    return {
      bytes: Array.from(new Uint8Array(data)),
      stats,
      color: meshes[0].material.color.toArray(),
    };
  }, digest);
  if (sha(fs.readFileSync(source)) !== digest)
    throw Error("Source changed during export");
  const bytes = Buffer.from(result.bytes);
  fs.writeFileSync(output, bytes, { flag: "wx" });
  console.log(
    JSON.stringify({
      source,
      source_sha256: digest,
      output,
      output_sha256: sha(bytes),
      bytes: bytes.length,
      verification: result.stats,
      color: result.color,
    }),
  );
} finally {
  await browser.close();
}
