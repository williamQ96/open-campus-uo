import { test, expect } from "@playwright/test";
for (const [name, occupant, source] of [
  [
    "Collier House",
    "School of Music and Dance (faculty office)",
    "https://musicanddance.uoregon.edu/directory/faculty/R",
  ],
  [
    "Clinical Services Building",
    "HEDCO Clinic (suite)",
    "https://education.uoregon.edu/college-educations-hedco-clinic-expansion",
  ],
])
  test(`${name} displays sourced occupant`, async ({ page }) => {
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const search = page.getByRole("combobox", { name: "Search buildings" });
    await search.fill(name);
    await page
      .getByRole("option", { name: new RegExp(name) })
      .first()
      .click();
    await expect(page.locator(".building-card-occupants")).toContainText(
      occupant,
    );
    await expect(page.locator(".building-card-source")).toHaveAttribute(
      "href",
      source,
    );
  });
