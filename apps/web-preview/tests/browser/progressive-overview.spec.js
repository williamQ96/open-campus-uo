// SPDX-License-Identifier: Apache-2.0
import { expect, test } from "@playwright/test";
import buildingScope from "../../data/building-scope.json" with { type: "json" };

const measure = (a, b) => Math.hypot(...a.map((value, i) => value - b[i]));
const state = (page) =>
  page.evaluate(
    () => window.__campus?.getState() ?? window.__campusPreview?.getState(),
  );

async function drag(page, x, y, dx, dy, button = "right") {
  await page.mouse.move(x, y);
  await page.mouse.down({ button });
  await page.mouse.move(x + dx, y + dy, { steps: 5 });
  await page.mouse.up({ button });
}

test("the first map accepts gestures and the detail queue completes away from its starting view", async ({
  page,
}) => {
  test.setTimeout(120_000);
  const requests = [];
  page.on("request", (req) => {
    if (req.url().endsWith("/site.json")) requests.push(req.url());
  });
  let unblock;
  const pending = new Promise((resolve) => (unblock = resolve));
  // Delay only the first detailed requests and retain the original browser origin.
  await page.route("**/scene/*/site.json", async (route) => {
    await pending;
    await route.continue();
  });
  // This scenery-only package can fail without removing a registered building.
  await page.route("**/old-campus-quad-landscape-review/site.glb", (route) =>
    route.fulfill({ status: 404 }),
  );
  await page.goto("/", { waitUntil: "commit" });
  await expect(page.locator("#app")).toHaveAttribute("data-stage", "overview");
  await expect(page.locator("[data-view=first]")).toBeDisabled();
  await expect(page.locator("#directions-open")).toBeHidden();
  await expect.poll(() => requests.length).toBeGreaterThan(0);
  const initial = await state(page);
  expect(initial.detailQueue.total).toBeGreaterThan(100);
  await drag(page, 550, 450, 230, 150);
  await expect
    .poll(async () =>
      measure(initial.orbitTarget, (await state(page)).orbitTarget),
    )
    .toBeGreaterThan(10);
  // Move again after the queue has started, leaving its original area.
  await drag(page, 550, 450, -240, 75, "left");
  await expect
    .poll(async () =>
      measure(initial.cameraDirection, (await state(page)).cameraDirection),
    )
    .toBeGreaterThan(0.25);
  await page.waitForFunction(
    () => {
      const { camera, orbitTarget } = window.__campusPreview.getState();
      const position = [...camera, ...orbitTarget];
      const previous = window.__previousOverviewPose;
      window.__previousOverviewPose = position;
      return (
        previous &&
        Math.hypot(...position.map((value, i) => value - previous[i])) < 0.03
      );
    },
    null,
    { timeout: 20000 },
  );
  const moved = await state(page);
  unblock();
  await expect(page.locator("#app")).toHaveAttribute("data-stage", "detail", {
    timeout: 85_000,
  });
  const complete = await state(page);
  expect(requests.length).toBeGreaterThan(100);
  expect(complete.detailQueue).toEqual({
    total: initial.detailQueue.total,
    settled: initial.detailQueue.total,
  });
  expect(complete.buildings).toBe(611);
  expect(measure(moved.orbitTarget, complete.orbitTarget)).toBeLessThan(3);
  expect(measure(moved.camera, complete.camera)).toBeLessThan(4);
  await expect(page.locator("[data-view=first]")).toBeEnabled();
  await expect(page.locator("#directions-open")).toBeVisible();
});

test("an excluded building keeps its physical model while the directory is filtered", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "commit" });
  await expect(page.locator("#app")).toHaveAttribute("data-stage", "detail", {
    timeout: 85_000,
  });
  const ids = Object.keys(buildingScope.backgroundOnly);
  expect((await state(page)).buildings).toBe(611);
  expect((await state(page)).backgroundBuildings).toBe(ids.length);
  const names = await page.evaluate(() =>
    window.__campus.selectableBuildingIds(),
  );
  for (const id of ids) {
    expect(names).not.toContain(id);
    await expect(page.locator(`[data-building-id="${id}"]`)).toHaveCount(0);
  }
  expect(names).toContain("roof-b8f94f8e");
  await page.locator("#building-search-input").fill("The Maverick Hotel");
  await expect(page.getByRole("option", { name: /Maverick/ })).toHaveCount(0);
});

test("Overview pans across labels and keeps wheel zoom and left rotation responsive", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "commit" });
  await expect(page.locator("#app")).toHaveAttribute("data-stage", "detail", {
    timeout: 85_000,
  });
  for (let step = 0; step < 3; step++) {
    const initial = await state(page);
    await drag(page, 604, 704 - step * 35, -46, 15);
    await expect
      .poll(async () =>
        measure(initial.orbitTarget, (await state(page)).orbitTarget),
      )
      .toBeGreaterThan(4);
    const label = await page.evaluate(() => {
      for (const item of document.querySelectorAll(
        ".building-label:not([hidden])",
      )) {
        const r = item.getBoundingClientRect();
        const x = r.x + r.width / 2,
          y = r.y + r.height / 2;
        if (
          x > 360 &&
          x < 1110 &&
          y > 210 &&
          y < 690 &&
          document.elementFromPoint(x, y) === item
        )
          return [x, y];
      }
      return null;
    });
    expect(label).toBeTruthy();
    const beforeZoom = await state(page);
    const radius = measure(beforeZoom.orbitTarget, beforeZoom.camera);
    await page.mouse.move(...label);
    await page.mouse.wheel(0, -360);
    await expect
      .poll(async () => {
        const zoom = await state(page);
        return measure(zoom.orbitTarget, zoom.camera) / radius;
      })
      .toBeLessThan(0.9);
    const zoom = await state(page);
    const panOverLabel = await page.evaluate(() => {
      const element = [
        ...document.querySelectorAll(".building-label:not([hidden])"),
      ]
        .map((item) => {
          const r = item.getBoundingClientRect();
          return [item, r.x + r.width / 2, r.y + r.height / 2];
        })
        .find(
          ([item, x, y]) =>
            x > 360 &&
            x < 1110 &&
            y > 210 &&
            y < 690 &&
            document.elementFromPoint(x, y) === item,
        );
      return element?.slice(1) ?? null;
    });
    expect(panOverLabel).toBeTruthy();
    await drag(page, ...panOverLabel, 65, -32);
    await expect
      .poll(async () =>
        measure(zoom.orbitTarget, (await state(page)).orbitTarget),
      )
      .toBeGreaterThan(4);
    const panned = await state(page);
    expect(panned.selectedBuilding).toBeNull();
    await drag(page, 650, 738, 45, -14, "left");
    await expect
      .poll(async () =>
        measure(panned.cameraDirection, (await state(page)).cameraDirection),
      )
      .toBeGreaterThan(0.04);
  }
});
