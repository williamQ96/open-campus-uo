import { test, expect } from "@playwright/test";
test("Matthew Knight Arena displays sourced home venue use", async ({
  page,
}) => {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("Matthew Knight Arena");
  await page
    .getByRole("option", { name: /Matthew Knight Arena/ })
    .first()
    .click();
  await expect(page.locator(".building-card-occupants")).toContainText(
    "UO basketball teams (home venue)",
  );
  await expect(page.locator(".building-card-source")).toHaveAttribute(
    "href",
    "https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/matthew-knight-arena",
  );
});
