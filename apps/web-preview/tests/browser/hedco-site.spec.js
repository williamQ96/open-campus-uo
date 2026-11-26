import { expect, test } from "@playwright/test";

const review = "/";
const id = "context-b0010";

async function ready(page, url) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

test("HEDCO review opens the courtyard and aligns the new wings and supports with collision", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await ready(page, review);
  const result = await page.evaluate(() => ({
    collision: [
      __campus.collisionCheck(-669, 431),
      __campus.collisionCheck(-655, 473),
      __campus.collisionCheck(-673.82, 416.9),
      __campus.collisionCheck(-673.82, 418.1),
      __campus.collisionCheck(-684.05, 444.2),
      __campus.collisionCheck(-682.1, 444.2),
    ],
    terrain: __campus.terrainCheck(-669, 431),
    westPaving: __campus.terrainCheck(-682.1, 444.2),
    gates: __campus.entranceInfo().filter(({ gate }) => !!gate),
  }));
  expect(result.collision).toEqual([false, true, true, false, true, false]);
  expect(result.terrain.mesh).toBeCloseTo(result.terrain.sampled, 3);
  expect(result.terrain["hedco-paving"] - result.terrain.sampled).toBeCloseTo(
    0.085,
    3,
  );
  expect(
    result.gates
      .filter((gate) => gate.id === id)
      .map((gate) => [gate.gate, gate.walkable]),
  ).toEqual([
    ["hedco-main", true],
    ["hedco-clinic", true],
  ]);
  expect(
    result.westPaving["hedco-paving"] - result.westPaving.sampled,
  ).toBeCloseTo(0.085, 3);
  expect(result.gates.find(({ gate }) => gate === "east")).toBeDefined();
  expect(errors).toEqual([]);
});

test("the modeled HEDCO entry accepts a click and returns to the same scene", async ({
  page,
}) => {
  await ready(page, review);
  await page.evaluate(() => {
    const door = __campus
      .entranceInfo()
      .find(({ gate }) => gate === "hedco-main");
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
    .toBe(id);
  const box = await page.locator("#viewport").boundingBox();
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe(id);
  expect(new URL(page.url()).search).toBe("");
});

test("a corrupt review mesh keeps the old HEDCO collision and the Ford/Arena entries", async ({
  page,
}) => {
  await page.route("**/hedco-exterior-review/site.glb", (route) =>
    route.fulfill({ body: "bad-mesh" }),
  );
  await ready(page, review);
  const result = await page.evaluate(() => ({
    old: __campus.collisionCheck(-669, 431),
    gates: __campus
      .entranceInfo()
      .filter(({ gate }) => gate)
      .map(({ gate }) => gate)
      .sort(),
  }));
  expect(result.old).toBe(true);
  expect(result.gates).toEqual([
    "beall-west",
    "cascade-courtyard",
    "chapman-north",
    "chapman-west",
    "condon-east",
    "east",
    "emu-east",
    "emu-fishbowl",
    "emu-hearth",
    "emu-historic",
    "emu-west",
    "esslinger-west",
    "gerlinger-annex-north",
    "gerlinger-hall-east",
    "gerlinger-hall-north",
    "hendricks-quad-west",
    "hendricks-university-east",
    "mcarthur-west",
    "memorial-east",
    "memorial-west",
    "museum-west",
    "music-south",
    "north",
    "plaza",
    "recreation-east",
    "susan-quad-east",
    "susan-west-porch",
    "volcanology-south",
    "west",
  ]);
});
