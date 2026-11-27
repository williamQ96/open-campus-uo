import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";

const baseline = "/?exterior-review=understory-model-baseline";
const { plants } = JSON.parse(
  readFileSync(
    new URL("../../../../data/metadata/understory-l2.json", import.meta.url),
    "utf8",
  ),
);

async function readScene(page, url = "/") {
  await page.goto(url, { waitUntil: "commit" });
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(() => {
    const campus = window.__campus;
    const { buildings, presentation } = campus.getState();
    return {
      buildings,
      trees: presentation.trees,
      pilotTrees: presentation.refinedPilotTrees,
      contextTrees: presentation.refinedContextTrees,
      understory: presentation.refinedUnderstory,
      approaches: campus.entranceInfo(),
    };
  });
}

test("the rebuilt planting follows the existing masks and leaves the new beds clear of solid collision", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const previous = await readScene(page, baseline);
  expect(previous.understory).toBeNull();
  expect(await readScene(page)).toEqual({
    ...previous,
    understory: { shrubs: 59, fronds: 5, retainedFernClusters: 3 },
  });
  const centers = plants
    .filter((plant) => plant.site)
    .map(({ anchor_gltf_m: [x, , z] }) => [x, z]);
  const blocked = await page.evaluate(
    (centers) => centers.map(([x, z]) => window.__campus.collisionCheck(x, z)),
    centers,
  );
  expect(centers).toHaveLength(13);
  expect(blocked).toEqual(Array(13).fill(false));
});

test("damaged understory bytes keep the older shrub and fern layout", async ({
  page,
}) => {
  const previous = await readScene(page, baseline);
  await page.route("**/understory-l2/plants.glb", (route) =>
    route.fulfill({ body: "damaged planting" }),
  );
  expect(await readScene(page)).toEqual(previous);
});

test("a rejected source removal restores its paired shrubs in the new batch", async ({
  page,
}) => {
  await page.route("**/pilot-green-tree-clearance.json", (route) =>
    route.fulfill({ body: "{}" }),
  );
  expect(await readScene(page)).toMatchObject({
    understory: { shrubs: 62, fronds: 5, retainedFernClusters: 3 },
    pilotTrees: 0,
  });
});
