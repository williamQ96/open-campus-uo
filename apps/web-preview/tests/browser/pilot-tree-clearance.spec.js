import { expect, test } from "@playwright/test";

async function ready(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

test("default planting clears the two sites and keeps all building approaches", async ({
  page,
}) => {
  const read = () => {
    const { presentation } = __campus.getState();
    return {
      visible: presentation.trees,
      source: presentation.sourceTrees,
      fitted: presentation.registeredPilotTrees,
      roofs: presentation.refinedContextRoofs,
      gates: __campus.entranceInfo(),
    };
  };
  await ready(page, "/?exterior-review=tree-baseline");
  const before = await page.evaluate(read);
  await ready(page);
  const after = await page.evaluate(read);
  expect(before.visible).toBe(568);
  expect(before.fitted).toBe(0);
  expect(after.visible).toBe(543);
  expect(after.fitted).toBe(11);
  expect(after.source).toBe(600);
  expect(after.roofs).toBe(7);
  expect(new Set(before.gates.map(({ id }) => id)).size).toBe(519);
  expect(after.gates).toEqual(before.gates);
});

test("invalid tree clearance bytes keep previous planting and confirmed site entrances", async ({
  page,
}) => {
  const entranceKeys = () =>
    __campus
      .entranceInfo()
      .filter(({ gate }) => gate)
      .map(({ id, gate }) => [id, gate])
      .sort();
  await ready(page);
  const gates = await page.evaluate(entranceKeys);
  const warning = page.waitForEvent("console", {
    predicate: (message) => message.text().includes("prior planting"),
  });
  await page.route("**/pilot-green-tree-clearance.json", (route) =>
    route.fulfill({ body: "{}" }),
  );
  await ready(page);
  await warning;
  const result = await page.evaluate(() => ({
    trees: __campus.getState().presentation.trees,
    fitted: __campus.getState().presentation.registeredPilotTrees,
  }));
  expect(result).toEqual({ trees: 568, fitted: 11 });
  expect(await page.evaluate(entranceKeys)).toEqual(gates);
});

test("invalid registration bytes keep clearance and the base tree positions", async ({
  page,
}) => {
  const warning = page.waitForEvent("console", {
    predicate: (message) =>
      message.text().includes("retaining original tree placement"),
  });
  await page.route("**/registered-pilot-trees.json", (route) =>
    route.fulfill({ body: "{}" }),
  );
  await ready(page);
  await warning;
  const { trees, registeredPilotTrees } = await page.evaluate(
    () => __campus.getState().presentation,
  );
  expect(trees).toBe(543);
  expect(registeredPilotTrees).toBe(0);
});
