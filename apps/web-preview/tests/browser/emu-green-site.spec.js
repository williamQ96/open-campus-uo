import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

const review = "/";
const baseline = "/?exterior-review=emu-baseline";
const emu = "roof-266f13fd";
const formerWing = "roof-39f81f68";

async function ready(page, url = review) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

test("the default EMU opens the green and gives five entrances clear approaches", async ({
  page,
}) => {
  await ready(page, baseline);
  expect(await page.evaluate(() => __campus.collisionCheck(-200, 78))).toBe(
    true,
  );
  await ready(page);
  const after = await page.evaluate(
    (ids) => ({
      opensGreen: !__campus.collisionCheck(-200, 78),
      ballroomBlocks: __campus.collisionCheck(-268, 117),
      ground: __campus.terrainCheck(-180, 90),
      gates: __campus.entranceInfo().filter((gate) => ids.includes(gate.id)),
      knightGates: __campus
        .entranceInfo()
        .filter(({ id }) => id === "roof-6684e091"),
      buildings: __campus.getState().buildings,
    }),
    [emu, formerWing],
  );
  expect(after.opensGreen).toBe(true);
  expect(after.ballroomBlocks).toBe(true);
  expect(after.ground.paving - after.ground.sampled).toBeCloseTo(0.12, 3);
  expect(after.buildings).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(after.knightGates.map(({ gate }) => gate)).toEqual([
    "memorial-west",
    "memorial-east",
  ]);
  expect(
    after.gates.map(({ gate, id, walkable }) => [gate, id, walkable]),
  ).toEqual([
    ["emu-hearth", emu, true],
    ["emu-east", emu, true],
    ["emu-west", emu, true],
    ["emu-fishbowl", emu, true],
    ["emu-historic", emu, true],
  ]);
});

test("the Hearth entry opens and returns to the default EMU", async ({
  page,
}) => {
  await ready(page);
  await page.evaluate(() => {
    const door = __campus
      .entranceInfo()
      .find(({ gate }) => gate === "emu-hearth");
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
    .toBe(emu);
  const box = await page.locator("#viewport").boundingBox();
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe(emu);
  expect(new URL(page.url()).searchParams.has("exterior-review")).toBe(false);
});

test("the campus west Fishbowl door opens and returns to the default EMU", async ({
  page,
}) => {
  await ready(page);
  await page.evaluate(() => {
    const door = __campus
      .entranceInfo()
      .find(({ gate }) => gate === "emu-fishbowl");
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
    .toBe(emu);
  await page.keyboard.press("KeyE");
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe(emu);
});

test("corrupt EMU bytes keep both old building records and the other entrance groups", async ({
  page,
}) => {
  const inspect = () =>
    page.evaluate(
      (id) => ({
        blocked: __campus.collisionCheck(-200, 78),
        priorWing: __campus.entranceInfo().some((entry) => entry.id === id),
        gates: __campus.entranceInfo(),
      }),
      formerWing,
    );
  await ready(page, baseline);
  const before = await inspect();
  expect(before.blocked).toBe(true);
  expect(before.priorWing).toBe(true);
  await page.route("**/emu-green-review/site.glb", (route) =>
    route.fulfill({ body: "corrupt" }),
  );
  await ready(page);
  expect(await inspect()).toEqual(before);
});

test("a saved return from the former EMU wing restores the outdoor location", async ({
  page,
}) => {
  await ready(page, baseline);
  await page.evaluate((buildingId) => {
    const ground = __campus.terrainCheck(-180, 90).sampled;
    sessionStorage.setItem(
      "explorer:outdoor-return:v1",
      JSON.stringify({
        version: 1,
        buildingId,
        player: [-180, ground, 90],
        view: "first",
        yaw: 0,
        pitch: 0,
        followDistance: 7.5,
        density: 0,
      }),
    );
  }, formerWing);
  await ready(page, "/?return=1");
  const { player, view } = await page.evaluate(() => __campus.getState());
  expect(view).toBe("first");
  expect(player[0]).toBeCloseTo(-180, 3);
  expect(player[2]).toBeCloseTo(90, 3);
});
