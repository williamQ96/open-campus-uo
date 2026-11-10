import { test, expect } from "@playwright/test";
test("pinned same-building batches recover three draws without losing selection or entrances", async ({
  browser,
}) => {
  const results = [];
  for (const batched of [false, true]) {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    if (!batched)
      await page.route("**/src/building-overlay-batches.js", (r) =>
        r.fulfill({
          contentType: "text/javascript",
          body: "export const trackedLayerNames=[]; export function recipeSupports(){return false;} export async function mergePinnedBuildingOverlays(){return 0;}",
        }),
      );
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    await page.locator("#settings-open").click();
    await page
      .getByRole("slider", { name: "Campus activity density" })
      .fill("0");
    await page.locator("#settings-close").click();
    await page.waitForTimeout(500);
    const draws = await page.evaluate(() => __campus.getState().drawCalls),
      entrances = await page.evaluate(() => __campus.entranceInfo());
    const selected = [];
    for (const [name, id] of [
      ["Knight Library", "roof-6684e091"],
      ["Gerlinger Hall", "roof-9ac93ab7"],
      ["Johnson Hall", "roof-906c030e"],
    ]) {
      await page.getByRole("combobox", { name: "Search buildings" }).fill(name);
      await page
        .getByRole("option", { name: new RegExp(name) })
        .first()
        .click();
      await expect
        .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
        .toBe(id);
      selected.push(id);
    }
    results.push({ draws, entrances, selected, errors });
    await page.close();
  }
  expect(results[1].draws).toBe(results[0].draws - 3);
  expect(results[1].draws).toBeLessThan(180);
  expect(results[1].entrances).toEqual(results[0].entrances);
  expect(results[1].selected).toEqual(results[0].selected);
  expect(results.flatMap((r) => r.errors)).toEqual([]);
  console.log(
    JSON.stringify(results.map(({ draws, selected }) => ({ draws, selected }))),
  );
});
