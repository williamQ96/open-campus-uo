import { test, expect } from "@playwright/test";
test("corrected Annex retains selection and sourced building card", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("Gerlinger Annex");
  await page
    .getByRole("option", { name: /Gerlinger Annex/ })
    .first()
    .click();
  await expect
    .poll(() =>
      page.evaluate(() => window.__campus.getState().selectedBuilding),
    )
    .toBe("roof-f0b575d6");
  await expect(page.locator(".building-card-occupants")).toContainText(
    "Department of Dance",
  );
  await expect(page.locator(".building-card-source")).toHaveAttribute(
    "href",
    "https://musicanddance.uoregon.edu/about/facilities",
  );
  expect(errors).toEqual([]);
});
