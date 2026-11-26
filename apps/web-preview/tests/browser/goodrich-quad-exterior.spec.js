import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const buildings = {
  "bushnell-facilities-1125": "Bushnell Facilities & Maintenance",
  "roof-fd7ba44a": "Goodrich Hall",
  "roof-ca96d4a8": "1145 Alder Building",
};
const baseline = "/?exterior-review=goodrich-quad-exterior-baseline";
const descriptorPath = "goodrich-quad-exterior-review/site.json";

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
        [-738, -212], // Bell tower base
        [-716, -217], // Historic hall
        [-746, -214], // West sidewalk
        [-735.1, -197.26], // Open facilities porch
        [-735.82, -193.01], // Porch masonry support
        [-729, -197], // Facilities building
        [-728, -178], // 1145 Alder masonry building
        [-728, -187], // Gap between the independent buildings
      ].map(([e, south]) => campus.collisionCheck(e, south)),
    };
  }, Object.keys(buildings));
}

test("Goodrich, Bushnell Facilities and 1145 Alder preserve the open porch and separate volumes", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ buildings: -1, batched: 2 }));
  expect(before.names).toEqual({});
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(buildings);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.collision).toEqual([
    true,
    true,
    false,
    false,
    true,
    true,
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
    await search.press("Enter");
    await expect
      .poll(() =>
        page.evaluate(() => window.__campus.getState().selectedBuilding),
      )
      .toBe(id);
  }
});

test("a damaged second source anchor restores the two candidates and removes the addition", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const descriptor = await (
    await page.request.get("/scene/" + descriptorPath)
  ).json();
  descriptor.batch_removals[1].source_vertices[0][1][0] += 1;
  const body = JSON.stringify(descriptor);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.goodrich_quad_site.sha256 = sha256;
    await route.fulfill({ response, json });
  });
  await page.route("**/scene/" + descriptorPath, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
