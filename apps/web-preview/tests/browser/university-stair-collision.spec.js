import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const b = readFileSync(
    new URL(
      "../../../../assets/exterior-refinement/university-before-stair-collision-2026-11-04.json",
      import.meta.url,
    ),
  ),
  hash = "ec75085bab607623e2c03a9bb2bbd5a8b9bcaa9d21bb995eefe2afdac6b02f4d";
test("University stair collision preserves entry and route", async ({
  browser,
}) => {
  test.setTimeout(100000);
  let results = [];
  for (const after of [false, true]) {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1000 },
    });
    if (!after) {
      await page.route("**/scene/university-hall-detail.json", (r) =>
        r.fulfill({ body: b, contentType: "application/json" }),
      );
      await page.route("**/scene/presentation.json", async (r) => {
        const res = await r.fetch(),
          j = await res.json();
        j.exterior_details.find(
          (x) => x.url === "university-hall-detail.json",
        ).sha256 = hash;
        await r.fulfill({ response: res, json: j });
      });
    }
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo());
    const probes = await page.evaluate(() =>
      [-472.5, -441.5].map((x) =>
        [-126.77, -125.85, -125, -124.15, -123.23].map((z) =>
          __campus.collisionCheck(x, z),
        ),
      ),
    );
    await page.locator("#directions-open").click();
    for (const [side, name] of [
      ["A", "Johnson Hall"],
      ["B", "University Hall"],
    ]) {
      await page
        .getByRole("button", { name: `Search ${side}`, exact: true })
        .click();
      let input = page.getByRole("combobox");
      await input.fill(name);
      await input.press("ArrowDown");
      await input.press("Enter");
    }
    await page.locator("#route-start").click();
    const route = await page.evaluate(() => __campus.getState().navigation);
    console.log(
      after,
      JSON.stringify({
        probes,
        route: { active: route.active, points: route.points.length },
        entry: entries.find((x) => x.id === "roof-9017feee"),
      }),
    );
    results.push({ entries, probes, route });
    await page.close();
  }
  expect(results[1].entries).toEqual(results[0].entries);
  expect(results[1].route).toEqual(results[0].route);
  expect(results[1].route.points.length).toBeGreaterThan(3);
  for (const row of results[1].probes)
    expect(row).toEqual([true, false, true, false, true]);
});
