import { expect, test } from "@playwright/test";

const ids = ["roof-0de7fadb", "context-oc-unthank"];
const baseline = "/?exterior-review=bean-unthank-baseline";

async function load(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function siteState(ids) {
  const state = __campus.getState();
  const gates = __campus.entranceInfo();
  return {
    count: state.buildings,
    batches: state.presentation.batchedBuildings,
    roads: state.roadSegments,
    gates: gates.filter(({ id }) => ids.includes(id)),
    neighbors: gates.filter(({ id }) => !ids.includes(id)),
    collision: [
      [236, 197],
      [300, 178],
      [196.8, 181],
      [234, 215],
      [300, 199],
      [148, 182],
    ].map(([e, z]) => __campus.collisionCheck(e, z)),
  };
}

test("Bean's two courtyards and the passage beside Unthank are open", async ({
  page,
}) => {
  await load(page, baseline);
  const before = await page.evaluate(siteState, ids);
  await load(page);
  const after = await page.evaluate(siteState, ids);
  expect(before.collision.slice(0, 3)).toEqual([false, true, true]);
  expect(after.collision).toEqual([false, false, false, true, true, true]);
  expect(after.count).toBe(before.count);
  expect(after.batches).toBe(before.batches);
  expect(after.roads).toBe(before.roads);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(
    after.gates.map(({ id, gate, walkable }) => [id, gate, walkable]),
  ).toEqual([
    [ids[0], "north-commons", true],
    [ids[0], "south-commons", true],
    [ids[1], "market-west", true],
    [ids[1], "market-north", true],
    [ids[1], "welcome-north", true],
    [ids[1], "market-south", true],
  ]);
});

test("a damaged shared package restores both previous footprints and entries", async ({
  page,
}) => {
  await load(page, baseline);
  const before = await page.evaluate(siteState, ids);
  await page.route("**/bean-unthank-review/site.glb", (route) =>
    route.fulfill({ status: 200, body: "bad model pin" }),
  );
  await load(page);
  expect(await page.evaluate(siteState, ids)).toEqual(before);
});
