import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
test("varied context trees preserve pinned runtime geometry and render", async ({
  page,
}) => {
  const bytes = readFileSync(
    new URL(
      "../../../../assets/vegetation-refinement/context-trees-varied-2026-11-04.glb",
      import.meta.url,
    ),
  );
  const code = readFileSync(
      new URL("../../src/context-trunks.js", import.meta.url),
    ),
    specBytes = readFileSync(
      new URL("../../public/scene/context-trunks.json", import.meta.url),
    );
  const sha = (b) => createHash("sha256").update(b).digest("hex"),
    hashes = {
      source: sha(code),
      spec: sha(specBytes),
      variation: sha(
        readFileSync(
          new URL(
            "../../public/scene/context-trunk-variation.json",
            import.meta.url,
          ),
        ),
      ),
      variationCode: sha(
        readFileSync(
          new URL("../../src/context-trunk-variation.js", import.meta.url),
        ),
      ),
    };
  await page.route("**/__local/context-trees.glb", (r) =>
    r.fulfill({ body: bytes, contentType: "model/gltf-binary" }),
  );
  await page.goto("/");
  const result = await page.evaluate(async (hashes) => {
    const T = await import("/node_modules/three/build/three.module.js"),
      { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js"),
      { refineContextTrunks } = await import("/src/context-trunks.js");
    const spec = await (await fetch("/scene/context-trunks.json")).json(),
      g = await new GLTFLoader().loadAsync("/scene/campus-expanded.glb");
    refineContextTrunks(g.scene, spec, spec.base_asset_sha256);
    const { varyContextTrunks } =
      await import("/src/context-trunk-variation.js");
    const variation = await (
      await fetch("/scene/context-trunk-variation.json")
    ).json();
    varyContextTrunks(g.scene, variation, spec.base_asset_sha256);
    const src = g.scene.getObjectByName("campus-trees"),
      loaded = await new GLTFLoader().loadAsync("/__local/context-trees.glb");
    loaded.scene.updateMatrixWorld(true);
    const items = [];
    loaded.scene.traverse((o) => {
      if (o.isMesh) items.push(o);
    });
    if (items.length !== 1) throw Error("Expected one mesh");
    const dst = items[0],
      errors = {};
    for (const key of ["position", "normal", "color"]) {
      const a = src.geometry.attributes[key],
        b = dst.geometry.attributes[key];
      if (a.count !== b.count || a.itemSize !== b.itemSize)
        throw Error("attribute count");
      let max = 0;
      for (let i = 0; i < a.array.length; i++)
        max = Math.max(max, Math.abs(a.array[i] - b.array[i]));
      errors[key] = max;
    }
    const sameIndex =
      src.geometry.index.count === dst.geometry.index.count &&
      src.geometry.index.array.every(
        (v, i) => v === dst.geometry.index.array[i],
      );
    const renderer = new T.WebGLRenderer({ antialias: false }),
      target = new T.WebGLRenderTarget(512, 512),
      cam = new T.PerspectiveCamera(45, 1, 0.1, 500);
    cam.position.set(-120, 8, 112);
    cam.lookAt(-109.1, 5, 102.69);
    const render = (object) => {
      const scene = new T.Scene();
      scene.background = new T.Color("#9cbcd2");
      scene.add(new T.AmbientLight("white", 1));
      const sun = new T.DirectionalLight("white", 2);
      sun.position.set(-10, 30, 20);
      scene.add(sun);
      scene.add(new T.Mesh(object.geometry, object.material));
      renderer.setRenderTarget(target);
      renderer.render(scene, cam);
      const pixels = new Uint8Array(512 * 512 * 4);
      renderer.readRenderTargetPixels(target, 0, 0, 512, 512, pixels);
      return pixels;
    };
    const a = render(src),
      b = render(dst);
    let diff = 0,
      nonbackground = 0;
    for (let i = 0; i < a.length; i++) {
      diff = Math.max(diff, Math.abs(a[i] - b[i]));
      if (i % 4 === 1 && a[i] < 130) nonbackground++;
    }
    renderer.dispose();
    target.dispose();
    return {
      errors,
      sameIndex,
      diff,
      nonbackground,
      identity: dst.matrixWorld.equals(new T.Matrix4()),
      source: dst.userData.source_code_sha256 === hashes.source,
      spec: dst.userData.source_spec_sha256 === hashes.spec,
      variation:
        dst.userData.variation_spec_sha256 === hashes.variation &&
        dst.userData.variation_code_sha256 === hashes.variationCode,
      base: dst.userData.source_glb_sha256 === spec.base_asset_sha256,
      count: dst.userData.tree_count,
      vertices: dst.geometry.attributes.position.count,
    };
  }, hashes);
  expect(
    result.sameIndex &&
      result.identity &&
      result.source &&
      result.spec &&
      result.variation &&
      result.base,
  ).toBe(true);
  expect(result.count).toBe(300);
  expect(result.vertices).toBe(55200);
  expect(result.nonbackground).toBeGreaterThan(100);
  expect(result.diff).toBe(0);
  for (const e of Object.values(result.errors))
    expect(e).toBeLessThanOrEqual(1e-6);
});
