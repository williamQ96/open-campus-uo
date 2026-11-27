import { expect, test } from "@playwright/test";
import { DEFAULT_PILOT_TREES } from "./exterior-counts.js";

const baseline = "/?exterior-review=tree-model-baseline";

async function sceneState(page, url = "/") {
  await page.goto(url, { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const { buildings, presentation } = campus.getState();
    return {
      buildings,
      trees: presentation.trees,
      registered: presentation.registeredPilotTrees,
      refined: presentation.refinedPilotTrees,
      gates: campus.entranceInfo(),
    };
  });
}

test("the rebuilt pilot trees use the same count, registered stems and entrances", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const before = await sceneState(page, baseline);
  expect(before.refined).toBe(0);
  expect(before.registered).toBe(11);
  expect(await sceneState(page)).toEqual({
    ...before,
    refined: DEFAULT_PILOT_TREES,
  });
});

test("damaged replacement geometry keeps the preceding pilot batches", async ({
  page,
}) => {
  const before = await sceneState(page, baseline);
  await page.route("**/pilot-trees-l2/trees.glb", (route) =>
    route.fulfill({ body: "damaged pilot geometry" }),
  );
  expect(await sceneState(page)).toEqual(before);
});

test("a failed placement recipe also keeps the legacy pilot layer", async ({
  page,
}) => {
  const before = await sceneState(page, baseline);
  await page.route("**/registered-pilot-trees.json", (route) =>
    route.fulfill({ body: "{}" }),
  );
  expect(await sceneState(page)).toEqual({ ...before, registered: 0 });
});
