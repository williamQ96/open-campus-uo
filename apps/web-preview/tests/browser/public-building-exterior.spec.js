import { expect, test } from "@playwright/test";

const baseline = "/?exterior-review=public-building-exterior-baseline";
const names = new Map([
  ["roof-c1ff8b83", "Clinical Services Building"],
  ["roof-e11ec58d", "Museum of Natural and Cultural History"],
  ["roof-a997a75f", "Outdoor Program Barn"],
  ["roof-b068940e", "Agate Hall"],
]);
const ids = [...names.keys()];

async function snapshot(page, location) {
  await page.goto(location);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const state = __campus.getState();
    const entries = __campus.entranceInfo();
    return {
      count: state.buildings,
      batch: state.presentation.batchedBuildings,
      roads: state.roadSegments,
      names: __campus.namedBuildings().filter(({ id }) => ids.includes(id)),
      approaches: entries.filter(({ id }) => ids.includes(id)),
      others: entries.filter(({ id }) => !ids.includes(id)),
      porchOpen: !__campus.collisionCheck(192.7, 282.4),
      columnBlocks: __campus.collisionCheck(191.5, 286.26),
    };
  }, ids);
}

test("the public exterior review keeps the four IDs and a traversable museum porch", async ({
  page,
}) => {
  const before = await snapshot(page, baseline);
  const after = await snapshot(page, "/");
  expect(after.others).toEqual(before.others);
  expect([after.count, after.batch, after.roads]).toEqual([
    before.count,
    before.batch - 1,
    before.roads,
  ]);
  expect(after.porchOpen && after.columnBlocks).toBe(true);
  expect(after.approaches).toHaveLength(6);
  expect(after.approaches.every(({ gate, walkable }) => gate && walkable)).toBe(
    true,
  );
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of names) {
    await search.fill(name);
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

test("a damaged public exterior restores the previous overlays, names and approaches", async ({
  page,
}) => {
  const before = await snapshot(page, baseline);
  await page.route("**/public-building-exterior-review/site.glb", (route) =>
    route.fulfill({ body: "invalid exterior package" }),
  );
  expect(await snapshot(page, "/")).toEqual(before);
});
