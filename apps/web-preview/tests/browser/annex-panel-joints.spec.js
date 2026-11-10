import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const prior = readFileSync(
  new URL(
    "../../../../assets/exterior-refinement/annex-before-panel-joints-2026-11-10.json",
    import.meta.url,
  ),
);
test("Annex shallow panel joints preserve geometry and draw budget", async ({
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
      await page.route("**/scene/gerlinger-annex-correction.json", (r) =>
        r.fulfill({ body: prior, contentType: "application/json" }),
      );
      await page.route("**/scene/presentation.json", async (r) => {
        const response = await r.fetch();
        const json = await response.json();
        json.exterior_details.find(
          (x) => x.url === "gerlinger-annex-correction.json",
        ).sha256 =
          "debbf767b3995a149757264323bd8ce8e7d6e50097c48d53007d0aa54215954c";
        await r.fulfill({ response, json });
      });
    }
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo());
    const views = [];
    for (let [label, x, z, yaw] of [
      ["front", -466, 220, Math.PI],
      ["oblique", -480, 220, 3.6],
      ["close", -466, 230, Math.PI],
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
              buildingId: "roof-f0b575d6",
              player: [x, ground, z],
              view: "first",
              yaw,
              pitch: -0.32,
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
      expect(actual.cameraDirection[2]).toBeGreaterThan(0.5);
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
        path: `../../docs/images/annex-panel-joints-${label}-${before ? "before" : "after"}-2026-11-10.png`,
      });
    }
    await page
      .getByRole("combobox", { name: "Search buildings" })
      .fill("Gerlinger Annex");
    await page
      .getByRole("option", { name: /Gerlinger Annex/ })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("roof-f0b575d6");
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
