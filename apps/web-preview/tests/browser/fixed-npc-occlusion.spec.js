import { test, expect } from "@playwright/test";

for (const mobile of [false, true]) {
  test(`fixed person label follows real building occlusion (${mobile ? "touch" : "desktop"})`, async ({
    browser,
  }, testInfo) => {
    const context = await browser.newContext({
      viewport: mobile
        ? { width: 390, height: 844 }
        : { width: 1440, height: 1000 },
      isMobile: mobile,
      hasTouch: mobile,
      reducedMotion: "reduce",
    });
    const page = await context.newPage();
    const visit = async (x, z, yaw, pitch = 0) => {
      await page.evaluate(
        ({ x, z, yaw, pitch }) =>
          sessionStorage.setItem(
            "explorer:outdoor-return:v1",
            JSON.stringify({
              version: 1,
              buildingId: "roof-0ca67b60",
              player: [x, 0.2, z],
              view: "first",
              yaw,
              pitch,
              followDistance: 7.5,
              density: 0,
              motionLevel: 0,
            }),
          ),
        { x, z, yaw, pitch },
      );
      await page.goto("/?return=1");
      await page.waitForFunction(
        () => window.__campus?.getState().ready && __campus.fixedNpcInfo(),
      );
    };
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    expect(await page.evaluate(() => __campus.collisionCheck(-5, -30))).toBe(
      false,
    );
    await visit(-5, -30, Math.atan2(37, 16));
    await expect
      .poll(() => page.evaluate(() => __campus.fixedNpcInfo().occluded))
      .toBe(true);
    expect(
      (await page.evaluate(() => __campus.fixedNpcScreenPosition())).visible,
    ).toBe(true);
    const label = page.getByRole("button", {
      name: "View Dan Carrere profile",
      includeHidden: true,
    });
    await expect(label).toBeHidden();
    await expect(page.locator(".fixed-person-bubble")).toBeHidden();
    await page.screenshot({ path: testInfo.outputPath("blocked.png") });
    await visit(-42, -41, 0, 0.13);
    await expect
      .poll(() => page.evaluate(() => __campus.fixedNpcInfo().occluded))
      .toBe(false);
    await expect(label).toBeVisible();
    const box = await label.boundingBox();
    if (mobile)
      await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2);
    else {
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await label.click();
    }
    const card = page.getByRole("dialog", { name: "Dan Carrere" });
    await expect(card).toBeVisible();
    await card.getByRole("button", { name: "Close" }).click();
    await expect(card).toBeHidden();
    await context.close();
  });
}
