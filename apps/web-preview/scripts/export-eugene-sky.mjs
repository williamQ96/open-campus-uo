// SPDX-License-Identifier: Apache-2.0
import { chromium } from "@playwright/test";
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { extname } from "node:path";

const [output, ...extra] = process.argv.slice(2);
if (!output || extra.length || extname(output).toLowerCase() !== ".glb")
  throw Error("Usage: node scripts/export-eugene-sky.mjs <new-output.glb>");
const files = ["src/eugene-sky.js", "src/npc-templates.js"];
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
const inputHashes = () =>
  Object.fromEntries(files.map((file) => [file, hash(readFileSync(file))]));
const inputs = inputHashes();
const browser = await chromium.launch({ channel: "chrome" });
try {
  const page = await browser.newPage();
  const exportPage = "http://127.0.0.1:5173/__sky-export";
  await page.route(exportPage, (route) =>
    route.fulfill({ contentType: "text/html", body: "<!doctype html>" }),
  );
  await page.goto(exportPage);
  const result = await page.evaluate(async (inputs) => {
    const { Scene, Matrix4 } =
      await import("/node_modules/three/build/three.module.js");
    const { GLTFExporter } =
      await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js");
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const { createEugeneSky } = await import("/src/eugene-sky.js");
    const scene = new Scene();
    const sky = createEugeneSky(scene);
    const root = scene.children[0];
    root.userData = {
      sources: inputs,
      layers: sky.state().layers,
      scope: "camera-centered-sky-at-rest",
    };
    const buffer = await new GLTFExporter().parseAsync(root, {
      binary: true,
      copyright:
        "Copyright 2026 Zhongyi William Qiu and Open Campus contributors. Original model output CC BY 4.0.",
    });
    const gltf = await new GLTFLoader().parseAsync(buffer, "");
    gltf.scene.updateMatrixWorld(true);
    const exported = gltf.scene.children[0];
    if (
      JSON.stringify(exported.userData.sources) !== JSON.stringify(inputs) ||
      JSON.stringify(exported.userData.layers) !==
        JSON.stringify(sky.state().layers) ||
      exported.children.length !== root.children.length
    )
      throw Error("Sky export metadata or mesh count mismatch.");

    const statistics = {};
    for (const mesh of root.children) {
      const result = exported.getObjectByName(mesh.name);
      if (
        !result?.material.isMeshBasicMaterial ||
        !result.material.vertexColors ||
        result.material.side !== mesh.material.side ||
        !result.matrixWorld.equals(new Matrix4())
      )
        throw Error("Sky export material or transform mismatch.");
      const index = mesh.geometry.index.array;
      const roundTripIndex = result.geometry.index.array;
      if (
        index.length !== roundTripIndex.length ||
        !index.every((value, i) => value === roundTripIndex[i])
      )
        throw Error("Sky export indices differ.");
      for (const attribute of ["position", "normal", "color"]) {
        const a = mesh.geometry.attributes[attribute].array;
        const b = result.geometry.attributes[attribute].array;
        if (
          a.length !== b.length ||
          !a.every((value, i) => Math.abs(value - b[i]) < 1e-6)
        )
          throw Error(
            mesh.name + " " + attribute + " differs after sky export.",
          );
      }
      statistics[mesh.name] = {
        vertices: mesh.geometry.attributes.position.count,
        triangles: index.length / 3,
      };
    }
    return { bytes: Array.from(new Uint8Array(buffer)), statistics };
  }, inputs);
  if (JSON.stringify(inputHashes()) !== JSON.stringify(inputs))
    throw Error("Sky inputs changed during export.");
  const bytes = Buffer.from(result.bytes);
  writeFileSync(output, bytes, { flag: "wx" });
  console.log(
    JSON.stringify(
      {
        inputs,
        output,
        sha256: hash(bytes),
        bytes: bytes.length,
        meshes: result.statistics,
      },
      null,
      2,
    ),
  );
} finally {
  await browser.close();
}
