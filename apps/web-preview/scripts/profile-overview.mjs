// Local-only measurement harness. Debug references are injected by Playwright,
// never shipped in the viewer or exposed to visitors.
import { chromium } from "@playwright/test";
import { mkdir, writeFile, readFile } from "node:fs/promises";
import { createHash } from "node:crypto";

const name = process.argv[2] || "overview-probe";
if (!/^[\w-]+$/.test(name)) throw Error("Use a simple output name");
const browser = await chromium.launch({ channel: "chrome", headless: true });
const page = await browser.newPage({
  viewport: { width: 1440, height: 1000 },
  deviceScaleFactor: Number(process.env.PROBE_DPR || 1),
});
await page.route("**/src/main.js*", async (route) => {
  const response = await route.fetch();
  const body = (await response.text()).replace(
    "window.__campus = {",
    "window.__renderProbe = {scene,camera,renderer,model,presentation,life,labels,sky,orbit,drawMap,player}; window.__campus = {",
  );
  await route.fulfill({ response, body });
});
await page.goto("http://127.0.0.1:5173/");
await page.waitForFunction(() => window.__campus?.getState().ready);
await page.waitForTimeout(1500);
const metadata = await page.evaluate(() => {
  const d = __renderProbe,
    gl = d.renderer.getContext();
  const ext = gl.getExtension("WEBGL_debug_renderer_info");
  const metrics = { render: [], labels: [], life: [], intervals: [], gpu: [] };
  window.__measurements = metrics;
  const timer = gl.getExtension("EXT_disjoint_timer_query_webgl2"),
    pending = [];
  let frame = 0;
  for (const [target, method, key] of [
    [d.renderer, "render", "render"],
    [d.labels, "update", "labels"],
    [d.life, "update", "life"],
  ]) {
    if (!target) continue;
    const original = target[method].bind(target);
    target[method] = (...args) => {
      let query;
      if (key === "render" && timer) {
        while (
          pending.length &&
          gl.getQueryParameter(pending[0], gl.QUERY_RESULT_AVAILABLE)
        ) {
          const q = pending.shift();
          if (!gl.getParameter(timer.GPU_DISJOINT_EXT))
            metrics.gpu.push(gl.getQueryParameter(q, gl.QUERY_RESULT) / 1e6);
          gl.deleteQuery(q);
        }
        if (frame++ % 4 === 0 && pending.length < 8) {
          query = gl.createQuery();
          gl.beginQuery(timer.TIME_ELAPSED_EXT, query);
        }
      }
      const start = performance.now();
      const result = original(...args);
      metrics[key].push(performance.now() - start);
      if (query) {
        gl.endQuery(timer.TIME_ELAPSED_EXT);
        pending.push(query);
      }
      return result;
    };
  }
  let last;
  function tick(now) {
    if (last) metrics.intervals.push(now - last);
    last = now;
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
  let nodes = 0,
    vertices = 0;
  d.scene.traverse((o) => {
    nodes++;
    if (o.isMesh) vertices += o.geometry.attributes.position.count;
  });
  return {
    gpu: ext
      ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)
      : gl.getParameter(gl.RENDERER),
    gpuTimer: !!timer,
    depthBits: gl.getParameter(gl.DEPTH_BITS),
    near: d.camera.near,
    pixelRatio: d.renderer.getPixelRatio(),
    nodes,
    vertices,
    triangles: d.renderer.info.render.triangles,
    drawCalls: d.renderer.info.render.calls,
    hazeCache: d.presentation?.contextFog?.state(),
    frozenStaticNodes: __campus.getState().frozenStaticNodes,
  };
});
const cdp = await page.context().newCDPSession(page);
const cpuRate = Number(process.env.PROBE_CPU || 1);
if (cpuRate > 1)
  await cdp.send("Emulation.setCPUThrottlingRate", { rate: cpuRate });
await cdp.send("Profiler.enable");
await cdp.send("Profiler.start");
async function reset() {
  await page.evaluate(() =>
    Object.values(__measurements).forEach((a) => (a.length = 0)),
  );
}
async function collect() {
  return page.evaluate(() => {
    const summary = {};
    for (const [key, values] of Object.entries(__measurements)) {
      const sorted = [...values].sort((a, b) => a - b);
      summary[key] = {
        samples: values.length,
        meanMs: values.reduce((a, b) => a + b, 0) / Math.max(1, values.length),
        p50Ms: sorted[Math.floor(sorted.length * 0.5)],
        p95Ms: sorted[Math.floor(sorted.length * 0.95)],
      };
    }
    return summary;
  });
}
await reset();
await page.waitForTimeout(2500);
const idle = await collect();
const dragStart = await page.evaluate(() => {
  for (let y = 800; y >= 550; y -= 30)
    for (let x = 750; x < 1100; x += 30)
      if (document.elementFromPoint(x, y)?.tagName === "CANVAS")
        return { x, y };
  throw Error("No clear canvas point");
});
async function drag(button) {
  await page.mouse.move(dragStart.x, dragStart.y);
  await page.mouse.down({ button });
  await reset();
  for (let i = 0; i < 120; i++) {
    await page.mouse.move(
      dragStart.x + Math.sin(i * 0.055) * 120,
      dragStart.y + Math.sin(i * 0.035) * 40,
    );
    await page.waitForTimeout(16);
  }
  await page.mouse.up({ button });
  return collect();
}
const orbit = await drag("left"),
  pan = await drag("right");
const { profile } = await cdp.send("Profiler.stop");
const counts = new Map();
for (const id of profile.samples || [])
  counts.set(id, (counts.get(id) || 0) + 1);
const topCpu = profile.nodes
  .map((n) => ({
    function: n.callFrame.functionName,
    url: n.callFrame.url.split("/").at(-1),
    line: n.callFrame.lineNumber + 1,
    selfSamples: counts.get(n.id) || 0,
  }))
  .sort((a, b) => b.selfSamples - a.selfSamples)
  .slice(0, 18);
const source = await readFile("src/main.js");
const result = {
  capturedAt: new Date().toISOString(),
  sourceSha256: createHash("sha256").update(source).digest("hex"),
  environment:
    "Headless Chrome, native ANGLE GPU, 1440x1000 CSS px. Local comparison only; not an in-app-browser or mobile FPS guarantee.",
  cpuThrottleRate: cpuRate,
  metadata,
  idle,
  orbit,
  pan,
  topCpu,
};
await mkdir("../../artifacts", { recursive: true });
await writeFile(
  `../../artifacts/${name}.json`,
  JSON.stringify(result, null, 2) + "\n",
);
await writeFile(`../../artifacts/${name}.cpuprofile`, JSON.stringify(profile));
console.log(JSON.stringify(result, null, 2));
await browser.close();
