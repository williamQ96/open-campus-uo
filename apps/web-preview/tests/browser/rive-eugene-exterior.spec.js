import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const id = "roof-513d7fee";
const name = "The Rive Eugene";
const packageUrl = "rive-eugene-exterior-review/site.json";
const baseline = "/?exterior-review=rive-eugene-exterior-baseline";
const probes = [
  [-890, -454],
  [-851, -457],
  [-840, -448],
  [-889, -425],
  [-894.45, -469.16],
  [-898.2, -469.16],
  [-833.4, -450],
  [-886, -419],
];

async function inspect(page, location = "/") {
  await page.goto(location);
  await page.waitForFunction(() => window.__campus?.getState().ready);
  return page.evaluate(
    ({ id, probes }) => {
      const c = window.__campus;
      const s = c.getState();
      const entrances = c.entranceInfo();
      return {
        counts: [
          s.buildings,
          s.presentation.batchedBuildings,
          s.presentation.refinedContextRoofs,
        ],
        building:
          c.namedBuildings().find((building) => building.id === id) ?? null,
        entrances: entrances.filter((entry) => entry.id === id),
        others: entrances.filter((entry) => entry.id !== id),
        collision: probes.map(([e, z]) => c.collisionCheck(e, z)),
      };
    },
    { id, probes },
  );
}

test("The Rive replaces the old Broadway footprint and its recessed lobby stays clear", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const original = await inspect(page, baseline);
  const current = await inspect(page);
  expect(original.counts).toEqual(exteriorCounts({ batched: 1 }));
  expect(original.building).toBeNull();
  expect(original.collision[0]).toBe(false);
  expect(current.counts).toEqual(exteriorCounts());
  expect(current.building).toMatchObject({ id, name });
  expect(current.others).toEqual(original.others);
  expect(current.collision).toEqual([
    true,
    true,
    true,
    true,
    false,
    false,
    false,
    false,
  ]);
  expect(current.entrances).toHaveLength(1);
  expect(current.entrances[0]).toMatchObject({
    gate: "rive-hilyard-entry",
    walkable: true,
    estimated: true,
  });
  const search = page.getByRole("combobox", { name: "Search buildings" });
  await search.fill(name);
  await search.press("Enter");
  await expect
    .poll(() =>
      page.evaluate(() => window.__campus.getState().selectedBuilding),
    )
    .toBe(id);
});

test("public outdoor routing reaches the Hilyard approach", async ({
  page,
}) => {
  await inspect(page);
  await page.locator("#directions-open").click();
  for (const [endpoint, label] of [
    ["A", "968 Alder Apartments"],
    ["B", name],
  ]) {
    await page
      .getByRole("button", { name: "Search " + endpoint, exact: true })
      .click();
    const input = page.getByRole("combobox");
    await input.fill(label);
    await input.press("ArrowDown");
    await input.press("Enter");
  }
  await page.locator("#route-start").click();
  const route = await page.evaluate(
    () => window.__campus.getState().navigation.points,
  );
  expect(route.length).toBeGreaterThan(2);
  expect(route.at(-1)[0]).toBeCloseTo(-896.5, 2);
  expect(route.at(-1)[1]).toBeCloseTo(469.16, 2);
});

test("a damaged source anchor retains the earlier building and other Broadway reviews", async ({
  page,
}) => {
  const before = await inspect(page, baseline);
  const descriptor = await (
    await page.request.get("/scene/" + packageUrl)
  ).json();
  descriptor.batch_removals[0].source_vertices[0][1][0] += 0.64;
  const body = JSON.stringify(descriptor);
  const sha256 = createHash("sha256").update(body).digest("hex");
  await page.route("**/scene/presentation.json", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.rive_eugene_exterior_site.sha256 = sha256;
    await route.fulfill({ response, json });
  });
  await page.route("**/scene/" + packageUrl, (route) =>
    route.fulfill({ body, contentType: "application/json" }),
  );
  expect(await inspect(page)).toEqual(before);
});
