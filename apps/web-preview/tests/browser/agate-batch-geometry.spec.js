import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
test("Agate batch and standalone export preserve source and detail geometry", async ({
  page,
}) => {
  const bytes = readFileSync(
    new URL(
      "../../../../assets/exterior-refinement/agate-west-provisional-2026-11-04.glb",
      import.meta.url,
    ),
  );
  await page.route("**/__local/agate.glb", (r) =>
    r.fulfill({ body: bytes, contentType: "model/gltf-binary" }),
  );
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js"),
      { createExteriorDetail } = await import("/src/exterior-detail.js"),
      { mergeBatchBuildingDetail } =
        await import("/src/batch-building-detail.js");
    const s = await (
        await fetch("/scene/agate-west-provisional-detail.json")
      ).json(),
      l = new GLTFLoader(),
      base = await l.loadAsync("/scene/campus-expanded.glb"),
      out = await l.loadAsync("/__local/agate.glb"),
      target = base.scene.getObjectByName(s.merge_batch_target),
      initial = target.geometry.index
        ? target.geometry.toNonIndexed()
        : target.geometry.clone(),
      detail = createExteriorDetail(
        s,
        s.base_asset_sha256,
        new Set([s.building_id]),
      ),
      extra = detail.children[0].geometry.clone(),
      standalone = [];
    out.scene.traverse((x) => {
      if (x.isMesh) standalone.push(x);
    });
    if (standalone.length !== 1) throw Error("Export mesh count");
    base.scene.add(detail);
    mergeBatchBuildingDetail(base.scene, detail, s);
    const errors = {};
    for (const key of ["position", "normal", "color"]) {
      const a = initial.attributes[key],
        b = extra.attributes[key],
        c = target.geometry.attributes[key],
        d = standalone[0].geometry.attributes[key];
      if (c.count !== a.count + b.count || b.count !== d.count)
        throw Error("Counts");
      let error = 0;
      for (let i = 0; i < a.array.length; i++)
        error = Math.max(error, Math.abs(a.array[i] - c.array[i]));
      for (let i = 0; i < b.array.length; i++)
        error = Math.max(
          error,
          Math.abs(b.array[i] - c.array[a.array.length + i]),
          Math.abs(b.array[i] - d.array[i]),
        );
      errors[key] = error;
    }
    return {
      errors,
      ids: target.userData.asset_ids,
      sourceHash:
        standalone[0].userData.base_asset_sha256 === s.base_asset_sha256,
      assetId: standalone[0].userData.asset_id,
    };
  });
  expect(result.errors).toEqual({ position: 0, normal: 0, color: 0 });
  expect(result.ids).toContain("roof-b068940e");
  expect(result.ids).toHaveLength(3);
  expect(result.sourceHash).toBe(true);
  expect(result.assetId).toBe("roof-b068940e");
});
