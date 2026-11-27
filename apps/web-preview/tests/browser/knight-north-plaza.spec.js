import { expect, test } from "@playwright/test";
import {
  DEFAULT_PILOT_TREES,
  DEFAULT_SELECTABLE_BUILDINGS,
  KNIGHT_PLAZA_PILOT_TREE_REMOVALS,
} from "./exterior-counts.js";

async function readPlaza(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const eastWalk = campus.terrainCheck(-525.46, 184.77);
    return {
      buildings: campus.getState().buildings,
      pilotTrees: campus.getState().presentation.refinedPilotTrees,
      eastWalk: eastWalk["knight-north-plaza-paving"] ?? null,
      basinBlocked: campus.collisionCheck(-549.03, 181.1),
      westEntrance: campus
        .entranceInfo()
        .some(
          ({ id, gate }) => id === "roof-6684e091" && gate === "memorial-west",
        ),
    };
  });
}

test("the Knight north plaza blocks the basin and falls back independently", async ({
  page,
}) => {
  expect(await readPlaza(page)).toMatchObject({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    pilotTrees: DEFAULT_PILOT_TREES,
    eastWalk: expect.any(Number),
    basinBlocked: true,
    westEntrance: true,
  });
  await page.route("**/knight-north-plaza-review/site.glb", (route) =>
    route.fulfill({ body: "damaged north plaza geometry" }),
  );
  expect(await readPlaza(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    pilotTrees: DEFAULT_PILOT_TREES + KNIGHT_PLAZA_PILOT_TREE_REMOVALS,
    eastWalk: null,
    basinBlocked: false,
    westEntrance: true,
  });
});
