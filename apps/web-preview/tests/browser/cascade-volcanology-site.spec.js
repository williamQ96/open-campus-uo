import { expect, test } from "@playwright/test";

const review = "/";
const cascade = "roof-f42d2ea3";
const volcanology = "roof-399a0551";

async function ready(page, url) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

test("the local site opens the courtyard while retaining bridge supports and both buildings", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await ready(page, review);
  const data = await page.evaluate(() => {
    const path = [
      [-249.8, 69.25],
      [-244.7, 69.8],
      [-242.52, 71.37],
      [-240.99, 72.68],
      [-239.55, 73.32],
      [-238.11, 73.62],
      [-237.76, 74.45],
      [-237.76, 76.62],
      [-238.47, 76.71],
    ];
    const blocked = (east, north) => __campus.collisionCheck(east, -north);
    return {
      route: path.slice(1).some(([e, n], index) => {
        const [a, b] = path[index];
        const samples = Math.ceil(Math.hypot(e - a, n - b) / 0.14);
        return Array.from({ length: samples + 1 }, (_, j) => j / samples).some(
          (t) => blocked(a + (e - a) * t, b + (n - b) * t),
        );
      }),
      collision: [
        blocked(-235.2, 63.4),
        blocked(-239.2, 70.7),
        blocked(-239.4, 42),
        blocked(-228.2, 99.4),
      ],
      ground: __campus.terrainCheck(-248.4, -69),
      streetPaving: __campus.terrainCheck(-228, -13.5),
      carriedBridge: __campus.terrainCheck(-235.2, -63.4),
      entries: __campus.entranceInfo().filter(({ gate }) => gate),
    };
  });
  expect(data.route).toBe(false);
  expect(data.collision).toEqual([false, true, true, true]);
  expect(data.ground.mesh).toBeCloseTo(data.ground.sampled, 3);
  expect(data.ground.courtyard - data.ground.sampled).toBeCloseTo(0.045, 3);
  expect(data.streetPaving.courtyard - data.streetPaving.sampled).toBeCloseTo(
    0.045,
    3,
  );
  expect(data.carriedBridge.bridge).toBeCloseTo(6.86, 2);
  expect(
    data.carriedBridge.bridge - data.carriedBridge.sampled,
  ).toBeGreaterThan(3.8);
  expect(data.entries.find(({ id }) => id === cascade)).toMatchObject({
    gate: "cascade-courtyard",
    walkable: true,
  });
  expect(data.entries.find(({ id }) => id === volcanology)).toMatchObject({
    gate: "volcanology-south",
    walkable: true,
  });
  expect(data.entries.find(({ gate }) => gate === "east")).toBeDefined();
  expect(errors).toEqual([]);
});

test("the modeled south door visits and returns to the default scene", async ({
  page,
}) => {
  await ready(page, review);
  await page.evaluate(() => {
    const door = __campus
      .entranceInfo()
      .find(({ gate }) => gate === "cascade-courtyard");
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
    .toBe(cascade);
  const box = await page.locator("#viewport").boundingBox();
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe(cascade);
  expect(new URL(page.url()).search).toBe("");
});

test("a failed Cascade asset keeps its old collision and the adopted Ford/Arena package", async ({
  page,
}) => {
  const readGates = () =>
    page.evaluate(
      ([cascadeId, volcanologyId]) => {
        const entrances = __campus.entranceInfo();
        return {
          priorBuilding: __campus.collisionCheck(-235.2, -63.4),
          cascadeGates: entrances
            .filter(
              ({ id, gate }) => gate && [cascadeId, volcanologyId].includes(id),
            )
            .map(({ gate }) => gate)
            .sort(),
          otherGates: entrances
            .filter(
              ({ id, gate }) =>
                gate && ![cascadeId, volcanologyId].includes(id),
            )
            .map(({ id, gate }) => [id, gate])
            .sort(),
        };
      },
      [cascade, volcanology],
    );
  await ready(page, review);
  const baseline = await readGates();
  expect(baseline.cascadeGates).toEqual([
    "cascade-courtyard",
    "volcanology-south",
  ]);
  expect(baseline.otherGates).toEqual(
    expect.arrayContaining([
      ["context-b0066", "plaza"],
      ["context-b0074", "east"],
      ["context-b0074", "north"],
      ["context-b0074", "west"],
    ]),
  );
  await page.route("**/cascade-volcanology-review/site.glb", (route) =>
    route.fulfill({ body: "corrupted-site" }),
  );
  await ready(page, review);
  expect(await readGates()).toEqual({
    priorBuilding: true,
    cascadeGates: [],
    otherGates: baseline.otherGates,
  });
});
