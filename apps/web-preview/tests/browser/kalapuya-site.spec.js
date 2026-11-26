import { expect, test } from "@playwright/test";

const id = "roof-b36ba733";
const baseline = "/?exterior-review=kalapuya-baseline";
const name = "Kalapuya Ilihi Hall";

async function ready(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

async function search(page, name) {
  const input = page.getByRole("combobox", { name: "Search buildings" });
  await input.fill(name);
  await input.press("ArrowDown");
  await input.press("Enter");
}

function inspect(id) {
  const state = __campus.getState();
  return {
    count: state.buildings,
    batches: state.presentation.batchedBuildings,
    roadSegments: state.roadSegments,
    name: __campus.namedBuildings().find((record) => record.id === id)?.name,
    gates: __campus.entranceInfo().filter((gate) => gate.id === id),
    neighbors: __campus.entranceInfo().filter((gate) => gate.id !== id),
    blocked: [
      [250, 434],
      [246, 451],
      [287, 457],
      [293, 422],
      [320, 467],
      [281.2, 471.8],
    ].map(([e, z]) => __campus.collisionCheck(e, z)),
  };
}

test("the full footprint replaces the partial batch member and removes the stale corridor", async ({
  page,
}) => {
  await ready(page, baseline);
  const before = await page.evaluate(inspect, id);
  await ready(page);
  const after = await page.evaluate(inspect, id);
  expect(after.count).toBe(before.count);
  expect(after.batches).toBe(before.batches - 1);
  expect(after.roadSegments).toBe(before.roadSegments - 1);
  expect(after.name).toBe(name);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.blocked).toEqual([true, false, true, false, true, false]);
  expect(after.gates.map(({ gate, walkable }) => [gate, walkable])).toEqual([
    ["kalapuya-north", true],
    ["kalapuya-court", true],
    ["kalapuya-south", true],
  ]);
  await search(page, name);
  await expect
    .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
    .toBe(id);
});

test("directions reach the west courtyard without crossing the new exterior", async ({
  page,
}) => {
  await ready(page);
  await page.locator("#directions-open").click();
  await page.getByRole("button", { name: "Search A", exact: true }).click();
  await search(page, "Global Scholars Hall");
  await page.getByRole("button", { name: "Search B", exact: true }).click();
  await search(page, name);
  await page.locator("#route-start").click();
  const route = await page.evaluate(() => {
    const route = __campus.getState().navigation;
    const blocked = route.points
      .flatMap(([a, b], i) => {
        const next = route.points[i + 1];
        if (!next) return [];
        const count = Math.ceil(Math.hypot(next[0] - a, next[1] - b));
        return Array.from({ length: count + 1 }, (_, j) => {
          const t = j / Math.max(count, 1);
          return __campus.collisionCheck(
            a + (next[0] - a) * t,
            -b - (next[1] - b) * t,
          );
        });
      })
      .some(Boolean);
    return { points: route.points, blocked };
  });
  expect(route.points.length).toBeGreaterThan(2);
  expect(route.blocked).toBe(false);
  expect(route.points.at(-1)[0]).toBeGreaterThan(247);
  expect(route.points.at(-1)[0]).toBeLessThan(284);
});

for (const gate of ["kalapuya-north", "kalapuya-court", "kalapuya-south"]) {
  test(`${gate} enters and returns to its own exterior approach`, async ({
    page,
  }) => {
    await ready(page);
    const point = await page.evaluate((gate) => {
      const entry = __campus.entranceInfo().find((item) => item.gate === gate);
      const player = [entry.approach[0], entry.ground, entry.approach[1]];
      sessionStorage.setItem(
        "explorer:outdoor-return:v1",
        JSON.stringify({
          version: 1,
          buildingId: entry.id,
          player,
          view: "first",
          yaw: Math.atan2(entry.outward[0], entry.outward[1]),
          pitch: 0,
          followDistance: 7.5,
          density: 0,
        }),
      );
      return player;
    }, gate);
    await ready(page, "/?return=1");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().nearbyEntrance))
      .toBe(id);
    await page.getByRole("button", { name: `Enter ${name}` }).click();
    await page.waitForFunction(() => window.__interior?.getState().ready);
    await page.getByRole("button", { name: /Return to campus/ }).click();
    await expect
      .poll(() =>
        page.evaluate(() => window.__campus?.getState().nearbyEntrance),
      )
      .toBe(id);
    const [e, , z] = await page.evaluate(() => __campus.getState().camera);
    expect(e).toBeCloseTo(point[0], 1);
    expect(z).toBeCloseTo(point[2], 1);
  });
}

for (const [label, glob] of [
  ["model", "**/kalapuya-review/site.glb"],
  ["navigation", "**/scene/navigation.json"],
]) {
  test(`a bad ${label} pin restores the old identity, collision and corridor`, async ({
    page,
  }) => {
    await ready(page, baseline);
    const before = await page.evaluate(inspect, id);
    await page.route(
      glob,
      (route) => route.fulfill({ body: "altered bytes" }),
      { times: 1 },
    );
    await ready(page);
    expect(await page.evaluate(inspect, id)).toEqual(before);
  });
}
