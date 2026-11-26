import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";

const ids = ["context-oc-cedar", "context-oc-yasui"];
const retired = ["roof-1fde9ce4", "roof-1d1803a6", "roof-7974be11"];
const baseline = "/?exterior-review=cedar-yasui-baseline";

async function load(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function inspect({ ids, retired }) {
  const state = __campus.getState();
  const gates = __campus.entranceInfo();
  return {
    count: state.buildings,
    batches: state.presentation.batchedBuildings,
    roads: state.roadSegments,
    gates: gates.filter(({ id }) => ids.includes(id)),
    neighbors: gates.filter(({ id }) => ![...ids, ...retired].includes(id)),
    retired: gates.filter(({ id }) => retired.includes(id)).map(({ id }) => id),
    portal: Array.from({ length: 40 }, (_, i) =>
      __campus.collisionCheck(-38 + i * 0.65, 182.62),
    ),
    collision: [
      [-25, 188],
      [10, 143],
      [3, 191],
      [17, 154],
      [48, 120],
    ].map(([e, z]) => __campus.collisionCheck(e, z)),
  };
}

test("the courtyards and Yasui passage open between the registered halls", async ({
  page,
}) => {
  await load(page, baseline);
  const old = await page.evaluate(inspect, { ids, retired });
  await load(page);
  const current = await page.evaluate(inspect, { ids, retired });
  expect(old.portal.every(Boolean)).toBe(true);
  expect(current.portal.some(Boolean)).toBe(false);
  expect(current.collision).toEqual([true, false, false, true, true]);
  expect(current.count).toBe(old.count - 3);
  expect(current.batches).toBe(old.batches - 3);
  expect(current.retired).toEqual([]);
  expect(current.neighbors).toEqual(old.neighbors);
  expect(current.roads).toBe(old.roads);
  expect(current.gates.map(({ gate }) => gate).sort()).toEqual([
    "cedar-agate",
    "cedar-north-court",
    "cedar-north-wing",
    "cedar-south-court",
    "yasui-breezeway",
    "yasui-north-court",
  ]);
  expect(current.gates.every(({ walkable }) => walkable)).toBe(true);

  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [i, name] of ["Cedar Hall", "Yasui Hall"].entries()) {
    await search.fill(name);
    await search.press("ArrowDown");
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(ids[i]);
  }
});

test("invalid ground footprints restore the entire prior group", async ({
  page,
}) => {
  await load(page, baseline);
  const old = await page.evaluate(inspect, { ids, retired });
  const descriptor = JSON.parse(
    readFileSync(
      new URL(
        "../../public/scene/cedar-yasui-review/site.json",
        import.meta.url,
      ),
      "utf8",
    ),
  );
  descriptor.buildings[1].ground_footprints_enu_m = [];
  const body = JSON.stringify(descriptor);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/cedar-yasui-review/site.json", (route) =>
    route.fulfill({ contentType: "application/json", body }),
  );
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.cedar_yasui_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await load(page);
  expect(await page.evaluate(inspect, { ids, retired })).toEqual(old);
});
