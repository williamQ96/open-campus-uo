import { expect, test } from "@playwright/test";
import {
  CENTRAL_CAMPUS_PILOT_TREE_REMOVALS,
  DEFAULT_ENTRANCES,
  DEFAULT_PILOT_TREES,
  DEFAULT_SELECTABLE_BUILDINGS,
} from "./exterior-counts.js";

async function fieldState(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const state = campus.getState();
    const sample = (x, n) => campus.terrainCheck(x, -n);
    const places = [
      [-395, -251],
      [-398, -228.7],
      [-429.55, -254],
      [-352, -278],
      [-335, -240],
    ];
    return {
      buildings: state.buildings,
      entrances: state.entranceCount,
      pilotTrees: state.presentation.refinedPilotTrees,
      paved: places.map(([x, n]) =>
        Number.isFinite(sample(x, n)["gerlinger-field-green-surface"]),
      ),
      treads: Array.from(
        { length: 15 },
        (_, i) => sample(-433.46 - ((i + 0.5) * 7.69) / 15, -270.425).standing,
      ),
      wall: campus.collisionCheck(-321.13, 255),
      sidewalk: campus.collisionCheck(-319.25, 255),
    };
  });
}

test("the field keeps its open lawn, perimeter access and stair", async ({
  page,
}) => {
  const state = await fieldState(page);
  expect(state).toMatchObject({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    entrances: DEFAULT_ENTRANCES,
    pilotTrees: DEFAULT_PILOT_TREES,
    paved: Array(5).fill(true),
    wall: true,
    sidewalk: false,
  });
  expect(
    state.treads.every((height, i) => i === 0 || height > state.treads[i - 1]),
  ).toBe(true);
});

test("a damaged field bundle restores the preceding geometry and pilot trees", async ({
  page,
}) => {
  await page.route("**/gerlinger-field-green-review/site.glb", (route) =>
    route.fulfill({ body: "damaged field geometry" }),
  );
  const state = await fieldState(page);
  expect(state).toMatchObject({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    entrances: DEFAULT_ENTRANCES,
    pilotTrees: 273 - CENTRAL_CAMPUS_PILOT_TREE_REMOVALS,
    paved: Array(5).fill(false),
    wall: false,
    sidewalk: false,
  });
});
