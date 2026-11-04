import { test, expect } from "@playwright/test";
test("seat refinement loads with full campus and keeps the original budget", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const p = page.waitForResponse((r) =>
    r.url().endsWith("/pilot-bench-seat-suppression.json"),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect((await p).status()).toBe(200);
  await page.locator("#settings-open").click();
  await page.getByRole("slider", { name: "Campus activity density" }).fill("0");
  await page.locator("#settings-close").click();
  await expect
    .poll(async () => page.evaluate(() => window.__campus.getState().drawCalls))
    .toBeLessThan(180);
  expect(errors).toEqual([]);
});
