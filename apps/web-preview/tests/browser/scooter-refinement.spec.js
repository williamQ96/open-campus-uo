import { test, expect } from "@playwright/test";
test("scooter export matches the runtime mesh and campus activity remains within budget", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  await page.waitForTimeout(500);
  let result = await page.evaluate(async () => {
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const { createCampusProp } = await import("/src/props.js");
    const g = await new GLTFLoader().loadAsync("/props/campus-props.glb");
    let m;
    g.scene.traverse((o) => {
      if (o.isMesh && o.userData.kind === "scooter") m = o;
    });
    const a = createCampusProp("scooter");
    const pa = a.geometry.getAttribute("position"),
      pb = m?.geometry.getAttribute("position");
    return {
      vertices: pb?.count,
      runtime: pa.count,
      positions:
        pb &&
        Array.from(pa.array).every((v, i) => Math.abs(v - pb.array[i]) < 1e-6),
      state: window.__campus.getState(),
    };
  });
  expect(result.vertices).toBe(3336);
  expect(result.runtime).toBe(result.vertices);
  expect(result.positions).toBe(true);
  expect(result.state.life.scooters).toBe(2);
  await page.locator("#settings-open").click();
  await page.getByRole("slider", { name: "Campus activity density" }).fill("0");
  await page.locator("#settings-close").click();
  await expect
    .poll(async () => page.evaluate(() => window.__campus.getState().drawCalls))
    .toBeLessThan(180);
  expect(errors).toEqual([]);
});
