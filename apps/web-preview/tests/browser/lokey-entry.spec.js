import { test, expect } from "@playwright/test";
test("Lokey entrance and building selection remain usable", async ({
  browser,
}) => {
  const states = [];
  for (const before of [true, false]) {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1000 },
      reducedMotion: "reduce",
    });
    if (before)
      await page.route("**/scene/presentation.json", async (r) => {
        const response = await r.fetch(),
          j = await response.json();
        j.wall_color_patches = j.wall_color_patches.filter(
          (x) => x.url !== "lokey-wall-color.json",
        );
        await r.fulfill({ response, json: j });
      });
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo()),
      ground = await page.evaluate(
        () => __campus.terrainCheck(-628, 292).sampled,
      );
    await page.evaluate(
      (g) =>
        sessionStorage.setItem(
          "explorer:outdoor-return:v1",
          JSON.stringify({
            version: 1,
            buildingId: "roof-74ecc113",
            player: [-628, g, 292],
            view: "first",
            yaw: Math.PI,
            pitch: -0.03,
            followDistance: 7.5,
            density: 0,
            motionLevel: 0,
          }),
        ),
      ground,
    );
    await page.goto("/?return=1");
    await page.waitForFunction(
      () =>
        window.__campus?.getState().ready &&
        __campus.getState().life.density === "No",
    );
    await page.waitForTimeout(700);
    const status = await page.evaluate(() => ({
      entry: __campus.entranceInfo().find((e) => e.id === "roof-74ecc113"),
      blocked: __campus.collisionCheck(-626.5, 310.5),
    }));
    await page.mouse.click(350, 400);
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("roof-74ecc113");
    await page.mouse.click(630, 530);
    await page.waitForURL(/interior=roof-74ecc113/);
    states.push({ entries, status });
    await page.close();
  }
  expect(states[1]).toEqual(states[0]);
  expect(states[1].status.blocked).toBe(false);
  expect(states[1].status.entry.walkable).toBe(true);
});
