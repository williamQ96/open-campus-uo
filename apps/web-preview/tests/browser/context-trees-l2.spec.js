import { expect, test } from "@playwright/test";
import {
  DEFAULT_BACKGROUND_TREES,
  DEFAULT_PILOT_TREES,
  DEFAULT_VISIBLE_SOURCE_TREES,
  HAYWARD_PRACTICE_CONTEXT_TREE_REMOVALS,
  HAYWARD_SQUARE_CONTEXT_TREE_REMOVALS,
} from "./exterior-counts.js";

const baseline = "/?exterior-review=context-tree-model-baseline";

async function readScene(page, url = "/") {
  await page.goto(url, { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const { buildings, presentation } = campus.getState();
    return {
      buildings,
      sourceTrees: presentation.sourceTrees,
      trees: presentation.trees,
      contextTrees: presentation.refinedContextTrees,
      pilotTrees: presentation.refinedPilotTrees,
      approaches: campus.entranceInfo(),
    };
  });
}

test("the rebuilt background layer retains the active site tree decisions", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const prior = await readScene(page, baseline);
  expect(prior).toMatchObject({
    sourceTrees: 600,
    trees: DEFAULT_VISIBLE_SOURCE_TREES,
    contextTrees: 0,
    pilotTrees: DEFAULT_PILOT_TREES,
  });
  expect(await readScene(page)).toEqual({
    ...prior,
    contextTrees: DEFAULT_BACKGROUND_TREES,
  });
});

test("the Alder baseline also restores its original background tree", async ({
  page,
}) => {
  const restored = await readScene(
    page,
    "/?exterior-review=alder-thirteenth-exterior-baseline",
  );
  expect(restored).toMatchObject({
    trees: DEFAULT_VISIBLE_SOURCE_TREES + 1,
    contextTrees: DEFAULT_BACKGROUND_TREES + 1,
  });
  expect(await readScene(page)).toMatchObject({
    trees: DEFAULT_VISIBLE_SOURCE_TREES,
    contextTrees: DEFAULT_BACKGROUND_TREES,
  });
});

test("invalid replacement bytes retain the existing site tree decisions", async ({
  page,
}) => {
  const prior = await readScene(page, baseline);
  await page.route("**/context-trees-l2/trees.glb", (route) =>
    route.fulfill({ body: "damaged background mesh" }),
  );
  expect(await readScene(page)).toEqual(prior);
});

test("a damaged Hayward practice bundle restores the prior context trees", async ({
  page,
}) => {
  await page.route("**/hayward-practice-fields-review/site.glb", (route) =>
    route.fulfill({ body: "damaged practice field mesh" }),
  );
  expect(await readScene(page)).toMatchObject({
    trees:
      DEFAULT_VISIBLE_SOURCE_TREES + HAYWARD_PRACTICE_CONTEXT_TREE_REMOVALS,
    contextTrees:
      DEFAULT_BACKGROUND_TREES + HAYWARD_PRACTICE_CONTEXT_TREE_REMOVALS,
    pilotTrees: DEFAULT_PILOT_TREES,
  });
});

test("a damaged square track bundle restores its context trees", async ({
  page,
}) => {
  await page.route("**/hayward-square-track-review/site.glb", (route) =>
    route.fulfill({ body: "damaged square track mesh" }),
  );
  expect(await readScene(page)).toMatchObject({
    trees: DEFAULT_VISIBLE_SOURCE_TREES + HAYWARD_SQUARE_CONTEXT_TREE_REMOVALS,
    contextTrees:
      DEFAULT_BACKGROUND_TREES + HAYWARD_SQUARE_CONTEXT_TREE_REMOVALS,
    pilotTrees: DEFAULT_PILOT_TREES,
  });
});
