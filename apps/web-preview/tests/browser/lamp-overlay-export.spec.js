import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
test("standalone lamp overlay matches source and scene-merged geometry", async ({
  page,
}) => {
  const bytes = readFileSync(
      new URL(
        "../../../../assets/exterior-refinement/pilot-lamp-overlay-2026-11-04.glb",
        import.meta.url,
      ),
    ),
    generator = createHash("sha256")
      .update(
        readFileSync(new URL("../../src/exterior-detail.js", import.meta.url)),
      )
      .digest("hex");
  await page.route("**/__local/lamp.glb", (r) =>
    r.fulfill({ body: bytes, contentType: "model/gltf-binary" }),
  );
  await page.goto("/");
  const result = await page.evaluate(async (generator) => {
    const T = await import("/node_modules/three/build/three.module.js"),
      { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js"),
      { createExteriorDetail, mergeEnvironmentDetail } =
        await import("/src/exterior-detail.js");
    const config = await (await fetch("/scene/presentation.json")).json(),
      spec = await (await fetch("/scene/pilot-lamp-detail.json")).json(),
      loader = new GLTFLoader(),
      base = await loader.loadAsync("/scene/campus-expanded.glb"),
      standalone = await loader.loadAsync("/__local/lamp.glb"),
      meshes = [];
    standalone.scene.updateMatrixWorld(true);
    standalone.scene.traverse((o) => {
      if (o.isMesh) meshes.push(o);
    });
    if (meshes.length !== 1) throw Error("expected one mesh");
    const output = meshes[0],
      target = base.scene.getObjectByName(spec.merge_target),
      n = target.geometry.index
        ? target.geometry.index.count
        : target.geometry.attributes.position.count,
      source = createExteriorDetail(spec, config.asset_sha256, new Set()),
      detail = source.children[0],
      errors = {};
    for (const key of ["position", "normal", "color"]) {
      const a = detail.geometry.attributes[key],
        b = output.geometry.attributes[key];
      if (a.count !== b.count) throw Error("attribute count mismatch");
      let max = 0;
      for (let i = 0; i < a.array.length; i++)
        max = Math.max(max, Math.abs(a.array[i] - b.array[i]));
      errors[key] = max;
    }
    const color = target.material.color.getHexString(),
      roughness = target.material.roughness,
      standaloneRoughness = output.material.roughness,
      targetSide = target.material.side,
      standaloneSide = output.material.side;
    base.scene.add(source);
    mergeEnvironmentDetail(base.scene, source, spec);
    const p = target.geometry.attributes.position;
    let mergedError = 0;
    for (let i = 0; i < output.geometry.attributes.position.array.length; i++)
      mergedError = Math.max(
        mergedError,
        Math.abs(
          p.array[n * 3 + i] - output.geometry.attributes.position.array[i],
        ),
      );
    return {
      count: output.geometry.attributes.position.count,
      errors,
      mergedError,
      pin:
        output.userData.source_overlay_sha256 ===
          config.exterior_details.find(
            (e) => e.url === "pilot-lamp-detail.json",
          ).sha256 && output.userData.generator_sha256 === generator,
      identity: output.matrixWorld.equals(new T.Matrix4()),
      kind: output.userData.asset_kind,
      color,
      roughness,
      standaloneRoughness,
      targetSide,
      standaloneSide,
    };
  }, generator);
  expect(result.count).toBe(3840);
  expect(result.pin && result.identity).toBe(true);
  expect(result.kind).toBe("prop");
  expect(result.color).toBe("3f514b");
  expect(result.standaloneSide).toBe(result.targetSide);
  expect(result.standaloneRoughness).toBeCloseTo(result.roughness, 6);
  expect(result.mergedError).toBeLessThanOrEqual(1e-5);
  for (const e of Object.values(result.errors))
    expect(e).toBeLessThanOrEqual(1e-6);
});
