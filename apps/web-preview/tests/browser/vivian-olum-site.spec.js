import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";

const models = {
  "roof-1c631d7c": "Vivian Olum Child Development Center",
  "roof-1d1be960": "Vivian Olum Child Development Center Annex",
};
const ids = Object.keys(models);
const baseline = "/?exterior-review=olum-baseline";

async function load(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function facts(ids) {
  const state = __campus.getState();
  const gates = __campus.entranceInfo();
  return {
    count: state.buildings,
    batch: state.presentation.batchedBuildings,
    roads: state.roadSegments,
    names: Object.fromEntries(
      __campus
        .namedBuildings()
        .filter(({ id }) => ids.includes(id))
        .map(({ id, name }) => [id, name]),
    ),
    gates: gates.filter(({ id }) => ids.includes(id)),
    others: gates.filter(({ id }) => !ids.includes(id)),
    collision: [
      [164, 416.1],
      [181, 401],
      [179, 408.9],
      [170.8, 432.7],
      [195, 434],
      [155, 414],
    ].map(([e, z]) => __campus.collisionCheck(e, z)),
  };
}

test("Vivian Olum keeps two selectable buildings and an open approach between them", async ({
  page,
}) => {
  await load(page, baseline);
  const before = await page.evaluate(facts, ids);
  await load(page);
  const after = await page.evaluate(facts, ids);
  expect(after.count).toBe(before.count);
  expect(after.batch).toBe(before.batch - 2);
  expect(after.roads).toBe(before.roads);
  expect(after.names).toEqual(models);
  expect(after.others).toEqual(before.others);
  expect(after.collision).toEqual([true, true, false, false, true, false]);
  expect(after.gates.map((g) => [g.id, g.gate, g.walkable])).toEqual([
    [ids[0], "olum-main", true],
    [ids[1], "olum-annex", true],
  ]);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(models)) {
    await search.fill(name);
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

test("a mismatched annex anchor restores both previous models", async ({
  page,
}) => {
  await load(page, baseline);
  const before = await page.evaluate(facts, ids);
  const descriptor = JSON.parse(
    readFileSync(
      new URL(
        "../../public/scene/vivian-olum-review/site.json",
        import.meta.url,
      ),
      "utf8",
    ),
  );
  descriptor.batch_removals[1].source_vertices[0][1][0] += 8;
  const body = JSON.stringify(descriptor);
  const sha = createHash("sha256").update(body).digest("hex");
  await page.route("**/vivian-olum-review/site.json", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body }),
  );
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.vivian_olum_site.sha256 = sha;
    await route.fulfill({ response, json: config });
  });
  await load(page);
  expect(await page.evaluate(facts, ids)).toEqual(before);
});
