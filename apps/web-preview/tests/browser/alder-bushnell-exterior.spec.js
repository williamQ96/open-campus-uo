import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const buildings = {
  "alder-suites-950": "Alder Suites",
  "roof-e45bcd54": "Morse Center",
  "roof-b98e8e3e": "Pomajevich Hall",
};
const baseline = "/?exterior-review=alder-bushnell-exterior-baseline";
const descriptorPath = "alder-bushnell-exterior-review/site.json";

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
        [-771.0, -420.0],
        [-815.9, -413.62],
        [-813.7, -414.62],
        [-807.7, -416.6],
        [-757.0, -291.8],
        [-773.0, -293.0],
        [-724.0, -290.0],
        [-765.0, -288.53],
      ].map(([e, south]) => campus.collisionCheck(e, south)),
    };
  }, Object.keys(buildings));
}

test("the missing Alder Suites is registered with two Bushnell exteriors and clear parking", async ({
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
    false,
    true,
    true,
    true,
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
    json.alder_bushnell_site.sha256 = sha256;
    await route.fulfill({ response, json });
  });
  await page.route("**/scene/" + descriptorPath, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
