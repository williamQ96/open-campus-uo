// SPDX-License-Identifier: Apache-2.0
// Compare the pinned pre-refinement module with the local portal at one camera.
import { chromium } from "@playwright/test";
import { createHash } from "node:crypto";
import fs from "node:fs";
const sha = (b) => createHash("sha256").update(b).digest("hex");
const [tag] = process.argv.slice(2);
if (process.argv.length !== 3 || !/^[a-z0-9-]+$/.test(tag || ""))
  throw Error(
    "Usage: node scripts/compare-entrance-performance.mjs <new-run-tag>",
  );
const report = `../../data/metadata/entrance-performance-${tag}.json`;
for (const p of [
  report,
  ...["baseline", "current"].map(
    (v) => `../../docs/images/entrance-performance-${tag}-${v}.png`,
  ),
])
  if (fs.existsSync(p)) throw Error(`Output already exists: ${p}`);
const baseline = fs.readFileSync(
    "../../assets/exterior-refinement/entrances-original-2026-11-04.js",
  ),
  current = fs.readFileSync("src/entrances.js"),
  lock = JSON.parse(fs.readFileSync("viewer-template.lock.json"));
if (sha(baseline) !== lock.files["src/entrances.js"])
  throw Error(
    "Archived baseline does not match the recorded pre-refinement source",
  );
const browser = await chromium.launch({
  channel: "chrome",
  headless: true,
  args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
try {
  const runs = [];
  for (const variant of ["baseline", "current"]) {
    const context = await browser.newContext({
        viewport: { width: 1440, height: 1000 },
        reducedMotion: "reduce",
      }),
      page = await context.newPage(),
      errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    if (variant === "baseline")
      await page.route("**/src/entrances.js*", async (route) => {
        const resp = await route.fetch(),
          transformed = await resp.text();
        let text = baseline.toString("utf8");
        const actualImports = transformed.match(/^import .*;$/gm).slice(0, 3),
          sourceImports = text.match(/^import .*;$/gm).slice(0, 3);
        if (actualImports.length !== 3 || sourceImports.length !== 3)
          throw Error("Cannot safely map Vite imports");
        for (let i = 0; i < 3; i++)
          text = text.replace(sourceImports[i], actualImports[i]);
        await route.fulfill({
          response: resp,
          body: text,
          headers: { ...resp.headers(), "content-type": "text/javascript" },
        });
      });
    await page.goto("http://127.0.0.1:5173/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    const entry = await page.evaluate(() =>
      __campus.entranceInfo().find((e) => e.id === "roof-0151b728"),
    );
    if (!entry || !entry.walkable) throw Error("Comparison entrance missing");
    await page.evaluate(
      (e) =>
        sessionStorage.setItem(
          "explorer:outdoor-return:v1",
          JSON.stringify({
            version: 1,
            buildingId: e.id,
            buildingName: e.name,
            player: [
              e.position[0] + e.outward[0] * 4,
              e.ground,
              e.position[1] + e.outward[1] * 4,
            ],
            view: "first",
            yaw: Math.atan2(e.outward[0], e.outward[1]),
            pitch: 0,
            followDistance: 7.5,
            density: 0,
            motionLevel: 1,
          }),
        ),
      entry,
    );
    await page.goto("http://127.0.0.1:5173/?return=1");
    await page.waitForFunction(
      () =>
        window.__campus?.getState().ready &&
        __campus.getState().life.density === "No",
    );
    await page.waitForTimeout(2500);
    const sample = await page.evaluate(async () => {
      const times = [],
        start = performance.now();
      await new Promise((resolve) => {
        function frame(t) {
          times.push(t);
          if (t - start >= 8000) resolve();
          else requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
      });
      let s = __campus.getState();
      return {
        drawCalls: s.drawCalls,
        triangles: s.triangles,
        camera: s.camera,
        cameraDirection: s.cameraDirection,
        player: s.player,
        view: s.view,
        density: s.life.density,
        entranceCount: s.entranceCount,
        frames: times.length,
        elapsedMs: times.at(-1) - times[0],
      };
    });
    await page.screenshot({
      path: `../../docs/images/entrance-performance-${tag}-${variant}.png`,
    });
    if (errors.length) throw Error(errors.join("; "));
    runs.push({
      variant,
      entry: { id: entry.id, position: entry.position, outward: entry.outward },
      ...sample,
    });
    await context.close();
  }
  const [a, b] = runs;
  if (
    JSON.stringify(a.camera) !== JSON.stringify(b.camera) ||
    JSON.stringify(a.cameraDirection) !== JSON.stringify(b.cameraDirection) ||
    JSON.stringify(a.player) !== JSON.stringify(b.player)
  )
    throw Error("Viewpoints differ");
  const out = {
    baseline_sha256: sha(baseline),
    current_sha256: sha(current),
    renderer: "Chrome headless SwiftShader",
    viewport: [1440, 1000],
    runs,
    delta: {
      drawCalls: b.drawCalls - a.drawCalls,
      triangles: b.triangles - a.triangles,
    },
    notes:
      "RAF samples are local software-rendered observations, not a device benchmark; placement remains estimated.",
  };
  fs.writeFileSync(report, JSON.stringify(out, null, 2) + "\n", { flag: "wx" });
  console.log(JSON.stringify(out));
} finally {
  await browser.close();
}
