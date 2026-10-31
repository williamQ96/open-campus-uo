import { test, expect } from "@playwright/test";
async function ready(page) {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  await page.waitForTimeout(300);
}
async function search(page, endpoint, name) {
  await page
    .getByRole("button", { name: `Search ${endpoint}`, exact: true })
    .click();
  const input = page.getByRole("combobox");
  await input.fill(name);
  await input.press("ArrowDown");
  await input.press("Enter");
}
const state = (page) => page.evaluate(() => window.__campus.getState());

test("rigged hero, default campus activity, motion and independent clean-map switches", async ({
  page,
}) => {
  await ready(page);
  const before = await state(page);
  expect(before.riggedHero).toBe(true);
  expect(before.life).toMatchObject({
    npcEnabled: true,
    propsEnabled: true,
    students: 8,
    bikes: 2,
    scooters: 2,
    cars: 4,
    props: 5,
  });
  await expect
    .poll(async () => JSON.stringify((await state(page)).life.positions))
    .not.toBe(JSON.stringify(before.life.positions));
  await page.locator("#settings-open").click();
  await page.locator("#people-setting").uncheck();
  expect((await state(page)).life.propsEnabled).toBe(true);
  await page.locator("#props-setting").uncheck();
  await page.locator("#settings-close").click();
  await page.waitForTimeout(200);
  const clean = await state(page);
  expect(clean.life.npcEnabled).toBe(false);
  expect(clean.life.propsEnabled).toBe(false);
  expect(clean.drawCalls).toBeLessThan(180);
  const positions = clean.life.positions;
  await page.waitForTimeout(150);
  expect((await state(page)).life.positions).toEqual(positions);
});
test("Overview A/B building routing and live player origin across walking modes", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await ready(page);
  const spawn = (await state(page)).player;
  await page.locator("#directions-open").click();
  expect(await page.locator("#route-start").isDisabled()).toBe(true);
  await search(page, "A", "Johnson Hall");
  await search(page, "B", "Knight Library");
  await page.locator("#route-start").click();
  let route = (await state(page)).navigation;
  expect(route.originMode).toBe("manual");
  expect(route.points.length).toBeGreaterThan(3);
  expect(route.distance).toBeGreaterThan(100);
  await page.locator("#directions-close").click();
  for (const mode of ["first", "third"]) {
    await page.evaluate((v) => __campus.setView(v), mode);
    route = (await state(page)).navigation;
    expect(route.originMode).toBe("player");
    expect(route.points[0][0]).toBeCloseTo(spawn[0]);
    expect(route.points[0][1]).toBeCloseTo(-spawn[2]);
  }
  await page.locator("#directions-open").click();
  await expect(page.locator("#route-a")).toHaveText("You · live position");
  await expect(
    page.getByRole("button", { name: "Search A", exact: true }),
  ).toBeHidden();
  await page.locator("#directions-close").click();
  await page.locator("#viewport").focus();
  await page.keyboard.down("KeyW");
  await page.waitForTimeout(700);
  await page.keyboard.up("KeyW");
  await page.waitForTimeout(1300);
  route = (await state(page)).navigation;
  const moved = (await state(page)).player;
  expect(
    Math.hypot(route.points[0][0] - moved[0], route.points[0][1] + moved[2]),
  ).toBeLessThan(4);
  expect(errors).toEqual([]);
});
test("phone Overview supports free ground pins without obstructing view controls", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await ready(page);
  await page.locator("#directions-open").click();
  await page.getByRole("button", { name: "Pin A on map" }).click();
  await expect(page.locator("#directions-panel")).toHaveClass(/is-pinning/);
  // A real canvas tap: choose one of several visible ground locations, skipping buildings.
  for (const [x, y] of [
    [200, 600],
    [300, 530],
    [160, 700],
    [70, 620],
    [310, 690],
    [200, 480],
  ]) {
    if (!(await state(page)).navigation.a) await page.mouse.click(x, y);
  }
  expect((await state(page)).navigation.a).toBeTruthy();
  await search(page, "B", "Erb Memorial Union");
  await page.locator("#route-start").click();
  expect((await state(page)).navigation.points.length).toBeGreaterThan(1);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.locator("#directions-close").click();
  await page
    .getByRole("button", { name: "First person", exact: false })
    .click();
  expect((await state(page)).view).toBe("first");
});
