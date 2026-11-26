import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const academic = "roof-b1c16a4e";
const residence = "roof-e3dcdde4";
const buildings = {
  [academic]:
    "Kellenberger Library · Lottie Price Music Building & Ross Evans Chapel",
  [residence]: "Burke-Griffeth Hall",
};
const baseline = "/?exterior-review=bushnell-east-exterior-baseline";
const descriptorPath = "bushnell-east-exterior-review/site.json";

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
        [-647, -216], // Music building
        [-651, -202.5], // Enclosed clock-entrance connector
        [-655.16, -203.51], // Entrance canopy support
        [-655.17, -202.16], // Passable between the two supports
        [-664, -203.2], // West approach
        [-669, -190], // Library's quadrangle wing
        [-724, -159.1], // Dining wing
        [-681, -145], // Residence wing
        [-671, -153.6], // Residence approach
        [-651, -155], // Gap between library and residence
      ].map(([e, south]) => campus.collisionCheck(e, south)),
    };
  }, Object.keys(buildings));
}

test("the East Quad restores the shared clock entrance and the residence with its dining wing", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 2 }));
  expect(before.names).toEqual({});
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(buildings);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.collision).toEqual([
    true,
    true,
    true,
    false,
    false,
    true,
    true,
    true,
    false,
    false,
  ]);
  expect(after.gates).toHaveLength(2);
  expect(
    after.gates.every(({ walkable, estimated }) => walkable && estimated),
  ).toBe(true);

  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [name, id] of [
    ["Kellenberger Library", academic],
    ["Lottie Price Music Building", academic],
    ["Ross Evans Chapel", academic],
    ["Burke-Griffeth Hall", residence],
  ]) {
    await search.fill(name);
    await search.press("Enter");
    await expect
      .poll(() =>
        page.evaluate(() => window.__campus.getState().selectedBuilding),
      )
      .toBe(id);
  }
});

test("a damaged second source anchor restores both East Quad source meshes", async ({
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
    json.bushnell_east_site.sha256 = sha256;
    await route.fulfill({ response, json });
  });
  await page.route("**/scene/" + descriptorPath, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
