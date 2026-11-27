import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readWestBelt(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    return {
      buildings: campus.getState().buildings,
      stems: [
        [-525.734, -387.276],
        [-520.655, -472.475],
        [-527.305, -494.115],
        [-544.405, -594.703],
      ].map(([e, n]) => campus.collisionCheck(e, -n)),
      lane: Number.isFinite(
        campus.terrainCheck(-534.1, 508)["frohnmayer-east-drive-paving"],
      ),
      openRoutes: [
        [-518.5, -466.9],
        [-534.2, -468.4],
        [-535.24, -600.22],
      ].every(([e, n]) => !campus.collisionCheck(e, -n)),
    };
  });
}

test("registered west belt trunks fall back independently of the road", async ({
  page,
}) => {
  expect(await readWestBelt(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    stems: [true, true, true, true],
    lane: true,
    openRoutes: true,
  });
  await page.route("**/pioneer-cemetery-west-trees-review/site.glb", (route) =>
    route.fulfill({ body: "invalid west-belt mesh" }),
  );
  expect(await readWestBelt(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    stems: [false, false, false, false],
    lane: true,
    openRoutes: true,
  });
});

test("west belt falls back with its pinned Frohnmayer predecessor", async ({
  page,
}) => {
  await page.route("**/frohnmayer-east-drive-review/site.glb", (route) =>
    route.fulfill({ body: "invalid Frohnmayer paving" }),
  );
  expect(await readWestBelt(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    stems: [false, false, false, false],
    lane: false,
    openRoutes: true,
  });
});
