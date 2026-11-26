import { test, expect } from "@playwright/test";
test("the registered courtyard with Anstett lamps preserves building selection", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const loaded = page.waitForResponse((r) =>
    r.url().includes("/scene/lillis-complex-review/site.glb"),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect((await loaded).status()).toBe(200);
  const surface = await page.evaluate(() => __campus.terrainCheck(-547, -27));
  expect(surface["lillis-complex-paving"]).toBeGreaterThan(surface.sampled);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("Anstett Hall");
  await page
    .getByRole("option", { name: /Anstett Hall/ })
    .first()
    .click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
    .toBe("roof-0a498bf7");
  await expect(page.locator(".building-card")).toBeVisible();
  expect(errors).toEqual([]);
});
