import { test, expect } from "@playwright/test";

const museum = "roof-16751515";

async function ready(page, path = "/") {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function site() {
  return {
    buildings: __campus.getState().buildings,
    gates: __campus.entranceInfo().filter(({ id }) => id === "roof-16751515"),
    collision: [
      [-495, 135],
      [-496, 110],
      [-496, 160],
      [-496, 107],
      [-496, 163],
      [-518, 135],
      [-476, 135],
    ].map(([x, z]) => __campus.collisionCheck(x, z)),
    court: __campus.terrainCheck(-495, 135),
  };
}

test("museum stays selectable in both modes", async ({ page }) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.route(
    (url) => !["127.0.0.1", "localhost"].includes(url.hostname),
    (r) => r.abort(),
  );
  await ready(page);
  const state = () => page.evaluate(() => window.__campus.getState());
  await page
    .getByRole("combobox", { name: "Search buildings" })
    .fill("Jordan Schnitzer");
  await page
    .getByRole("option", { name: /Jordan Schnitzer/ })
    .first()
    .click();
  await expect.poll(async () => (await state()).selectedBuilding).toBe(museum);
  await page.getByRole("button", { name: "Settings / About" }).click();
  const toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  expect((await state()).selectedBuilding).toBe(museum);
  await toon.check();
  expect(errors).toEqual([]);
});

test("default museum exposes three courtyards and the west approach", async ({
  page,
}) => {
  await ready(page);
  const reviewed = await page.evaluate(site);
  expect(reviewed.collision).toEqual([
    false,
    false,
    false,
    true,
    true,
    true,
    true,
  ]);
  expect(reviewed.court["museum-paving"] - reviewed.court.sampled).toBeCloseTo(
    0.085,
    2,
  );
  const [{ gate, walkable, approach, ground }] = reviewed.gates;
  expect([gate, walkable]).toEqual(["museum-west", true]);
  await page.evaluate(
    ({ museum, approach, ground }) =>
      sessionStorage.setItem(
        "explorer:outdoor-return:v1",
        JSON.stringify({
          version: 1,
          buildingId: museum,
          player: [approach[0], ground, approach[1]],
          view: "first",
          yaw: -Math.PI / 2,
          pitch: 0,
          followDistance: 7.5,
          density: 0,
        }),
      ),
    { museum, approach, ground },
  );
  await ready(page, "/?return=1");
  await expect
    .poll(() => page.evaluate(() => __campus.getState().nearbyEntrance))
    .toBe(museum);
  const viewport = await page.locator("#viewport").boundingBox();
  await page.mouse.click(
    viewport.x + viewport.width / 2,
    viewport.y + viewport.height / 2,
  );
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe(museum);
});

test("a damaged museum package falls back to the previous site", async ({
  page,
}) => {
  await ready(page, "/?exterior-review=museum-baseline");
  const baseline = await page.evaluate(site);
  expect(baseline.collision[0]).toBe(true);
  await page.route("**/museum-exterior-review/site.glb", (route) =>
    route.fulfill({ body: "corrupt museum mesh" }),
  );
  await ready(page);
  expect(await page.evaluate(site)).toEqual(baseline);
});
