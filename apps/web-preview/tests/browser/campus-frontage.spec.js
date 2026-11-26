import { createHash } from "node:crypto";
import { test, expect } from "@playwright/test";
import {
  DEFAULT_BATCHED_BUILDINGS,
  DEFAULT_SELECTABLE_BUILDINGS,
} from "./exterior-counts.js";

const buildings = {
  "roof-29dae856": "University Health Services",
  "roof-2518e2a2": "Central Power Station",
  "roof-5fd54bd8": "Riley Hall",
  "roof-a55aea46": "Student Tennis Center",
  "roof-ee63827c": "Alder Building",
};

async function frontageState(page, url) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const current = __campus.getState();
    return {
      buildings: current.buildings,
      batches: current.presentation.batchedBuildings,
      roads: current.roadSegments,
      gates: __campus.entranceInfo().filter(({ id }) => ids.includes(id)),
      names: Object.fromEntries(
        __campus
          .namedBuildings()
          .filter(({ id }) => ids.includes(id))
          .map(({ id, name }) => [id, name]),
      ),
      collision: [
        [21, 26],
        [52, 30],
        [57, 51],
        [-275, -322],
        [-271, -349],
        [-990, -216],
        [-978, -226],
        [-192, 440],
        [-217, 444],
        [-724, 263],
        [-725.55, 259.61],
        [-724, 259.5],
      ].map(([x, z]) => __campus.collisionCheck(x, z)),
    };
  }, Object.keys(buildings));
}

test("five registered frontages keep their IDs and preserve open courtyards and porch", async ({
  page,
}) => {
  const state = await frontageState(page, "/");
  expect([state.buildings, state.batches, state.roads]).toEqual([
    DEFAULT_SELECTABLE_BUILDINGS,
    DEFAULT_BATCHED_BUILDINGS,
    139,
  ]);
  expect(state.names).toEqual(buildings);
  expect(state.gates).toHaveLength(6);
  expect(state.gates.every(({ gate, walkable }) => gate && walkable)).toBe(
    true,
  );
  expect(state.collision).toEqual([
    true,
    false,
    false,
    true,
    true,
    false,
    true,
    true,
    false,
    true,
    true,
    false,
  ]);
});

test("a late invalid batch anchor restores the earlier frontages and entrances", async ({
  page,
}) => {
  const baseline = await frontageState(
    page,
    "/?exterior-review=campus-frontage-baseline",
  );
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    const siteUrl = new URL(config.campus_frontage_site.url, response.url())
      .href;
    const site = await (await page.request.get(siteUrl)).json();
    site.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.85;
    const body = JSON.stringify(site);
    config.campus_frontage_site.sha256 = createHash("sha256")
      .update(body)
      .digest("hex");
    await page.route(siteUrl, (siteRoute) =>
      siteRoute.fulfill({
        body,
        contentType: "application/json",
      }),
    );
    await route.fulfill({ response, json: config });
  });
  expect(await frontageState(page, "/")).toEqual(baseline);
});
