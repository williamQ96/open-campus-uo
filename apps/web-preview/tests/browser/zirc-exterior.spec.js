import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const id = "roof-f0cd697a";
const name = "Zebrafish International Resource Center";
const baseline = "/?exterior-review=zirc-exterior-baseline";
const path = "zirc-exterior-review/site.json";

async function inspect(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate((id) => {
    const { buildings, presentation } = window.__campus.getState();
    const entries = window.__campus.entranceInfo();
    return {
      counts: [
        buildings,
        presentation.batchedBuildings,
        presentation.refinedContextRoofs,
      ],
      name: window.__campus.namedBuildings().find((row) => row.id === id),
      gate: entries.filter((row) => row.id === id),
      otherGates: entries.filter((row) => row.id !== id),
      blocked: [
        [-113, -360],
        [-104, -373],
        [-100, -356],
        [-74, -353],
        [-119.2, -366],
      ].map(([e, z]) => window.__campus.collisionCheck(e, z)),
    };
  }, id);
}

test("ZIRC retains its source ID while registering the completed addition", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const after = await inspect(page);
  expect(before.counts).toEqual(exteriorCounts({ batched: 1 }));
  expect(before.name).toBeUndefined();
  expect(before.blocked).toEqual([false, false, true, false, false]);
  expect(after.counts).toEqual(exteriorCounts());
  expect(after.name).toMatchObject({
    id,
    name,
    name_match: "registered-campus-outline",
  });
  expect(after.blocked).toEqual([true, true, true, false, false]);
  expect(after.gate).toHaveLength(1);
  expect(after.gate[0]).toMatchObject({
    gate: "south-approach",
    walkable: true,
    estimated: true,
  });
  expect(after.otherGates).toEqual(before.otherGates);

  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill("Zebrafish International Resource Center");
  await search.press("Enter");
  await expect
    .poll(() =>
      page.evaluate(() => window.__campus.getState().selectedBuilding),
    )
    .toBe(id);
});

test("a damaged source anchor restores the original ZIRC batch member", async ({
  page,
}) => {
  const baselineState = await inspect(page, baseline);
  const descriptor = await (await page.request.get("/scene/" + path)).json();
  descriptor.batch_removals[0].source_vertices[0][1][0] += 1;
  const body = JSON.stringify(descriptor);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.zirc_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json });
  });
  await page.route("**/scene/" + path, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(baselineState);
});
