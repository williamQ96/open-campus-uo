import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";

const primary = "roof-72c79877";
const absorbed = "roof-7b325cb8";
const name = "Moss Street Children's Center";
const baseline = "/?exterior-review=moss-baseline";

async function ready(page, path = "/") {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function facts([primary, absorbed]) {
  const state = __campus.getState();
  const entries = __campus.entranceInfo();
  const matches = (id) => id === primary || id === absorbed;
  return {
    count: state.buildings,
    batches: state.presentation.batchedBuildings,
    roads: state.roadSegments,
    names: __campus.namedBuildings().filter(({ id }) => matches(id)),
    entries: entries.filter(({ id }) => matches(id)),
    neighbors: entries.filter(({ id }) => !matches(id)),
    collision: [
      [368, 424],
      [386.397, 443.615],
      [380, 447],
      [396, 469],
      [404, 443],
      [410, 447],
    ].map(([e, z]) => __campus.collisionCheck(e, z)),
  };
}

test("the five volumes use one selectable identity, with the courtyard open around the tree", async ({
  page,
}) => {
  await ready(page, baseline);
  const before = await page.evaluate(facts, [primary, absorbed]);
  await ready(page);
  const after = await page.evaluate(facts, [primary, absorbed]);
  expect(after.count).toBe(before.count - 1);
  expect(after.batches).toBe(before.batches - 2);
  expect(after.roads).toBe(before.roads);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.names.map((b) => [b.id, b.name])).toEqual([[primary, name]]);
  expect(after.entries.map((e) => [e.id, e.gate, e.walkable])).toEqual([
    [primary, "moss-street", true],
  ]);
  expect(after.collision).toEqual([true, true, false, true, true, false]);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("Moss Street Children");
  await page.getByRole("option", { name }).first().click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
    .toBe(primary);
});

for (const broken of ["model", "second source triangle anchor"]) {
  test(`a damaged ${broken} restores both old mesh members`, async ({
    page,
  }) => {
    await ready(page, baseline);
    const prior = await page.evaluate(facts, [primary, absorbed]);
    if (broken === "model") {
      await page.route("**/moss-street-review/site.glb", (route) =>
        route.fulfill({ status: 200, body: "bad model pin" }),
      );
    } else {
      const descriptor = JSON.parse(
        readFileSync(
          new URL(
            "../../public/scene/moss-street-review/site.json",
            import.meta.url,
          ),
          "utf8",
        ),
      );
      descriptor.batch_removals[1].source_vertices[0][1][0] += 8;
      const body = JSON.stringify(descriptor);
      const sha = createHash("sha256").update(body).digest("hex");
      await page.route("**/scene/moss-street-review/site.json", (route) =>
        route.fulfill({ status: 200, contentType: "application/json", body }),
      );
      await page.route("**/scene/presentation.json", async (route) => {
        const response = await route.fetch();
        const config = await response.json();
        config.moss_street_site.sha256 = sha;
        await route.fulfill({ response, json: config });
      });
    }
    await ready(page);
    expect(await page.evaluate(facts, [primary, absorbed])).toEqual(prior);
  });
}
