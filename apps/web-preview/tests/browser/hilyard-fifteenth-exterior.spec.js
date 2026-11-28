import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const buildings = {
  "roof-9bdc0828": "1515 Hilyard Apartments",
  "east-15th-740": "Treetop Apartments · 740 E 15th",
  "hilyard-1547-1549": "1547–1549 Hilyard Duplex",
};
const baseline = "/?exterior-review=hilyard-fifteenth-exterior-baseline";
const descriptorPath = "hilyard-fifteenth-exterior-review/site.json";

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
        [-869.7, 268.4],
        [-848.6, 270.3],
        [-889.5, 294],
        [-858.75, 274],
        [-853.0, 257.55],
        [-843.0, 257.55],
        [-848.45, 257.55],
      ].map(([x, z]) => campus.collisionCheck(x, z)),
    };
  }, Object.keys(buildings));
}

test("the three Hilyard buildings register independently and preserve the parking recess", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ buildings: -2, batched: 1 }));
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
    false,
    true,
  ]);
  expect(after.gates).toHaveLength(4);
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

test("a damaged split anchor restores the unsplit Hilyard source", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const descriptor = await (
    await page.request.get("/scene/" + descriptorPath)
  ).json();
  descriptor.batch_removals[0].source_vertices[0][1][0] += 1;
  const body = JSON.stringify(descriptor);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.hilyard_1515_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json });
  });
  await page.route("**/scene/" + descriptorPath, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
