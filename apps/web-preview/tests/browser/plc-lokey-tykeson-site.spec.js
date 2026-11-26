import { expect, test } from "@playwright/test";

const previous = "/?exterior-review=plc-lokey-tykeson-baseline";
const replaced = [
  "roof-8f611273",
  "roof-74ecc113",
  "roof-5bbb5fd1",
  "context-b0103",
];
const retired = ["roof-30574cc0", "roof-4f014745", "roof-9346417e"];

async function readSite(page, url) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const state = __campus.getState();
    return {
      count: state.buildings,
      batch: state.presentation.batchedBuildings,
      roads: state.roadSegments,
      names: __campus.namedBuildings(),
      gates: __campus.entranceInfo(),
      low: __campus.terrainCheck(-595, 164).sampled,
      high: __campus.terrainCheck(-594, 133.5).sampled,
      solid: [
        [-595, 164], // PLC sunken court.
        [-606, 125], // PLC tower.
        [-626, 375], // Lokey C south porch.
        [-634, 375], // Lokey C wall.
        [-453.55, 20.1], // Tykeson north portico.
        [-442, 23], // Tykeson brick wing.
        [-467.4, 45], // Tykeson canopy approach.
        [-467.7, 51.35], // Canopy column.
      ].map(([x, z]) => __campus.collisionCheck(x, z)),
    };
  });
}

test("the reconstructed exteriors retain identities and open approaches", async ({
  page,
}) => {
  const before = await readSite(page, previous);
  const after = await readSite(page, "/");
  expect(after.count).toBe(before.count - 3);
  expect(after.batch).toBe(before.batch - 4);
  expect(after.roads).toBe(before.roads);
  const gates = after.gates.filter(({ id }) => replaced.includes(id));
  expect(gates).toHaveLength(13);
  expect(gates.every(({ gate, walkable }) => gate && walkable)).toBe(true);
  expect(after.names).toEqual(
    expect.arrayContaining([
      expect.objectContaining({
        id: "roof-5bbb5fd1",
        name: "Lokey Education Building (C)",
      }),
    ]),
  );
  expect(after.gates.some(({ id }) => retired.includes(id))).toBe(false);
  expect(after.high - after.low).toBeGreaterThan(2.5);
  expect(after.solid).toEqual([
    false,
    true,
    false,
    true,
    false,
    true,
    false,
    true,
  ]);
});
