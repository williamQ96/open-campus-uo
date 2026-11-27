// SPDX-License-Identifier: Apache-2.0
import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readCourt(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const point = (east, north) => {
      const h = campus.terrainCheck(east, -north);
      return {
        terrace: h["price-courtyard-terrace"] ?? null,
        onyx: h["onyx-green-walks"] ?? null,
        standing: h.standing,
        blocked: campus.collisionCheck(east, -north),
      };
    };
    return {
      buildings: campus.getState().buildings,
      south: point(-193.95, 77.15),
      west: point(-197.1, 95.1),
      court: point(-192.45, 89),
      rail: point(-195.81, 95.1),
      junction: point(-200.27, 69.7),
    };
  });
}

test("the Price courtyard has an upper walk and a protected lower level", async ({
  page,
}) => {
  const current = await readCourt(page);
  expect(current.buildings).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  for (const probe of [current.south, current.west]) {
    expect(probe.terrace).toBeGreaterThan(1.2);
    expect(probe.standing).toBeCloseTo(probe.terrace, 2);
    expect(probe.blocked).toBe(false);
  }
  expect(current.court).toMatchObject({ blocked: true, terrace: null });
  expect(current.rail.blocked).toBe(true);

  await page.route("**/price-courtyard-review/site.glb", (route) =>
    route.fulfill({ body: "damaged Price courtyard" }),
  );
  const prior = await readCourt(page);
  expect(prior.buildings).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(prior.south.terrace).toBeNull();
  expect(prior.west.terrace).toBeNull();
  expect(prior.court.blocked).toBe(false);
  expect(prior.rail.blocked).toBe(false);
  expect(prior.junction.onyx).toBeCloseTo(current.junction.onyx, 4);
});

for (const [title, asset] of [
  ["Onyx Green predecessor", "onyx-green-walks-review/site.glb"],
  ["pinned foundation", "landcover-l2/ground.glb"],
]) {
  test(`Price courtyard rolls back without the ${title}`, async ({ page }) => {
    await page.route(`**/${asset}`, (route) =>
      route.fulfill({ body: "damaged courtyard prerequisite" }),
    );
    const prior = await readCourt(page);
    expect(prior.buildings).toBe(DEFAULT_SELECTABLE_BUILDINGS);
    expect(prior.south.terrace).toBeNull();
    expect(prior.west.terrace).toBeNull();
    expect(prior.court.blocked).toBe(false);
  });
}
