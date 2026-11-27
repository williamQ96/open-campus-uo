import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readOregonGrounds(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const at = (e, n) => campus.terrainCheck(e, -n);
    return {
      buildings: campus.getState().buildings,
      bed: [
        [50, 17],
        [56, 18],
        [63, 19],
      ].map(([e, n]) => Number.isFinite(at(e, n)["oregon-southeast-grounds"])),
      apron: [
        [43.61, 17.26],
        [46.53, 18.01],
        [44.58, 22.46],
        [63.5, 13.15],
      ].map(([e, n]) => {
        const ground = at(e, n);
        return (
          Math.abs(ground.standing - ground.sampled - 0.113) < 0.02 &&
          !campus.collisionCheck(e, -n)
        );
      }),
      fixtures: [
        [79.332, 14.366],
        [78.214, 19.023],
        [46.236, 19.721],
        [44.974, 24.595],
        [46.452, 22.786],
        [64.043, 14.074],
        [43.847, 25.332],
        [65.907, 13.871],
      ].map(([e, n]) => campus.collisionCheck(e, -n)),
      sidewalk: [
        [42, 10.9],
        [57, 10.8],
        [73, 10.5],
        [80, 10.1],
      ].map(
        ([e, n]) =>
          Number.isFinite(at(e, n)["east-thirteenth-east-paving"]) &&
          !campus.collisionCheck(e, -n),
      ),
    };
  });
}

test("Oregon Hall fixtures and foundation bed install without narrowing the East 13th route", async ({
  page,
}) => {
  expect(await readOregonGrounds(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    bed: Array(3).fill(true),
    apron: Array(4).fill(true),
    fixtures: Array(8).fill(true),
    sidewalk: Array(4).fill(true),
  });
  await page.route(
    "**/oregon-hall-southeast-landscape-review/site.glb",
    (route) => route.fulfill({ body: "invalid Oregon landscape geometry" }),
  );
  expect(await readOregonGrounds(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    bed: Array(3).fill(false),
    apron: Array(4).fill(false),
    fixtures: Array(8).fill(false),
    sidewalk: Array(4).fill(true),
  });
});

for (const prerequisite of [
  "oregon-jaqua-review",
  "east-thirteenth-east-review",
]) {
  test(`the grounds depend on the ${prerequisite} registration`, async ({
    page,
  }) => {
    await page.route(`**/${prerequisite}/site.glb`, (route) =>
      route.fulfill({ body: "invalid Oregon grounds prerequisite" }),
    );
    expect(await readOregonGrounds(page)).toMatchObject({
      buildings: DEFAULT_SELECTABLE_BUILDINGS,
      bed: Array(3).fill(false),
      apron: Array(4).fill(false),
      fixtures: Array(8).fill(false),
    });
  });
}
