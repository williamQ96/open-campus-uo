import { test, expect } from "@playwright/test";
test("Collier House exterior retains selectable identity in both render modes", async ({
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
    .fill("Collier House");
  await page
    .getByRole("option", { name: /Collier House/ })
    .first()
    .click();
  await expect(
    page.evaluate(() => __campus.collisionCheck(-338.65, 55.14)),
  ).resolves.toBe(true);
  await expect(
    page.evaluate(() => __campus.collisionCheck(-336.8, 55.14)),
  ).resolves.toBe(false);
  await expect(
    page.evaluate(() => __campus.collisionCheck(-335.13, 53.42)),
  ).resolves.toBe(true);
  await expect
    .poll(async () => (await state()).selectedBuilding)
    .toBe("roof-e5accf83");
  await expect.poll(async () => (await state()).drawCalls).toBeLessThan(250);
  await page.getByRole("button", { name: "Settings / About" }).click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  expect((await state()).selectedBuilding).toBe("roof-e5accf83");
  await toon.check();
  expect(errors).toEqual([]);
});
