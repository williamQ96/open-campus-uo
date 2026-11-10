import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const prior = readFileSync(
  new URL(
    "../../../../assets/exterior-refinement/tykeson-before-canopy-cladding-2026-11-10.json",
    import.meta.url,
  ),
);
test("Tykeson canopy and cladding retain openings and draw budget", async ({
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
      await page.route("**/scene/tykeson-north-detail.json", (r) =>
        r.fulfill({ body: prior, contentType: "application/json" }),
      );
      await page.route("**/scene/presentation.json", async (r) => {
        const response = await r.fetch();
        const json = await response.json();
        json.exterior_details.find(
          (x) => x.url === "tykeson-north-detail.json",
        ).sha256 =
          "83dc8689edf6656926631570d704c75b98612834a6ab4ed81897ebfcf30c395a";
        await r.fulfill({ response, json });
      });
    }
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo());
    const views = [];
    for (let [label, x, z, yaw] of [
      ["front", -447, 9, Math.PI],
      ["oblique", -420, 12, 2.16],
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
              buildingId: "context-b0103",
              player: [x, ground, z],
              view: "first",
              yaw,
              pitch: -0.22,
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
      expect(actual.cameraDirection[2]).toBeGreaterThan(0.4);
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
        path: `../../docs/images/tykeson-canopy-cladding-${label}-${before ? "before" : "after"}-2026-11-10.png`,
      });
    }
    await page
      .getByRole("combobox", { name: "Search buildings" })
      .fill("Tykeson Hall");
    await page
      .getByRole("option", { name: /Tykeson Hall/ })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("context-b0103");
    results.push({ entries, views, errors });
    await page.close();
  }
  expect(results[1].entries).toEqual(results[0].entries);
  expect(results.flatMap((r) => r.errors)).toEqual([]);
  for (let i = 0; i < 2; i++) {
    expect(results[1].views[i].blocked).toEqual(results[0].views[i].blocked);
    expect(results[1].views[i].draws).toBeLessThanOrEqual(
      results[0].views[i].draws,
    );
  }
  console.log(JSON.stringify(results.map((r) => r.views)));
});
