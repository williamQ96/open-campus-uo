import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function readEastDrive(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    return {
      buildings: campus.getState().buildings,
      drive: [
        [-532.8, -435],
        [-534.1, -508],
        [-539, -572],
      ].map(([e, n]) =>
        Number.isFinite(
          campus.terrainCheck(e, -n)["frohnmayer-east-drive-paving"],
        ),
      ),
      islands: [
        [-532.38, -567.27],
        [-533.1, -580.37],
      ].map(([e, n]) => campus.collisionCheck(e, -n)),
      walksClear: [
        [-557.61, -585.06],
        [-532.57, -593.35],
      ].every(([e, n]) => !campus.collisionCheck(e, -n)),
      street: Number.isFinite(
        campus.terrainCheck(-535.24, 600.22)["east-18th-west-paving"],
      ),
      cemetery: Number.isFinite(
        campus.terrainCheck(-518.5, 572)["pioneer-cemetery-paving"],
      ),
    };
  });
}

test("the east drive and its parking islands fall back without losing the street or cemetery", async ({
  page,
}) => {
  expect(await readEastDrive(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    drive: [true, true, true],
    islands: [true, true],
    walksClear: true,
    street: true,
    cemetery: true,
  });

  await page.route("**/frohnmayer-east-drive-review/site.glb", (route) =>
    route.fulfill({ body: "invalid Frohnmayer paving" }),
  );

  expect(await readEastDrive(page)).toEqual({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    drive: [false, false, false],
    islands: [false, false],
    walksClear: true,
    street: true,
    cemetery: true,
  });
});

test("the Frohnmayer bundle falls back when the East 18th connection fails", async ({
  page,
}) => {
  await page.route(
    "**/east-eighteenth-west-approach-review/site.glb",
    (route) => route.fulfill({ body: "invalid East 18th paving" }),
  );

  expect(await readEastDrive(page)).toMatchObject({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    drive: [false, false, false],
    islands: [false, false],
    street: false,
    cemetery: true,
  });
});
