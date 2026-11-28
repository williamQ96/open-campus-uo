import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const buildings = {
  "roof-efd78630": "1401 Villard St",
  "roof-d3e38b75": "1599 Villard St",
  "roof-bb028710": "1637 Villard St",
  "roof-5f1e62f1": "1801 Villard St",
  "roof-45158580": "1969 Villard St",
  "roof-c2d79893": "1979 Villard St",
};
const baseline = "/?exterior-review=villard-street-exterior-baseline";

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
      porch: [
        __campus.collisionCheck(499.0236, 821.78),
        __campus.collisionCheck(503.26, 821.78),
        __campus.collisionCheck(496.78, 821.78),
      ],
    };
  }, Object.keys(buildings));
}

test("six Villard Street exteriors keep their IDs and the 1969 porch stays open", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 6 }));
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(buildings);
  expect(after.porch).toEqual([false, true, false]);
  expect(before.porch[0]).toBe(true);
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

test("an invalid final Villard Street anchor restores all six source ranges", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const descriptor = "villard-street-exterior-review/site.json";
  const json = await (await page.request.get("/scene/" + descriptor)).json();
  json.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.58;
  const body = JSON.stringify(json);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.villard_street_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await page.route("**/" + descriptor, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
