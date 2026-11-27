import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readCourtyard(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const at = (east, north) => campus.terrainCheck(east, -north);
    const probes = [
      [-247.1, 21],
      [-246.7, 41],
      [-249.79, 58.85],
      [-249.79, 59.61],
      [-249.79, 60.02],
      [-249.79, 60.44],
      [-249.79, 60.85],
      [-249.79, 61.26],
      [-249.79, 61.68],
      [-249.79, 62.09],
      [-249.79, 62.55],
      [-250.14, 66.42],
      [-244.98, 66.55],
    ];
    const results = probes.map(([e, n]) => {
      const ground = at(e, n);
      const paving = ground["cascade-courtyard-access"];
      return {
        paving: Number.isFinite(paving) ? paving : null,
        standing: ground.standing,
        clear: !campus.collisionCheck(e, -n),
      };
    });
    return {
      buildings: campus.getState().buildings,
      results,
      fountain: [
        [-245.93, 62.97],
        [-246.5, 64.71],
        [-240.2, 60.9],
        [-246.61, 65.05],
        [-241.2, 64.9],
      ].map(([e, n]) => campus.collisionCheck(e, -n)),
      rails: [-250.55, -249.03].map((e) => campus.collisionCheck(e, -60.8)),
    };
  });
}

test("the Volcanology west walk descends by seven walkable treads into the courtyard", async ({
  page,
}) => {
  const current = await readCourtyard(page);
  expect(current.buildings).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(current.fountain).toEqual([true, true, true, true, false]);
  expect(current.rails).toEqual([true, true]);
  for (const { paving, standing, clear } of current.results) {
    expect(paving).not.toBeNull();
    expect(standing).toBeCloseTo(paving, 2);
    expect(clear).toBe(true);
  }
  const levels = current.results.slice(2, 11).map(({ paving }) => paving);
  expect(levels[0] - levels.at(-1)).toBeCloseTo(1.19, 1);
  for (let i = 1; i < levels.length; i += 1) {
    expect(levels[i - 1] - levels[i]).toBeCloseTo(0.149, 2);
  }
  await page.route("**/cascade-courtyard-access-review/site.glb", (route) =>
    route.fulfill({ body: "damaged courtyard walk" }),
  );
  const prior = await readCourtyard(page);
  expect(prior.results.map(({ paving }) => paving)).toEqual(
    Array(current.results.length).fill(null),
  );
  expect(prior).toMatchObject({
    fountain: Array(5).fill(false),
    rails: [false, false],
  });
});

for (const packageName of [
  "cascade-volcanology-review",
  "east-thirteenth-east-review",
]) {
  test(`the Cascade courtyard access requires ${packageName}`, async ({
    page,
  }) => {
    await page.route(`**/${packageName}/site.glb`, (route) =>
      route.fulfill({ body: "damaged courtyard predecessor" }),
    );
    const state = await readCourtyard(page);
    expect(state.results.every(({ paving }) => paving === null)).toBe(true);
    // The original Cascade collision returns when its host overlay is unavailable.
    const originalHost = packageName === "cascade-volcanology-review";
    expect(state.fountain).toEqual([
      false,
      false,
      originalHost,
      false,
      originalHost,
    ]);
  });
}
