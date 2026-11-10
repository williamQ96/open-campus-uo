import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const b = readFileSync(
    new URL(
      "../../../../assets/exterior-refinement/gerlinger-before-portico-2026-11-04.json",
      import.meta.url,
    ),
  ),
  hash = "86b2ef379efde7ae1d1c0f930a92ce8fc550b8fcdfa2014ff603b59360f78255";
test("Gerlinger portico preserves campus selection, entrances and collision", async ({
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
      await page.route("**/scene/gerlinger-east-detail.json", (r) =>
        r.fulfill({ body: b, contentType: "application/json" }),
      );
      await page.route("**/scene/presentation.json", async (r) => {
        const res = await r.fetch(),
          j = await res.json();
        j.exterior_details.find(
          (x) => x.url === "gerlinger-east-detail.json",
        ).sha256 = hash;
        await r.fulfill({ response: res, json: j });
      });
    }
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo()),
      views = [];
    for (const [name, x, z, yaw] of [
      ["front", -338, 210, Math.PI / 2],
      ["oblique", -342, 195, 2.3],
      ["south", -370, 240, 0],
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
              buildingId: "roof-9ac93ab7",
              player: [x, ground, z],
              view: "first",
              yaw,
              pitch: -0.25,
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
      let state = await page.evaluate(() => ({
        camera: __campus.getState().camera,
        draws: __campus.getState().drawCalls,
      }));
      expect(state.camera[0]).toBeCloseTo(x, 1);
      expect(state.camera[2]).toBeCloseTo(z, 1);
      await page.screenshot({
        path: `../../docs/images/gerlinger-portico-${name}-${after ? "after" : "before"}-2026-11-04.png`,
      });
      views.push({ blocked, ...state });
    }
    await page
      .getByRole("combobox", { name: "Search buildings" })
      .fill("Gerlinger Hall");
    await page
      .getByRole("option", { name: /Gerlinger Hall/ })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("roof-9ac93ab7");
    results.push({ entries, views, errors });
    await page.evaluate(() => localStorage.clear());
    await context.clearCookies();
    await page.close();
  }
  await context.close();
  expect(results[0].entries).toEqual(results[1].entries);
  // Current pinned layers may batch while historical source variants remain separate.
  // All non-render-cost observations stay exact; draw calls must never increase.
  expect(results[1].views).toHaveLength(results[0].views.length);
  for (let i = 0; i < results[0].views.length; i++) {
    const { draws: beforeDraws, ...beforeState } = results[0].views[i];
    const { draws: afterDraws, ...afterState } = results[1].views[i];
    expect(afterState).toEqual(beforeState);
    expect(afterDraws).toBeLessThanOrEqual(beforeDraws);
  }
  expect(results.flatMap((x) => x.errors)).toEqual([]);
});
