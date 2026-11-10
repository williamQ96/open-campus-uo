import { test, expect } from "@playwright/test";
test("Knight reveals front and oblique preserve balcony, entrances and collision", async ({
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
          (x) => x.url !== "knight-library-window-reveals.json",
        );
        await r.fulfill({ response, json });
      });
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo());
    const views = [];
    for (let [label, x, z, yaw] of [
      ["front", -561.8, 158, Math.PI],
      ["oblique", -540, 158, 2.58],
    ]) {
      if (label === "oblique") {
        const safe = await page.evaluate(() =>
          [
            [-540, 158],
            [-535, 158],
            [-530, 155],
            [-545, 150],
            [-540, 140],
          ].find(([x, z]) => !__campus.collisionCheck(x, z)),
        );
        expect(
          safe,
          "an unobstructed north-side oblique viewpoint",
        ).toBeTruthy();
        [x, z] = safe;
        yaw = Math.atan2(x + 561.8, z - 192.58);
      }
      await page.evaluate(
        ({ x, z, yaw }) =>
          sessionStorage.setItem(
            "explorer:outdoor-return:v1",
            JSON.stringify({
              version: 1,
              buildingId: "roof-6684e091",
              player: [x, 5.066, z],
              view: "first",
              yaw,
              pitch: -0.22,
              followDistance: 7.5,
              density: 0,
              motionLevel: 0,
            }),
          ),
        { x, z, yaw },
      );
      await page.goto("/?return=1");
      await page.waitForFunction(
        () =>
          window.__campus?.getState().ready &&
          __campus.getState().life.density === "No",
      );
      await page.waitForTimeout(700);
      const actual = await page.evaluate(() => __campus.getState());
      expect(actual.player[0]).toBeCloseTo(x, 1);
      expect(actual.player[2]).toBeCloseTo(z, 1);
      expect(actual.view).toBe("first");
      expect(actual.cameraDirection[2]).toBeGreaterThan(0.7);
      views.push(
        await page.evaluate(
          ({ x, z }) => ({
            draws: __campus.getState().drawCalls,
            blocked: __campus.collisionCheck(x, z),
          }),
          { x, z },
        ),
      );
      await page.screenshot({
        path: `../../docs/images/knight-reveals-${label}-${before ? "before" : "after"}-2026-11-10.png`,
      });
    }
    await page
      .getByRole("combobox", { name: "Search buildings" })
      .fill("Knight Library");
    await page
      .getByRole("option", { name: /Knight Library/ })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("roof-6684e091");
    results.push({ entries, views, errors });
    await page.close();
  }
  expect(results[1].entries).toEqual(results[0].entries);
  expect(results.flatMap((r) => r.errors)).toEqual([]);
  for (let i = 0; i < 2; i++) {
    expect(results[1].views[i].blocked).toEqual(results[0].views[i].blocked);
    expect(results[1].views[i].draws).toBeLessThanOrEqual(
      results[0].views[i].draws + 1,
    );
  }
  console.log(JSON.stringify(results.map((r) => r.views)));
});
