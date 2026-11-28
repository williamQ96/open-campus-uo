import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const directory = "fairmount-residential-exterior-review";
const baseline = "/?exterior-review=fairmount-residential-exterior-baseline";
const houses = {
  "roof-41f5448c": "1705 Fairmount Blvd",
  "roof-57f699be": "1799 Fairmount Blvd",
  "roof-8aa49f9b": "1834 Fairmount Blvd",
  "roof-e057643a": "1892 Fairmount Blvd",
  "roof-7bb19f64": "1925 Fairmount Blvd",
  "roof-72b4d323": "2055 Fairmount Blvd",
  "roof-78a95ac1": "2094 Fairmount Blvd",
};

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
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
      otherEntries: entries.filter(({ id }) => !ids.includes(id)),
      overhang: __campus.collisionCheck(827.7707, 603.0138),
      underBalcony: __campus.collisionCheck(682.8143, 707.9363),
      balconyPosts: [
        __campus.collisionCheck(684.0285, 705.7395),
        __campus.collisionCheck(681.6002, 710.1331),
      ],
    };
  }, Object.keys(houses));
}

test("the additional Fairmount homes retain their IDs, entry routes and open covered areas", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 7 }));
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(houses);
  expect(after.otherEntries).toEqual(before.otherEntries);
  expect(after.entries).toHaveLength(7);
  expect(
    after.entries.every(
      ({ gate, walkable }) => gate === "street-entry" && walkable,
    ),
  ).toBe(true);
  expect(before.overhang).toBe(true);
  expect(after.overhang).toBe(false);
  expect(after.underBalcony).toBe(false);
  expect(after.balconyPosts).toEqual([true, true]);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(houses)) {
    await search.fill(name);
    if (isBackgroundBuilding(id)) {
      await expect(page.getByRole("option", { name, exact: true })).toHaveCount(
        0,
      );
      continue;
    }
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

test("a shifted final source range restores all seven Fairmount source meshes", async ({
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
    config.fairmount_residential_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await page.route("**/" + path, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
