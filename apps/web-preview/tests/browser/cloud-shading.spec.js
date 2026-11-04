import { test, expect } from "@playwright/test";
test("cloud shading loads with reduced motion and existing draw budget", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect(
    await page.evaluate(() => window.__campus.getState().sky),
  ).toMatchObject({ blue: true, clouds: 18, roundedEdges: true });
  await page.locator("#settings-open").click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  await toon.check();
  await page.getByRole("slider", { name: "Campus activity density" }).fill("0");
  await page.locator("#settings-close").click();
  await expect
    .poll(async () => page.evaluate(() => window.__campus.getState().drawCalls))
    .toBeLessThan(180);
  expect(errors).toEqual([]);
});
