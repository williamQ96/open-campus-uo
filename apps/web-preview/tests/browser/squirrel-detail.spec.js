import { test, expect } from "@playwright/test";
test("squirrel accents preserve source body, shared material batching and campus budget", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const result = await page.evaluate(async () => {
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const { addSquirrelEyes } = await import("/src/squirrel-detail.js");
    const loader = new GLTFLoader(),
      gltf = await loader.loadAsync("/animals/campus-squirrel.glb");
    const original = gltf.scene.getObjectByName("Campus_squirrel_-_CC0_source");
    const before = original.geometry.toNonIndexed();
    const info = addSquirrelEyes(gltf.scene),
      after = info.mesh.geometry;
    let max = 0;
    for (const key of ["position", "normal"]) {
      const a = before.attributes[key].array,
        b = after.attributes[key].array;
      for (let i = 0; i < a.length; i++)
        max = Math.max(max, Math.abs(a[i] - b[i]));
    }
    let rejection = false;
    try {
      addSquirrelEyes(gltf.scene);
    } catch {
      rejection = true;
    }
    return {
      max,
      rejection,
      body: info.originalVertices,
      extra: info.addedVertices,
      oneMesh: gltf.scene.children.length,
      vertexColors: info.mesh.material.vertexColors,
      life: __campus.getState().life,
    };
  });
  expect(result.max).toBe(0);
  expect(result.body).toBe(2700);
  expect(result.extra).toBe(480);
  expect(result.rejection).toBe(true);
  expect(result.vertexColors).toBe(true);
  expect(result.life.squirrels).toBe(8);
  await page.locator("#settings-open").click();
  await page.getByRole("slider", { name: "Campus activity density" }).fill("0");
  await page.locator("#settings-close").click();
  await expect
    .poll(() => page.evaluate(() => __campus.getState().drawCalls))
    .toBeLessThan(180);
  expect(errors).toEqual([]);
});
