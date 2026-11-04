import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const old = readFileSync(
  new URL(
    "../../../../assets/exterior-refinement/university-before-entry-stairs-2026-11-04.json",
    import.meta.url,
  ),
);
test("University entrance stairs preserve selection, entrances, sampled collision and draw calls", async ({
  browser,
}) => {
  test.setTimeout(90000);
  const results = [];
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    reducedMotion: "reduce",
  });
  for (const before of [true, false]) {
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    page.on("console", (m) => {
      if (m.type() === "error") errors.push(m.text());
    });
    if (before) {
      await page.route("**/scene/university-hall-detail.json", (r) =>
        r.fulfill({ body: old, contentType: "application/json" }),
      );
      await page.route("**/scene/presentation.json", async (r) => {
        const response = await r.fetch(),
          json = await response.json();
        json.exterior_details.find(
          (x) => x.url === "university-hall-detail.json",
        ).sha256 =
          "4fabdca6fbc3f429e21b2de165db3be8a92aa41b30c0e94fba8f459c5903837a";
        await r.fulfill({ response, json });
      });
    }
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo()),
      views = [];
    for (const [label, x, z, yaw] of [
      ["east", -430, -125, Math.PI / 2],
      ["west", -484, -125, -Math.PI / 2],
      ["south", -457, -100, 0],
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
              buildingId: "roof-9017feee",
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
      const view = await page.evaluate(
        ({ x, z }) => ({
          camera: __campus.getState().camera,
          draws: __campus.getState().drawCalls,
          blocked: __campus.collisionCheck(x, z),
        }),
        { x, z },
      );
      expect(view.camera[0]).toBeCloseTo(x, 1);
      expect(view.camera[2]).toBeCloseTo(z, 1);
      await page.screenshot({
        path: `../../docs/images/university-stairs-${label}-${before ? "before" : "after"}-2026-11-04.png`,
      });
      views.push(view);
    }
    await page
      .getByRole("combobox", { name: "Search buildings" })
      .fill("University Hall");
    await page
      .getByRole("option", { name: /University Hall/ })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("roof-9017feee");
    results.push({ entries, views, errors });
    await page.evaluate(() => localStorage.clear());
    await context.clearCookies();
    await page.close();
  }
  await context.close();
  expect(results[1].entries).toEqual(results[0].entries);
  expect(results[1].views).toEqual(results[0].views);
  expect(results.flatMap((r) => r.errors)).toEqual([]);
});
