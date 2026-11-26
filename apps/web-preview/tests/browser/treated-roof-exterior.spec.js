import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const directory = "treated-roof-exterior-review";
const baseline = "/?exterior-review=treated-roof-exterior-baseline";
const names = {
  "roof-76af1329": "1951 Onyx Alley",
  "roof-f447a8a6": "1772 Hilyard St",
  "roof-57dfe898": "Spencer Apartments",
  "roof-efbfe809": "Eugene Institute of Religion",
  "roof-aae8fc07": "1010–1020 E 18th Ave",
  "roof-f1651047": "1010 E 20th Ave",
};

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((ids) => {
    const { buildings, presentation } = __campus.getState();
    const entries = __campus.entranceInfo();
    return {
      counts: [
        buildings,
        presentation.batchedBuildings,
        presentation.refinedContextRoofs,
      ],
      names: Object.fromEntries(
        __campus
          .namedBuildings()
          .filter(({ id }) => ids.includes(id))
          .map(({ id, name }) => [id, name]),
      ),
      entries: entries.filter(({ id }) => ids.includes(id)),
      otherEntries: entries.filter(({ id }) => !ids.includes(id)),
      parking: [
        [-964.529, 569.0988],
        [-541.7239, 624.6201],
        [-518.9276, 868.402],
      ].map(([x, z]) => __campus.collisionCheck(x, z)),
      posts: [
        [-966.05487, 575.73747],
        [-543.04566, 626.63893],
        [-520.68191, 867.19363],
      ].map(([x, z]) => __campus.collisionCheck(x, z)),
    };
  }, Object.keys(names));
}

test("six L2 exteriors replace roof treatments and preserve seven walkable approaches", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 6, roofs: 6 }));
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.names).toEqual(names);
  expect(after.otherEntries).toEqual(before.otherEntries);
  expect(after.entries).toHaveLength(7);
  expect(after.entries.every(({ gate, walkable }) => gate && walkable)).toBe(
    true,
  );
  expect(
    after.entries
      .filter(({ id }) => id === "roof-aae8fc07")
      .map(({ gate }) => gate),
  ).toEqual(["west-entry", "east-entry"]);
  expect(after.parking).toEqual([false, false, false]);
  expect(after.posts).toEqual([true, true, true]);
  const search = page.getByRole("combobox", { name: "Search buildings" });
  for (const address of ["1010 E 18th Ave", "1020 E 18th Ave"]) {
    await search.fill(address);
    await expect(page.getByRole("option").first()).toContainText(
      names["roof-aae8fc07"],
    );
    await search.press("Enter");
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("roof-aae8fc07");
  }
});

test("a shifted source range restores all six source walls and roof treatments", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const path = directory + "/site.json";
  const item = await (await page.request.get("/scene/" + path)).json();
  item.batch_removals.at(-1).source_vertices.at(-1)[1][0] += 0.58;
  const body = JSON.stringify(item);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const config = await response.json();
    config.treated_roof_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json: config });
  });
  await page.route("**/" + path, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
