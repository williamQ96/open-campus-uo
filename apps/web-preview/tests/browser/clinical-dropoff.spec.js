import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readDropoff(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    return {
      buildings: campus.getState().buildings,
      crossings: [
        [-675.25, 495.2],
        [-700.188, 495.2],
      ].map(([e, z]) => [
        campus.terrainCheck(e, z)["clinical-dropoff-paving"] ?? null,
        campus.collisionCheck(e, z),
      ]),
      islandBlocked: campus.collisionCheck(-635.4, 501),
      kendall: Number.isFinite(
        campus.terrainCheck(-630.78, 466)["kendall-plaza-paving"],
      ),
    };
  });
}

test("the drop-off preserves both crossings and restores the preceding scene on failure", async ({
  page,
}) => {
  expect(await readDropoff(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    crossings: [
      [expect.any(Number), false],
      [expect.any(Number), false],
    ],
    islandBlocked: true,
    kendall: true,
  });

  await page.route("**/clinical-dropoff-landscape-review/site.glb", (route) =>
    route.fulfill({ body: "invalid drop-off geometry" }),
  );

  expect(await readDropoff(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    crossings: [
      [null, false],
      [null, false],
    ],
    islandBlocked: false,
    kendall: true,
  });
});

test("the dependent drop-off rolls back with the Kendall approach", async ({
  page,
}) => {
  await page.route("**/kendall-plaza-landscape-review/site.glb", (route) =>
    route.fulfill({ body: "invalid Kendall geometry" }),
  );
  expect(await readDropoff(page)).toMatchObject({
    crossings: [
      [null, false],
      [null, false],
    ],
    islandBlocked: false,
    kendall: false,
  });
});
