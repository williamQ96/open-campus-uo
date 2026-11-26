import test from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import { createCampusProp, roadVehicleCollider } from "../src/props.js";

const vehicles = {
  car: { dimensions: [4.64, 2.01, 1.44], body: 1.78, wheelbase: 2.7 },
  suv: { dimensions: [4.69, 2.1, 1.68], body: 1.87, wheelbase: 2.7 },
  van: { dimensions: [4.73, 2.04, 1.87], body: 1.73, wheelbase: 2.93 },
  pickup: { dimensions: [5.08, 2.12, 1.75], body: 1.84, wheelbase: 3.08 },
};
const close = (actual, expected) =>
  assert.ok(
    Math.abs(actual - expected) < 1e-5,
    `${actual} differs from ${expected}`,
  );
const hasColor = (colors, i, { r, g, b }) =>
  Math.abs(colors.getX(i) - r) < 1e-5 &&
  Math.abs(colors.getY(i) - g) < 1e-5 &&
  Math.abs(colors.getZ(i) - b) < 1e-5;

for (const [kind, { dimensions, body, wheelbase }] of Object.entries(
  vehicles,
)) {
  test(`${kind} has grounded wheels, visible glazing and matching collision dimensions`, () => {
    const mesh = createCampusProp(kind);
    const { geometry } = mesh;
    const { position, color } = geometry.attributes;
    const tire = new THREE.Color(0x273334);
    const glass = new THREE.Color(0x69958e);
    const contacts = new Set();
    const axles = new Set();

    assert.equal(mesh.userData.kind, kind);
    assert.ok(position.count <= 3200);
    assert.ok(position.array.every(Number.isFinite));
    geometry.computeBoundingBox();
    const { min, max } = geometry.boundingBox;
    close(min.y, 0);
    [max.z - min.z, max.x - min.x, max.y - min.y].forEach((value, i) =>
      close(value, dimensions[i]),
    );
    for (let i = 0; i < position.count; i++) {
      if (Math.abs(position.getY(i)) > 1e-5 || !hasColor(color, i, tire))
        continue;
      const axle = Number(position.getZ(i).toFixed(4));
      contacts.add(`${Math.sign(position.getX(i))},${axle}`);
      axles.add(axle);
    }
    assert.equal(contacts.size, 4);
    assert.equal(axles.size, 2);
    close(Math.max(...axles) - Math.min(...axles), wheelbase);

    const hit = new THREE.Raycaster(
      new THREE.Vector3(0, max.y - 0.26, max.z + 1),
      new THREE.Vector3(0, 0, -1),
    ).intersectObject(mesh)[0];
    assert.ok(hit && hasColor(color, hit.face.a, glass));

    const capsule = roadVehicleCollider(kind);
    close(2 * capsule.radius, body);
    close(2 * (capsule.radius + capsule.halfLength), dimensions[0]);
    close(capsule.height, dimensions[2]);
  });
}
