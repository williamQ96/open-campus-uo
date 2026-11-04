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
test("PLC tower overlay is source-pinned and clears screened navigation graph", () => {
  const data = read("../public/scene/plc-tower-detail.json"),
    d = JSON.parse(data),
    c = JSON.parse(read("../public/scene/presentation.json"));
  assert.equal(
    c.exterior_details.find((e) => e.url === "plc-tower-detail.json").sha256,
    createHash("sha256").update(data).digest("hex"),
  );
  assert.equal(d.base_asset_sha256, c.asset_sha256);
  assert.equal(d.building_id, "roof-8f611273");
  assert.equal(d.replace_building, false);
  assert.ok(
    createExteriorDetail(d, c.asset_sha256, new Set([d.building_id])).children
      .length,
  );
  const g = JSON.parse(read("../public/scene/navigation.json")),
    b = [
      [-614, -139, -612.3, -103],
      [-602.7, -139, -601, -103],
      [-613, -101, -602, -99],
      [-613, -145, -602, -143],
    ];
  assert.equal(
    g.edges.filter(([a, z]) =>
      segmentHitsBoxes(g.nodes_enu_m[a], g.nodes_enu_m[z], b, 0.5),
    ).length,
    0,
  );
});
test("nearby Anstett and Chapman planting batches retain positions, colors and building identity", () => {
  const a = JSON.parse(read("../public/scene/anstett-south-detail.json")),
    b = JSON.parse(read("../public/scene/chapman-west-detail.json")),
    root = new THREE.Group();
  let first = createExteriorDetail(
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
    positions = [
      ...x.geometry.attributes.position.array,
      ...y.geometry.attributes.position.array,
    ],
    colors = [
      ...x.geometry.attributes.color.array,
      ...y.geometry.attributes.color.array,
    ];
  const aBuilding = first.children.find(
      (x) => x.userData.asset_kind === "building",
    ),
    bBuilding = second.children.find(
      (x) => x.userData.asset_kind === "building",
    );
  mergeLocalDetailKind(first, second, "vegetation");
  assert.deepEqual([...x.geometry.attributes.position.array], positions);
  assert.deepEqual([...x.geometry.attributes.color.array], colors);
  assert.equal(find(second), undefined);
  assert.equal(aBuilding.userData.asset_id, a.building_id);
  assert.equal(bBuilding.userData.asset_id, b.building_id);
});
