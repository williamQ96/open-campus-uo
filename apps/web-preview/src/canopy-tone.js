// SPDX-License-Identifier: Apache-2.0
// Source-pinned, reversible presentation color variation for existing canopy meshes.
import * as THREE from "three";
export function applyCanopyTone(root, spec, assetSha) {
  if (
    spec.version !== 1 ||
    spec.operation !== "canopy-tone-v1" ||
    spec.base_asset_sha256 !== assetSha ||
    spec.target_name !== "vegetation" ||
    !Number.isFinite(spec.strength) ||
    spec.strength < 0 ||
    spec.strength > 0.2 ||
    !Array.isArray(spec.meshes) ||
    spec.meshes.length !== 3
  )
    throw new Error("Invalid source-pinned canopy tone specification.");
  const target = root.getObjectByName(spec.target_name),
    found = new Map();
  if (!target) throw new Error("Missing vegetation batch.");
  target.traverse((o) => {
    if (o.isMesh) {
      if (found.has(o.name)) throw new Error("Duplicate vegetation mesh.");
      found.set(o.name, o);
    }
  });
  const seen = new Set(),
    pending = [];
  for (const record of spec.meshes) {
    const mesh = found.get(record.name),
      p = mesh?.geometry?.attributes?.position;
    if (
      seen.has(record.name) ||
      !mesh ||
      !p ||
      p.itemSize !== 3 ||
      p.count !== record.vertices ||
      mesh.geometry.hasAttribute("color") ||
      Array.isArray(mesh.material) ||
      mesh.material.name !== record.material ||
      mesh.material.color?.getHexString() !== record.color ||
      mesh.material.vertexColors ||
      !mesh.matrix.equals(new THREE.Matrix4())
    )
      throw new Error(
        "Canopy mesh or material changed; revalidate the source.",
      );
    seen.add(record.name);
    const color = new Float32Array(p.count * 3);
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i),
        y = p.getY(i),
        z = p.getZ(i);
      if (![x, y, z].every(Number.isFinite))
        throw new Error("Invalid canopy vertex.");
      const wave = Math.sin(x * 0.71 + z * 0.37) * Math.sin(y * 0.6 - z * 0.24);
      const shade = 1 - spec.strength * (0.5 + 0.5 * wave);
      color.set([shade, shade, shade], i * 3);
    }
    // The leaf material is shared with non-canopy planting; clone before enabling vertex colors.
    pending.push([
      mesh,
      new THREE.BufferAttribute(color, 3),
      mesh.material.clone(),
    ]);
  }
  for (const [mesh, color, material] of pending) {
    mesh.geometry.setAttribute("color", color);
    material.vertexColors = true;
    material.needsUpdate = true;
    mesh.material = material;
  }
  return pending.reduce(
    (sum, [mesh]) => sum + mesh.geometry.attributes.position.count,
    0,
  );
}
