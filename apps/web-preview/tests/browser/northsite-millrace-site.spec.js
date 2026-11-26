import { expect, test } from "@playwright/test";

const baseline = "/?exterior-review=northsite-millrace-baseline";
const names = {
  "roof-f37c4e05": "Fine Arts Studios Sculpture",
  "roof-1f65a447": "Fine Arts Studios Ceramics",
  "roof-4071cebd": "Fine Arts Studios Metalsmith/Jewelry",
  "roof-37a3afa0": "1600 Millrace Drive",
};
const ids = Object.keys(names);
const probes = [
  [-28, -364], // Sculpture.
  [-26, -335], // Ceramics.
  [-27, -305], // Metalsmith/Jewelry.
  [-34.52, -350], // Clear ground beneath the north passage roof.
  [-34.26, -323], // Clear ground beneath the south passage roof.
  [-5.27, -327.25], // Timber post in the Kiln shelter.
  [0.6, -327.7], // Ground beneath the open Kiln shelter.
  [140, -280], // Millrace office wing.
  [146.5, -313.5], // Entrance path outside the rotunda.
];

async function snapshot(page, path) {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(
    ({ ids, probes }) => {
      const state = __campus.getState();
      const gates = __campus.entranceInfo();
      return {
        count: state.buildings,
        batch: state.presentation.batchedBuildings,
        roads: state.roadSegments,
        names: Object.fromEntries(
          __campus
            .namedBuildings()
            .filter(({ id }) => ids.includes(id))
            .map(({ id, name }) => [id, name]),
        ),
        entries: gates.filter(({ id }) => ids.includes(id)),
        neighbors: gates.filter(({ id }) => !ids.includes(id)),
        collision: probes.map(([e, z]) => __campus.collisionCheck(e, z)),
      };
    },
    { ids, probes },
  );
}

test("the Northsite and Millrace rebuild preserves source IDs and open covered passages", async ({
  page,
}) => {
  const previous = await snapshot(page, baseline);
  const current = await snapshot(page, "/");
  expect(Object.keys(previous.names)).toHaveLength(0);
  expect(current.names).toEqual(names);
  expect([current.count, current.batch, current.roads]).toEqual([
    previous.count,
    previous.batch - 4,
    previous.roads,
  ]);
  expect(current.neighbors).toEqual(previous.neighbors);
  expect(current.entries).toHaveLength(6);
  expect(current.entries.every(({ gate, walkable }) => gate && walkable)).toBe(
    true,
  );
  expect(current.collision).toEqual([
    true,
    true,
    true,
    false,
    false,
    true,
    false,
    true,
    false,
  ]);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(names)) {
    await search.fill(name);
    await page.getByRole("option", { name }).first().click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

test("an invalid Northsite asset restores all four source batches and selection records", async ({
  page,
}) => {
  const previous = await snapshot(page, baseline);
  await page.route("**/northsite-millrace-review/site.glb", (route) =>
    route.fulfill({ body: "invalid exterior" }),
  );
  const fallback = await snapshot(page, "/");
  expect(fallback).toEqual(previous);
});
