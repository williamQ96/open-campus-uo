import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import {
  createExteriorDetail,
  mergeLocalDetailKind,
} from "../src/exterior-detail.js";
import { segmentHitsBoxes } from "../src/collision-supplement.js";
const read = (p) => readFileSync(new URL(p, import.meta.url));
test("Bean exterior and wall patch are source-pinned and avoid screened ENU graph", () => {
  const c = JSON.parse(read("../public/scene/presentation.json")),
    a = read("../public/scene/bean-exterior-detail.json"),
    b = read("../public/scene/bean-wall-color.json"),
    d = JSON.parse(a),
    patch = JSON.parse(b),
    sha = (x) => createHash("sha256").update(x).digest("hex");
  assert.equal(
    c.exterior_details.find((e) => e.url === "bean-exterior-detail.json")
      .sha256,
    sha(a),
  );
  assert.equal(
    c.wall_color_patches.find((e) => e.url === "bean-wall-color.json").sha256,
    sha(b),
  );
  assert.equal(d.base_asset_sha256, c.asset_sha256);
  assert.equal(patch.base_asset_sha256, c.asset_sha256);
  assert.equal(d.building_id, "roof-0de7fadb");
  assert.equal(patch.building_id, d.building_id);
  assert.equal(d.replace_building, false);
  assert.ok(
    createExteriorDetail(d, c.asset_sha256, new Set([d.building_id])).children
      .length,
  );
  const g = JSON.parse(read("../public/scene/navigation.json")),
    boxes = [
      [330, -204, 332, -147],
      [275, -144.5, 327, -142.5],
      [275, -208, 327, -206],
    ];
  assert.equal(
    g.edges.filter(([x, y]) =>
      segmentHitsBoxes(g.nodes_enu_m[x], g.nodes_enu_m[y], boxes, 0.5),
    ).length,
    0,
  );
});
test("nearby Condon and Peterson planting batches preserve positions, colors and identities", () => {
  const a = JSON.parse(read("../public/scene/condon-east-detail.json")),
    b = JSON.parse(read("../public/scene/peterson-south-detail.json")),
    root = new THREE.Group(),
    first = createExteriorDetail(
      a,
      a.base_asset_sha256,
      new Set([a.building_id]),
    ),
    second = createExteriorDetail(
      b,
      b.base_asset_sha256,
      new Set([b.building_id]),
    );
  root.add(first, second);
  const find = (g) =>
      g.children.find((x) => x.userData.asset_kind === "vegetation"),
    x = find(first),
    y = find(second),
    pos = [
      ...x.geometry.attributes.position.array,
      ...y.geometry.attributes.position.array,
    ],
    colors = [
      ...x.geometry.attributes.color.array,
      ...y.geometry.attributes.color.array,
    ];
  let ba = first.children.find((x) => x.userData.asset_kind === "building"),
    bb = second.children.find((x) => x.userData.asset_kind === "building");
  mergeLocalDetailKind(first, second, "vegetation");
  assert.deepEqual([...x.geometry.attributes.position.array], pos);
  assert.deepEqual([...x.geometry.attributes.color.array], colors);
  assert.equal(find(second), undefined);
  assert.equal(ba.userData.asset_id, a.building_id);
  assert.equal(bb.userData.asset_id, b.building_id);
});
