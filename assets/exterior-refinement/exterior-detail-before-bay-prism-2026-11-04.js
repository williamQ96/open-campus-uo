// SPDX-License-Identifier: Apache-2.0
// Construct a source-pinned, independently editable exterior detail layer.
import * as THREE from "three";
import { createFernGeometry } from "./fern-geometry.js";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
const palette = {
  stone: "#e4d6bb",
  "station-cladding": "#d5ddda",
  "station-wall": "#526f6d",
  roof: "#a8adb0",
  dark: "#283d39",
  wood: "#8e7154",
  "bench-wood": "#77634f",
  "fern-green": "#829e59",
  "lamp-metal": "#3f514b",
  glass: "#608788",
  shrub: "#577750",
  "shrub-light": "#718c5d",
  "shrub-deep": "#405f49",
  soil: "#675744",
  metal: "#3f514b",
  brick: "#b96f55",
  concrete: "#a8adb0",
  cream: "#eee6d3",
  awning: "#824b51",
  "flower-magenta": "#ba4d78",
  "flower-light": "#df83a2",
  "brick-dark": "#9c5d4d",
  "roof-dark": "#655f4b",
  "roof-slate": "#6c7271",
};
export function createExteriorDetail(spec, assetSha, buildingIds) {
  const environment = spec?.scope === "environment";
  if (
    spec?.version !== 1 ||
    spec.base_asset_sha256 !== assetSha ||
    (spec.scope !== undefined && !environment) ||
    (environment
      ? spec.building_id !== undefined ||
        spec.replace_building !== false ||
        !Array.isArray(spec.objects) ||
        spec.objects.some((item) => item?.kind === "building")
      : !buildingIds.has(spec.building_id)) ||
    !Array.isArray(spec.objects) ||
    !spec.objects.length ||
    spec.objects.length > 500
  )
    throw new Error("Exterior detail does not match the presentation asset.");
  const buckets = new Map();
  const labels = [];
  for (const item of spec.objects) {
    if (
      !["building", "vegetation", "prop"].includes(item.kind) ||
      !Object.hasOwn(palette, item.material) ||
      ![
        "box",
        "shrub",
        "gable",
        "label",
        "disk",
        "ridge",
        "hip",
        "arch",
        "arch-x",
        "pointed-arch-x",
        "gambrel",
        "gable-hip",
        "fern",
        "column",
      ].includes(item.shape) ||
      ![item.position, item.size].every(
        (v) => Array.isArray(v) && v.length === 3 && v.every(Number.isFinite),
      ) ||
      item.size.some((n) => n <= 0 || n > 100) ||
      (item.rotation !== undefined &&
        (item.shape === "label" ||
          !Array.isArray(item.rotation) ||
          item.rotation.length !== 3 ||
          !item.rotation.every(
            (n) => Number.isFinite(n) && Math.abs(n) <= Math.PI,
          )))
    )
      throw new Error("Invalid exterior detail geometry.");
    if (item.shape === "label") {
      if (
        item.kind !== "building" ||
        typeof item.text !== "string" ||
        !/^[A-Z ]{1,64}$/.test(item.text)
      )
        throw new Error("Invalid exterior label.");
      labels.push(item);
      continue;
    }
    let geometry;
    if (item.shape === "gambrel") {
      const shape = new THREE.Shape();
      shape.moveTo(-0.5, 0);
      shape.lineTo(0.5, 0);
      shape.lineTo(0.38, 0.68);
      shape.lineTo(0.2, 1);
      shape.lineTo(-0.2, 1);
      shape.lineTo(-0.38, 0.68);
      shape.closePath();
      geometry = new THREE.ExtrudeGeometry(shape, {
        depth: 1,
        bevelEnabled: false,
      });
      geometry.translate(0, 0, -0.5);
      geometry.rotateY(Math.PI / 2);
      geometry.scale(...item.size);
    } else if (
      item.shape === "arch" ||
      item.shape === "arch-x" ||
      item.shape === "pointed-arch-x"
    ) {
      const shape = new THREE.Shape();
      shape.moveTo(-0.5, -0.5);
      shape.lineTo(0.5, -0.5);
      if (item.shape === "pointed-arch-x") {
        shape.lineTo(0.5, 0.15);
        shape.quadraticCurveTo(0.5, 0.32, 0, 0.5);
        shape.quadraticCurveTo(-0.5, 0.32, -0.5, 0.15);
      } else {
        shape.lineTo(0.5, 0.25);
        shape.quadraticCurveTo(0.5, 0.5, 0, 0.5);
        shape.quadraticCurveTo(-0.5, 0.5, -0.5, 0.25);
      }
      shape.closePath();
      geometry = new THREE.ExtrudeGeometry(shape, {
        depth: 1,
        bevelEnabled: false,
        curveSegments: 8,
      });
      geometry.translate(0, 0, -0.5);
      if (item.shape === "arch-x" || item.shape === "pointed-arch-x")
        geometry.rotateY(Math.PI / 2);
      geometry.scale(...item.size);
    } else if (item.shape === "column") {
      geometry = new THREE.CylinderGeometry(0.5, 0.5, 1, 8);
      geometry.scale(...item.size);
    } else if (item.shape === "fern") {
      geometry = createFernGeometry();
      geometry.scale(...item.size);
    } else if (item.shape === "hip") {
      geometry = new THREE.CylinderGeometry(0.27, 0.5, 1, 4, 1);
      geometry.rotateY(Math.PI / 4);
      geometry.scale(
        item.size[0] * Math.SQRT2,
        item.size[1],
        item.size[2] * Math.SQRT2,
      );
    } else if (item.shape === "gable-hip") {
      const [w, h, d] = item.size;
      if (w <= d)
        throw new Error("Gable-hip roof requires width greater than depth.");
      const r = (w - d) / 2;
      const vertices = [
        [-w / 2, 0, -d / 2],
        [w / 2, 0, -d / 2],
        [w / 2, 0, d / 2],
        [-w / 2, 0, d / 2],
        [-r, h, 0],
        [r, h, 0],
      ];
      const faces = [
        [0, 4, 5],
        [0, 5, 1],
        [3, 2, 5],
        [3, 5, 4],
        [0, 3, 4],
        [1, 5, 2],
        [0, 1, 2],
        [0, 2, 3],
      ];
      geometry = new THREE.BufferGeometry();
      geometry.setAttribute(
        "position",
        new THREE.Float32BufferAttribute(
          faces.flatMap((face) => face.flatMap((i) => vertices[i])),
          3,
        ),
      );
      geometry.computeVertexNormals();
    } else if (item.shape === "ridge") {
      const [w, h, d] = item.size;
      const v = [
        [-w / 2, 0, -d / 2],
        [w / 2, 0, -d / 2],
        [0, h, -d / 2],
        [-w / 2, 0, d / 2],
        [w / 2, 0, d / 2],
        [0, h, d / 2],
      ];
      const faces = [
        [0, 2, 1],
        [3, 4, 5],
        [0, 3, 5],
        [0, 5, 2],
        [1, 2, 5],
        [1, 5, 4],
        [0, 1, 4],
        [0, 4, 3],
      ];
      geometry = new THREE.BufferGeometry();
      geometry.setAttribute(
        "position",
        new THREE.Float32BufferAttribute(
          faces.flatMap((face) => face.flatMap((i) => v[i])),
          3,
        ),
      );
      geometry.computeVertexNormals();
    } else if (item.shape === "disk") {
      geometry = new THREE.CylinderGeometry(0.5, 0.5, 1, 20);
      geometry.rotateZ(Math.PI / 2);
      geometry.scale(...item.size);
    } else if (item.shape === "gable") {
      const shape = new THREE.Shape();
      shape.moveTo(-0.5, 0);
      shape.lineTo(0.5, 0);
      shape.lineTo(0, 1);
      shape.closePath();
      geometry = new THREE.ExtrudeGeometry(shape, {
        depth: 1,
        bevelEnabled: false,
      });
      geometry.scale(item.size[2], item.size[1], item.size[0]);
      geometry.rotateY(Math.PI / 2);
    } else {
      geometry =
        item.shape === "box"
          ? new THREE.BoxGeometry(1, 1, 1)
          : new THREE.IcosahedronGeometry(1, 1);
      geometry.scale(...item.size);
    }
    if (item.rotation) {
      geometry.rotateX(item.rotation[0]);
      geometry.rotateY(item.rotation[1]);
      geometry.rotateZ(item.rotation[2]);
    }
    geometry.translate(...item.position);
    if (geometry.index) {
      const indexed = geometry;
      geometry = indexed.toNonIndexed();
      indexed.dispose();
    }
    geometry.deleteAttribute("uv");
    const color = new THREE.Color(palette[item.material]);
    const colors = new Float32Array(geometry.attributes.position.count * 3);
    for (let i = 0; i < colors.length; i += 3) {
      colors[i] = color.r;
      colors[i + 1] = color.g;
      colors[i + 2] = color.b;
    }
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    if (!buckets.has(item.kind)) buckets.set(item.kind, []);
    buckets.get(item.kind).push(geometry);
  }
  const group = new THREE.Group();
  for (const [key, geometries] of buckets) {
    const kind = key;
    const geometry = mergeGeometries(geometries);
    for (const part of geometries) part.dispose();
    const mesh = new THREE.Mesh(
      geometry,
      new THREE.MeshStandardMaterial({
        vertexColors: true,
        roughness: 0.87,
      }),
    );
    mesh.name = `exterior-detail-${key}`;
    mesh.userData =
      kind === "building"
        ? { asset_kind: "building", asset_id: spec.building_id }
        : { asset_kind: kind };
    group.add(mesh);
  }
  for (const item of labels) {
    const canvas = document.createElement("canvas");
    canvas.width = 2048;
    canvas.height = 128;
    const context = canvas.getContext("2d");
    if (!context) throw new Error("Exterior label canvas unavailable.");
    context.fillStyle = palette[item.material];
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = "#796a49";
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.font = "80px Georgia, serif";
    context.fillText(
      item.text,
      canvas.width / 2,
      canvas.height / 2,
      canvas.width - 80,
    );
    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    const mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(item.size[0], item.size[1]),
      new THREE.MeshStandardMaterial({
        map: texture,
        roughness: 0.87,
        side: THREE.DoubleSide,
      }),
    );
    mesh.name = "exterior-detail-label";
    mesh.position.set(...item.position);
    mesh.rotation.y = Math.PI;
    mesh.userData = { asset_kind: "building", asset_id: spec.building_id };
    group.add(mesh);
  }
  return group;
}

// Apply an independently source-pinned replacement without changing the base GLB.
export function installExteriorDetail(root, spec, assetSha, buildingIds) {
  if (
    spec?.replace_building !== undefined &&
    typeof spec.replace_building !== "boolean"
  )
    throw new Error("Invalid exterior replacement flag.");
  const matches = [];
  if (spec?.replace_building) {
    root.traverse((object) => {
      if (
        (object.isMesh || object.isGroup) &&
        object.userData.asset_kind === "building" &&
        object.userData.asset_id === spec.building_id
      )
        matches.push(object);
    });
    if (matches.length !== 1 || !matches[0].parent)
      throw new Error("Exterior replacement target is ambiguous or absent.");
  }
  const detail = createExteriorDetail(spec, assetSha, buildingIds);
  if (matches.length) matches[0].parent.remove(matches[0]);
  root.add(detail);
  return detail;
}

// Merge an authored facade into its exact, uniquely identified source building mesh.
// The source material and semantic identity remain; no additional draw call is added.
export function mergeBuildingDetailIntoSource(root, detail, spec) {
  if (
    spec.replace_building !== false ||
    !Number.isInteger(spec.merge_source_vertex_count) ||
    spec.merge_source_vertex_count < 1 ||
    detail.parent !== root
  )
    throw new Error("Invalid building detail merge contract.");
  const targets = root.children.filter(
    (o) =>
      o.isMesh &&
      o.name === spec.building_id &&
      o.userData.asset_kind === "building" &&
      o.userData.asset_id === spec.building_id,
  );
  const parts = detail.children.filter(
    (o) =>
      o.isMesh &&
      o.name === "exterior-detail-building" &&
      o.userData.asset_id === spec.building_id,
  );
  if (
    targets.length !== 1 ||
    parts.length !== 1 ||
    detail.children.length !== 1
  )
    throw new Error("Ambiguous building detail merge.");
  const target = targets[0],
    part = parts[0];
  for (const o of [target, detail, part]) {
    o.updateMatrix();
    if (
      !o.matrix.equals(new THREE.Matrix4()) ||
      o.animations.length ||
      !o.visible
    )
      throw new Error("Building merge requires static identity transforms.");
  }
  const a = target.geometry,
    b = part.geometry,
    m = target.material,
    n = part.material;
  if (
    a.attributes.position.count !== spec.merge_source_vertex_count ||
    target.userData.surface_grain ||
    Array.isArray(m) ||
    !m.isMeshStandardMaterial ||
    !m.vertexColors ||
    m.color.getHexString() !== "ffffff" ||
    m.map ||
    m.transparent ||
    m.metalness !== 0 ||
    m.side !== THREE.DoubleSide ||
    Math.abs(m.roughness - 0.9) > 0.001 ||
    Array.isArray(n) ||
    !n.isMeshStandardMaterial ||
    !n.vertexColors ||
    n.map ||
    n.transparent
  )
    throw new Error("Source building merge contract changed.");
  a.computeBoundingBox();
  b.computeBoundingBox();
  const ab = a.boundingBox,
    bb = b.boundingBox;
  if (
    !ab ||
    !bb ||
    bb.min.x < ab.min.x - 3 ||
    bb.max.x > ab.max.x + 3 ||
    bb.min.z < ab.min.z - 3 ||
    bb.max.z > ab.max.z + 3 ||
    bb.min.y < ab.min.y - 3 ||
    bb.max.y > ab.max.y + 3
  )
    throw new Error("Building detail exceeds source bounds.");
  let base = a.index ? a.toNonIndexed() : a.clone();
  if (
    spec.trim_source_min_y !== undefined ||
    spec.trim_source_expected_triangles !== undefined
  ) {
    if (
      !Number.isFinite(spec.trim_source_min_y) ||
      spec.trim_source_min_y <= ab.min.y ||
      spec.trim_source_min_y >= ab.max.y ||
      !Number.isInteger(spec.trim_source_expected_triangles) ||
      spec.trim_source_expected_triangles < 1 ||
      spec.trim_source_expected_triangles >=
        base.attributes.position.count / 3 ||
      base.attributes.position.count % 3
    )
      throw new Error("Invalid source roof trim contract.");
    const pos = base.attributes.position,
      keep = [];
    let removed = 0;
    for (let i = 0; i < pos.count; i += 3) {
      if ([i, i + 1, i + 2].every((v) => pos.getY(v) >= spec.trim_source_min_y))
        removed++;
      else keep.push(i, i + 1, i + 2);
    }
    if (removed !== spec.trim_source_expected_triangles) {
      base.dispose();
      throw new Error("Source roof triangle match changed.");
    }
    const filtered = new THREE.BufferGeometry();
    for (const [name, attr] of Object.entries(base.attributes)) {
      if (attr.isInterleavedBufferAttribute || attr.count !== pos.count) {
        base.dispose();
        throw new Error("Unsupported source roof attributes.");
      }
      const out = new attr.array.constructor(keep.length * attr.itemSize);
      for (let k = 0; k < keep.length; k++)
        for (let c = 0; c < attr.itemSize; c++)
          out[k * attr.itemSize + c] = attr.array[keep[k] * attr.itemSize + c];
      filtered.setAttribute(
        name,
        new THREE.BufferAttribute(out, attr.itemSize, attr.normalized),
      );
    }
    base.dispose();
    base = filtered;
  }
  const extra = b.index ? b.toNonIndexed() : b.clone();
  const combined = mergeGeometries([base, extra]);
  base.dispose();
  extra.dispose();
  if (!combined) throw new Error("Incompatible building detail geometry.");
  target.geometry = combined;
  part.geometry.dispose();
  part.material.dispose();
  detail.remove(part);
  detail.removeFromParent();
}

// Combine matching, static, non-selectable detail meshes at the same site.
// Building meshes remain separate, preserving selection and collision identity.
export function mergeLocalDetailKind(first, second, kind) {
  if (
    !["vegetation", "prop"].includes(kind) ||
    !first?.parent ||
    first.parent !== second?.parent
  )
    throw new Error("Invalid local detail merge target.");
  const find = (group) =>
    group.children.filter(
      (child) =>
        child.isMesh &&
        child.name === `exterior-detail-${kind}` &&
        child.userData.asset_kind === kind &&
        !child.userData.asset_id,
    );
  const a = find(first),
    b = find(second);
  if (a.length !== 1 || b.length !== 1)
    throw new Error("Ambiguous local detail mesh.");
  for (const object of [first, second, a[0], b[0]]) {
    object.updateMatrix();
    if (
      !object.matrix.equals(new THREE.Matrix4()) ||
      object.animations.length ||
      !object.visible
    )
      throw new Error(
        "Local detail must have an identity transform and be static.",
      );
  }
  for (const mesh of [a[0], b[0]]) {
    const m = mesh.material;
    if (
      Array.isArray(m) ||
      !m.isMeshStandardMaterial ||
      !m.vertexColors ||
      m.map ||
      m.roughness !== 0.87 ||
      m.transparent ||
      m.side !== THREE.FrontSide
    )
      throw new Error("Incompatible local detail material.");
  }
  const merged = mergeGeometries([a[0].geometry, b[0].geometry]);
  if (!merged) throw new Error("Incompatible local detail geometry.");
  a[0].geometry.dispose();
  a[0].geometry = merged;
  b[0].geometry.dispose();
  b[0].material.dispose();
  second.remove(b[0]);
}

// Merge a source-pinned, single-material environment layer into its original
// batch, preserving the scene draw-call budget and the target's material.
export function mergeEnvironmentDetail(root, detail, spec) {
  const contracts = {
    furniture_1: {
      parent: "furniture",
      color: "77634f",
      material: "bench-wood",
      count: 432,
    },
    furniture_2: {
      parent: "furniture",
      color: "3f514b",
      material: "lamp-metal",
      count: 960,
    },
    understory_2: {
      parent: "understory",
      color: "829e59",
      material: "fern-green",
      count: 264,
    },
  };
  const contract = contracts[spec.merge_target];
  if (
    spec.scope !== "environment" ||
    !contract ||
    spec.objects.some((item) => item.material !== contract.material)
  )
    throw new Error("Invalid environment merge contract.");
  const target = root.getObjectByName(spec.merge_target);
  const child = detail.children[0];
  if (
    !target?.isMesh ||
    target.parent?.name !== contract.parent ||
    Array.isArray(target.material) ||
    target.material.color.getHexString() !== contract.color ||
    detail.children.length !== 1 ||
    !child?.isMesh ||
    target.geometry.attributes.position.count !== contract.count
  )
    throw new Error("Environment merge target changed.");
  root.updateMatrixWorld(true);
  const matrix = target.matrixWorld
    .clone()
    .invert()
    .multiply(child.matrixWorld);
  const base = target.geometry.index
    ? target.geometry.toNonIndexed()
    : target.geometry.clone();
  const extra = child.geometry.clone().applyMatrix4(matrix);
  extra.deleteAttribute("color");
  const combined = mergeGeometries([base, extra]);
  base.dispose();
  extra.dispose();
  if (!combined) throw new Error("Environment geometry could not be merged.");
  target.geometry.dispose();
  target.geometry = combined;
  child.geometry.dispose();
  child.material.dispose();
  detail.removeFromParent();
}
