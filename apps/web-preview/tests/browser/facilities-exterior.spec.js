import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";

const buildings = {
  "roof-2975e487": "CPFM Warehouse and Shops",
  "roof-3b3ed882": "Facilities Services Miscellaneous Quonset",
  "roof-4c8ea72b": "Facilities Services Recycling Quonset",
  "roof-b5543048": "CPFM Administration",
  "roof-0151b728": "Romania Warehouse and Showroom",
};

async function inspect(page, url) {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const state = __campus.getState();
    const entries = __campus.entranceInfo();
    return {
      counts: [
        state.buildings,
        state.presentation.batchedBuildings,
        state.roadSegments,
      ],
      roofs: state.presentation.refinedContextRoofs,
      names: Object.fromEntries(
        __campus
          .namedBuildings()
          .filter(({ id }) => ids.includes(id))
          .map(({ id, name }) => [id, name]),
      ),
      approaches: entries.filter(({ id }) => ids.includes(id)),
      otherApproaches: entries.filter(({ id }) => !ids.includes(id)),
    };
  }, Object.keys(buildings));
}

test("facilities replace their source batches and one overlapping context roof", async ({
  page,
}) => {
  const previous = await inspect(
    page,
    "/?exterior-review=facilities-exterior-baseline",
  );
  const next = await inspect(page, "/");
  expect(next.names).toEqual(buildings);
  expect(next.roofs).toBe(previous.roofs - 1);
  expect(next.counts).toEqual([
    previous.counts[0],
    previous.counts[1] - 5,
    previous.counts[2],
  ]);
  expect(next.otherApproaches).toEqual(previous.otherApproaches);
  expect(next.approaches).toHaveLength(6);
  expect(next.approaches.every(({ gate, walkable }) => gate && walkable)).toBe(
    true,
  );
});

test("a late facilities anchor mismatch restores the previous Quonset roof and names", async ({
  page,
}) => {
  const previous = await inspect(
    page,
    "/?exterior-review=facilities-exterior-baseline",
  );
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    const siteUrl = new URL(config.facilities_exterior_site.url, response.url())
      .href;
    const site = await (await page.request.get(siteUrl)).json();
    site.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.57;
    const body = JSON.stringify(site);
    config.facilities_exterior_site.sha256 = createHash("sha256")
      .update(body)
      .digest("hex");
    await page.route(siteUrl, (request) =>
      request.fulfill({
        body,
        contentType: "application/json",
      }),
    );
    await route.fulfill({ response, json: config });
  });
  expect(await inspect(page, "/")).toEqual(previous);
});
