import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";

test("standalone portal matches the two instanced meshes in the viewer", async ({
  page,
}) => {
  const source = readFileSync(
    new URL("../../src/entrances.js", import.meta.url),
  );
  const digest = createHash("sha256").update(source).digest("hex");
  const bytes = readFileSync(
    new URL(
      "../../../../assets/exterior-refinement/entrance-portal-l2-2026-11-26.glb",
      import.meta.url,
    ),
  );
  await page.route("**/__local/portal.glb", (route) =>
    route.fulfill({ body: bytes, contentType: "model/gltf-binary" }),
  );
  await page.goto("/");
  const result = await page.evaluate(async (digest) => {
    const { Matrix4 } =
      await import("/node_modules/three/build/three.module.js");
    const { createEntrancePortalParts } = await import("/src/entrances.js");
    const { GLTFLoader } =
      await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
    const gltf = await new GLTFLoader().loadAsync("/__local/portal.glb");
    gltf.scene.updateMatrixWorld(true);
    let pin = false;
    const meshes = [];
    gltf.scene.traverse((object) => {
      if (object.userData.source_sha256 === digest) pin = true;
      if (object.isMesh) meshes.push(object);
    });
    const errors = {};
    for (const [name, { geometry, roughness }] of Object.entries(
      createEntrancePortalParts(),
    )) {
      const mesh = meshes.find((object) => object.name === name);
      if (
        !mesh?.matrixWorld.equals(new Matrix4()) ||
        !mesh.material.vertexColors ||
        mesh.material.color.getHex() !== 0xffffff ||
        Math.abs(mesh.material.roughness - roughness) > 1e-6
      )
        throw Error("Missing mesh, transform or material");
      const { index } = geometry;
      if (
        index.count !== mesh.geometry.index.count ||
        !index.array.every((value, i) => value === mesh.geometry.index.array[i])
      )
        throw Error("Indices differ");
      for (const key of ["position", "normal", "color"]) {
        const a = geometry.attributes[key];
        const b = mesh.geometry.attributes[key];
        if (a.count !== b.count) throw Error("Attribute counts differ");
        errors[name + key] = Math.max(
          ...a.array.map((value, i) => Math.abs(value - b.array[i])),
        );
      }
    }
    return { pin, count: meshes.length, errors };
  }, digest);
  expect(result.pin).toBe(true);
  expect(result.count).toBe(2);
  for (const error of Object.values(result.errors))
    expect(error).toBeLessThanOrEqual(1e-6);
});

test("the center seam remains clickable and authored doors have no generic geometry", async ({
  page,
}) => {
  await page.route("**/portal-hit-test", (route) =>
    route.fulfill({ contentType: "text/html", body: '<div id="app"></div>' }),
  );
  await page.goto("/portal-hit-test");
  const result = await page.evaluate(async () => {
    const { Scene, Raycaster, Vector3 } =
      await import("/node_modules/three/build/three.module.js");
    const { createEntrances } = await import("/src/entrances.js");
    const scene = new Scene();
    const activations = [];
    const controller = createEntrances({
      scene,
      half: 20,
      buildings: [
        {
          id: "generic",
          footprint_enu_m: [
            [-2, 0],
            [2, 0],
            [2, 3],
            [-2, 3],
          ],
        },
        {
          id: "authored",
          footprint_enu_m: [
            [4, 0],
            [8, 0],
            [8, 3],
            [4, 3],
          ],
        },
      ],
      field: {
        nx: 2,
        ny: 2,
        spacing_m: 40,
        min_east_m: -20,
        min_north_m: -20,
        heights_m: [0, 0, 0, 0],
      },
      meshesById: new Map(),
      overrides: {
        generic: { position_enu_m: [0, 0], outward_degrees: 180 },
        authored: [
          {
            gate: "real-door",
            position_enu_m: [6, 0],
            outward_degrees: 180,
            snap_to_facade: false,
          },
        ],
      },
      onEnter: ({ id }) => activations.push(id),
    });
    scene.updateMatrixWorld(true);
    const hit = (x, y, wallDistance) =>
      controller.pick(
        new Raycaster(new Vector3(x, y, 2.5), new Vector3(0, 0, -1)),
        wallDistance,
      );
    return {
      hits: [hit(0, 1.5), hit(6, 1.5), hit(0, 1.5, 1), hit(0.94, 1.5)],
      activations,
      meshes: scene.children.map(({ count, visible }) => [count, visible]),
    };
  });
  expect(result.hits).toEqual([true, true, false, true]);
  expect(result.activations).toEqual(["generic", "authored", "generic"]);
  expect(result.meshes).toEqual([
    [1, true],
    [1, true],
    [2, false],
  ]);
});
