import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const buildings = {
  "roof-3ac532c7": "1848 Garden Ave",
  "roof-9c95368e": "Riverview Business Park (1901 Garden)",
  "roof-f2c952e3": "1976 Garden Ave",
  "roof-1a10907d": "Millrace Gardens South Building",
  "roof-e3c224a3": "Millrace Gardens North Building",
};
const baseline = "/?exterior-review=garden-avenue-exterior-baseline";

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
      millrace: [
        __campus.collisionCheck(700.962, -111.889),
        __campus.collisionCheck(686.173, -108.135),
        __campus.collisionCheck(703.401, -123.2),
      ],
    };
  }, Object.keys(buildings));
}

test("five Garden Avenue exteriors keep their IDs and the Millrace Gardens passage stays open", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 5 }));
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(buildings);
  expect(after.millrace).toEqual([false, true, true]);
  expect(after.otherEntries).toEqual(before.otherEntries);
  expect(after.entries).toHaveLength(5);
  expect(
    after.entries.every(
      ({ gate, walkable }) => gate === "street-entry" && walkable,
    ),
  ).toBe(true);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(buildings)) {
    await search.fill(name);
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

test("an invalid final Garden Avenue anchor restores all five source ranges", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const descriptor = "garden-avenue-exterior-review/site.json";
  const json = await (await page.request.get("/scene/" + descriptor)).json();
  json.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.58;
  const body = JSON.stringify(json);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.garden_avenue_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await page.route("**/" + descriptor, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
