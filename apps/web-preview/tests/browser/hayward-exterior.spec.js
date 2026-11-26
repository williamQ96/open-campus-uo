import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";

const stadium = "context-oc-hayward";
const old = ["roof-64589bec", "roof-f7af1b95"];
const baseline = "/?exterior-review=hayward-exterior-baseline";

async function snapshot(page, location) {
  await page.goto(location);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(
    ({ stadium, old }) => {
      const state = __campus.getState();
      const entries = __campus.entranceInfo();
      return {
        count: state.buildings,
        trees: state.presentation.trees,
        batch: state.presentation.batchedBuildings,
        roads: state.roadSegments,
        entries,
        neighbors: entries.filter(
          ({ id }) => id !== stadium && !old.includes(id),
        ),
        openField: !__campus.collisionCheck(0, 374),
        tower: __campus.collisionCheck(66, 295),
        columbia: __campus
          .namedBuildings()
          .some(({ id, name }) => id === "uo-036" && name === "Columbia Hall"),
      };
    },
    { stadium, old },
  );
}

test("Hayward preserves Columbia and replaces both overlapping old stand meshes", async ({
  page,
}) => {
  const before = await snapshot(page, baseline);
  const after = await snapshot(page, "/");
  expect(after.neighbors).toEqual(before.neighbors);
  expect([after.count, after.batch, after.roads]).toEqual([
    before.count - 2,
    before.batch - 1,
    before.roads,
  ]);
  expect(after.trees).toBe(before.trees - 20);
  expect(after.openField && after.tower && after.columbia).toBe(true);
  expect(after.entries.filter(({ id }) => old.includes(id))).toHaveLength(0);
  const gates = after.entries.filter(({ id }) => id === stadium);
  expect(gates.map(({ gate, walkable }) => [gate, walkable])).toEqual([
    ["powell-plaza", true],
    ["tower-public-entry", true],
  ]);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("Hayward Field");
  await search.press("Enter");
  await expect
    .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
    .toBe(stadium);
});

test("a bad last tree anchor restores the full earlier stadium scene", async ({
  page,
  request,
}) => {
  const before = await snapshot(page, baseline);
  const response = await request.get(
    "/scene/hayward-exterior-review/site.json",
  );
  const spec = await response.json();
  spec.context_trees.at(-1).position_enu_m[0] += 0.8;
  const body = JSON.stringify(spec);
  await page.route("**/hayward-exterior-review/site.json", (route) =>
    route.fulfill({ contentType: "application/json", body }),
  );
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.hayward_exterior_site.sha256 = createHash("sha256")
      .update(body)
      .digest("hex");
    await route.fulfill({ response, json });
  });
  expect(await snapshot(page, "/")).toEqual(before);
});
