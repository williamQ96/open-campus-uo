import { test, expect } from "@playwright/test";
test("Knight Law Center remains selectable in both render modes and within budget", async ({
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
    .fill("Knight Law Center");
  await page
    .getByRole("option", { name: /Knight Law Center/ })
    .first()
    .click();
  await expect
    .poll(async () => (await state()).selectedBuilding)
    .toBe("roof-f52041e8");
  await page.getByRole("button", { name: "Settings / About" }).click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  expect((await state()).selectedBuilding).toBe("roof-f52041e8");
  await toon.check();
  await page.getByRole("slider", { name: "Campus activity density" }).fill("0");
  await page.locator("#settings-close").click();
  await expect.poll(async () => (await state()).drawCalls).toBeLessThan(180);
  expect(errors).toEqual([]);
});
