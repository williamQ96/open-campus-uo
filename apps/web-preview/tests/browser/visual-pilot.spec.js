import { test, expect } from "@playwright/test";

test("authored pilot preserves all landmark search modes, geometry provenance and material fallback", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.route(
    (url) => !["127.0.0.1", "localhost"].includes(url.hostname),
    (route) => route.abort(),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const state = () => page.evaluate(() => window.__campus.getState());
  expect((await state()).presentation).toMatchObject({
    id: "knight-emu-johnson-v1",
    buildings: 14,
    trees: 220,
    landmarkBuildings: 3,
    toon: true,
  });
  expect((await state()).drawCalls).toBeLessThan(180);
  const spawn = (await state()).player;
  for (const name of ["Knight Library", "Johnson Hall", "Erb Memorial Union"]) {
    const search = page.getByRole("combobox", { name: "Search buildings" });
    await search.fill(name);
    await search.press("ArrowDown");
    await search.press("Enter");
    await expect.poll(async () => (await state()).cameraTransition).toBe(false);
    await expect(page.locator("#selection")).toContainText(
      "Photo-informed art model",
    );
    await expect(page.locator(".building-label.is-selected")).toHaveText(name);
    for (const [mode, view] of [
      ["Digit1", "third"],
      ["Digit2", "first"],
      ["Digit3", "aerial"],
    ]) {
      await page.keyboard.press(mode);
      expect((await state()).view).toBe(view);
      expect((await state()).player).toEqual(spawn);
      expect((await state()).selectedBuilding).toBeTruthy();
    }
  }
  await page.getByRole("button", { name: "Settings / About" }).click();
  await page.getByLabel("Architectural toon", { exact: false }).uncheck();
  expect((await state()).presentation.toon).toBe(false);
  await page.getByLabel("Wireframe", { exact: false }).check();
  await page.getByLabel("Wireframe", { exact: false }).uncheck();
  await page.getByLabel("Architectural toon", { exact: false }).check();
  await page.getByRole("button", { name: "About", exact: true }).click();
  await expect(page.locator("#about-panel")).toContainText("illustrative");
  expect(errors).toEqual([]);
});
