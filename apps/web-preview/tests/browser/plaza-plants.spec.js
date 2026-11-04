import { test, expect } from "@playwright/test";
test("additional plaza patch loads alongside existing fern and bench layers", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const p = page.waitForResponse((r) =>
    r.url().endsWith("/pilot-plaza-plant-suppression.json"),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect((await p).status()).toBe(200);
  expect(errors).toEqual([]);
});
