// SPDX-License-Identifier: Apache-2.0
// Export a reusable local-coordinate placeholder portal, without placement data.
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
  throw Error("Usage: node scripts/export-entrance.mjs <new-output.glb>");
const source = "src/entrances.js",
  sha = (b) => createHash("sha256").update(b).digest("hex"),
  digest = sha(fs.readFileSync(source));
const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:5173/");
  const result = await page.evaluate(async (digest) => {
    const T = await import("/node_modules/three/build/three.module.js"),
      { createEntranceFrameGeometry, createEntranceDoorGeometry } =
        await import("/src/entrances.js"),
      { GLTFExporter } =
        await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js"),
      { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const root = new T.Group(),
      frame = new T.Mesh(
        createEntranceFrameGeometry(),
        new T.MeshStandardMaterial({ color: 0xead5a0, roughness: 0.85 }),
      ),
      door = new T.Mesh(
        createEntranceDoorGeometry(),
        new T.MeshStandardMaterial({ color: 0x285d51, roughness: 0.72 }),
      );
    frame.name = "portal-trim";
    door.name = "portal-door";
    root.userData = {
      source_sha256: digest,
      scope: "illustrative-portal-no-placement",
    };
    root.add(frame, door);
    const raw = await new GLTFExporter().parseAsync(root, {
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
    if (meshes.length !== 2)
      throw Error("Expected two materials and two meshes");
    const stats = {};
    for (const src of [frame, door]) {
      const dst = meshes.find((x) => x.name === src.name);
      if (!dst || !dst.matrixWorld.equals(new T.Matrix4()))
        throw Error("Invalid mesh or transform");
      if (
        src.material.color
          .toArray()
          .some((x, i) => Math.abs(x - dst.material.color.toArray()[i]) > 1e-6)
      )
        throw Error("Color mismatch");
      for (const k of ["position", "normal"]) {
        const a = src.geometry.attributes[k],
          b = dst.geometry.attributes[k];
        if (a.count !== b.count || a.itemSize !== b.itemSize)
          throw Error("Attribute mismatch");
        let e = 0;
        for (let i = 0; i < a.array.length; i++)
          e = Math.max(e, Math.abs(a.array[i] - b.array[i]));
        if (e > 1e-6) throw Error("Attribute values mismatch");
        stats[src.name + "-" + k] = { count: a.count, max_abs_error: e };
      }
    }
    const node = g.scene.children.find(
      (x) => x.userData.source_sha256 === digest,
    );
    if (!node) throw Error("Missing source provenance");
    return { bytes: Array.from(new Uint8Array(raw)), stats };
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
    }),
  );
} finally {
  await browser.close();
}
