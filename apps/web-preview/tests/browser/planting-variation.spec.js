import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
test("40 source-pinned shrubs remain within their original bounds and match standalone export", async ({
  page,
}) => {
  const raw = readFileSync(
      new URL("../../public/scene/pilot-shrub-variation.json", import.meta.url),
    ),
    spec = JSON.parse(raw),
    config = JSON.parse(
      readFileSync(
        new URL("../../public/scene/presentation.json", import.meta.url),
      ),
    ),
    sha = (b) => createHash("sha256").update(b).digest("hex");
  expect(sha(raw)).toBe(config.planting_variation_sha256);
  const bytes = readFileSync(
    new URL(
      "../../../../assets/vegetation-refinement/pilot-shrubs-varied-2026-11-04.glb",
      import.meta.url,
    ),
  );
  await page.route("**/__local/shrubs.glb", (r) =>
    r.fulfill({ body: bytes, contentType: "model/gltf-binary" }),
  );
  await page.goto("/");
  const result = await page.evaluate(async (spec) => {
    const T = await import("/node_modules/three/build/three.module.js"),
      { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js"),
      { varyPlanting } = await import("/src/planting-variation.js");
    const gltf = await new GLTFLoader().loadAsync("/scene/campus-expanded.glb"),
      plant = gltf.scene.getObjectByName("planting"),
      canopy = gltf.scene.getObjectByName("vegetation_2"),
      old = plant.geometry,
      shared = plant.material;
    const bad = structuredClone(spec);
    bad.groups[22].max[1] += 1;
    let rejected = false;
    try {
      varyPlanting(gltf.scene, bad, spec.base_asset_sha256);
    } catch {
      rejected =
        plant.geometry === old &&
        plant.material === shared &&
        !old.attributes.color;
    }
    const count = varyPlanting(gltf.scene, spec, spec.base_asset_sha256),
      g = plant.geometry,
      pos = g.attributes.position,
      normal = g.attributes.normal,
      color = g.attributes.color;
    let bounded = true,
      base = true,
      changed = false,
      normalOk = true;
    for (let i = 0; i < 40; i++) {
      let minY = Infinity;
      const r = spec.groups[i];
      for (let j = 0; j < 216; j++) {
        let k = i * 216 + j,
          xyz = [pos.getX(k), pos.getY(k), pos.getZ(k)];
        for (let a = 0; a < 3; a++)
          if (xyz[a] < r.min[a] - 0.001 || xyz[a] > r.max[a] + 0.001)
            bounded = false;
        minY = Math.min(minY, xyz[1]);
        if (Math.abs(xyz[0] - old.attributes.position.getX(k)) > 0.001)
          changed = true;
        let len = Math.hypot(normal.getX(k), normal.getY(k), normal.getZ(k));
        if (!Number.isFinite(len) || len < 0.99 || len > 1.01) normalOk = false;
      }
      if (Math.abs(minY - r.min[1]) > 0.001) base = false;
    }
    const loaded = await new GLTFLoader().loadAsync("/__local/shrubs.glb"),
      meshes = [];
    loaded.scene.updateMatrixWorld(true);
    loaded.scene.traverse((o) => {
      if (o.isMesh) meshes.push(o);
    });
    if (meshes.length !== 1) throw Error("Expected one mesh");
    const copy = meshes[0],
      errors = {};
    for (const key of ["position", "normal", "color"]) {
      const a = g.attributes[key],
        b = copy.geometry.attributes[key];
      if (a.count !== b.count) throw Error("attribute count");
      let max = 0;
      for (let i = 0; i < a.array.length; i++)
        max = Math.max(max, Math.abs(a.array[i] - b.array[i]));
      errors[key] = max;
    }
    const sameIndex =
      g.index.count === copy.geometry.index.count &&
      g.index.array.every((v, i) => v === copy.geometry.index.array[i]);
    return {
      rejected,
      count,
      bounded,
      base,
      changed,
      normalOk,
      sharedIntact: canopy.material === shared && !shared.vertexColors,
      cloned: plant.material !== shared && plant.material.vertexColors,
      colors: color.count,
      sameIndex,
      identity: copy.matrixWorld.equals(new T.Matrix4()),
      baseHash: copy.userData.source_glb_sha256 === spec.base_asset_sha256,
      errors,
    };
  }, spec);
  for (const key of [
    "rejected",
    "bounded",
    "base",
    "changed",
    "normalOk",
    "sharedIntact",
    "cloned",
    "sameIndex",
    "identity",
    "baseHash",
  ])
    expect(result[key], key).toBe(true);
  expect(result.count).toBe(40);
  expect(result.colors).toBe(8640);
  for (const e of Object.values(result.errors))
    expect(e).toBeLessThanOrEqual(1e-6);
});
