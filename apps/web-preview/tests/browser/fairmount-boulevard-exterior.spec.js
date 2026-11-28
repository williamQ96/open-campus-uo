import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const homes = {
  "roof-41959677": "1610 Fairmount Blvd",
  "roof-4c44850e": "1720 Fairmount Blvd",
  "roof-c60174af": "1740 Fairmount Blvd",
  "roof-333eb38f": "1780 Fairmount Blvd",
  "roof-8d9a1132": "1800 Fairmount Blvd",
  "roof-29f81172": "1820 Fairmount Blvd",
  "roof-9cf9957b": "1956 Fairmount Blvd",
};
const baseline = "/?exterior-review=fairmount-boulevard-exterior-baseline";

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
      garage: __campus.collisionCheck(808.91, 562.98),
    };
  }, Object.keys(homes));
}

test("seven Fairmount houses keep their IDs and the 1780 garage bay opens", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 7 }));
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(homes);
  expect(after.garage).toBe(false);
  expect(before.garage).toBe(true);
  expect(after.otherEntries).toEqual(before.otherEntries);
  expect(after.entries).toHaveLength(7);
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

test("an invalid final Fairmount anchor restores all seven source ranges", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const descriptor = "fairmount-boulevard-exterior-review/site.json";
  const json = await (await page.request.get("/scene/" + descriptor)).json();
  json.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.58;
  const body = JSON.stringify(json);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.fairmount_boulevard_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await page.route("**/" + descriptor, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
