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
test("LLC exterior and wall patch remain source-pinned and avoid screened ENU graph", () => {
  const c = JSON.parse(read("../public/scene/presentation.json")),
    a = read("../public/scene/llc-north-detail.json"),
    b = read("../public/scene/llc-north-wall-color.json"),
    d = JSON.parse(a),
    patch = JSON.parse(b),
    sha = (x) => createHash("sha256").update(x).digest("hex");
  assert.equal(
    c.exterior_details.find((e) => e.url === "llc-north-detail.json").sha256,
    sha(a),
  );
  assert.equal(
    c.wall_color_patches.find((e) => e.url === "llc-north-wall-color.json")
      .sha256,
    sha(b),
  );
  assert.equal(d.base_asset_sha256, c.asset_sha256);
  assert.equal(patch.base_asset_sha256, c.asset_sha256);
  assert.equal(d.building_id, "roof-d2f88f9e");
  assert.equal(patch.building_id, d.building_id);
  assert.equal(d.replace_building, false);
  assert.equal(d.merge_source_vertex_count, 2686);
  assert.ok(
    createExteriorDetail(d, c.asset_sha256, new Set([d.building_id])).children
      .length,
  );
  const g = JSON.parse(read("../public/scene/navigation.json")),
    boxes = [
      [-105.2, -161, -103.2, -124],
      [-52.6, -138, -50.3, -115],
      [-54.1, -159, -51.8, -142],
    ];
  assert.equal(
    g.edges.filter(([x, y]) =>
      segmentHitsBoxes(g.nodes_enu_m[x], g.nodes_enu_m[y], boxes, 0.5),
    ).length,
    0,
  );
});
test("building merge validates before mutation and preserves source identity and geometry", () => {
  const root = new THREE.Group(),
    g = new THREE.BoxGeometry(4, 4, 4),
    colors = new Float32Array(g.attributes.position.count * 3).fill(0.5);
  g.deleteAttribute("uv");
  g.setAttribute("color", new THREE.BufferAttribute(colors, 3));
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
      merge_source_vertex_count: g.attributes.position.count,
      objects: [
        {
          kind: "building",
          material: "brick",
          shape: "box",
          position: [0, 0, 0],
          size: [1, 1, 1],
        },
      ],
    },
    detail = createExteriorDetail(d, "s", new Set(["x"]));
  root.add(detail);
  const before = g.toNonIndexed(),
    expectPos = [
      ...before.attributes.position.array,
      ...detail.children[0].geometry.attributes.position.array,
    ],
    expectColors = [
      ...before.attributes.color.array,
      ...detail.children[0].geometry.attributes.color.array,
    ];
  assert.throws(() =>
    mergeBuildingDetailIntoSource(root, detail, {
      ...d,
      merge_source_vertex_count: 1,
    }),
  );
  assert.equal(base.geometry, g);
  assert.equal(detail.parent, root);
  mergeBuildingDetailIntoSource(root, detail, d);
  assert.equal(base.material, mat);
  assert.equal(base.userData.asset_id, "x");
  assert.equal(detail.parent, null);
  assert.deepEqual([...base.geometry.attributes.position.array], expectPos);
  assert.deepEqual([...base.geometry.attributes.color.array], expectColors);
});
