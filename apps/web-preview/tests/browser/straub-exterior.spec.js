import { test, expect } from "@playwright/test";
test("Straub west facade retains selectable identity in both render modes", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.route(
    (url) => !["127.0.0.1", "localhost"].includes(url.hostname),
    (r) => r.abort(),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const state = () => page.evaluate(() => window.__campus.getState());
  await page
    .getByRole("combobox", { name: "Search buildings" })
    .fill("Straub Hall");
  await page
    .getByRole("option", { name: /Straub Hall/ })
    .first()
    .click();
  await expect
    .poll(async () => (await state()).selectedBuilding)
    .toBe("roof-5ded2bf0");
  await expect.poll(async () => (await state()).drawCalls).toBeLessThan(250);
  await page.getByRole("button", { name: "Settings / About" }).click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  expect((await state()).selectedBuilding).toBe("roof-5ded2bf0");
  await toon.check();
  expect(errors).toEqual([]);
});
