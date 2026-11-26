import { expect, test } from "@playwright/test";

const hall = "roof-9ac93ab7";
const annex = "roof-f0b575d6";
const ids = [hall, annex];

async function ready(page, path = "/") {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

const readSite = (ids) => ({
  count: __campus.getState().buildings,
  doors: __campus.entranceInfo().filter(({ id }) => ids.includes(id)),
  collision: [
    [-401, 211],
    [-462, 252],
    [-439, 231],
    [-439, 235.9],
    [-475, 230],
    [-422.12, 227],
    [-392, 231],
  ].map(([x, z]) => __campus.collisionCheck(x, z)),
  landing: __campus.terrainCheck(-353, 210.74),
});

test("Gerlinger exteriors keep distinct IDs, modeled approaches and breezeway clearance", async ({
  page,
}) => {
  await ready(page);
  const state = await page.evaluate(readSite, ids);
  expect(state.count).toBe(519);
  expect(state.collision).toEqual([true, true, false, true, true, true, false]);
  expect(state.landing["gerlinger-paving"] - state.landing.sampled).toBeCloseTo(
    0.085,
    3,
  );
  expect(
    state.doors.map(({ gate, walkable }) => [gate, walkable]).sort(),
  ).toEqual([
    ["gerlinger-annex-north", true],
    ["gerlinger-hall-east", true],
    ["gerlinger-hall-north", true],
  ]);
  for (const [name, id] of [
    ["Gerlinger Hall", hall],
    ["Gerlinger Annex", annex],
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

test("the historic east portal reaches the interior preview and returns", async ({
  page,
}) => {
  await ready(page);
  await page.evaluate(() => {
    const door = __campus
      .entranceInfo()
      .find(({ gate }) => gate === "gerlinger-hall-east");
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
    .toBe(hall);
  const viewport = await page.locator("#viewport").boundingBox();
  await page.mouse.click(
    viewport.x + viewport.width / 2,
    viewport.y + viewport.height / 2,
  );
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe(hall);
});

test("a damaged package leaves both earlier building models in use", async ({
  page,
}) => {
  await ready(page, "/?exterior-review=gerlinger-baseline");
  const previous = await page.evaluate(readSite, ids);
  await page.route("**/gerlinger-site-review/site.glb", (route) =>
    route.fulfill({ body: "broken Gerlinger mesh" }),
  );
  await ready(page);
  expect(await page.evaluate(readSite, ids)).toEqual(previous);
});
