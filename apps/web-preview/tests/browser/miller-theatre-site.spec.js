import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

const id = "roof-944fcd46";

async function ready(page, path = "/") {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function inspect(id) {
  const entries = __campus.entranceInfo();
  return {
    buildings: __campus.getState().buildings,
    entry: entries.find((entry) => entry.id === id),
    others: entries.filter((entry) => entry.id !== id),
    collisions: [
      [-518.0, -183.4],
      [-520.93, -183.4],
      [-524.5, -183.4],
      [-527.0, -183.4],
      [-531.0, -183.4],
      [-460.2, -196.25],
    ].map(([e, z]) => __campus.collisionCheck(e, z)),
  };
}

test("the Miller model keeps its ID, clears the west landing and closes the northern joint", async ({
  page,
}) => {
  await ready(page, "/?exterior-review=miller-baseline");
  const previous = await page.evaluate(inspect, id);
  await ready(page);
  const actual = await page.evaluate(inspect, id);
  expect(actual.buildings).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(actual.others).toEqual(previous.others);
  expect(actual.entry).toMatchObject({
    id,
    gate: "miller-west",
    walkable: true,
    snapToFacade: false,
  });
  expect(actual.entry.thresholdZ - actual.entry.ground).toBeGreaterThan(0.8);
  expect(previous.collisions.at(-1)).toBe(false);
  expect(actual.collisions).toEqual([true, false, true, false, true, true]);
});

test("the Miller west entrance returns to the landing after visiting the interior", async ({
  page,
}) => {
  await ready(page);
  const player = await page.evaluate((id) => {
    const entry = __campus.entranceInfo().find((item) => item.id === id);
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
  }, id);
  await ready(page, "/?return=1");
  await expect
    .poll(() => page.evaluate(() => __campus.getState().nearbyEntrance))
    .toBe(id);
  await page
    .getByRole("button", { name: /Enter Miller Theatre Complex/ })
    .click();
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe(id);
  const [e, , z] = await page.evaluate(() => __campus.getState().camera);
  expect(e).toBeCloseTo(player[0], 1);
  expect(z).toBeCloseTo(player[2], 1);
});

test("a failed Miller export restores the prior Heritage Core package", async ({
  page,
}) => {
  await ready(page, "/?exterior-review=miller-baseline");
  const previous = await page.evaluate(inspect, id);
  await page.route("**/heritage-miller-review/site.glb", (route) =>
    route.fulfill({ body: "invalid Miller model" }),
  );
  await ready(page);
  expect(await page.evaluate(inspect, id)).toEqual(previous);
});
