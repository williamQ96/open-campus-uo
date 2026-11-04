import { test, expect } from "@playwright/test";
test("Volcanology map match is explicitly approximate and has sourced information", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("Volcanology");
  await page
    .getByRole("option", { name: /Volcanology \(approximate\)/ })
    .first()
    .click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
    .toBe("roof-399a0551");
  await expect(page.locator(".building-card-summary")).toContainText(
    "Approximate map match",
  );
  await expect(page.locator(".building-card-occupants")).toContainText(
    "Department of Earth Sciences",
  );
  await expect(page.locator(".building-card-source")).toHaveAttribute(
    "href",
    "https://cas.uoregon.edu/directory/natural-sciences/G",
  );
  const entry = await page.evaluate(() =>
    __campus.namedBuildings().find((x) => x.id === "roof-399a0551"),
  );
  expect(entry.name_match).toBe("approximate-map-match");
  expect((await page.evaluate(() => __campus.namedBuildings())).length).toBe(
    64,
  );
  expect(errors).toEqual([]);
});
test("missing optional identity annotations leave the campus usable and unnamed", async ({
  page,
}) => {
  await page.route("**/scene/building-identities.json", (route) =>
    route.fulfill({ status: 404, body: "missing" }),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect(
    await page.evaluate(() =>
      __campus.namedBuildings().some((x) => x.id === "roof-399a0551"),
    ),
  ).toBe(false);
});
