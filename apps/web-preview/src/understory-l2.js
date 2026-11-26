// SPDX-License-Identifier: Apache-2.0
import { BufferAttribute } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { readPinnedScene } from "./pinned-scene.js";

const directory = "understory-l2";
const groups = ["planting", "understory_1", "understory_2"];
const sourceFanVertices = 264;
const existingFernVertices = 6120;

function visibleGroups(mesh, contract, fans) {
  const [count, stride, indices] = contract;
  const geometry = mesh.geometry;
  const position = geometry.attributes.position;
  const active = new Uint16Array(count);
  if (
    !position ||
    position.count !== count * stride + (fans ? existingFernVertices : 0) ||
    (fans ? !!geometry.index : !geometry.index)
  )
    throw Error("Legacy understory geometry changed.");
  const array = geometry.index?.array;
  const limit = fans ? sourceFanVertices : array.length;
  for (let i = 0; i < limit; i += 3) {
    const a = array?.[i] ?? i;
    const b = array?.[i + 1] ?? i + 1;
    const c = array?.[i + 2] ?? i + 2;
    const group = Math.floor(a / stride);
    if (
      group >= count ||
      Math.floor(b / stride) !== group ||
      Math.floor(c / stride) !== group
    )
      throw Error("Legacy understory indices cross plant bounds.");
    active[group] += 3;
  }
  if (active.some((size) => size !== 0 && size !== indices))
    throw Error("Legacy understory has an incomplete plant.");
  return Array.from(active, (size, group) => {
    if (!size) return false;
    const first = group * stride;
    const x = position.getX(first);
    const z = position.getZ(first);
    // An older suppression collapses whole plants to a single point.
    for (let i = first + 1; i < first + stride; i++) {
      if (
        Math.abs(position.getX(i) - x) > 0.001 ||
        Math.abs(position.getZ(i) - z) > 0.001
      )
        return true;
    }
    return false;
  });
}

function selectReplacement(mesh, masks, ranges) {
  const geometry = mesh.geometry;
  const index = geometry.index?.array;
  const count = geometry.attributes.position?.count;
  const active = masks.flat();
  if (
    !index ||
    !geometry.attributes.color ||
    ranges.length !== active.length ||
    ranges.at(-1)[0] !== count ||
    ranges.at(-1)[1] !== index.length
  )
    throw Error("Invalid understory replacement batch.");
  const retained = new index.constructor(index.length);
  let start = 0,
    vertexStart = 0,
    write = 0;
  const result = { shrubs: 0, fronds: 0, retainedFernClusters: 3 };
  for (const [i, [vertices, end, include]] of ranges.entries()) {
    if (
      !Number.isInteger(vertices) ||
      !Number.isInteger(end) ||
      vertices <= vertexStart ||
      vertices > count ||
      end <= start ||
      end > index.length ||
      end % 3 !== 0 ||
      typeof include !== "boolean"
    )
      throw Error("Invalid individual understory range.");
    const pick = index.subarray(start, end);
    if (pick.some((v) => v < vertexStart || v >= vertices))
      throw Error("Replacement indices cross plant bounds.");
    if (active[i] && include) {
      retained.set(pick, write);
      write += pick.length;
      if (i < masks[0].length + masks[1].length) result.shrubs++;
      else result.fronds++;
    }
    start = end;
    vertexStart = vertices;
  }
  geometry.setIndex(new BufferAttribute(retained.slice(0, write), 1));
  return result;
}

export async function installUnderstory(root, base, config) {
  const descriptor = config.understory_l2;
  if (!descriptor) return null;
  try {
    if (
      config.verify_source_sha256 !== true ||
      descriptor.url !== `${directory}/plants.json`
    )
      throw Error("Invalid understory descriptor.");
    const data = JSON.parse(
      new TextDecoder().decode(
        await readPinnedScene(base + descriptor.url, descriptor.sha256),
      ),
    );
    const recipes = [
      ...config.additional_environment_patches,
      ...config.additional_tree_suppressions,
      ...["understory_patch", "fern_patch"].map((name) => ({
        url: config[`${name}_url`],
        sha256: config[`${name}_sha256`],
      })),
    ];
    if (
      data.source_art_sha256 !== config.asset_sha256 ||
      data.url !== `${directory}/plants.glb` ||
      !Object.entries(data.source_recipes).every(([url, sha256]) =>
        recipes.some((entry) => entry.url === url && entry.sha256 === sha256),
      )
    )
      throw Error("Understory source recipes changed.");
    const legacy = groups.map((name) => root.getObjectByName(name));
    const masks = legacy.map((mesh, i) =>
      visibleGroups(mesh, data.source_ranges[groups[i]], i === 2),
    );
    const bytes = await readPinnedScene(base + data.url, data.sha256);
    const { scene } = await new GLTFLoader().parseAsync(bytes, base);
    const replacement = scene.getObjectByName("understory-rebuilt");
    if (
      !replacement?.isMesh ||
      !scene.getObjectByName("understory-planting-beds")?.isMesh
    )
      throw Error("Missing understory mesh.");
    const result = selectReplacement(replacement, masks, data.ranges);
    legacy[0].visible = false;
    legacy[1].visible = false;
    legacy[2].geometry.setDrawRange(sourceFanVertices, existingFernVertices);
    root.add(scene);
    return result;
  } catch (error) {
    console.warn(
      "Understory unavailable; retaining the preceding planting.",
      error,
    );
    return null;
  }
}
