// SPDX-License-Identifier: Apache-2.0
// Generic eye accents on the existing CC0-derived squirrel silhouette.
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
