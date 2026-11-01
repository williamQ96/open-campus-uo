// Test-only A/B injection: compare cached and original spatial-haze shaders.
import { chromium } from "@playwright/test";
import { writeFile, mkdir } from "node:fs/promises";
const browser = await chromium.launch({ channel: "chrome", headless: true });
await mkdir("../../artifacts", { recursive: true });
const results = [];
for (const cached of [false, true, true, false]) {
  const index = results.length;
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
    deviceScaleFactor: 1,
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });
  await page.route("**/src/campus.js*", async (route) => {
    const response = await route.fetch();
    let s = (await response.text()).replace(
      "window.__campus = {",
      "window.__renderProbe={scene,camera,renderer,model,presentation,life,sky,character,contactShadow}; window.__campus = {",
    );
    if (cached)
      s = s.replace(
        "if (presentation?.contextFog) {",
        "if (presentation?.contextFog) { viewerSettings.cache_static_haze=true;",
      );
    await route.fulfill({ response, body: s });
  });
  if (!cached)
    await page.route("**/src/context-fog.js*", async (route) => {
      const response = await route.fetch();
      const s = await response.text();
      const match = "bakeMesh(mesh, materials = [mesh.material].flat()) {";
      if (!s.includes(match)) throw Error("Haze bypass marker missing");
      await route.fulfill({
        response,
        body: s.replace(match, match + " return false;"),
      });
    });
  await page.goto("http://127.0.0.1:5173/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const info = await page.evaluate(() => {
    const d = __renderProbe;
    d.renderer.setAnimationLoop(null);
    d.life.setDensity(0);
    d.character.root.visible = false;
    d.contactShadow.visible = false;
    d.camera.position.set(-650, 455, -310);
    d.camera.near = 32;
    d.camera.lookAt(-350, 5, 0);
    d.camera.updateProjectionMatrix();
    d.sky.update(d.camera, 0, false);
    d.renderer.shadowMap.needsUpdate = true;
    d.renderer.render(d.scene, d.camera);
    return {
      cache: d.presentation.contextFog.state(),
      triangles: d.renderer.info.render.triangles,
      drawCalls: d.renderer.info.render.calls,
    };
  });
  if (index < 2)
    for (const toon of [true, false]) {
      const image = await page.evaluate((toon) => {
        const d = __renderProbe;
        d.presentation.setToon(toon);
        d.renderer.shadowMap.needsUpdate = true;
        d.renderer.render(d.scene, d.camera);
        d.renderer.getContext().finish();
        return d.renderer.domElement.toDataURL("image/png");
      }, toon);
      await writeFile(
        `../../artifacts/phase14-haze-${cached ? "cached" : "dynamic"}-${toon ? "toon" : "pbr"}.png`,
        Buffer.from(image.split(",")[1], "base64"),
      );
    }
  const timing = await page.evaluate(async () => {
    const { scene, camera, renderer, presentation } = __renderProbe;
    presentation.setToon(true);
    const gl = renderer.getContext(),
      ext = gl.getExtension("EXT_disjoint_timer_query_webgl2"),
      pending = [],
      times = [];
    for (let i = 0; i < 160; i++) {
      await new Promise(requestAnimationFrame);
      while (
        pending.length &&
        gl.getQueryParameter(pending[0], gl.QUERY_RESULT_AVAILABLE)
      ) {
        const q = pending.shift();
        if (!gl.getParameter(ext.GPU_DISJOINT_EXT))
          times.push(gl.getQueryParameter(q, gl.QUERY_RESULT) / 1e6 / 3);
        gl.deleteQuery(q);
      }
      const q = gl.createQuery();
      gl.beginQuery(ext.TIME_ELAPSED_EXT, q);
      for (let k = 0; k < 3; k++) renderer.render(scene, camera);
      gl.endQuery(ext.TIME_ELAPSED_EXT);
      pending.push(q);
    }
    const sorted = times.slice(20).sort((a, b) => a - b);
    return {
      samples: sorted.length,
      meanMs: sorted.reduce((a, b) => a + b, 0) / sorted.length,
      p50Ms: sorted[Math.floor(sorted.length * 0.5)],
      p95Ms: sorted[Math.floor(sorted.length * 0.95)],
    };
  });
  results.push({ cached, info, timing, errors });
  await page.close();
}
await writeFile(
  "../../artifacts/phase14-haze-ab.json",
  JSON.stringify(results, null, 2) + "\n",
);
console.log(JSON.stringify(results, null, 2));
await browser.close();
