import { test, expect } from "@playwright/test";
import {
  BAILEY_PILOT_TREE_REMOVALS,
  DEFAULT_ENTRANCES,
  DEFAULT_PILOT_TREES,
} from "./exterior-counts.js";

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
  expect(installed.presentation.baileyOakCount).toBe(8);
  expect(installed.presentation.refinedPilotTrees).toBe(DEFAULT_PILOT_TREES);
  const clearances = await page.evaluate(() => {
    const roots = [
      [-562.132, 99.868],
      [-562.38, 118.231],
      [-562.456, 148.903],
      [-562.152, 167.154],
      [-532.822, 166.872],
      [-533.155, 149.123],
      [-532.79, 118.426],
      [-532.698, 99.552],
    ];
    return {
      trees: roots.map(([x, z]) => window.__campus.collisionCheck(x, z)),
      sideWalk: [99.552, 118.426, 149.123, 166.872].map((z) =>
        window.__campus.collisionCheck(-529.2, z),
      ),
    };
  });
  expect(clearances.trees).toEqual(Array(8).fill(true));
  expect(clearances.sideWalk).toEqual(Array(4).fill(false));
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
  expect(fallback.presentation.baileyOakCount).toBe(0);
  expect(fallback.presentation.refinedPilotTrees).toBe(
    DEFAULT_PILOT_TREES + BAILEY_PILOT_TREE_REMOVALS,
  );
  expect(
    await page.evaluate(() => window.__campus.collisionCheck(-562.132, 99.868)),
  ).toBe(false);
  expect(fallback.roadSegments).toBe(139);
  expect(fallback.roadSurfaces).toBe(2);
  expect(fallback.entranceCount).toBe(DEFAULT_ENTRANCES);
  const walker = fallback.life.entities.find(({ id }) => id === "walk-0");
  expect(walker.position.east).toBe(-552);
});
