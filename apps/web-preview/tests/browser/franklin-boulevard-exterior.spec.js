import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const buildings = {
  "roof-5e02b3d2": "1675 Franklin Blvd",
  "roof-fd64edbd": "1809 Franklin Blvd",
  "roof-1587e3e1": "1895 Franklin Blvd",
  "roof-b1290409": "1917 Franklin Blvd",
  "roof-0dc3fa8a": "1933 Franklin Blvd",
  "roof-4b8868e0": "2091 Franklin Blvd",
};
const baseline = "/?exterior-review=franklin-boulevard-exterior-baseline";

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const s = __campus.getState();
    const entries = __campus.entranceInfo();
    return {
      counts: [
        s.buildings,
        s.presentation.batchedBuildings,
        s.presentation.refinedContextRoofs,
      ],
      names: Object.fromEntries(
        __campus
          .namedBuildings()
          .filter(({ id }) => ids.includes(id))
          .map(({ id, name }) => [id, name]),
      ),
      entries: entries.filter(({ id }) => ids.includes(id)),
      otherEntries: entries.filter(({ id }) => !ids.includes(id)),
    };
  }, Object.keys(buildings));
}

test("six Franklin Boulevard exteriors keep their IDs and walkable approaches", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 6 }));
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(buildings);
  expect(after.otherEntries).toEqual(before.otherEntries);
  expect(after.entries).toHaveLength(6);
  expect(
    after.entries.every(
      ({ gate, walkable }) => gate === "street-entry" && walkable,
    ),
  ).toBe(true);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(buildings)) {
    await search.fill(name);
    if (isBackgroundBuilding(id)) {
      await expect(
        page.getByRole("option").filter({ hasText: name }),
      ).toHaveCount(0);
      continue;
    }
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

test("an invalid final Franklin anchor restores all six source ranges", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const descriptor = "franklin-boulevard-exterior-review/site.json";
  const json = await (await page.request.get("/scene/" + descriptor)).json();
  json.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.58;
  const body = JSON.stringify(json);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.franklin_boulevard_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await page.route("**/" + descriptor, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});

test("2091 Franklin keeps both passages open around the fuel canopy supports", async ({
  page,
}) => {
  await inspect(page);
  const collisions = await page.evaluate(async () => {
    const site = await fetch(
      "/scene/franklin-boulevard-exterior-review/site.json",
    ).then((response) => response.json());
    const station = site.buildings.find(({ id }) => id === "roof-4b8868e0");
    const points = station.support_collision_enu_m.map((ring) => {
      const edges = ring.slice(0, -1);
      return edges.reduce(
        ([east, north], [x, y]) => [
          east + x / edges.length,
          north + y / edges.length,
        ],
        [0, 0],
      );
    });
    const [east, north] = points[1];
    // The recorded canopy is 8 m wide. Sample both lanes beside the column.
    const lanes = [-2.35, 2.35].map((offset) =>
      __campus.collisionCheck(
        east + offset * 0.9538,
        -(north - offset * 0.3005),
      ),
    );
    const columns = points.map(([x, y]) => __campus.collisionCheck(x, -y));
    return { lanes, columns };
  });
  expect(collisions).toEqual({ lanes: [false, false], columns: [true, true] });
});
