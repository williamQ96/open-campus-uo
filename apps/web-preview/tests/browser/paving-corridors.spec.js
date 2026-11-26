import { test, expect } from "@playwright/test";
import { DEFAULT_ENTRANCES } from "./exterior-counts.js";

const state = (page) => page.evaluate(() => window.__campus.getState());

test("the refined Quad and 139 corridor features load with active campus routing", async ({
  page,
}) => {
  const asset = page.waitForResponse((response) =>
    response.url().endsWith("/scene/paving-corridors-l2/surfaces.glb"),
  );
  await page.goto("/");
  expect((await asset).status()).toBe(200);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const installed = await state(page);
  expect(installed.roadSurfaces).toBe(2);
  expect(installed.roadSegments).toBe(139);
  expect(installed.presentation.refinedPavingCorridors).toEqual({
    corridors: 139,
    quad: true,
  });
  for (const id of ["walk-0", "bicycle-0", "scooter-0"]) {
    const actor = installed.life.entities.find((actor) => actor.id === id);
    expect(actor.path.id).toBe("sidewalk-0-0");
    expect(actor.position.east).toBeLessThan(-560);
  }
  await page.locator("#directions-open").click();
  for (const [endpoint, name] of [
    ["A", "Condon Hall"],
    ["B", "Knight Library"],
  ]) {
    await page
      .getByRole("button", { name: `Search ${endpoint}`, exact: true })
      .click();
    const input = page.getByRole("combobox");
    await input.fill(name);
    await input.press("ArrowDown");
    await input.press("Enter");
  }
  await page.locator("#route-start").click();
  const route = (await state(page)).navigation;
  expect(route.points.length).toBeGreaterThan(5);
  expect(route.b.label).toContain("Knight Library");
});

test("a damaged surface bundle keeps the previous paving, routes and base ground", async ({
  page,
}) => {
  await page.route("**/scene/paving-corridors-l2/surfaces.glb", (route) =>
    route.fulfill({ status: 200, body: "damaged" }),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const fallback = await state(page);
  expect(fallback.presentation.landcoverLevel).toBe(2);
  expect(fallback.presentation.refinedPavingCorridors).toBeUndefined();
  expect(fallback.roadSegments).toBe(139);
  expect(fallback.roadSurfaces).toBe(2);
  expect(fallback.entranceCount).toBe(DEFAULT_ENTRANCES);
  const walker = fallback.life.entities.find(({ id }) => id === "walk-0");
  expect(walker.position.east).toBe(-552);
});
