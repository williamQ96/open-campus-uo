import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

const id = "roof-4f0c798e";

async function ready(page, path = "/") {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function inspect(id) {
  const gates = __campus.entranceInfo();
  return {
    buildings: __campus.getState().buildings,
    doors: gates.filter((door) => door.id === id),
    neighbors: gates.filter((door) => door.id !== id),
    blocked: [
      [-432, -30.78],
      [-430.15, -30.78],
      [-442.78, -14.15],
      [-442.78, -11.98],
      [-451.0, -14.5],
      [-472.5, -30],
    ].map(([x, z]) => __campus.collisionCheck(x, z)),
  };
}

test("Fenton replaces the exterior with two clear approaches and stable neighboring gates", async ({
  page,
}) => {
  await ready(page, "/?exterior-review=fenton-baseline");
  const before = await page.evaluate(inspect, id);
  await ready(page);
  const after = await page.evaluate(inspect, id);
  expect(after.buildings).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.blocked).toEqual([true, false, true, false, true, true]);
  expect(after.doors.map(({ gate }) => gate).sort()).toEqual([
    "fenton-east",
    "fenton-south",
  ]);
  for (const door of after.doors) {
    expect(door.walkable).toBe(true);
    expect(door.thresholdZ - door.ground).toBeGreaterThan(
      door.gate === "fenton-east" ? 0.65 : 0.8,
    );
  }
});

for (const gate of ["fenton-east", "fenton-south"]) {
  test(`Fenton returns to the ${gate} approach after visiting the interior`, async ({
    page,
  }) => {
    await ready(page);
    const approach = await page.evaluate((gate) => {
      const door = __campus.entranceInfo().find((entry) => entry.gate === gate);
      const point = [door.approach[0], door.ground, door.approach[1]];
      sessionStorage.setItem(
        "explorer:outdoor-return:v1",
        JSON.stringify({
          version: 1,
          buildingId: door.id,
          player: point,
          view: "first",
          yaw: Math.atan2(door.outward[0], door.outward[1]),
          pitch: 0,
          followDistance: 7.5,
          density: 0,
        }),
      );
      return point;
    }, gate);
    await ready(page, "/?return=1");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().nearbyEntrance))
      .toBe(id);
    await page.getByRole("button", { name: /Enter Fenton Hall/ }).click();
    await page.waitForFunction(() => window.__interior?.getState().ready);
    await page.getByRole("button", { name: /Return to campus/ }).click();
    await expect
      .poll(() =>
        page.evaluate(() => window.__campus?.getState().nearbyEntrance),
      )
      .toBe(id);
    const [x, , z] = await page.evaluate(() => __campus.getState().camera);
    expect(x).toBeCloseTo(approach[0], 1);
    expect(z).toBeCloseTo(approach[2], 1);
  });
}

test("a damaged Fenton package restores the prior building and entrances", async ({
  page,
}) => {
  await ready(page, "/?exterior-review=fenton-baseline");
  const before = await page.evaluate(inspect, id);
  await page.route("**/fenton-site-review/site.glb", (route) =>
    route.fulfill({ body: "invalid Fenton site mesh" }),
  );
  await ready(page);
  expect(await page.evaluate(inspect, id)).toEqual(before);
});
