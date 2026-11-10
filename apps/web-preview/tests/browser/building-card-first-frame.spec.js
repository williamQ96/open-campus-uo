import { test, expect } from "@playwright/test";
for (const viewport of [
  { width: 1440, height: 1000 },
  { width: 390, height: 844 },
]) {
  test(`building cards are positioned synchronously on opening and switching at ${viewport.width}px`, async ({
    page,
  }) => {
    await page.setViewportSize(viewport);
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    await expect(page.locator(".building-label:visible").first()).toBeVisible();
    const result = await page.evaluate(() => {
      const labels = [...document.querySelectorAll(".building-label")].filter(
        (el) => !el.hidden && el.getBoundingClientRect().width > 0,
      );
      const card = document.querySelector(".building-card");
      const read = () => {
        const b = card.getBoundingClientRect();
        return {
          hidden: card.hidden,
          transform: card.style.transform,
          id: card.dataset.buildingId,
          x: b.x,
          y: b.y,
          right: b.right,
          bottom: b.bottom,
        };
      };
      labels[0].click();
      const first = read();
      // Switch and measure in this same task, before a render-loop update.
      card.style.transform = "translate(0px, 0px)";
      labels[1].click();
      return {
        first,
        second: read(),
        expectedFirst: labels[0].dataset.buildingId,
        expectedSecond: labels[1].dataset.buildingId,
      };
    });
    expect(result.first.id).toBe(result.expectedFirst);
    expect(result.second.id).toBe(result.expectedSecond);
    expect(result.first.id).not.toBe(result.second.id);
    for (const card of [result.first, result.second]) {
      expect(card.hidden).toBe(false);
      expect(card.transform).toMatch(/^translate\(/);
      expect(card.x).toBeGreaterThan(0);
      expect(card.y).toBeGreaterThan(0);
      expect(card.right).toBeLessThanOrEqual(viewport.width);
      expect(card.bottom).toBeLessThanOrEqual(viewport.height);
    }
    await page.keyboard.press("Escape");
    await expect(page.locator(".building-card")).toBeHidden();
  });
}
