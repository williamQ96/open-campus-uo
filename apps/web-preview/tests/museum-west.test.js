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
test("museum frontage is pinned, supports pointed arches and clears screened navigation graph", () => {
  const data = read("../public/scene/museum-west-detail.json"),
    d = JSON.parse(data),
    c = JSON.parse(read("../public/scene/presentation.json"));
  assert.equal(
    c.exterior_details.find((e) => e.url === "museum-west-detail.json").sha256,
    createHash("sha256").update(data).digest("hex"),
  );
  assert.equal(d.base_asset_sha256, c.asset_sha256);
  assert.equal(d.building_id, "roof-16751515");
  assert.equal(d.replace_building, false);
  assert.ok(d.objects.some((o) => o.shape === "pointed-arch-x"));
  const root = createExteriorDetail(
    d,
    c.asset_sha256,
    new Set([d.building_id]),
  );
  root.traverse((o) => {
    if (o.isMesh)
      assert.ok(
        [...o.geometry.attributes.position.array].every(Number.isFinite),
      );
  });
  const g = JSON.parse(read("../public/scene/navigation.json")),
    boxes = [
      [-525, -159, -523, -114],
      [-519, -106, -512, -104],
      [-519, -163, -512, -161],
    ];
  assert.equal(
    g.edges.filter(([a, b]) =>
      segmentHitsBoxes(g.nodes_enu_m[a], g.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
});
test("Tykeson and Fenton vegetation combine without losing geometry or building identities", () => {
  const a = JSON.parse(read("../public/scene/tykeson-north-detail.json")),
    b = JSON.parse(read("../public/scene/fenton-south-detail.json")),
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
  let firstBuilding = first.children.find(
      (x) => x.userData.asset_kind === "building",
    ),
    secondBuilding = second.children.find(
      (x) => x.userData.asset_kind === "building",
    );
  mergeLocalDetailKind(first, second, "vegetation");
  assert.deepEqual([...x.geometry.attributes.position.array], pos);
  assert.deepEqual([...x.geometry.attributes.color.array], colors);
  assert.equal(find(second), undefined);
  assert.equal(firstBuilding.userData.asset_id, a.building_id);
  assert.equal(secondBuilding.userData.asset_id, b.building_id);
});
