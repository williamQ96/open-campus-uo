import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readCourt(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const state = campus.getState();
    return {
      buildings: state.buildings,
      quad: state.presentation.refinedPavingCorridors?.quad ?? false,
      tread:
        campus.terrainCheck(-569.9, 131.4)["plc-east-court-paving"] ?? null,
      bed: campus.collisionCheck(-578.21, 135.06),
      rails: [
        [-569.74, 132.48],
        [-569.74, 126.28],
        [-569.74, 129.5],
      ].map(([x, z]) => campus.collisionCheck(x, z)),
      eastGate: campus
        .entranceInfo()
        .some(
          ({ id, gate }) => id === "roof-8f611273" && gate === "plc-court-east",
        ),
    };
  });
}

test("the PLC court falls back without replacing its host building or Quad", async ({
  page,
}) => {
  expect(await readCourt(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    quad: true,
    tread: expect.any(Number),
    bed: true,
    rails: [true, true, false],
    eastGate: true,
  });
  await page.route("**/plc-east-court-review/site.glb", (route) =>
    route.fulfill({ body: "damaged PLC court geometry" }),
  );
  expect(await readCourt(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    quad: true,
    tread: null,
    bed: false,
    rails: [false, false, false],
    eastGate: true,
  });
});

test("the raised court stays available when the Quad bundle fails", async ({
  page,
}) => {
  await page.route("**/paving-corridors-l2/surfaces.glb", (route) =>
    route.fulfill({ body: "damaged Quad geometry" }),
  );
  expect(await readCourt(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    quad: false,
    tread: expect.any(Number),
    bed: true,
    rails: [true, true, false],
    eastGate: true,
  });
});
