import { test, expect } from "@playwright/test";
test("context trunk variation preserves canopy and rejects mismatches", async ({
  page,
}) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js"),
      { refineContextTrunks } = await import("/src/context-trunks.js"),
      { varyContextTrunks } = await import("/src/context-trunk-variation.js");
    const base = await (await fetch("/scene/context-trunks.json")).json(),
      spec = await (await fetch("/scene/context-trunk-variation.json")).json(),
      gltf = await new GLTFLoader().loadAsync("/scene/campus-expanded.glb");
    refineContextTrunks(gltf.scene, base, base.base_asset_sha256);
    let mesh = gltf.scene.getObjectByName("campus-trees"),
      old = mesh.geometry;
    let rejected = false;
    try {
      varyContextTrunks(
        gltf.scene,
        { ...spec, top_ratio: 0.77 },
        spec.base_asset_sha256,
      );
    } catch {
      rejected = mesh.geometry === old;
    }
    let count = varyContextTrunks(gltf.scene, spec, spec.base_asset_sha256),
      next = mesh.geometry,
      canopy = true,
      indices = true,
      changed = 0,
      baseFixed = true,
      heights = true;
    for (const key of ["position", "normal", "color"])
      for (let i = 0; i < 45600 * 3; i++)
        if (old.attributes[key].array[i] !== next.attributes[key].array[i])
          canopy = false;
    for (let i = 0; i < old.index.count; i++)
      if (old.index.getX(i) !== next.index.getX(i)) indices = false;
    for (let t = 0; t < 300; t++) {
      let start = 45600 + t * 32;
      for (let j = 0; j < 32; j++) {
        let i = start + j;
        if (
          j % 4 < 2 &&
          (old.attributes.position.getX(i) !==
            next.attributes.position.getX(i) ||
            old.attributes.position.getZ(i) !==
              next.attributes.position.getZ(i))
        )
          baseFixed = false;
        if (
          old.attributes.position.getY(i) !== next.attributes.position.getY(i)
        )
          heights = false;
        if (
          j % 4 >= 2 &&
          (old.attributes.position.getX(i) !==
            next.attributes.position.getX(i) ||
            old.attributes.position.getZ(i) !==
              next.attributes.position.getZ(i))
        )
          changed++;
      }
    }
    return { rejected, count, canopy, indices, changed, baseFixed, heights };
  });
  expect(result).toEqual({
    rejected: true,
    count: 300,
    canopy: true,
    indices: true,
    changed: 4800,
    baseFixed: true,
    heights: true,
  });
});
