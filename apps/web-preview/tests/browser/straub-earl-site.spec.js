import { expect, test } from "@playwright/test";

const halls = {
  "roof-5ded2bf0": "Straub Hall",
  "roof-f01c8434": "Earl Hall",
};
const absorbed = ["roof-303d99fd", "roof-aedc356a"];
const affected = [...Object.keys(halls), ...absorbed];
const baseline = "/?exterior-review=straub-baseline";

async function ready(page, path = "/") {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function inspect(affected) {
  const entries = __campus.entranceInfo();
  return {
    count: __campus.getState().buildings,
    gates: entries.filter(({ id }) => affected.includes(id)),
    neighbors: entries.filter(({ id }) => !affected.includes(id)),
    collision: [
      [-157.2, 155],
      [-157.2, 161.2],
      [-150.8, 149.3],
      [-138.4, 148.6],
      [-173.5, 220.6],
      [-174.8, 212.0],
    ].map(([e, z]) => __campus.collisionCheck(e, z)),
  };
}

test("Straub and Earl keep separate identities and the new set of entrances", async ({
  page,
}) => {
  await ready(page, baseline);
  const before = await page.evaluate(inspect, affected);
  await ready(page);
  const after = await page.evaluate(inspect, affected);
  expect(before.count).toBe(after.count + absorbed.length);
  expect(after.count).toBe(519);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.collision).toEqual([false, true, true, false, false, true]);
  expect(after.gates.map(({ gate, walkable }) => [gate, walkable])).toEqual([
    ["straub-west", true],
    ["straub-north", true],
    ["straub-south", true],
    ["earl-morton", true],
  ]);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const [id, name] of Object.entries(halls)) {
    await search.fill(name);
    await search.press("ArrowDown");
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe(id);
  }
});

for (const [id, gate] of [
  ["roof-5ded2bf0", "straub-west"],
  ["roof-5ded2bf0", "straub-north"],
  ["roof-5ded2bf0", "straub-south"],
  ["roof-f01c8434", "earl-morton"],
]) {
  test(`${gate} returns to its own modeled approach`, async ({ page }) => {
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
    await page.getByRole("button", { name: `Enter ${halls[id]}` }).click();
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

test("a failed Straub package restores both former meshes with their batch members", async ({
  page,
}) => {
  await ready(page, baseline);
  const before = await page.evaluate(inspect, affected);
  await page.route("**/straub-earl-review/site.glb", (route) =>
    route.fulfill({ body: "damaged GLB" }),
  );
  await ready(page);
  expect(await page.evaluate(inspect, affected)).toEqual(before);
});
