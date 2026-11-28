import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const directory = "broadway-orchard-exterior-review";
const baseline = "/?exterior-review=broadway-orchard-exterior-baseline";
const names = {
  "roof-b40f786d": "652 E Broadway",
  "roof-f8b27077": "659 E Broadway",
  "roof-060ab58a": "686 E Broadway",
  "roof-6c97d6b4": "782 E Broadway",
  "roof-b3252193": "1432 Orchard St",
  "roof-bb9ee65a": "1468–1476 Orchard Aly",
  "roof-a8a115d2": "1505 Orchard St",
  "roof-846446eb": "1838 Orchard St",
  "roof-8eff0cee": "2059 Orchard St",
};

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const { buildings, presentation } = __campus.getState();
    const gates = __campus.entranceInfo();
    return {
      counts: [
        buildings,
        presentation.batchedBuildings,
        presentation.refinedContextRoofs,
      ],
      names: Object.fromEntries(
        __campus
          .namedBuildings()
          .filter(({ id }) => ids.includes(id))
          .map(({ id, name }) => [id, name]),
      ),
      entries: gates.filter(({ id }) => ids.includes(id)),
      otherEntries: gates.filter(({ id }) => !ids.includes(id)),
    };
  }, Object.keys(names));
}

test("nine Broadway and Orchard exteriors retain their IDs and entrances", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 9 }));
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(names);
  expect(after.otherEntries).toEqual(before.otherEntries);
  expect(after.entries).toHaveLength(9);
  expect(
    after.entries.every(
      ({ gate, walkable }) => gate === "street-entry" && walkable,
    ),
  ).toBe(true);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(names)) {
    await search.fill(name);
    if (isBackgroundBuilding(id)) {
      await expect(
        page.getByRole("option").filter({ hasText: name }),
      ).toHaveCount(0);
      continue;
    }
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});
test("Orchard covered parking and courtyard are clear while their supports block movement", async ({
  page,
}) => {
  await inspect(page);
  // Check the lower hospital gallery, three parking stalls and the courtyard gap and floor.
  const openPoints = [
    [590.92834, 172.36],
    [538.92893, 205.01536],
    [539.03331, 209.62418],
    [538.81617, 200.03664],
    [630.53093, 271.10227],
    [638.68094, 271.09941],
    [643.00031, 283.23319],
  ];
  const result = await page.evaluate(
    async ({ directory, openPoints }) => {
      const response = await fetch("/scene/" + directory + "/site.json");
      const residents = (await response.json()).buildings.filter(
        ({ id }) => id === "roof-bb9ee65a" || id === "roof-b3252193",
      );
      const columns = residents
        .flatMap(({ support_collision_enu_m }) => support_collision_enu_m)
        .map((ring) => {
          const corners = ring.slice(0, -1);
          return corners.reduce(
            ([x, z], [e, n]) => [
              x + e / corners.length,
              z - n / corners.length,
            ],
            [0, 0],
          );
        });
      return {
        coveredAndCourtyard: openPoints.map(([x, z]) =>
          __campus.collisionCheck(x, z),
        ),
        columns: columns.map(([x, z]) => __campus.collisionCheck(x, z)),
      };
    },
    { directory, openPoints },
  );
  expect(result).toEqual({
    coveredAndCourtyard: Array(7).fill(false),
    columns: Array(10).fill(true),
  });
});
test("a shifted range restores all nine Broadway and Orchard sources", async ({
  page,
}) => {
  const original = await inspect(page, baseline);
  const url = "/scene/" + directory + "/site.json";
  const descriptor = await (await page.request.get(url)).json();
  descriptor.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.56;
  const body = JSON.stringify(descriptor);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.broadway_orchard_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await page.route("**" + url, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(original);
});
