import { test, expect } from "@playwright/test";
test("west seam views are valid and reproducible", async ({ page }) => {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect(await page.evaluate(() => __campus.collisionCheck(-495, -185.5))).toBe(
    true,
  );
  for (const [name, x, z, yaw, pitch] of [
    ["north-approach", -465, -205, Math.PI, -0.18],
    ["south-approach", -465, -165, 0, -0.18],
    ["toward-villard", -465, -185, -Math.PI / 2, -0.15],
    ["toward-theatre", -465, -185, Math.PI / 2, -0.15],
  ]) {
    let v = await page.evaluate(
      ({ x, z }) => ({
        blocked: __campus.collisionCheck(x, z),
        ground: __campus.terrainCheck(x, z).sampled,
      }),
      { x, z },
    );
    expect(v.blocked).toBe(false);
    await page.evaluate(
      ({ x, z, yaw, pitch, ground }) =>
        sessionStorage.setItem(
          "explorer:outdoor-return:v1",
          JSON.stringify({
            version: 1,
            buildingId: "roof-399c648e",
            player: [x, ground, z],
            view: "first",
            yaw,
            pitch,
            followDistance: 7.5,
            density: 0,
            motionLevel: 0,
          }),
        ),
      { x, z, yaw, pitch, ground: v.ground },
    );
    await page.goto("/?return=1");
    await page.waitForFunction(
      () =>
        window.__campus?.getState().ready &&
        __campus.getState().life.density === "No",
    );
    await page.waitForTimeout(300);
    let camera = await page.evaluate(() => __campus.getState().camera);
    expect(camera[0]).toBeCloseTo(x, 1);
    expect(camera[2]).toBeCloseTo(z, 1);
    console.log(
      name,
      JSON.stringify({
        camera,
        draws: await page.evaluate(() => __campus.getState().drawCalls),
      }),
    );
  }
});
