import { expect, test } from "@playwright/test";

const baseline = "/?exterior-review=knight-campus-baseline";
const ids = ["context-oc-knight-1", "context-oc-knight-2"];
const obsolete = "roof-a79ff330";
const points = [
  [-25.85, -143.8], // Franklin roadway below the suspended span.
  [-25.72, -125.82], // South arch footing.
  [-35, -190], // Building 1 west wing.
  [31.3, -228], // Millrace bridge approach at ground level.
  [29.3, -218.75], // Millrace bridge pedestal.
  [38, -274], // Below the Building 2 west terraces.
  [52, -246], // Building 2 ground volume.
  [73.5, -280], // Riverfront walk.
];

async function inspect(page, path) {
  await page.goto(path);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(
    ({ points, ids, obsolete }) => {
      const state = __campus.getState();
      const gates = __campus.entranceInfo();
      return {
        count: state.buildings,
        batch: state.presentation.batchedBuildings,
        roads: state.roadSegments,
        occupied: points.map(([e, z]) => __campus.collisionCheck(e, z)),
        entries: gates.filter(({ id }) => ids.includes(id)),
        neighbors: gates.filter(
          ({ id }) => !ids.includes(id) && id !== obsolete,
        ),
        obsolete: gates.some(({ id }) => id === obsolete),
      };
    },
    { points, ids, obsolete },
  );
}

test("Knight Campus preserves the road and walk beneath its elevated spans", async ({
  page,
}) => {
  const previous = await inspect(page, baseline);
  const current = await inspect(page, "/");
  expect([current.count, current.batch, current.roads]).toEqual([
    previous.count - 1,
    previous.batch - 1,
    previous.roads,
  ]);
  expect(previous.obsolete).toBe(true);
  expect(current.obsolete).toBe(false);
  expect(current.neighbors).toEqual(previous.neighbors);
  expect(current.entries).toHaveLength(6);
  expect(current.entries.every(({ gate, walkable }) => gate && walkable)).toBe(
    true,
  );
  expect(current.occupied).toEqual([
    false,
    true,
    true,
    false,
    true,
    false,
    true,
    false,
  ]);
});

test("Knight Campus restores both original selections and the old batch on failure", async ({
  page,
}) => {
  const previous = await inspect(page, baseline);
  await page.route("**/knight-campus-review/site.glb", (route) =>
    route.fulfill({ body: "broken site" }),
  );
  const fallback = await inspect(page, "/");
  expect(fallback).toEqual(previous);
});
