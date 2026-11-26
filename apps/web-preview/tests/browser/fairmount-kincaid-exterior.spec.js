import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const baseline = "/?exterior-review=fairmount-kincaid-exterior-baseline";
const descriptorPath = "/scene/fairmount-kincaid-exterior-review/site.json";
const buildings = [
  ["roof-046adce7", "1517 Walnut Street"],
  ["roof-58551b68", "1680 Walnut Street"],
  ["roof-622a75af", "1671 Walnut Street"],
  ["roof-c4396bfc", "1991 E 19th Avenue"],
  ["roof-d427a5ce", "1931 Moss Street"],
  ["roof-c54987d3", "1879 Moss Street"],
  ["roof-d6ddd6ae", "Pi Beta Phi Chapter House"],
  ["roof-f414e967", "Alpha Chi Omega Chapter House"],
];
const screened = ["roof-c4396bfc", "roof-c54987d3"];
const interiors = [
  [766, 284],
  [716, 466],
  [766, 449],
  [583, 711],
  [376, 779],
  [381, 700],
  [-657, 268],
  [-689, 265],
];

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(
    ({ buildings, interiors }) => {
      const campus = window.__campus;
      const state = campus.getState();
      const ids = new Set(buildings.map(([id]) => id));
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
        gates: campus.entranceInfo().filter(({ id }) => ids.has(id)),
        roofs: interiors.map(([x, z]) => campus.collisionCheck(x, z)),
      };
    },
    { buildings, interiors },
  );
}

test("eight exterior identities replace their batch candidates and keep six sourced approaches", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const original = await inspect(page, baseline);
  expect(original.counts).toEqual(exteriorCounts({ batched: 8 }));
  expect(original.names).toEqual({});
  const current = await inspect(page);
  expect(current.counts).toEqual(exteriorCounts());
  expect(current.names).toEqual(Object.fromEntries(buildings));
  expect(current.roofs).toEqual(Array(8).fill(true));
  expect(current.gates.map(({ id }) => id).sort()).toEqual(
    buildings
      .map(([id]) => id)
      .filter((id) => !screened.includes(id))
      .sort(),
  );
  for (const gate of current.gates) {
    expect(gate).toMatchObject({ walkable: true, estimated: true });
  }
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of buildings) {
    await search.fill(name);
    await search.press("Enter");
    await expect
      .poll(() =>
        page.evaluate(() => window.__campus.getState().selectedBuilding),
      )
      .toBe(id);
  }
});

test("outdoor navigation reaches the Pi Beta Phi front approach", async ({
  page,
}) => {
  await inspect(page);
  await page.locator("#directions-open").click();
  for (const [end, name] of [
    ["A", "968 Alder Apartments"],
    ["B", "Pi Beta Phi Chapter House"],
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
  expect(points.at(-1)[0]).toBeCloseTo(-646.33847, 2);
  expect(points.at(-1)[1]).toBeCloseTo(-269.7702, 2);
});

test("one invalid anchor rolls back all eight replacements", async ({
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
    json.fairmount_kincaid_exterior_site.sha256 = hash;
    await route.fulfill({ response, json });
  });
  await page.route("**" + descriptorPath, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(previous);
});
