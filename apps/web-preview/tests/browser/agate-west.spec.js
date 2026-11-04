import { test, expect } from "@playwright/test";
test("Agate frontage preserves entrance image, all entries, picking and modeled approach", async ({
  browser,
}) => {
  const results = [];
  for (const before of [true, false]) {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1000 },
      reducedMotion: "reduce",
    });
    if (before)
      await page.route("**/scene/presentation.json", async (r) => {
        const response = await r.fetch(),
          j = await response.json();
        j.exterior_details = j.exterior_details.filter(
          (e) => e.url !== "agate-west-provisional-detail.json",
        );
        await r.fulfill({ response, json: j });
      });
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo());
    const g = await page.evaluate(() => __campus.terrainCheck(72, 586).sampled);
    await page.evaluate(
      (g) =>
        sessionStorage.setItem(
          "explorer:outdoor-return:v1",
          JSON.stringify({
            version: 1,
            buildingId: "roof-b068940e",
            player: [72, g, 586],
            view: "first",
            yaw: -Math.PI / 2,
            pitch: -0.03,
            followDistance: 7.5,
            density: 0,
            motionLevel: 0,
          }),
        ),
      g,
    );
    await page.goto("/?return=1");
    await page.waitForFunction(
      () =>
        window.__campus?.getState().ready &&
        __campus.getState().life.density === "No",
    );
    await page.waitForTimeout(700);
    const frame = await page.screenshot({
      clip: { x: 709, y: 492, width: 54, height: 87 },
    });
    const status = await page.evaluate(() => ({
      entry: __campus.entranceInfo().find((e) => e.id === "roof-b068940e"),
      approachBlocked: __campus.collisionCheck(106.5, 586.5),
      openPathBlocked: __campus.collisionCheck(104, 586.5),
    }));
    await page.mouse.click(350, 360);
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("roof-b068940e");
    await page.mouse.click(736, 530);
    await page.waitForURL(/interior=roof-b068940e/);
    expect(errors).toEqual([]);
    results.push({ entries, frame, status });
    await page.close();
  }
  expect(results[1].entries).toEqual(results[0].entries);
  expect(results[1].status).toEqual(results[0].status);
  expect(results[1].status.entry.walkable).toBe(true);
  expect(results[1].status.approachBlocked).toBe(false);
  expect(results[1].status.openPathBlocked).toBe(false);
  expect(results[1].frame.equals(results[0].frame)).toBe(true);
});
