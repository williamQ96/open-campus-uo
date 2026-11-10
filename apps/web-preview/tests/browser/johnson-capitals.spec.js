import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
const layer = readFileSync(
  new URL("../../public/scene/johnson-north-capitals.json", import.meta.url),
);
test("Johnson north capitals retain source placement and navigation in front and oblique views", async ({
  browser,
}) => {
  const out = [];
  for (const before of [true, false]) {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1000 },
    });
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.route("**/scene/presentation.json", async (r) => {
      const response = await r.fetch(),
        json = await response.json();
      json.exterior_details = json.exterior_details.filter(
        (x) => x.url !== "johnson-north-capitals.json",
      );
      if (!before)
        json.exterior_details.push({
          url: "johnson-north-capitals.json",
          sha256: createHash("sha256").update(layer).digest("hex"),
        });
      await r.fulfill({ response, json });
    });
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo());
    const views = [];
    for (const [label, x, z] of [
      ["front", -401, 0],
      ["oblique", -420, 0],
    ]) {
      const ground = await page.evaluate(
        ({ x, z }) => __campus.terrainCheck(x, z).sampled,
        { x, z },
      );
      const yaw = Math.atan2(x + 401, z - 25.7);
      await page.evaluate(
        ({ x, z, ground, yaw }) =>
          sessionStorage.setItem(
            "explorer:outdoor-return:v1",
            JSON.stringify({
              version: 1,
              buildingId: "roof-906c030e",
              player: [x, ground, z],
              view: "first",
              yaw,
              pitch: -0.33,
              followDistance: 7.5,
              density: 0,
              motionLevel: 0,
            }),
          ),
        { x, z, ground, yaw },
      );
      await page.goto("/?return=1");
      await page.waitForFunction(
        () =>
          window.__campus?.getState().ready &&
          __campus.getState().life.density === "No",
      );
      await page.waitForTimeout(600);
      const actual = await page.evaluate(() => __campus.getState());
      expect(actual.player[0]).toBeCloseTo(x, 1);
      expect(actual.player[2]).toBeCloseTo(z, 1);
      expect(actual.view).toBe("first");
      expect(actual.cameraDirection[2]).toBeGreaterThan(0.6);
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
        path: `../../docs/images/johnson-capitals-${label}-${before ? "before" : "after"}-2026-11-10.png`,
      });
    }
    out.push({ entries, views, errors });
    await page.close();
  }
  expect(out[0].entries).toEqual(out[1].entries);
  expect(out.flatMap((x) => x.errors)).toEqual([]);
  for (let i = 0; i < 2; i++) {
    expect(out[0].views[i].blocked).toEqual(out[1].views[i].blocked);
    expect(out[1].views[i].draws).toBeLessThanOrEqual(
      out[0].views[i].draws + 1,
    );
  }
  console.log(JSON.stringify(out.map((x) => x.views)));
});
