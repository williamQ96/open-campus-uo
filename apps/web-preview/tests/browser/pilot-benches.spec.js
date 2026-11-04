import { test, expect } from "@playwright/test";
test("reusable pilot benches load with the full campus", async ({ page }) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const patch = page.waitForResponse((r) =>
    r.url().endsWith("/pilot-bench-back-suppression.json"),
  );
  const detail = page.waitForResponse((r) =>
    r.url().endsWith("/pilot-bench-detail.json"),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect((await patch).status()).toBe(200);
  expect((await detail).status()).toBe(200);
  expect((await page.evaluate(() => __campus.getState())).life.density).toBe(
    "Mid",
  );
  expect(errors).toEqual([]);
});
