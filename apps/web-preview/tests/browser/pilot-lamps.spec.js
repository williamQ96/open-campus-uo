import { test, expect } from "@playwright/test";
test("pilot lamp detail loads in the complete campus", async ({ page }) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const response = page.waitForResponse((r) =>
    r.url().endsWith("/pilot-lamp-detail.json"),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect((await response).status()).toBe(200);
  expect(errors).toEqual([]);
});
