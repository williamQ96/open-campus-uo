import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readFrontage(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const rankin = campus.terrainCheck(-512, 600.25);
    const road = campus.terrainCheck(-340.9, 610);
    return {
      buildings: campus.getState().buildings,
      west: Number.isFinite(
        campus.terrainCheck(-520, 600.32)["east-18th-west-paving"],
      ),
      rankinGap: rankin["pioneer-cemetery-paving"] - rankin.standing,
      road: road["rankin-frontage-paving"] ?? null,
      crossings: [
        [-321.42, 607.6],
        [-297.47, 608.6],
      ].map(
        ([e, z]) =>
          Number.isFinite(
            campus.terrainCheck(e, z)["hayward-square-track-ground"],
          ) && !campus.collisionCheck(e, z),
      ),
      poleBlocked: campus.collisionCheck(-321.5, 598.35),
      cornerOpen: !campus.collisionCheck(-321.18, 599.08),
      returns: [
        [-321.99, 625.5],
        [-290.18, 617.53],
      ].map(
        ([e, z]) =>
          Number.isFinite(
            campus.terrainCheck(e, z)["hayward-square-track-ground"],
          ) && !campus.collisionCheck(e, z),
      ),
    };
  });
}

test("the Rankin walk uses the visible grade and falls back with the frontage mesh", async ({
  page,
}) => {
  const frontage = await readFrontage(page);
  expect(frontage).toMatchObject({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    west: true,
    road: expect.any(Number),
    crossings: [true, true],
    poleBlocked: true,
    cornerOpen: true,
    returns: [true, true],
  });
  expect(Math.abs(frontage.rankinGap)).toBeLessThan(0.012);

  await page.route("**/rankin-frontage-review/site.glb", (route) =>
    route.fulfill({ body: "invalid Rankin frontage" }),
  );
  const fallback = await readFrontage(page);
  expect(fallback).toMatchObject({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    west: true,
    road: null,
    crossings: [true, true],
    poleBlocked: false,
    cornerOpen: true,
    returns: [true, true],
  });
  expect(fallback.rankinGap).toBeGreaterThan(0.09);
});

test("a lost University Street predecessor leaves the west site and cemetery sidewalk available", async ({
  page,
}) => {
  await page.route("**/university-south-axis-review/site.glb", (route) =>
    route.fulfill({ body: "invalid University Street geometry" }),
  );
  const fallback = await readFrontage(page);
  expect(fallback).toMatchObject({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    west: true,
    road: null,
  });
  expect(fallback.rankinGap).toBeGreaterThan(0.09);
});
