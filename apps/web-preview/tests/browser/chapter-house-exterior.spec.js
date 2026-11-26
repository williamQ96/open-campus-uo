import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const HOUSE_IDS = ["roof-c85e8e54", "state-1841241"];
const names = ["Delta Delta Delta House", "Chi Omega House"];
const baseline = "/?exterior-review=chapter-house-exterior-baseline";

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const state = __campus.getState();
    return {
      counts: [
        state.buildings,
        state.presentation.batchedBuildings,
        state.presentation.refinedContextRoofs,
      ],
      entries: __campus.entranceInfo().filter(({ id }) => ids.includes(id)),
      names: __campus.namedBuildings().filter(({ id }) => ids.includes(id)),
      collision: [
        [-720, 195],
        [-691, 223],
        [-703.6, 201.5],
        [-705, 207.2],
      ].map(([x, z]) => __campus.collisionCheck(x, z)),
    };
  }, HOUSE_IDS);
}

test("split chapter houses have independent names, entrances and collision", async ({
  page,
}) => {
  const current = await inspect(page);
  expect(current.counts).toEqual(exteriorCounts());
  expect(current.names.map(({ name }) => name).sort()).toEqual(
    [...names].sort(),
  );
  expect(current.entries).toHaveLength(2);
  expect(current.entries.every(({ gate, walkable }) => gate && walkable)).toBe(
    true,
  );
  expect(current.collision).toEqual([true, true, false, false]);

  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [i, name] of names.entries()) {
    await search.fill(name);
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(HOUSE_IDS[i]);
  }
});

test("a bad split source returns to the previous single selection", async ({
  page,
}) => {
  const previous = await inspect(page, baseline);
  expect(previous.counts).toEqual(
    exteriorCounts({ buildings: -1, batched: 1 }),
  );
  expect(previous.entries).toHaveLength(1);
  expect(previous.collision).toEqual([true, true, true, true]);
  const site = JSON.parse(
    await (
      await page.request.get("/scene/chapter-house-exterior-review/site.json")
    ).text(),
  );
  site.split_buildings[HOUSE_IDS[1]] = "roof-2cbfcd06";
  const body = JSON.stringify(site);
  const hash = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.chapter_house_exterior_site.sha256 = hash;
    await route.fulfill({ response, json: config });
  });
  await page.route("**/chapter-house-exterior-review/site.json", (route) =>
    route.fulfill({ contentType: "application/json", body }),
  );
  expect(await inspect(page)).toEqual(previous);
});
