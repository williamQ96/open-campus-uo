import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const homes = {
  "roof-bef4cf29": "1841 E 15th Ave",
  "roof-7dd08283": "1602 Villard St",
  "roof-e086d515": "1778 Villard St",
  "roof-9fdf719c": "1795 Moss St",
  "roof-fb6ac47a": "1800 Columbia St",
  "roof-6f41ba80": "1848 Moss St",
};
const baseline = "/?exterior-review=east-campus-housing-baseline";

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
      garage: __campus.collisionCheck(439.0, 585.0),
    };
  }, Object.keys(homes));
}

test("six campus homes keep their IDs and the detached garage has its own collision footprint", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 6, roofs: 1 }));
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(homes);
  expect(after.garage).toBe(true);
  expect(before.garage).toBe(false);
  expect(after.otherEntries).toEqual(before.otherEntries);
  expect(after.entries).toHaveLength(6);
  expect(
    after.entries.every(
      ({ gate, walkable }) => gate === "street-entry" && walkable,
    ),
  ).toBe(true);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(homes)) {
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

test("an invalid final East Campus anchor restores the six source ranges", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const descriptor = "east-campus-housing-exterior-review/site.json";
  const json = await (await page.request.get("/scene/" + descriptor)).json();
  json.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.58;
  const body = JSON.stringify(json);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.east_campus_housing_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await page.route("**/" + descriptor, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
