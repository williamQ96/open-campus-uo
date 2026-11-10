// SPDX-License-Identifier: Apache-2.0
// Original stylized fur/face accents on the existing CC0-derived silhouette.
// Vertex colors preserve the shared material and do not imply a surveyed species.
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";

export function addSquirrelEyes(scene) {
  const matches = [];
  scene.traverse((o) => {
    if (o.isMesh && o.name === "Campus_squirrel_-_CC0_source") matches.push(o);
  });
  if (matches.length !== 1)
    throw Error("Squirrel source mesh missing or ambiguous");
  const mesh = matches[0],
    g = mesh.geometry;
  if (
    g.attributes.position?.count !== 2700 ||
    !g.index ||
    !g.attributes.normal ||
    !g.attributes.uv ||
    Array.isArray(mesh.material) ||
    mesh.material.color.getHexString() !== "866142" ||
    mesh.material.vertexColors ||
    mesh.material.map
  )
    throw Error("Squirrel source geometry or material changed");
  g.computeBoundingBox();
  const box = g.boundingBox;
  if (
    Math.abs(box.min.x + 0.30840984) > 0.00001 ||
    Math.abs(box.max.y - 0.47440159) > 0.00001
  )
    throw Error("Squirrel source bounds changed");
  const points = [
    [0.17, 0.27, 0.0374],
    [0.17, 0.27, -0.0339],
  ];
  const ray = new THREE.Raycaster();
  for (const [x, y, z] of points) {
    ray.set(
      new THREE.Vector3(x, y, Math.sign(z)),
      new THREE.Vector3(0, 0, -Math.sign(z)),
    );
    const hit = ray.intersectObject(mesh)[0];
    if (!hit || Math.abs(hit.point.z - z) > 0.002)
      throw Error("Squirrel face surface changed");
  }
  const body = g.toNonIndexed();
  body.deleteAttribute("uv");
  const colorBody = new Float32Array(body.attributes.position.count * 3).fill(
    1,
  );
  const positions = body.attributes.position;
  // A small charcoal nose and restrained warm chest contrast improve readability
  // in close-up without changing the source silhouette or topology.
  const chestWarmth = [0.14, 0.16, 0.18];
  for (let i = 0; i < positions.count; i++) {
    const x = positions.getX(i),
      y = positions.getY(i),
      z = positions.getZ(i);
    const nose =
      THREE.MathUtils.smoothstep(x, 0.222, 0.237) *
      THREE.MathUtils.smoothstep(y, 0.19, 0.21);
    const chest =
      Math.max(0, 1 - ((y - 0.12) / 0.13) ** 2 - (z / 0.065) ** 2) *
      THREE.MathUtils.smoothstep(x, 0.035, 0.105);
    for (let channel = 0; channel < 3; channel++) {
      const warm = chestWarmth[channel];
      colorBody[i * 3 + channel] = THREE.MathUtils.lerp(
        0.82 + chest * warm,
        0.12,
        nose,
      );
    }
  }
  body.setAttribute("color", new THREE.BufferAttribute(colorBody, 3));
  const parts = [body];
  for (const [x, y, z] of points) {
    const eye = new THREE.IcosahedronGeometry(0.007, 1);
    eye.translate(x, y, z + Math.sign(z) * 0.001);
    eye.deleteAttribute("uv");
    const color = new Float32Array(eye.attributes.position.count * 3).fill(
      0.035,
    );
    eye.setAttribute("color", new THREE.BufferAttribute(color, 3));
    parts.push(eye);
  }
  const merged = mergeGeometries(parts);
  // mergeGeometries copies attributes; release only our temporary geometries.
  // The caller still owns the source GLB geometry and material.
  for (const part of parts) part.dispose();
  if (!merged) throw Error("Squirrel geometry could not be merged");
  const material = mesh.material.clone();
  material.vertexColors = true;
  mesh.geometry = merged;
  mesh.material = material;
  return {
    mesh,
    originalVertices: body.attributes.position.count,
    addedVertices:
      merged.attributes.position.count - body.attributes.position.count,
  };
}
