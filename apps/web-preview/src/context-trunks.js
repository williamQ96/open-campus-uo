// SPDX-License-Identifier: Apache-2.0
// Replaces only the 300 source-matched square context trunks with octagonal trunks.
import * as THREE from "three";
export function refineContextTrunks(root, spec, sha) {
  if (
    spec?.version !== 1 ||
    spec.operation !== "context-trunks-v1" ||
    spec.base_asset_sha256 !== sha ||
    spec.target_name !== "campus-trees" ||
    spec.count !== 300 ||
    spec.sides !== 8
  )
    throw Error("Invalid context trunk specification");
  const found = [];
  root.traverse((o) => {
    if (o.isMesh && o.name === spec.target_name) found.push(o);
  });
  if (found.length !== 1) throw Error("Context tree mesh missing or ambiguous");
  const mesh = found[0],
    g = mesh.geometry,
    p = g.attributes.position,
    n = g.attributes.normal,
    c = g.attributes.color,
    index = g.index;
  if (
    mesh.userData.asset_kind !== "landscape-detail" ||
    !mesh.matrix.equals(new THREE.Matrix4()) ||
    Array.isArray(mesh.material) ||
    !mesh.material.vertexColors ||
    !p ||
    !n ||
    !c ||
    !index ||
    p.count !== 45600 ||
    n.count !== 45600 ||
    c.count !== 45600 ||
    c.itemSize !== 3 ||
    index.count !== 68400
  )
    throw Error("Context tree source contract changed");
  const centers = [];
  const bark = [0.18447499, 0.12477182, 0.07818742];
  for (let tree = 0; tree < 300; tree++) {
    const off = tree * 152,
      io = tree * 228;
    let xmin = Infinity,
      xmax = -Infinity,
      zmin = Infinity,
      zmax = -Infinity,
      ymin = Infinity,
      ymax = -Infinity;
    for (let j = 0; j < 24; j++) {
      let i = off + j;
      let x = p.getX(i),
        y = p.getY(i),
        z = p.getZ(i);
      if (
        ![x, y, z, c.getX(i), c.getY(i), c.getZ(i)].every(Number.isFinite) ||
        Math.abs(c.getX(i) - bark[0]) > 0.0001 ||
        Math.abs(c.getY(i) - bark[1]) > 0.0001 ||
        Math.abs(c.getZ(i) - bark[2]) > 0.0001
      )
        throw Error("Context trunk color changed");
      xmin = Math.min(xmin, x);
      xmax = Math.max(xmax, x);
      zmin = Math.min(zmin, z);
      zmax = Math.max(zmax, z);
      ymin = Math.min(ymin, y);
      ymax = Math.max(ymax, y);
    }
    if (
      Math.abs(xmax - xmin - 0.3) > 0.0002 ||
      Math.abs(zmax - zmin - 0.3) > 0.0002 ||
      ymax <= ymin
    )
      throw Error("Context trunk dimensions changed");
    for (let j = 0; j < 228; j++) {
      const relative = index.getX(io + j) - off;
      if (
        relative < 0 ||
        relative >= 152 ||
        (j < 36 ? relative >= 24 : relative < 24)
      )
        throw Error("Context tree topology changed");
    }
    centers.push([(xmin + xmax) / 2, (zmin + zmax) / 2, ymin, ymax]);
  }
  const extra = 300 * 32,
    total = p.count + extra,
    positions = new Float32Array(total * 3),
    normals = new Float32Array(total * 3),
    colors = new Float32Array(total * 3);
  positions.set(p.array);
  normals.set(n.array);
  colors.set(c.array);
  const indices = new Uint16Array(300 * (192 + 48));
  let at = 0;
  for (let tree = 0; tree < 300; tree++) {
    for (let j = 36; j < 228; j++) indices[at++] = index.getX(tree * 228 + j);
    const [x, z, y0, y1] = centers[tree];
    for (let side = 0; side < 8; side++) {
      const a = (2 * Math.PI * side) / 8,
        b = (2 * Math.PI * (side + 1)) / 8,
        mid = (a + b) / 2,
        base = p.count + tree * 32 + side * 4;
      const verts = [
        [x + 0.15 * Math.cos(a), y0, z + 0.15 * Math.sin(a)],
        [x + 0.15 * Math.cos(b), y0, z + 0.15 * Math.sin(b)],
        [x + 0.15 * Math.cos(b), y1, z + 0.15 * Math.sin(b)],
        [x + 0.15 * Math.cos(a), y1, z + 0.15 * Math.sin(a)],
      ];
      for (let q = 0; q < 4; q++) {
        const k = (base + q) * 3;
        positions.set(verts[q], k);
        normals.set([Math.cos(mid), 0, Math.sin(mid)], k);
        colors.set(bark, k);
      }
      indices.set([base, base + 2, base + 1, base, base + 3, base + 2], at);
      at += 6;
    }
  }
  const replacement = new THREE.BufferGeometry();
  replacement.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  replacement.setAttribute("normal", new THREE.BufferAttribute(normals, 3));
  replacement.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  replacement.setIndex(new THREE.BufferAttribute(indices, 1));
  replacement.computeBoundingBox();
  replacement.computeBoundingSphere();
  mesh.geometry = replacement;
  return centers.length;
}
