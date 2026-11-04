import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const old = readFileSync(
  new URL(
    "../../../../assets/exterior-refinement/university-before-mansard-2026-11-04.json",
    import.meta.url,
  ),
);
test("University mansard refinement preserves campus selection, entrances, collision and draw budget", async ({
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
    page.on("console", (m) => {
      if (m.type() === "error") errors.push(m.text());
    });
    if (before) {
      await page.route("**/scene/university-hall-detail.json", (r) =>
        r.fulfill({ body: old, contentType: "application/json" }),
      );
      await page.route("**/scene/presentation.json", async (r) => {
        const res = await r.fetch(),
          j = await res.json();
        j.exterior_details.find(
          (x) => x.url === "university-hall-detail.json",
        ).sha256 =
          "002e68c05da416ed0ebe5616790f9174f3509918220aa879efcd91c314f7fb62";
        await r.fulfill({ response: res, json: j });
      });
    }
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo());
    let views = [];
    for (const [label, z, yaw] of [
      ["south", -88, 0],
      ["north", -162, Math.PI],
    ]) {
      const ground = await page.evaluate(
        (z) => __campus.terrainCheck(-457, z).sampled,
        z,
      );
      await page.evaluate(
        ({ ground, z, yaw }) =>
          sessionStorage.setItem(
            "explorer:outdoor-return:v1",
            JSON.stringify({
              version: 1,
              buildingId: "roof-9017feee",
              player: [-457, ground, z],
              view: "first",
              yaw,
              pitch: -0.28,
              followDistance: 7.5,
              density: 0,
              motionLevel: 0,
            }),
          ),
        { ground, z, yaw },
      );
      await page.goto("/?return=1");
      await page.waitForFunction(
        () =>
          window.__campus?.getState().ready &&
          __campus.getState().life.density === "No",
      );
      await page.waitForTimeout(500);
      await page.screenshot({
        path: `../../docs/images/university-mansard-${label}-${before ? "before" : "after"}-2026-11-04.png`,
      });
      views.push(
        await page.evaluate(
          ({ z }) => ({
            draws: __campus.getState().drawCalls,
            blocked: __campus.collisionCheck(-457, z),
          }),
          { z },
        ),
      );
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
