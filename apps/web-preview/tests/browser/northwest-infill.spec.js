import { expect, test } from "@playwright/test";
import {
  DEFAULT_BATCHED_BUILDINGS,
  DEFAULT_SELECTABLE_BUILDINGS,
} from "./exterior-counts.js";

const labels = {
  "roof-8007cb2f": "Phi Kappa Psi Chapter House",
  "roof-3961d925": "642 East 8th Avenue",
  "roof-d830368a": "1414 Alder Street / 790 E 14th Ave",
  "roof-ec27d788": "Eugene Steam Plant",
};

async function load(page) {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

async function registered(page) {
  return page.evaluate((ids) => {
    const campus = window.__campus;
    return Object.fromEntries(
      campus
        .namedBuildings()
        .filter(({ id }) => ids.includes(id))
        .map(({ id, name }) => [id, name]),
    );
  }, Object.keys(labels));
}

test("four northwest exteriors preserve selection and their open bays", async ({
  page,
}) => {
  await load(page);
  expect(await registered(page)).toEqual(labels);
  const details = await page.evaluate((ids) => {
    const c = window.__campus;
    return {
      solids: [
        [-862, -278],
        [-974, -574],
        [-788, 141],
        [-980.8, -744.6],
      ].map(([e, z]) => c.collisionCheck(e, z)),
      recesses: [
        [-854, -274.25],
        [-968.9, -592.7],
        [-771, 141.2],
      ].map(([e, z]) => c.collisionCheck(e, z)),
      gates: c.entranceInfo().filter(({ id }) => ids.includes(id)),
      buildings: c.getState().buildings,
    };
  }, Object.keys(labels));
  expect(details.buildings).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(details.solids).toEqual([true, true, true, true]);
  expect(details.recesses).toEqual([false, false, false]);
  expect(details.gates).toMatchObject([
    { id: "roof-8007cb2f", gate: "phi-psi-south-arcade", estimated: true },
  ]);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("790 E 14th Ave");
  await expect(
    page.getByRole("option").filter({ hasText: "1414 Alder Street" }),
  ).toHaveCount(0);
});

test("a rejected northwest site keeps the original building batch", async ({
  page,
}) => {
  await page.route("**/northwest-infill-exterior-review/site.glb", (route) =>
    route.fulfill({ status: 200, body: "damaged" }),
  );
  await load(page);
  expect(await registered(page)).toEqual({});
  const state = await page.evaluate(() => window.__campus.getState());
  expect(state.buildings).toBe(DEFAULT_SELECTABLE_BUILDINGS);
  expect(state.presentation.batchedBuildings).toBe(
    DEFAULT_BATCHED_BUILDINGS + Object.keys(labels).length,
  );
});
