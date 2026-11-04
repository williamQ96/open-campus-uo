import test from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import { createSky } from "../src/sky.js";
import { shapeCloudVolumes } from "../src/cloud-volumes.js";
const bounds = (p, start, count) => {
  let min = [Infinity, Infinity, Infinity],
    max = [-Infinity, -Infinity, -Infinity];
  for (let i = start; i < start + count; i++) {
    let v = [p.getX(i), p.getY(i), p.getZ(i)];
    for (let k = 0; k < 3; k++) {
      min[k] = Math.min(min[k], v[k]);
      max[k] = Math.max(max[k], v[k]);
    }
  }
  return { min, max };
};
test("rounded cloud lobes keep source centers, base heights and motion", () => {
  const scene = new THREE.Scene(),
    sky = createSky(scene),
    cloud = scene.getObjectByName("Rounded voxel cloud layer"),
    old = cloud.geometry,
    material = cloud.material;
  assert.equal(shapeCloudVolumes(scene), 90);
  const next = cloud.geometry;
  assert.equal(next.attributes.position.count, 27000);
  assert.equal(cloud.material, material);
  assert.ok([...next.attributes.position.array].every(Number.isFinite));
  for (let l = 0; l < 90; l++) {
    const a = bounds(old.attributes.position, l * 900, 900),
      b = bounds(next.attributes.position, l * 300, 300);
    assert.ok(Math.abs(a.min[1] - b.min[1]) < 0.001);
    for (const k of [0, 2]) {
      assert.ok(Math.abs(a.min[k] + a.max[k] - (b.min[k] + b.max[k])) < 0.002);
      assert.ok(b.min[k] >= a.min[k] - 0.001 && b.max[k] <= a.max[k] + 0.001);
    }
    const multiplier =
      l % 5 === 2 ? 1.35 : l % 5 === 1 || l % 5 === 3 ? 1.15 : 1;
    assert.ok(
      Math.abs(b.max[1] - b.min[1] - (a.max[1] - a.min[1]) * multiplier) <
        0.002,
    );
  }
  const camera = new THREE.PerspectiveCamera();
  sky.update(camera, 1000, false);
  const angle = cloud.rotation.y;
  sky.update(camera, 2000, true);
  assert.equal(cloud.rotation.y, angle);
  assert.throws(() => shapeCloudVolumes(scene));
  assert.equal(cloud.geometry, next);
});
test("unexpected cloud source rejects before mutation", () => {
  const scene = new THREE.Scene();
  createSky(scene);
  const m = scene.getObjectByName("Rounded voxel cloud layer"),
    g = m.geometry;
  m.geometry = g.clone();
  m.geometry.deleteAttribute("position");
  const invalid = m.geometry;
  assert.throws(() => shapeCloudVolumes(scene));
  assert.equal(m.geometry, invalid);
});
