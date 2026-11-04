import { test, expect } from "@playwright/test";
test("Lokey wall patch affects only source-matched wall vertices", async ({
  page,
}) => {
  await page.goto("/");
  const r = await page.evaluate(async () => {
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const { applyWallColorPatch } = await import("/src/wall-color-patch.js");
    const s = await (await fetch("/scene/lokey-wall-color.json")).json();
    const gltf = await new GLTFLoader().loadAsync("/scene/campus-expanded.glb");
    const mesh = gltf.scene.getObjectByName(s.building_id),
      old = mesh.geometry,
      material = mesh.material,
      data = JSON.stringify(mesh.userData),
      before = old.attributes.color.array.slice();
    let rejected = false;
    try {
      applyWallColorPatch(
        gltf.scene,
        { ...s, expected_vertices: 121 },
        s.base_asset_sha256,
      );
    } catch {
      rejected = true;
    }
    const untouched = mesh.geometry === old;
    applyWallColorPatch(gltf.scene, s, s.base_asset_sha256);
    const next = mesh.geometry,
      colors = next.attributes.color.array;
    let changed = 0,
      wrong = 0;
    for (let i = 0; i < old.attributes.position.count; i++)
      if ([0, 1, 2].some((k) => before[i * 3 + k] !== colors[i * 3 + k])) {
        changed++;
        const c = old.attributes.color,
          n = old.attributes.normal;
        if (
          Math.abs(n.getY(i)) >= s.normal_y_abs_max ||
          [c.getX(i), c.getY(i), c.getZ(i)].some(
            (x, k) => Math.round(x * 255) !== s.source_rgb8[k],
          )
        )
          wrong++;
      }
    const same =
      ["position", "normal"].every((k) =>
        Array.from(old.attributes[k].array).every(
          (x, i) => x === next.attributes[k].array[i],
        ),
      ) &&
      Array.from(old.index?.array || []).every(
        (x, i) => x === next.index.array[i],
      );
    return {
      rejected,
      untouched,
      changed,
      wrong,
      same,
      material: mesh.material === material,
      identity: JSON.stringify(mesh.userData) === data,
    };
  });
  expect(r).toEqual({
    rejected: true,
    untouched: true,
    changed: 120,
    wrong: 0,
    same: true,
    material: true,
    identity: true,
  });
});
