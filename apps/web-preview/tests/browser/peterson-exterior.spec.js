import { test, expect } from "@playwright/test";
test("Peterson exterior remains selectable in toon and PBR", async ({
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
    .fill("Peterson Hall");
  await page
    .getByRole("option", { name: /Peterson Hall/ })
    .first()
    .click();
  await expect
    .poll(async () => (await state()).selectedBuilding)
    .toBe("roof-75e776d0");
  await expect.poll(async () => (await state()).drawCalls).toBeLessThan(250);
  await expect(page.locator(".building-card-occupants")).toContainText(
    "Oregon MBA",
  );
  await page.getByRole("button", { name: "Settings / About" }).click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  expect((await state()).selectedBuilding).toBe("roof-75e776d0");
  await toon.check();
  expect(errors).toEqual([]);
});
