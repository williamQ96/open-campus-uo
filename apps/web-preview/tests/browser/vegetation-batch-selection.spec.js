import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const source = readFileSync(
  new URL("../../src/presentation.js", import.meta.url),
  "utf8",
);
const start = source.indexOf(
    "  // Adjacent original source-pinned shrub layers",
  ),
  end = source.indexOf("  if (config.landcover_url)", start),
  block = source.slice(start, end);
test("adjacent shrub batching preserves all entrances and both building selections", async ({
  browser,
}) => {
  expect(start).toBeGreaterThanOrEqual(0);
  expect(end).toBeGreaterThan(start);
  const entries = [];
  for (const before of [true, false]) {
    const page = await browser.newPage();
    if (before)
      await page.route(/\/src\/presentation\.js(?:\?.*)?$/, async (route) => {
        const response = await route.fetch(),
          body = await response.text();
        if (!body.includes(block))
          throw Error("Unable to establish unbatched baseline");
        await route.fulfill({ response, body: body.replace(block, "") });
      });
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    entries.push(await page.evaluate(() => __campus.entranceInfo()));
    const search = page.getByRole("combobox", { name: "Search buildings" });
    for (const [name, id] of [
      ["University Hall", "roof-9017feee"],
      ["Villard Hall", "roof-399c648e"],
    ]) {
      await search.fill(name);
      await page
        .getByRole("option", { name: new RegExp(name) })
        .first()
        .click();
      await expect
        .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
        .toBe(id);
    }
    expect(errors).toEqual([]);
    await page.close();
  }
  expect(entries[0]).toHaveLength(534);
  expect(entries[1]).toEqual(entries[0]);
});
