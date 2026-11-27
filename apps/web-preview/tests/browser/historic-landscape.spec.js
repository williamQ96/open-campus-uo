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
      greatLawnWalks: [
        [95.27, -110.63],
        [108.6, -118.92],
        [109.98, -118.52],
        [112.4, -115.4],
      ].map(([x, north]) => {
        const terrain = campus.terrainCheck(x, -north);
        return [
          terrain["great-lawn-oak-court"] > terrain.sampled + 0.12,
          blocked(x, north),
        ];
      }),
      greatLawnSolids: [
        [115.54, -117.1],
        [112.4, -114.31],
        [112.52, -117.14],
        [110.26, -112.46],
      ].map(([x, north]) => blocked(x, north)),
      agateWalks: [
        [89.72, -21.29],
        [98.86, -39.2],
        [76.67, -79.4],
        [84.37, -102.96],
        [89.529, -111.113],
        [95.28, -111.06],
        [88.86, -234.63],
        [77.3, -247.9],
      ].map(([x, north]) => {
        const terrain = campus.terrainCheck(x, -north);
        return [
          terrain["agate-thirteenth-fifteenth-paving"] > terrain.sampled + 0.07,
          blocked(x, north),
        ];
      }),
      agateSolids: [
        [89.55, -36.8],
        [86.72, -97.2],
        [89.764, -134.366],
        [79.65, -229.25],
      ].map(([x, north]) => blocked(x, north)),
      agateSouthWalks: [
        [73.8, -313.6],
        [100.62, -349],
        [90.12, -478.21],
        [90.25, -496.85],
        [89.41, -598.12],
        [100.37, -610.5],
        [64, -600.5],
        [102.69, -486.98],
      ].map(([x, north]) => {
        const terrain = campus.terrainCheck(x, -north);
        return [
          terrain["agate-fifteenth-eighteenth-paving"] > terrain.sampled + 0.07,
          blocked(x, north),
        ];
      }),
      agateSouthFixtures: [
        [78.79, -471.9],
        [97.76, -602.76],
        [104.41, -493.78],
        [97.35, -559.08],
      ].map(([x, north]) => blocked(x, north)),
      practiceSurfaces: [
        [-32.03, -599.69],
        [-79.1, -599.57],
        [-142.08, -599.65],
        [40, -543.07],
        [20.31, -570.36],
      ].map(([x, north]) => {
        const terrain = campus.terrainCheck(x, -north);
        return [
          terrain["hayward-practice-fields-ground"] > terrain.sampled + 0.05,
          blocked(x, north),
        ];
      }),
      practiceFences: [
        [40, -596.77],
        [-33.35, -596.84],
        [71.61, -560],
        [22, -541.4],
        [-110, -596.94],
      ].map(([x, north]) => blocked(x, north)),
      squareTrackGround: [
        [-243, -598.68],
        [-297.35, -590],
        [-309.38, -596.14],
        [-130, -485.6],
        [-69.5, -533],
        [-120.7, -514.5],
        [-120.7, -559],
      ].map(([x, north]) => {
        const terrain = campus.terrainCheck(x, -north);
        return [
          terrain["hayward-square-track-ground"] > terrain.sampled + 0.035,
          blocked(x, north),
        ];
      }),
      squareTrackSolids: [
        [-317.55, -589.12],
        [-301.34, -588.97],
        [-154.62, -549],
        [-35.29, -545],
        [-144.4, -520],
      ].map(([x, north]) => blocked(x, north)),
      universityAxisWalks: [
        [-321.94, -578.9],
        [-320.95, -506.5],
        [-318.93, -387.79],
        [-296.41, -481.41],
        [-297.69, -438.17],
        [-303.68, -252.63],
      ].map(([x, north]) => {
        const terrain = campus.terrainCheck(x, -north);
        return [
          terrain["university-south-axis-paving"] > terrain.sampled + 0.044,
          blocked(x, north),
        ];
      }),
      universityAxisFixtures: [
        [-320.42, -554.28],
        [-319.92, -506.5],
        [-297.43, -351.12],
        [-293.68, -535.2],
      ].map(([x, north]) => blocked(x, north)),
      haywardMidblockSurfaces: [
        [-121.9, -310],
        [-137.65, -394],
        [-137.2, -277],
        [-106, -441],
        [-211, -486.55],
        [-235.1, -487.78],
        [-137.3, -444.2],
        [-157.8, -490.8],
        [69.4, -480.14],
      ].map(([x, north]) => {
        const terrain = campus.terrainCheck(x, -north);
        return [
          terrain["hayward-midblock-paving"] > terrain.sampled + 0.045,
          blocked(x, north),
        ];
      }),
      haywardMidblockSolids: [
        [-110, -259.48],
        [-103.1, -254.59],
        [-235, -489.065],
        [-235, -486.505],
        [-107, -470.02],
      ].map(([x, north]) => blocked(x, north)),
      eastFifteenthSurfaces: [
        [-276.3, -244.9],
        [-259.0, -235.65],
        [-174, -245.4],
        [-119, -245.25],
        [-25.9, -239.53],
        [45.2, -245.2],
      ].map(([x, north]) => {
        const terrain = campus.terrainCheck(x, -north);
        return [
          terrain["east-fifteenth-hayward-paving"] > terrain.sampled + 0.046,
          blocked(x, north),
        ];
      }),
      eastFifteenthFixtures: [
        [-187.5, -249.6],
        [34.37, -251.43],
        [50.04, -255.83],
        [54.8, -271],
      ].map(([x, north]) => blocked(x, north)),
      rankinWalks: [
        [-435, -600.52],
        [-400, -600.57],
        [-346, -600.75],
        [-424, -589.7],
      ].map(([x, north]) => {
        const terrain = campus.terrainCheck(x, -north);
        return [
          terrain["pioneer-cemetery-paving"] > terrain.sampled + 0.04,
          blocked(x, north),
        ];
      }),
      rankinWalls: [
        [-459, -598.9],
        [-400, -599.02],
        [-327.1, -599.09],
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
    greatLawnWalks: Array(4).fill([true, false]),
    greatLawnSolids: Array(4).fill(true),
    agateWalks: Array(8).fill([true, false]),
    agateSolids: Array(4).fill(true),
    agateSouthWalks: Array(8).fill([true, false]),
    agateSouthFixtures: Array(4).fill(true),
    practiceSurfaces: Array(5).fill([true, false]),
    practiceFences: Array(5).fill(true),
    squareTrackGround: Array(7).fill([true, false]),
    squareTrackSolids: Array(5).fill(true),
    universityAxisWalks: Array(6).fill([true, false]),
    universityAxisFixtures: Array(4).fill(true),
    haywardMidblockSurfaces: Array(9).fill([true, false]),
    haywardMidblockSolids: Array(5).fill(true),
    eastFifteenthSurfaces: Array(6).fill([true, false]),
    eastFifteenthFixtures: Array(4).fill(true),
    rankinWalks: Array(4).fill([true, false]),
    rankinWalls: [true, false, true],
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
    /\/(?:pioneer-cemetery-landscape-review|fenton-site-review|howe-field-gates-review|dads-gates-landscape-review|east-thirteenth-west-gateway-review|east-thirteenth-central-review|east-thirteenth-east-review|great-lawn-landscape-review|agate-thirteenth-fifteenth-review|agate-fifteenth-eighteenth-review|hayward-practice-fields-review|hayward-square-track-review|university-south-axis-review|hayward-midblock-review|east-fifteenth-hayward-review)\/site\.glb$/,
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
    greatLawnWalks: Array(4).fill([false, false]),
    greatLawnSolids: Array(4).fill(false),
    agateWalks: Array(8).fill([false, false]),
    agateSolids: Array(4).fill(false),
    agateSouthWalks: Array(8).fill([false, false]),
    agateSouthFixtures: Array(4).fill(false),
    practiceSurfaces: Array(5).fill([false, false]),
    practiceFences: Array(5).fill(false),
    squareTrackGround: Array(7).fill([false, false]),
    squareTrackSolids: Array(5).fill(false),
    universityAxisWalks: Array(6).fill([false, false]),
    universityAxisFixtures: Array(4).fill(false),
    haywardMidblockSurfaces: Array(9).fill([false, false]),
    haywardMidblockSolids: Array(5).fill(false),
    eastFifteenthSurfaces: Array(6).fill([false, false]),
    eastFifteenthFixtures: Array(4).fill(false),
    rankinWalks: Array(4).fill([false, false]),
    rankinWalls: Array(3).fill(false),
    heritageWalks: Array(5).fill([false, false]),
    universitySign: false,
    helloWalk: Array(5).fill([false, false]),
  });
});
