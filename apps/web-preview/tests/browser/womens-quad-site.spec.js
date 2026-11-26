import { expect, test } from "@playwright/test";

const susan = "roof-fd061857";
const hendricks = "roof-e145c222";
const legacy = "roof-6cd16f5c";

async function ready(page, path = "/") {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

const site = (ids) => ({
  buildings: __campus.getState().buildings,
  doors: __campus.entranceInfo().filter(({ id }) => ids.includes(id)),
  occupied: [
    [-439, 165],
    [-428, 156],
    [-366, 166],
    [-350, 155],
    [-338, 136],
    [-367, 152],
    [-446.536, 168.65],
    [-447.85, 169.79],
  ].map(([x, z]) => __campus.collisionCheck(x, z)),
});

const ids = [susan, hendricks, legacy];

test("the quad keeps two building identities and the combined Hendricks outline", async ({
  page,
}) => {
  await ready(page);
  const actual = await page.evaluate(site, ids);
  expect(actual.buildings).toBe(519);
  expect(actual.occupied).toEqual([
    true,
    false,
    true,
    true,
    true,
    false,
    true,
    false,
  ]);
  expect(
    actual.doors.map(({ id, gate, walkable }) => [id, gate, walkable]).sort(),
  ).toEqual(
    [
      [hendricks, "hendricks-quad-west", true],
      [hendricks, "hendricks-university-east", true],
      [susan, "susan-quad-east", true],
      [susan, "susan-west-porch", true],
    ].sort(),
  );
  for (const [name, id] of [
    ["Susan Campbell", susan],
    ["Hendricks Hall", hendricks],
  ]) {
    await page.getByRole("combobox", { name: "Search buildings" }).fill(name);
    await page
      .getByRole("option", { name: new RegExp(name) })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
  const clear = await page.evaluate(async () => {
    const graph = await fetch("/scene/navigation.json").then((r) => r.json());
    const end = graph.nodes_enu_m.findIndex(
      ([e, n]) => e === -447.85 && n === -169.79,
    );
    const [edge] = graph.edges.filter(([a, b]) => a === end || b === end);
    if (!edge) return false;
    const [a, b] = edge.map((i) => graph.nodes_enu_m[i]);
    return Array.from({ length: 9 }, (_, i) => i / 8).every(
      (t) =>
        !__campus.collisionCheck(
          a[0] + (b[0] - a[0]) * t,
          -(a[1] + (b[1] - a[1]) * t),
        ),
    );
  });
  expect(clear).toBe(true);
});

test("the Susan east approach enters and returns to the same building", async ({
  page,
}) => {
  await ready(page);
  await page.evaluate(() => {
    const door = __campus
      .entranceInfo()
      .find(({ gate }) => gate === "susan-quad-east");
    sessionStorage.setItem(
      "explorer:outdoor-return:v1",
      JSON.stringify({
        version: 1,
        buildingId: door.id,
        player: [door.approach[0], door.ground, door.approach[1]],
        view: "first",
        yaw: Math.atan2(door.outward[0], door.outward[1]),
        pitch: 0,
        followDistance: 7.5,
        density: 0,
      }),
    );
  });
  await ready(page, "/?return=1");
  await expect
    .poll(() => page.evaluate(() => __campus.getState().nearbyEntrance))
    .toBe(susan);
  const viewport = await page.locator("#viewport").boundingBox();
  await page.mouse.click(
    viewport.x + viewport.width / 2,
    viewport.y + viewport.height / 2,
  );
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe(susan);
});

test("damaged quad geometry keeps the two old Hendricks records and prior Susan model", async ({
  page,
}) => {
  await ready(page, "/?exterior-review=womens-baseline");
  const prior = await page.evaluate(site, ids);
  expect(new Set(prior.doors.map(({ id }) => id))).toEqual(new Set(ids));
  await page.route("**/womens-quad-review/site.glb", (route) =>
    route.fulfill({ body: "invalid quad GLB" }),
  );
  await ready(page);
  expect(await page.evaluate(site, ids)).toEqual(prior);
});
