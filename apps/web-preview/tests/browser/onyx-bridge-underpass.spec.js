// SPDX-License-Identifier: Apache-2.0
import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readPassage(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    function sample(east, north) {
      const h = campus.terrainCheck(east, -north);
      return {
        paving: h["onyx-bridge-underpass"] ?? null,
        green: h["onyx-green-walks"] ?? null,
        apron: h["northeast-wayfinding-paving"] ?? null,
        standing: h.standing,
        blocked: campus.collisionCheck(east, -north),
      };
    }
    return {
      count: campus.getState().buildings,
      south: sample(-202.99, 112.24),
      opening: sample(-202.98, 124),
      east: sample(-197.26, 145.05),
      west: sample(-210.78, 141.62),
      map: sample(-191.6, 156.24),
      planting: [
        sample(-204.46, 144.5),
        sample(-210.015, 135.196),
        sample(-197.905, 135.738),
      ],
    };
  });
}

test("Onyx Bridge connects the ground passage and both garden walks", async ({
  page,
}) => {
  const passage = await readPassage(page);
  expect(passage.count).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  for (const [point, height] of [
    [passage.opening, 1.174],
    [passage.east, 0.959],
    [passage.west, 1.082],
  ]) {
    expect(point.blocked).toBe(false);
    expect(point.paving).toBeCloseTo(height, 2);
    expect(point.standing).toBeCloseTo(point.paving, 3);
  }
  expect(passage.south.standing).toBeCloseTo(passage.south.green, 3);
  expect(passage.map.standing).toBeCloseTo(passage.map.apron, 3);
  expect(passage.map.blocked).toBe(false);
  expect(passage.planting.map(({ blocked }) => blocked)).toEqual([
    true,
    true,
    true,
  ]);
});

for (const [title, asset, apronAvailable] of [
  ["passage mesh", "onyx-bridge-underpass-review/site.glb", true],
  [
    "north map-station predecessor",
    "northeast-campus-wayfinding-review/site.glb",
    false,
  ],
]) {
  test(`Onyx Bridge falls back without the ${title}`, async ({ page }) => {
    await page.route(`**/${asset}`, (route) =>
      route.fulfill({ body: "damaged Onyx Bridge dependency" }),
    );
    const prior = await readPassage(page);
    expect(prior.count).toBe(DEFAULT_SELECTABLE_BUILDINGS);
    expect(prior.opening.paving).toBeNull();
    expect(prior.east.paving).toBeNull();
    expect(prior.west.paving).toBeNull();
    expect(prior.south.green).toBeCloseTo(1.215, 2);
    expect(prior.map.apron !== null).toBe(apronAvailable);
  });
}
