import { test, expect } from "@playwright/test";
for (const [name, occupants, source] of [
  [
    "Villard Hall",
    ["Department of Cinema Studies", "Department of Theatre Arts"],
    "https://cas.uoregon.edu/news/cas-connection/2026/june",
  ],
  [
    "Chiles Business Center",
    ["Information Services and Instructional Technology"],
    "https://business.uoregon.edu/directory/information-services",
  ],
])
  test(`${name} displays verified occupants`, async ({ page }) => {
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const search = page.getByRole("combobox", { name: "Search buildings" });
    await search.fill(name);
    await page
      .getByRole("option", { name: new RegExp(name) })
      .first()
      .click();
    for (const value of occupants)
      await expect(page.locator(".building-card-occupants")).toContainText(
        value,
      );
    await expect(page.locator(".building-card-source")).toHaveAttribute(
      "href",
      source,
    );
  });
