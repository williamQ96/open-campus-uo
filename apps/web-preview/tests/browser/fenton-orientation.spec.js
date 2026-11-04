import { test, expect } from "@playwright/test";
test("Fenton correction retains selection and original building collision", async ({
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
    .fill("Fenton Hall");
  await page
    .getByRole("option", { name: /Fenton Hall/ })
    .first()
    .click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
    .toBe("roof-4f0c798e");
  await expect(
    page.evaluate(() => __campus.collisionCheck(-450, -30)),
  ).resolves.toBe(true);
  await page.getByRole("button", { name: "Settings / About" }).click();
  let toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  await toon.check();
  expect(errors).toEqual([]);
});
