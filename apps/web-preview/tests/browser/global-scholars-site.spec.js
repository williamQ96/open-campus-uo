import { expect, test } from "@playwright/test";

const id = "context-b0158";
const baseline = "/?exterior-review=scholars-baseline";
const name = "Global Scholars Hall";

async function load(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function inspect(id) {
  const state = __campus.getState();
  const entries = __campus.entranceInfo();
  return {
    count: state.buildings,
    batches: state.presentation.batchedBuildings,
    roads: state.roadSegments,
    name: __campus.namedBuildings().find((b) => b.id === id)?.name,
    entries: entries.filter((gate) => gate.id === id),
    neighbors: entries.filter((gate) => gate.id !== id),
    collision: [
      [314, 268],
      [311, 291],
      [283, 289],
      [313, 333],
      [315, 355],
      [344, 296],
    ].map(([e, z]) => __campus.collisionCheck(e, z)),
  };
}

test("the three wings retain one identity and both courts are open", async ({
  page,
}) => {
  await load(page, baseline);
  const before = await page.evaluate(inspect, id);
  await load(page);
  const after = await page.evaluate(inspect, id);
  expect(after.count).toBe(before.count);
  expect(after.batches).toBe(before.batches);
  expect(after.roads).toBe(before.roads);
  expect(after.name).toBe(name);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.collision).toEqual([true, false, true, false, true, false]);
  expect(after.entries.map(({ gate, walkable }) => [gate, walkable])).toEqual([
    ["scholars-north", true],
    ["scholars-west", true],
    ["scholars-south", true],
    ["scholars-court", true],
  ]);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill(name);
  await search.press("ArrowDown");
  await search.press("Enter");
  await expect
    .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
    .toBe(id);
});

test("a damaged exterior restores the prior selection, collision and entrance", async ({
  page,
}) => {
  await load(page, baseline);
  const before = await page.evaluate(inspect, id);
  await page.route("**/global-scholars-review/site.glb", (route) =>
    route.fulfill({ status: 200, body: "bad model pin" }),
  );
  await load(page);
  expect(await page.evaluate(inspect, id)).toEqual(before);
});

for (const gate of ["scholars-north", "scholars-court"]) {
  test(`${gate} returns to its own modeled threshold`, async ({ page }) => {
    await load(page);
    const coords = await page.evaluate((gate) => {
      const { id, approach, ground, outward } = __campus
        .entranceInfo()
        .find((entry) => entry.gate === gate);
      const player = [approach[0], ground, approach[1]];
      sessionStorage.setItem(
        "explorer:outdoor-return:v1",
        JSON.stringify({
          version: 1,
          buildingId: id,
          player,
          view: "first",
          yaw: Math.atan2(outward[0], outward[1]),
          pitch: 0,
          followDistance: 7.5,
          density: 0,
        }),
      );
      return player;
    }, gate);
    await load(page, "/?return=1");
    await page.getByRole("button", { name: `Enter ${name}` }).click();
    await page.waitForFunction(() => window.__interior?.getState().ready);
    await page.getByRole("button", { name: /Return to campus/ }).click();
    await expect
      .poll(() =>
        page.evaluate(() => window.__campus?.getState().nearbyEntrance),
      )
      .toBe(id);
    const [e, , z] = await page.evaluate(() => __campus.getState().camera);
    expect(e).toBeCloseTo(coords[0], 1);
    expect(z).toBeCloseTo(coords[2], 1);
  });
}
