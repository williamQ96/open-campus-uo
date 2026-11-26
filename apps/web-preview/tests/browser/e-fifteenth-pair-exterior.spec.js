import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const buildings = {
  "roof-0c745864": "E 15th Apartments · Street Building",
  "east-fifteenth-alley-apartments": "E 15th Apartments · Alley Building",
};
const baseline = "/?exterior-review=e-fifteenth-pair-exterior-baseline";
const descriptorPath = "e-fifteenth-pair-exterior-review/site.json";

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
        [-831.6, 269],
        [-819.4, 270],
        [-829, 288],
        [-819, 288],
        [-832.4, 256.13],
        [-818, 256.13],
        [-825.4, 254.95],
        [-824.2, 281.42],
        [-823.32, 294.3],
      ].map(([x, z]) => campus.collisionCheck(x, z)),
    };
  }, Object.keys(buildings));
}

test("the E 15th pair restores the alley building and leaves the parking and court clear", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ buildings: -1, batched: 1 }));
  expect(before.names).toEqual({});
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(buildings);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.collision).toEqual([
    true,
    true,
    true,
    true,
    false,
    false,
    true,
    false,
    false,
  ]);
  expect(after.gates).toHaveLength(2);
  expect(
    after.gates.every(
      ({ walkable, estimated, snapToFacade }) =>
        walkable && estimated && snapToFacade === false,
    ),
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

test("a mismatched source anchor drops the added alley building and restores the street volume", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const descriptor = await (
    await page.request.get("/scene/" + descriptorPath)
  ).json();
  descriptor.batch_removals[0].source_vertices[2][1][0] += 1;
  const body = JSON.stringify(descriptor);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.e_fifteenth_pair_site.sha256 = sha256;
    await route.fulfill({ response, json });
  });
  await page.route("**/scene/" + descriptorPath, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
