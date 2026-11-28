// SPDX-License-Identifier: Apache-2.0
import { expect, test } from "@playwright/test";
import buildingScope from "../../data/building-scope.json" with { type: "json" };

const measure = (a, b) => Math.hypot(...a.map((value, i) => value - b[i]));
const state = (page) =>
  page.evaluate(
    () => window.__campus?.getState() ?? window.__campusPreview?.getState(),
  );

async function expectCameraReadout(page) {
  await expect(async () => {
    await checkCameraReadout(page);
  }).toPass({ timeout: 8000 });
}

async function checkCameraReadout(page) {
  const result = await page.evaluate(() => {
    const { camera, cameraDirection, orbitTarget, view } = (
      window.__campus ?? window.__campusPreview
    ).getState();
    const coordinates = ([e, h, south]) =>
      `E ${e.toFixed(1)} N ${(-south).toFixed(1)} H ${h.toFixed(1)} m`;
    const [east, up, south] = cameraDirection;
    return {
      pose: document.querySelector("#camera-pose").textContent,
      position: coordinates(camera),
      heading: (Math.atan2(east, -south) * 180) / Math.PI,
      pitch: (Math.atan2(up, Math.hypot(east, south)) * 180) / Math.PI,
      orbit: document.querySelector("#camera-orbit").textContent,
      target: coordinates(orbitTarget),
      view,
      range: Math.hypot(...camera.map((value, i) => value - orbitTarget[i])),
    };
  });
  expect(result.pose).toContain(`CAM ${result.position}`);
  const heading = Number(result.pose.match(/HDG ([\d.]+)°/)[1]);
  expect(Math.abs(((heading - result.heading + 540) % 360) - 180)).toBeLessThan(
    0.051,
  );
  const pitch = Number(result.pose.match(/PITCH (-?[\d.]+)°/)[1]);
  expect(Math.abs(pitch - result.pitch)).toBeLessThan(0.051);
  if (result.view === "aerial") {
    expect(result.orbit).toBe(
      `TARGET ${result.target} · RANGE ${result.range.toFixed(1)} m`,
    );
  } else {
    expect(result.orbit).toBe("");
  }
}

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
  // This building has no mesh in the original full-scene model.
  await page.route("**/education-annex-review/site.glb", (route) =>
    route.fulfill({ status: 404 }),
  );
  await page.goto("/", { waitUntil: "commit" });
  await expect(page.locator("#app")).toHaveAttribute("data-stage", "overview");
  await expect(page.locator("#camera-readout")).toBeVisible();
  await expectCameraReadout(page);
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
  await expectCameraReadout(page);
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
  expect(complete.buildings + complete.fallbackBuildingIds.length).toBe(611);
  expect(complete.fallbackBuildingIds).toEqual(["uo-education-annex"]);
  expect(
    await page.evaluate(() => __campus.collisionCheck(-601.7, 414.9)),
  ).toBe(true);
  expect(measure(moved.orbitTarget, complete.orbitTarget)).toBeLessThan(3);
  expect(measure(moved.camera, complete.camera)).toBeLessThan(4);
  await expectCameraReadout(page);
  await expect(page.locator("[data-view=first]")).toBeEnabled();
  await expect(page.locator("#directions-open")).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.locator("#camera-readout")).toBeInViewport();
  for (const view of ["first", "third"]) {
    await page.locator(`button[data-view=${view}]`).click();
    await expect(page.locator("#camera-orbit")).toBeEmpty();
    await expectCameraReadout(page);
  }
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
  const excluded = new Set(ids);
  expect(names.filter((id) => excluded.has(id))).toEqual([]);
  const labels = await page
    .locator(".building-label")
    .evaluateAll((nodes) => nodes.map((node) => node.dataset.buildingId));
  expect(labels.filter((id) => excluded.has(id))).toEqual([]);
  expect(await page.evaluate(() => __campus.collisionCheck(-890, -454))).toBe(
    true,
  );
  expect(names).toEqual(
    expect.arrayContaining(["context-oc-hayward", "roof-b8fa3497"]),
  );
  for (const name of [
    "The Maverick Hotel",
    "Rainier Building",
    "The Rive Eugene",
  ]) {
    const search = page.locator("#building-search-input");
    await search.fill(name);
    await expect(page.getByRole("option", { name, exact: true })).toHaveCount(
      0,
    );
    await search.press("Enter");
    expect((await state(page)).selectedBuilding).toBeNull();
  }
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
    await expectCameraReadout(page);
  }
});
