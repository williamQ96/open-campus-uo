// SPDX-License-Identifier: Apache-2.0
// Export the original generic three-hoop rack; no site placement is included.
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
  throw Error("Usage: node scripts/export-bike-rack.mjs <new-output.glb>");
const source = "src/bike-rack-geometry.js",
  sha = (b) => createHash("sha256").update(b).digest("hex"),
  digest = sha(fs.readFileSync(source));
const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:5173/");
  const result = await page.evaluate(async (digest) => {
    const T = await import("/node_modules/three/build/three.module.js"),
      { createBikeRackGeometry } = await import("/src/bike-rack-geometry.js"),
      { GLTFExporter } =
        await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js"),
      { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const mesh = new T.Mesh(
      createBikeRackGeometry({ hoops: 3 }),
      new T.MeshStandardMaterial({ color: 0x3f514b, roughness: 0.87 }),
    );
    mesh.name = "generic-bike-rack";
    mesh.userData = {
      source_sha256: digest,
      scope: "generic-bike-rack-unplaced",
      hoops: 3,
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
      meshes[0].userData.source_sha256 !== digest
    )
      throw Error("Identity or provenance mismatch");
    const copy = meshes[0],
      stats = {};
    for (const key of ["position", "normal"]) {
      const a = mesh.geometry.attributes[key],
        b = copy.geometry.attributes[key];
      if (a.count !== b.count) throw Error("attribute count mismatch");
      let max = 0;
      for (let i = 0; i < a.array.length; i++)
        max = Math.max(max, Math.abs(a.array[i] - b.array[i]));
      if (max > 1e-6) throw Error("attribute mismatch");
      stats[key] = { count: a.count, max_abs_error: max };
    }
    if (
      mesh.geometry.index.count !== copy.geometry.index.count ||
      mesh.geometry.index.array.some(
        (v, i) => v !== copy.geometry.index.array[i],
      )
    )
      throw Error("triangle indices mismatch");
    if (copy.material.color.getHexString() !== "3f514b")
      throw Error("color mismatch");
    return {
      bytes: Array.from(new Uint8Array(raw)),
      stats,
      triangles: mesh.geometry.index.count / 3,
    };
  }, digest);
  if (sha(fs.readFileSync(source)) !== digest)
    throw Error("Source changed during export");
  const bytes = Buffer.from(result.bytes);
  fs.writeFileSync(output, bytes, { flag: "wx" });
  console.log(
    JSON.stringify({
      source_sha256: digest,
      output,
      output_sha256: sha(bytes),
      bytes: bytes.length,
      verification: result.stats,
      triangles: result.triangles,
    }),
  );
} finally {
  await browser.close();
}
