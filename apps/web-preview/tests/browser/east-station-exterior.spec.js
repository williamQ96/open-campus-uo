import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const buildings = {
  "roof-ce1d33a1": "UOPD East Station Annex A",
  "roof-4cf339e8": "UO Police Department East Station",
  "roof-38958a7f": "UOPD East Station Annex B",
};
const baseline = "/?exterior-review=east-station-exterior-baseline";
const descriptorPath = "east-station-exterior-review/site.json";

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const campus = window.__campus;
    const { buildings, presentation } = campus.getState();
    const named = campus.namedBuildings().filter(({ id }) => ids.includes(id));
    const gates = campus.entranceInfo();
    return {
      counts: [
        buildings,
        presentation.batchedBuildings,
        presentation.refinedContextRoofs,
      ],
      names: Object.fromEntries(named.map(({ id, name }) => [id, name])),
      gates: gates.filter(({ id }) => ids.includes(id)),
      neighbors: gates.filter(({ id }) => !ids.includes(id)),
      collision: [
        [793.0, 215], // Main body
        [791.28, 230.89], // Clear center of the canopy
        [789.82, 230.84], // Main canopy post
        [791.28, 233.6], // Public-side forecourt
        [834.0, 193], // Annex A
        [832.5, 209], // Setback between the near buildings
        [832.2, 132.7], // Annex B
        [832.2, 148], // Outdoor gap between the annexes
      ].map(([e, south]) => campus.collisionCheck(e, south)),
    };
  }, Object.keys(buildings));
}

test("the three East Station exteriors are searchable with independent footprints and a clear front porch", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 3 }));
  expect(before.names).toEqual({});
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(buildings);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.collision).toEqual([
    true,
    false,
    true,
    false,
    true,
    false,
    true,
    false,
  ]);
  expect(after.gates).toHaveLength(3);
  expect(
    after.gates.every(({ walkable, estimated }) => walkable && estimated),
  ).toBe(true);

  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(buildings)) {
    await search.fill(name);
    if (isBackgroundBuilding(id)) {
      await expect(page.getByRole("option", { name, exact: true })).toHaveCount(
        0,
      );
      continue;
    }
    await search.press("Enter");
    await expect
      .poll(() =>
        page.evaluate(() => window.__campus.getState().selectedBuilding),
      )
      .toBe(id);
  }
});

test("a damaged last source anchor restores all three preceding volumes", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const descriptor = await (
    await page.request.get("/scene/" + descriptorPath)
  ).json();
  descriptor.batch_removals[2].source_vertices[0][1][0] += 1;
  const body = JSON.stringify(descriptor);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.east_station_site.sha256 = sha256;
    await route.fulfill({ response, json });
  });
  await page.route("**/scene/" + descriptorPath, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
