import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";

test("complete bench export matches the suppressed and merged scene", async ({
  page,
}) => {
  const bytes = readFileSync(
    new URL(
      "../../../../assets/exterior-refinement/pilot-benches-complete-2026-11-04.glb",
      import.meta.url,
    ),
  );
  await page.route("**/__local/benches.glb", (r) =>
    r.fulfill({ body: bytes, contentType: "model/gltf-binary" }),
  );
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const T = await import("/node_modules/three/build/three.module.js");
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const { createExteriorDetail, mergeEnvironmentDetail } =
      await import("/src/exterior-detail.js");
    const { applyVegetationPatch } = await import("/src/vegetation-patch.js");
    const cfg = await (await fetch("/scene/presentation.json")).json(),
      spec = await (await fetch("/scene/pilot-bench-detail.json")).json(),
      loader = new GLTFLoader(),
      base = await loader.loadAsync("/scene/campus-expanded.glb"),
      output = await loader.loadAsync("/__local/benches.glb");
    for (const f of [
      "pilot-bench-back-suppression.json",
      "pilot-bench-seat-suppression.json",
    ])
      applyVegetationPatch(
        base.scene,
        await (await fetch("/scene/" + f)).json(),
        cfg.asset_sha256,
      );
    const supports = base.scene.getObjectByName("furniture_2"),
      wood = base.scene.getObjectByName("furniture_1"),
      original = wood.geometry.index.count,
      detail = createExteriorDetail(spec, cfg.asset_sha256, new Set());
    base.scene.add(detail);
    mergeEnvironmentDetail(base.scene, detail, spec);
    const legs = output.scene.getObjectByName("original-metal-supports"),
      boards = output.scene.getObjectByName("wooden-seats-backs-and-arms"),
      errors = {};
    for (const name of ["position", "normal"]) {
      const source = supports.geometry.attributes[name],
        copy = legs.geometry.attributes[name];
      let e = 0;
      for (let i = 0; i < copy.array.length; i++)
        e = Math.max(e, Math.abs(copy.array[i] - source.array[i]));
      errors["legs_" + name] = e;
      const w = wood.geometry.attributes[name],
        b = boards.geometry.attributes[name];
      e = 0;
      for (let i = 0; i < b.array.length; i++)
        e = Math.max(e, Math.abs(b.array[i] - w.array[original * 3 + i]));
      errors["wood_" + name] = e;
    }
    const root = output.scene.getObjectByName("pilot-benches-nine");
    document.body.replaceChildren();
    document.body.style.cssText = "margin:0;display:flex;background:#e6ece7";
    for (const objects of [
      [wood, supports],
      [boards, legs],
    ]) {
      const scene = new T.Scene();
      scene.background = new T.Color(0xe6ece7);
      scene.add(new T.HemisphereLight(0xffffff, 0x566357, 2));
      const light = new T.DirectionalLight(0xffffff, 2);
      light.position.set(2, 8, 5);
      scene.add(light);
      for (const o of objects) scene.add(new T.Mesh(o.geometry, o.material));
      const camera = new T.PerspectiveCamera(32, 1, 0.1, 100);
      camera.position.set(-576.2, 5.1, 63.5);
      camera.lookAt(-581, 3.05, 58);
      const renderer = new T.WebGLRenderer({
        antialias: true,
        preserveDrawingBuffer: true,
      });
      renderer.setSize(600, 600);
      document.body.appendChild(renderer.domElement);
      renderer.render(scene, camera);
    }
    return {
      errors,
      legCount: legs.geometry.attributes.position.count,
      woodCount: boards.geometry.attributes.position.count,
      pin: root.userData.base_asset_sha256 === cfg.asset_sha256,
      legColor: legs.material.color.getHexString(),
      woodColor: boards.material.color.getHexString(),
      indicesMatch: Array.from(legs.geometry.index.array).every(
        (v, i) => v === supports.geometry.index.array[i],
      ),
      materialMatch: ["side", "roughness", "metalness"].every(
        (k) =>
          legs.material[k] === supports.material[k] &&
          boards.material[k] === wood.material[k],
      ),
    };
  });
  expect(result).toEqual({
    errors: {
      legs_position: 0,
      legs_normal: 0,
      wood_position: 0,
      wood_normal: 0,
    },
    legCount: 432,
    woodCount: 6480,
    pin: true,
    legColor: "3f514b",
    woodColor: "77634f",
    indicesMatch: true,
    materialMatch: true,
  });
  await page.setViewportSize({ width: 1200, height: 600 });
  await page.screenshot({
    path: "../../docs/images/pilot-benches-complete-comparison-2026-11-04.png",
  });
});
