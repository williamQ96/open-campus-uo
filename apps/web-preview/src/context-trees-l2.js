// SPDX-License-Identifier: Apache-2.0
import { BufferAttribute } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { readPinnedScene } from "./pinned-scene.js";

const directory = "context-trees-l2";
const sourceCount = 300;
const canopyVertices = 45600;
const sourceVertices = 55200;
const indicesPerTree = 240;

function retainedSourceTrees(mesh) {
  const index = mesh?.geometry.index;
  if (
    !mesh?.userData.contextTrunkVariation ||
    mesh.geometry.attributes.position?.count !== sourceVertices ||
    !index
  )
    throw Error("Background tree source mesh changed.");
  const counts = new Uint16Array(sourceCount);
  for (const vertex of index.array) {
    if (vertex >= sourceVertices)
      throw Error("Invalid background tree source vertex.");
    const id =
      vertex < canopyVertices
        ? Math.floor(vertex / 152)
        : Math.floor((vertex - canopyVertices) / 32);
    counts[id]++;
  }
  if (counts.some((count) => count !== 0 && count !== indicesPerTree))
    throw Error("Background tree source has incomplete trees.");
  return counts;
}

function fitReplacement(mesh, legacy, ranges) {
  const counts = retainedSourceTrees(legacy);
  const geometry = mesh.geometry;
  const positions = geometry.attributes.position;
  const sourcePositions = legacy.geometry.attributes.position;
  const index = geometry.index?.array;
  if (
    !index ||
    !geometry.attributes.color ||
    ranges.length !== sourceCount ||
    ranges.at(-1)[0] !== positions.count ||
    ranges.at(-1)[1] !== index.length
  )
    throw Error("Invalid replacement tree batch.");
  const retained = new index.constructor(index.length);
  let vertexStart = 0,
    indexStart = 0,
    kept = 0,
    active = 0;
  for (const [id, [vertexEnd, indexEnd, ground]] of ranges.entries()) {
    if (
      !Number.isInteger(vertexEnd) ||
      !Number.isInteger(indexEnd) ||
      vertexEnd <= vertexStart ||
      vertexEnd > positions.count ||
      indexEnd <= indexStart ||
      indexEnd > index.length ||
      indexEnd % 3 !== 0 ||
      !Number.isFinite(ground)
    )
      throw Error("Invalid individual background tree range.");
    const section = index.subarray(indexStart, indexEnd);
    if (section.some((vertex) => vertex < vertexStart || vertex >= vertexEnd))
      throw Error("Background replacement indices cross tree bounds.");
    if (counts[id]) {
      const offset = sourcePositions.getY(canopyVertices + id * 32) - ground;
      if (!Number.isFinite(offset))
        throw Error("Invalid background tree ground offset.");
      if (Math.abs(offset) > 0.00001) {
        for (let v = vertexStart; v < vertexEnd; v++)
          positions.setY(v, positions.getY(v) + offset);
      }
      retained.set(section, kept);
      kept += section.length;
      active++;
    }
    vertexStart = vertexEnd;
    indexStart = indexEnd;
  }
  positions.needsUpdate = true;
  geometry.setIndex(new BufferAttribute(retained.slice(0, kept), 1));
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();
  return active;
}

export async function installContextTrees(root, base, config) {
  const descriptor = config.context_trees_l2;
  if (!descriptor) return 0;
  try {
    if (
      config.verify_source_sha256 !== true ||
      descriptor.url !== `${directory}/trees.json`
    )
      throw Error("Invalid background tree descriptor.");
    const data = JSON.parse(
      new TextDecoder().decode(
        await readPinnedScene(base + descriptor.url, descriptor.sha256),
      ),
    );
    if (
      data.source_art_sha256 !== config.asset_sha256 ||
      data.url !== `${directory}/trees.glb` ||
      !["context_trunks", "context_trunk_variation"].every(
        (name) =>
          data.source_trunk_recipes[config[`${name}_url`]] ===
          config[`${name}_sha256`],
      )
    )
      throw Error("Background tree source recipes changed.");
    const bytes = await readPinnedScene(base + data.url, data.sha256);
    const { scene } = await new GLTFLoader().parseAsync(bytes, base);
    const replacement = scene.getObjectByName("context-trees-rebuilt");
    if (!replacement?.isMesh) throw Error("Missing background tree mesh.");
    const legacy = root.getObjectByName("campus-trees");
    const shown = fitReplacement(replacement, legacy, data.ranges);
    legacy.visible = false;
    root.add(scene);
    return shown;
  } catch (error) {
    console.warn(
      "Background trees unavailable; retaining the preceding tree batch.",
      error,
    );
    return 0;
  }
}
