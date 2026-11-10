// SPDX-License-Identifier: Apache-2.0
// Batch only these immutable, independently exported UO overlays; never the source GLB.
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { createExteriorDetail } from "./exterior-detail.js";
const BASE = "29f22c38eb5737fba2c8b3ab9618e049443c052e169e175f19428e66174ae896";
const recipes = [
  [
    "roof-6684e091",
    [
      "knight-library-balcony-detail.json",
      "b8344565659668b48f6ba00fceda9d096f7bac5f23c365ad1607495566a9ed74",
    ],
    [
      "knight-library-window-reveals.json",
      "aa58ed85991c5db92b921ede21bec4d9c1959b782e5acc815cf57a2302417dbf",
    ],
  ],
  [
    "roof-9ac93ab7",
    [
      "gerlinger-east-detail.json",
      "db6f5c816dcd48ec46cb1f7bac00e6202abe56e9f2465584745ad9bdb87f9e8a",
    ],
    [
      "gerlinger-east-masonry-detail.json",
      "fdae26b98f8f49b2de41d9475157d2e4fdc4b182e995f5a4346d660cbb9fb832",
    ],
  ],
  [
    "roof-906c030e",
    [
      "johnson-rear-detail.json",
      "2f8673dd96875d0f680e7a8431922e0989db8816500c63bdc6d4c0ea7249f81b",
    ],
    [
      "johnson-north-capitals.json",
      "95b1c547e803ad37d48b70d389c80d2fe28850e5c6f3b8fe6c9a290828f73a7d",
    ],
  ],
];
export const trackedLayerNames = recipes.flatMap((r) =>
  r.slice(1).map((v) => v[0]),
);
// Historical/configured alternative layers remain installed, but are not batched.
export function recipeSupports(name, configuredSha) {
  return recipes.some((recipe) =>
    recipe
      .slice(1)
      .some(([url, hash]) => url === name && hash === configuredSha),
  );
}
const identity = new THREE.Matrix4();
function staticObject(o) {
  if (!o.matrixAutoUpdate)
    throw Error("Overlay batch manual transforms unsupported");
  o.updateMatrix();
  if (
    !o.matrix.equals(identity) ||
    !o.visible ||
    o.animations.length ||
    o.renderOrder !== 0 ||
    o.layers.mask !== 1 ||
    o.castShadow ||
    o.receiveShadow ||
    !o.frustumCulled
  )
    throw Error("Overlay batching requires static identity objects");
}
function buildingMesh(group, id) {
  const matches = group.children.filter(
    (o) =>
      o.isMesh &&
      o.name === "exterior-detail-building" &&
      o.userData.asset_kind === "building" &&
      o.userData.asset_id === id,
  );
  if (matches.length !== 1) throw Error("Ambiguous overlay building identity");
  return matches[0];
}
function assertMaterial(m) {
  if (m?.isMeshStandardMaterial && !Array.isArray(m)) {
    const expected = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 0.87,
    });
    const a = m.toJSON(),
      b = expected.toJSON();
    delete a.uuid;
    delete b.uuid;
    expected.dispose();
    if (JSON.stringify(a) !== JSON.stringify(b))
      throw Error("Overlay serialized material contract changed");
  }
  if (
    Array.isArray(m) ||
    !m?.isMeshStandardMaterial ||
    !m.vertexColors ||
    m.color.getHexString() !== "ffffff" ||
    m.roughness !== 0.87 ||
    m.metalness !== 0 ||
    m.side !== THREE.FrontSide ||
    m.transparent ||
    m.opacity !== 1 ||
    m.alphaTest !== 0 ||
    !m.depthTest ||
    !m.depthWrite ||
    m.blending !== THREE.NormalBlending ||
    m.wireframe ||
    m.flatShading ||
    m.emissive.getHex() !== 0 ||
    m.polygonOffset ||
    m.clippingPlanes ||
    m.onBeforeCompile !== THREE.Material.prototype.onBeforeCompile ||
    Object.values(m).some((v) => v?.isTexture)
  )
    throw Error("Overlay material contract changed");
}
function assertGeometry(actual, expected) {
  if (
    actual.index ||
    actual.groups.length ||
    Object.keys(actual.morphAttributes).length ||
    actual.drawRange.start !== 0 ||
    actual.drawRange.count !== Infinity ||
    Object.keys(actual.attributes).sort().join() !== "color,normal,position"
  )
    throw Error("Overlay geometry layout changed");
  for (const key of ["position", "normal", "color"]) {
    const a = actual.attributes[key],
      b = expected.attributes[key];
    if (
      a.isInterleavedBufferAttribute ||
      a.itemSize !== b.itemSize ||
      a.count !== b.count ||
      a.normalized !== b.normalized ||
      a.array.constructor !== b.array.constructor
    )
      throw Error("Overlay geometry layout changed");
    for (let i = 0; i < a.array.length; i++)
      if (!Number.isFinite(a.array[i]) || a.array[i] !== b.array[i])
        throw Error("Overlay geometry differs from pinned source");
  }
}
// records: Map(url, { rawBytes: Uint8Array|ArrayBuffer, group: installed Group }).
// Missing layers are deliberately allowed for before/after diagnostics.
export async function mergePinnedBuildingOverlays(root, records, assetSha) {
  if (assetSha !== BASE) throw Error("Overlay batch base hash changed");
  const plans = [];
  try {
    for (const [id, left, right] of recipes) {
      if (!records.has(left[0]) || !records.has(right[0])) continue;
      const meshes = [];
      for (const [url, expectedHash] of [left, right]) {
        const { rawBytes: bytes, group } = records.get(url);
        const raw = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
        const digest = await crypto.subtle.digest("SHA-256", raw);
        const hash = Array.from(new Uint8Array(digest), (x) =>
          x.toString(16).padStart(2, "0"),
        ).join("");
        if (hash !== expectedHash)
          throw Error("Overlay batch source hash changed: " + url);
        const spec = JSON.parse(new TextDecoder().decode(raw));
        if (
          spec.base_asset_sha256 !== BASE ||
          spec.building_id !== id ||
          group.parent !== root
        )
          throw Error("Overlay batch source identity changed");
        staticObject(group);
        const mesh = buildingMesh(group, id);
        staticObject(mesh);
        assertMaterial(mesh.material);
        if (
          mesh.userData.surface_grain ||
          mesh.isSkinnedMesh ||
          mesh.isInstancedMesh
        )
          throw Error("Unsupported overlay state");
        let geometryOwners = 0,
          materialOwners = 0;
        root.traverse((o) => {
          if (o.isMesh) {
            if (o.geometry === mesh.geometry) geometryOwners++;
            if ([o.material].flat().includes(mesh.material)) materialOwners++;
          }
        });
        if (geometryOwners !== 1 || materialOwners !== 1)
          throw Error("Overlay resources have shared ownership");
        const generated = createExteriorDetail(spec, BASE, new Set([id]));
        try {
          assertGeometry(mesh.geometry, buildingMesh(generated, id).geometry);
        } finally {
          generated.traverse((o) => {
            if (o.isMesh) {
              o.geometry.dispose();
              [o.material].flat().forEach((m) => m.dispose());
            }
          });
        }
        meshes.push(mesh);
      }
      const geometry = mergeGeometries(
        meshes.map((m) => m.geometry),
        false,
      );
      if (!geometry) throw Error("Overlay batch geometry incompatible");
      geometry.computeBoundingBox();
      geometry.computeBoundingSphere();
      plans.push({ a: meshes[0], b: meshes[1], geometry });
    }
  } catch (error) {
    plans.forEach((p) => p.geometry.dispose());
    throw error;
  }
  // All source/material/ownership checks complete before mutating any layer.
  for (const { a, b, geometry } of plans) {
    const group = b.parent;
    a.geometry.dispose();
    a.geometry = geometry;
    b.geometry.dispose();
    b.material.dispose();
    b.removeFromParent();
    if (!group.children.length) group.removeFromParent();
  }
  return plans.length;
}
