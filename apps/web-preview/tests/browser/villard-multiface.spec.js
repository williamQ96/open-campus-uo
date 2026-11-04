import { test, expect } from "@playwright/test";
test("Villard remains selectable and collision follows visible entrance", async ({
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
  await page
    .getByRole("combobox", { name: "Search buildings" })
    .fill("Villard Hall");
  await page
    .getByRole("option", { name: /Villard Hall/ })
    .first()
    .click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
    .toBe("roof-399c648e");
  await expect(
    page.evaluate(() => __campus.collisionCheck(-450, -202)),
  ).resolves.toBe(true);
  await expect(
    page.evaluate(() => __campus.collisionCheck(-438.5, -185)),
  ).resolves.toBe(true);
  await page.getByRole("button", { name: "Settings / About" }).click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  await toon.check();
  expect(errors).toEqual([]);
});
