import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const names = {
  "roof-4286ad30": "Coho Townhouses (South)",
  "roof-2cbfcd06": "Pi Kappa Alpha House",
  "roof-e17be27c": "Christus House",
  "roof-f89a9211": "St. Thomas More Newman Center",
  "roof-cea1e466": "Hayward House Apartments",
  "roof-04683fef": "Aldersgate Apartments",
  "roof-5e7ce49c": "The 1840",
};

async function ready(page, path = "/") {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

async function inspect(page, path) {
  await ready(page, path);
  return page.evaluate((ids) => {
    const state = __campus.getState();
    const names = Object.fromEntries(
      __campus
        .namedBuildings()
        .filter(({ id }) => ids.includes(id))
        .map(({ id, name }) => [id, name]),
    );
    const entrances = __campus
      .entranceInfo()
      .filter(({ id }) => ids.includes(id));
    const groundPassages = [
      [-655, 194],
      [-652, 204],
      [-219, 632],
      [-227, 623.4],
      [-781, 166],
      [-779, 173.45],
    ].map(([x, z]) => __campus.collisionCheck(x, z));
    return {
      counts: [
        state.buildings,
        state.presentation.batchedBuildings,
        state.presentation.refinedContextRoofs,
      ],
      names,
      entrances,
      groundPassages,
    };
  }, Object.keys(names));
}

test("seven campus neighbors are searchable and preserve exterior approaches", async ({
  page,
}) => {
  const adopted = await inspect(page, "/");
  expect(adopted.counts).toEqual(exteriorCounts());
  expect(adopted.names).toEqual(names);
  expect(adopted.entrances).toHaveLength(7);
  expect(
    adopted.entrances.every(({ gate, walkable }) => gate && walkable),
  ).toBe(true);
  expect(adopted.groundPassages).toEqual([
    true,
    false,
    true,
    false,
    true,
    false,
  ]);

  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill(names["roof-4286ad30"]);
  await expect(
    page.getByRole("option").filter({ hasText: "Coho Townhouses (South)" }),
  ).toHaveCount(0);
});

test("Hayward's raised gallery entrance returns to the approach at street grade", async ({
  page,
}) => {
  await ready(page);
  const point = await page.evaluate(() => {
    const entry = __campus
      .entranceInfo()
      .find(({ gate }) => gate === "balcony-entry");
    const player = [entry.approach[0], entry.ground, entry.approach[1]];
    sessionStorage.setItem(
      "explorer:outdoor-return:v1",
      JSON.stringify({
        version: 1,
        buildingId: entry.id,
        player,
        view: "first",
        yaw: Math.atan2(entry.outward[0], entry.outward[1]),
        pitch: 0,
        followDistance: 7.5,
        density: 0,
      }),
    );
    return { player, threshold: entry.thresholdZ };
  });
  expect(point.threshold - point.player[1]).toBeGreaterThan(1);
  await ready(page, "/?return=1");
  await expect
    .poll(() => page.evaluate(() => __campus.getState().nearbyEntrance))
    .toBe("roof-cea1e466");
  await page
    .getByRole("button", { name: "Enter Hayward House Apartments" })
    .click();
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe("roof-cea1e466");
  const [x, , z] = await page.evaluate(() => __campus.getState().player);
  expect(x).toBeCloseTo(point.player[0], 1);
  expect(z).toBeCloseTo(point.player[2], 1);
});

test("invalid neighbor mesh restores the seven earlier roof treatments and source ranges", async ({
  page,
}) => {
  const before = await inspect(
    page,
    "/?exterior-review=campus-neighbor-exterior-baseline",
  );
  await page.route("**/campus-neighbor-exterior-review/site.glb", (route) =>
    route.fulfill({ body: "invalid neighbor exterior" }),
  );
  expect(await inspect(page, "/")).toEqual(before);
  expect(before.counts).toEqual(exteriorCounts({ batched: 7, roofs: 7 }));
  expect(before.names).toEqual({});
});
