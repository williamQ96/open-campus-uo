// SPDX-License-Identifier: Apache-2.0
import { BufferAttribute } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import {
  recordContextOmissions,
  retainedContextRange,
} from "./context-roof-refinements.js";
import {
  isFootprintRing as polygon,
  readPinnedScene as readPinned,
} from "./pinned-scene.js";

const cascadeId = "roof-f42d2ea3";
const volcanologyId = "roof-399a0551";
const ids = [cascadeId, volcanologyId];
const siteUrl = "cascade-volcanology-review/site.json";
const meshUrl = "cascade-volcanology-review/site.glb";

export async function loadCascadeVolcanologyReview(base, manifest, config) {
  const descriptor = config.cascade_volcanology_site;
  if (!config.verify_source_sha256 || descriptor.url !== siteUrl)
    throw new Error("Invalid Cascade site descriptor.");
  const site = JSON.parse(
    new TextDecoder().decode(
      await readPinned(base + siteUrl, descriptor.sha256),
    ),
  );
  const batch = site.volcanology_batch;
  if (
    site.url !== meshUrl ||
    site.source_presentation_sha256 !== config.asset_sha256 ||
    site.source_base_model_sha256 !== manifest.model.sha256 ||
    batch?.name !== "context-campus-1-2" ||
    batch.vertex_count !== 8909 ||
    batch.index_count !== 13947 ||
    batch.remove_triangles?.join(",") !== "1172,1608" ||
    site.buildings?.length !== ids.length
  )
    throw new Error("Cascade site does not match the scene.");

  const replacements = new Map(site.buildings.map((item) => [item.id, item]));
  for (const [i, id] of ids.entries()) {
    const item = replacements.get(id);
    const door = item?.entrances?.[0];
    const supports = item?.support_collision_enu_m ?? [];
    if (
      !manifest.buildings.some((building) => building.id === id) ||
      !polygon(item?.footprint_enu_m) ||
      !Number.isFinite(item.roof_z_m) ||
      item.entrances?.length !== 1 ||
      door?.gate !== ["cascade-courtyard", "volcanology-south"][i] ||
      door.outward_degrees !== 180 ||
      door.position_enu_m?.length !== 2 ||
      !door.position_enu_m.every(Number.isFinite) ||
      supports.length !== (i === 0 ? 2 : 0) ||
      !supports.every(polygon)
    )
      throw new Error("Invalid Cascade building, entrance or bridge supports.");
  }
  const [glb] = await Promise.all([
    readPinned(base + meshUrl, site.sha256),
    readPinned(base + manifest.heightfield_url, site.source_heightfield_sha256),
  ]);
  const { scene } = await new GLTFLoader().parseAsync(glb, base);
  const link = scene.getObjectByName("cascade-link");
  const courtyard = scene.getObjectByName("cascade-courtyard");
  if (
    !link?.isMesh ||
    !courtyard?.isMesh ||
    ids.some((id) => {
      const mesh = scene.getObjectByName(id);
      return !mesh?.isMesh || mesh.userData.asset_id !== id;
    })
  )
    throw new Error("Cascade review nodes are missing.");

  return {
    link,
    courtyard,
    entrances: Object.fromEntries(
      site.buildings.map((item) => [item.id, item.entrances]),
    ),
    buildingRecords(buildings) {
      return buildings.map((record) => {
        const item = replacements.get(record.id);
        return item
          ? {
              ...record,
              footprint_enu_m: item.footprint_enu_m,
              roof_z_m: item.roof_z_m,
              height_m: item.roof_z_m - record.base_z_m,
              collision_extra_enu_m: item.support_collision_enu_m,
            }
          : record;
      });
    },
    install(root, oldOverlay) {
      const old = root.getObjectByName(cascadeId);
      const oldBatch = root.getObjectByName(batch.name);
      const geometry = oldBatch?.geometry;
      const indices = geometry?.index?.array;
      const members = oldBatch?.userData.asset_ids;
      const range =
        geometry &&
        retainedContextRange(
          geometry,
          batch.remove_triangles,
          batch.index_count / 3,
        );
      if (
        !old?.isMesh ||
        old.userData.asset_id !== cascadeId ||
        oldOverlay?.parent !== root ||
        (geometry?.getAttribute("position")?.count ?? 0) < batch.vertex_count ||
        geometry?.groups.length !== 0 ||
        !indices ||
        !range ||
        !members?.includes(volcanologyId)
      )
        throw new Error(
          "The source Cascade mesh or Volcanology batch changed.",
        );

      const [from, to] = range.map((triangle) => triangle * 3);
      const kept = new indices.constructor(indices.length - (to - from));
      kept.set(indices.subarray(0, from));
      kept.set(indices.subarray(to), from);
      // Verify all inputs before changing any visible or collision geometry.
      oldBatch.geometry.setIndex(new BufferAttribute(kept, 1));
      recordContextOmissions(geometry, batch.index_count / 3, [
        batch.remove_triangles,
      ]);
      oldBatch.userData.asset_ids = members.filter(
        (id) => id !== volcanologyId,
      );
      old.removeFromParent();
      oldOverlay.removeFromParent();
      root.add(scene);
    },
  };
}
