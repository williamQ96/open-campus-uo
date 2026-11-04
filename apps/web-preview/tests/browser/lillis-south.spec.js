import { test, expect } from "@playwright/test";
test("Lillis stays selectable in both material modes within the existing budget", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.route(
    (url) => !["127.0.0.1", "localhost"].includes(url.hostname),
    (route) => route.abort(),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const state = () => page.evaluate(() => window.__campus.getState());
  await page
    .getByRole("combobox", { name: "Search buildings" })
    .fill("Lillis Hall");
  await page
    .getByRole("option", { name: /Lillis Hall/ })
    .first()
    .click();
  await expect
    .poll(async () => (await state()).selectedBuilding)
    .toBe("roof-86754ad7");
  await page.getByRole("button", { name: "Settings / About" }).click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  expect((await state()).selectedBuilding).toBe("roof-86754ad7");
  await toon.check();
  await page.getByRole("slider", { name: "Campus activity density" }).fill("0");
  await page.locator("#settings-close").click();
  await expect.poll(async () => (await state()).drawCalls).toBeLessThan(180);
  expect(errors).toEqual([]);
});
