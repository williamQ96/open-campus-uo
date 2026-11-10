import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const prior = readFileSync(
  new URL(
    "../../../../assets/exterior-refinement/chapman-before-west-frieze-2026-11-10.json",
    import.meta.url,
  ),
);
test("Chapman west shallow arch relief preserve geometry and draw budget", async ({
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
    if (before) {
      await page.route("**/scene/chapman-west-detail.json", (r) =>
        r.fulfill({ body: prior, contentType: "application/json" }),
      );
      await page.route("**/scene/presentation.json", async (r) => {
        const response = await r.fetch();
        const json = await response.json();
        json.exterior_details.find(
          (x) => x.url === "chapman-west-detail.json",
        ).sha256 =
          "c517238075ef611d80920f99a0036e7e711c65d69fe9b6b74408cc937ff27009";
        await r.fulfill({ response, json });
      });
    }
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo());
    const views = [];
    for (let [label, x, z, yaw] of [
      ["front", -540, 26, -Math.PI / 2],
      ["oblique", -532, 33, -0.95],
      ["close", -532, 26, -Math.PI / 2],
    ]) {
      const ground = await page.evaluate(
        ({ x, z }) => __campus.terrainCheck(x, z).sampled,
        { x, z },
      );
      await page.evaluate(
        ({ x, z, yaw, ground }) =>
          sessionStorage.setItem(
            "explorer:outdoor-return:v1",
            JSON.stringify({
              version: 1,
              buildingId: "roof-f5cea51d",
              player: [x, ground, z],
              view: "first",
              yaw,
              pitch: x === -532 ? -0.95 : -0.45,
              followDistance: 7.5,
              density: 0,
              motionLevel: 0,
            }),
          ),
        { x, z, yaw, ground },
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
      expect(actual.cameraDirection[0]).toBeGreaterThan(0.5);
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
        path: `../../docs/images/chapman-west-frieze-${label}-${before ? "before" : "after"}-2026-11-10.png`,
      });
    }
    await page
      .getByRole("combobox", { name: "Search buildings" })
      .fill("Chapman Hall");
    await page
      .getByRole("option", { name: /Chapman Hall/ })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("roof-f5cea51d");
    results.push({ entries, views, errors });
    await page.close();
  }
  expect(results[1].entries).toEqual(results[0].entries);
  expect(results.flatMap((r) => r.errors)).toEqual([]);
  for (let i = 0; i < 3; i++) {
    expect(results[1].views[i].blocked).toEqual(results[0].views[i].blocked);
    expect(results[1].views[i].draws).toBeLessThanOrEqual(
      results[0].views[i].draws,
    );
  }
  console.log(JSON.stringify(results.map((r) => r.views)));
});
