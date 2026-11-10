import { test, expect } from "@playwright/test";

for (const viewport of [
  { width: 1440, height: 1000 },
  { width: 390, height: 844 },
]) {
  test(`person card is anchored in the opening task at ${viewport.width}px`, async ({
    page,
  }) => {
    await page.setViewportSize(viewport);
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
    const result = await label.evaluate((button) => {
      // Opening and measurement share one JS task: no animation-frame retry can hide a flash.
      button.focus();
      button.click();
      const card = document.querySelector(".fixed-person-card");
      const rect = card.getBoundingClientRect();
      const first = {
        x: rect.x,
        y: rect.y,
        right: rect.right,
        bottom: rect.bottom,
        transform: card.style.transform,
        open: card.open,
      };
      card.querySelector("button").click();
      card.style.transform = "translate(0px, 0px)";
      button.focus();
      button.click();
      const reopened = card.getBoundingClientRect();
      return {
        first,
        reopened: { x: reopened.x, y: reopened.y },
        modal: card.matches(":modal"),
        focused: document.activeElement === card.querySelector("button"),
      };
    });
    expect(result.first.open).toBe(true);
    expect(result.modal).toBe(false);
    expect(result.focused).toBe(true);
    expect(result.first.transform).toMatch(/^translate\(/);
    expect(result.first.x).toBeGreaterThan(0);
    expect(result.first.y).toBeGreaterThan(0);
    expect(result.first.right).toBeLessThanOrEqual(viewport.width);
    expect(result.first.bottom).toBeLessThanOrEqual(viewport.height);
    expect(result.reopened).toEqual({ x: result.first.x, y: result.first.y });
    await page.keyboard.press("Escape");
    await expect(
      page.getByRole("dialog", { name: "Dan Carrere" }),
    ).not.toBeVisible();
    await expect(label).toBeFocused();
  });
}
