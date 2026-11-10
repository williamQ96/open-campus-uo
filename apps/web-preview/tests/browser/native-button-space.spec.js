import { test, expect } from "@playwright/test";
for (const target of ["Follow", "Settings / About"]) {
  test(`Space activates focused ${target} button without jumping`, async ({
    page,
  }) => {
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    await page.evaluate(() => __campus.setView("first"));
    const button = page.getByRole("button", {
      name: target,
      exact: target === "Settings / About",
    });
    await button.focus();
    await page.keyboard.down("Space");
    expect((await page.evaluate(() => __campus.getState())).grounded).toBe(
      true,
    );
    await page.keyboard.up("Space");
    if (target === "Follow")
      await expect
        .poll(() => page.evaluate(() => __campus.getState().view))
        .toBe("third");
    else
      await expect(
        page.getByRole("button", { name: "Close settings" }),
      ).toBeVisible();
  });
}

test("viewport Space still jumps and clicking Follow leaves W movement available", async ({
  page,
}) => {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  await page.getByRole("button", { name: "Follow", exact: false }).click();
  const before = await page.evaluate(() => __campus.getState().player);
  await page.keyboard.down("KeyW");
  await expect
    .poll(async () => {
      const p = await page.evaluate(() => __campus.getState().player);
      return Math.hypot(p[0] - before[0], p[2] - before[2]);
    })
    .toBeGreaterThan(0.1);
  await page.keyboard.up("KeyW");
  await page.locator("#viewport").focus();
  await page.keyboard.down("Space");
  expect((await page.evaluate(() => __campus.getState())).grounded).toBe(false);
  await page.keyboard.up("Space");
  await expect
    .poll(() => page.evaluate(() => __campus.getState().grounded))
    .toBe(true);
});
