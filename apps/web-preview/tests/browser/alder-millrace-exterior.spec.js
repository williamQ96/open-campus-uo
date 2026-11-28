import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const addresses = {
  "roof-4fa203d9": ["1915 Alder St", "1915 Alder St"],
  "roof-7dcf2f03": ["Hess Apartments", "1390 Alder St"],
  "roof-77a7eb6c": ["Millrace Apartments", "1805 Garden Ave"],
};

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const state = __campus.getState();
    const entries = __campus.entranceInfo();
    return {
      counts: [
        state.buildings,
        state.presentation.batchedBuildings,
        state.presentation.refinedContextRoofs,
      ],
      names: Object.fromEntries(
        __campus
          .namedBuildings()
          .filter(({ id }) => ids.includes(id))
          .map(({ id, name }) => [id, name]),
      ),
      entrances: entries.filter(({ id }) => ids.includes(id)),
      remainingEntrances: entries.filter(({ id }) => !ids.includes(id)),
      collision: [
        [-734, 753],
        [-781.5, 100.5],
        [363, -195],
        [-767.8, 99.4],
      ].map(([x, z]) => __campus.collisionCheck(x, z)),
    };
  }, Object.keys(addresses));
}

const baseline = "/?exterior-review=alder-millrace-exterior-baseline";

test("the registered apartments preserve their selections and open the Hess parking bay", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 3, roofs: 3 }));
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(
    Object.fromEntries(
      Object.entries(addresses).map(([id, [name]]) => [id, name]),
    ),
  );
  expect(after.remainingEntrances).toEqual(before.remainingEntrances);
  expect(after.entrances).toHaveLength(3);
  expect(
    after.entrances.every(
      ({ gate, walkable }) => gate === "street-entry" && walkable,
    ),
  ).toBe(true);
  expect(before.collision).toEqual([true, true, true, true]);
  expect(after.collision).toEqual([true, true, true, false]);

  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, [name]] of Object.entries(addresses)) {
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

test("a mismatched final source anchor restores all three source buildings and roofs", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const descriptor = "alder-millrace-exterior-review/site.json";
  const response = await page.request.get("/scene/" + descriptor);
  const site = await response.json();
  site.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.56;
  const body = JSON.stringify(site);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.alder_millrace_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await page.route("**/" + descriptor, (route) =>
    route.fulfill({ contentType: "application/json", body }),
  );
  expect(await inspect(page)).toEqual(before);
});
