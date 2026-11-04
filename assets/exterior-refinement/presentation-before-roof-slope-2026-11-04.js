// SPDX-License-Identifier: Apache-2.0
// Optional authored art layer. It never rewrites the measured scene manifest.
import * as THREE from "three";
import { applyWallColorPatch } from "./wall-color-patch.js";
import { applyVegetationPatch } from "./vegetation-patch.js";
import { applyCanopyTone } from "./canopy-tone.js";
import { installExteriorDetail, mergeEnvironmentDetail, mergeLocalDetailKind, mergeBuildingDetailIntoSource } from "./exterior-detail.js";
import { collisionBoxesForDetail } from "./collision-supplement.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { applySurfaceGrain } from "./surface-grain.js";
import { createContextFog } from "./context-fog.js";

export function sceneAssetUrl(base, name) {
  if (
    typeof name !== "string" ||
    !/^[\w./-]+$/.test(name) ||
    name.startsWith("/") ||
    name.split("/").includes("..")
  )
    throw new Error("Presentation asset must stay inside the scene directory.");
  return base + name;
}

export function setEmissive(object, color) {
  object?.traverse((child) => {
    if (!child.isMesh) return;
    for (const material of Array.isArray(child.material)
      ? child.material
      : [child.material])
      material.emissive?.setHex(color);
  });
}

export async function loadPresentation(base, name, buildingIds) {
  const response = await fetch(sceneAssetUrl(base, name));
  if (!response.ok)
    throw new Error("Could not load presentation: " + response.status);
  const config = await response.json();
  if (config.version !== 1 || !Array.isArray(config.replaces_building_ids))
    throw new Error("Unsupported presentation contract.");
  for (const id of config.replaces_building_ids)
    if (!buildingIds.has(id))
      throw new Error("Unknown presentation building: " + id);
  const gltf = await new GLTFLoader().loadAsync(
    sceneAssetUrl(base, config.asset_url),
  );
  const wallPatches = config.wall_color_patches ?? [];
  if (!Array.isArray(wallPatches) || wallPatches.some(entry => !entry || typeof entry.url !== "string") || new Set(wallPatches.map(entry => entry.url)).size !== wallPatches.length)
    throw new Error("Invalid wall color patches.");
  for (const entry of wallPatches) {
    const result = await fetch(sceneAssetUrl(base, entry.url));
    if (!result.ok) throw new Error("Could not load wall color patch: " + result.status);
    applyWallColorPatch(gltf.scene, await result.json(), config.asset_sha256);
  }
  const extraPatches = config.additional_environment_patches ?? [];
  if (!Array.isArray(extraPatches) || extraPatches.some((entry) => !entry || typeof entry.url !== "string") ||
      new Set(extraPatches.map((entry) => entry.url)).size !== extraPatches.length)
    throw new Error("Invalid additional environment patches.");
  for (const patchUrl of [
    config.vegetation_patch_url,
    config.understory_patch_url,
    config.furniture_patch_url,
    config.fern_patch_url,
    config.tree_suppression_url,
    ...(config.additional_tree_suppressions || []).map((entry) => entry.url),
    ...extraPatches.map((entry) => entry.url),
  ]) {
    if (!patchUrl) continue;
    const result = await fetch(sceneAssetUrl(base, patchUrl));
    if (!result.ok)
      throw new Error("Could not load vegetation patch: " + result.status);
    const patch = await result.json();
    if (patch.operation === "canopy-tone-v1") applyCanopyTone(gltf.scene, patch, config.asset_sha256);
    else applyVegetationPatch(gltf.scene, patch, config.asset_sha256);
  }
  const detailUrls = [
    ...(config.exterior_detail_url ? [config.exterior_detail_url] : []),
    ...(config.exterior_details || []).map((entry) => entry.url),
  ];
  if (new Set(detailUrls).size !== detailUrls.length)
    throw new Error("Duplicate exterior detail layer.");
  const collisionSupplements = [];
  const localDetails = new Map();
  for (const detailUrl of detailUrls) {
    const result = await fetch(sceneAssetUrl(base, detailUrl));
    if (!result.ok)
      throw new Error("Could not load exterior detail: " + result.status);
    const detail = await result.json();
    const boxes = collisionBoxesForDetail(detail);
    const installed = installExteriorDetail(gltf.scene, detail, config.asset_sha256, buildingIds);
    if (detail.merge_target) mergeEnvironmentDetail(gltf.scene, installed, detail);
    if (detail.merge_source_vertex_count !== undefined) mergeBuildingDetailIntoSource(gltf.scene, installed, detail);
    if (["anstett-south-detail.json", "anstett-lamps-detail.json", "chapman-west-detail.json", "tykeson-north-detail.json", "fenton-south-detail.json", "condon-east-detail.json", "peterson-south-detail.json"].includes(detailUrl)) {
      const expectedId = detailUrl === "chapman-west-detail.json" ? "roof-f5cea51d" : detailUrl === "tykeson-north-detail.json" ? "context-b0103" : detailUrl === "fenton-south-detail.json" ? "roof-4f0c798e" : detailUrl === "condon-east-detail.json" ? "roof-7ffcf31b" : detailUrl === "peterson-south-detail.json" ? "roof-75e776d0" : "roof-0a498bf7";
      if (detail.building_id !== expectedId) throw new Error("Local detail identity changed.");
      localDetails.set(detailUrl, installed);
    }
    if (boxes.length)
      collisionSupplements.push({ buildingId: detail.building_id, boxes });
  }
  if (localDetails.has("anstett-south-detail.json") && localDetails.has("anstett-lamps-detail.json")) {
    const first = localDetails.get("anstett-south-detail.json");
    const second = localDetails.get("anstett-lamps-detail.json");
    mergeLocalDetailKind(first, second, "vegetation");
    mergeLocalDetailKind(first, second, "prop");
  }
  // Two nearby, non-selectable planting layers share the same material contract.
  if (localDetails.has("anstett-south-detail.json") && localDetails.has("chapman-west-detail.json")) {
    mergeLocalDetailKind(localDetails.get("anstett-south-detail.json"), localDetails.get("chapman-west-detail.json"), "vegetation");
  }
  // Consolidate two nearby non-selectable planting layers without merging buildings.
  if (localDetails.has("tykeson-north-detail.json") && localDetails.has("fenton-south-detail.json")) {
    mergeLocalDetailKind(localDetails.get("tykeson-north-detail.json"), localDetails.get("fenton-south-detail.json"), "vegetation");
  }
  // Nearby generic planting remains independently source-pinned and non-selectable.
  if (localDetails.has("condon-east-detail.json") && localDetails.has("peterson-south-detail.json")) {
    mergeLocalDetailKind(localDetails.get("condon-east-detail.json"), localDetails.get("peterson-south-detail.json"), "vegetation");
  }
  if (config.landcover_url) {
    const land = await new GLTFLoader().loadAsync(
      sceneAssetUrl(base, config.landcover_url),
    );
    gltf.scene.add(land.scene);
  }
  return createPresentation(gltf.scene, config, collisionSupplements);
}

export function createPresentation(root, config, collisionSupplements = []) {
  const groups = new Map();
  const batchedIds = new Set();
  const contextFog = createContextFog(config.context_fog);
  const collisionMeshes = [];
  const materials = [];
  let hasFoundation = false;
  const ramp = new THREE.DataTexture(
    new Uint8Array([105, 185, 255]),
    3,
    1,
    THREE.RedFormat,
  );
  ramp.minFilter = ramp.magFilter = THREE.NearestFilter;
  ramp.needsUpdate = true;
  root.traverse((object) => {
    if (!object.isMesh) return;
    for (
      let parent = object.parent;
      parent && !object.userData.asset_kind;
      parent = parent.parent
    )
      if (parent.userData.asset_kind)
        object.userData = { ...parent.userData, ...object.userData };
    object.castShadow = object.userData.asset_kind !== "landscape-surface";
    object.receiveShadow = true;
    const original = Array.isArray(object.material)
      ? object.material.map((material) => material.clone())
      : object.material.clone();
    const toToon = (source) =>
      new THREE.MeshToonMaterial({
        color: source.color.clone(),
        gradientMap: ramp,
        side: source.side,
        map: source.map,
        vertexColors: source.vertexColors,
      });
    const toon = Array.isArray(original)
      ? original.map(toToon)
      : toToon(original);
    for (const material of [original, toon].flat()) {
      contextFog?.apply(material);
      if (object.userData.surface_grain)
        applySurfaceGrain(material, object.userData.surface_grain);
    }
    materials.push({ object, original, toon });
    object.material = toon;
    if (object.userData.asset_kind === "landscape-surface") {
      for (const material of [original, toon].flat()) {
        material.polygonOffset = true;
        const foundation = object.userData.surface_layer === "foundation";
        hasFoundation ||= foundation;
        material.polygonOffsetFactor = foundation ? -0.1 : -2;
        material.polygonOffsetUnits = foundation ? -0.25 : -4;
      }
    }
    const id = object.userData.asset_id;
    if (object.userData.asset_kind === "context-building-batch") {
      if (!Array.isArray(object.userData.asset_ids))
        throw Error("Missing batch identities");
      for (const batchId of object.userData.asset_ids) {
        if (!config.replaces_building_ids.includes(batchId))
          throw Error("Unregistered context building: " + batchId);
        batchedIds.add(batchId);
      }
      collisionMeshes.push(object);
    }
    if (id && object.userData.asset_kind === "building") {
      if (!config.replaces_building_ids.includes(id))
        throw new Error("Unregistered authored building: " + id);
      if (!groups.has(id)) groups.set(id, new THREE.Group());
      groups.get(id).add(object.clone());
      collisionMeshes.push(object);
    }
  });
  // Groups reference the same materials, while original nodes retain their exported transforms.
  for (const id of config.replaces_building_ids)
    if (!groups.has(id) && !batchedIds.has(id))
      throw new Error("Missing authored building geometry: " + id);
  return {
    root,
    config,
    groups,
    batchedIds,
    contextFog,
    collisionMeshes,
    collisionSupplements,
    hasFoundation,
    bakeStaticHaze() {
      for (const entry of materials)
        contextFog?.bakeMesh(entry.object, [entry.original, entry.toon].flat());
    },
    setToon(enabled) {
      for (const entry of materials) {
        const wireframe = [entry.object.material].flat()[0].wireframe;
        entry.object.material = enabled ? entry.toon : entry.original;
        for (const material of [entry.object.material].flat())
          material.wireframe = wireframe;
      }
      // Selection uses actual scene meshes in either material mode.
      for (const [id, group] of groups) {
        group.clear();
        for (const object of collisionMeshes)
          if (object.userData.asset_id === id) group.add(object.clone());
      }
    },
  };
}
