import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import * as THREE from "three";
import { createExteriorDetail } from "../src/exterior-detail.js";
import {
  trackedLayerNames,
  recipeSupports,
  mergePinnedBuildingOverlays,
} from "../src/building-overlay-batches.js";
const BASE = "29f22c38eb5737fba2c8b3ab9618e049443c052e169e175f19428e66174ae896";
function fixture() {
  const root = new THREE.Group(),
    entries = new Map();
  for (const name of trackedLayerNames) {
    const rawBytes = fs.readFileSync(
      new URL("../public/scene/" + name, import.meta.url),
    );
    const spec = JSON.parse(rawBytes),
      group = createExteriorDetail(spec, BASE, new Set([spec.building_id]));
    root.add(group);
    entries.set(name, { rawBytes, spec, group });
  }
  return { root, entries };
}
const mesh = (entry) =>
  entry.group.children.find((o) => o.name === "exterior-detail-building");
test("three pinned same-building overlay batches preserve every attribute, identity and vegetation", async () => {
  const { root, entries } = fixture();
  const expected = [];
  let disposals = 0;
  const foliage = [];
  for (let i = 0; i < trackedLayerNames.length; i += 2) {
    const a = mesh(entries.get(trackedLayerNames[i])),
      b = mesh(entries.get(trackedLayerNames[i + 1]));
    expected.push({
      a,
      b,
      material: a.material,
      attrs: Object.fromEntries(
        ["position", "normal", "color"].map((k) => [
          k,
          [
            ...a.geometry.attributes[k].array,
            ...b.geometry.attributes[k].array,
          ],
        ]),
      ),
    });
    a.geometry.addEventListener("dispose", () => disposals++);
    b.geometry.addEventListener("dispose", () => disposals++);
    b.material.addEventListener("dispose", () => disposals++);
  }
  root.traverse((o) => {
    if (o.userData.asset_kind === "vegetation")
      foliage.push([o, o.parent, o.geometry, o.material]);
  });
  assert.equal(await mergePinnedBuildingOverlays(root, entries, BASE), 3);
  assert.equal(disposals, 9);
  for (const { a, b, material, attrs } of expected) {
    assert.equal(a.material, material);
    assert.equal(a.userData.asset_kind, "building");
    assert.equal(b.parent, null);
    for (const k of Object.keys(attrs))
      assert.deepEqual([...a.geometry.attributes[k].array], attrs[k]);
  }
  for (const [o, parent, g, m] of foliage) {
    assert.equal(o.parent, parent);
    assert.equal(o.geometry, g);
    assert.equal(o.material, m);
  }
});
test("missing donor layer safely skips, while corrupted source fails atomically", async () => {
  const { root, entries } = fixture();
  entries.delete(trackedLayerNames[1]);
  assert.equal(await mergePinnedBuildingOverlays(root, entries, BASE), 2);
  const fresh = fixture(),
    a = mesh(fresh.entries.get(trackedLayerNames[0])),
    g = a.geometry;
  const last = fresh.entries.get(trackedLayerNames.at(-1));
  last.rawBytes = Buffer.concat([last.rawBytes, Buffer.from(" ")]);
  await assert.rejects(
    mergePinnedBuildingOverlays(fresh.root, fresh.entries, BASE),
    /hash/,
  );
  assert.equal(a.geometry, g);
  assert.ok(mesh(fresh.entries.get(trackedLayerNames[1])).parent);
});
test("batch rejects identity, transform, material, geometry and shared ownership changes before mutation", async () => {
  const mutations = [
    ({ root, entries }) =>
      (mesh(entries.get(trackedLayerNames[0])).position.x = 1),
    ({ entries }) =>
      (mesh(entries.get(trackedLayerNames[0])).userData.asset_id = "wrong"),
    ({ entries }) =>
      (mesh(entries.get(trackedLayerNames[0])).material.roughness = 0.9),
    ({ entries }) =>
      mesh(entries.get(trackedLayerNames[0])).geometry.attributes.position.setX(
        0,
        999,
      ),
    ({ root, entries }) =>
      root.add(mesh(entries.get(trackedLayerNames[0])).clone()),
    ({ entries }) =>
      (mesh(entries.get(trackedLayerNames[0])).material.onBeforeCompile =
        () => {}),
    ({ entries }) =>
      (mesh(entries.get(trackedLayerNames[0])).material.map =
        new THREE.Texture()),
    ({ entries }) =>
      mesh(entries.get(trackedLayerNames[0])).geometry.setDrawRange(0, 3),
  ];
  for (const mutate of mutations) {
    const f = fixture();
    const g = mesh(f.entries.get(trackedLayerNames[0])).geometry;
    mutate(f);
    await assert.rejects(mergePinnedBuildingOverlays(f.root, f.entries, BASE));
    assert.equal(mesh(f.entries.get(trackedLayerNames[0]))?.geometry ?? g, g);
  }
  const f = fixture();
  await assert.rejects(
    mergePinnedBuildingOverlays(f.root, f.entries, "wrong"),
    /base/,
  );
});

test("historical configured pins exclude a pair without suppressing its geometry", async () => {
  const { root, entries } = fixture();
  const key = "knight-library-window-reveals.json",
    entry = entries.get(key),
    original = mesh(entry),
    geometry = original.geometry;
  assert.equal(
    recipeSupports(
      key,
      "aa58ed85991c5db92b921ede21bec4d9c1959b782e5acc815cf57a2302417dbf",
    ),
    true,
  );
  assert.equal(recipeSupports(key, "historical-reviewed-pin"), false);
  assert.equal(
    recipeSupports("unknown.json", "historical-reviewed-pin"),
    false,
  );
  // Mirrors the loader: retain installed layer, omit it only from current-recipe map.
  if (!recipeSupports(key, "historical-reviewed-pin")) entries.delete(key);
  assert.equal(await mergePinnedBuildingOverlays(root, entries, BASE), 2);
  assert.equal(original.geometry, geometry);
  assert.equal(original.parent, entry.group);
  assert.equal(entry.group.parent, root);
});

test("batch preserves actual triangle ray hits and selected building identity", async () => {
  const { root, entries } = fixture();
  root.updateMatrixWorld(true);
  const checks = [];
  for (let i = 0; i < trackedLayerNames.length; i += 2) {
    const a = mesh(entries.get(trackedLayerNames[i])),
      b = mesh(entries.get(trackedLayerNames[i + 1]));
    const p = b.geometry.attributes.position,
      center = new THREE.Vector3();
    for (let j = 0; j < 3; j++)
      center.add(new THREE.Vector3().fromBufferAttribute(p, j));
    center.divideScalar(3);
    const normal = new THREE.Vector3()
      .fromBufferAttribute(b.geometry.attributes.normal, 0)
      .normalize();
    const ray = new THREE.Raycaster(
      center.clone().addScaledVector(normal, 0.2),
      normal.clone().negate(),
    );
    const before = ray.intersectObjects([a, b])[0];
    assert.ok(before);
    checks.push({
      ray,
      a,
      point: before.point.clone(),
      distance: before.distance,
      id: before.object.userData.asset_id,
    });
  }
  await mergePinnedBuildingOverlays(root, entries, BASE);
  root.updateMatrixWorld(true);
  for (const { ray, a, point, distance, id } of checks) {
    const after = ray.intersectObject(a)[0];
    assert.ok(after);
    assert.ok(after.point.distanceTo(point) < 1e-8);
    assert.ok(Math.abs(after.distance - distance) < 1e-8);
    assert.equal(after.object.userData.asset_id, id);
  }
});
