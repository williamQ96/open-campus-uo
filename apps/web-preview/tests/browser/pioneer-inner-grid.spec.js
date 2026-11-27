import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readPlots(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const track = campus.terrainCheck(-478.1, 331.82);
    return {
      buildings: campus.getState().buildings,
      grass: track["pioneer-inner-grid-grass"] ?? null,
      marker: campus.collisionCheck(-389.917, 506.583),
      dorris: Number.isFinite(
        campus.terrainCheck(-419.65, 387.72)["pioneer-cemetery-paving"],
      ),
    };
  });
}

test("inner plot details install and fall back independently of the named roads", async ({
  page,
}) => {
  expect(await readPlots(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    grass: expect.any(Number),
    marker: true,
    dorris: true,
  });

  await page.route("**/pioneer-cemetery-inner-grid-review/site.glb", (route) =>
    route.fulfill({ body: "invalid inner plot geometry" }),
  );

  expect(await readPlots(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    grass: null,
    marker: false,
    dorris: true,
  });
});

test("a damaged base cemetery also rolls back its inner plot details", async ({
  page,
}) => {
  await page.route("**/pioneer-cemetery-landscape-review/site.glb", (route) =>
    route.fulfill({ body: "invalid base cemetery geometry" }),
  );
  expect(await readPlots(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    grass: null,
    marker: false,
    dorris: false,
  });
});
