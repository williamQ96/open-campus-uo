import { expect, test } from "@playwright/test";

const baseline = "/?exterior-review=oregon-jaqua-baseline";

async function inspect(page, url) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const state = __campus.getState();
    const ids = ["roof-11d15952", "context-b0067"];
    const gateList = __campus
      .entranceInfo()
      .filter(({ id }) => ids.includes(id));
    const points = [
      [21.2, -35.77], // Under the Oregon Hall arcade.
      [16.38, -34.7], // One arcade pier.
      [21.2, -37.95], // The recessed building wall.
      [105.9, -45], // West basin.
      [106, -26.55], // Open west entrance.
      [134, -15], // Open south entrance.
    ];
    return {
      buildings: state.buildings,
      batches: state.presentation.batchedBuildings,
      trees: state.presentation.trees,
      gateList,
      blocked: points.map(([e, z]) => __campus.collisionCheck(e, z)),
    };
  });
}

test("the arcade is open between piers and Jaqua approaches skirt the pool", async ({
  page,
}) => {
  const previous = await inspect(page, baseline);
  const current = await inspect(page, "/");
  expect(previous.blocked).toEqual([true, true, true, false, false, false]);
  expect(current.blocked).toEqual([false, true, true, true, false, false]);
  expect(current.buildings).toBe(previous.buildings);
  expect(current.batches).toBe(previous.batches);
  expect(current.trees).toBe(previous.trees - 2);
  expect(current.gateList).toHaveLength(5);
  expect(current.gateList.every(({ walkable }) => walkable)).toBe(true);
  expect(
    current.gateList.find(({ gate }) => gate === "oregon-south"),
  ).toMatchObject({
    position: [17.82, -36.61],
    snapToFacade: false,
  });
});
