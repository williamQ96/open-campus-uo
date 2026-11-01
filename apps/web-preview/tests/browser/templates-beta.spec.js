import { test, expect } from "@playwright/test";
const state = (page) => page.evaluate(() => __campus.getState());
async function ready(page) {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

test("demand-generated NPCs have repeatable traits and a gated click inspector", async ({
  page,
}) => {
  await ready(page);
  let initial = await state(page);
  expect(initial.developerMode).toBe(false);
  expect(initial.life.allocatedInstances).toBe(29);
  expect(initial.life.preloadedActorPool).toBe(0);
  const student = initial.life.entities.find((e) => e.template === "student");
  expect(student.properties.heightM).toBeGreaterThanOrEqual(1.4);
  expect(student.properties.heightM).toBeLessThanOrEqual(2);
  expect(
    initial.life.entities
      .filter((e) => e.template === "squirrel")
      .some((e) => e.path.surface === "tree"),
  ).toBe(true);
  await page.locator("#settings-open").click();
  await page.locator("#activity-density").fill("0");
  expect((await state(page)).life.allocatedInstances).toBe(0);
  await page.locator("#activity-density").fill("2");
  expect(
    (await state(page)).life.entities.find((e) => e.id === student.id)
      .properties,
  ).toEqual(student.properties);
  await page.locator("#about-tab").click();
  await page.locator("#developer-setting").check();
  await page.locator("#settings-close").click();
  const ids = (await state(page)).life.entities.map((e) => e.id);
  for (const id of ids) {
    const point = await page.evaluate(
      (id) => __campus.npcScreenPosition(id),
      id,
    );
    if (
      !point?.visible ||
      point.x < 360 ||
      point.x > 1050 ||
      point.y < 180 ||
      point.y > 850
    )
      continue;
    await page.mouse.click(point.x, point.y);
    if (await page.locator("#developer-panel").isVisible()) break;
  }
  await expect(page.locator("#developer-panel")).toBeVisible();
  await expect(page.locator("#developer-properties")).toContainText("seed");
  const inspected = (await state(page)).inspectedNpc,
    info = await page.evaluate((id) => __campus.npcInfo(id), inspected);
  await expect(page.locator("#developer-properties")).toContainText(
    String(info.seed),
  );
  await page.locator("#settings-open").click();
  await page.locator("#developer-setting").uncheck();
  await page.locator("#settings-close").click();
  await expect(page.locator("#developer-panel")).toBeHidden();
});

test("first-level Zombie School beta clears ambience, spawns grounded monsters and restores the previous density", async ({
  page,
}) => {
  await ready(page);
  await page.locator("#settings-open").click();
  await page.locator("#activity-density").fill("1");
  await page.locator("#beta-tab").click();
  const toggle = page.getByRole("checkbox", {
    name: "ZOMBIE SCHOOL!!!",
    exact: true,
  });
  await toggle.check();
  let current = await state(page);
  expect(current.life.allocatedInstances).toBe(0);
  expect(current.life.colliders).toBe(0);
  expect(current.zombies.active).toBe(true);
  expect(current.zombies.count).toBe(28);
  expect(current.zombies.rules).toMatchObject({
    attractRadius: 30,
    releaseRadius: 60,
    wanderRadius: 12,
    wanderSpeed: 0.45,
    activeSpeed: 2.2,
  });
  const positions = current.zombies.actors.map((a) => [a.x, a.z]);
  await page.locator("#settings-close").click();
  await expect
    .poll(async () =>
      JSON.stringify((await state(page)).zombies.actors.map((a) => [a.x, a.z])),
    )
    .not.toBe(JSON.stringify(positions));
  for (const mode of ["first", "third", "aerial"]) {
    await page.evaluate((v) => __campus.setView(v), mode);
    expect((await state(page)).view).toBe(mode);
  }
  await expect(page.locator("#beta-badge")).toBeVisible();
  await page.locator("#settings-open").click();
  await toggle.uncheck();
  current = await state(page);
  expect(current.zombies.count).toBe(0);
  expect(current.life.density).toBe("Low");
  expect(current.life.allocatedInstances).toBe(7);
  await page.locator("#settings-close").click();
  await expect(page.locator("#beta-badge")).toBeHidden();
});
