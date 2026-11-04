import { test, expect } from "@playwright/test";
for (const [name, occupant, source] of [
  [
    "Lillis Hall",
    "Lundquist College of Business, Office of the Dean",
    "https://business.uoregon.edu/directory/deans-office",
  ],
  [
    "Columbia Hall",
    "Environmental Studies (faculty offices)",
    "https://cas.uoregon.edu/directory/environmental-studies-faculty/L",
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
