import { expect, test } from "@playwright/test";
import {
  DEFAULT_BACKGROUND_TREES,
  DEFAULT_SELECTABLE_BUILDINGS,
  SCIENCE_GREEN_CONTEXT_TREE_REMOVALS,
  SCIENCE_GREEN_WEST_CONTEXT_TREE_REMOVALS,
} from "./exterior-counts.js";

async function readScienceGreen(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    return {
      count: campus.getState().buildings,
      contextTrees: campus.getState().presentation.refinedContextTrees,
      currentTrees: [
        [-54.978, 67.671],
        [-48.729, 62.618],
        [-47.778, 59.437],
      ].map(([e, n]) => campus.collisionCheck(e, -n)),
      oldTreePath: !campus.collisionCheck(-50.404, -67.166),
      dial: campus.collisionCheck(-59.97, -75.65),
      paving: [
        [-72.56, 19.34],
        [-49.42, 48.43],
        [-49.34, 73.65],
        [-59.97, 74.03],
      ].map(([e, n]) => {
        const surface = campus.terrainCheck(e, -n);
        const height = surface["science-green-paving"];
        return (
          Number.isFinite(height) &&
          Math.abs(surface.standing - height) < 0.025 &&
          !campus.collisionCheck(e, -n)
        );
      }),
      south: Number.isFinite(
        campus.terrainCheck(-77.35, -9.94)["east-thirteenth-east-paving"],
      ),
    };
  });
}

test("the Mays dial and Science Green approach load and fall back together", async ({
  page,
}) => {
  expect(await readScienceGreen(page)).toEqual({
    count: DEFAULT_SELECTABLE_BUILDINGS,
    dial: true,
    contextTrees: DEFAULT_BACKGROUND_TREES,
    currentTrees: Array(3).fill(true),
    oldTreePath: true,
    paving: Array(4).fill(true),
    south: true,
  });
  await page.route("**/science-green-sundial-review/site.glb", (route) =>
    route.fulfill({ body: "invalid sundial mesh" }),
  );
  expect(await readScienceGreen(page)).toEqual({
    count: DEFAULT_SELECTABLE_BUILDINGS,
    dial: false,
    contextTrees:
      DEFAULT_BACKGROUND_TREES +
      SCIENCE_GREEN_CONTEXT_TREE_REMOVALS +
      SCIENCE_GREEN_WEST_CONTEXT_TREE_REMOVALS,
    currentTrees: Array(3).fill(false),
    oldTreePath: true,
    paving: Array(4).fill(false),
    south: true,
  });
});

for (const fixture of [
  "northeast-science-review",
  "east-thirteenth-east-review",
]) {
  test(`the Science Green overlay requires ${fixture}`, async ({ page }) => {
    await page.route(`**/${fixture}/site.glb`, (route) =>
      route.fulfill({ body: "invalid Science Green predecessor" }),
    );
    expect(await readScienceGreen(page)).toMatchObject({
      dial: false,
      currentTrees: Array(3).fill(false),
      paving: Array(4).fill(false),
    });
  });
}
