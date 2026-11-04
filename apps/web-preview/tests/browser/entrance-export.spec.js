import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
test("standalone portal matches the shared runtime components", async ({
  page,
}) => {
  const source = readFileSync(
      new URL("../../src/entrances.js", import.meta.url),
    ),
    digest = createHash("sha256").update(source).digest("hex"),
    bytes = readFileSync(
      new URL(
        "../../../../assets/exterior-refinement/entrance-portal-optimized-2026-11-04.glb",
        import.meta.url,
      ),
    );
  await page.route("**/__local/portal.glb", (r) =>
    r.fulfill({ body: bytes, contentType: "model/gltf-binary" }),
  );
  await page.goto("/");
  const result = await page.evaluate(async (digest) => {
    const T = await import("/node_modules/three/build/three.module.js"),
      { createEntranceFrameGeometry, createEntranceDoorGeometry } =
        await import("/src/entrances.js"),
      { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js"),
      g = await new GLTFLoader().loadAsync("/__local/portal.glb");
    g.scene.updateMatrixWorld(true);
    let pin = false;
    const meshes = [];
    g.scene.traverse((o) => {
      if (o.userData.source_sha256 === digest) pin = true;
      if (o.isMesh) meshes.push(o);
    });
    const errors = {};
    for (const [name, geo, color] of [
      ["portal-trim", createEntranceFrameGeometry(), "ead5a0"],
      ["portal-door", createEntranceDoorGeometry(), "285d51"],
    ]) {
      const m = meshes.find((x) => x.name === name);
      if (
        !m ||
        !m.matrixWorld.equals(new T.Matrix4()) ||
        m.material.color.getHexString() !== color
      )
        throw Error("mesh, transform or material mismatch");
      for (const key of ["position", "normal"]) {
        const a = geo.attributes[key],
          b = m.geometry.attributes[key];
        if (a.count !== b.count) throw Error("attribute count mismatch");
        let error = 0;
        for (let i = 0; i < a.array.length; i++)
          error = Math.max(error, Math.abs(a.array[i] - b.array[i]));
        errors[name + key] = error;
      }
    }
    return { pin, count: meshes.length, errors };
  }, digest);
  expect(result.pin).toBe(true);
  expect(result.count).toBe(2);
  for (const e of Object.values(result.errors))
    expect(e).toBeLessThanOrEqual(1e-6);
});
