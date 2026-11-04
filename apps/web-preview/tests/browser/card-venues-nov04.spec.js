import { test, expect } from "@playwright/test";
for (const [name, occupant, source] of [
  [
    "McArthur Court",
    "Physical Education and Recreation (program use)",
    "https://rec.uoregon.edu/rooms/mcarthur-court",
  ],
  [
    "Hayward Field",
    "UO Track and Field (home venue)",
    "https://hayward.uoregon.edu/tower",
  ],
])
  test(`${name} displays sourced venue use`, async ({ page }) => {
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
