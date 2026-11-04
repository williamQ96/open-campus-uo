import { test, expect } from "@playwright/test";
test("Anstett landscape loads in the campus viewer without breaking selection", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const loaded = page.waitForResponse((r) =>
    r.url().includes("/scene/anstett-lamps-detail.json"),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect((await loaded).status()).toBe(200);
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
