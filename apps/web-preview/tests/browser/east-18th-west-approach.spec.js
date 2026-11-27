import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readApproach(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    return {
      buildings: campus.getState().buildings,
      crossings: [
        [-566.38, 607.5],
        [-548.05, 607.7],
        [-697.85, 593.9],
      ].map(([e, z]) => [
        campus.terrainCheck(e, z)["east-18th-west-paving"] ?? null,
        campus.collisionCheck(e, z),
      ]),
      bed: campus.collisionCheck(-542, 601.9),
      cemetery: Number.isFinite(
        campus.terrainCheck(-511.5, 600.25)["pioneer-cemetery-paving"],
      ),
      clinic: campus
        .entranceInfo()
        .some((entry) => entry.id === "roof-c1ff8b83" && entry.walkable),
    };
  });
}

test("a damaged East 18th bundle leaves the cemetery frontage and clinic entrance available", async ({
  page,
}) => {
  expect(await readApproach(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    crossings: Array(3).fill([expect.any(Number), false]),
    bed: true,
    cemetery: true,
    clinic: true,
  });

  await page.route(
    "**/east-eighteenth-west-approach-review/site.glb",
    (route) => route.fulfill({ body: "invalid East 18th paving" }),
  );

  expect(await readApproach(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    crossings: Array(3).fill([null, false]),
    bed: false,
    cemetery: true,
    clinic: true,
  });
});

test("East 18th falls back when the pinned clinic site cannot install", async ({
  page,
}) => {
  await page.route("**/public-building-exterior-review/site.glb", (route) =>
    route.fulfill({ body: "invalid clinic host" }),
  );
  expect(await readApproach(page)).toMatchObject({
    crossings: Array(3).fill([null, false]),
    bed: false,
  });
});
