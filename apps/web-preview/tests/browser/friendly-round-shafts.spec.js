import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const b = readFileSync(
    new URL(
      "../../../../assets/exterior-refinement/friendly-before-round-shafts-2026-11-10.json",
      import.meta.url,
    ),
  ),
  hash = "d8b439add6401343e891aa641fd4d12ae4aebe9a53bbc9cc99667f1bdcebdaba";
test("Friendly round shafts preserve campus selection, entrances and collision", async ({
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
      await page.route("**/scene/friendly-west-detail.json", (r) =>
        r.fulfill({ body: b, contentType: "application/json" }),
      );
      await page.route("**/scene/presentation.json", async (r) => {
        const res = await r.fetch(),
          j = await res.json();
        j.exterior_details.find(
          (x) => x.url === "friendly-west-detail.json",
        ).sha256 = hash;
        await r.fulfill({ response: res, json: j });
      });
    }
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo()),
      views = [];
    for (const [name, x, z, yaw] of [
      ["west-porch", -374, -30, -Math.PI / 2],
      ["oblique-porch", -374, -23, -0.9],
      ["south-porch", -374, -54, -Math.PI / 2],
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
              buildingId: "roof-556799cc",
              player: [x, ground, z],
              view: "first",
              yaw,
              pitch: 0.1,
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
        path: `../../docs/images/friendly-round-shafts-${name}-${after ? "after" : "before"}-2026-11-10.png`,
      });
      views.push({ blocked, ...state });
    }
    await page
      .getByRole("combobox", { name: "Search buildings" })
      .fill("Friendly Hall");
    await page
      .getByRole("option", { name: /Friendly Hall/ })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("roof-556799cc");
    results.push({ entries, views, errors });
    await page.evaluate(() => localStorage.clear());
    await context.clearCookies();
    await page.close();
  }
  await context.close();
  expect(results[0].entries).toEqual(results[1].entries);
  // Four shapes share their original material bucket: exact draw count and camera.
  expect(results[1].views).toHaveLength(results[0].views.length);
  for (let i = 0; i < results[0].views.length; i++) {
    const { draws: beforeDraws, ...beforeState } = results[0].views[i];
    const { draws: afterDraws, ...afterState } = results[1].views[i];
    expect(afterState).toEqual(beforeState);
    expect(afterDraws).toBe(beforeDraws);
  }
  expect(results.flatMap((x) => x.errors)).toEqual([]);
});
