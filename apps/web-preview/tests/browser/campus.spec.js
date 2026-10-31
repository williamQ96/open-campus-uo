import { test, expect } from "@playwright/test";
test.beforeEach(async ({ page }) => {
  await page.route(
    (url) => !["127.0.0.1", "localhost"].includes(url.hostname),
    (route) => route.abort(),
  );
});
async function ready(page) {
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
}
test("full main campus loads, is English, and has terrain-aligned walking plus all views", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await ready(page);
  const state = () => page.evaluate(() => window.__campus.getState());
  expect((await state()).aoiSize).toBe(2000);
  expect((await state()).buildings).toBeGreaterThan(100);
  expect((await state()).namedBuildings).toBeGreaterThan(40);
  expect((await state()).roadSegments).toBeGreaterThan(100);
  expect((await state()).roadSurfaces).toBe(2);
  expect((await state()).blocked).toBe(false);
  const spawn = (await state()).player;
  expect(spawn[0]).toBeCloseTo(-305.469651, 4);
  expect(spawn[2]).toBeCloseTo(-0.824825, 4);
  const facesEmu = (direction, position) => {
    const dx = -215.002909 - position[0];
    const dz = 53.891474 - position[2];
    return (
      (direction[0] * dx + direction[2] * dz) /
      (Math.hypot(direction[0], direction[2]) * Math.hypot(dx, dz))
    );
  };
  expect(facesEmu((await state()).characterDirection, spawn)).toBeGreaterThan(
    0.999,
  );
  await expect(page.locator(".location-panel")).toHaveCount(0);
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  expect(await page.locator("body").innerText()).not.toMatch(/[\u3400-\u9fff]/);
  expect(
    await page
      .locator(".brand-logo")
      .evaluate((image) => image.complete && image.naturalWidth > 0),
  ).toBe(true);
  for (const [x, z] of [
    [0, 0],
    [50.3, -60.7],
    [-80.6, 70.4],
  ]) {
    const heights = await page.evaluate(
      ([x, z]) => window.__campus.terrainCheck(x, z),
      [x, z],
    );
    expect(heights.mesh).toBeDefined();
    expect(Math.abs(heights.mesh - heights.sampled)).toBeLessThan(0.001);
  }
  await page.screenshot({ path: "../../artifacts/eugene-campus-overview.png" });
  await page.getByRole("button", { name: /Follow/ }).click();
  expect((await state()).view).toBe("third");
  expect(
    facesEmu((await state()).cameraDirection, (await state()).player),
  ).toBeGreaterThan(0.999);
  const before = (await state()).player;
  await page.keyboard.down("KeyW");
  await expect
    .poll(async () => {
      const after = (await state()).player;
      return Math.hypot(after[0] - before[0], after[2] - before[2]);
    })
    .toBeGreaterThan(0.5);
  await page.keyboard.up("KeyW");
  expect((await state()).blocked).toBe(false);
  expect(
    Math.abs((await state()).player[1] - (await state()).ground),
  ).toBeLessThan(0.01);
  await page.screenshot({ path: "../../artifacts/eugene-follow.png" });
  await page.keyboard.press("Digit2");
  expect((await state()).view).toBe("first");
  await page.mouse.move(720, 650);
  await page.mouse.down();
  await page.mouse.move(800, 680, { steps: 5 });
  await page.mouse.up();
  await page.keyboard.press("KeyV");
  expect((await state()).view).toBe("aerial");
  await page.getByRole("button", { name: "Settings / About" }).click();
  await page.getByRole("button", { name: "About", exact: true }).click();
  await expect(page.locator("#about-panel")).toContainText("2008");
  await expect(page.locator("#road-source")).toContainText(
    "U.S. Census Bureau",
  );
  await expect(
    page.getByRole("link", { name: "Open Campus: UO · Campus application ↗" }),
  ).toHaveAttribute("href", "https://github.com/williamQ96/open-campus-uo");
  await expect(
    page.getByRole("link", {
      name: "Open Geospatial-to-3D Reconstruction Pipeline · Upstream ↗",
    }),
  ).toHaveAttribute(
    "href",
    "https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline",
  );
  await expect(page.locator("#coverage-stat")).toHaveText("2,000 × 2,000 m");
  expect(await page.locator("#about-panel").innerText()).not.toMatch(
    /[\u3400-\u9fff]/,
  );
  await page.screenshot({ path: "../../artifacts/eugene-about.png" });
  await page.getByRole("button", { name: "Settings", exact: true }).click();
  await page.getByLabel("Wireframe", { exact: false }).check();
  await page.getByLabel("Wireframe", { exact: false }).uncheck();
  await page.getByLabel("Building names", { exact: false }).uncheck();
  await expect(page.locator(".label-layer")).toBeHidden();
  await page.getByLabel("Building names", { exact: false }).check();
  await page.getByRole("button", { name: "Close settings" }).click();
  await page.getByRole("button", { name: /Return to start/ }).click();
  expect((await state()).player[0]).toBeCloseTo(before[0], 2);
  expect((await state()).player[2]).toBeCloseTo(before[2], 2);
  expect(
    facesEmu((await state()).characterDirection, (await state()).player),
  ).toBeGreaterThan(0.999);
  await page.keyboard.press("Digit2");
  await expect
    .poll(async () =>
      facesEmu((await state()).cameraDirection, (await state()).player),
    )
    .toBeGreaterThan(0.999);
  expect(errors).toEqual([]);
});
test("jump rises, lands, and works in first-person mode", async ({ page }) => {
  await ready(page);
  await page.getByRole("button", { name: /Follow/ }).click();
  await page.keyboard.press("Space");
  await expect
    .poll(async () =>
      page.evaluate(() => {
        const s = window.__campus.getState();
        return s.player[1] - s.ground;
      }),
    )
    .toBeGreaterThan(0.05);
  await page.screenshot({ path: "../../artifacts/eugene-jump.png" });
  await expect
    .poll(() => page.evaluate(() => window.__campus.getState().grounded), {
      timeout: 20000,
    })
    .toBe(true);
  await page.keyboard.press("Digit2");
  await page.keyboard.press("Space");
  await expect
    .poll(() => page.evaluate(() => window.__campus.getState().grounded))
    .toBe(false);
  await expect
    .poll(() => page.evaluate(() => window.__campus.getState().grounded), {
      timeout: 20000,
    })
    .toBe(true);
  const s = await page.evaluate(() => window.__campus.getState());
  expect(s.player[1]).toBeCloseTo(s.ground, 3);
});

test("Follow mouse-wheel zoom is bounded, keeps view changes, and respects settings", async ({
  page,
}) => {
  await ready(page);
  await page.keyboard.press("Digit1");
  await page.mouse.move(720, 700);
  const state = () => page.evaluate(() => window.__campus.getState());
  expect((await state()).followDistance).toBe(7.5);
  const before = (await state()).camera;
  await page.mouse.wheel(0, -480);
  await expect
    .poll(async () => (await state()).followDistance)
    .toBeLessThan(7.5);
  await expect
    .poll(async () => {
      const after = (await state()).camera;
      return Math.hypot(...after.map((value, i) => value - before[i]));
    })
    .toBeGreaterThan(0.3);
  for (let i = 0; i < 6; i++) await page.mouse.wheel(0, -1000);
  await expect.poll(async () => (await state()).followDistance).toBe(2.5);
  await page.keyboard.press("Digit2");
  await page.mouse.wheel(0, 500);
  expect((await state()).followDistance).toBe(2.5);
  await page.keyboard.press("Digit1");
  for (let i = 0; i < 6; i++) await page.mouse.wheel(0, 1000);
  await expect.poll(async () => (await state()).followDistance).toBe(30);
  await page.getByRole("button", { name: "Settings / About" }).click();
  await page.mouse.wheel(0, -600);
  expect((await state()).followDistance).toBe(30);
  await page.getByRole("button", { name: "Close settings" }).click();
  await page.getByRole("button", { name: /Return to start/ }).click();
  expect((await state()).followDistance).toBe(7.5);
});
test("building names follow projected roof anchors and remain screen-facing while orbiting", async ({
  page,
}) => {
  await ready(page);
  const names = await page.evaluate(() => window.__campus.namedBuildings());
  expect(names.some((b) => b.name === "Knight Library")).toBe(true);
  await expect(page.locator(".building-label:visible").first()).toBeVisible();
  const first = await page
    .locator(".building-label:visible")
    .first()
    .getAttribute("data-building-id");
  const before = await page.evaluate(
    (id) => window.__campus.labelInfo(id),
    first,
  );
  await page.mouse.move(600, 800);
  await page.mouse.down();
  await page.mouse.move(730, 800, { steps: 8 });
  await page.mouse.up();
  await expect
    .poll(() =>
      page.evaluate((id) => window.__campus.labelInfo(id).screen[0], first),
    )
    .not.toBeCloseTo(before.screen[0], 0);
  const check = await page
    .locator(".building-label:visible")
    .first()
    .evaluate((element) => {
      const matrix = new DOMMatrix(getComputedStyle(element).transform),
        rect = element.getBoundingClientRect();
      const info = window.__campus.labelInfo(element.dataset.buildingId);
      return {
        a: matrix.a,
        b: matrix.b,
        c: matrix.c,
        d: matrix.d,
        center: [rect.x + rect.width / 2, rect.y + rect.height / 2],
        screen: info.screen,
      };
    });
  expect(check.a).toBeCloseTo(1);
  expect(check.b).toBeCloseTo(0);
  expect(check.c).toBeCloseTo(0);
  expect(check.d).toBeCloseTo(1);
  expect(Math.abs(check.center[0] - check.screen[0])).toBeLessThan(2);
  expect(Math.abs(check.center[1] - check.screen[1])).toBeLessThan(2);
});
test("small viewport controls are reachable and movement stops on blur", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await ready(page);
  await expect(page.getByRole("button", { name: /Follow/ })).toBeInViewport();
  await expect(
    page.getByRole("button", { name: /First person/ }),
  ).toBeInViewport();
  await page.screenshot({ path: "../../artifacts/eugene-mobile.png" });
  await page.getByRole("button", { name: /First person/ }).click();
  await page.keyboard.down("KeyW");
  await page.evaluate(() => window.dispatchEvent(new Event("blur")));
  const before = await page.evaluate(() => window.__campus.getState().player);
  await page.waitForTimeout(600);
  expect(await page.evaluate(() => window.__campus.getState().player)).toEqual(
    before,
  );
  await page.keyboard.up("KeyW");
});
