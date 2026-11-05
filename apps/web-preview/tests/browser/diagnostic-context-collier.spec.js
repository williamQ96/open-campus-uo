import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const old = readFileSync(
  new URL(
    "../../../../assets/exterior-refinement/collier-before-bays-2026-11-04.json",
    import.meta.url,
  ),
);
test("Collier exterior retains campus selection, entrances, collision and draw counts", async ({
  browser,
}) => {
  const results = [];
  const sharedContext =
    process.env.DIAG_CONTEXT === "reuse"
      ? await browser.newContext({
          viewport: { width: 1440, height: 1000 },
          reducedMotion: "reduce",
        })
      : null;
  for (const before of [true, false]) {
    const page = sharedContext
        ? await sharedContext.newPage()
        : await browser.newPage({
            viewport: { width: 1440, height: 1000 },
            reducedMotion: "reduce",
          }),
      errors = [];
    await page.addInitScript(() => {
      window.__diagnosticInitialStorage = {
        local: { ...localStorage },
        session: { ...sessionStorage },
      };
    });
    page.on("pageerror", (e) => errors.push(e.message));
    page.on("console", (m) => {
      if (m.type() === "error") errors.push(m.text());
    });
    if (before) {
      await page.route("**/scene/collier-house-detail.json", (r) =>
        r.fulfill({ body: old, contentType: "application/json" }),
      );
      await page.route("**/scene/presentation.json", async (r) => {
        const res = await r.fetch(),
          j = await res.json();
        j.exterior_details.find(
          (x) => x.url === "collier-house-detail.json",
        ).sha256 =
          "5ddf7032c90127d7b14dd58a89f6b622e586da7aa15c0d746941cb0cbfd27820";
        await r.fulfill({ response: res, json: j });
      });
    }
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    expect(
      await page.evaluate(() => window.__diagnosticInitialStorage),
    ).toEqual({ local: {}, session: {} });
    const entries = await page.evaluate(() => __campus.entranceInfo());
    const views = [];
    for (const [label, x, z, yaw] of [
      ["east", -305, 58.5, Math.PI / 2],
      ["north", -345, 22, Math.PI],
    ]) {
      const ground = await page.evaluate(
        ({ x, z }) => __campus.terrainCheck(x, z).sampled,
        { x, z },
      );
      await page.evaluate(
        ({ x, z, yaw, ground }) =>
          sessionStorage.setItem(
            "explorer:outdoor-return:v1",
            JSON.stringify({
              version: 1,
              buildingId: "roof-e5accf83",
              player: [x, ground, z],
              view: "first",
              yaw,
              pitch: -0.28,
              followDistance: 7.5,
              density: 0,
              motionLevel: 0,
            }),
          ),
        { x, z, yaw, ground },
      );
      await page.goto("/?return=1");
      await page.waitForFunction(
        () =>
          window.__campus?.getState().ready &&
          __campus.getState().life.density === "No",
      );
      await page.waitForTimeout(500);
      await page.screenshot({
        path: `test-results/context-captures/collier-bays-${label}-${before ? "before" : "after"}-2026-11-04.png`,
      });
      views.push(
        await page.evaluate(
          ({ x, z }) => ({
            draws: __campus.getState().drawCalls,
            blocked: __campus.collisionCheck(x, z),
          }),
          { x, z },
        ),
      );
    }
    await page
      .getByRole("combobox", { name: "Search buildings" })
      .fill("Collier House");
    await page
      .getByRole("option", { name: /Collier House/ })
      .first()
      .click();
    await expect
      .poll(() => page.evaluate(() => __campus.getState().selectedBuilding))
      .toBe("roof-e5accf83");
    results.push({ entries, views, errors });
    if (sharedContext) {
      // A new browser context has empty origin storage, cookies, and cache.
      // Clear all of them before the next page while retaining the context.
      const cdp = await sharedContext.newCDPSession(page);
      await cdp.send("Storage.clearDataForOrigin", {
        origin: new URL(page.url()).origin,
        storageTypes: "all",
      });
      await cdp.send("Network.clearBrowserCache");
      await cdp.detach();
      await sharedContext.clearCookies();
    }
    await page.close();
  }
  if (sharedContext) await sharedContext.close();
  expect(results[1].entries).toEqual(results[0].entries);
  expect(results[1].views.map((v) => v.blocked)).toEqual(
    results[0].views.map((v) => v.blocked),
  );
  expect(results[1].views.map((v) => v.draws)).toEqual(
    results[0].views.map((v) => v.draws),
  );
  expect(results.flatMap((x) => x.errors)).toEqual([]);
});
