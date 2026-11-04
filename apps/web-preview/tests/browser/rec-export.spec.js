import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { capturePreview } from "./screenshots.js";

test("standalone rotated facade matches runtime geometry and rendering", async ({
  page,
}) => {
  const glb = readFileSync(
    new URL(
      "../../../../assets/exterior-refinement/rec-east-detail-2026-11-04.glb",
      import.meta.url,
    ),
  );
  await page.route("**/__local/rec-export.glb", (route) =>
    route.fulfill({ status: 200, contentType: "model/gltf-binary", body: glb }),
  );
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const T = await import("/node_modules/three/build/three.module.js");
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const { createExteriorDetail } = await import("/src/exterior-detail.js");
    const spec = await (await fetch("/scene/rec-east-detail.json")).json();
    const runtime = createExteriorDetail(
      spec,
      spec.base_asset_sha256,
      new Set([spec.building_id]),
    );
    const loaded = await new GLTFLoader().loadAsync("/__local/rec-export.glb");
    loaded.scene.updateMatrixWorld(true);
    const meshes = [];
    loaded.scene.traverse((o) => {
      if (o.isMesh) meshes.push(o);
    });
    if (meshes.length !== 1) throw Error("Expected one exported mesh");
    const a = runtime.children[0],
      b = meshes[0],
      differences = {};
    for (const key of ["position", "normal", "color"]) {
      const x = a.geometry.attributes[key],
        y = b.geometry.attributes[key];
      let max = 0;
      if (x.count !== y.count) throw Error(`${key} count mismatch`);
      for (let i = 0; i < x.array.length; i++)
        max = Math.max(max, Math.abs(x.array[i] - y.array[i]));
      differences[key] = max;
    }
    const bounds = new T.Box3().setFromObject(runtime),
      center = bounds.getCenter(new T.Vector3());
    document.body.replaceChildren();
    document.body.style.cssText =
      "margin:0;background:#e1e8dc;display:flex;gap:4px";
    const images = [];
    for (const [label, object] of [
      ["Runtime source", runtime],
      ["Standalone GLB", loaded.scene],
    ]) {
      const wrapper = document.createElement("div");
      wrapper.style.cssText =
        "width:50%;text-align:center;font:18px sans-serif;color:#25372f";
      wrapper.append(label);
      document.body.append(wrapper);
      const scene = new T.Scene();
      scene.background = new T.Color(0xe1e8dc);
      scene.add(object);
      scene.add(new T.HemisphereLight(0xffffff, 0x9baba0, 2));
      const sun = new T.DirectionalLight(0xffffff, 2);
      sun.position.set(10, 20, 10);
      scene.add(sun);
      const renderer = new T.WebGLRenderer({
        antialias: true,
        preserveDrawingBuffer: true,
      });
      renderer.setSize(680, 420);
      renderer.setPixelRatio(1);
      wrapper.append(renderer.domElement);
      const camera = new T.OrthographicCamera(-31, 31, 19.15, -19.15, 0.1, 200);
      camera.position.copy(center).add(new T.Vector3(80, 8, 10));
      camera.lookAt(center);
      renderer.render(scene, camera);
      const gl = renderer.getContext(),
        pixels = new Uint8Array(680 * 420 * 4);
      gl.readPixels(0, 0, 680, 420, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
      images.push(pixels);
    }
    let diff = 0,
      max = 0;
    for (let i = 0; i < images[0].length; i++) {
      let v = Math.abs(images[0][i] - images[1][i]);
      diff += v;
      max = Math.max(max, v);
    }
    return {
      differences,
      vertexCount: a.geometry.attributes.position.count,
      identity: b.matrixWorld.equals(new T.Matrix4()),
      assetId: b.userData.asset_id,
      sourceHash: b.userData.source_overlay_sha256,
      meanPixelError: diff / images[0].length,
      maxPixelError: max,
    };
  });
  expect(result.vertexCount).toBe(936);
  expect(result.identity).toBe(true);
  expect(result.assetId).toBe("roof-af9a4442");
  expect(result.sourceHash).toBe(
    "96f3433f0dadd7a6a409ed547924632718512493e56f7e27fc67439fa72bccfa",
  );
  for (const error of Object.values(result.differences))
    expect(error).toBeLessThanOrEqual(1e-6);
  expect(result.meanPixelError).toBeLessThan(0.01);
  console.log(JSON.stringify(result));
  await capturePreview(
    page,
    "../../docs/images/rec-export-comparison-2026-11-04.png",
  );
});

test("all three rotation axes survive a GLB round trip", async ({ page }) => {
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const T = await import("/node_modules/three/build/three.module.js");
    const { createExteriorDetail } = await import("/src/exterior-detail.js");
    const { GLTFExporter } =
      await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js");
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const rotation = [0.31, -0.42, 0.23],
      position = [2, 3, 4],
      size = [2, 4, 6],
      id = "test-building",
      spec = {
        version: 1,
        base_asset_sha256: "test",
        building_id: id,
        replace_building: false,
        objects: [
          {
            kind: "building",
            material: "glass",
            shape: "box",
            rotation,
            position,
            size,
          },
        ],
      };
    const mesh = createExteriorDetail(spec, "test", new Set([id]));
    const raw = await new GLTFExporter().parseAsync(mesh, { binary: true });
    const loaded = await new GLTFLoader().parseAsync(raw, "");
    let actual;
    loaded.scene.traverse((o) => {
      if (o.isMesh) actual = o.geometry.attributes.position;
    });
    const expected = new T.Vector3(1, 2, 3)
      .applyAxisAngle(new T.Vector3(1, 0, 0), rotation[0])
      .applyAxisAngle(new T.Vector3(0, 1, 0), rotation[1])
      .applyAxisAngle(new T.Vector3(0, 0, 1), rotation[2])
      .add(new T.Vector3(...position));
    let nearest = Infinity;
    for (let i = 0; i < actual.count; i++)
      nearest = Math.min(
        nearest,
        expected.distanceTo(new T.Vector3().fromBufferAttribute(actual, i)),
      );
    return { nearest, count: actual.count };
  });
  expect(result.count).toBe(36);
  expect(result.nearest).toBeLessThan(1e-5);
});
