import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as THREE from "three";
import {
  createExteriorDetail,
  mergeLocalDetailKind,
} from "../src/exterior-detail.js";
const read = (p) => JSON.parse(readFileSync(new URL(p, import.meta.url)));
test("Anstett adjacent details merge by non-building kind without losing vertices or identity", () => {
  const a = read("../public/scene/anstett-south-detail.json"),
    b = read("../public/scene/anstett-lamps-detail.json");
  const ids = new Set([a.building_id]),
    root = new THREE.Group();
  const first = createExteriorDetail(a, a.base_asset_sha256, ids),
    second = createExteriorDetail(b, b.base_asset_sha256, ids);
  root.add(first, second);
  const building = first.children.find(
    (x) => x.userData.asset_kind === "building",
  );
  for (const kind of ["vegetation", "prop"]) {
    const mesh = (g) => g.children.find((x) => x.userData.asset_kind === kind);
    const m = mesh(first),
      n = mesh(second);
    const position = [
      ...m.geometry.attributes.position.array,
      ...n.geometry.attributes.position.array,
    ];
    const colors = [
      ...m.geometry.attributes.color.array,
      ...n.geometry.attributes.color.array,
    ];
    mergeLocalDetailKind(first, second, kind);
    assert.deepEqual([...m.geometry.attributes.position.array], position);
    assert.deepEqual([...m.geometry.attributes.color.array], colors);
    assert.equal(mesh(second), undefined);
  }
  assert.equal(building.userData.asset_id, a.building_id);
  assert.ok(first.children.includes(building));
  assert.throws(() => mergeLocalDetailKind(first, second, "building"));
});

test("University and Villard shrubs batch without changing vertices or building identities", () => {
  const a = read("../public/scene/university-hall-detail.json"),
    b = read("../public/scene/villard-east-detail.json"),
    ids = new Set([a.building_id, b.building_id]),
    root = new THREE.Group(),
    first = createExteriorDetail(a, a.base_asset_sha256, ids),
    second = createExteriorDetail(b, b.base_asset_sha256, ids);
  root.add(first, second);
  const mesh = (group) =>
      group.children.find((x) => x.userData.asset_kind === "vegetation"),
    firstVegetation = mesh(first),
    secondVegetation = mesh(second),
    buildings = [first, second].map((g) =>
      g.children.find((x) => x.userData.asset_kind === "building"),
    ),
    expected = Object.fromEntries(
      ["position", "normal", "color"].map((k) => [
        k,
        [
          ...firstVegetation.geometry.attributes[k].array,
          ...secondVegetation.geometry.attributes[k].array,
        ],
      ]),
    );
  assert.deepEqual(
    buildings.map((o) => o.userData.asset_id),
    ["roof-9017feee", "roof-399c648e"],
  );
  assert.equal(firstVegetation.geometry.index, null);
  assert.equal(secondVegetation.geometry.index, null);
  assert.equal(firstVegetation.castShadow, secondVegetation.castShadow);
  assert.equal(firstVegetation.receiveShadow, secondVegetation.receiveShadow);
  mergeLocalDetailKind(first, second, "vegetation");
  for (const k of Object.keys(expected))
    assert.deepEqual(
      [...firstVegetation.geometry.attributes[k].array],
      expected[k],
    );
  assert.equal(mesh(second), undefined);
  assert.equal(first.children.includes(buildings[0]), true);
  assert.equal(second.children.includes(buildings[1]), true);
  assert.equal(firstVegetation.userData.asset_id, undefined);
});
