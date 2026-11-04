import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const b = readFileSync(
    new URL(
      "../../../../assets/exterior-refinement/tykeson-before-upper-frontage-2026-11-04.json",
      import.meta.url,
    ),
  ),
  hash = "01bd8c5c4c57eba839f13f0a060052726bfbed5880095f09e43f0f8fd0bb91e1";
test("Tykeson frontage preserves selection, entrances, collision and draw calls", async ({
  browser,
}) => {
  test.setTimeout(90000);
  const results = [];
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
  });
  for (const after of [false, true]) {
    const page = await context.newPage(),
      errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    if (!after) {
      await page.route("**/scene/tykeson-north-detail.json", (r) =>
        r.fulfill({ body: b, contentType: "application/json" }),
      );
      await page.route("**/scene/presentation.json", async (r) => {
        const res = await r.fetch(),
          j = await res.json();
        j.exterior_details.find(
          (x) => x.url === "tykeson-north-detail.json",
        ).sha256 = hash;
        await r.fulfill({ response: res, json: j });
      });
    }
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo()),
      views = [];
    for (const [name, x, z, yaw] of [
      ["front", -447, 9, Math.PI],
      ["east", -420, 12, 2.16],
      ["west", -475, 12, -2.14],
    ]) {
      const ground = await page.evaluate(
          ({ x, z }) => __campus.terrainCheck(x, z).sampled,
          { x, z },
        ),
        blocked = await page.evaluate(
          ({ x, z }) => __campus.collisionCheck(x, z),
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
              pitch: -0.3,
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
      await page.waitForTimeout(500);
      const state = await page.evaluate(() => ({
        camera: __campus.getState().camera,
        draws: __campus.getState().drawCalls,
      }));
      expect(state.camera[0]).toBeCloseTo(x, 1);
      expect(state.camera[2]).toBeCloseTo(z, 1);
      await page.screenshot({
        path: `../../docs/images/tykeson-frontage-${name}-${after ? "after" : "before"}-2026-11-04.png`,
      });
      views.push({ blocked, ...state });
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
    await page.evaluate(() => localStorage.clear());
    await context.clearCookies();
    await page.close();
  }
  await context.close();
  expect(results[0].entries).toEqual(results[1].entries);
  expect(results[0].views).toEqual(results[1].views);
  expect(results.flatMap((x) => x.errors)).toEqual([]);
});
