import { expect, test } from "@playwright/test";

const university = "roof-9017feee";
const villard = "roof-399c648e";
const theater = "roof-944fcd46";

async function ready(page, path = "/") {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function inspect(ids) {
  const gates = __campus.entranceInfo();
  return {
    count: __campus.getState().buildings,
    neighbors: gates.filter((door) => !ids.includes(door.id)),
    doors: gates.filter((door) => ids.includes(door.id)),
    blocked: [
      [-433.1, -123.75],
      [-430.72, -123.75],
      [-475.0, -123.85],
      [-477.78, -123.85],
      [-436.4, -184.93],
      [-434.43, -184.93],
      [-465.0, -185.0],
    ].map(([e, z]) => __campus.collisionCheck(e, z)),
  };
}

test("University and Villard keep their building identities and close the theater joint", async ({
  page,
}) => {
  const ids = [university, villard];
  await ready(page, "/?exterior-review=heritage-baseline");
  const before = await page.evaluate(inspect, ids);
  await ready(page, "/?exterior-review=miller-baseline");
  const after = await page.evaluate(inspect, ids);
  expect(after.count).toBe(519);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(before.blocked.at(-1)).toBe(false);
  expect(after.blocked).toEqual([true, false, true, false, true, false, true]);
  expect(after.doors.map(({ gate }) => gate).sort()).toEqual([
    "university-east",
    "university-west",
    "villard-east",
  ]);
  for (const door of after.doors) {
    expect(door.walkable).toBe(true);
    expect(door.thresholdZ).toBeGreaterThan(door.ground);
  }
  for (const [name, id] of [
    ["University Hall", university],
    ["Villard Hall", villard],
    ["Miller Theatre", theater],
  ]) {
    const search = page.getByRole("combobox", { name: "Search buildings" });
    await search.fill(name);
    await page
      .getByRole("option", { name: new RegExp(name) })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

for (const [target, id, name] of [
  ["university-east", university, "University Hall"],
  ["university-west", university, "University Hall"],
  ["villard-east", villard, "Villard Hall"],
]) {
  test(`the ${target} stair approach survives a preview visit`, async ({
    page,
  }) => {
    await ready(page);
    const point = await page.evaluate((target) => {
      const door = __campus.entranceInfo().find(({ gate }) => gate === target);
      const player = [door.approach[0], door.ground, door.approach[1]];
      sessionStorage.setItem(
        "explorer:outdoor-return:v1",
        JSON.stringify({
          version: 1,
          buildingId: door.id,
          player,
          view: "first",
          yaw: Math.atan2(door.outward[0], door.outward[1]),
          pitch: 0,
          followDistance: 7.5,
          density: 0,
        }),
      );
      return player;
    }, target);
    await ready(page, "/?return=1");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().nearbyEntrance))
      .toBe(id);
    await page
      .getByRole("button", { name: new RegExp("Enter " + name) })
      .click();
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

test("a damaged Heritage Core package restores both prior exteriors", async ({
  page,
}) => {
  const ids = [university, villard];
  await ready(page, "/?exterior-review=heritage-baseline");
  const before = await page.evaluate(inspect, ids);
  await page.route("**/heritage-core-review/site.glb", (route) =>
    route.fulfill({ body: "invalid Heritage Core mesh" }),
  );
  await ready(page, "/?exterior-review=miller-baseline");
  expect(await page.evaluate(inspect, ids)).toEqual(before);
});
