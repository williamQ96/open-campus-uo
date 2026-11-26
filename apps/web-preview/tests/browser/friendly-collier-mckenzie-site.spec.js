import { expect, test } from "@playwright/test";

const baseline = "/?exterior-review=friendly-collier-mckenzie-baseline";
const ids = ["roof-556799cc", "roof-e5accf83", "roof-f61e9b20"];

async function read(page, url) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const state = __campus.getState();
    const gates = __campus.entranceInfo().filter(({ id }) => ids.includes(id));
    return {
      count: state.buildings,
      batches: state.presentation.batchedBuildings,
      gates,
      ground: __campus.terrainCheck(-577, -184),
      rim: __campus.terrainCheck(-567, -186).sampled,
      occupied: [
        [-363.3, -49.9557], // Friendly porch.
        [-361, -49.86], // Friendly wall.
        [-336.8, 55.14], // Collier porch.
        [-338.65, 55.14], // Collier wall.
        [-589, -146.4], // McKenzie south arcade.
        [-578, -183.25], // McKenzie courtyard.
        [-584.75, -184.62], // McKenzie courtyard wall.
      ].map(([x, z]) => __campus.collisionCheck(x, z)),
    };
  }, ids);
}

test("the porches and McKenzie court are open within their ground footprints", async ({
  page,
}) => {
  const before = await read(page, baseline);
  const after = await read(page, "/");
  expect(after.count).toBe(before.count);
  expect(after.batches).toBe(before.batches);
  expect(after.gates).toHaveLength(8);
  expect(after.gates.every(({ gate, walkable }) => gate && walkable)).toBe(
    true,
  );
  expect(after.occupied).toEqual([
    false,
    true,
    false,
    true,
    false,
    false,
    true,
  ]);
  expect(after.ground.sampled).toBe(before.ground.sampled);
  expect(after.rim - after.ground.sampled).toBeGreaterThan(1.05);
  expect(after.ground["friendly-collier-mckenzie-paving"]).toBeCloseTo(
    after.ground.sampled + 0.085,
    3,
  );
});
