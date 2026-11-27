import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readOnyx(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const at = (east, north) => {
      const h = campus.terrainCheck(east, -north);
      return {
        plaza: h["onyx-green-walks"] ?? null,
        prior: h["cascade-courtyard-north"] ?? null,
        standing: h.standing,
        blocked: campus.collisionCheck(east, -north),
      };
    };
    return {
      count: campus.getState().buildings,
      walk: [
        [-203.15, 70.64],
        [-190, 66.14],
        [-179.86, 73.35],
        [-172.85, 64.9],
        [-221.48, 38.47],
        [-207.47, 91.36],
        [-202.99, 112.24],
      ].map(([e, n]) => at(e, n)),
      islands: [
        [-200.9, 86.4],
        [-201.5, 99.9],
      ].map(([e, n]) => at(e, n).blocked),
      cascade: at(-207.4, 70.34),
    };
  });
}

test("Onyx Green registers all four walking approaches and both planted islands", async ({
  page,
}) => {
  const scene = await readOnyx(page);
  expect(scene.count).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(scene.cascade.prior).not.toBeNull();
  expect(scene.islands).toEqual([true, true]);
  const heights = [1.255, 1.297, 1.325, 1.359, 3.274, 1.276, 1.215];
  for (const [i, point] of scene.walk.entries()) {
    expect(point.plaza).toBeCloseTo(heights[i], 2);
    expect(point.standing).toBeCloseTo(point.plaza, 3);
    expect(point.blocked).toBe(false);
  }

  await page.route("**/onyx-green-walks-review/site.glb", (route) =>
    route.fulfill({ body: "damaged Onyx Green mesh" }),
  );
  const prior = await readOnyx(page);
  expect(prior.count).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(prior.cascade.prior).toBeCloseTo(scene.cascade.prior, 4);
  expect(prior.walk.every(({ plaza }) => plaza === null)).toBe(true);
  expect(prior.islands).toEqual([false, false]);
});

test("the Onyx Green surface falls back with the Cascade connector", async ({
  page,
}) => {
  await page.route("**/cascade-courtyard-north-review/site.glb", (route) =>
    route.fulfill({ body: "damaged Cascade connector" }),
  );
  const prior = await readOnyx(page);
  expect(prior.count).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(prior.cascade.prior).toBeNull();
  expect(prior.walk.every(({ plaza }) => plaza === null)).toBe(true);
  expect(prior.islands).toEqual([false, false]);
});
