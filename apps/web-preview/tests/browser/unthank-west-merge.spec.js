import { test, expect } from "@playwright/test";
test("Unthank west facade merges without changing original source vertices or colors", async ({
  page,
}) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const { installExteriorDetail, mergeBuildingDetailIntoSource } =
      await import("/src/exterior-detail.js");
    const spec = await (await fetch("/scene/unthank-west-detail.json")).json();
    const g = await new GLTFLoader().loadAsync("/scene/campus-expanded.glb");
    const source = g.scene.getObjectByName(spec.building_id);
    const oldGeometry = source.geometry;
    const before = source.geometry.toNonIndexed();
    const detail = installExteriorDetail(
      g.scene,
      spec,
      spec.base_asset_sha256,
      new Set([spec.building_id]),
    );
    const extra = detail.children[0].geometry.attributes.position.count;
    mergeBuildingDetailIntoSource(g.scene, detail, spec);
    const after = source.geometry;
    const same = (name) =>
      Array.from(before.attributes[name].array).every(
        (v, i) => v === after.attributes[name].array[i],
      );
    return {
      cloned: source.geometry !== oldGeometry,
      position: same("position"),
      color: same("color"),
      normal: same("normal"),
      originalCount: before.attributes.position.count,
      afterCount: after.attributes.position.count,
      extra,
      detailRemoved: !detail.parent,
      id: source.userData.asset_id,
    };
  });
  expect(result.cloned).toBe(true);
  expect(result.extra).toBe(4716);
  expect(result.position && result.color && result.normal).toBe(true);
  expect(result.afterCount).toBe(result.originalCount + result.extra);
  expect(result.detailRemoved).toBe(true);
  expect(result.id).toBe("context-oc-unthank");
});
