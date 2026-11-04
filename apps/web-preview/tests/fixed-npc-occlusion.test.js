import { test } from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import { createPersonOcclusion } from "../src/fixed-npc-occlusion.js";
test("building hides person only when both body samples are obstructed", () => {
  const camera = new THREE.PerspectiveCamera();
  camera.position.set(0, 1.5, 0);
  camera.updateMatrixWorld();
  const wall = new THREE.Mesh(
    new THREE.BoxGeometry(4, 4, 0.2),
    new THREE.MeshBasicMaterial(),
  );
  wall.position.set(0, 1, -5);
  wall.updateMatrixWorld();
  const isHidden = createPersonOcclusion(camera, [wall]),
    person = new THREE.Vector3(0, 0, -10);
  assert.equal(isHidden(person), true);
  wall.position.x = 5;
  wall.updateMatrixWorld();
  assert.equal(isHidden(person), false);
  wall.position.set(0, 0.65, -5);
  wall.scale.y = 0.325;
  wall.updateMatrixWorld();
  const probe = (height) => {
    const target = person.clone().add(new THREE.Vector3(0, height, 0));
    const direction = target.sub(camera.position).normalize();
    return (
      new THREE.Raycaster(camera.position, direction, 0, 10).intersectObject(
        wall,
      ).length > 0
    );
  };
  assert.equal(probe(0.95), true);
  assert.equal(probe(1.65), false);
  assert.equal(isHidden(person), false);
  wall.position.set(0, 1, -15);
  wall.scale.y = 1;
  wall.updateMatrixWorld();
  assert.equal(isHidden(person), false);
});
