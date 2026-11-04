import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import * as THREE from "three";
import { createSky } from "../src/sky.js";
test("cloud shading keeps geometry, cloud batching and reduced-motion behavior", () => {
  const scene = new THREE.Scene(),
    sky = createSky(scene),
    root = scene.children[0],
    cloud = scene.getObjectByName("Rounded voxel cloud layer"),
    p = cloud.geometry.attributes.position,
    c = cloud.geometry.attributes.color;
  assert.deepEqual(sky.state(), { blue: true, clouds: 18, roundedEdges: true });
  assert.equal(root.children.length, 2);
  assert.equal(p.count, 81000);
  assert.equal(c.count, p.count);
  assert.equal(
    createHash("sha256")
      .update(
        Buffer.from(p.array.buffer, p.array.byteOffset, p.array.byteLength),
      )
      .digest("hex"),
    "964944a208d37f56db35df2dfbbe687e497ad9e1e2212f6c0b6ea1a96ddda7da",
  );
  assert.ok(
    [...c.array].every((v) => Number.isFinite(v) && v >= 0.71999 && v <= 1),
  );
  let low = 1,
    high = 0;
  for (let i = 0; i < c.count; i++) {
    low = Math.min(low, c.getX(i));
    high = Math.max(high, c.getX(i));
  }
  assert.ok(low < 0.73 && high > 0.99);
  assert.equal(cloud.material.vertexColors, true);
  const camera = new THREE.PerspectiveCamera();
  camera.position.set(2, 3, 4);
  sky.update(camera, 100, false);
  const angle = cloud.rotation.y;
  assert.ok(angle > 0);
  sky.update(camera, 1000, true);
  assert.equal(cloud.rotation.y, angle);
  assert.deepEqual(root.position.toArray(), [2, 3, 4]);
});
