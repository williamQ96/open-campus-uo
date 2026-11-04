import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
test("unplaced bike rack export matches source mesh and material", async ({
  page,
}) => {
  const source = readFileSync(
      new URL("../../src/bike-rack-geometry.js", import.meta.url),
    ),
    hash = createHash("sha256").update(source).digest("hex"),
    bytes = readFileSync(
      new URL(
        "../../../../assets/props/bike-rack-candidate-2026-11-04.glb",
        import.meta.url,
      ),
    );
  await page.route("**/__local/bike-rack.glb", (r) =>
    r.fulfill({ body: bytes, contentType: "model/gltf-binary" }),
  );
  await page.goto("/");
  const result = await page.evaluate(async (hash) => {
    const T = await import("/node_modules/three/build/three.module.js"),
      { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js"),
      { createBikeRackGeometry } = await import("/src/bike-rack-geometry.js"),
      g = await new GLTFLoader().loadAsync("/__local/bike-rack.glb"),
      items = [];
    g.scene.updateMatrixWorld(true);
    g.scene.traverse((o) => {
      if (o.isMesh) items.push(o);
    });
    if (items.length !== 1) throw Error("Expected one mesh");
    const mesh = items[0],
      a = createBikeRackGeometry(),
      b = mesh.geometry,
      errors = {};
    for (const key of ["position", "normal"]) {
      let max = 0;
      if (a.attributes[key].count !== b.attributes[key].count)
        throw Error("attribute count");
      for (let i = 0; i < a.attributes[key].array.length; i++)
        max = Math.max(
          max,
          Math.abs(a.attributes[key].array[i] - b.attributes[key].array[i]),
        );
      errors[key] = max;
    }
    return {
      errors,
      identicalIndex:
        a.index.count === b.index.count &&
        a.index.array.every((v, i) => v === b.index.array[i]),
      identity: mesh.matrixWorld.equals(new T.Matrix4()),
      hash: mesh.userData.source_sha256 === hash,
      scope: mesh.userData.scope,
      color: mesh.material.color.getHexString(),
      triangles: b.index.count / 3,
    };
  }, hash);
  expect(result.identicalIndex && result.identity && result.hash).toBe(true);
  expect(result.scope).toBe("generic-bike-rack-unplaced");
  expect(result.color).toBe("3f514b");
  expect(result.triangles).toBe(984);
  for (const e of Object.values(result.errors))
    expect(e).toBeLessThanOrEqual(1e-6);
});
