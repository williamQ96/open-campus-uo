// SPDX-License-Identifier: Apache-2.0
import { expect, test } from "@playwright/test";
import {
  DEFAULT_BACKGROUND_TREES,
  DEFAULT_SELECTABLE_BUILDINGS,
  OLD_CAMPUS_QUAD_CONTEXT_TREE_REMOVALS,
} from "./exterior-counts.js";

async function readOldQuad(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const viewer = window.__campus;
    const state = viewer.getState();
    const probe = (e, n) => {
      const h = viewer.terrainCheck(e, -n);
      return {
        quad: h["old-campus-quad-crosswalks"] ?? null,
        standing: h.standing,
        blocked: viewer.collisionCheck(e, -n),
      };
    };
    const hello = viewer.terrainCheck(-454.13, -85);
    return {
      count: state.buildings,
      trees: state.presentation.refinedContextTrees,
      stone: probe(-425.92, 218.12).blocked,
      inventoryTrunk: probe(-374.27, 126.325).blocked,
      walks: [
        [-400, 124.4],
        [-383.65, 142.37],
        [-420.4, 177.4],
        [-370.45, 158.67],
      ].map(([e, n]) => probe(e, n)),
      hello: hello.standing - hello.sampled > 0.07,
    };
  });
}

test("Old Campus Quad stitches the cross-paths into Hello Walk and loads the 1893 stone", async ({
  page,
}) => {
  const quad = await readOldQuad(page);
  expect(quad.count).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(quad.trees).toBe(DEFAULT_BACKGROUND_TREES);
  expect(quad.stone).toBe(true);
  expect(quad.inventoryTrunk).toBe(true);
  expect(quad.hello).toBe(true);
  for (const { quad: paving, standing, blocked } of quad.walks) {
    expect(paving).toBeGreaterThan(3.55);
    expect(standing).toBeCloseTo(paving, 2);
    expect(blocked).toBe(false);
  }
});

for (const [title, url, keepHello] of [
  ["new scene mesh", "old-campus-quad-landscape-review/site.glb", true],
  ["Hello Walk predecessor", "fenton-site-review/site.glb", false],
]) {
  test(
    "Old Campus Quad falls back when the " + title + " is missing",
    async ({ page }) => {
      await page.route("**/" + url, (route) =>
        route.fulfill({ body: "corrupted landscape dependency" }),
      );
      const quad = await readOldQuad(page);
      expect(quad.count).toBe(DEFAULT_SELECTABLE_BUILDINGS);
      expect(quad.trees).toBe(
        DEFAULT_BACKGROUND_TREES +
          OLD_CAMPUS_QUAD_CONTEXT_TREE_REMOVALS +
          // Fenton also retires two of its own background trees.
          (keepHello ? 0 : 2),
      );
      expect(quad.stone).toBe(false);
      expect(quad.inventoryTrunk).toBe(false);
      expect(quad.walks.every(({ quad: paving }) => paving === null)).toBe(
        true,
      );
      expect(quad.hello).toBe(keepHello);
    },
  );
}
