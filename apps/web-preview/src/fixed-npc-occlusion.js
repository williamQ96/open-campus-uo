// SPDX-License-Identifier: Apache-2.0
import * as THREE from "three";

// Hide a person's label only if both sampled body points are behind buildings.
// Occluders are the scene's selectable building meshes, including batched proxies.
export function createPersonOcclusion(camera, occluders) {
  const ray = new THREE.Raycaster();
  const origin = new THREE.Vector3(),
    target = new THREE.Vector3();
  const direction = new THREE.Vector3(),
    hits = [];
  const blocked = (position, height) => {
    target.copy(position);
    target.y += height;
    direction.subVectors(target, origin);
    const distance = direction.length();
    if (distance <= 0.2) return false;
    ray.set(origin, direction.multiplyScalar(1 / distance));
    ray.near = 0.05;
    ray.far = distance - 0.1;
    hits.length = 0;
    return ray.intersectObjects(occluders, false, hits).length > 0;
  };
  return (position) => {
    camera.getWorldPosition(origin);
    return blocked(position, 0.95) && blocked(position, 1.65);
  };
}
