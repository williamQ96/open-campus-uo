import { test, expect } from "@playwright/test";
test("sprinting crosses six metres with one render per second", async ({
  page,
}) => {
  test.setTimeout(90000);
  await page.addInitScript(() => {
    const original = window.requestAnimationFrame.bind(window);
    window.requestAnimationFrame = (cb) =>
      original((now) => {
        setTimeout(() => original(cb), 900);
      });
  });
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready, null, {
    timeout: 45000,
  });
  await page.evaluate(() => __campus.setView("first"));
  await page.locator("#viewport").focus();
  const start = (await page.evaluate(() => __campus.getState())).player;
  await page.keyboard.down("ShiftLeft");
  await page.keyboard.down("KeyW");
  try {
    await expect
      .poll(
        async () => {
          const p = (await page.evaluate(() => __campus.getState())).player;
          return Math.hypot(p[0] - start[0], p[2] - start[2]);
        },
        { timeout: 15000 },
      )
      .toBeGreaterThan(6);
  } finally {
    await page.keyboard.up("KeyW");
    await page.keyboard.up("ShiftLeft");
  }
});
