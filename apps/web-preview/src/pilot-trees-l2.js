// SPDX-License-Identifier: Apache-2.0
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { readPinnedScene } from "./pinned-scene.js";

const directory = "pilot-trees-l2";
const replacementNames = ["pilot-trees-wood", "pilot-trees-foliage"];

export async function installPilotTrees(
  root,
  base,
  config,
  registered,
  removed,
) {
  const descriptor = config.pilot_trees_l2;
  if (!descriptor) return 0;
  try {
    if (
      config.verify_source_sha256 !== true ||
      descriptor.url !== `${directory}/trees.json`
    )
      throw Error("Invalid pilot canopy descriptor.");
    const data = JSON.parse(
      new TextDecoder().decode(
        await readPinnedScene(base + descriptor.url, descriptor.sha256),
      ),
    );
    const legacy = root.getObjectByName("vegetation");
    const recipeEntries = [
      config.registered_pilot_trees,
      ...config.additional_tree_suppressions,
      {
        url: config.vegetation_patch_url,
        sha256: config.vegetation_patch_sha256,
      },
      {
        url: config.tree_suppression_url,
        sha256: config.tree_suppression_sha256,
      },
    ];
    const references = Object.entries(data.source_placement_recipes);
    if (
      data.source_art_sha256 !== config.asset_sha256 ||
      data.url !== `${directory}/trees.glb` ||
      data.tree_count !== 273 ||
      references.length !== recipeEntries.length ||
      references.some(
        ([url, hash]) =>
          !recipeEntries.some(
            (entry) => entry?.url === url && entry.sha256 === hash,
          ),
      ) ||
      registered !== data.active_recipes.registered ||
      removed !== data.active_recipes.removed ||
      legacy?.children.length !== Object.keys(data.source_groups).length ||
      legacy.children.some((node) => {
        const spec = data.source_groups[node.name];
        return (
          !node.isMesh ||
          !spec ||
          node.geometry.attributes.position?.count !== spec.positions ||
          node.geometry.index?.count !== spec.indices
        );
      })
    )
      throw Error("Pilot canopy placement inputs changed.");
    const bytes = await readPinnedScene(base + data.url, data.sha256);
    const { scene } = await new GLTFLoader().parseAsync(bytes, base);
    const nodes = replacementNames.map((name) => scene.getObjectByName(name));
    if (
      nodes.some(
        (node) =>
          !node?.isMesh ||
          !node.geometry.attributes.color ||
          node.userData.asset_kind !== "vegetation",
      )
    )
      throw Error("Missing pilot canopy geometry.");
    legacy.visible = false;
    root.add(scene);
    return data.tree_count;
  } catch (error) {
    console.warn(
      "Pilot canopy unavailable; retaining the preceding tree meshes.",
      error,
    );
    return 0;
  }
}
