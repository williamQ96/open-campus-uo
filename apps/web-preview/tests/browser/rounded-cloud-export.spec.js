import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
test("rounded cloud export matches runtime geometry and unlit appearance", async ({
  page,
}) => {
  const files = ["sky.js", "npc-templates.js", "cloud-volumes.js"],
    hashes = Object.fromEntries(
      files.map((n) => [
        n,
        createHash("sha256")
          .update(readFileSync(new URL(`../../src/${n}`, import.meta.url)))
          .digest("hex"),
      ]),
    ),
    bytes = readFileSync(
      new URL(
        "../../../../assets/sky-refinement/campus-rounded-clouds-2026-11-04.glb",
        import.meta.url,
      ),
    );
  await page.route("**/__local/clouds.glb", (r) =>
    r.fulfill({ body: bytes, contentType: "model/gltf-binary" }),
  );
  await page.goto("/");
  const result = await page.evaluate(async (hashes) => {
    const T = await import("/node_modules/three/build/three.module.js"),
      { createSky } = await import("/src/sky.js"),
      { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const s = new T.Scene();
    createSky(s);
    const { shapeCloudVolumes } = await import("/src/cloud-volumes.js");
    shapeCloudVolumes(s);
    const a = s.getObjectByName("Rounded voxel cloud layer"),
      g = await new GLTFLoader().loadAsync("/__local/clouds.glb"),
      meshes = [];
    g.scene.updateMatrixWorld(true);
    g.scene.traverse((o) => {
      if (o.isMesh) meshes.push(o);
    });
    if (meshes.length !== 1) throw Error("expected one cloud mesh");
    const b = meshes[0],
      errors = {};
    for (const key of ["position", "normal", "color"]) {
      const x = a.geometry.attributes[key],
        y = b.geometry.attributes[key];
      if (x.count !== y.count) throw Error("count mismatch");
      let max = 0;
      for (let i = 0; i < x.array.length; i++)
        max = Math.max(max, Math.abs(x.array[i] - y.array[i]));
      errors[key] = max;
    }
    const ix = a.geometry.index,
      iy = b.geometry.index;
    if (
      !!ix !== !!iy ||
      (ix &&
        (ix.count !== iy.count ||
          Array.from(ix.array).some((v, i) => v !== iy.array[i])))
    )
      throw Error("triangle indices differ");
    const renderer = new T.WebGLRenderer({
      preserveDrawingBuffer: true,
      antialias: false,
    });
    renderer.setSize(512, 512);
    renderer.setClearColor(0x7caed0);
    const camera = new T.PerspectiveCamera(55, 1, 1, 10000);
    camera.position.set(0, 650, 0);
    camera.lookAt(3000, 650, 0);
    const render = (m) => {
      const sc = new T.Scene();
      sc.add(m.clone());
      renderer.render(sc, camera);
      const pixels = new Uint8Array(512 * 512 * 4);
      renderer
        .getContext()
        .readPixels(
          0,
          0,
          512,
          512,
          renderer.getContext().RGBA,
          renderer.getContext().UNSIGNED_BYTE,
          pixels,
        );
      return pixels;
    };
    const x = render(a),
      y = render(b);
    let changed = 0,
      max = 0;
    for (let i = 0; i < x.length; i++) {
      const delta = Math.abs(x[i] - y[i]);
      if (delta > 1) changed++;
      max = Math.max(max, delta);
    }
    let nonBackground = 0;
    for (let i = 0; i < x.length; i += 4) {
      if (x[i] !== x[0] || x[i + 1] !== x[1] || x[i + 2] !== x[2])
        nonBackground++;
    }
    renderer.dispose();
    return {
      nonBackground,
      errors,
      count: a.geometry.attributes.position.count,
      pin:
        b.userData.source_sha256 === hashes["sky.js"] &&
        b.userData.random_source_sha256 === hashes["npc-templates.js"] &&
        b.userData.volume_source_sha256 === hashes["cloud-volumes.js"],
      identity: b.matrixWorld.equals(new T.Matrix4()),
      opacity: b.material.opacity,
      transparent: b.material.transparent,
      depthWrite: b.material.depthWrite,
      changed,
      max,
    };
  }, hashes);
  expect(result.count).toBe(27000);
  expect(result.nonBackground).toBeGreaterThan(100);
  expect(result.pin && result.identity && result.transparent).toBe(true);
  expect(result.opacity).toBeCloseTo(0.91, 6);
  expect(result.depthWrite).toBe(false);
  for (const e of Object.values(result.errors))
    expect(e).toBeLessThanOrEqual(1e-6);
  expect(result.changed).toBe(0);
});
