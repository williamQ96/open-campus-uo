import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

const chapman = "roof-f5cea51d";
const condon = "roof-7ffcf31b";
const ids = [chapman, condon];

async function ready(page, path = "/") {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

const read = (ids) => ({
  buildings: __campus.getState().buildings,
  doors: __campus.entranceInfo().filter(({ id }) => ids.includes(id)),
  collision: [
    [-521, 25.9],
    [-523.76, 25.9],
    [-570, 25.35],
    [-567.44, 25.35],
    [-595, 53],
    [-583, 47],
  ].map(([x, z]) => __campus.collisionCheck(x, z)),
});

test("the Memorial Quad exteriors keep their IDs and clear approaches below the steps", async ({
  page,
}) => {
  await ready(page);
  const actual = await page.evaluate(read, ids);
  expect(actual.buildings).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(actual.collision).toEqual([true, false, true, false, true, false]);
  expect(actual.doors.map(({ gate }) => gate).sort()).toEqual([
    "chapman-north",
    "chapman-west",
    "condon-east",
  ]);
  for (const gate of ["chapman-west", "condon-east"]) {
    const door = actual.doors.find((d) => d.gate === gate);
    expect(door.walkable).toBe(true);
    expect(door.thresholdZ - door.ground).toBeGreaterThan(1);
    expect(Math.abs(door.approach[0] - door.position[0])).toBeCloseTo(4.68, 2);
  }
  for (const [label, id] of [
    ["Chapman Hall", chapman],
    ["Condon Hall", condon],
  ]) {
    await page.getByRole("combobox", { name: "Search buildings" }).fill(label);
    await page
      .getByRole("option", { name: new RegExp(label) })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

test("the Chapman steps give access to the interior preview and the same outdoor approach", async ({
  page,
}) => {
  await ready(page);
  await page.evaluate(() => {
    const door = __campus
      .entranceInfo()
      .find(({ gate }) => gate === "chapman-west");
    sessionStorage.setItem(
      "explorer:outdoor-return:v1",
      JSON.stringify({
        version: 1,
        buildingId: door.id,
        player: [door.approach[0], door.ground, door.approach[1]],
        view: "first",
        yaw: Math.atan2(door.outward[0], door.outward[1]),
        pitch: 0,
        followDistance: 7.5,
        density: 0,
      }),
    );
  });
  await ready(page, "/?return=1");
  await expect
    .poll(() => page.evaluate(() => __campus.getState().nearbyEntrance))
    .toBe(chapman);
  await page.getByRole("button", { name: /Enter Chapman Hall/ }).click();
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe(chapman);
});

test("damaged Memorial Quad geometry retains both prior exteriors", async ({
  page,
}) => {
  await ready(page, "/?exterior-review=memorial-baseline");
  const prior = await page.evaluate(read, ids);
  await page.route("**/memorial-quad-review/site.glb", (route) =>
    route.fulfill({ body: "invalid Memorial Quad mesh" }),
  );
  await ready(page);
  expect(await page.evaluate(read, ids)).toEqual(prior);
});
