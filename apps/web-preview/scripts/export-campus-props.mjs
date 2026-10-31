// SPDX-License-Identifier: Apache-2.0
import { chromium } from "@playwright/test";
import fs from "node:fs";
const b = await chromium.launch({ channel: "chrome", headless: true });
const p = await b.newPage();
await p.goto("http://127.0.0.1:5173/");
const bytes = await p.evaluate(async () => {
  const THREE = await import("/node_modules/three/build/three.module.js");
  const { createCampusProp } = await import("/src/props.js");
  const { GLTFExporter } =
    await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js");
  const group = new THREE.Group();
  for (const [i, kind] of [
    "car",
    "van",
    "pickup",
    "bicycle",
    "scooter",
  ].entries()) {
    const mesh = createCampusProp(kind);
    mesh.position.x = i * 5;
    group.add(mesh);
  }
  const data = await new GLTFExporter().parseAsync(group, {
    binary: true,
    copyright:
      "Copyright 2026 Zhongyi William Qiu and Open Campus contributors. Original model output: CC BY 4.0.",
  });
  return Array.from(new Uint8Array(data));
});
fs.mkdirSync("public/props", { recursive: true });
fs.writeFileSync("public/props/campus-props.glb", Buffer.from(bytes));
console.log("exported", bytes.length);
await b.close();
