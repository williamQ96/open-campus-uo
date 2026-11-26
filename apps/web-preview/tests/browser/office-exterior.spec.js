import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const names = {
  "roof-17c233f0": "UO Annex",
  "roof-b8f94f8e": "Rainier Building",
  "roof-3c2b8bdc": "1311 Franklin",
  "roof-7c1c7fb1": "University Business Operations Center",
  "roof-bb20ea46": "1715 Franklin",
};

async function inspect(page, path) {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const state = __campus.getState();
    return {
      names: Object.fromEntries(
        __campus
          .namedBuildings()
          .filter(({ id }) => ids.includes(id))
          .map(({ id, name }) => [id, name]),
      ),
      entrances: __campus.entranceInfo().filter(({ id }) => ids.includes(id)),
      openCourt: !__campus.collisionCheck(239, -115),
      courtWing: __campus.collisionCheck(255, -113),
      roofs: state.presentation.refinedContextRoofs,
      batches: state.presentation.batchedBuildings,
      buildings: state.buildings,
    };
  }, Object.keys(names));
}

test("the five office exteriors preserve the courtyard and selection census", async ({
  page,
}) => {
  const current = await inspect(page, "/");
  expect(current.names).toEqual(names);
  expect(current.entrances).toHaveLength(6);
  expect(
    current.entrances.every(({ gate, walkable }) => gate && walkable),
  ).toBe(true);
  expect(current.openCourt && current.courtWing).toBe(true);
  expect([current.buildings, current.batches, current.roofs]).toEqual(
    exteriorCounts(),
  );
});

test("the older Alder facade and the remaining roof caps survive the office replacement", async ({
  page,
}) => {
  const current = await inspect(
    page,
    "/?exterior-review=campus-frontage-baseline",
  );
  expect(current.names).toEqual(names);
  expect([current.buildings, current.batches, current.roofs]).toEqual(
    exteriorCounts({ batched: 4 }),
  );
  const alder = await page.evaluate(() =>
    __campus.entranceInfo().filter(({ id }) => id === "roof-ee63827c"),
  );
  expect(alder).toHaveLength(1);
  expect(alder[0].gate).toBeUndefined();
  expect(alder[0].walkable).toBe(true);
});

test("invalid office mesh bytes restore the 1311 Franklin roof and the earlier identities", async ({
  page,
}) => {
  const prior = await inspect(
    page,
    "/?exterior-review=office-exterior-baseline",
  );
  await page.route("**/office-exterior-review/site.glb", (route) =>
    route.fulfill({ body: "damaged offices" }),
  );
  expect(await inspect(page, "/")).toEqual(prior);
  expect([prior.buildings, prior.batches, prior.roofs]).toEqual(
    exteriorCounts({ batched: 5, roofs: 1 }),
  );
});
