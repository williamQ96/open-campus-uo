import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const directory = "millrace-fairmount-exterior-review";
const chapter = "roof-4bcb9296";
const garage = "roof-f9fb8501";
const targets = {
  [chapter]: "Alpha Tau Omega Chapter House",
  "roof-01c76e05": "1956 E 15th Avenue",
  "roof-e7592432": "1871 E 19th Avenue",
  [garage]: "Walnut Alley Garage Building",
};
const probes = [
  [-791, -377],
  [-782, -356],
  [-776.8, -364.12],
  [-774.25, -365.64],
  [-766, -365],
  [555, 265],
  [556, 255.8],
  [423, 709],
  [422.8, 721],
  [685, 315],
  [677.5, 315],
];

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(
    ({ ids, probes }) => {
      const campus = window.__campus;
      const { buildings, presentation } = campus.getState();
      const entries = campus.entranceInfo();
      return {
        counts: [
          buildings,
          presentation.batchedBuildings,
          presentation.refinedContextRoofs,
        ],
        names: Object.fromEntries(
          campus
            .namedBuildings()
            .filter(({ id }) => ids.includes(id))
            .map(({ id, name }) => [id, name]),
        ),
        entries: entries.filter(({ id }) => ids.includes(id)),
        neighbors: entries.filter(({ id }) => !ids.includes(id)),
        collision: probes.map(([x, z]) => campus.collisionCheck(x, z)),
      };
    },
    { ids: Object.keys(targets), probes },
  );
}

test("the four registered exteriors preserve their public approaches and search", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const before = await inspect(
    page,
    "/?exterior-review=millrace-fairmount-exterior-baseline",
  );
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 4 }));
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(targets);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.entries).toHaveLength(3);
  expect(after.entries.some(({ id }) => id === garage)).toBe(false);
  expect(
    after.entries.every(({ estimated, walkable }) => estimated && walkable),
  ).toBe(true);
  expect(after.collision).toEqual([
    true,
    true,
    true,
    false,
    false,
    true,
    false,
    true,
    false,
    true,
    false,
  ]);

  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(targets)) {
    await search.fill(name);
    await search.press("Enter");
    await expect
      .poll(() =>
        page.evaluate(() => window.__campus.getState().selectedBuilding),
      )
      .toBe(id);
  }
});

test("a route from 968 Alder reaches the chapter's east recess without the former terminal spur", async ({
  page,
}) => {
  const state = await inspect(page);
  expect(state.entries.find(({ id }) => id === chapter)).toMatchObject({
    gate: "millrace-east-entry",
    walkable: true,
  });
  await page.locator("#directions-open").click();
  for (const [endpoint, text] of [
    ["A", "968 Alder Apartments"],
    ["B", targets[chapter]],
  ]) {
    await page
      .getByRole("button", { name: `Search ${endpoint}`, exact: true })
      .click();
    const input = page.getByRole("combobox");
    await input.fill(text);
    await input.press("ArrowDown");
    await input.press("Enter");
  }
  await page.locator("#route-start").click();
  const points = await page.evaluate(
    () => window.__campus.getState().navigation.points,
  );
  expect(points.length).toBeGreaterThan(3);
  expect(points.some(([e, n]) => e === -777.1 && n === 364.04)).toBe(false);
  const [x, n] = points.at(-1);
  expect(x).toBeGreaterThan(-775.91);
  expect(x).toBeLessThan(-770);
  expect(Math.abs(n - 365.64)).toBeLessThan(1);
});

test("damaged batch anchors restore all four source buildings and the previous gate state", async ({
  page,
}) => {
  const path = directory + "/site.json";
  const before = await inspect(
    page,
    "/?exterior-review=millrace-fairmount-exterior-baseline",
  );
  const spec = await (await page.request.get("/scene/" + path)).json();
  spec.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.62;
  const body = JSON.stringify(spec);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.millrace_fairmount_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json });
  });
  await page.route("**/scene/" + path, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
