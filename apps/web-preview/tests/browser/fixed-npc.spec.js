import { test, expect } from "@playwright/test";

test("Dan fixed person path, label, speech and model interaction", async ({
  page,
}, testInfo) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const pathClear = await page.evaluate(() =>
    Array.from({ length: 49 }, (_, i) => -46 + i * 0.25).every(
      (z) => !__campus.collisionCheck(-42, z),
    ),
  );
  expect(pathClear).toBe(true);
  await page.evaluate(() =>
    sessionStorage.setItem(
      "explorer:outdoor-return:v1",
      JSON.stringify({
        version: 1,
        buildingId: "roof-0ca67b60",
        player: [-42, 0.2, -41],
        view: "first",
        yaw: 0,
        pitch: 0.13,
        followDistance: 7.5,
        density: 0,
        motionLevel: 0,
      }),
    ),
  );
  await page.goto("/?return=1");
  await page.waitForFunction(
    () => window.__campus?.getState().ready && __campus.fixedNpcInfo(),
  );
  const initial = await page.evaluate(() => __campus.fixedNpcInfo());
  await expect
    .poll(
      async () =>
        (await page.evaluate(() => __campus.fixedNpcInfo())).position[1] -
        initial.position[1],
      { timeout: 12000 },
    )
    .toBeGreaterThan(0.02);
  expect(
    (await page.evaluate(() => __campus.fixedNpcInfo())).gait.phase,
  ).toBeGreaterThan(initial.gait.phase);
  const label = page.getByRole("button", { name: "View Dan Carrere profile" });
  await expect(label).toBeVisible();
  await expect(page.locator(".fixed-person-bubble")).toHaveText(
    "you just graduated",
  );
  await expect(page.locator(".fixed-person-bubble")).toBeVisible();
  const bubbleBox = await page.locator(".fixed-person-bubble").boundingBox();
  const nameBox = await label.boundingBox();
  expect(bubbleBox.x).toBeGreaterThan(nameBox.x + nameBox.width / 2);
  expect(bubbleBox.y + bubbleBox.height).toBeLessThan(
    nameBox.y + nameBox.height,
  );
  const tail = await page
    .locator(".fixed-person-bubble")
    .evaluate((el) => getComputedStyle(el, "::after").clipPath);
  expect(tail).not.toBe("none");
  await page.screenshot({
    path: testInfo.outputPath("visible-person.png"),
  });
  const box = await label.boundingBox();
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await expect
    .poll(() => page.evaluate(() => __campus.fixedNpcInfo().hovered))
    .toBe(true);
  await label.click();
  const card = page.getByRole("dialog", { name: "Dan Carrere" });
  await expect(card).toBeVisible();
  expect(await card.evaluate((element) => element.matches(":modal"))).toBe(
    false,
  );
  await expect
    .poll(async () => {
      const cardBox = await card.boundingBox();
      const labelBox = await label.boundingBox();
      return cardBox.x > labelBox.x + labelBox.width / 2;
    })
    .toBe(true);
  const desktopCard = await card.boundingBox();
  expect(desktopCard.x + desktopCard.width).toBeLessThanOrEqual(1440);
  expect(desktopCard.y + desktopCard.height).toBeLessThanOrEqual(1000);
  await page.screenshot({
    path: testInfo.outputPath("person-card-desktop.png"),
  });
  await page.setViewportSize({ width: 700, height: 700 });
  await expect
    .poll(async () => {
      const bounds = await card.boundingBox();
      return (
        bounds &&
        bounds.x >= 0 &&
        bounds.y >= 0 &&
        bounds.x + bounds.width <= 700 &&
        bounds.y + bounds.height <= 700
      );
    })
    .toBe(true);
  await page.setViewportSize({ width: 1440, height: 1000 });
  await expect(
    card.getByRole("link", { name: "University profile" }),
  ).toHaveAttribute(
    "href",
    "https://cas.uoregon.edu/directory/school-of-computer-and-data-sciences/all/dcarrere",
  );
  const playerBefore = await page.evaluate(() => __campus.getState().player);
  await page.keyboard.down("KeyD");
  await page.waitForTimeout(300);
  await page.keyboard.up("KeyD");
  await expect
    .poll(async () => {
      const playerAfter = await page.evaluate(() => __campus.getState().player);
      return Math.hypot(
        playerAfter[0] - playerBefore[0],
        playerAfter[2] - playerBefore[2],
      );
    })
    .toBeGreaterThan(0.05);
  await expect(card).toBeVisible();
  await card.getByRole("button", { name: "Close" }).click();
  await expect(card).not.toBeVisible();
  await expect(label).toBeFocused();
  const pt = await page.evaluate(() => __campus.fixedNpcScreenPosition());
  expect(pt.visible).toBe(true);
  await page.mouse.move(pt.x, pt.y);
  await expect
    .poll(() => page.evaluate(() => __campus.fixedNpcInfo().hovered))
    .toBe(true);
  await page.mouse.click(pt.x, pt.y);
  await expect(card).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(card).not.toBeVisible();
  await label.focus();
  await expect
    .poll(() => page.evaluate(() => __campus.fixedNpcInfo().hovered))
    .toBe(true);
  await page.keyboard.press("Enter");
  await expect(card).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(card).not.toBeVisible();
  await label.click();
  await expect(card).toBeVisible();
  await page.mouse.move(80, 450);
  await page.mouse.down();
  await page.mouse.move(680, 450, { steps: 8 });
  await page.mouse.up();
  await expect(card).not.toBeVisible();
  await page.evaluate(() =>
    sessionStorage.setItem(
      "explorer:outdoor-return:v1",
      JSON.stringify({
        version: 1,
        buildingId: "roof-0ca67b60",
        player: [-42, 0.2, -41],
        view: "first",
        yaw: 0,
        pitch: 0.13,
        followDistance: 7.5,
        density: 0,
        motionLevel: 0,
      }),
    ),
  );
  await page.goto("/?return=1");
  await page.waitForFunction(
    () => window.__campus?.getState().ready && __campus.fixedNpcInfo(),
  );
  await expect(label).toBeVisible();
  await label.click();
  await expect(card).toBeVisible();
  await card.getByRole("button", { name: "Close" }).click();
  expect(errors).toEqual([]);
});

test("fixed person label and profile work on touch screens", async ({
  browser,
}, testInfo) => {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true,
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  await page.evaluate(() =>
    sessionStorage.setItem(
      "explorer:outdoor-return:v1",
      JSON.stringify({
        version: 1,
        buildingId: "roof-0ca67b60",
        player: [-42, 0.2, -41],
        view: "first",
        yaw: 0,
        pitch: 0.13,
        followDistance: 7.5,
        density: 0,
        motionLevel: 0,
      }),
    ),
  );
  await page.goto("/?return=1");
  await page.waitForFunction(
    () => window.__campus?.getState().ready && __campus.fixedNpcInfo(),
  );
  const label = page.getByRole("button", { name: "View Dan Carrere profile" });
  await expect(label).toBeVisible();
  const box = await label.boundingBox();
  await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2);
  const card = page.getByRole("dialog", { name: "Dan Carrere" });
  await expect(card).toBeVisible();
  await expect
    .poll(async () => {
      const bounds = await card.boundingBox();
      return (
        bounds.x >= 0 &&
        bounds.y >= 0 &&
        bounds.x + bounds.width <= 390 &&
        bounds.y + bounds.height <= 844
      );
    })
    .toBe(true);
  const mobileCard = await card.boundingBox(),
    mobileLabel = await label.boundingBox();
  expect(mobileCard.y).toBeGreaterThan(mobileLabel.y + mobileLabel.height);
  await page.screenshot({
    path: testInfo.outputPath("person-card-mobile.png"),
  });
  await card.getByRole("button", { name: "Close" }).tap();
  await expect(card).not.toBeVisible();
  await context.close();
});
