import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
test("EMU paving retains model navigation, unrelated pixels, and draw calls", async ({
  browser,
}) => {
  const prior = readFileSync(
      new URL(
        "../../../../assets/exterior-refinement/paving-joints-before-emu-2026-11-04.json",
        import.meta.url,
      ),
    ),
    states = [];
  for (const before of [true, false]) {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1000 },
      reducedMotion: "reduce",
    });
    if (before)
      await page.route("**/scene/pilot-paving-joints.json", (r) =>
        r.fulfill({ body: prior, contentType: "application/json" }),
      );
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    page.on("console", (m) => {
      if (m.type() === "error") errors.push(m.text());
    });
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entries = await page.evaluate(() => __campus.entranceInfo()),
      ground = await page.evaluate(
        () => __campus.terrainCheck(-300, 31).sampled,
      );
    await page.evaluate(
      (g) =>
        sessionStorage.setItem(
          "explorer:outdoor-return:v1",
          JSON.stringify({
            version: 1,
            buildingId: "roof-266f13fd",
            player: [-300, g, 31],
            view: "first",
            yaw: -Math.PI / 2,
            pitch: 0.27,
            followDistance: 7.5,
            density: 0,
            motionLevel: 0,
          }),
        ),
      ground,
    );
    await page.goto("/?return=1");
    await page.waitForFunction(
      () =>
        window.__campus?.getState().ready &&
        __campus.getState().life.density === "No",
    );
    await page.waitForTimeout(700);
    const state = await page.evaluate(() => ({
      calls: __campus.getState().drawCalls,
      triangles: __campus.getState().triangles,
      blocked: __campus.getState().blocked,
      collision: __campus.collisionCheck(-277, 31),
    }));
    const outside = await page.screenshot({
      clip: { x: 400, y: 650, width: 600, height: 140 },
    });
    await page.screenshot({
      path: `../../docs/images/emu-radial-${before ? "before" : "after"}-2026-11-04.png`,
    });
    if (!before) {
      await page.locator("#settings-open").click();
      await page.getByLabel("Architectural toon", { exact: false }).uncheck();
      await page.locator("#settings-close").click();
      await page.waitForTimeout(500);
      await page.screenshot({
        path: "../../docs/images/emu-radial-pbr-2026-11-04.png",
      });
    }
    expect(errors).toEqual([]);
    states.push({ entries, state, outside });
    await page.close();
  }
  expect(states[1].entries).toEqual(states[0].entries);
  expect(states[1].state).toEqual(states[0].state);
  expect(states[1].outside.equals(states[0].outside)).toBe(true);
  expect(states[1].state.blocked).toBe(false);
});
