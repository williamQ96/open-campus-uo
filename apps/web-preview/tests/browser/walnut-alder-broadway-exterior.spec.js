import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const buildings = {
  "roof-b3b290df": "Transportation Services",
  "roof-8fea5de9": "968 Alder Apartments",
  "roof-31cf5cf8": "Former Motel 66 Entrance · July 2024",
};
const baseline = "/?exterior-review=walnut-alder-broadway-exterior-baseline";
const descriptorPath = "walnut-alder-broadway-exterior-review/site.json";

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
        [770.0, 123.0],
        [-815.0, -398.0],
        [-855.0, -511.0],
        [-841.25, -511.05],
        [-841.75, -514.43],
        [-845.15, -508.0],
        [-845.15, -511.7],
        [-845.15, -515.2],
      ].map(([e, south]) => campus.collisionCheck(e, south)),
    };
  }, Object.keys(buildings));
}

test("the three exteriors are searchable and the motel drive-through is open", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 3, roofs: 2 }));
  expect(before.names).toEqual({});
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(buildings);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.collision).toEqual([
    true,
    true,
    true,
    true,
    true,
    false,
    false,
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

test("a damaged third source anchor restores all three original exteriors", async ({
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
    json.walnut_alder_broadway_site.sha256 = sha256;
    await route.fulfill({ response, json });
  });
  await page.route("**/scene/" + descriptorPath, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
