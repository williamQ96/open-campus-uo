import { test, expect } from "@playwright/test";
test("pinned Longhouse palette preserves other geometry and exports overlay exactly", async ({
  page,
}) => {
  await page.goto("/");
  const r = await page.evaluate(async () => {
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const { applyBatchPalette } = await import("/src/batch-palette.js");
    const { createExteriorDetail } = await import("/src/exterior-detail.js");
    const { mergeBatchBuildingDetail } =
      await import("/src/batch-building-detail.js");
    const p = await (await fetch("/scene/longhouse-batch-palette.json")).json();
    const s = await (
      await fetch("/scene/longhouse-south-provisional-detail.json")
    ).json();
    const loader = new GLTFLoader(),
      base = await loader.loadAsync("/scene/campus-expanded.glb");
    const mesh = base.scene.getObjectByName(p.target_name),
      original = mesh.geometry,
      material = mesh.material;
    const ids = JSON.stringify(mesh.userData.asset_ids),
      before = original.attributes.color.array.slice();
    const bad = structuredClone(p);
    bad.groups[0].expected_vertices++;
    let rejected = false;
    try {
      applyBatchPalette(base.scene, bad, p.base_asset_sha256);
    } catch {
      rejected = true;
    }
    if (mesh.geometry !== original)
      throw Error("invalid patch mutated geometry");
    const counts = applyBatchPalette(base.scene, p, p.base_asset_sha256),
      altered = mesh.geometry;
    const geometrySame =
      ["position", "normal"].every((k) =>
        Array.from(original.attributes[k].array).every(
          (x, i) => x === altered.attributes[k].array[i],
        ),
      ) &&
      Array.from(original.index?.array || []).every(
        (x, i) => x === altered.index.array[i],
      );
    let changed = 0,
      outside = 0;
    const v = altered.attributes.position,
      c = altered.attributes.color,
      b = p.bounds;
    for (let i = 0; i < v.count; i++)
      if ([0, 1, 2].some((k) => before[i * 3 + k] !== c.array[i * 3 + k])) {
        changed++;
        if (
          [v.getX(i), v.getY(i), v.getZ(i)].some(
            (x, k) => x < b[k] || x > b[k + 3],
          )
        )
          outside++;
      }
    const initial = altered.index ? altered.toNonIndexed() : altered.clone(),
      detail = createExteriorDetail(
        s,
        s.base_asset_sha256,
        new Set([s.building_id]),
      ),
      extra = detail.children[0].geometry.clone();
    base.scene.add(detail);
    mergeBatchBuildingDetail(base.scene, detail, s);
    const errors = {};
    for (const k of ["position", "normal", "color"]) {
      let a = initial.attributes[k].array,
        b = extra.attributes[k].array,
        c = mesh.geometry.attributes[k].array;
      if (c.length !== a.length + b.length) throw Error("merge count");
      let max = 0;
      for (let i = 0; i < a.length; i++)
        max = Math.max(max, Math.abs(a[i] - c[i]));
      for (let i = 0; i < b.length; i++)
        max = Math.max(max, Math.abs(b[i] - c[a.length + i]));
      errors[k] = max;
    }
    return {
      rejected,
      counts,
      changed,
      outside,
      geometrySame,
      idsSame: ids === JSON.stringify(mesh.userData.asset_ids),
      idCount: mesh.userData.asset_ids.length,
      materialSame: mesh.material === material,
      errors,
    };
  });
  expect(r).toEqual({
    rejected: true,
    counts: [80, 6, 6],
    changed: 92,
    outside: 0,
    geometrySame: true,
    idsSame: true,
    idCount: 22,
    materialSame: true,
    errors: { position: 0, normal: 0, color: 0 },
  });
});
