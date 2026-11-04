import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import {
  createExteriorDetail,
  mergeBuildingDetailIntoSource,
} from "../src/exterior-detail.js";
import { segmentHitsBoxes } from "../src/collision-supplement.js";
const read = (p) => readFileSync(new URL(p, import.meta.url));
test("LLC South detail and color patch are pinned and avoid the screened ENU graph", () => {
  const c = JSON.parse(read("../public/scene/presentation.json")),
    a = read("../public/scene/llc-south-detail.json"),
    b = read("../public/scene/llc-south-wall-color.json"),
    d = JSON.parse(a),
    patch = JSON.parse(b),
    sha = (x) => createHash("sha256").update(x).digest("hex");
  assert.equal(
    c.exterior_details.find((e) => e.url === "llc-south-detail.json").sha256,
    sha(a),
  );
  assert.equal(
    c.wall_color_patches.find((e) => e.url === "llc-south-wall-color.json")
      .sha256,
    sha(b),
  );
  assert.equal(d.base_asset_sha256, c.asset_sha256);
  assert.equal(patch.base_asset_sha256, c.asset_sha256);
  assert.equal(d.building_id, "roof-453966d5");
  assert.equal(patch.building_id, d.building_id);
  assert.equal(d.replace_building, false);
  assert.equal(d.merge_source_vertex_count, 1664);
  assert.equal(d.trim_source_expected_triangles, 162);
  assert.ok(
    createExteriorDetail(d, c.asset_sha256, new Set([d.building_id])).children
      .length,
  );
  const g = JSON.parse(read("../public/scene/navigation.json")),
    boxes = [
      [-104.2, -224, -102.2, -204],
      [-46.1, -224, -44, -204],
      [-100, -202.1, -48, -200],
      [-88, -217.1, -61, -215],
    ];
  assert.equal(
    g.edges.filter(([x, y]) =>
      segmentHitsBoxes(g.nodes_enu_m[x], g.nodes_enu_m[y], boxes, 0.5),
    ).length,
    0,
  );
});
test("roof trim rejects mismatch before mutation and retains lower triangles and identity", () => {
  const root = new THREE.Group(),
    g = new THREE.BufferGeometry();
  g.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(
      [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 2, 0, 1, 2, 0, 0, 2, 1],
      3,
    ),
  );
  g.setAttribute(
    "normal",
    new THREE.Float32BufferAttribute(
      [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
      3,
    ),
  );
  g.setAttribute(
    "color",
    new THREE.Float32BufferAttribute(Array(18).fill(0.5), 3),
  );
  const mat = new THREE.MeshStandardMaterial({
      vertexColors: true,
      color: 0xffffff,
      side: THREE.DoubleSide,
      roughness: 0.9,
      metalness: 0,
    }),
    base = new THREE.Mesh(g, mat);
  base.name = "x";
  base.userData = { asset_kind: "building", asset_id: "x" };
  root.add(base);
  const d = {
      version: 1,
      base_asset_sha256: "s",
      building_id: "x",
      replace_building: false,
      merge_source_vertex_count: 6,
      trim_source_min_y: 1,
      trim_source_expected_triangles: 1,
      objects: [
        {
          kind: "building",
          material: "brick",
          shape: "box",
          position: [0, 1, 0],
          size: [1, 1, 1],
        },
      ],
    },
    detail = createExteriorDetail(d, "s", new Set(["x"]));
  root.add(detail);
  assert.throws(() =>
    mergeBuildingDetailIntoSource(root, detail, {
      ...d,
      trim_source_expected_triangles: 2,
    }),
  );
  assert.equal(base.geometry, g);
  assert.equal(detail.parent, root);
  mergeBuildingDetailIntoSource(root, detail, d);
  assert.equal(base.material, mat);
  assert.equal(base.userData.asset_id, "x");
  assert.equal(detail.parent, null);
  assert.deepEqual(
    [...base.geometry.attributes.position.array].slice(0, 9),
    [0, 0, 0, 1, 0, 0, 0, 0, 1],
  );
  assert.equal(g.attributes.position.count, 6);
});
