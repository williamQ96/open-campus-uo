import { test, expect } from "@playwright/test";
test("Chapman remains selectable with existing collision", async ({ page }) => {
  let errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.route(
    (url) => !["127.0.0.1", "localhost"].includes(url.hostname),
    (r) => r.abort(),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  await page
    .getByRole("combobox", { name: "Search buildings" })
    .fill("Chapman Hall");
  await page
    .getByRole("option", { name: /Chapman Hall/ })
    .first()
    .click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
    .toBe("roof-f5cea51d");
  await expect(
    page.evaluate(() => __campus.collisionCheck(-500, 25)),
  ).resolves.toBe(true);
  await page.getByRole("button", { name: "Settings / About" }).click();
  let toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  await toon.check();
  expect(errors).toEqual([]);
});
