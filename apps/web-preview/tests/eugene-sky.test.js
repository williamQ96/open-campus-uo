import test from "node:test";
import assert from "node:assert/strict";
import { PerspectiveCamera, Raycaster, Scene, Vector3 } from "three";
import { createEugeneSky } from "../src/eugene-sky.js";

test("Eugene sky has an inward dome and two distinct cloud heights in two meshes", () => {
  const scene = new Scene();
  const sky = createEugeneSky(scene);
  const [dome, clouds] = scene.children[0].children;
  assert.equal(scene.children[0].children.length, 2);
  assert.deepEqual(sky.state().layers, [12, 6]);
  assert.equal(sky.state().clouds, 18);
  assert.equal(dome.geometry.index.count / 3, 1680);
  assert.equal(clouds.geometry.index.count / 3, 7776);

  for (const mesh of [dome, clouds]) {
    const { position, color, normal } = mesh.geometry.attributes;
    assert.equal(color.count, position.count);
    assert.ok(color.array.every((value) => value >= 0 && value <= 1));
    for (let i = 0; i < normal.count; i++) {
      const length = Math.hypot(normal.getX(i), normal.getY(i), normal.getZ(i));
      assert.ok(Math.abs(length - 1) < 1e-6);
    }
    assert.equal(mesh.material.depthWrite, false);
    assert.equal(mesh.material.fog, false);
  }
  for (const direction of [
    [1, 0, 0],
    [0, 1, 0],
    [-1, -1, 1],
  ]) {
    const [hit] = new Raycaster(
      new Vector3(),
      new Vector3(...direction).normalize(),
    ).intersectObject(dome);
    assert.ok(hit?.distance >= 6700 && hit.distance <= 6801);
    assert.ok(hit.normal.dot(hit.point) < 0);
  }

  const p = clouds.geometry.attributes.position;
  const perBank = p.count / sky.state().clouds;
  const altitudes = Array.from({ length: 18 }, (_, bank) => {
    const samples = Array.from({ length: perBank }, (_, i) =>
      p.getY(bank * perBank + i),
    );
    return [Math.min(...samples), Math.max(...samples)];
  });
  const low = altitudes.slice(0, 12);
  const upper = altitudes.slice(12);
  assert.ok(
    Math.max(...low.map(([, top]) => top)) <
      Math.min(...upper.map(([base]) => base)),
  );
  assert.ok(Math.min(...low.map(([base, top]) => top - base)) > 100);
  assert.ok(Math.max(...upper.map(([base, top]) => top - base)) < 95);
});

test("sky tracks the camera and resumes drift without catching up reduced-motion time", () => {
  const scene = new Scene();
  const sky = createEugeneSky(scene);
  const root = scene.children[0];
  const clouds = root.getObjectByName("cloud-banks");
  const camera = new PerspectiveCamera();
  camera.position.set(50, 100, -40);
  sky.update(camera, 10);
  const angle = clouds.rotation.y;
  assert.ok(angle > 0);
  sky.update(camera, 80, true);
  camera.position.set(30, 5, -18);
  sky.update(camera, 300, true);
  assert.deepEqual(root.position.toArray(), [30, 5, -18]);
  assert.equal(clouds.rotation.y, angle);
  sky.update(camera, 605);
  assert.equal(clouds.rotation.y, angle);
  sky.update(camera, 606);
  assert.ok(Math.abs(clouds.rotation.y - angle - angle / 10) < 1e-12);
});
