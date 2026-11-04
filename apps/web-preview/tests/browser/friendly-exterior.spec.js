import { test, expect } from "@playwright/test";

test("Friendly exterior retains its building identity in toon and PBR", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.route(
    (url) => !["127.0.0.1", "localhost"].includes(url.hostname),
    (route) => route.abort(),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const state = () => page.evaluate(() => window.__campus.getState());
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("Friendly Hall");
  await page
    .getByRole("option", { name: /Friendly Hall/ })
    .first()
    .click();
  await expect
    .poll(async () => (await state()).selectedBuilding)
    .toBe("roof-556799cc");
  await expect(page.locator(".building-card-source")).toHaveAttribute(
    "href",
    /uoregon\.edu/,
  );
  await expect.poll(async () => (await state()).drawCalls).toBeLessThan(250);
  await page.getByRole("button", { name: "Settings / About" }).click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  expect((await state()).presentation.toon).toBe(false);
  expect((await state()).selectedBuilding).toBe("roof-556799cc");
  await toon.check();
  expect((await state()).presentation.toon).toBe(true);
  expect(errors).toEqual([]);
});
