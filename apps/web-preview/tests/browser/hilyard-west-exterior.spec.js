import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const directory = "hilyard-west-exterior-review";
const baseline = "/?exterior-review=hilyard-west-exterior-baseline";
const dependentDistrict = ["roof-62a81026", "roof-19858777", "roof-bdbcb4fc"];
const names = {
  "roof-a3d5625f": "Catherine Cornwall Townhouses",
  "roof-ca59da4d": "Hilyard House",
  "roof-dcc94271": "Campus Studios",
  "roof-ae986c58": "Bushnell University · 722 E 11th Ave",
};

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(
    ({ ids, dependentIds }) => {
      const { buildings, presentation } = __campus.getState();
      const entries = __campus.entranceInfo();
      return {
        counts: [
          buildings,
          presentation.batchedBuildings,
          presentation.refinedContextRoofs,
        ],
        names: Object.fromEntries(
          __campus
            .namedBuildings()
            .filter(({ id }) => ids.includes(id))
            .map(({ id, name }) => [id, name]),
        ),
        entries: entries.filter(({ id }) => ids.includes(id)),
        otherEntries: entries.filter(
          ({ id }) => !ids.includes(id) && !dependentIds.includes(id),
        ),
        openSpaces: [
          [-880.1755, 82.9155],
          [-876.9664, 105.0442],
          [-947.1785, -379.0058],
          [-846.375, 98.9088],
          [-846.4197, 74.4088],
        ].map(([x, z]) => !__campus.collisionCheck(x, z)),
      };
    },
    { ids: Object.keys(names), dependentIds: dependentDistrict },
  );
}

test("the L2 models retain the open courtyard, covered parking and four approaches", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  // Disabling the 722 model also restores the dependent University District batch.
  expect(before.counts).toEqual(exteriorCounts({ batched: 7 }));
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.otherEntries).toEqual(before.otherEntries);
  expect(after.names).toEqual(names);
  expect(before.openSpaces[0]).toBe(false);
  expect(after.openSpaces).toEqual(Array(5).fill(true));
  expect(after.entries).toHaveLength(4);
  expect(after.entries.every(({ walkable }) => walkable)).toBe(true);
  const stairs = after.entries.find(({ id }) => id === "roof-a3d5625f");
  expect(stairs).toMatchObject({ gate: "west-stair", snapToFacade: false });
  // The rendered entry marker sits 0.14 m outward of the authored stair edge.
  expect(
    Math.hypot(
      stairs.approach[0] - stairs.position[0],
      stairs.approach[1] - stairs.position[1],
    ),
  ).toBeCloseTo(4.7, 4);

  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, query] of Object.entries(names)) {
    await search.fill(query);
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

test("a changed last batch anchor keeps the four original exterior selections", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const path = directory + "/site.json";
  const item = await (await page.request.get("/scene/" + path)).json();
  item.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.58;
  const body = JSON.stringify(item);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.hilyard_west_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await page.route("**/" + path, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
