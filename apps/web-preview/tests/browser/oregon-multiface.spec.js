import { test, expect } from "@playwright/test";
test("Oregon Hall remains selectable with existing collision", async ({
  page,
}) => {
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
    .fill("Oregon Hall");
  await page
    .getByRole("option", { name: /Oregon Hall/ })
    .first()
    .click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
    .toBe("roof-11d15952");
  await expect(
    page.evaluate(() => __campus.collisionCheck(55, -40)),
  ).resolves.toBe(true);
  await page.getByRole("button", { name: "Settings / About" }).click();
  let toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  await toon.check();
  expect(errors).toEqual([]);
});
