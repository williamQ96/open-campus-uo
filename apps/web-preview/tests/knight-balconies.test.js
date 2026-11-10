import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import {
  createExteriorDetail,
  installExteriorDetail,
} from "../src/exterior-detail.js";
const bytes = readFileSync(
  new URL(
    "../public/scene/knight-library-balcony-detail.json",
    import.meta.url,
  ),
);
const spec = JSON.parse(bytes);
const ids = new Set([spec.building_id]);
test("Knight parapets are pinned, additive and retain all three original balcony centers", () => {
  const presentation = JSON.parse(
    readFileSync(new URL("../public/scene/presentation.json", import.meta.url)),
  );
  assert.equal(
    presentation.exterior_details.find(
      (x) => x.url === "knight-library-balcony-detail.json",
    ).sha256,
    createHash("sha256").update(bytes).digest("hex"),
  );
  assert.equal(spec.replace_building, false);
  assert.deepEqual(
    spec.objects
      .filter((x) => x.role === "front-parapet")
      .map((x) => x.position[0]),
    [-571.2, -561.8, -552.4],
  );
  assert.equal(spec.objects.length, 21);
  const root = new THREE.Group();
  const original = new THREE.Mesh(
    new THREE.BoxGeometry(),
    new THREE.MeshBasicMaterial(),
  );
  original.userData = { asset_kind: "building", asset_id: spec.building_id };
  root.add(original);
  const detail = installExteriorDetail(root, spec, spec.base_asset_sha256, ids);
  assert.equal(original.parent, root);
  assert.equal(detail.children.length, 1);
  const bounds = new THREE.Box3().setFromObject(detail);
  assert.ok(bounds.min.y > 9 && bounds.max.y < 12);
  assert.ok(bounds.min.z > 189 && bounds.max.z < 193);
  for (const value of detail.children[0].geometry.attributes.position.array)
    assert.ok(Number.isFinite(value));
  assert.throws(
    () => createExteriorDetail(spec, "wrong", ids),
    /does not match/,
  );
  assert.throws(
    () => createExteriorDetail(spec, spec.base_asset_sha256, new Set()),
    /does not match/,
  );
});
