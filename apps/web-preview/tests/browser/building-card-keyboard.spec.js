import { test, expect } from "@playwright/test";
for (const key of ["Enter", "Space"]) {
  test(`keyboard ${key} opens a non-modal building card and restores its label`, async ({
    page,
  }) => {
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const labels = page.locator(".building-label:visible");
    const id = await labels.first().getAttribute("data-building-id");
    const label = page.locator(`.building-label[data-building-id="${id}"]`);
    await label.focus();
    await page.keyboard.press(key);
    const card = page.locator(".building-card");
    const close = card.getByRole("button", { name: "Close building card" });
    await expect(close).toBeFocused();
    await expect(label).toBeHidden();
    await page.keyboard.press("Tab");
    expect(
      await card.evaluate((el) => el.contains(document.activeElement)),
    ).toBe(true);
    await card.getByRole("button", { name: "Enter", exact: true }).focus();
    await page.keyboard.press("Tab");
    expect(
      await card.evaluate((el) => el.contains(document.activeElement)),
    ).toBe(false);
    await close.focus();
    await page.keyboard.press("Escape");
    await expect(card).toBeHidden();
    await expect(label).toBeFocused();
    await page.keyboard.press(key);
    await expect(close).toBeFocused();
    await page.keyboard.press(key);
    await expect(card).toBeHidden();
    await expect(label).toBeFocused();
    // Switching via another label updates the return destination.
    await page.keyboard.press(key);
    await expect(close).toBeFocused();
    const other = page.locator(".building-label:visible").first();
    const otherId = await other.getAttribute("data-building-id");
    await other.focus();
    await page.keyboard.press(key);
    await expect(close).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(
      page.locator(`.building-label[data-building-id="${otherId}"]`),
    ).toBeFocused();
    await page.keyboard.press(key);
    await card.getByRole("button", { name: "Enter", exact: true }).focus();
    await page.keyboard.press(key);
    await page.waitForFunction(() => window.__interior?.getState().ready);
    expect(await page.evaluate(() => __interior.getState().buildingId)).toBe(
      otherId,
    );
  });
}
test("pointer selection does not move focus into the building card", async ({
  page,
}) => {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  await page.locator(".building-label:visible").first().click();
  const card = page.locator(".building-card");
  await expect(card).toBeVisible();
  expect(await card.evaluate((el) => el.contains(document.activeElement))).toBe(
    false,
  );
  await card.getByRole("button", { name: "Close building card" }).click();
  await expect(card).toBeHidden();
  await expect(page.locator("#viewport")).toBeFocused();
});
