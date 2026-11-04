import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
test("van export is updated and five other prop meshes remain unchanged", async ({
  page,
}) => {
  const bytes = readFileSync(
    new URL(
      "../../../../assets/props/campus-props-before-van-profile-2026-11-04.glb",
      import.meta.url,
    ),
  );
  await page.route("**/__local/old-props.glb", (r) =>
    r.fulfill({ body: bytes, contentType: "model/gltf-binary" }),
  );
  await page.goto("/");
  const result = await page.evaluate(async () => {
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const loader = new GLTFLoader();
    async function meshes(url) {
      const scene = (await loader.loadAsync(url)).scene,
        out = {};
      scene.traverse((o) => {
        if (o.isMesh) out[o.userData.kind] = o;
      });
      return out;
    }
    const old = await meshes("/__local/old-props.glb"),
      now = await meshes("/props/campus-props.glb"),
      out = {};
    for (const k of Object.keys(old)) {
      const a = old[k],
        b = now[k],
        details = {};
      for (const attr of ["position", "normal", "color"]) {
        const x = a.geometry.attributes[attr].array,
          y = b.geometry.attributes[attr].array;
        details[attr] =
          x.length === y.length && Array.from(x).every((v, i) => v === y[i]);
      }
      out[k] = {
        attributes: details,
        transform:
          a.position.equals(b.position) &&
          a.rotation.equals(b.rotation) &&
          a.scale.equals(b.scale),
        oldCount: a.geometry.attributes.position.count,
        newCount: b.geometry.attributes.position.count,
      };
    }
    return out;
  });
  expect(Object.keys(result).sort()).toEqual([
    "bicycle",
    "car",
    "pickup",
    "scooter",
    "suv",
    "van",
  ]);
  for (const [kind, value] of Object.entries(result)) {
    expect(value.transform).toBe(true);
    if (kind === "van") {
      expect(value.oldCount).toBe(2184);
      expect(value.newCount).toBe(2196);
      expect(value.attributes.position).toBe(false);
    } else
      expect(value.attributes).toEqual({
        position: true,
        normal: true,
        color: true,
      });
  }
});
