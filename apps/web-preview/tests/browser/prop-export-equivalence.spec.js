import { test, expect } from "@playwright/test";
test("all exported prop positions match the current procedural source", async ({
  page,
}) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js"),
      { createCampusProp } = await import("/src/props.js");
    const gltf = await new GLTFLoader().loadAsync("/props/campus-props.glb"),
      out = {};
    gltf.scene.traverse((o) => {
      if (!o.isMesh) return;
      const kind = o.userData.kind,
        a = createCampusProp(kind),
        x = a.geometry.attributes.position,
        y = o.geometry.attributes.position;
      out[kind] = {
        runtime: x.count,
        glb: y.count,
        match:
          x.count === y.count &&
          Array.from(x.array).every((v, i) => Math.abs(v - y.array[i]) < 1e-6),
      };
    });
    return out;
  });
  expect(Object.keys(result).sort()).toEqual([
    "bicycle",
    "car",
    "pickup",
    "scooter",
    "suv",
    "van",
  ]);
  for (const item of Object.values(result)) expect(item.match).toBe(true);
  console.log(JSON.stringify(result));
});
