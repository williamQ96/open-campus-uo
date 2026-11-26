import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";

const readJson = (relative) =>
  JSON.parse(readFileSync(new URL(relative, import.meta.url), "utf8"));
const spec = readJson("../../../../data/metadata/pilot-hardscape-l2.json");
const descriptorPath = "../../public/scene/pilot-hardscape-review/site.json";

async function ready(page, url = "/") {
  await page.goto(url, { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

test("both library flights, Johnson stairs and the EMU tiers support the player", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await ready(page);
  const points = spec.flights.flatMap((flight) =>
    Array.from({ length: flight.treads }, (_, index) => {
      const { lowest_y, landing_y, bottom_north, landing_north, treads } =
        flight;
      return [
        flight.center_east,
        bottom_north +
          ((landing_north - bottom_north) * (index + 0.5)) / treads,
        lowest_y + ((landing_y - lowest_y) * (index + 1)) / treads,
      ];
    }),
  );
  const { center_enu_m, treads } = spec.amphitheater;
  for (const [inner, outer] of treads) {
    const radius = (inner + outer) / 2;
    const angle = (219 * Math.PI) / 180;
    points.push([
      center_enu_m[0] + radius * Math.cos(angle),
      center_enu_m[1] + radius * Math.sin(angle),
      null,
    ]);
  }
  points.push([-515.56, -186, null]);
  const rails = readJson(descriptorPath).collision_boxes_enu_m;
  const { samples, blocked, railCount, libraryPortals } = await page.evaluate(
    ({ points, rails }) => ({
      samples: points.map(([e, n]) => ({
        ...__campus.terrainCheck(e, -n),
        blocked: __campus.collisionCheck(e, -n),
      })),
      blocked: rails.map(([west, south, east, north]) =>
        __campus.collisionCheck((west + east) / 2, -(south + north) / 2),
      ),
      railCount: __campus.getState().presentation.hardscapeRailBoxes,
      libraryPortals: __campus
        .entranceInfo()
        .filter(({ id }) => id === "roof-6684e091")
        .map(({ ground }) => ground),
    }),
    { points, rails },
  );
  expect(railCount).toBe(6);
  expect(blocked).toEqual(Array(6).fill(true));
  expect(libraryPortals).toHaveLength(2);
  for (const [index, ground] of libraryPortals.entries())
    expect(ground).toBeCloseTo(spec.flights[index + 1].landing_y);
  for (const [index, sample] of samples.entries()) {
    expect(sample.blocked).toBe(false);
    expect(sample.hardscape).toBeGreaterThan(sample.sampled);
    expect(sample.standing).toBe(sample.hardscape);
    const expected = points[index][2];
    if (expected !== null)
      expect(Math.abs(sample.hardscape - expected)).toBeLessThan(0.02);
  }
});

test("a player can climb the library stairs from the front and stays on the ground at the tall side", async ({
  page,
}) => {
  const state = () => page.evaluate(() => __campus.getState());
  await page.addInitScript(() => {
    const side = new URL(location.href).searchParams.get("side") === "1";
    sessionStorage.setItem(
      "explorer:outdoor-return:v1",
      JSON.stringify({
        version: 1,
        buildingId: "roof-6684e091",
        player: side ? [-584.5, 0, 194.3] : [-578.5, 0, 188.08],
        view: "first",
        yaw: side ? -Math.PI / 2 : Math.PI,
        pitch: 0,
        followDistance: 7.5,
        density: 0,
      }),
    );
  });

  await ready(page, "/?return=1");
  expect((await state()).player[2]).toBeCloseTo(188.08);
  await page.keyboard.down("KeyW");
  try {
    await expect
      .poll(async () => (await state()).player[2])
      .toBeGreaterThan(190);
  } finally {
    await page.keyboard.up("KeyW");
  }
  const climbed = await state();
  expect(climbed.ground).toBeGreaterThan(5.7);
  expect(climbed.player[1]).toBeCloseTo(climbed.ground);

  await ready(page, "/?return=1&side=1");
  expect((await state()).player[0]).toBeCloseTo(-584.5);
  expect((await state()).player[2]).toBeCloseTo(194.3);
  const [below, above, open] = await page.evaluate(() => [
    __campus.terrainCheck(-582.15, 194.3).standing,
    __campus.terrainCheck(-581.85, 194.3).standing,
    !__campus.collisionCheck(-581.85, 194.3),
  ]);
  expect(open).toBe(true);
  expect(above - below).toBeGreaterThan(1);
  await page.keyboard.down("KeyW");
  try {
    await expect
      .poll(async () => (await state()).player[0])
      .toBeGreaterThan(-582.25);
    await page.evaluate(async () => {
      for (let i = 0; i < 25; i++)
        await new Promise((resolve) => requestAnimationFrame(resolve));
    });
    const side = await state();
    expect(side.player[0]).toBeLessThan(-581.97);
    expect(side.player[1]).toBeLessThan(above - 1);
  } finally {
    await page.keyboard.up("KeyW");
  }
});

test("a displaced final source anchor restores the original hardscape", async ({
  page,
}) => {
  const descriptor = readJson(descriptorPath);
  descriptor.cuts.at(-1).anchors[0][2][1] += 0.1;
  const body = JSON.stringify(descriptor);
  const config = readJson("../../public/scene/presentation.json");
  config.pilot_hardscape_site.sha256 = createHash("sha256")
    .update(body)
    .digest("hex");
  const state = () =>
    page.evaluate(() => ({
      gates: __campus.entranceInfo(),
      buildings: __campus.getState().buildings,
      rails: __campus.getState().presentation.hardscapeRailBoxes,
      tread: __campus.terrainCheck(-578.5, 191),
    }));
  await ready(page, "/?exterior-review=hardscape-baseline");
  const baseline = await state();
  const warning = page.waitForEvent("console", {
    predicate: (message) =>
      message.text().includes("A source hardscape anchor changed"),
  });
  await page.route("**/scene/presentation.json", (route) =>
    route.fulfill({ json: config }),
  );
  await page.route("**/pilot-hardscape-review/site.json", (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  await ready(page);
  await warning;
  expect(baseline.rails).toBe(0);
  expect(baseline.tread.hardscape).toBeUndefined();
  expect(await state()).toEqual(baseline);
});
