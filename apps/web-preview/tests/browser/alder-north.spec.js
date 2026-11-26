import { test, expect } from "@playwright/test";
test("Alder batch preserves original geometry, resolves facade hits and maintains all entrance positions", async ({
  page,
}) => {
  const baseline = "/?exterior-review=campus-frontage-baseline";
  const configUrl = "**/scene/presentation.json";
  const entries = async () => {
    await page.goto(baseline);
    await page.waitForFunction(() => window.__campus?.getState().ready);
    return page.evaluate(() => __campus.entranceInfo());
  };
  await page.route(configUrl, async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.exterior_details = json.exterior_details.filter(
      ({ url }) => url !== "alder-north-provisional-detail.json",
    );
    await route.fulfill({ response, json });
  });
  const before = await entries();
  await page.unroute(configUrl);
  const after = await entries();
  expect(after).toEqual(before);
  expect(after.find((e) => e.id === "roof-ee63827c").walkable).toBe(true);
  const result = await page.evaluate(async () => {
    const T = await import("/node_modules/three/build/three.module.js"),
      { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js"),
      { createExteriorDetail } = await import("/src/exterior-detail.js"),
      { mergeBatchBuildingDetail } =
        await import("/src/batch-building-detail.js"),
      { attachCollisionBoxes } = await import("/src/collision-supplement.js"),
      { resolveBuildingHit } = await import("/src/building-highlight.js");
    const s = await (
        await fetch("/scene/alder-north-provisional-detail.json")
      ).json(),
      m = await (await fetch("/scene/manifest.json")).json(),
      l = new GLTFLoader(),
      g = await l.loadAsync("/scene/campus-expanded.glb"),
      target = g.scene.getObjectByName(s.merge_batch_target),
      base = target.geometry.index
        ? target.geometry.toNonIndexed()
        : target.geometry.clone(),
      d = createExteriorDetail(
        s,
        s.base_asset_sha256,
        new Set([s.building_id]),
      ),
      extra = d.children[0].geometry.clone();
    let rejected = false;
    try {
      const bad = { ...s, merge_batch_bounds: [0, 0, 0, 1, 1, 1] },
        d2 = createExteriorDetail(
          bad,
          s.base_asset_sha256,
          new Set([s.building_id]),
        );
      g.scene.add(d2);
      mergeBatchBuildingDetail(g.scene, d2, bad);
    } catch {
      rejected = true;
    }
    g.scene.add(d);
    mergeBatchBuildingDetail(g.scene, d, s);
    let errors = {};
    for (const k of ["position", "normal", "color"]) {
      const actual = target.geometry.attributes[k],
        a = base.attributes[k],
        b = extra.attributes[k];
      if (actual.count !== a.count + b.count) throw Error("count mismatch");
      let max = 0;
      for (let i = 0; i < a.array.length; i++)
        max = Math.max(max, Math.abs(a.array[i] - actual.array[i]));
      for (let i = 0; i < b.array.length; i++)
        max = Math.max(
          max,
          Math.abs(b.array[i] - actual.array[a.array.length + i]),
        );
      errors[k] = max;
    }
    const records = new Map(m.buildings.map((b) => [b.id, b]));
    attachCollisionBoxes(m.buildings, [
      {
        buildingId: s.building_id,
        boxes: s.overlay_collision_boxes_enu_m,
        overlay: true,
      },
    ]);
    g.scene.updateMatrixWorld(true);
    const ray = new T.Raycaster(
        new T.Vector3(-730.4, 7, 250),
        new T.Vector3(0, 0, 1),
      ),
      hit = ray.intersectObject(target, false)[0];
    const selected = resolveBuildingHit(hit, records);
    return {
      errors,
      selected,
      rejected,
      ids: target.userData.asset_ids.length,
    };
  });
  expect(result).toEqual({
    errors: { position: 0, normal: 0, color: 0 },
    selected: "roof-ee63827c",
    rejected: true,
    ids: 52,
  });
});
