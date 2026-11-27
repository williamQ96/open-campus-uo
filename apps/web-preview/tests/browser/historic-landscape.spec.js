import { expect, test } from "@playwright/test";
import { DEFAULT_SELECTABLE_BUILDINGS } from "./exterior-counts.js";

async function landscapeState(page) {
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const blocked = (x, north) => campus.collisionCheck(x, -north);
    const paved = (x, north) => {
      const { sampled, standing } = campus.terrainCheck(x, -north);
      return standing - sampled > 0.07;
    };
    return {
      buildings: campus.getState().buildings,
      vault: blocked(-391.05, -534.51),
      vaultApproach: blocked(-388.5, -535.2),
      cherryAvenue: blocked(-391.2, -542.5),
      fountain: blocked(-446.52, 79.19),
      bubbler: blocked(-426.15, 26.4),
      howeWalls: [
        [-287.85, -472],
        [-290.0, -478.5],
        [-292.65, -485.6],
      ].map(([x, north]) => blocked(x, north)),
      howeOpenings: [
        [-288.5, -476.42],
        [-291.56, -481.33],
      ].map(([x, north]) => blocked(x, north)),
      howePlanter: blocked(-251.78, -501.58),
      howePlaza: [paved(-278, -494), blocked(-278, -494)],
      dadsGateOpenings: [
        [-544.94, 221.84],
        [-555.91, 221.84],
        [-534.71, 221.84],
      ].map(([x, north]) => [paved(x, north), blocked(x, north)]),
      dadsGateIronwork: [
        [-551.2, 221.84],
        [-538.1, 221.84],
        [-548.08, 220.04],
        [-541.9, 220.04],
      ].map(([x, north]) => blocked(x, north)),
      normalGateSupport: blocked(-520.23, 157.57),
      southernAxis: [
        [-545.66, 148.284],
        [-531.49, 153.54],
        [-528.12, 161.15],
        [-546.01, 101.05],
        [-548.03, 89.15],
      ].map(([x, north]) => [paved(x, north), blocked(x, north)]),
      heritageWalks: [
        [-452.5, 108.8],
        [-479.4, 129],
        [-448.3, 156.9],
        [-431.5, 179],
        [-461.5, 165.94],
      ].map(([x, north]) => [paved(x, north), blocked(x, north)]),
      universitySign: blocked(-432.93, 117.92),
      villardTreads: Array.from({ length: 5 }, (_, index) => {
        const { sampled, standing } = campus.terrainCheck(
          -448.29,
          -(164.4 + ((index + 0.5) * 1.56) / 5),
        );
        return { sampled, standing };
      }),
      helloWalk: [
        [-428.55, 8.1],
        [-428.75, 31],
        [-454.13, 85],
        [-451.52, 80],
        [-446.22, 70],
      ].map(([x, north]) => [paved(x, north), blocked(x, north)]),
    };
  });
}

test("historic landscape solids leave Cherry Avenue and Hello Walk open", async ({
  page,
}) => {
  const state = await landscapeState(page);
  expect(state).toMatchObject({
    buildings: DEFAULT_SELECTABLE_BUILDINGS,
    vault: true,
    vaultApproach: false,
    cherryAvenue: false,
    fountain: true,
    bubbler: true,
    howeWalls: [true, true, true],
    howeOpenings: [false, false],
    howePlanter: true,
    howePlaza: [true, false],
    dadsGateOpenings: Array(3).fill([true, false]),
    dadsGateIronwork: Array(4).fill(true),
    normalGateSupport: true,
    southernAxis: Array(5).fill([true, false]),
    heritageWalks: Array(5).fill([true, false]),
    universitySign: true,
    helloWalk: Array(5).fill([true, false]),
  });
  expect(
    state.villardTreads.every(
      ({ sampled, standing }, i, rows) =>
        standing > sampled + 0.1 &&
        (i === 0 || standing > rows[i - 1].standing),
    ),
  ).toBe(true);
});

test("failed historic site bundles restore the preceding ground and access", async ({
  page,
}) => {
  await page.route(
    /\/(?:pioneer-cemetery-landscape-review|fenton-site-review|howe-field-gates-review|dads-gates-landscape-review)\/site\.glb$/,
    (route) => route.fulfill({ body: "invalid site mesh" }),
  );
  expect(await landscapeState(page)).toMatchObject({
    vault: false,
    vaultApproach: false,
    cherryAvenue: false,
    fountain: false,
    bubbler: false,
    howeWalls: [false, false, false],
    howeOpenings: [false, false],
    howePlanter: false,
    howePlaza: [false, false],
    dadsGateOpenings: Array(3).fill([false, false]),
    dadsGateIronwork: Array(4).fill(false),
    normalGateSupport: false,
    southernAxis: Array(5).fill([false, false]),
    heritageWalks: Array(5).fill([false, false]),
    universitySign: false,
    helloWalk: Array(5).fill([false, false]),
  });
});
