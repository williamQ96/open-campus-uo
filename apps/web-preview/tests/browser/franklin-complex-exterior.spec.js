import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const directory = "franklin-complex-exterior-review";
const baseline = "/?exterior-review=franklin-complex-exterior-baseline";
const names = {
  "roof-b59639cc": "Womack Hall",
  "roof-fc0fcc2e": "1920–1960 Franklin Blvd",
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

test("Womack Hall and four connected stores retain two building IDs and five approaches", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 2 }));
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(names);
  expect(after.otherEntries).toEqual(before.otherEntries);
  expect(after.entries.map(({ gate }) => gate).sort()).toEqual([
    "cafe-seoul",
    "hirons",
    "market-of-choice",
    "north-portico",
    "subway",
  ]);
  expect(after.entries.every(({ walkable }) => walkable)).toBe(true);
  expect(
    new Set(after.entries.map(({ approach }) => approach.join(","))).size,
  ).toBe(5);

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

  const collision = await page.evaluate(async (directory) => {
    const response = await fetch("/scene/" + directory + "/site.json");
    const site = await response.json();
    const hall = site.buildings.find(({ id }) => id === "roof-b59639cc");
    const supports = hall.support_collision_enu_m.map((ring) => {
      const points = ring.slice(0, -1);
      return points.reduce(
        ([x, z], [e, n]) => [x + e / points.length, z - n / points.length],
        [0, 0],
      );
    });
    const [left, right] = supports;
    const center = [(left[0] + right[0]) / 2, (left[1] + right[1]) / 2];
    return {
      pillars: supports.map(([x, z]) => __campus.collisionCheck(x, z)),
      drive: __campus.collisionCheck(...center),
    };
  }, directory);
  expect(collision).toEqual({ pillars: [true, true], drive: false });
});

test("a changed complex range keeps both originals and the six Franklin storefronts", async ({
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
    config.franklin_complex_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await page.route("**" + url, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(original);
});
