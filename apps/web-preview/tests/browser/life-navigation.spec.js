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

test("rigged hero, four density levels, wildlife and clean-map collision removal", async ({
  page,
}) => {
  await ready(page);
  const before = await state(page);
  expect(before.riggedHero).toBe(true);
  expect(before.life).toMatchObject({
    density: "Mid",
    students: 8,
    bikes: 2,
    scooters: 2,
    cars: 4,
    squirrels: 8,
    props: 5,
    colliders: 29,
  });
  await expect
    .poll(async () => JSON.stringify((await state(page)).life.positions))
    .not.toBe(JSON.stringify(before.life.positions));
  await page.locator("#settings-open").click();
  const slider = page.getByRole("slider", { name: "Campus activity density" });
  await expect(slider).toHaveValue("2");
  for (const [level, name, count] of [
    [0, "No", 0],
    [1, "Low", 7],
    [2, "Mid", 29],
    [3, "High", 74],
  ]) {
    await slider.fill(String(level));
    await expect(slider).toHaveAttribute("aria-valuetext", name);
    expect((await state(page)).life.colliders).toBe(count);
  }
  await slider.fill("0");
  await page.locator("#settings-close").click();
  await expect
    .poll(async () => (await state(page)).drawCalls)
    .toBeLessThan(180);
  expect((await state(page)).life.positions).toEqual([]);
  expect(await page.evaluate(() => __campus.lifeColliders())).toEqual([]);
});
test("Overview A/B and fixed walking origins survive movement, view switches and explicit restart", async ({
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
  const manual = (await state(page)).navigation;
  expect(manual.originMode).toBe("manual");
  expect(manual.points.length).toBeGreaterThan(3);
  await page.locator("#directions-close").click();
  let walkingPoints;
  for (const mode of ["first", "third"]) {
    await page.evaluate((v) => __campus.setView(v), mode);
    let route = (await state(page)).navigation;
    expect(route.originMode).toBe("player");
    expect(route.walkingStart).toEqual([spawn[0], -spawn[2]]);
    walkingPoints ||= route.points;
    expect(route.points).toEqual(walkingPoints);
    await page.locator("#directions-open").click();
    await expect(page.locator("#route-a")).toHaveText(
      "You · fixed starting point",
    );
    await expect(
      page.getByRole("button", { name: "Search A", exact: true }),
    ).toBeHidden();
    await page.locator("#directions-close").click();
    await page.locator("#viewport").focus();
    const before = (await state(page)).player;
    await page.keyboard.down("ShiftLeft");
    await page.keyboard.down("KeyW");
    try {
      // Cross the previous 3 m reroute threshold by a clear margin.
      await expect
        .poll(async () => {
          const p = (await state(page)).player;
          return Math.hypot(p[0] - before[0], p[2] - before[2]);
        })
        .toBeGreaterThan(6);
    } finally {
      await page.keyboard.up("KeyW");
      await page.keyboard.up("ShiftLeft");
    }
    await page.waitForTimeout(1200);
    route = (await state(page)).navigation;
    expect(route.walkingStart).toEqual([spawn[0], -spawn[2]]);
    expect(route.points).toEqual(walkingPoints);
  }
  await page.evaluate(() => __campus.setView("aerial"));
  expect((await state(page)).navigation.points).toEqual(manual.points);
  await page.evaluate(() => __campus.setView("third"));
  expect((await state(page)).navigation.points).toEqual(walkingPoints);
  const restart = (await state(page)).player;
  await page.locator("#directions-open").click();
  await page.locator("#route-start").click();
  const newRoute = (await state(page)).navigation;
  expect(newRoute.walkingStart).toEqual([restart[0], -restart[2]]);
  expect(newRoute.points[0]).toEqual([restart[0], -restart[2]]);
  expect(newRoute.points).not.toEqual(walkingPoints);
  await page.locator("#route-clear").click();
  expect((await state(page)).navigation).toMatchObject({
    active: false,
    walkingStart: null,
    points: [],
  });
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
