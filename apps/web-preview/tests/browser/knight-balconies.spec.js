import { test, expect } from "@playwright/test";
test("Knight solid balconies preserve entrance and collision contracts within one extra draw", async ({
  browser,
}) => {
  const results = [];
  for (const before of [true, false]) {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1000 },
      reducedMotion: "reduce",
    });
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    if (before)
      await page.route("**/scene/presentation.json", async (r) => {
        const response = await r.fetch();
        const json = await response.json();
        json.exterior_details = json.exterior_details.filter(
          (x) => x.url !== "knight-library-balcony-detail.json",
        );
        await r.fulfill({ response, json });
      });
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo());
    await page.evaluate(() =>
      sessionStorage.setItem(
        "explorer:outdoor-return:v1",
        JSON.stringify({
          version: 1,
          buildingId: "roof-6684e091",
          player: [-561.8, 5.066, 168],
          view: "first",
          yaw: Math.PI,
          pitch: -0.23,
          followDistance: 7.5,
          density: 0,
          motionLevel: 0,
        }),
      ),
    );
    await page.goto("/?return=1");
    await page.waitForFunction(
      () =>
        window.__campus?.getState().ready &&
        __campus.getState().life.density === "No",
    );
    await page.waitForTimeout(800);
    results.push({
      entries,
      errors,
      ...(await page.evaluate(() => ({
        draws: __campus.getState().drawCalls,
        blocked: __campus.collisionCheck(-561.8, 168),
      }))),
    });
    await page.screenshot({
      path: `../../docs/images/knight-balconies-${before ? "before" : "after"}-2026-11-10.png`,
    });
    await page.close();
  }
  expect(results[1].entries).toEqual(results[0].entries);
  expect(results[1].blocked).toEqual(results[0].blocked);
  expect(results[1].draws).toBeLessThanOrEqual(results[0].draws + 1);
  expect(results.flatMap((x) => x.errors)).toEqual([]);
  console.log(
    JSON.stringify(
      results.map(({ draws, blocked, errors }) => ({ draws, blocked, errors })),
    ),
  );
});
