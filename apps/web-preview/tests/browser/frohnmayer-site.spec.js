import { expect, test } from "@playwright/test";

const review = "/";
const music = "roof-e4a5429f";
const aliases = ["roof-cd7b6d76", "roof-fcd40d9f"];

async function ready(page, url = review) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

const readSite = (ids) => ({
  count: __campus.getState().buildings,
  gates: __campus.entranceInfo().filter((item) => ids.includes(item.id)),
  roofCount: __campus.getState().presentation.refinedContextRoofs,
  collides: [
    [-586, 527],
    [-556, 548],
    [-555, 450],
    [-604, 573],
    [-559, 526],
  ].map(([x, z]) => __campus.collisionCheck(x, z)),
  ground: __campus.terrainCheck(-586, 527),
});

test("the music review joins the wings, keeps the courtyard open and installs the two modeled gates", async ({
  page,
}) => {
  await ready(page, "/?exterior-review=music-baseline");
  const ids = [music, ...aliases];
  const baseline = await page.evaluate(readSite, ids);
  expect(baseline.gates.map(({ id }) => id).sort()).toEqual(ids.sort());
  expect(baseline.collides).toEqual([false, false, true, true, true]);
  await ready(page);
  const site = await page.evaluate(readSite, ids);
  expect(site.count).toBe(baseline.count - 2);
  expect(site.collides).toEqual([false, true, true, true, true]);
  expect(site.ground["music-paving"] - site.ground.sampled).toBeCloseTo(
    0.12,
    3,
  );
  expect(
    site.gates.map(({ id, gate, walkable }) => [id, gate, walkable]),
  ).toEqual([
    [music, "beall-west", true],
    [music, "music-south", true],
  ]);
  expect(site.roofCount).toBe(baseline.roofCount);
});

test("the Beall approach opens the campus interior preview and returns to the same music review", async ({
  page,
}) => {
  await ready(page);
  await page.evaluate(() => {
    const door = __campus
      .entranceInfo()
      .find(({ gate }) => gate === "beall-west");
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
  await ready(page, review + "?return=1");
  await expect
    .poll(() => page.evaluate(() => __campus.getState().nearbyEntrance))
    .toBe(music);
  const viewport = await page.locator("#viewport").boundingBox();
  await page.mouse.click(
    viewport.x + viewport.width / 2,
    viewport.y + viewport.height / 2,
  );
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe(music);
  expect(new URL(page.url()).search).toBe("");
});

test("a failed music mesh check retains the old wings, collisions and background roofs", async ({
  page,
}) => {
  await ready(page, "/?exterior-review=music-baseline");
  const ids = [music, ...aliases];
  const baseline = await page.evaluate(readSite, ids);
  await page.route("**/frohnmayer-exterior-review/site.glb", (route) =>
    route.fulfill({ body: "corrupt music mesh" }),
  );
  await ready(page);
  expect(await page.evaluate(readSite, ids)).toEqual(baseline);
});
