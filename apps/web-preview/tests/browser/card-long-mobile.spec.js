import { test, expect } from "@playwright/test";

for (const viewport of [
  { width: 390, height: 844 },
  { width: 844, height: 390 },
]) {
  test(`long building information remains usable at ${viewport.width}x${viewport.height}`, async ({
    browser,
  }) => {
    const context = await browser.newContext({
      viewport,
      isMobile: true,
      hasTouch: true,
    });
    const page = await context.newPage();
    await page.route("**/building-info.json", async (route) => {
      const response = await route.fetch();
      const data = await response.json();
      for (const entry of Object.values(data.records)) {
        entry.purpose =
          "A long example of campus building information. ".repeat(24);
        entry.occupants = [
          "A representative department with a long name",
          "Another campus department",
        ];
      }
      await route.fulfill({ response, json: data });
    });
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const search = page.getByRole("combobox", { name: "Search buildings" });
    await search.fill("Knight Library");
    await page
      .getByRole("option", { name: /Knight Library/ })
      .first()
      .tap();
    await page.waitForFunction(
      () => !window.__campus.getState().cameraTransition,
    );
    const card = page.locator(".building-card");
    await expect(card).toBeVisible();
    await expect(card.locator(".building-card-summary")).toContainText(
      "long example",
    );
    const bounds = await card.boundingBox();
    expect(bounds.x).toBeGreaterThanOrEqual(0);
    expect(bounds.y).toBeGreaterThanOrEqual(0);
    expect(bounds.y + bounds.height).toBeLessThanOrEqual(viewport.height);
    expect(await card.evaluate((el) => el.scrollHeight > el.clientHeight)).toBe(
      true,
    );
    const cdp = await context.newCDPSession(page);
    const point = (y) => ({
      id: 1,
      x: bounds.x + bounds.width / 2,
      y,
      radiusX: 4,
      radiusY: 4,
      force: 1,
    });
    await cdp.send("Input.dispatchTouchEvent", {
      type: "touchStart",
      touchPoints: [point(bounds.y + bounds.height * 0.8)],
    });
    for (const fraction of [0.65, 0.5, 0.35, 0.2])
      await cdp.send("Input.dispatchTouchEvent", {
        type: "touchMove",
        touchPoints: [point(bounds.y + bounds.height * fraction)],
      });
    await cdp.send("Input.dispatchTouchEvent", {
      type: "touchEnd",
      touchPoints: [],
    });
    await expect
      .poll(() => card.evaluate((el) => el.scrollTop))
      .toBeGreaterThan(0);
    const enter = card.getByRole("button", { name: "Enter", exact: true });
    await enter.scrollIntoViewIfNeeded();
    await enter.tap();
    await page.waitForFunction(() => window.__interior?.getState().ready);
    expect(await page.evaluate(() => window.__interior.getState().view)).toBe(
      "aerial",
    );
    await context.close();
  });
}
