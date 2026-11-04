import { test, expect } from "@playwright/test";
test("campus canopy tone loads in toon and PBR and respects the existing budget", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const patch = page.waitForResponse((r) =>
    r.url().endsWith("/pilot-canopy-tone.json"),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect((await patch).status()).toBe(200);
  await page.locator("#settings-open").click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  await page.waitForTimeout(250);
  await toon.check();
  await page.getByRole("slider", { name: "Campus activity density" }).fill("0");
  await page.locator("#settings-close").click();
  await expect
    .poll(async () => page.evaluate(() => window.__campus.getState().drawCalls))
    .toBeLessThan(180);
  expect(errors).toEqual([]);
});
