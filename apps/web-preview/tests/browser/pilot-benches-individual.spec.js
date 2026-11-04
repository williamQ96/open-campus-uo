import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";

test("individual bench groups reproduce the complete export", async ({
  page,
}) => {
  for (const [name, file] of [
    ["old", "pilot-benches-complete-2026-11-04.glb"],
    ["individual", "pilot-benches-individual-2026-11-04.glb"],
  ]) {
    const bytes = readFileSync(
      new URL(
        `../../../../assets/exterior-refinement/${file}`,
        import.meta.url,
      ),
    );
    await page.route(`**/__local/${name}.glb`, (r) =>
      r.fulfill({ body: bytes, contentType: "model/gltf-binary" }),
    );
  }
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const T = await import("/node_modules/three/build/three.module.js");
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const loader = new GLTFLoader();
    const [old, individual] = await Promise.all([
      loader.loadAsync("/__local/old.glb"),
      loader.loadAsync("/__local/individual.glb"),
    ]);
    const counts = (scene) => {
      scene.updateMatrixWorld(true);
      const result = new Map(),
        vector = new T.Vector3();
      scene.traverse((o) => {
        if (!o.isMesh) return;
        const p = o.geometry.attributes.position,
          n = o.geometry.attributes.normal;
        for (let i = 0; i < p.count; i++) {
          vector.fromBufferAttribute(p, i).applyMatrix4(o.matrixWorld);
          const key = [
            o.material.color.getHexString(),
            vector.x,
            vector.y,
            vector.z,
            n.getX(i),
            n.getY(i),
            n.getZ(i),
          ].join(",");
          result.set(key, (result.get(key) || 0) + 1);
        }
      });
      return result;
    };
    const a = counts(old.scene),
      b = counts(individual.scene);
    const groups = Array.from({ length: 9 }, (_, i) =>
      individual.scene.getObjectByName(`bench-${i + 1}`),
    );
    document.body.replaceChildren();
    document.body.style.cssText = "margin:0;display:flex;background:#e6ece7";
    const frames = [];
    for (const source of [old.scene, individual.scene]) {
      const scene = new T.Scene();
      scene.background = new T.Color(0xe6ece7);
      scene.add(new T.HemisphereLight(0xffffff, 0x566357, 2));
      const light = new T.DirectionalLight(0xffffff, 2);
      light.position.set(2, 8, 5);
      scene.add(light);
      scene.add(source);
      const camera = new T.PerspectiveCamera(32, 1, 0.1, 100);
      camera.position.set(-576.2, 5.1, 63.5);
      camera.lookAt(-581, 3.05, 58);
      const renderer = new T.WebGLRenderer({
        antialias: true,
        preserveDrawingBuffer: true,
      });
      renderer.setSize(500, 500);
      document.body.appendChild(renderer.domElement);
      renderer.render(scene, camera);
      const pixels = new Uint8Array(500 * 500 * 4);
      renderer
        .getContext()
        .readPixels(
          0,
          0,
          500,
          500,
          renderer.getContext().RGBA,
          renderer.getContext().UNSIGNED_BYTE,
          pixels,
        );
      frames.push(pixels);
    }
    let maxPixel = 0,
      changed = 0;
    for (let i = 0; i < frames[0].length; i++) {
      const d = Math.abs(frames[0][i] - frames[1][i]);
      maxPixel = Math.max(maxPixel, d);
      if (d) changed++;
    }
    return {
      equivalent:
        a.size === b.size &&
        [...a].every(([key, value]) => b.get(key) === value),
      groups: groups.map((g) => g?.children.map((c) => c.name)),
      maxPixel,
      changed,
    };
  });
  expect(result.equivalent).toBe(true);
  expect(result.groups).toEqual(
    Array.from({ length: 9 }, (_, i) => [
      `bench-${i + 1}-supports`,
      `bench-${i + 1}-wood`,
    ]),
  );
  expect(result.changed).toBeLessThan(2000);
  expect(result.maxPixel).toBeLessThanOrEqual(50);
});
