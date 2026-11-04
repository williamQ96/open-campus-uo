import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const previous = readFileSync(
  new URL(
    "../../../../assets/exterior-refinement/johnson-before-rear-band-window-2026-11-04.json",
    import.meta.url,
  ),
);
test("Johnson rear window and cornice retain selection, entrances, collision and budget", async ({
  browser,
}) => {
  const out = [];
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
      await page.route("**/scene/johnson-rear-detail.json", (r) =>
        r.fulfill({ body: previous, contentType: "application/json" }),
      );
      await page.route("**/scene/presentation.json", async (r) => {
        const res = await r.fetch(),
          j = await res.json();
        j.exterior_detail_sha256 =
          "ec05e9528eebe13db4c7856bc81a1cabd8e8ff080ceaee4646c16ad9f290a17d";
        await r.fulfill({ response: res, json: j });
      });
    }
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo());
    const views = [];
    for (const [label, x, z, yaw] of [
      ["south", -401, 85, 0],
      ["oblique", -387, 80, 0.45],
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
              buildingId: "roof-906c030e",
              player: [x, ground, z],
              view: "first",
              yaw,
              pitch: -0.23,
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
        path: `../../docs/images/johnson-rear-window-band-${label}-${before ? "before" : "after"}-2026-11-04.png`,
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
      .fill("Johnson Hall");
    await page
      .getByRole("option", { name: /Johnson Hall/ })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("roof-906c030e");
    out.push({ entries, views, errors });
    await page.close();
  }
  expect(out[1].entries).toEqual(out[0].entries);
  expect(out[1].views).toEqual(out[0].views);
  expect(out.flatMap((x) => x.errors)).toEqual([]);
});
