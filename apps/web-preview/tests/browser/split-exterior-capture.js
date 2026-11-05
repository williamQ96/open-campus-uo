import { test, expect } from "@playwright/test";

// Serial execution makes the final paired comparison depend on every capture.
// Playwright reports a failed capture and skips the comparison rather than passing it.
export function splitExteriorCapture(config) {
  test.describe(config.title, () => {
    test.describe.configure({ mode: "serial" });
    const results = { before: [], after: [] };
    for (const phase of ["before", "after"]) {
      for (const [label, x, z, yaw] of config.views) {
        test(`${phase}: ${label} return view`, async ({ browser }) => {
          test.setTimeout(config.timeout);
          const context = await browser.newContext({
            viewport: { width: 1440, height: 1000 },
            ...(config.reducedMotion ? { reducedMotion: "reduce" } : {}),
          });
          try {
            const page = await context.newPage();
            const errors = [];
            page.on("pageerror", (error) => errors.push(error.message));
            if (config.checkConsole) {
              page.on("console", (message) => {
                if (message.type() === "error") errors.push(message.text());
              });
            }
            if (phase === "before") {
              await page.route(`**/scene/${config.detail}`, (route) =>
                route.fulfill({
                  body: config.old,
                  contentType: "application/json",
                }),
              );
              await page.route("**/scene/presentation.json", async (route) => {
                const response = await route.fetch();
                const json = await response.json();
                json.exterior_details.find(
                  (item) => item.url === config.detail,
                ).sha256 = config.hash;
                await route.fulfill({ response, json });
              });
            }
            await page.goto("/");
            await page.waitForFunction(() => window.__campus?.getState().ready);
            const entries = await page.evaluate(() => __campus.entranceInfo());
            const ground = await page.evaluate(
              ({ x, z }) => __campus.terrainCheck(x, z).sampled,
              { x, z },
            );
            let blocked;
            if (config.checkCamera) {
              blocked = await page.evaluate(
                ({ x, z }) => __campus.collisionCheck(x, z),
                { x, z },
              );
            }
            await page.evaluate(
              ({ x, z, yaw, ground, buildingId, pitch }) =>
                sessionStorage.setItem(
                  "explorer:outdoor-return:v1",
                  JSON.stringify({
                    version: 1,
                    buildingId,
                    player: [x, ground, z],
                    view: "first",
                    yaw,
                    pitch,
                    followDistance: 7.5,
                    density: 0,
                    motionLevel: 0,
                  }),
                ),
              {
                x,
                z,
                yaw,
                ground,
                buildingId: config.buildingId,
                pitch: config.pitch,
              },
            );
            await page.goto("/?return=1");
            await page.waitForFunction(
              () =>
                window.__campus?.getState().ready &&
                __campus.getState().life.density === "No",
            );
            await page.waitForTimeout(500);
            let state;
            if (config.checkCamera) {
              state = await page.evaluate(() => ({
                camera: __campus.getState().camera,
                draws: __campus.getState().drawCalls,
              }));
              expect(state.camera[0]).toBeCloseTo(x, 1);
              expect(state.camera[2]).toBeCloseTo(z, 1);
            }
            await page.screenshot({
              path: `test-results/scene-captures/${config.imagePrefix}-${label}-${phase}-2026-11-04.png`,
            });
            if (!config.checkCamera) {
              const sampled = await page.evaluate(
                ({ x, z }) => ({
                  draws: __campus.getState().drawCalls,
                  blocked: __campus.collisionCheck(x, z),
                }),
                { x, z },
              );
              state = sampled;
              blocked = sampled.blocked;
            }
            await page
              .getByRole("combobox", { name: "Search buildings" })
              .fill(config.name);
            await page
              .getByRole("option", { name: config.namePattern })
              .first()
              .click();
            await expect
              .poll(() =>
                page.evaluate(() => __campus.getState().selectedBuilding),
              )
              .toBe(config.buildingId);
            expect(errors).toEqual([]);
            results[phase].push({
              label,
              entries,
              blocked,
              draws: state.draws,
              ...(config.checkCamera ? { camera: state.camera } : {}),
            });
          } finally {
            await context.close();
          }
        });
      }
    }
    test("compare all before and after views", async () => {
      expect(results.before).toHaveLength(config.views.length);
      expect(results.after).toHaveLength(config.views.length);
      expect(results.after).toEqual(results.before);
    });
  });
}
