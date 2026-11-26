import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { exteriorCounts } from "./exterior-counts.js";

const replacement = "pilot-furnishings-l2.glb";
const legacyDetails = [
  "pilot-bench-back-suppression.json",
  "pilot-bench-seat-suppression.json",
  "pilot-bench-detail.json",
  "pilot-lamp-detail.json",
];

async function inspect(page) {
  const requests = new Set();
  page.on("request", (request) =>
    requests.add(new URL(request.url()).pathname),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const state = await page.evaluate(async () => {
    const campus = window.__campus;
    const { buildings, presentation } = campus.getState();
    const { pilot_furnishings: spec } = await (
      await fetch("/scene/presentation.json")
    ).json();
    const gates = campus
      .entranceInfo()
      .filter(
        ({ id, walkable }) =>
          (id === "context-b0103" || id === "roof-8f611273") && walkable,
      );
    return {
      counts: [
        buildings,
        presentation.batchedBuildings,
        presentation.refinedContextRoofs,
      ],
      furnishings: presentation.pilotFurnishings,
      blocked: spec.collision_boxes_enu_m.map(([e0, n0, e1, n1]) =>
        campus.collisionCheck((e0 + e1) / 2, -(n0 + n1) / 2),
      ),
      open: [
        [-427, 85],
        [-357, 85],
        [-470, 68],
        [-581, 134],
        [-275, 27],
      ].map(([e, z]) => !campus.collisionCheck(e, z)),
      approachIds: [...new Set(gates.map(({ id }) => id))].sort(),
    };
  });
  return { ...state, requests };
}

for (const width of [1440, 390]) {
  test(`pilot benches, acorn lights and rack are walkable around at ${width}px`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 844 });
    const mounted = page.waitForResponse((r) => r.url().endsWith(replacement));
    const actual = await inspect(page);
    expect(actual.counts).toEqual(exteriorCounts());
    expect(actual.furnishings).toBe(21);
    expect(actual.blocked).toEqual(Array(21).fill(true));
    expect(actual.open).toEqual(Array(5).fill(true));
    expect(actual.approachIds).toEqual(["context-b0103", "roof-8f611273"]);
    expect((await mounted).ok()).toBe(true);
    expect(
      legacyDetails.filter((file) => actual.requests.has("/scene/" + file)),
    ).toEqual([]);
  });
}

test("bad furnishing bytes restore all baseline patches and clear the replacement collision boxes", async ({
  page,
}) => {
  await page.route("**/scene/" + replacement, (route) =>
    route.fulfill({
      body: createHash("sha256").update("other scene").digest(),
      contentType: "model/gltf-binary",
    }),
  );
  const actual = await inspect(page);
  expect(actual.counts).toEqual(exteriorCounts());
  expect(actual.furnishings).toBe(0);
  expect(actual.blocked).toEqual(Array(21).fill(false));
  expect(actual.open).toEqual(Array(5).fill(true));
  expect(
    legacyDetails.every((file) => actual.requests.has("/scene/" + file)),
  ).toBe(true);
});
