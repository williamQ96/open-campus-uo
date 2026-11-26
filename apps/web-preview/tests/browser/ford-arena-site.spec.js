import { test, expect } from "@playwright/test";

test("Ford/Arena review swaps both footprints and keeps scene ground and approaches aligned", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const state = () => page.evaluate(() => __campus.getState());
  const checks = await page.evaluate(() => {
    const points = [
      [245.2, 42.1], // New Ford shell outside the historical box.
      [276.5, 60.8], // Passage between the two candidate outlines.
      [299.7, 76.25], // New Arena shell outside the historical box.
      [430.5, 114.5], // Open outside the Arena candidate.
      [301.2, 40.0], // New northern vestibule lies in front of the roof-derived shell.
      [297.1, 24.0], // Open plaza in front of the vestibule.
      [426.89, 45.21], // East gate extension.
      [437.0, 45.0], // Villard Street approach.
      [286.54, 94.82], // West gate extension.
      [278.0, 97.0], // Open west plaza.
    ];
    const cityGround = [
      ...points,
      [234.7, 15.5],
      [458.4, 110.6],
      [189.6, 56.3],
      [193.4, 56.3],
      [494.4, 90.6],
      [-305, 0],
    ].map(([x, z]) => __campus.terrainCheck(x, z));
    return {
      collision: points.map(([x, z]) => __campus.collisionCheck(x, z)),
      plazaEdges: [
        [296.875, 32.985], // North stair handrail.
        [298.644, 32.281], // Lane alongside that rail.
        [443.986, 36.724], // East stair handrail.
        [264.8, 90.295], // Ford's terrace planter wall.
      ].map(([x, z]) => __campus.collisionCheck(x, z)),
      stairRail: __campus.terrainCheck(296.875, 32.985),
      ground: cityGround,
      plaza: [
        [301.5, 34.0],
        [302.6, 30.2],
        [298.8, 21.0],
        [263.1, 24.65],
        [245.0, 91.0], // Ford garden.
        [264.0, 87.0], // Ford south terrace.
        [432.0, 43.2],
        [281.0, 97.0],
      ].map(([x, z]) => __campus.terrainCheck(x, z)),
      entrances: __campus
        .entranceInfo()
        .filter(({ id }) => ["context-b0066", "context-b0074"].includes(id))
        .map((entry) => ({
          ...entry,
          approachBlocked: __campus.collisionCheck(...entry.approach),
        })),
    };
  });
  expect(checks.collision).toEqual([
    true,
    false,
    true,
    false,
    true,
    false,
    true,
    false,
    true,
    false,
  ]);
  expect(checks.plazaEdges).toEqual([true, false, true, true]);
  expect(checks.stairRail.frontage - checks.stairRail.sampled).toBeGreaterThan(
    0.9,
  );
  expect(checks.stairRail.frontage - checks.stairRail.sampled).toBeLessThan(
    1.3,
  );
  for (const { mesh, sampled, foundation } of checks.ground) {
    expect(Math.abs(mesh - sampled)).toBeLessThan(0.001);
    expect(Math.abs(foundation - sampled - 0.018)).toBeLessThan(0.001);
  }
  for (const { sampled, frontage } of checks.plaza) {
    expect(frontage - sampled).toBeGreaterThan(0.07);
    expect(frontage - sampled).toBeLessThan(0.4);
  }
  expect(checks.entrances).toHaveLength(4);
  for (const entry of checks.entrances)
    expect(entry).toMatchObject({
      estimated: true,
      walkable: true,
      approachBlocked: false,
    });
  const positions = Object.fromEntries(
    checks.entrances.map(({ gate, position }) => [gate, position]),
  );
  for (const [gate, x, z] of [
    ["plaza", 261.9, 25.1],
    ["north", 301.5, 35.9],
    ["east", 429.0, 44.4],
    ["west", 284.4, 95.6],
  ]) {
    expect(positions[gate][0]).toBeCloseTo(x, 0);
    expect(positions[gate][1]).toBeCloseTo(z, 0);
  }
  expect((await state()).buildings).toBe(519);

  await page.locator("#directions-open").click();
  for (const [endpoint, name, id] of [
    ["A", "Ford Alumni Center", "context-b0066"],
    ["B", "Matthew Knight Arena", "context-b0074"],
  ]) {
    await page
      .getByRole("button", { name: `Search ${endpoint}`, exact: true })
      .click();
    await page.getByRole("combobox").fill(name);
    await page
      .getByRole("option", { name: new RegExp(name) })
      .first()
      .click();
    await expect.poll(async () => (await state()).selectedBuilding).toBe(id);
  }
  await page.locator("#route-start").click();
  expect((await state()).navigation.points.length).toBeGreaterThan(0);
  expect(errors).toEqual([]);
});

test("the modeled east door accepts a click and returns to the same site", async ({
  page,
}) => {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  await page.evaluate(() => {
    const door = __campus.entranceInfo().find(({ gate }) => gate === "east");
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
  await page.goto("/?return=1");
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe("context-b0074");
  const box = await page.locator("#viewport").boundingBox();
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe("context-b0074");
  expect(new URL(page.url()).search).toBe("");
});

test("a late site asset failure restores the prior land, buildings, and doors together", async ({
  page,
}) => {
  await page.route(
    "**/scene/landcover.glb",
    (route) => route.fulfill({ status: 200, body: "stale-geometry" }),
    { times: 1 },
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const prior = await page.evaluate(() => ({
    gates: __campus
      .entranceInfo()
      .filter(({ id }) => ["context-b0066", "context-b0074"].includes(id))
      .map(({ gate }) => gate ?? null),
    blocked: __campus.collisionCheck(245.2, 42.1),
    land: __campus.terrainCheck(301.5, 34.0),
    greenOpen: !__campus.collisionCheck(-200, 78),
    knightGates: __campus
      .entranceInfo()
      .filter(({ id }) => id === "roof-6684e091")
      .map(({ gate }) => gate),
  }));
  expect(prior.gates).toEqual([null, null]);
  expect(prior.blocked).toBe(false);
  expect(prior.land.mesh).toBeCloseTo(prior.land.sampled, 3);
  expect(prior.land.frontage).toBeUndefined();
  expect(prior.greenOpen).toBe(true);
  expect(prior.knightGates).toEqual(["memorial-west", "memorial-east"]);
});
