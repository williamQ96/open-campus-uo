import { expect, test } from "@playwright/test";
import { exteriorCounts, isBackgroundBuilding } from "./exterior-counts.js";

const targets = {
  "roof-62a81026": {
    name: "Bushnell University · 770 E 11th Ave",
    gate: "south-entry",
  },
  "roof-19858777": {
    name: "633 E 12th Avenue Parking Garage",
    gate: "street-approach",
  },
  "roof-bdbcb4fc": {
    name: "666 E 13th Avenue Parking Garage & Retail",
    gate: "retail-entry",
  },
};
const neighbor = "roof-ae986c58";

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(
    ({ ids, neighbor }) => {
      const { buildings, presentation } = window.__campus.getState();
      return {
        counts: [
          buildings,
          presentation.batchedBuildings,
          presentation.refinedContextRoofs,
        ],
        entries: window.__campus
          .entranceInfo()
          .filter(({ id }) => ids.includes(id) || id === neighbor)
          .map(({ id, name, gate, walkable }) => ({
            id,
            name,
            gate,
            walkable,
          })),
        open: [
          [-837, -189.8],
          [-841, -189.9],
          [-768, -214],
          [-836, -221],
        ].map(([x, z]) => !window.__campus.collisionCheck(x, z)),
        solid: [
          [-853.45, -190.44],
          [-851.35, -188.83],
          [-835.9, -190.4],
          [-815.65, -188.78],
          [-765, -198],
          [-996, -151],
          [-946, 24],
        ].map(([x, z]) => window.__campus.collisionCheck(x, z)),
      };
    },
    { ids: Object.keys(targets), neighbor },
  );
}

test("the paired Bushnell exteriors and garage approaches integrate with the phone viewer", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const state = await inspect(page);
  expect(state.counts).toEqual(exteriorCounts());
  expect(state.entries).toHaveLength(4);
  expect(state.entries).toEqual(
    expect.arrayContaining(
      Object.entries(targets).map(([id, { name, gate }]) => ({
        id,
        name,
        gate,
        walkable: true,
      })),
    ),
  );
  expect(state.entries.find(({ id }) => id === neighbor)?.walkable).toBe(true);
  expect(state.open).toEqual(Array(4).fill(true));
  expect(state.solid).toEqual(Array(7).fill(true));
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, { name }] of Object.entries(targets)) {
    await search.fill(name);
    if (isBackgroundBuilding(id)) {
      await expect(page.getByRole("option", { name, exact: true })).toHaveCount(
        0,
      );
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

test("a missing district mesh restores the three source members and keeps 722", async ({
  page,
}) => {
  const before = await inspect(
    page,
    "/?exterior-review=university-district-exterior-baseline",
  );
  expect(before.counts).toEqual(exteriorCounts({ batched: 3 }));
  await page.route(
    "**/scene/university-district-exterior-review/site.glb",
    (route) => route.fulfill({ status: 503 }),
  );
  const after = await inspect(page);
  expect(after).toEqual(before);
  expect(after.entries.find(({ id }) => id === neighbor)).toMatchObject({
    gate: "street-entry",
    walkable: true,
  });
  expect(
    after.entries
      .filter(({ id }) => Object.hasOwn(targets, id))
      .every(({ id, gate }) => gate !== targets[id].gate),
  ).toBe(true);
  const old = await inspect(
    page,
    "/?exterior-review=hilyard-west-exterior-baseline",
  );
  expect(old.counts).toEqual(exteriorCounts({ batched: 7 }));
  expect(old.entries.every(({ gate }) => !gate)).toBe(true);
});
