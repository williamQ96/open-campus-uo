import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
test("fern export matches bounded runtime geometry", async ({ page }) => {
  const oldSource = readFileSync(
    new URL(
      "../../../../assets/vegetation-refinement/fern-geometry-before-variation-2026-11-04.js",
      import.meta.url,
    ),
    "utf8",
  );
  const source = readFileSync(
      new URL("../../src/fern-geometry.js", import.meta.url),
    ),
    digest = createHash("sha256").update(source).digest("hex");
  const bytes = readFileSync(
    new URL(
      "../../../../assets/vegetation-refinement/fern-varied-2026-11-04.glb",
      import.meta.url,
    ),
  );
  await page.route("**/__local/fern.glb", (r) =>
    r.fulfill({ body: bytes, contentType: "model/gltf-binary" }),
  );
  await page.goto("/");
  const result = await page.evaluate(
    async ({ oldSource, digest }) => {
      const T = await import("/node_modules/three/build/three.module.js"),
        { createFernGeometry } = await import("/src/fern-geometry.js"),
        { GLTFLoader } =
          await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
      const script = oldSource.replace(
          'import * as THREE from "three";',
          `import * as THREE from "${location.origin}/node_modules/three/build/three.module.js";`,
        ),
        url = URL.createObjectURL(
          new Blob([script], { type: "text/javascript" }),
        );
      const old = (await import(url)).createFernGeometry();
      URL.revokeObjectURL(url);
      const current = createFernGeometry(),
        loaded = await new GLTFLoader().loadAsync("/__local/fern.glb"),
        meshes = [];
      loaded.scene.updateMatrixWorld(true);
      loaded.scene.traverse((o) => {
        if (o.isMesh) meshes.push(o);
      });
      if (meshes.length !== 1) throw Error("Expected one mesh");
      const mesh = meshes[0],
        errors = {};
      for (const key of ["position", "normal"]) {
        const a = current.attributes[key],
          b = mesh.geometry.attributes[key];
        if (a.count !== b.count) throw Error("count mismatch");
        let e = 0;
        for (let i = 0; i < a.array.length; i++)
          e = Math.max(e, Math.abs(a.array[i] - b.array[i]));
        errors[key] = e;
      }
      let changed = 0,
        maxRadius = 0;
      const a = current.attributes.position,
        b = old.attributes.position;
      for (let i = 0; i < a.count; i++) {
        if (
          a.getX(i) !== b.getX(i) ||
          a.getY(i) !== b.getY(i) ||
          a.getZ(i) !== b.getZ(i)
        )
          changed++;
        maxRadius = Math.max(maxRadius, Math.hypot(a.getX(i), a.getZ(i)));
      }
      return {
        errors,
        changed,
        maxRadius,
        count: a.count,
        digest: mesh.userData.source_sha256,
        identity: mesh.matrixWorld.equals(new T.Matrix4()),
        color: mesh.material.color.getHexString(),
      };
    },
    { oldSource, digest },
  );
  expect(result.count).toBe(2040);
  expect(result.changed).toBeGreaterThan(500);
  expect(result.maxRadius * 1.08).toBeLessThan(1.35);
  expect(result.digest).toBe(digest);
  expect(result.identity).toBe(true);
  expect(result.color).toBe("829e59");
  for (const e of Object.values(result.errors))
    expect(e).toBeLessThanOrEqual(1e-6);
});
