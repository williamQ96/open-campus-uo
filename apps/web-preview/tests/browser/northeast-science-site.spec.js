import { expect, test } from "@playwright/test";

const baseline = "/?exterior-review=northeast-science-baseline";
const scienceBaseline = "/?exterior-review=science-baseline";
const models = [
  "roof-a5a51275",
  "roof-0f5fbbd5",
  "context-b0038",
  "context-b0040",
  "roof-0ca67b60",
  "context-b0045",
  "roof-34f891de",
];
const retired = ["roof-4041562c", "roof-77c44142", "roof-e495d9f5"];

async function snapshot(page, url) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const view = __campus.getState();
    return {
      count: view.buildings,
      batches: view.presentation.batchedBuildings,
      roads: view.roadSegments,
      names: __campus.namedBuildings(),
      gates: __campus.entranceInfo(),
      occupied: [
        [-205, -123], // Onyx underpass.
        [-211.4, -117.45], // Bridge pier.
        [-247, -139], // Cascade Annex West.
        [-223, -138], // Cascade Annex East.
        [-123, -111], // Space under the Streisinger connection.
        [-96.8, -21], // Huestis south approach.
        [-97.52, -26.3], // Huestis wall.
        [-34.8, -33.3], // Deschutes west entrance recess.
        [-30, -33.1], // Deschutes wall.
      ].map(([e, z]) => __campus.collisionCheck(e, z)),
    };
  });
}

test("science exteriors keep the bridge and the annex ground contacts distinct", async ({
  page,
}) => {
  const previous = await snapshot(page, baseline);
  const current = await snapshot(page, "/");
  expect(current.count).toBe(previous.count - 3);
  expect(current.batches).toBe(previous.batches - 3);
  expect(current.roads).toBe(previous.roads);
  expect(current.names).toEqual(
    expect.arrayContaining([
      expect.objectContaining({
        id: "roof-0f5fbbd5",
        name: "Cascade Annex East",
      }),
      expect.objectContaining({ id: "uo-035", name: "Pacific Hall" }),
    ]),
  );
  const gates = current.gates.filter(({ id }) => models.includes(id));
  expect(gates).toHaveLength(15);
  expect(gates.every(({ gate, walkable }) => gate && walkable)).toBe(true);
  expect(current.gates.some(({ id }) => retired.includes(id))).toBe(false);
  expect(current.occupied).toEqual([
    false,
    true,
    true,
    true,
    false,
    false,
    true,
    false,
    true,
  ]);
});

test("the former Pacific alias stays available if its replacement fails", async ({
  page,
}) => {
  const previous = await snapshot(page, scienceBaseline);
  await page.route("**/lawrence-science-review/site.glb", (route) =>
    route.fulfill({ body: "invalid Pacific reconstruction" }),
  );
  const fallback = await snapshot(page, "/");
  expect(fallback).toEqual(previous);
  expect(fallback.names).toEqual(
    expect.arrayContaining([
      expect.objectContaining({ id: "roof-4041562c", name: "Pacific Hall" }),
    ]),
  );
});
