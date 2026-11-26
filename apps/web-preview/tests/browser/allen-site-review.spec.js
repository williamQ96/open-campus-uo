import { expect, test } from "@playwright/test";

const id = "roof-7b7893d6";

async function ready(page, path = "/") {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function inspect(id) {
  const entries = __campus.entranceInfo();
  return {
    buildings: __campus.getState().buildings,
    entries: entries.filter((item) => item.id === id),
    neighbors: entries.filter((item) => item.id !== id),
    collision: [
      [-365.95, -76.91],
      [-367.88, -76.91],
      [-318.0, -89.81],
      [-343.71, -71.73],
      [-366.9, -95.0],
      [-326.7, -101.5],
    ].map(([e, z]) => __campus.collisionCheck(e, z)),
  };
}

test("Allen keeps its identity and the three modeled approaches clear", async ({
  page,
}) => {
  await ready(page, "/?exterior-review=allen-baseline");
  const before = await page.evaluate(inspect, id);
  await ready(page);
  const after = await page.evaluate(inspect, id);
  expect(after.buildings).toBe(519);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.collision).toEqual([true, false, false, false, true, true]);
  expect(after.entries.map((e) => e.gate).sort()).toEqual([
    "allen-east",
    "allen-south",
    "allen-west",
  ]);
  for (const entry of after.entries) {
    expect(entry.walkable).toBe(true);
    expect(entry.snapToFacade).toBe(false);
  }
  await page
    .getByRole("combobox", { name: "Search buildings" })
    .fill("Allen Hall");
  await page
    .getByRole("option", { name: /Allen Hall/ })
    .first()
    .click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
    .toBe(id);
});

for (const gate of ["allen-west", "allen-east", "allen-south"]) {
  test(`Allen returns to the ${gate} approach after visiting the interior`, async ({
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
    await page.getByRole("button", { name: /Enter Allen Hall/ }).click();
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

test("damaged Allen geometry restores the prior Allen and neighboring exteriors", async ({
  page,
}) => {
  await ready(page, "/?exterior-review=allen-baseline");
  const before = await page.evaluate(inspect, id);
  await page.route("**/allen-site-review/site.glb", (route) =>
    route.fulfill({ body: "invalid Allen mesh" }),
  );
  await ready(page);
  expect(await page.evaluate(inspect, id)).toEqual(before);
});
