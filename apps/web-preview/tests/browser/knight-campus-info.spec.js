import { test, expect } from "@playwright/test";
test("Knight Campus placeholder cards show sourced building information", async ({
  page,
}) => {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const search = page.getByRole("combobox", { name: "Search buildings" }),
    card = page.locator(".building-card");
  for (const [name, id, year] of [
    ["Knight Campus 1", "context-oc-knight-1", "2020"],
    ["Knight Campus 2", "context-oc-knight-2", "2026"],
  ]) {
    await search.fill(name);
    await page.getByRole("option", { name }).first().click();
    await expect
      .poll(() =>
        page.evaluate(() => window.__campus.getState().selectedBuilding),
      )
      .toBe(id);
    await expect(card.locator(".building-card-summary")).toContainText(year);
    await expect(card.locator(".building-card-source")).toHaveAttribute(
      "href",
      "https://knightcampus.uoregon.edu/about",
    );
  }
});
