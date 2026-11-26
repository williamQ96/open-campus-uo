import { expect, test } from "@playwright/test";

const id = "roof-f736712f";
const name = "Many Nations Longhouse";
const baseline = "/?exterior-review=longhouse-baseline";

async function load(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

function facts(id) {
  const api = window.__campus;
  const state = api.getState();
  const entries = api.entranceInfo();
  return {
    buildings: state.buildings,
    batches: state.presentation.batchedBuildings,
    roads: state.roadSegments,
    name: api.namedBuildings().find((b) => b.id === id)?.name ?? null,
    gates: entries.filter((entry) => entry.id === id),
    neighbors: entries.filter((entry) => entry.id !== id),
    collision: [
      [196, 376],
      [204.9, 377],
      [188.0, 373],
      [207, 370],
    ].map(([e, z]) => api.collisionCheck(e, z)),
  };
}

test("the named Longhouse replaces only the original batch member", async ({
  page,
}) => {
  await load(page, baseline);
  const before = await page.evaluate(facts, id);
  await load(page);
  const after = await page.evaluate(facts, id);
  expect(after.buildings).toBe(before.buildings);
  expect(after.batches).toBe(before.batches - 1);
  expect(after.roads).toBe(before.roads);
  expect(after.name).toBe(name);
  expect(after.neighbors).toEqual(before.neighbors);
  expect(after.collision).toEqual([true, false, false, false]);
  expect(after.gates.map(({ gate, walkable }) => [gate, walkable])).toEqual([
    ["longhouse-east", true],
  ]);
  const input = page.getByRole("combobox", { name: "Search buildings" });
  await input.fill(name);
  await input.press("ArrowDown");
  await input.press("Enter");
  await expect
    .poll(() =>
      page.evaluate(() => window.__campus.getState().selectedBuilding),
    )
    .toBe(id);
  const [entry] = after.gates;
  await page.evaluate(({ id, approach, ground, outward }) => {
    sessionStorage.setItem(
      "explorer:outdoor-return:v1",
      JSON.stringify({
        version: 1,
        buildingId: id,
        player: [approach[0], ground, approach[1]],
        view: "first",
        yaw: Math.atan2(outward[0], outward[1]),
        pitch: 0,
        followDistance: 7.5,
        density: 0,
      }),
    );
  }, entry);
  await load(page, "/?return=1");
  await page.getByRole("button", { name: `Enter ${name}` }).click();
  await page.waitForFunction(() => window.__interior?.getState().ready);
  await page.getByRole("button", { name: /Return to campus/ }).click();
  await expect
    .poll(() => page.evaluate(() => window.__campus?.getState().nearbyEntrance))
    .toBe(id);
});

test("a bad source-triangle anchor restores the prior facade and entrance", async ({
  page,
}) => {
  await load(page, baseline);
  const before = await page.evaluate(facts, id);
  const expected = await page.evaluate(async () => {
    const { loadPresentation } = await import("/src/presentation.js");
    const manifest = await (await fetch("/scene/manifest.json")).json();
    const art = await loadPresentation(
      "/scene/",
      "presentation.json",
      new Set(manifest.buildings.map((b) => b.id)),
    );
    const batch = art.root.getObjectByName("context-campus-2-1");
    return batch.geometry.getAttribute("position").count;
  });
  const actual = await page.evaluate(async (id) => {
    const { loadPresentation } = await import("/src/presentation.js");
    const { loadBuildingSiteReview } =
      await import("/src/building-site-review.js");
    const manifest = await (await fetch("/scene/manifest.json")).json();
    const config = await (await fetch("/scene/presentation.json")).json();
    const response = await fetch("/scene/longhouse-review/site.json");
    const descriptor = await response.json();
    descriptor.batch_removals[0].source_vertices[0][1][0] += 8;
    const bytes = new TextEncoder().encode(JSON.stringify(descriptor));
    const digest = Array.from(
      new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)),
      (byte) => byte.toString(16).padStart(2, "0"),
    ).join("");
    const realFetch = window.fetch;
    let review;
    try {
      window.fetch = (url, ...args) =>
        url === "/scene/longhouse-review/site.json"
          ? Promise.resolve(new Response(bytes))
          : realFetch(url, ...args);
      review = await loadBuildingSiteReview("/scene/", manifest, config, {
        descriptor: { url: "longhouse-review/site.json", sha256: digest },
        directory: "longhouse-review",
        ids: [id],
        groundNode: "longhouse-approach",
        registeredNames: { [id]: "Many Nations Longhouse" },
        sourceBatchIds: [id],
        replacedDetails: ["longhouse-south-provisional-detail.json"],
      });
    } finally {
      window.fetch = realFetch;
    }
    const art = await loadPresentation(
      "/scene/",
      "presentation.json",
      new Set(manifest.buildings.map((b) => b.id)),
      { config, buildingReviews: [review] },
    );
    if (art.buildingReviews.length)
      throw Error("Accepted a wrong source anchor");
    return art.root
      .getObjectByName("context-campus-2-1")
      .geometry.getAttribute("position").count;
  }, id);
  expect(actual).toBe(expected);
  await page.route("**/longhouse-review/site.glb", (route) =>
    route.fulfill({ status: 200, body: "bad pin" }),
  );
  await load(page);
  expect(await page.evaluate(facts, id)).toEqual(before);
});
