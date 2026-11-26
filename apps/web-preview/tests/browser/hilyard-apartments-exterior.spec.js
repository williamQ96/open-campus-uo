import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const id = "hilyard-apartments-973";
const directory = "hilyard-apartments-exterior-review";
const baseline = "/?exterior-review=hilyard-apartments-exterior-baseline";

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((id) => {
    const { buildings, presentation } = window.__campus.getState();
    const entries = window.__campus.entranceInfo();
    return {
      counts: [
        buildings,
        presentation.batchedBuildings,
        presentation.refinedContextRoofs,
      ],
      name: window.__campus.namedBuildings().find((row) => row.id === id),
      entries: entries.filter((row) => row.id === id),
      neighboringEntries: entries.filter((row) =>
        ["roof-eab27ea2", "roof-9feed235", "roof-a3d5625f"].includes(row.id),
      ),
      blocked: [
        [-877, -389],
        [-885, -396.5],
        [-888, -394.6],
        [-891, -402.2],
        [-856, -380],
      ].map(([e, z]) => window.__campus.collisionCheck(e, z)),
    };
  }, id);
}

test("973 Hilyard adds its own exterior and leaves its neighbors usable", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  expect(before.counts).toEqual(exteriorCounts({ buildings: -1 }));
  expect(before.entries).toEqual([]);
  expect(before.blocked).toEqual([false, false, false, false, true]);

  const after = await inspect(page);
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.name).toMatchObject({
    id,
    name: "Hilyard Apartments · 973 Hilyard",
    name_match: "registered-municipal-address",
  });
  expect(after.entries).toHaveLength(1);
  expect(after.entries[0]).toMatchObject({
    gate: "west-entry",
    walkable: true,
  });
  expect(after.neighboringEntries).toEqual(before.neighboringEntries);
  expect(after.blocked).toEqual([true, true, false, false, true]);

  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("973 Hilyard");
  await search.press("Enter");
  await expect
    .poll(() =>
      page.evaluate(() => window.__campus.getState().selectedBuilding),
    )
    .toBe(id);

  await page.locator("#directions-open").click();
  for (const [label, name] of [
    ["A", "Bushnell University · 770 E 11th Ave"],
    ["B", "973 Hilyard"],
  ]) {
    await page
      .getByRole("button", { name: "Search " + label, exact: true })
      .click();
    await search.fill(name);
    await search.press("Enter");
  }
  await page.locator("#route-start").click();
  const route = await page.evaluate(
    () => window.__campus.getState().navigation,
  );
  const [east, south] = after.entries[0].approach;
  expect(route.points.length).toBeGreaterThan(4);
  expect(route.points.at(-1)).toEqual([east, -south]);
});

test("an unexpected new ID keeps the baseline site and selection", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const path = directory + "/site.json";
  const record = await (await page.request.get("/scene/" + path)).json();
  record.new_building_ids = ["roof-eab27ea2"];
  const body = JSON.stringify(record);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.hilyard_apartments_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await page.route("**/scene/" + path, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
