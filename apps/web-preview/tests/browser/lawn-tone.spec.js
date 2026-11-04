import { test, expect } from "@playwright/test";
test("lawn tone and paving load without shader errors in toon and PBR within existing budget", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });
  const response = page.waitForResponse((r) =>
    r.url().endsWith("/pilot-lawn-tone.json"),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect((await response).status()).toBe(200);
  await page.locator("#settings-open").click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  await page.waitForTimeout(300);
  await toon.check();
  await page.getByRole("slider", { name: "Campus activity density" }).fill("0");
  await page.locator("#settings-close").click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().drawCalls))
    .toBeLessThan(180);
  expect(errors).toEqual([]);
});
