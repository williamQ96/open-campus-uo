import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
test("context trunk replacement is source pinned and leaves canopy positions and indices intact", async ({
  page,
}) => {
  const spec = JSON.parse(
      readFileSync(
        new URL("../../public/scene/context-trunks.json", import.meta.url),
      ),
    ),
    config = JSON.parse(
      readFileSync(
        new URL("../../public/scene/presentation.json", import.meta.url),
      ),
    );
  expect(
    createHash("sha256")
      .update(
        readFileSync(
          new URL("../../public/scene/context-trunks.json", import.meta.url),
        ),
      )
      .digest("hex"),
  ).toBe(config.context_trunks_sha256);
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const result = await page.evaluate(async (spec) => {
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const { refineContextTrunks } = await import("/src/context-trunks.js");
    const gltf = await new GLTFLoader().loadAsync("/scene/campus-expanded.glb"),
      m = gltf.scene.getObjectByName("campus-trees"),
      old = m.geometry,
      p = old.attributes.position,
      idx = old.index;
    let rejected = false;
    try {
      refineContextTrunks(gltf.scene, spec, "mismatch");
    } catch {
      rejected = m.geometry === old;
    }
    const count = refineContextTrunks(gltf.scene, spec, spec.base_asset_sha256),
      g = m.geometry;
    let unchanged = true;
    for (let t = 0; t < 300; t++) {
      for (let j = 24; j < 152; j++)
        for (let a = 0; a < 3; a++)
          if (
            p.array[(t * 152 + j) * 3 + a] !==
            g.attributes.position.array[(t * 152 + j) * 3 + a]
          )
            unchanged = false;
      for (let j = 36; j < 228; j++)
        if (idx.getX(t * 228 + j) !== g.index.getX(t * 240 + j - 36))
          unchanged = false;
    }
    return {
      rejected,
      count,
      unchanged,
      positions: g.attributes.position.count,
      indices: g.index.count,
    };
  }, spec);
  expect(result).toEqual({
    rejected: true,
    count: 300,
    unchanged: true,
    positions: 55200,
    indices: 72000,
  });
});
