// SPDX-License-Identifier: Apache-2.0
import { expect, test } from "@playwright/test";
import {
  DEFAULT_BACKGROUND_TREES,
  DEFAULT_SELECTABLE_BUILDINGS,
  SCIENCE_GREEN_WEST_CONTEXT_TREE_REMOVALS,
} from "./exterior-counts.js";

async function readWestGreen(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const viewer = window.__campus;
    const { buildings, presentation } = viewer.getState();
    const sample = (e, n) => {
      const h = viewer.terrainCheck(e, -n);
      return {
        west: h["science-green-west-paving"] ?? null,
        east: h["science-green-paving"] ?? null,
        standing: h.standing,
        collision: viewer.collisionCheck(e, -n),
      };
    };
    return {
      buildings,
      backgroundTrees: presentation.refinedContextTrees,
      arc: [
        [-75.24, 29.23],
        [-80.56, 50.65],
        [-72.36, 67.36],
        [-67.07, 66.79],
        [-79.4, 27.1],
      ].map(([e, n]) => sample(e, n)),
      lawn: sample(-66, 46),
      enclosure: sample(-78.4, 21),
      lawnFeature: sample(-61.9, 36.36),
      tree: sample(-82.268, 43.575),
      sundial: sample(-59.97, 75.65),
    };
  });
}

test("Science Green has a continuous west walk and a clear oval lawn", async ({
  page,
}) => {
  const scene = await readWestGreen(page);
  expect(scene.buildings).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(scene.backgroundTrees).toBe(DEFAULT_BACKGROUND_TREES);
  for (const { west, standing, collision } of scene.arc) {
    expect(west).toBeGreaterThan(1.1);
    expect(standing).toBeCloseTo(west, 3);
    expect(collision).toBe(false);
  }
  expect(scene.lawn.west).toBeCloseTo(1.5, 2);
  expect(scene.lawn.standing).toBeCloseTo(scene.lawn.west, 3);
  expect(scene.lawn.collision).toBe(false);
  expect(scene.enclosure.collision).toBe(true);
  expect(scene.lawnFeature.collision).toBe(true);
  expect(scene.tree.collision).toBe(true);
  expect(scene.sundial.collision).toBe(true);
});

test("a damaged west package restores the existing lawn and east approach", async ({
  page,
}) => {
  await page.route("**/science-green-west-review/site.glb", (route) =>
    route.fulfill({ body: "invalid west Science Green mesh" }),
  );
  const prior = await readWestGreen(page);
  expect(prior.buildings).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(prior.backgroundTrees).toBe(
    DEFAULT_BACKGROUND_TREES + SCIENCE_GREEN_WEST_CONTEXT_TREE_REMOVALS,
  );
  expect(prior.arc.every(({ west }) => west === null)).toBe(true);
  expect(prior.lawn.west).toBeNull();
  expect(prior.enclosure.collision).toBe(false);
  expect(prior.lawnFeature.collision).toBe(false);
  expect(prior.tree.collision).toBe(false);
  expect(prior.sundial.collision).toBe(true);
});
