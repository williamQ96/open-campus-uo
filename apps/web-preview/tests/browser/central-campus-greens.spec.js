import { expect, test } from "@playwright/test";
import {
  CENTRAL_CAMPUS_PILOT_TREE_REMOVALS,
  DEFAULT_ENTRANCES,
  DEFAULT_PILOT_TREES,
  DEFAULT_SELECTABLE_BUILDINGS,
} from "./exterior-counts.js";

async function greenState(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const state = campus.getState();
    const terrain = (x, n) => campus.terrainCheck(x, -n);
    const spots = [
      [-401.05, -135.95],
      [-415.56, -167.99],
      [-401.7, -154.45],
      [-331.5, -224],
      [-319.1, -217],
      [-255.7, -210.2],
      [-281, -184.12],
      [-307.9, -181.41],
      [-307.895, -183.058],
    ];
    return {
      buildings: state.buildings,
      entrances: state.entranceCount,
      trees: state.presentation.refinedPilotTrees,
      shrubs: state.presentation.refinedUnderstory.shrubs,
      sampleHits: spots.map(([x, n]) =>
        Number.isFinite(terrain(x, n)["central-campus-greens-surface"]),
      ),
      stairHeights: [
        [-415.56, -167.99, 1.91],
        [-386.83, -168.01, 1.96],
      ].map(([x, n, run]) =>
        Array.from(
          { length: 3 },
          (_, i) => terrain(x, n + run / 2 - ((i + 0.5) * run) / 3).standing,
        ),
      ),
      wall: campus.collisionCheck(-407, 167.92),
      gap: campus.collisionCheck(-415.56, 167.99),
    };
  });
}

test("central greens retain open paths, the stone wall and both stairs", async ({
  page,
}) => {
  const state = await greenState(page);
  expect(state).toMatchObject({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    entrances: DEFAULT_ENTRANCES,
    trees: DEFAULT_PILOT_TREES,
    shrubs: 59,
    sampleHits: Array(9).fill(true),
    wall: true,
    gap: false,
  });
  for (const flight of state.stairHeights) {
    expect(flight[0]).toBeLessThan(flight[1]);
    expect(flight[1]).toBeLessThan(flight[2]);
  }
});

test("a corrupt central green bundle restores prior vegetation and access", async ({
  page,
}) => {
  await page.route("**/central-campus-greens-review/site.glb", (route) =>
    route.fulfill({ body: "damaged campus greens" }),
  );
  expect(await greenState(page)).toMatchObject({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    entrances: DEFAULT_ENTRANCES,
    trees: DEFAULT_PILOT_TREES + CENTRAL_CAMPUS_PILOT_TREE_REMOVALS,
    shrubs: 63,
    sampleHits: Array(9).fill(false),
    wall: false,
    gap: false,
  });
});
