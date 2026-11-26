import { expect, test } from "@playwright/test";

const hallNames = {
  "roof-57a37f8e": "Lawrence Hall",
  "uo-035": "Pacific Hall",
  "uo-036": "Columbia Hall",
};
const affectedIds = [
  ...Object.keys(hallNames),
  "roof-4041562c",
  "roof-64589bec",
  "roof-21450e38",
];

async function ready(page, path = "/") {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function inspect({ names, affected }) {
  const entries = __campus.entranceInfo();
  return {
    count: __campus.getState().buildings,
    names: Object.fromEntries(
      __campus
        .namedBuildings()
        .filter(({ name }) => Object.values(names).includes(name))
        .map(({ id, name }) => [id, name]),
    ),
    entries: entries.filter(({ id }) => affected.includes(id)),
    neighbors: entries.filter(({ id }) => !affected.includes(id)),
    collision: [
      [-340, -173],
      [-353, -184],
      [-339, -161],
      [-269, -54],
      [-269, -48],
      [-269, -63],
    ].map(([e, z]) => __campus.collisionCheck(e, z)),
  };
}

const inspectArgs = { names: hallNames, affected: affectedIds };
const baseline = "/?exterior-review=science-baseline";

test("science halls have registered identities, an open courtyard, and a walkable underpass", async ({
  page,
}) => {
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    delete json.northeast_science_site;
    delete json.hayward_exterior_site;
    await route.fulfill({ response, json });
  });
  await ready(page, baseline);
  const before = await page.evaluate(inspect, inspectArgs);
  await ready(page);
  const after = await page.evaluate(inspect, inspectArgs);
  expect(after.count).toBe(before.count + 1);
  expect(after.names).toEqual(hallNames);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.entries.some(({ id }) => id === "roof-21450e38")).toBe(false);
  expect(after.collision).toEqual([false, true, true, false, true, true]);
  expect(
    after.entries
      .filter(({ gate }) => gate)
      .map(({ gate, walkable }) => [gate, walkable]),
  ).toEqual([
    ["lawrence-west", true],
    ["lawrence-east", true],
    ["lawrence-south", true],
    ["pacific-west", true],
    ["columbia-south", true],
  ]);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(hallNames)) {
    await search.fill(name);
    await page.getByRole("option", { name }).first().click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

for (const [id, gate] of [
  ["roof-57a37f8e", "lawrence-west"],
  ["uo-035", "pacific-west"],
  ["uo-036", "columbia-south"],
]) {
  test(`${hallNames[id]} returns to its modeled approach`, async ({ page }) => {
    await ready(page);
    const point = await page.evaluate((gate) => {
      const entry = __campus.entranceInfo().find((item) => item.gate === gate);
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
      return player;
    }, gate);
    await ready(page, "/?return=1");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().nearbyEntrance))
      .toBe(id);
    await page.getByRole("button", { name: `Enter ${hallNames[id]}` }).click();
    await page.waitForFunction(() => window.__interior?.getState().ready);
    await page.getByRole("button", { name: /Return to campus/ }).click();
    await expect
      .poll(() =>
        page.evaluate(() => window.__campus?.getState().nearbyEntrance),
      )
      .toBe(id);
    const [e, , z] = await page.evaluate(() => __campus.getState().camera);
    expect(e).toBeCloseTo(point[0], 1);
    expect(z).toBeCloseTo(point[2], 1);
  });
}

test("damaged science geometry restores the prior geometry and identity bindings together", async ({
  page,
}) => {
  await ready(page, baseline);
  const before = await page.evaluate(inspect, inspectArgs);
  await page.route("**/lawrence-science-review/site.glb", (route) =>
    route.fulfill({ body: "invalid science mesh" }),
  );
  await ready(page);
  expect(await page.evaluate(inspect, inspectArgs)).toEqual(before);
});
