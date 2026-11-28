import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const names = {
  "roof-5f1a5ce2": "The Lewis",
  "roof-4cb05afd": "The Clark",
  "roof-175d8088": "Student Manor Apartments",
  "roof-57cd5529": "Royal Terrace",
  "roof-4855fc7e": "Coho Townhouses (North)",
};

async function inspect(page, path) {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const state = __campus.getState();
    return {
      counts: [
        state.buildings,
        state.presentation.batchedBuildings,
        state.presentation.refinedContextRoofs,
      ],
      buildings: __campus.namedBuildings().filter(({ id }) => ids.includes(id)),
      gates: __campus.entranceInfo().filter(({ id }) => ids.includes(id)),
      court: [
        [-989, 322],
        [-974, 325],
        [-981.45, 314],
        [-981.45, 323.3],
        [-982.87, 323.3],
      ].map(([x, z]) => __campus.collisionCheck(x, z)),
    };
  }, Object.keys(names));
}

test("five address-registered residences retain their IDs and Royal Terrace stays open", async ({
  page,
}) => {
  const current = await inspect(page, "/");
  expect(
    Object.fromEntries(current.buildings.map(({ id, name }) => [id, name])),
  ).toEqual(names);
  expect(current.counts).toEqual(exteriorCounts());
  expect(current.gates).toHaveLength(7);
  expect(current.gates.every(({ gate, walkable }) => gate && walkable)).toBe(
    true,
  );
  expect(current.court).toEqual([true, true, false, true, false]);

  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("Coho Townhouses (North)");
  await expect(
    page.getByRole("option", { name: "Coho Townhouses (North)", exact: true }),
  ).toHaveCount(0);
});

test("invalid residential mesh restores all five earlier roof treatments", async ({
  page,
}) => {
  const previous = await inspect(
    page,
    "/?exterior-review=residential-exterior-baseline",
  );
  await page.route("**/residential-exterior-review/site.glb", (route) =>
    route.fulfill({ body: "invalid residential exterior" }),
  );
  expect(await inspect(page, "/")).toEqual(previous);
  expect(previous.counts).toEqual(exteriorCounts({ batched: 5, roofs: 5 }));
  expect(previous.buildings).toEqual([]);
});
