import { test, expect } from "@playwright/test";
test("integrated Longhouse retains original fixed draw budget", async ({
  page,
}) => {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  await page.getByRole("button", { name: "Settings / About" }).click();
  await page.getByRole("slider", { name: "Campus activity density" }).fill("0");
  await page.locator("#settings-close").click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().drawCalls))
    .toBeLessThan(180);
  console.log(
    "draw calls",
    await page.evaluate(() => __campus.getState().drawCalls),
  );
});
