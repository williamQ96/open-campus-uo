/* SPDX-License-Identifier: Apache-2.0 */
import { BufferAttribute, Vector3 } from "three";

const terraceTiles = [
  ["terrain", 36],
  ["Eugene_terrain_and_land_cover_L2", 36],
  ["campus-lawn-extension", 30],
];

// The Price courtyard assembly supplies replacement surfaces for these complete
// 5 m cells. Stage all changes before changing any of the three source meshes.
export function stagePriceCourtyardCut(
  root,
  baseRoot,
  [west, south, east, north],
) {
  const point = new Vector3();
  return terraceTiles.map(([name, expectedRemoved]) => {
    const mesh = (name === "terrain" ? baseRoot : root)?.getObjectByName(name);
    const geometry = mesh?.geometry;
    const index = geometry?.index;
    const positions = geometry?.attributes.position;
    if (!mesh?.isMesh || !index || !positions || geometry.groups.length)
      throw new Error(`Price courtyard terrain source ${name} is unavailable.`);
    mesh.updateWorldMatrix(true, false);

    const inside = new Uint8Array(positions.count);
    for (let i = 0; i < positions.count; i++) {
      point.fromBufferAttribute(positions, i).applyMatrix4(mesh.matrixWorld);
      inside[i] =
        point.x >= west &&
        point.x <= east &&
        -point.z >= south &&
        -point.z <= north;
    }
    const source = index.array;
    const retained = new source.constructor(
      source.length - expectedRemoved * 3,
    );
    let cursor = 0;
    let removed = 0;
    for (let i = 0; i < source.length; i += 3) {
      const a = source[i],
        b = source[i + 1],
        c = source[i + 2];
      if (inside[a] && inside[b] && inside[c]) {
        removed++;
      } else {
        retained[cursor++] = a;
        retained[cursor++] = b;
        retained[cursor++] = c;
      }
    }
    if (removed !== expectedRemoved || cursor !== retained.length)
      throw new Error("Price courtyard terrain cells no longer match.");
    return { geometry, index: new BufferAttribute(retained, 1) };
  });
}
