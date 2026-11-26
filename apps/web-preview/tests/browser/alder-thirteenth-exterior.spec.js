import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const baseline = "/?exterior-review=alder-thirteenth-exterior-baseline";
const descriptorPath = "/scene/alder-thirteenth-exterior-review/site.json";
const buildings = [
  ["alder-thirteenth-corner", "Alder & 13th Corner Shops"],
  ["alder-gopuran", "Gopuran Building · Webfoot Bar & Grill"],
  ["roof-5ed4d412", "Flock13"],
  ["alder-duck-store", "The Duck Store"],
];
const probes = [
  [-734, -24],
  [-704, -29],
  [-687, -28],
  [-648, -25],
  [-730, -54],
  [-712, -28],
  [-649.4, -13],
  [-737, -9.4],
  [-714, -10.5],
  [-722, -63.5],
  [-744.5, -25],
];

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(
    ({ buildings, probes }) => {
      const c = window.__campus;
      const s = c.getState();
      const ids = new Set(buildings.map(([id]) => id));
      return {
        counts: [
          s.buildings,
          s.presentation.batchedBuildings,
          s.presentation.refinedContextRoofs,
        ],
        names: Object.fromEntries(
          c
            .namedBuildings()
            .filter(({ id }) => ids.has(id))
            .map(({ id, name }) => [id, name]),
        ),
        gates: c.entranceInfo().filter(({ id }) => ids.has(id)),
        collision: probes.map(([e, z]) => c.collisionCheck(e, z)),
      };
    },
    { buildings, probes },
  );
}

test("split addresses remain selectable and only the construction parcel is closed", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const original = await inspect(page, baseline);
  expect(original.counts).toEqual(
    exteriorCounts({ buildings: -2, batched: 2 }),
  );
  expect(original.names).toEqual({});
  expect(original.collision[5]).toBe(false);
  const current = await inspect(page);
  expect(current.counts).toEqual(exteriorCounts());
  expect(current.names).toEqual(Object.fromEntries(buildings));
  expect(current.gates).toHaveLength(4);
  for (const gate of current.gates) {
    expect(gate).toMatchObject({ walkable: true, estimated: true });
  }
  expect(current.collision).toEqual([
    true,
    true,
    true,
    true,
    true,
    true,
    false,
    false,
    false,
    false,
    false,
  ]);
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

test("the public route ends at the modeled Flock13 entrance approach", async ({
  page,
}) => {
  await inspect(page);
  await page.locator("#directions-open").click();
  for (const [end, label] of [
    ["A", "968 Alder Apartments"],
    ["B", "Flock13"],
  ]) {
    await page
      .getByRole("button", { name: "Search " + end, exact: true })
      .click();
    const input = page.getByRole("combobox");
    await input.fill(label);
    await input.press("ArrowDown");
    await input.press("Enter");
  }
  await page.locator("#route-start").click();
  const route = await page.evaluate(
    () => window.__campus.getState().navigation.points,
  );
  expect(route.length).toBeGreaterThan(2);
  expect(route.at(-1)[0]).toBeCloseTo(-680.4992, 2);
  expect(route.at(-1)[1]).toBeCloseTo(9.614, 2);
});

test("an invalid demolition anchor restores both original buildings and opens the replacement closure", async ({
  page,
}) => {
  const previous = await inspect(page, baseline);
  const descriptor = await (await page.request.get(descriptorPath)).json();
  descriptor.batch_removals.find(
    ({ id }) => id === "roof-f6be07b4",
  ).source_vertices[0][1][0] += 0.76;
  const body = JSON.stringify(descriptor);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.alder_thirteenth_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json });
  });
  await page.route("**" + descriptorPath, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(previous);
});
