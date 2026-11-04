import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const old = readFileSync(
  new URL(
    "../../../../assets/exterior-refinement/susan-before-courtyard-2026-11-04.json",
    import.meta.url,
  ),
);
test("Susan courtyard study retains campus selection, entrances, collision and draw counts", async ({
  browser,
}) => {
  const results = [];
  for (const before of [true, false]) {
    const page = await browser.newPage({
        viewport: { width: 1440, height: 1000 },
        reducedMotion: "reduce",
      }),
      errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    page.on("console", (m) => {
      if (m.type() === "error") errors.push(m.text());
    });
    if (before) {
      await page.route("**/scene/susan-roof-detail.json", (r) =>
        r.fulfill({ body: old, contentType: "application/json" }),
      );
      await page.route("**/scene/presentation.json", async (r) => {
        const res = await r.fetch(),
          j = await res.json();
        j.exterior_details.find(
          (x) => x.url === "susan-roof-detail.json",
        ).sha256 =
          "6bcfacf17d80aa9e934ed27c6280c8dd48e2556b350b54500725a99757450189";
        await r.fulfill({ response: res, json: j });
      });
    }
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo());
    const views = [];
    for (const [label, x, z, yaw] of [
      ["court", -440, 147, 2.78],
      ["south", -446.5, 205, 0],
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
              buildingId: "roof-fd061857",
              player: [x, ground, z],
              view: "first",
              yaw,
              pitch: -0.28,
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
      await page.screenshot({
        path: `../../docs/images/susan-courtyard-${label}-${before ? "before" : "after"}-2026-11-04.png`,
      });
      views.push(
        await page.evaluate(
          ({ x, z }) => ({
            draws: __campus.getState().drawCalls,
            blocked: __campus.collisionCheck(x, z),
          }),
          { x, z },
        ),
      );
    }
    await page
      .getByRole("combobox", { name: "Search buildings" })
      .fill("Susan Campbell Hall");
    await page
      .getByRole("option", { name: /Susan Campbell Hall/ })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("roof-fd061857");
    results.push({ entries, views, errors });
    await page.close();
  }
  expect(results[1].entries).toEqual(results[0].entries);
  expect(results[1].views.map((v) => v.blocked)).toEqual(
    results[0].views.map((v) => v.blocked),
  );
  expect(results[1].views.map((v) => v.draws)).toEqual(
    results[0].views.map((v) => v.draws),
  );
  expect(results.flatMap((x) => x.errors)).toEqual([]);
});
