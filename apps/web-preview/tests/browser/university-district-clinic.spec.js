import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const clinic = "roof-4c79682d";
const office = "roof-4a7d9b5a";
const garage = "university-district-650-e-12th-garage";
const packagePath = "university-district-clinic-review";
const targets = {
  [clinic]: ["PeaceHealth University District Clinic", "hilyard-entry"],
  [office]: ["University District North Building", "twelfth-avenue-entry"],
  [garage]: [
    "University District South Parking Garage",
    "thirteenth-avenue-entry",
  ],
};

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const { buildings, presentation } = window.__campus.getState();
    return {
      counts: [
        buildings,
        presentation.batchedBuildings,
        presentation.refinedContextRoofs,
      ],
      entries: window.__campus
        .entranceInfo()
        .filter(({ id }) => ids.includes(id))
        .map(({ id, name, gate, walkable }) => ({ id, name, gate, walkable })),
      blocks: [
        [-932.4, -108.25],
        [-933.2, -101.25],
        [-964.9, -124.96],
        [-963.65, -124.962],
        [-931.11, -98.6],
        [-931.11, -105.6],
        [-931.11, -112.15],
        [-930.98, -145],
        [-970, -113],
        [-984, -90],
      ].map(([x, z]) => window.__campus.collisionCheck(x, z)),
    };
  }, Object.keys(targets));
}

test("the clinic, South Garage and North Building have separate searchable approaches", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const after = await inspect(page);
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.entries).toHaveLength(3);
  for (const [id, [, gate]] of Object.entries(targets)) {
    expect(after.entries.find((entry) => entry.id === id)).toMatchObject({
      gate,
      walkable: true,
    });
  }
  expect(after.blocks).toEqual(
    Array(4).fill(false).concat(Array(6).fill(true)),
  );
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, [query]] of Object.entries(targets)) {
    await search.fill(query);
    if (isBackgroundBuilding(id)) {
      await expect(
        page.getByRole("option").filter({ hasText: query }),
      ).toHaveCount(0);
      continue;
    }
    await search.press("Enter");
    await expect
      .poll(() =>
        page.evaluate(() => window.__campus.getState().selectedBuilding),
      )
      .toBe(id);
  }
});

test("a shifted source anchor rolls back both ranges and the added garage identity", async ({
  page,
}) => {
  const before = await inspect(
    page,
    "/?exterior-review=university-district-clinic-baseline",
  );
  expect(before.counts).toEqual(exteriorCounts({ buildings: -1, batched: 2 }));
  expect(before.entries.some(({ id }) => id === garage)).toBe(false);
  const path = packagePath + "/site.json";
  const descriptor = await (await page.request.get("/scene/" + path)).json();
  descriptor.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.4;
  const body = JSON.stringify(descriptor);
  const hash = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const manifest = await response.json();
    manifest.university_district_clinic_site.sha256 = hash;
    await route.fulfill({ response, json: manifest });
  });
  await page.route("**/scene/" + path, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
