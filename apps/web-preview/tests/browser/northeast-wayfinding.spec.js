import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readWayfinding(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    return {
      buildings: campus.getState().buildings,
      pavement: [
        [35, 92.22],
        [-191.55, 154.92],
        [-192.15, 151.92],
        [-199, 162.4],
      ].map(([e, n]) =>
        Number.isFinite(
          campus.terrainCheck(e, -n)["northeast-wayfinding-paving"],
        ),
      ),
      fixtures: [
        [35.15, 95.27],
        [-196.7, 155.6],
        [-192.92, 155.26],
        [-190.28, 154.45],
        [-204.758, 155.183],
      ].map(([e, n]) => campus.collisionCheck(e, -n)),
      entryOpen: !campus.collisionCheck(-191.55, -154.92),
    };
  });
}

test("wayfinding installs both sites together and clears the new collisions on fallback", async ({
  page,
}) => {
  expect(await readWayfinding(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    pavement: [true, true, true, true],
    fixtures: [true, true, true, true, true],
    entryOpen: true,
  });

  await page.route("**/northeast-campus-wayfinding-review/site.glb", (route) =>
    route.fulfill({ body: "invalid northeast wayfinding geometry" }),
  );
  expect(await readWayfinding(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    pavement: [false, false, false, false],
    fixtures: [false, false, false, false, false],
    entryOpen: true,
  });
});
