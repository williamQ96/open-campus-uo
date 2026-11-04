import { test, expect } from "@playwright/test";
test("Anstett frontage remains selectable and renders in both modes", async ({
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
    .fill("Anstett Hall");
  await page
    .getByRole("option", { name: /Anstett Hall/ })
    .first()
    .click();
  await expect
    .poll(async () => (await state()).selectedBuilding)
    .toBe("roof-0a498bf7");
  await expect.poll(async () => (await state()).drawCalls).toBeLessThan(250);
  await expect(page.locator(".building-card-summary")).toContainText(
    "classrooms and offices",
  );
  await expect(page.locator(".building-card-occupants")).toContainText(
    "Anstett Family Accounting Suite",
  );
  await page.getByRole("button", { name: "Settings / About" }).click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  expect((await state()).selectedBuilding).toBe("roof-0a498bf7");
  await toon.check();
  expect(errors).toEqual([]);
});
