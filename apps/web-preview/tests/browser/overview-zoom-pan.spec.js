import { test, expect } from "@playwright/test";

const distance = async (page) =>
  page.evaluate(() => {
    const { camera, orbitTarget } = __campus.getState();
    return Math.hypot(...camera.map((value, i) => value - orbitTarget[i]));
  });

test("overview wheel reaches both bounds after panning and works over labels", async ({
  page,
}) => {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  await page.mouse.move(900, 500);
  await page.mouse.wheel(0, -100000);
  await expect.poll(() => distance(page)).toBeCloseTo(12, 1);
  await page.mouse.wheel(0, 100000);
  await expect.poll(() => distance(page)).toBeCloseTo(6000, 1);
  await page.evaluate(() => __campus.setView("aerial"));
  const initial = await page.evaluate(() => __campus.getState().orbitTarget);
  await page.mouse.move(900, 300);
  await page.mouse.down({ button: "right" });
  await page.mouse.move(900, 800, { steps: 12 });
  await page.mouse.up({ button: "right" });
  await expect
    .poll(async () => {
      const target = await page.evaluate(() => __campus.getState().orbitTarget);
      return Math.hypot(...target.map((value, i) => value - initial[i]));
    })
    .toBeGreaterThan(20);
  await page.waitForTimeout(1200);
  const labelPoint = await page.evaluate(() => {
    for (const label of document.querySelectorAll(".building-label")) {
      const box = label.getBoundingClientRect();
      const x = box.x + box.width / 2,
        y = box.y + box.height / 2;
      if (
        !label.hidden &&
        box.width &&
        x > 40 &&
        x < innerWidth - 40 &&
        y > 180 &&
        y < innerHeight - 150 &&
        document.elementFromPoint(x, y) === label
      )
        return { x, y };
    }
    return null;
  });
  expect(labelPoint).not.toBeNull();
  await page.mouse.move(labelPoint.x, labelPoint.y);
  await page.waitForTimeout(200);
  expect(
    await page.evaluate(
      ({ x, y }) =>
        document.elementFromPoint(x, y)?.classList.contains("building-label"),
      labelPoint,
    ),
  ).toBe(true);
  const before = await distance(page);
  await page.mouse.wheel(0, -5000);
  await expect.poll(() => distance(page)).toBeLessThan(before * 0.5);
  await page.mouse.move(900, 500);
  await page.mouse.wheel(0, -100000);
  await expect.poll(() => distance(page)).toBeCloseTo(12, 1);
  await page.mouse.wheel(0, 100000);
  await expect.poll(() => distance(page)).toBeCloseTo(6000, 1);
});

test("overview touch pinch still zooms after a two-finger pan", async ({
  browser,
}) => {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true,
    reducedMotion: "reduce",
  });
  try {
    const page = await context.newPage();
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const cdp = await context.newCDPSession(page);
    const point = (id, x, y) => ({
      id,
      x,
      y,
      radiusX: 4,
      radiusY: 4,
      force: 1,
    });
    const touch = (type, touchPoints) =>
      cdp.send("Input.dispatchTouchEvent", { type, touchPoints });
    const pinch = async (direction) => {
      const positions =
        direction === "in" ? [140, 250, 25, 365] : [25, 365, 185, 205];
      const y = await page.evaluate(([first, second]) => {
        for (let y = 300; y <= 740; y += 20) {
          if (
            [first, second].every(
              (x) => document.elementFromPoint(x, y)?.tagName === "CANVAS",
            )
          )
            return y;
        }
        return null;
      }, positions);
      expect(y).not.toBeNull();
      await touch("touchStart", [
        point(1, positions[0], y),
        point(2, positions[1], y),
      ]);
      await touch("touchMove", [
        point(1, positions[2], y),
        point(2, positions[3], y),
      ]);
      await touch("touchEnd", []);
      await page.waitForTimeout(220);
    };
    const checkBounds = async () => {
      for (let i = 0; i < 12 && (await distance(page)) > 12.01; i++)
        await pinch("in");
      expect(await distance(page)).toBeCloseTo(12, 1);
      for (let i = 0; i < 12 && (await distance(page)) < 5999.9; i++)
        await pinch("out");
      expect(await distance(page)).toBeCloseTo(6000, 1);
    };
    await page.waitForTimeout(700);
    await checkBounds();
    await page.evaluate(() => __campus.setView("aerial"));
    await page.waitForTimeout(700);
    const start = await page.evaluate(() => __campus.getState().orbitTarget);
    await touch("touchStart", [point(1, 55, 600), point(2, 285, 600)]);
    await touch("touchMove", [point(1, 95, 630), point(2, 325, 630)]);
    await touch("touchEnd", []);
    await expect
      .poll(async () => {
        const target = await page.evaluate(
          () => __campus.getState().orbitTarget,
        );
        return Math.hypot(...target.map((value, i) => value - start[i]));
      })
      .toBeGreaterThan(1);
    await page.waitForTimeout(500);
    const before = await distance(page);
    await touch("touchStart", [point(1, 140, 600), point(2, 240, 600)]);
    await touch("touchMove", [point(1, 55, 600), point(2, 325, 600)]);
    await touch("touchEnd", []);
    await expect.poll(() => distance(page)).toBeLessThan(before * 0.8);
    await checkBounds();
  } finally {
    await context.close();
  }
});
