import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";

const models = {
  "roof-311b157f": "East Campus Graduate Village West",
  "roof-03ecaaba": "East Campus Graduate Village East",
};
const ids = Object.keys(models);
const baseline = "/?exterior-review=graduates-baseline";

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
      [375, 163],
      [394, 177],
      [395, 163],
      [453, 165],
      [433, 153],
      [433, 170],
      [412, 170],
    ].map(([e, z]) => __campus.collisionCheck(e, z)),
  };
}

test("Graduate Village keeps two selectable buildings and an open approach between them", async ({
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
  const adjacentId = "roof-6dc8ed19";
  expect(after.others.filter(({ id }) => id !== adjacentId)).toEqual(
    before.others.filter(({ id }) => id !== adjacentId),
  );
  expect(after.others.find(({ id }) => id === adjacentId)).toMatchObject({
    estimated: true,
    walkable: true,
  });
  expect(after.collision).toEqual([
    true,
    true,
    false,
    true,
    true,
    false,
    false,
  ]);
  expect(
    Object.fromEntries(after.gates.map((g) => [g.id, [g.gate, g.walkable]])),
  ).toEqual({
    [ids[0]]: ["graduate-west", true],
    [ids[1]]: ["graduate-east", true],
  });
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(models)) {
    await search.fill(name);
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

test("a mismatched east anchor restores both previous models", async ({
  page,
}) => {
  await load(page, baseline);
  const before = await page.evaluate(facts, ids);
  const descriptor = JSON.parse(
    readFileSync(
      new URL(
        "../../public/scene/graduate-village-review/site.json",
        import.meta.url,
      ),
      "utf8",
    ),
  );
  descriptor.batch_removals[1].source_vertices[0][1][0] += 8;
  const body = JSON.stringify(descriptor);
  const sha = createHash("sha256").update(body).digest("hex");
  await page.route("**/graduate-village-review/site.json", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body }),
  );
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.graduate_village_site.sha256 = sha;
    await route.fulfill({ response, json: config });
  });
  await load(page);
  expect(await page.evaluate(facts, ids)).toEqual(before);
});
