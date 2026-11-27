import { expect, test } from "@playwright/test";
import {
  DEFAULT_PILOT_TREES,
  DEFAULT_SELECTABLE_BUILDINGS,
  EAST_THIRTEENTH_PILOT_TREE_REMOVALS,
} from "./exterior-counts.js";

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
      pilotTrees: campus.getState().presentation.refinedPilotTrees,
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
      westGatewayWalks: [
        [-628.81, 10.48],
        [-628.83, -6.75],
        [-617.08, 2.34],
        [-603, 9.17],
        [-546.25, 9.22],
      ].map(([x, north]) => [
        Number.isFinite(
          campus.terrainCheck(x, -north)["east-thirteenth-west-paving"],
        ),
        blocked(x, north),
      ]),
      westGatewaySolids: [
        [-617.06, 3.62],
        [-616.8, 14.39],
        [-617.1, -8.77],
        [-622.19, 15.49],
        [-554.6, 5.28],
        [-538.4, -2.4],
        [-537.22, 7.93],
      ].map(([x, north]) => blocked(x, north)),
      centralCorridorWalks: [
        [-510.94, 1.3],
        [-428.32, 0.88],
        [-374, -7.94],
        [-306.9, 0.9],
        [-306.51, -14.7],
      ].map(([x, north]) => [
        Number.isFinite(
          campus.terrainCheck(x, -north)["east-thirteenth-central-paving"],
        ),
        blocked(x, north),
      ]),
      centralCorridorSolids: [
        [-324.7, 3.7],
        [-286.5, 3.4],
        [-286.4, -4.45],
        [-312.48, -10.15],
        [-495.4, 20.86],
        [-313.0, 16.22],
      ].map(([x, north]) => blocked(x, north)),
      eastCorridorWalks: [
        [-235.8, -0.27],
        [-197.3, 0],
        [-109.55, 0.32],
        [89.2, 1.12],
        [127.6, -10.58],
        [178.45, -10.43],
        [227.9, -7.85],
      ].map(([x, north]) => {
        const terrain = campus.terrainCheck(x, -north);
        return [
          terrain["east-thirteenth-east-paving"] > terrain.sampled + 0.07,
          blocked(x, north),
        ];
      }),
      eastCorridorSolids: [
        [-239.0, 9.5],
        [-224.51, -7.1],
        [-165.45, -6.65],
        [-60.98, -6.1],
      ].map(([x, north]) => blocked(x, north)),
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
    pilotTrees: DEFAULT_PILOT_TREES,
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
    westGatewayWalks: Array(5).fill([true, false]),
    westGatewaySolids: Array(7).fill(true),
    centralCorridorWalks: Array(5).fill([true, false]),
    centralCorridorSolids: Array(6).fill(true),
    eastCorridorWalks: Array(7).fill([true, false]),
    eastCorridorSolids: Array(4).fill(true),
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
    /\/(?:pioneer-cemetery-landscape-review|fenton-site-review|howe-field-gates-review|dads-gates-landscape-review|east-thirteenth-west-gateway-review|east-thirteenth-central-review|east-thirteenth-east-review)\/site\.glb$/,
    (route) => route.fulfill({ body: "invalid site mesh" }),
  );
  expect(await landscapeState(page)).toMatchObject({
    pilotTrees: DEFAULT_PILOT_TREES + EAST_THIRTEENTH_PILOT_TREE_REMOVALS,
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
    westGatewayWalks: Array(5).fill([false, false]),
    westGatewaySolids: Array(7).fill(false),
    centralCorridorWalks: Array(5).fill([false, false]),
    centralCorridorSolids: Array(6).fill(false),
    eastCorridorWalks: Array(7).fill([false, false]),
    eastCorridorSolids: Array(4).fill(false),
    heritageWalks: Array(5).fill([false, false]),
    universitySign: false,
    helloWalk: Array(5).fill([false, false]),
  });
});
