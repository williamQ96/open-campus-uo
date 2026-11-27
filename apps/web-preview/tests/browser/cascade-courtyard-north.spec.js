import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readNorthCourt(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const ground = ([east, north]) => campus.terrainCheck(east, -north);
    const walk = (point) => {
      const [east, north] = point;
      const sample = ground(point);
      const surface = sample["cascade-courtyard-north"];
      return {
        surface: surface ?? null,
        standing: sample.standing,
        clear: !campus.collisionCheck(east, -north),
      };
    };
    return {
      count: campus.getState().buildings,
      passes: [
        [-249.12, 49],
        [-259.15, 63],
        [-258.02, 73.23],
        [-256.02, 93.8],
        [-260.1, 124.91],
        [-254.7, 72.04],
        [-239.55, 73.32],
        [-237.76, 75.4],
      ].map(walk),
      treads: [
        [-242.265, 71.588],
        [-241.755, 72.025],
        [-241.245, 72.462],
      ].map(walk),
      scienceWalk: [
        [-235.5, 73.57],
        [-231.94, 73.5],
        [-222.5, 71.85],
        [-207.4, 70.34],
      ].map(walk),
      redwood: campus.collisionCheck(-222.42, -67.77),
      supports: campus.collisionCheck(-239.2, -70.7),
      southwest: Boolean(ground([-249.79, 60.85])["cascade-courtyard-access"]),
    };
  });
}

test("the Pacific Hall loop and Science Walk register their walking surfaces", async ({
  page,
}) => {
  const scene = await readNorthCourt(page);
  expect(scene.count).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(scene.supports).toBe(true);
  expect(scene.southwest).toBe(true);
  expect(scene.redwood).toBe(true);
  for (const point of [
    ...scene.passes,
    ...scene.treads,
    ...scene.scienceWalk,
  ]) {
    expect(point.surface).not.toBeNull();
    expect(point.clear).toBe(true);
    expect(point.standing).toBeCloseTo(point.surface, 2);
  }
  for (const [i, height] of [2.466, 2.348, 2.23].entries()) {
    expect(scene.treads[i].surface).toBeCloseTo(height, 2);
  }

  for (const [i, height] of [2.011, 1.872, 1.495, 1.256].entries()) {
    expect(scene.scienceWalk[i].surface).toBeCloseTo(height, 2);
  }

  await page.route("**/cascade-courtyard-north-review/site.glb", (route) =>
    route.fulfill({ body: "damaged Cascade north mesh" }),
  );
  const prior = await readNorthCourt(page);
  expect(prior.count).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(prior.southwest).toBe(true);
  expect(prior.supports).toBe(true);
  expect(prior.redwood).toBe(false);
  expect(
    [...prior.passes, ...prior.treads, ...prior.scienceWalk].every(
      (p) => p.surface === null,
    ),
  ).toBe(true);
});

test("the north paths fall back with the connecting south package", async ({
  page,
}) => {
  await page.route("**/cascade-courtyard-access-review/site.glb", (route) =>
    route.fulfill({ body: "damaged Cascade south predecessor" }),
  );
  const prior = await readNorthCourt(page);
  expect(prior.count).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(prior.southwest).toBe(false);
  expect(prior.supports).toBe(true);
  expect(prior.redwood).toBe(false);
  expect(
    [...prior.passes, ...prior.treads, ...prior.scienceWalk].every(
      (p) => p.surface === null,
    ),
  ).toBe(true);
});
