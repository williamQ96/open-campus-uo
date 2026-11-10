import { test, expect } from "@playwright/test";
for (const target of ["label", "close"]) {
  test(`Space activates the person ${target} button instead of jumping`, async ({
    page,
  }) => {
    await page.addInitScript(() =>
      sessionStorage.setItem(
        "explorer:outdoor-return:v1",
        JSON.stringify({
          version: 1,
          buildingId: "roof-0ca67b60",
          player: [-42, 0.2, -41],
          view: "first",
          yaw: 0,
          pitch: 0.13,
          followDistance: 7.5,
          density: 0,
          motionLevel: 0,
        }),
      ),
    );
    await page.goto("/?return=1");
    await page.waitForFunction(
      () => window.__campus?.getState().ready && __campus.fixedNpcInfo(),
    );
    const label = page.getByRole("button", {
      name: "View Dan Carrere profile",
    });
    await expect(label).toBeVisible();
    await label.focus();
    const card = page.getByRole("dialog", { name: "Dan Carrere" });
    if (target === "close") {
      await page.keyboard.press("Enter");
      await expect(card).toBeVisible();
      await expect(
        card.getByRole("button", { name: "Close", exact: true }),
      ).toBeFocused();
    }
    await page.keyboard.down("Space");
    expect((await page.evaluate(() => __campus.getState())).grounded).toBe(
      true,
    );
    await page.keyboard.up("Space");
    if (target === "label") {
      await expect(card).toBeVisible();
      await page.keyboard.press("Escape");
    }
    await expect(card).toBeHidden();
    await expect(label).toBeFocused();
  });
}
