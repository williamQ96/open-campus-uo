import { test, expect } from "@playwright/test";
import { capturePreview } from "./screenshots.js";

test.beforeEach(async ({ page }) => {
  await page.route(
    (url) => !["127.0.0.1", "localhost"].includes(url.hostname),
    (route) => route.abort(),
  );
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
});

test("search frames an overview at 45 degrees, turns walking views and prioritizes its label", async ({
  page,
}) => {
  const state = () => page.evaluate(() => window.__campus.getState());
  const before = (await state()).player;
  const emuId = await page.evaluate(
    () =>
      window.__campus
        .namedBuildings()
        .find((b) => b.name === "Erb Memorial Union").id,
  );
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("emu");
  await expect(
    page.getByRole("option", { name: /Erb Memorial Union/ }),
  ).toBeVisible();
  await search.press("ArrowDown");
  await expect(search).toHaveAttribute(
    "aria-activedescendant",
    "building-result-0",
  );
  await search.press("Enter");
  await expect.poll(async () => (await state()).cameraTransition).toBe(false);
  const overview = await state();
  expect(overview.selectedBuilding).toBe(emuId);
  expect(overview.player).toEqual(before);
  const offset = overview.camera.map((v, i) => v - overview.orbitTarget[i]);
  expect(Math.atan2(offset[1], Math.hypot(offset[0], offset[2]))).toBeCloseTo(
    Math.PI / 4,
    3,
  );
  expect(Math.hypot(...offset)).toBeLessThan(500);
  await expect(search).toHaveValue("Erb Memorial Union");
  await expect(search).toHaveAttribute("aria-expanded", "false");
  const label = page.locator(`.building-label[data-building-id="${emuId}"]`);
  await expect(label).toHaveClass(/is-selected/);
  await expect(label).toBeHidden();
  await expect(page.locator(".building-card")).toBeVisible();
  await capturePreview(page, "../../artifacts/search-overview.png");
  for (const mode of ["Digit2", "Digit1"]) {
    await page.keyboard.press(mode);
    await expect
      .poll(async () => {
        const current = await state();
        const target = await page.evaluate(
          (id) => window.__campus.labelInfo(id).anchor,
          emuId,
        );
        const direction = target.map((value, i) => value - current.camera[i]);
        const length = Math.hypot(direction[0], direction[2]);
        const cameraLength = Math.hypot(
          current.cameraDirection[0],
          current.cameraDirection[2],
        );
        return (
          (direction[0] * current.cameraDirection[0] +
            direction[2] * current.cameraDirection[2]) /
          (length * cameraLength)
        );
      })
      .toBeGreaterThan(0.999);
    expect((await state()).player).toEqual(before);
    await expect(label).toBeVisible();
  }
  await capturePreview(page, "../../artifacts/search-follow.png");
  await page.getByRole("button", { name: "Settings / About" }).click();
  await page.getByLabel("Building names", { exact: false }).uncheck();
  await page.getByRole("button", { name: "Close settings" }).click();
  await expect(label).toBeVisible();
  await expect(
    page.locator(".building-label:not(.is-selected):visible"),
  ).toHaveCount(0);
  await page.keyboard.press("Digit2");
  await page.mouse.move(850, 550);
  await page.mouse.down();
  await page.mouse.move(850, 850, { steps: 6 });
  await page.mouse.up();
  await expect(label).toHaveClass(/is-pinned/);
  await expect(label).toBeVisible();
  await page.getByRole("button", { name: "Clear building search" }).click();
  expect((await state()).selectedBuilding).toBeNull();
  await expect(page.locator(".label-layer")).toBeHidden();
  await expect(search).toHaveValue("");
});

test("search works on a narrow screen, supports no matches, and typing does not move the character", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const state = () => page.evaluate(() => window.__campus.getState());
  const before = (await state()).player;
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await expect(search).toBeInViewport();
  await page.keyboard.press("Slash");
  await expect(search).toBeFocused();
  await search.pressSequentially("WASD no such building", { delay: 10 });
  await expect(page.locator(".search-status")).toContainText(
    "No buildings found",
  );
  await search.press("Enter");
  expect((await state()).selectedBuilding).toBeNull();
  expect((await state()).player).toEqual(before);
  await search.fill("Knight Library");
  await page.getByRole("option", { name: /Knight Library/ }).click();
  await expect.poll(async () => (await state()).cameraTransition).toBe(false);
  await expect(page.locator(".building-label.is-selected")).toContainText(
    "Knight Library",
  );
  await expect(page.locator(".building-label.is-selected")).toBeHidden();
  await expect(page.locator(".building-card")).toBeVisible();
  await capturePreview(page, "../../artifacts/search-mobile.png");
  await search.focus();
  await search.press("Escape");
  await expect(search).toHaveAttribute("aria-expanded", "false");
  await expect(search).not.toBeFocused();
  await page.getByRole("button", { name: /Return to start/ }).click();
  expect((await state()).selectedBuilding).toBeNull();
  expect((await state()).player).toEqual(before);
});
