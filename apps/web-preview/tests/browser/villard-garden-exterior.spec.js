import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const homes = {
  "roof-5d371770": "1848 Villard St",
  "state-1841280": "1878 Villard St",
  "roof-a0566b7b": "1989 Villard St",
  "state-1830735": "1991 Villard St",
  "roof-3ce27cdc": "1923 Garden Ave",
  "state-1841318": "Treetops Apartments",
};

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const s = __campus.getState();
    return {
      counts: [
        s.buildings,
        s.presentation.batchedBuildings,
        s.presentation.refinedContextRoofs,
      ],
      entries: __campus.entranceInfo().filter(({ id }) => ids.includes(id)),
      names: Object.fromEntries(
        __campus
          .namedBuildings()
          .filter(({ id }) => ids.includes(id))
          .map(({ id, name }) => [id, name]),
      ),
      gaps: [
        [445.131, 659.833],
        [505.946, 855.39],
        [597.4839, -156.4755],
      ].map(([x, z]) => __campus.collisionCheck(x, z)),
    };
  }, Object.keys(homes));
}

test("Villard and Garden split into six independently searchable homes", async ({
  page,
}) => {
  const current = await inspect(page);
  expect(current.counts).toEqual(exteriorCounts());
  expect(current.names).toEqual(homes);
  expect(current.entries).toHaveLength(6);
  expect(
    current.entries.every(
      ({ gate, walkable }) => gate === "street-entry" && walkable,
    ),
  ).toBe(true);
  expect(current.gaps).toEqual([false, false, false]);

  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(homes)) {
    await search.fill(name);
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

test("a failed third anchor returns all three residential source candidates", async ({
  page,
}) => {
  const previous = await inspect(
    page,
    "/?exterior-review=villard-garden-exterior-baseline",
  );
  expect(previous.counts).toEqual(
    exteriorCounts({ buildings: -3, batched: 3 }),
  );
  expect(previous.entries).toHaveLength(3);
  expect(previous.gaps).toEqual([true, true, true]);

  const descriptor = "villard-garden-exterior-review/site.json";
  const response = await page.request.get("/scene/" + descriptor);
  const site = await response.json();
  site.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.61;
  const body = JSON.stringify(site);
  const hash = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.villard_garden_exterior_site.sha256 = hash;
    await route.fulfill({ response, json: config });
  });
  await page.route("**/" + descriptor, (route) =>
    route.fulfill({ contentType: "application/json", body }),
  );
  expect(await inspect(page)).toEqual(previous);
});
