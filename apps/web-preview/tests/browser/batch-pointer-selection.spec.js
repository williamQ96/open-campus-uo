import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const source = readFileSync(
    new URL("../../src/presentation.js", import.meta.url),
    "utf8",
  ),
  start = source.indexOf("  // Adjacent original source-pinned shrub layers"),
  end = source.indexOf("  if (config.landcover_url)", start),
  block = source.slice(start, end);
test("pointer selection of each landmark survives shrub batching", async ({
  browser,
}) => {
  expect(start).toBeGreaterThanOrEqual(0);
  expect(end).toBeGreaterThan(start);
  for (const before of [true, false]) {
    const page = await browser.newPage();
    if (before)
      await page.route(/\/src\/presentation\.js(?:\?.*)?$/, async (route) => {
        const response = await route.fetch(),
          body = await response.text();
        if (!body.includes(block)) throw Error("Cannot establish baseline");
        await route.fulfill({ response, body: body.replace(block, "") });
      });
    for (const [id, x, z, yaw] of [
      ["roof-9017feee", -459, -92, 0],
      ["roof-399c648e", -417, -184, Math.PI / 2],
    ]) {
      await page.goto("/");
      await page.waitForFunction(() => window.__campus?.getState().ready);
      const ground = await page.evaluate(
        ([x, z]) => __campus.terrainCheck(x, z).sampled,
        [x, z],
      );
      await page.evaluate(
        ({ id, x, z, yaw, ground }) =>
          sessionStorage.setItem(
            "explorer:outdoor-return:v1",
            JSON.stringify({
              version: 1,
              buildingId: id,
              player: [x, ground, z],
              view: "first",
              yaw,
              pitch: 0,
              followDistance: 7.5,
              density: 0,
              motionLevel: 0,
            }),
          ),
        { id, x, z, yaw, ground },
      );
      await page.goto("/?return=1");
      await page.waitForFunction(
        () =>
          window.__campus?.getState().ready &&
          __campus.getState().life.density === "No",
      );
      await page.mouse.click(360, 380);
      await expect
        .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
        .toBe(id);
    }
    await page.close();
  }
});
