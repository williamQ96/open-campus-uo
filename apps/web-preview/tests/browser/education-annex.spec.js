import { expect, test } from "@playwright/test";
import {
  DEFAULT_ENTRANCES,
  DEFAULT_SELECTABLE_BUILDINGS,
} from "./exterior-counts.js";

const annexId = "uo-education-annex";

async function readAnnex(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((id) => {
    const campus = window.__campus;
    const { buildings, entranceCount } = campus.getState();
    return {
      buildings,
      entranceCount,
      entrance: campus.entranceInfo().find((e) => e.id === id) ?? null,
      ramp:
        campus.terrainCheck(-608.215, 420)["education-annex-approach"] ?? null,
      rampClear: !campus.collisionCheck(-608.215, 420),
      railBlocked: campus.collisionCheck(-608.81, 420),
      plaza: campus.terrainCheck(-630.5, 395)["kendall-plaza-paving"] ?? null,
    };
  }, annexId);
}

test("the Education Annex is selectable and its failed pack leaves the plaza open", async ({
  page,
}) => {
  const active = await readAnnex(page);
  expect(active).toMatchObject({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    entranceCount: DEFAULT_ENTRANCES,
    entrance: { id: annexId, walkable: true },
    rampClear: true,
    railBlocked: true,
  });
  expect(active.ramp).toBeGreaterThan(10.3);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("Education Annex");
  await page.getByRole("option", { name: "Education Annex" }).click();
  await expect(page.locator(".building-card").getByRole("heading")).toHaveText(
    "Education Annex",
  );
  await page.route("**/education-annex-review/site.glb", (route) =>
    route.fulfill({ body: "damaged Education Annex mesh" }),
  );
  expect(await readAnnex(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS - 1,
    entranceCount: DEFAULT_ENTRANCES - 1,
    ramp: null,
    rampClear: true,
    railBlocked: false,
    entrance: null,
    plaza: active.plaza,
  });
});
