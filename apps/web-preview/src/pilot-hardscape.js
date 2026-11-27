// SPDX-License-Identifier: Apache-2.0
import { BufferAttribute, Raycaster, Vector3 } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { readPinnedScene } from "./pinned-scene.js";

const directory = "pilot-hardscape-review";

function validBox(box) {
  return (
    Array.isArray(box) &&
    box.length === 4 &&
    box.every((value) => Number.isFinite(value) && Math.abs(value) < 1000) &&
    box[0] < box[2] &&
    box[1] < box[3] &&
    box[2] - box[0] < 32 &&
    box[3] - box[1] < 32
  );
}

function stageCut(root, cut) {
  const target = root.getObjectByName(cut.target);
  const matches = (target?.isMesh ? [target] : (target?.children ?? [])).filter(
    (node) =>
      node.isMesh &&
      node.geometry.attributes.position?.count === cut.vertices &&
      node.geometry.index?.count === 3 * cut.triangles &&
      (!cut.material || node.material.name === cut.material),
  );
  if (matches.length !== 1 || !cut.spans.length || !cut.anchors.length)
    throw Error("The source hardscape primitive changed.");
  const geometry = matches[0].geometry;
  const position = geometry.attributes.position;
  const source = geometry.index.array;
  let previous = 0;
  const ranges = cut.spans.map(([start, end]) => {
    if (
      !Number.isInteger(start) ||
      !Number.isInteger(end) ||
      start < previous ||
      start >= end ||
      end > cut.triangles
    )
      throw Error("Invalid source hardscape triangle range.");
    previous = end;
    return [start * 3, end * 3];
  });
  for (const [slot, id, xyz] of cut.anchors) {
    if (
      source[slot] !== id ||
      !ranges.some(([start, end]) => slot >= start && slot < end) ||
      position.getX(id) !== xyz[0] ||
      position.getY(id) !== xyz[1] ||
      position.getZ(id) !== xyz[2]
    )
      throw Error("A source hardscape anchor changed.");
  }
  const index = source.filter(
    (_, slot) => !ranges.some(([start, end]) => slot >= start && slot < end),
  );
  if (!index.length) throw Error("The source hardscape patch is empty.");
  return { geometry, index: new BufferAttribute(index, 1) };
}

export function sampleSurface(mesh, bounds) {
  const ray = new Raycaster();
  const from = new Vector3();
  const down = new Vector3(0, -1, 0);
  return (x, z) => {
    if (
      !bounds.some(
        ([left, south, right, north]) =>
          x >= left && x <= right && -z >= south && -z <= north,
      )
    )
      return undefined;
    ray.set(from.set(x, 32, z), down);
    return ray.intersectObject(mesh, false)[0]?.point.y;
  };
}

export async function installPilotHardscape(root, base, config, reviews) {
  const descriptor = config.pilot_hardscape_site;
  if (!descriptor) return null;
  try {
    if (
      config.verify_source_sha256 !== true ||
      descriptor.url !== `${directory}/site.json`
    )
      throw Error("Invalid pilot hardscape descriptor.");
    const data = JSON.parse(
      new TextDecoder().decode(
        await readPinnedScene(base + descriptor.url, descriptor.sha256),
      ),
    );
    const { collision_boxes_enu_m: boxes, walkable_bounds_enu_m: bounds } =
      data;
    if (
      data.source_art_sha256 !== config.asset_sha256 ||
      data.url !== `${directory}/site.glb` ||
      Object.entries(data.related_models).length !== 3 ||
      Object.entries(data.related_models).some(
        ([id, hash]) =>
          !reviews.some(
            (review) => review.ids.includes(id) && review.assetSha === hash,
          ),
      ) ||
      !Array.isArray(data.cuts) ||
      data.cuts.length !== 4 ||
      !Array.isArray(boxes) ||
      boxes.length !== 6 ||
      !boxes.every(validBox) ||
      !Array.isArray(bounds) ||
      bounds.length !== 4 ||
      !bounds.every(validBox)
    )
      throw Error(
        "Pilot hardscape assets do not match their verified sources.",
      );
    const bytes = await readPinnedScene(base + data.url, data.sha256);
    const { scene } = await new GLTFLoader().parseAsync(bytes, base);
    const surface = scene.getObjectByName("hardscape-walkable");
    if (
      !surface?.isMesh ||
      surface.userData.asset_kind !== "landscape-surface" ||
      !scene.getObjectByName("hardscape-detail")?.isMesh
    )
      throw Error("Missing pilot hardscape meshes.");
    const cuts = data.cuts.map((cut) => stageCut(root, cut));
    if (new Set(cuts.map(({ geometry }) => geometry)).size !== cuts.length)
      throw Error("Duplicate source hardscape primitive.");
    for (const { geometry, index } of cuts) geometry.setIndex(index);
    root.add(scene);
    return { boxes, height: sampleSurface(surface, bounds) };
  } catch (error) {
    console.warn(
      "Pilot hardscape unavailable; retaining the preceding site.",
      error,
    );
    return null;
  }
}
