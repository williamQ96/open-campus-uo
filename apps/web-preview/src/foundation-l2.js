// SPDX-License-Identifier: Apache-2.0
import { Matrix4, Vector3 } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { readPinnedScene } from "./pinned-scene.js";
import { sampleGround } from "./world.js";
import { restoreFoundationLawns } from "./foundation-lawn-corrections.js";

export async function loadFoundationL2(base, manifest, config, exteriorReview) {
  const recipe = config.landcover_l2;
  if (
    recipe.url !== "landcover-l2/ground.glb" ||
    recipe.source_model_sha256 !== manifest.model.sha256 ||
    recipe.source_landcover_sha256 !== config.landcover_sha256 ||
    manifest.heightfield_url !== "heightfield.json"
  )
    throw new Error("Ground refinement does not match the source scene.");

  const sourceField =
    exteriorReview?.sourceHeightfieldSha256 === recipe.source_heightfield_sha256
      ? exteriorReview.sourceField
      : readPinnedScene(
          base + manifest.heightfield_url,
          recipe.source_heightfield_sha256,
        ).then((bytes) => JSON.parse(new TextDecoder().decode(bytes)));
  const [bytes, field] = await Promise.all([
    readPinnedScene(base + recipe.url, recipe.sha256),
    sourceField,
  ]);
  const { scene } = await new GLTFLoader().parseAsync(bytes, base);
  const parts = scene.getObjectsByProperty("isMesh", true);
  const ground = parts[0];
  const { nx, ny, min_east_m, min_north_m, spacing_m, heights_m } = field;
  const positions = ground?.geometry.getAttribute("position");
  const offset = ground?.userData.heightfield_offset_m;
  if (
    parts.length !== 1 ||
    ground.userData.surface_layer !== "foundation" ||
    offset !== 0.018 ||
    positions?.count !== nx * ny ||
    heights_m.length !== positions.count ||
    ground.geometry.index?.count !== (nx - 1) * (ny - 1) * 6
  )
    throw new Error("Ground refinement has an invalid mesh grid.");
  const deltas = heights_m.map((height, i) => {
    const east = min_east_m + (i % nx) * spacing_m;
    const north = min_north_m + Math.floor(i / nx) * spacing_m;
    const delta = Math.round((positions.getY(i) - height - offset) * 1e4) / 1e4;
    if (
      positions.getX(i) !== east ||
      positions.getZ(i) !== -north ||
      !Number.isFinite(delta) ||
      Math.abs(delta) > 1.2 ||
      (exteriorReview &&
        exteriorReview.field.heights_m[i] !== height &&
        delta !== 0)
    )
      throw new Error(
        "Ground refinement changes a protected or out-of-bounds vertex.",
      );
    return delta;
  });
  ground.userData.context_haze_weight = 0.48;
  ground.userData.correctedLawnVertices = restoreFoundationLawns(
    ground.geometry,
  );
  return { scene, grade: { ...field, heights_m: deltas } };
}

export function applyFoundationGrade(root, field, grade) {
  if (!grade) return field;
  const mesh = root
    .getObjectsByProperty("isMesh", true)
    .find((part) => part.userData.asset_kind === "terrain");
  mesh.updateWorldMatrix(true, false);
  const point = new Vector3();
  const inverse = new Matrix4().copy(mesh.matrixWorld).invert();
  const positions = mesh.geometry.getAttribute("position");
  for (let i = 0; i < positions.count; i++) {
    point.fromBufferAttribute(positions, i).applyMatrix4(mesh.matrixWorld);
    const delta = sampleGround(grade, point.x, point.z);
    if (delta === 0) continue;
    point.y += delta;
    point.applyMatrix4(inverse);
    positions.setXYZ(i, point.x, point.y, point.z);
  }
  positions.needsUpdate = true;
  mesh.geometry.computeBoundingBox();
  mesh.geometry.computeBoundingSphere();
  return {
    ...field,
    heights_m: field.heights_m.map((height, i) => height + grade.heights_m[i]),
  };
}
