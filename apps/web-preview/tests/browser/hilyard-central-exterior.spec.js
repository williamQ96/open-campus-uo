import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const buildings = {
  "roof-9feed235": "Hilyard Apartments · 957 Hilyard",
  "hilyard-apartments-971": "Hilyard Apartments · 971 Hilyard",
  "roof-eab27ea2": "975 Hilyard St",
};
const baseline = "/?exterior-review=hilyard-central-exterior-baseline";
const descriptorPath = "hilyard-central-exterior-review/site.json";

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
        [-851.3, -411.2],
        [-853, -395.7],
        [-855, -379.5],
        [-853, -403.8],
        [-854.5, -388.6],
        [-880, -389],
      ].map(([x, z]) => campus.collisionCheck(x, z)),
    };
  }, Object.keys(buildings));
}

test("the three Hilyard exteriors retain clear courtyards and the 973 approach", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(
    exteriorCounts({ buildings: -1, batched: 2, roofs: 1 }),
  );
  expect(before.names).toEqual({});
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(buildings);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.collision).toEqual([true, true, true, false, false, true]);
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

test("a damaged second source anchor restores both original Hilyard candidates", async ({
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
    json.hilyard_central_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json });
  });
  await page.route("**/scene/" + descriptorPath, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
