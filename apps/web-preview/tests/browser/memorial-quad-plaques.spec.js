import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readPlaques(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const state = campus.getState();
    const locations = [
      [-558.138, 9.42, 0.106],
      [-531.857, 9.42, 0.106],
      [-531.027, 69.546, 0.07],
    ];
    return {
      count: state.buildings,
      quad: state.presentation.refinedPavingCorridors?.quad ?? false,
      plaques: locations.map(([east, south, supportLift]) => {
        const hit = campus.terrainCheck(east, south);
        return {
          rise:
            hit["memorial-quad-plaques"] === undefined
              ? null
              : hit["memorial-quad-plaques"] - hit.sampled - supportLift,
          clear: !campus.collisionCheck(east, south),
        };
      }),
    };
  });
}

test("the Quad plaques fit the pavement and fall back with their site bundle", async ({
  page,
}) => {
  const installed = await readPlaques(page);
  expect(installed.count).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(installed.quad).toBe(true);
  for (const plaque of installed.plaques) {
    expect(plaque.clear).toBe(true);
    expect(plaque.rise).toBeGreaterThanOrEqual(0);
    expect(plaque.rise).toBeLessThan(0.014);
  }
  await page.route("**/memorial-quad-plaques-review/site.glb", (route) =>
    route.fulfill({ body: "damaged plaque asset" }),
  );
  const fallback = await readPlaques(page);
  expect(fallback).toEqual({
    count: DEFAULT_SELECTABLE_BUILDINGS,
    quad: true,
    plaques: Array(3).fill({ rise: null, clear: true }),
  });
});
