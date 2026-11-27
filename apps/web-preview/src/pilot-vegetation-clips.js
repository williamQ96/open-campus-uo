// SPDX-License-Identifier: Apache-2.0
import { BufferAttribute } from "three";

export function removeVegetationRanges(root, targets, expectedName) {
  const replacements = Object.entries(targets).map(
    ([name, { vertices, removed_indices, ranges }]) => {
      const mesh = root.getObjectByName(name);
      const geometry = mesh?.geometry;
      const index = geometry?.index;
      if (
        !expectedName.test(name) ||
        !mesh?.isMesh ||
        geometry.getAttribute("position")?.count !== vertices ||
        geometry.groups.length ||
        !index ||
        !Array.isArray(ranges) ||
        !ranges.length
      )
        throw new Error("Exterior review pilot vegetation mesh changed.");
      const remove = new Uint8Array(vertices);
      let cursor = 0;
      for (const [start, end] of ranges) {
        if (
          !Number.isInteger(start) ||
          !Number.isInteger(end) ||
          start < cursor ||
          end <= start ||
          end > vertices
        )
          throw new Error("Invalid exterior review pilot vegetation range.");
        remove.fill(1, start, end);
        cursor = end;
      }
      const source = index.array;
      for (let i = 0; i < source.length; i += 3) {
        const a = remove[source[i]];
        if (a !== remove[source[i + 1]] || a !== remove[source[i + 2]])
          throw new Error(
            "Exterior review pilot vegetation triangles are mixed.",
          );
      }
      const retained = source.filter((vertex) => !remove[vertex]);
      if (
        !retained.length ||
        source.length - retained.length !== removed_indices
      )
        throw new Error("Exterior review pilot vegetation count changed.");
      return [geometry, new BufferAttribute(retained, 1)];
    },
  );
  for (const [geometry, retained] of replacements) geometry.setIndex(retained);
}

export function removePilotTrees(root, recipe, sourceSha, refined) {
  const { tree_indices: trees } = recipe;
  const expectedSha = refined
    ? recipe.source_refined_sha256
    : recipe.source_legacy_sha256;
  if (
    sourceSha !== expectedSha ||
    !Array.isArray(trees) ||
    !trees.length ||
    new Set(trees).size !== trees.length ||
    trees.some((i) => !Number.isInteger(i) || i < 0 || i >= 300)
  )
    throw new Error("Exterior review pilot tree source changed.");
  removeVegetationRanges(
    root,
    refined ? recipe.refined : recipe.legacy,
    refined ? /^pilot-trees-(wood|foliage)$/ : /^vegetation_[1-4]$/,
  );
  return trees.length;
}
