import { test, expect } from "@playwright/test";

test("full ground layer loads with local assets and compiles in toon and PBR", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });
  const groundResponse = page.waitForResponse((r) =>
    r.url().endsWith("/scene/landcover-l2/ground.glb"),
  );
  await page.goto("/");
  expect((await groundResponse).status()).toBe(200);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect(
    await page.evaluate(() => __campus.getState().presentation.landcoverLevel),
  ).toBe(2);
  const terrain = await page.evaluate(() => __campus.terrainCheck(-305, 0));
  expect(Math.abs(terrain.mesh - terrain.sampled)).toBeLessThan(0.001);
  const park = await page.evaluate(() => __campus.terrainCheck(-840, -630));
  expect(park.sampled).toBeCloseTo(-0.7125, 3);
  expect(park.mesh).toBeCloseTo(park.sampled, 3);
  expect(park.foundation).toBeCloseTo(park.sampled + 0.018, 3);
  await page.locator("#settings-open").click();
  await page.locator("#toon-setting").uncheck();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().presentation.toon))
    .toBe(false);
  await page.locator("#settings-close").click();
  await page.evaluate(() => __campus.setView("first"));
  await page.waitForTimeout(150);
  await page.locator("#settings-open").click();
  await page.locator("#toon-setting").check();
  await page.locator("#settings-close").click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().presentation.toon))
    .toBe(true);
  expect(errors).toEqual([]);
});

test("a damaged ground package keeps the earlier field and the fitted Arena site", async ({
  page,
}) => {
  await page.route("**/scene/landcover-l2/ground.glb", (route) =>
    route.fulfill({ status: 200, body: "stale-geometry" }),
  );
  const priorGround = page.waitForResponse((response) =>
    response.url().endsWith("/scene/landcover.glb"),
  );
  await page.goto("/");
  expect((await priorGround).status()).toBe(200);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const late = await page.evaluate(() => ({
    level: __campus.getState().presentation.landcoverLevel,
    park: __campus.terrainCheck(-840, -630),
    arena: __campus.terrainCheck(301.5, 34),
  }));
  expect(late.level).toBe(1);
  expect(late.park.sampled).toBeCloseTo(-1.8621, 3);
  expect(late.park.mesh).toBeCloseTo(late.park.sampled, 3);
  expect(late.park.foundation).toBeCloseTo(late.park.sampled + 0.018, 3);
  expect(late.arena.frontage).toBeCloseTo(3.20346, 3);
});

test("death window remains centered and restart reachable on a narrow phone", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 720 });
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  await page.evaluate(async () => {
    const { createDeathFlow } = await import("/src/death.js");
    createDeathFlow().show();
  });
  const dialog = page.locator("#death-dialog"),
    box = await dialog.boundingBox();
  expect(box.x).toBeGreaterThanOrEqual(16);
  expect(box.x + box.width).toBeLessThanOrEqual(374);
  expect(Math.abs(box.y + box.height / 2 - 360)).toBeLessThan(2);
  await expect(
    page.getByRole("button", { name: "Restart", exact: true }),
  ).toBeInViewport();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});
