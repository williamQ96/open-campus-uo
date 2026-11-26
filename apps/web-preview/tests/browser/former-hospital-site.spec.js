import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const directory = "former-hospital-site-review";
const retired = [
  "roof-a3f76ab6",
  "roof-eb5ba9b8",
  "roof-8caa7792",
  "roof-6d2ad952",
  "roof-8e0e504c",
];

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((retired) => {
    const { buildings, presentation } = window.__campus.getState();
    return {
      counts: [
        buildings,
        presentation.batchedBuildings,
        presentation.refinedContextRoofs,
      ],
      historicEntrances: window.__campus
        .entranceInfo()
        .filter(({ id }) => retired.includes(id))
        .map(({ id }) => id)
        .sort(),
      adjacentEntrances: window.__campus
        .entranceInfo()
        .filter(({ id }) =>
          ["roof-4c79682d", "roof-ae986c58", "roof-bdbcb4fc"].includes(id),
        )
        .map(({ id, gate, walkable }) => ({ id, gate, walkable })),
      blocked: [
        [-882, -117],
        [-846, -151],
        [-845, -26],
        [-824, -72],
        [-899.6, -32],
        [-899.6, -149],
        [-916, -47],
        [-838, -11],
        [-754, -63],
      ].map(([x, z]) => window.__campus.collisionCheck(x, z)),
    };
  }, retired);
}

test("early construction replaces five old selections with the dated site perimeter", async ({
  page,
}) => {
  const before = await inspect(
    page,
    "/?exterior-review=former-hospital-site-baseline",
  );
  expect(before.counts).toEqual(exteriorCounts({ buildings: 5, batched: 5 }));
  expect(before.historicEntrances).toEqual([...retired].sort());

  const after = await inspect(page);
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.historicEntrances).toEqual([]);
  expect(after.adjacentEntrances).toEqual(before.adjacentEntrances);
  expect(after.adjacentEntrances.every(({ walkable }) => walkable)).toBe(true);
  expect(after.blocked).toEqual([
    false,
    false,
    true,
    true,
    true,
    true,
    false,
    false,
    false,
  ]);
  expect(before.blocked.slice(0, 6)).toEqual([
    true,
    true,
    true,
    true,
    false,
    false,
  ]);

  await page.locator("#directions-open").click();
  for (const [label, name] of [
    ["A", "666 E 13th Avenue Parking Garage & Retail"],
    ["B", "Bushnell University · 770 E 11th Ave"],
  ]) {
    await page
      .getByRole("button", { name: "Search " + label, exact: true })
      .click();
    const search = page.getByRole("combobox");
    await search.fill(name);
    await search.press("Enter");
  }
  await page.locator("#route-start").click();
  const path = await page.evaluate(
    () => window.__campus.getState().navigation.points,
  );
  expect(path.length).toBeGreaterThan(12);
  const info = await (
    await page.request.get("/scene/" + directory + "/site.json")
  ).json();
  const crossesClosedGround = await page.evaluate(
    async ({ path, boxes }) => {
      const { segmentHitsBoxes } = await import("/src/collision-supplement.js");
      return path.some(
        (point, i) => i && segmentHitsBoxes(path[i - 1], point, boxes, 0.5),
      );
    },
    { path, boxes: info.closed_site_boxes_enu_m },
  );
  expect(crossesClosedGround).toBe(false);
});

test("invalid construction bounds restore both the original geometry and walking area", async ({
  page,
}) => {
  const baseline = await inspect(
    page,
    "/?exterior-review=former-hospital-site-baseline",
  );
  const descriptorPath = directory + "/site.json";
  const bad = await (await page.request.get("/scene/" + descriptorPath)).json();
  bad.closed_site_boxes_enu_m[0][2] = bad.closed_site_boxes_enu_m[0][0] - 4;
  const body = JSON.stringify(bad);
  const hash = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const data = await response.json();
    data.former_hospital_site.sha256 = hash;
    await route.fulfill({ response, json: data });
  });
  await page.route("**/scene/" + descriptorPath, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(baseline);
});
