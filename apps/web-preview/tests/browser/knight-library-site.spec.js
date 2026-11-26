import { expect, test } from "@playwright/test";

const knight = "roof-6684e091";
const review = "/";
const baseline = "/?exterior-review=knight-baseline";

async function ready(page, url = review) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

const read = (id) => ({
  buildings: __campus.getState().buildings,
  roofs: __campus.getState().presentation.refinedContextRoofs,
  gates: __campus.entranceInfo().filter((gate) => gate.id === id),
  solid: [
    [-606, 198],
    [-541, 200],
    [-577, 201],
    [-523, 288],
  ].map(([x, z]) => __campus.collisionCheck(x, z)),
});

test("the library review registers the building outline and both north portals", async ({
  page,
}) => {
  await ready(page, baseline);
  const original = await page.evaluate(read, knight);
  expect(original.gates).toHaveLength(1);
  expect(original.solid).toEqual([false, false, true, false]);
  await ready(page);
  const revised = await page.evaluate(read, knight);
  expect(revised.buildings).toBe(original.buildings);
  expect(revised.roofs).toBe(original.roofs);
  expect(revised.solid).toEqual([false, false, true, true]);
  expect(
    revised.gates.map(({ gate, estimated, walkable }) => [
      gate,
      estimated,
      walkable,
    ]),
  ).toEqual([
    ["memorial-west", true, true],
    ["memorial-east", true, true],
  ]);
  for (const { position, approach } of revised.gates)
    expect(position[1]).toBeGreaterThan(approach[1]);
});

for (const [side, action] of [
  ["west", "pointer"],
  ["east", "keyboard"],
]) {
  test(`the ${side} portal opens the local interior by ${action} and returns to the review`, async ({
    page,
  }) => {
    await ready(page);
    await page.evaluate((side) => {
      const door = __campus
        .entranceInfo()
        .find(({ gate }) => gate === `memorial-${side}`);
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
    }, side);
    await ready(page, "/?return=1");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().nearbyEntrance))
      .toBe(knight);
    if (action === "pointer") {
      const viewport = await page.locator("#viewport").boundingBox();
      await page.mouse.click(
        viewport.x + viewport.width / 2,
        viewport.y + viewport.height / 2,
      );
    } else {
      await page.keyboard.press("KeyE");
    }
    await page.waitForFunction(() => window.__interior?.getState().ready);
    await page.getByRole("button", { name: /Return to campus/ }).click();
    await page.waitForFunction(
      (id) => window.__campus?.getState().nearbyEntrance === id,
      knight,
    );
    expect(new URL(page.url()).searchParams.has("exterior-review")).toBe(false);
  });
}

test("a damaged Knight review GLB reverts to the existing geometry and entrance", async ({
  page,
}) => {
  await ready(page, baseline);
  const original = await page.evaluate(read, knight);
  const warning = page.waitForEvent("console", {
    predicate: (entry) => entry.text().includes("using the prior site"),
  });
  await page.route("**/knight-library-review/site.glb", (route) =>
    route.fulfill({ body: "changed" }),
  );
  await ready(page);
  await warning;
  expect(await page.evaluate(read, knight)).toEqual(original);
});
