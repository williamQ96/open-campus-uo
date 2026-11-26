import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

async function ready(page, url = "/") {
  await page.goto(url);
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

test("default context roofs keep the selected building footprints and both frontage packages", async ({
  page,
}) => {
  await ready(page);
  const read = () => {
    const api = __campus;
    return {
      roofCount: api.getState().presentation.refinedContextRoofs,
      ids: api.getState().presentation.batchedBuildings,
      gates: api
        .entranceInfo()
        .filter(({ gate }) => gate)
        .map(({ gate }) => gate),
      collides: [
        [-114, -402],
        [-990, 72],
        [-953, -685],
        [-950, 571],
        [-988, 95],
        [-734, 753],
        [-218, 628],
        [-856, -380],
        [-820, 434],
        [-844, 772],
        [-146, -418],
        [-234.5, 803.5],
        [-532, 871.5],
        [194.779, 619.934],
        [-781.5, 100.5],
        [-43.5, 644.5],
        [-87, 672.5],
        [-781, 166],
        [363, -195],
        [-806.5, -399.5],
        [-525.286, 627],
        [-850.5, -512],
        [-6, 646],
        [-974, 319.5],
        [-25, 643.5],
        [-482.5, 635.5],
        [47.5, 657],
        [-658.5, 208],
        [-812, 400],
      ].map(([x, z]) => api.collisionCheck(x, z)),
    };
  };
  const after = await page.evaluate(read);
  expect(after.roofCount).toBe(exteriorCounts()[2]);
  expect(after.collides).toEqual(Array(29).fill(true));
  expect(after.gates).toEqual(
    expect.arrayContaining(["allen-west", "fenton-south"]),
  );
  await ready(page, "/?exterior-review=roof-baseline");
  const before = await page.evaluate(read);
  expect(before.roofCount).toBe(0);
  expect(before.collides).toEqual(after.collides);
  expect(before.gates.sort()).toEqual(after.gates.sort());
  expect(before.ids).toBe(after.ids);
});

test("courtyard geometry and names are installed with the compound roof package", async ({
  page,
}) => {
  const read = () => {
    const api = __campus;
    const siteIds = ["roof-53501ed1", "roof-8826f960"];
    return {
      names: api.namedBuildings().filter(({ id }) => siteIds.includes(id)),
      blocked: [
        [-837, 154],
        [-846.6, 153],
        [-850.3, 152],
        [-825, 155],
        [-95, -320],
      ].map(([x, z]) => api.collisionCheck(x, z)),
      approaches: api.entranceInfo().filter(({ id }) => siteIds.includes(id)),
    };
  };
  await ready(page);
  const revised = await page.evaluate(read);
  expect(revised.names).toEqual([
    { id: "roof-53501ed1", name: "Canterbury Court" },
    { id: "roof-8826f960", name: "Millrace 3" },
  ]);
  expect(revised.blocked).toEqual([false, true, true, true, true]);
  expect(revised.approaches).toHaveLength(2);
  expect(
    revised.approaches.every(
      ({ walkable, estimated }) => walkable && estimated,
    ),
  ).toBe(true);

  await ready(page, "/?exterior-review=roof-baseline");
  const original = await page.evaluate(read);
  expect(original.names).toEqual([]);
  expect(original.blocked).toEqual([true, true, true, true, true]);
});

test("invalid context roof bytes keep the campus and other overrides available", async ({
  page,
}) => {
  const warning = page.waitForEvent("console", {
    predicate: (message) => message.text().includes("prior roofs"),
  });
  await page.route("**/context-roof-refinements.json", (route) =>
    route.fulfill({ body: "{}" }),
  );
  await ready(page);
  await warning;
  expect(
    await page.evaluate(
      () => __campus.getState().presentation.refinedContextRoofs,
    ),
  ).toBe(0);
  expect(
    await page.evaluate(() =>
      __campus.entranceInfo().some(({ gate }) => gate === "plaza"),
    ),
  ).toBe(true);
});
