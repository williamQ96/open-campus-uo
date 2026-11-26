// SPDX-License-Identifier: Apache-2.0
import { writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "@playwright/test";

const output = resolve(
  process.argv[2] || "../../assets/characters/dan-carrere-l2.glb",
);
const browser = await chromium.launch({ channel: "chrome" });
try {
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:5173/viewer-profile.json");
  const glb = await page.evaluate(async () => {
    const { danCarrereAppearance, styleDanCarrere } =
      await import("/src/dan-carrere-style.js");
    const { loadStudentFactory } = await import("/src/student.js");
    const { GLTFExporter } =
      await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js");
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const { character } = await fetch("/viewer-profile.json").then((r) =>
      r.json(),
    );
    const url = "/" + character.asset_url;
    const factory = await loadStudentFactory(url, character);
    const { root } = factory(danCarrereAppearance);
    root.name = "Dan Carrere stylized campus character";
    styleDanCarrere(root);
    const source = await new GLTFLoader().loadAsync(url);
    const idle = source.animations.find((clip) => clip.name === "Idle");
    if (!idle) throw new Error("The source Idle clip is missing.");
    const bytes = await new GLTFExporter().parseAsync(root, {
      binary: true,
      animations: [idle],
      includeCustomExtensions: false,
      copyright:
        "Kenney source rig and Idle action CC0. Original Open Campus additions CC BY 4.0.",
    });
    const checked = await new GLTFLoader().parseAsync(bytes, "");
    if (
      checked.scene.getObjectsByProperty("isMesh", true).length !== 7 ||
      !checked.scene.getObjectByName("CarrereHeadAndHat") ||
      !checked.scene.getObjectByName("CarrereCollarAndPlacket") ||
      checked.animations[0]?.name !== "Idle"
    )
      throw new Error("The character export did not retain its visual parts.");
    return Array.from(new Uint8Array(bytes));
  });
  await writeFile(output, Buffer.from(glb));
  console.log(`${output} (${glb.length} bytes)`);
} finally {
  await browser.close();
}
