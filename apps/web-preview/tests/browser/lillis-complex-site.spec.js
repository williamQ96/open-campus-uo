import { expect, test } from "@playwright/test";

const retired = "roof-7fee2881";
const names = [
  ["roof-1afe792e", "Chiles Business Center"],
  ["roof-0a498bf7", "Anstett Hall"],
  ["roof-75e776d0", "Peterson Hall"],
  ["roof-86754ad7", "Lillis Hall"],
  ["context-b0039", "Computing Center"],
];

async function inspect(page, url) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(
    ({ ids, retired }) => {
      const state = __campus.getState();
      const gates = __campus.entranceInfo();
      return {
        count: state.buildings,
        batches: state.presentation.batchedBuildings,
        roads: state.roadSegments,
        gates: gates.filter(({ id }) => ids.includes(id)),
        neighbors: gates.filter(
          ({ id }) => !ids.includes(id) && id !== retired,
        ),
        retired: gates.some(({ id }) => id === retired),
        blocked: [
          [-564, -27.23], // Peterson stair approach.
          [-563.34, -28.98], // Peterson stair wall.
          [-548, -24.5], // Courtyard axis.
          [-554, -27], // Courtyard planter.
          [-598.787, -109.3], // Computing Center's recessed entry.
          [-598.787, -105.2], // Computing Center's north wall.
        ].map(([e, z]) => __campus.collisionCheck(e, z)),
      };
    },
    { ids: names.map(([id]) => id), retired },
  );
}

test("five registered buildings share a clear courtyard and one old wing is retired", async ({
  page,
}) => {
  const before = await inspect(
    page,
    "/?exterior-review=lillis-complex-baseline",
  );
  const after = await inspect(page, "/");
  expect(before.retired).toBe(true);
  expect(after.retired).toBe(false);
  expect(after.count).toBe(before.count - 1);
  expect(after.batches).toBe(before.batches - 1);
  expect(after.roads).toBe(before.roads);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.blocked).toEqual([false, true, false, true, false, true]);
  expect(after.gates).toHaveLength(9);
  expect(after.gates.every(({ walkable, gate }) => walkable && gate)).toBe(
    true,
  );
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of names) {
    await search.fill(name);
    await search.press("ArrowDown");
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});
