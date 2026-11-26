import { expect, test } from "@playwright/test";

const review = "/";
const court = "context-b0020";
const esslinger = "roof-a5ff3d5a";
const recreation = "roof-af9a4442";

async function ready(page, url = review) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

test("the three sports buildings use separated footprints, an open east arcade and aligned approaches", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await ready(page);
  const result = await page.evaluate(() => {
    const arcade = __campus.terrainCheck(-142, 336);
    return {
      gates: __campus.entranceInfo().filter(({ gate }) => gate),
      court: __campus.collisionCheck(-267, 425),
      stair: __campus.collisionCheck(-238.4, 455),
      besideStair: __campus.collisionCheck(-236.6, 455),
      treeCount: __campus.getState().presentation.trees,
      eastOfCourt: __campus.collisionCheck(-228, 424),
      esslinger: __campus.collisionCheck(-260, 365),
      betweenWings: __campus.collisionCheck(-210, 360),
      recreation: __campus.collisionCheck(-179, 363),
      arcade: __campus.collisionCheck(-142, 336),
      column: __campus.collisionCheck(-140.26, 325.1),
      pavingLift: arcade["athletic-paving"] - arcade.sampled,
    };
  });
  expect(result).toMatchObject({
    court: true,
    stair: true,
    besideStair: false,
    treeCount: 570,
    eastOfCourt: false,
    esslinger: true,
    betweenWings: false,
    recreation: true,
    arcade: false,
    column: true,
  });
  expect(result.pavingLift).toBeCloseTo(0.085, 3);
  expect(result.gates).toEqual(
    expect.arrayContaining([
      expect.objectContaining({
        id: court,
        gate: "mcarthur-west",
        walkable: true,
      }),
      expect.objectContaining({
        id: esslinger,
        gate: "esslinger-west",
        walkable: true,
      }),
      expect.objectContaining({
        id: recreation,
        gate: "recreation-east",
        walkable: true,
      }),
      expect.objectContaining({ id: "context-b0074", gate: "east" }),
    ]),
  );
  expect(errors).toEqual([]);
});

test("the SRC east entrance returns the player to the default scene", async ({
  page,
}) => {
  await ready(page);
  await page.evaluate(() => {
    const door = __campus
      .entranceInfo()
      .find(({ gate }) => gate === "recreation-east");
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
  await ready(page, `${review}?return=1`);
  await expect
    .poll(() => page.evaluate(() => __campus.getState().nearbyEntrance))
    .toBe(recreation);
  const box = await page.locator("#viewport").boundingBox();
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe(recreation);
  expect(new URL(page.url()).search).toBe("");
});

test("a corrupt sports block package keeps the prior footprints and entrances", async ({
  page,
}) => {
  const inspect = () =>
    page.evaluate(() => ({
      oldEsslinger: __campus.collisionCheck(-267, 425),
      treeCount: __campus.getState().presentation.trees,
      oldMcArthurProtrusion: __campus.collisionCheck(-232, 424),
      gates: __campus
        .entranceInfo()
        .filter(({ gate }) => gate)
        .map(({ gate }) => gate)
        .sort(),
    }));
  await ready(page, "/?exterior-review=athletic-baseline");
  const previous = await inspect();
  expect(previous).toMatchObject({
    oldEsslinger: true,
    oldMcArthurProtrusion: true,
  });
  expect(previous.gates).not.toContain("recreation-east");
  await page.route("**/athletic-exterior-review/site.glb", (route) =>
    route.fulfill({ body: "bad mesh" }),
  );
  await ready(page);
  expect(await inspect()).toEqual(previous);
});
