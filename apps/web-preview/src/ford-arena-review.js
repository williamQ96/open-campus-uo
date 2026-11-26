// SPDX-License-Identifier: Apache-2.0
import { Matrix4, Vector3 } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { isFootprintRing } from "./pinned-scene.js";
import { insidePolygon, sampleGround } from "./world.js";

const buildings = new Map([
  ["context-b0066", "ford-alumni-detail.json"],
  ["context-b0074", "arena-north-detail.json"],
]);
const gates = new Map([
  ["context-b0066", ["plaza"]],
  ["context-b0074", ["north", "east", "west"]],
]);

async function pinned(url, expected) {
  const response = await fetch(url);
  if (!response.ok) throw new Error("Could not load Ford/Arena review asset.");
  const bytes = await response.arrayBuffer();
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  const actual = Array.from(new Uint8Array(digest), (v) =>
    v.toString(16).padStart(2, "0"),
  ).join("");
  if (actual !== expected) throw new Error("Ford/Arena review asset changed.");
  return bytes;
}

export async function loadFordArenaReview(base, manifest, descriptor) {
  if (descriptor.url !== "ford-arena-review/site.json")
    throw new Error("Invalid Ford/Arena site path.");
  const site = JSON.parse(
    new TextDecoder().decode(
      await pinned(base + descriptor.url, descriptor.sha256),
    ),
  );
  const field = JSON.parse(
    new TextDecoder().decode(
      await pinned(
        base + manifest.heightfield_url,
        site.source_heightfield_sha256,
      ),
    ),
  );
  const { row, column, deltas_m: rows } = site.grade;
  const width = rows[0]?.length;
  if (
    site.source_model_sha256 !== manifest.model.sha256 ||
    field.heights_m.length !== field.nx * field.ny ||
    !Number.isInteger(row) ||
    !Number.isInteger(column) ||
    row < 0 ||
    column < 0 ||
    rows.length < 2 ||
    width < 2 ||
    row + rows.length > field.ny ||
    column + width > field.nx ||
    rows.some(
      (line, i) =>
        line.length !== width ||
        !line.every(Number.isFinite) ||
        line[0] !== 0 ||
        line[width - 1] !== 0 ||
        ((i === 0 || i === rows.length - 1) &&
          line.some((delta) => delta !== 0)),
    ) ||
    site.buildings?.length !== buildings.size ||
    new Set(site.buildings.map(({ id }) => id)).size !== buildings.size
  )
    throw new Error("Ford/Arena review does not match the scene.");
  const grade = {
    nx: width,
    ny: rows.length,
    min_east_m: field.min_east_m + column * field.spacing_m,
    min_north_m: field.min_north_m + row * field.spacing_m,
    spacing_m: field.spacing_m,
    heights_m: rows.flat(),
  };
  const maxEast = grade.min_east_m + (grade.nx - 1) * grade.spacing_m;
  const maxNorth = grade.min_north_m + (grade.ny - 1) * grade.spacing_m;
  const offsetAt = (x, z) =>
    x < grade.min_east_m ||
    x > maxEast ||
    -z < grade.min_north_m ||
    -z > maxNorth
      ? 0
      : sampleGround(grade, x, z);
  const adjustedField = { ...field, heights_m: [...field.heights_m] };
  rows.forEach((line, j) =>
    line.forEach((delta, i) => {
      const index = (row + j) * field.nx + column + i;
      adjustedField.heights_m[index] += delta;
    }),
  );
  const loader = new GLTFLoader();
  const ground = site.frontage_ground;
  if (
    ground?.url !== "ford-arena-review/frontage-ground.glb" ||
    ground.paved_areas_enu_m?.length !== 4
  )
    throw new Error("Missing Ford/Arena frontage ground.");
  const groundScene = await loader.parseAsync(
    await pinned(base + ground.url, ground.sha256),
    base,
  );
  const frontage = groundScene.scene.getObjectByName(
    "ford-arena-frontage-ground",
  );
  if (!frontage?.isMesh)
    throw new Error("Missing Ford/Arena frontage geometry.");
  frontage.userData = {
    asset_kind: "landscape-surface",
    surface_layer: "hardscape",
    surface_grain: 0.09,
  };
  const replacements = await Promise.all(
    site.buildings.map(async (entry) => {
      const plazaCollision = entry.collision_extra_enu_m ?? [];
      if (
        !buildings.has(entry.id) ||
        !/^ford-arena-review\/[a-z-]+-site\.glb$/.test(entry.url) ||
        !entry.footprint_enu_m ||
        entry.footprint_enu_m.length < 3 ||
        !entry.footprint_enu_m.every(
          (p) => p.length === 2 && p.every(Number.isFinite),
        ) ||
        !Array.isArray(plazaCollision) ||
        !plazaCollision.every(isFootprintRing) ||
        ![entry.base_z_m, entry.roof_z_m].every(Number.isFinite) ||
        entry.entrances?.length !== gates.get(entry.id)?.length ||
        entry.entrances.some(
          (door, index) =>
            door.gate !== gates.get(entry.id)[index] ||
            door.estimated !== true ||
            door.position_enu_m?.length !== 2 ||
            ![...door.position_enu_m, door.outward_degrees].every(
              Number.isFinite,
            ),
        )
      )
        throw new Error("Invalid Ford/Arena review building.");
      const gltf = await loader.parseAsync(
        await pinned(base + entry.url, entry.sha256),
        base,
      );
      const mesh = gltf.scene.getObjectByName(entry.id);
      if (!mesh?.isMesh) throw new Error("Missing Ford/Arena review mesh.");
      return { ...entry, mesh, plazaCollision };
    }),
  );
  return {
    field: adjustedField,
    entrances: Object.fromEntries(
      replacements.map(({ id, entrances }) => [id, entrances]),
    ),
    frontage,
    async loadSource(url, sha256, base) {
      return loader.parseAsync(await pinned(url, sha256), base);
    },
    skippedDetails: new Set(buildings.values()),
    buildingRecords: manifest.buildings.map((record) => {
      const entry = replacements.find(({ id }) => id === record.id);
      if (!entry) return record;
      const { footprint_enu_m, base_z_m, roof_z_m, plazaCollision } = entry;
      return {
        ...record,
        footprint_enu_m,
        base_z_m,
        roof_z_m,
        height_m: roof_z_m - base_z_m,
        collision_extra_enu_m: plazaCollision,
      };
    }),
    replaceBuildings(root, config) {
      if (
        !config.verify_source_sha256 ||
        config.asset_sha256 !== site.source_presentation_sha256 ||
        config.landcover_sha256 !== site.source_landcover_sha256
      )
        throw new Error("Ford/Arena review presentation changed.");
      const old = replacements.map(({ id }) => root.getObjectByName(id));
      if (
        old.some(
          (mesh, i) =>
            !mesh?.isMesh || mesh.userData.asset_id !== replacements[i].id,
        )
      )
        throw new Error("Missing source mesh for Ford/Arena review.");
      replacements.forEach(({ mesh, id }, index) => {
        old[index].removeFromParent();
        mesh.userData = { asset_kind: "building", asset_id: id };
        root.add(mesh);
      });
    },
    fitContextTrees(root) {
      const mesh = root.getObjectByName("campus-trees");
      const geometry = mesh?.geometry;
      const positions = geometry?.getAttribute("position");
      const index = geometry?.index;
      if (
        !mesh?.userData.contextTrunkVariation ||
        positions?.count !== 55200 ||
        index?.count !== 72000
      )
        throw new Error("Ford/Arena review context trees changed.");
      // The active downstream trunk recipes keep 152 source vertices, 32 new
      // trunk vertices, and 240 indices for each tree in known contiguous spans.
      const removed = new Set();
      const excluded = [
        ...replacements.map(({ footprint_enu_m }) => footprint_enu_m),
        ...ground.paved_areas_enu_m,
      ];
      for (let tree = 0; tree < 300; tree++) {
        const trunk = 45600 + tree * 32;
        const x = (positions.getX(trunk) + positions.getX(trunk + 16)) / 2;
        const z = (positions.getZ(trunk) + positions.getZ(trunk + 16)) / 2;
        if (excluded.some((ring) => insidePolygon(x, -z, ring))) {
          removed.add(tree);
          continue;
        }
        const delta = offsetAt(x, z);
        if (delta === 0) continue;
        for (const [start, length] of [
          [tree * 152, 152],
          [trunk, 32],
        ])
          for (let i = start; i < start + length; i++)
            positions.setY(i, positions.getY(i) + delta);
      }
      if (removed.size)
        geometry.setIndex(
          Array.from(index.array).filter(
            (_, i) => !removed.has(Math.floor(i / 240)),
          ),
        );
      positions.needsUpdate = true;
      geometry.computeBoundingBox();
      geometry.computeBoundingSphere();
      return removed.size;
    },
    fitGrade(root) {
      const point = new Vector3();
      const inverse = new Matrix4();
      root.updateMatrixWorld(true);
      root.traverse((mesh) => {
        if (
          !mesh.isMesh ||
          !["terrain", "corridor", "landscape-surface"].includes(
            mesh.userData.asset_kind,
          )
        )
          return;
        const positions = mesh.geometry.getAttribute("position");
        inverse.copy(mesh.matrixWorld).invert();
        let changed = false;
        for (let i = 0; i < positions.count; i++) {
          point
            .fromBufferAttribute(positions, i)
            .applyMatrix4(mesh.matrixWorld);
          const delta = offsetAt(point.x, point.z);
          if (delta === 0) continue;
          point.y += delta;
          point.applyMatrix4(inverse);
          positions.setXYZ(i, point.x, point.y, point.z);
          changed = true;
        }
        if (!changed) return;
        positions.needsUpdate = true;
        mesh.geometry.computeVertexNormals();
        mesh.geometry.computeBoundingBox();
        mesh.geometry.computeBoundingSphere();
      });
    },
  };
}
