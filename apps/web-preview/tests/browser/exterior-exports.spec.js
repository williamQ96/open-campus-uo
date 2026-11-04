import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
const fixtures = [
  [
    "arena-north-detail",
    "arena-north-detail-v3-2026-11-04.glb",
    "context-b0074",
  ],
  [
    "unthank-west-detail",
    "unthank-west-detail-2026-11-04.glb",
    "context-oc-unthank",
  ],
  [
    "hedco-exterior-detail",
    "hedco-exterior-detail-2026-11-04.glb",
    "context-b0010",
  ],
  [
    "knight-campus1-south-detail",
    "knight-campus1-south-detail-2026-11-04.glb",
    "context-oc-knight-1",
  ],
  [
    "jaqua-exterior-detail",
    "jaqua-exterior-detail-2026-11-04.glb",
    "context-b0067",
  ],
  [
    "knight-campus2-east-detail",
    "knight-campus2-east-detail-2026-11-04.glb",
    "context-oc-knight-2",
  ],
  [
    "lillis-south-detail",
    "lillis-south-detail-2026-11-04.glb",
    "roof-86754ad7",
  ],
];
for (const [name, file, id] of fixtures) {
  test(`${name} on-disk export matches runtime source`, async ({ page }) => {
    const bytes = readFileSync(
      new URL(
        `../../../../assets/exterior-refinement/${file}`,
        import.meta.url,
      ),
    );
    await page.route("**/__local/overlay.glb", (r) =>
      r.fulfill({ status: 200, contentType: "model/gltf-binary", body: bytes }),
    );
    await page.goto("/");
    const result = await page.evaluate(
      async ({ name }) => {
        const T = await import("/node_modules/three/build/three.module.js");
        const { GLTFLoader } =
          await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
        const { createExteriorDetail } =
          await import("/src/exterior-detail.js");
        const config = await (await fetch("/scene/presentation.json")).json(),
          spec = await (await fetch(`/scene/${name}.json`)).json();
        const a = createExteriorDetail(
          spec,
          spec.base_asset_sha256,
          new Set([spec.building_id]),
        ).children[0];
        const g = await new GLTFLoader().loadAsync("/__local/overlay.glb");
        g.scene.updateMatrixWorld(true);
        const meshes = [];
        g.scene.traverse((o) => {
          if (o.isMesh) meshes.push(o);
        });
        if (meshes.length !== 1) throw Error("Expected one mesh");
        const b = meshes[0],
          errors = {};
        for (const key of ["position", "normal", "color"]) {
          const x = a.geometry.attributes[key],
            y = b.geometry.attributes[key];
          if (x.count !== y.count) throw Error(`${key} count mismatch`);
          let max = 0;
          for (let i = 0; i < x.array.length; i++)
            max = Math.max(max, Math.abs(x.array[i] - y.array[i]));
          errors[key] = max;
        }
        return {
          errors,
          id: b.userData.asset_id,
          sourceHash: b.userData.source_overlay_sha256,
          pin: config.exterior_details.find((x) => x.url === `${name}.json`)
            .sha256,
          identity: b.matrixWorld.equals(new T.Matrix4()),
        };
      },
      { name },
    );
    expect(result.id).toBe(id);
    expect(result.sourceHash).toBe(result.pin);
    expect(result.identity).toBe(true);
    for (const error of Object.values(result.errors))
      expect(error).toBeLessThanOrEqual(1e-6);
  });
}
