import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import { applyWallColorPatch } from "../src/wall-color-patch.js";
import { createExteriorDetail } from "../src/exterior-detail.js";
import { segmentHitsBoxes } from "../src/collision-supplement.js";
const read = (p) => readFileSync(new URL(p, import.meta.url));
test("Carson layer and color patch remain pinned and avoid the route graph", () => {
  const config = JSON.parse(read("../public/scene/presentation.json")),
    data = read("../public/scene/carson-exterior-detail.json"),
    bytes = read("../public/scene/carson-wall-color.json"),
    detail = JSON.parse(data),
    patch = JSON.parse(bytes);
  const sha = (b) => createHash("sha256").update(b).digest("hex");
  assert.equal(
    config.exterior_details.find((e) => e.url === "carson-exterior-detail.json")
      .sha256,
    sha(data),
  );
  assert.equal(
    config.wall_color_patches.find((e) => e.url === "carson-wall-color.json")
      .sha256,
    sha(bytes),
  );
  assert.equal(detail.base_asset_sha256, config.asset_sha256);
  assert.equal(patch.base_asset_sha256, config.asset_sha256);
  assert.equal(detail.building_id, patch.building_id);
  assert.equal(detail.replace_building, false);
  assert.ok(
    createExteriorDetail(
      detail,
      config.asset_sha256,
      new Set([detail.building_id]),
    ).children.length,
  );
  const g = JSON.parse(read("../public/scene/navigation.json")),
    boxes = [
      [-102, -40, -100.5, -19],
      [-50.5, -53, -49, -32],
      [-78, -74, -75.5, -54],
      [-63.5, -74, -62, -67],
      [-83, -13.5, -70, -12],
      [-72, -79, -66, -77.5],
    ];
  assert.equal(
    g.edges.filter(([a, b]) =>
      segmentHitsBoxes(g.nodes_enu_m[a], g.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
});
test("Carson east transoms join the upper grouped casements without covering the panes", () => {
  const detail = JSON.parse(
    read("../public/scene/carson-exterior-detail.json"),
  );
  const group = createExteriorDetail(
    detail,
    detail.base_asset_sha256,
    new Set([detail.building_id]),
  );
  assert.equal(group.children.length, 1);
  group.updateMatrixWorld(true);

  const eastGlass = detail.objects.filter(
    ({ material, position }) =>
      material === "glass" && Math.abs(position[0] + 49.37) < 1e-6,
  );
  assert.equal(eastGlass.length, 20);

  const paneFace = -49.345;
  const transomFace = -49.308;
  const firstEastIntersection = (y, z) => {
    const ray = new THREE.Raycaster(
      new THREE.Vector3(-47, y, z),
      new THREE.Vector3(-1, 0, 0),
    );
    return ray.intersectObject(group, true)[0]?.point.x;
  };
  const assertFace = (y, z, expected) =>
    assert.ok(Math.abs(firstEastIntersection(y, z) - expected) < 1e-5);

  for (const {
    position: [, y, z],
  } of eastGlass) {
    const paneCenter = z + 0.25;
    assertFace(y - 0.2, paneCenter, y === 2.5 ? paneFace : transomFace);
    assertFace(y + 0.25, paneCenter, paneFace);
    assertFace(y - 0.45, paneCenter, paneFace);
    assertFace(y - 0.2, z, -49.305);
  }
});

test("wall recolor is atomic, matches vertical source colors and preserves other vertices", () => {
  const root = new THREE.Group(),
    geo = new THREE.BufferGeometry();
  geo.setAttribute(
    "position",
    new THREE.Float32BufferAttribute([0, 0, 0, 1, 0, 0, 0, 1, 0], 3),
  );
  geo.setAttribute(
    "normal",
    new THREE.Float32BufferAttribute([1, 0, 0, 0, 1, 0, 1, 0, 0], 3),
  );
  geo.setAttribute(
    "color",
    new THREE.Float32BufferAttribute(
      [
        168 / 255,
        154 / 255,
        124 / 255,
        168 / 255,
        154 / 255,
        124 / 255,
        0.2,
        0.3,
        0.4,
      ],
      3,
    ),
  );
  const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial());
  m.userData = { asset_kind: "building", asset_id: "x" };
  root.add(m);
  const p = {
      version: 1,
      base_asset_sha256: "s",
      building_id: "x",
      source_rgb8: [168, 154, 124],
      target_srgb: "#b96f55",
      normal_y_abs_max: 0.4,
      expected_vertices: 1,
    },
    before = [...geo.attributes.color.array];
  assert.throws(() =>
    applyWallColorPatch(root, { ...p, expected_vertices: 2 }, "s"),
  );
  assert.equal(m.geometry, geo);
  assert.deepEqual([...geo.attributes.color.array], before);
  applyWallColorPatch(root, p, "s");
  assert.notEqual(m.geometry, geo);
  let after = [...m.geometry.attributes.color.array];
  assert.notDeepEqual(after.slice(0, 3), before.slice(0, 3));
  assert.deepEqual(after.slice(3), before.slice(3));
  assert.deepEqual([...geo.attributes.color.array], before);
  assert.throws(() => applyWallColorPatch(root, p, "wrong"));
});
