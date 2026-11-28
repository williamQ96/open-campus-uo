import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const baseline = "/?exterior-review=southeast-fairmount-exterior-baseline";
const descriptorPath = "/scene/southeast-fairmount-exterior-review/site.json";
const buildings = [
  ["roof-e0d560b4", "281 Sunset Drive", 882, 669],
  ["roof-169a7b78", "365 Sunset Drive", 942, 568],
  ["roof-699d6c1e", "366 Sunset Drive", 982, 559],
  ["roof-22175da6", "2281 Rose Lane", 966, 488],
  ["roof-05727176", "2275 Rose Lane", 967, 460],
  ["roof-b2800bfe", "2293 Birch Lane", 984, 302],
];

async function inspect(page, url = "/") {
  await page.goto(url, { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((buildings) => {
    const campus = window.__campus;
    const state = campus.getState();
    const ids = new Set(buildings.map(([id]) => id));
    const gates = campus.entranceInfo().filter(({ id }) => ids.has(id));
    return {
      counts: [
        state.buildings,
        state.presentation.batchedBuildings,
        state.presentation.refinedContextRoofs,
      ],
      names: Object.fromEntries(
        campus
          .namedBuildings()
          .filter(({ id }) => ids.has(id))
          .map(({ id, name }) => [id, name]),
      ),
      gates,
      solid: buildings.map(([, , x, z]) => campus.collisionCheck(x, z)),
      clear: gates.map(({ approach }) => !campus.collisionCheck(...approach)),
    };
  }, buildings);
}

test("six hillside exteriors are searchable and only three approaches are placed", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const original = await inspect(page, baseline);
  expect(original.counts).toEqual(exteriorCounts({ batched: 6 }));
  expect(original.names).toEqual({});
  const current = await inspect(page);
  expect(current.counts).toEqual(exteriorCounts());
  expect(current.names).toEqual(
    Object.fromEntries(buildings.map(([id, name]) => [id, name])),
  );
  expect(current.solid).toEqual(Array(6).fill(true));
  expect(current.clear).toEqual(Array(3).fill(true));
  expect(current.gates.map(({ gate }) => gate).sort()).toEqual([
    "birch-recess-south",
    "rose-cottage-west",
    "sunset-recess-west",
  ]);
  for (const gate of current.gates)
    expect(gate).toMatchObject({ walkable: true, estimated: true });

  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of buildings) {
    await search.fill(name);
    if (isBackgroundBuilding(id)) {
      await expect(
        page.getByRole("option").filter({ hasText: name }),
      ).toHaveCount(0);
      continue;
    }
    await search.press("Enter");
    await page.waitForFunction(
      (id) => window.__campus.getState().selectedBuilding === id,
      id,
    );
  }
});

test("the network route reaches the modeled west approach on Rose Lane", async ({
  page,
}) => {
  const { gates } = await inspect(page);
  const rose = gates.find(({ gate }) => gate === "rose-cottage-west");
  await page.locator("#directions-open").click();
  for (const [end, name] of [
    ["A", "968 Alder Apartments"],
    ["B", "2281 Rose Lane"],
  ]) {
    await page
      .getByRole("button", { name: "Search " + end, exact: true })
      .click();
    const search = page.getByRole("combobox");
    await search.fill(name);
    await search.press("ArrowDown");
    await search.press("Enter");
  }
  await page.locator("#route-start").click();
  const points = await page.evaluate(
    () => window.__campus.getState().navigation.points,
  );
  expect(points.length).toBeGreaterThan(2);
  expect(points.at(-1)).toEqual([rose.approach[0], -rose.approach[1]]);
});

test("an invalid last source anchor restores the six source shapes together", async ({
  page,
}) => {
  const previous = await inspect(page, baseline);
  const descriptor = await (await page.request.get(descriptorPath)).json();
  descriptor.batch_removals.at(-1).source_vertices[0][1][0] += 0.64;
  const body = JSON.stringify(descriptor);
  const hash = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.southeast_fairmount_exterior_site.sha256 = hash;
    await route.fulfill({ response, json });
  });
  await page.route("**" + descriptorPath, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(previous);
});
