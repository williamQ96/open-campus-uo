import { test, expect } from "@playwright/test";
test("Susan selection and exterior collision remain consistent", async ({
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
    .fill("Susan Campbell");
  await page
    .getByRole("option", { name: /Susan Campbell/ })
    .first()
    .click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
    .toBe("roof-fd061857");
  await expect(
    page.evaluate(() => __campus.collisionCheck(-451, 150)),
  ).resolves.toBe(true);
  await expect(
    page.evaluate(() => __campus.collisionCheck(-437, 163)),
  ).resolves.toBe(true);
  await page.getByRole("button", { name: "Settings / About" }).click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  await toon.check();
  expect(errors).toEqual([]);
});
