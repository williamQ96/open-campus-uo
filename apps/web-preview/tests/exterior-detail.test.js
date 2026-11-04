import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  createExteriorDetail,
  installExteriorDetail,
} from "../src/exterior-detail.js";
import * as THREE from "three";
const spec = JSON.parse(
  readFileSync(
    new URL("../public/scene/johnson-rear-detail.json", import.meta.url),
  ),
);
test("exterior detail is source-pinned, grouped and preserves the building identity", () => {
  const ids = new Set([spec.building_id]);
  const group = createExteriorDetail(spec, spec.base_asset_sha256, ids);
  assert.ok(
    group.children.some((mesh) => mesh.userData.asset_id === spec.building_id),
  );
  assert.ok(
    group.children.some((mesh) => mesh.userData.asset_kind === "vegetation"),
  );
  assert.ok(group.children.length < spec.objects.length);
  for (const child of group.children)
    for (const value of child.geometry.attributes.position.array)
      assert.ok(Number.isFinite(value));
  assert.throws(
    () => createExteriorDetail(spec, "other", ids),
    /does not match/,
  );
  assert.throws(
    () => createExteriorDetail(spec, spec.base_asset_sha256, new Set()),
    /does not match/,
  );
  const bad = structuredClone(spec);
  bad.objects[0].size[0] = -1;
  assert.throws(
    () => createExteriorDetail(bad, spec.base_asset_sha256, ids),
    /Invalid/,
  );
});

test("replacement removes only one matching source mesh and rejects ambiguous or mismatched sources", () => {
  const root = new THREE.Group(),
    original = new THREE.Mesh(
      new THREE.BoxGeometry(),
      new THREE.MeshBasicMaterial(),
    );
  original.userData = { asset_kind: "building", asset_id: spec.building_id };
  const other = new THREE.Mesh(
    new THREE.BoxGeometry(),
    new THREE.MeshBasicMaterial(),
  );
  other.userData = { asset_kind: "building", asset_id: "other" };
  root.add(original, other);
  const replacement = { ...spec, replace_building: true };
  assert.throws(
    () =>
      installExteriorDetail(
        root,
        replacement,
        "wrong",
        new Set([spec.building_id]),
      ),
    /does not match/,
  );
  assert.equal(original.parent, root);
  const detail = installExteriorDetail(
    root,
    replacement,
    spec.base_asset_sha256,
    new Set([spec.building_id]),
  );
  assert.equal(original.parent, null);
  assert.equal(other.parent, root);
  assert.equal(detail.parent, root);
  assert.throws(
    () =>
      installExteriorDetail(
        new THREE.Group(),
        replacement,
        spec.base_asset_sha256,
        new Set([spec.building_id]),
      ),
    /ambiguous or absent/,
  );
});

test("east elevation gable and detail geometry are finite and retain the Hall identity", () => {
  const hall = JSON.parse(
    readFileSync(
      new URL("../public/scene/gerlinger-east-detail.json", import.meta.url),
    ),
  );
  const detail = createExteriorDetail(
    hall,
    hall.base_asset_sha256,
    new Set([hall.building_id]),
  );
  assert.ok(hall.objects.some((entry) => entry.shape === "gable"));
  for (const child of detail.children)
    for (const value of child.geometry.attributes.position.array)
      assert.ok(Number.isFinite(value));
  assert.ok(
    detail.children.some(
      (child) => child.userData.asset_id === "roof-9ac93ab7",
    ),
  );
});

test("exterior labels reject unsafe characters before rendering", () => {
  const label = {
    ...spec,
    objects: [
      {
        kind: "building",
        material: "cream",
        shape: "label",
        position: [0, 0, 0],
        size: [1, 1, 0.02],
        text: "<unsafe>",
      },
    ],
  };
  assert.throws(
    () =>
      createExteriorDetail(
        label,
        label.base_asset_sha256,
        new Set([label.building_id]),
      ),
    /Invalid exterior label/,
  );
});

test("replacement supports a semantic building group and preserves its neighbors", () => {
  const root = new THREE.Group(),
    original = new THREE.Group(),
    child = new THREE.Mesh(
      new THREE.BoxGeometry(),
      new THREE.MeshBasicMaterial(),
    );
  original.userData = { asset_kind: "building", asset_id: spec.building_id };
  original.add(child);
  const neighbor = new THREE.Group();
  root.add(original, neighbor);
  installExteriorDetail(
    root,
    { ...spec, replace_building: true },
    spec.base_asset_sha256,
    new Set([spec.building_id]),
  );
  assert.equal(original.parent, null);
  assert.equal(neighbor.parent, root);
});

test("Friendly replacement constructs finite roof, disks and semantic identity", () => {
  const item = JSON.parse(
    readFileSync(
      new URL("../public/scene/friendly-west-detail.json", import.meta.url),
    ),
  );
  const result = createExteriorDetail(
    item,
    item.base_asset_sha256,
    new Set([item.building_id]),
  );
  assert.ok(
    item.objects.some((o) => o.shape === "gambrel") &&
      item.objects.some((o) => o.shape === "disk"),
  );
  assert.ok(
    result.children.some((o) => o.userData.asset_id === item.building_id),
  );
  for (const child of result.children)
    for (const value of child.geometry.attributes.position.array)
      assert.ok(Number.isFinite(value));
});

test("hip roof has finite tapered geometry and retains building identity", () => {
  const hip = {
    ...spec,
    objects: [
      {
        kind: "building",
        material: "roof",
        shape: "hip",
        position: [0, 0, 0],
        size: [8, 4, 6],
      },
    ],
  };
  const result = createExteriorDetail(
    hip,
    hip.base_asset_sha256,
    new Set([hip.building_id]),
  );
  const mesh = result.children[0];
  mesh.geometry.computeBoundingBox();
  assert.ok(
    Math.abs(
      mesh.geometry.boundingBox.max.x - mesh.geometry.boundingBox.min.x - 8,
    ) < 1e-5,
  );
  assert.ok(
    [...mesh.geometry.attributes.position.array].every(Number.isFinite),
  );
  assert.equal(mesh.userData.asset_id, hip.building_id);
});

test("arched windows generate finite geometry on both facade axes", () => {
  for (const shape of ["arch", "arch-x"]) {
    const detail = {
      ...spec,
      objects: [
        {
          kind: "building",
          material: "glass",
          shape,
          position: [0, 0, 0],
          size: [2, 4, 0.2],
        },
      ],
    };
    const result = createExteriorDetail(
      detail,
      detail.base_asset_sha256,
      new Set([detail.building_id]),
    );
    const geometry = result.children[0].geometry;
    geometry.computeBoundingBox();
    assert.ok([...geometry.attributes.position.array].every(Number.isFinite));
    assert.ok(
      Math.abs(geometry.boundingBox.max.y - geometry.boundingBox.min.y - 4) <
        1e-5,
    );
  }
});

test("exterior props retain their own semantic kind", () => {
  const prop = {
    ...spec,
    objects: [
      {
        kind: "prop",
        material: "wood",
        shape: "box",
        position: [0, 0, 0],
        size: [2, 1, 0.4],
      },
    ],
  };
  const detail = createExteriorDetail(
    prop,
    prop.base_asset_sha256,
    new Set([prop.building_id]),
  );
  assert.equal(detail.children[0].userData.asset_kind, "prop");
  assert.equal(detail.children[0].userData.asset_id, undefined);
});

test("landscape detail batches soil and foliage without losing their colors", () => {
  const objects = ["soil", "shrub-light", "shrub-deep"].map((material, i) => ({
    kind: "vegetation",
    material,
    shape: "box",
    position: [i * 2, 0, 0],
    size: [1, 1, 1],
  }));
  const detail = createExteriorDetail(
    { ...spec, objects },
    spec.base_asset_sha256,
    new Set([spec.building_id]),
  );
  assert.equal(detail.children.length, 1);
  assert.equal(detail.children[0].userData.asset_kind, "vegetation");
  const colors = detail.children[0].geometry.attributes.color.array;
  assert.ok(
    new Set(
      Array.from(
        { length: colors.length / 3 },
        (_, i) => `${colors[i * 3]},${colors[i * 3 + 1]},${colors[i * 3 + 2]}`,
      ),
    ).size >= 3,
  );
});

test("gambrel roof preserves expected span and height", () => {
  const roof = {
    ...spec,
    objects: [
      {
        kind: "building",
        material: "roof",
        shape: "gambrel",
        position: [0, 0, 0],
        size: [20, 3, 8],
      },
    ],
  };
  const detail = createExteriorDetail(
    roof,
    roof.base_asset_sha256,
    new Set([roof.building_id]),
  );
  const g = detail.children[0].geometry;
  g.computeBoundingBox();
  assert.ok(Math.abs(g.boundingBox.max.x - g.boundingBox.min.x - 20) < 1e-5);
  assert.ok(Math.abs(g.boundingBox.max.y - g.boundingBox.min.y - 3) < 1e-5);
  assert.ok(Math.abs(g.boundingBox.max.z - g.boundingBox.min.z - 8) < 1e-5);
  assert.ok([...g.attributes.position.array].every(Number.isFinite));
});
