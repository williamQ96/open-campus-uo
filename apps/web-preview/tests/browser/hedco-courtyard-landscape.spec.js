import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readCourtyard(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const at = (e, n) => campus.terrainCheck(e, -n);
    return {
      buildings: campus.getState().buildings,
      oldCourt: Number.isFinite(at(-673, -434)["hedco-paving"]),
      surfaces: [
        [-673, -434],
        [-679.4, -443.61],
        [-670, -453],
        [-661.3, -430],
      ].map(([e, n]) =>
        Number.isFinite(at(e, n)["hedco-landscape-courtyard-paving"]),
      ),
      fixtures: [
        [-661.3, -430],
        [-661.3, -444],
        [-663.9, -427.2],
        [-672.13, -418.46],
        [-684.52, -447.3],
      ].map(([e, n]) => campus.collisionCheck(e, -n)),
      walk: [
        [-679.4, -443.61],
        [-662.67, -433.6],
        [-674, -448.17],
      ].map(([e, n]) => !campus.collisionCheck(e, -n)),
    };
  });
}

test("HEDCO furnishings and paving fall back together while the courtyard remains open", async ({
  page,
}) => {
  expect(await readCourtyard(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    oldCourt: true,
    surfaces: Array(4).fill(true),
    fixtures: Array(5).fill(true),
    walk: Array(3).fill(true),
  });

  await page.route("**/hedco-courtyard-landscape-review/site.glb", (route) =>
    route.fulfill({ body: "invalid courtyard landscape geometry" }),
  );

  expect(await readCourtyard(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    oldCourt: true,
    surfaces: Array(4).fill(false),
    fixtures: Array(5).fill(false),
    walk: Array(3).fill(true),
  });
});

test("the courtyard landscape falls back when its HEDCO host fails", async ({
  page,
}) => {
  await page.route("**/hedco-exterior-review/site.glb", (route) =>
    route.fulfill({ body: "invalid HEDCO building geometry" }),
  );

  expect(await readCourtyard(page)).toMatchObject({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    oldCourt: false,
    surfaces: Array(4).fill(false),
  });
});
