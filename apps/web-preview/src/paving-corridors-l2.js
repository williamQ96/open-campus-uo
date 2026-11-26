// SPDX-License-Identifier: Apache-2.0
import { BufferAttribute } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { readPinnedScene } from "./pinned-scene.js";

const directory = "paving-corridors-l2";
const roadNames = ["corridors-road", "corridors-path"];
const quadNames = ["landscape-paving", "landscape-lawn"];

function replaceQuadRoutes(graph, patch) {
  // Active site packages may compact the node array. Resolve the shared
  // source chain by its exact projected coordinates before changing edges.
  const positions = new Map(
    graph.nodes_enu_m.map((point, i) => [point.join(","), i]),
  );
  const source = new Map(
    patch.source_nodes.map(([id, point]) => [
      id,
      positions.get(point.join(",")),
    ]),
  );
  if (
    [...source.values()].some((id) => id === undefined) ||
    new Set(source.values()).size !== source.size
  )
    throw new Error("An earlier Memorial Quad route anchor changed.");
  const retired = new Set(
    patch.retired_edges.map(([a, b]) =>
      [source.get(a), source.get(b)].join(","),
    ),
  );
  const removed = new Set(patch.retired_nodes.map((id) => source.get(id)));
  const nodes = [],
    remap = new Map();
  for (const [i, point] of graph.nodes_enu_m.entries()) {
    if (removed.has(i)) continue;
    remap.set(i, nodes.length);
    nodes.push(point);
  }
  const edges = [];
  for (const [a, b, length, kind] of graph.edges) {
    if (kind === "path" && retired.delete([a, b].join(","))) continue;
    if (!remap.has(a) || !remap.has(b))
      throw new Error("An earlier Memorial Quad junction changed.");
    edges.push([remap.get(a), remap.get(b), length, kind]);
  }
  if (retired.size || patch.original_anchors.length !== 3)
    throw new Error("An earlier Memorial Quad route changed.");
  const anchors = new Map(
    patch.original_anchors.map(([original, local]) => {
      const active = source.get(original);
      const [e, n] = graph.nodes_enu_m[active];
      if (
        patch.nodes[local][0] !== e ||
        patch.nodes[local][1] !== n ||
        !remap.has(active)
      )
        throw new Error("A Memorial Quad route anchor changed.");
      return [local, remap.get(active)];
    }),
  );
  const added = patch.nodes.map((point, i) => {
    if (anchors.has(i)) return anchors.get(i);
    return nodes.push(point) - 1;
  });
  for (const [a, b, length, kind] of patch.edges)
    edges.push([added[a], added[b], length, kind]);
  return { ...graph, nodes_enu_m: nodes, edges };
}

function mergeQuad(mesh, addition, cut) {
  const original = mesh?.geometry;
  const indices = original?.index?.array;
  if (
    !mesh?.isMesh ||
    !addition?.isMesh ||
    original.attributes.position.count !== cut.vertices ||
    indices?.length !== 3 * cut.triangles ||
    !cut.remove?.length ||
    cut.anchors?.length !== 8
  )
    throw new Error("The Memorial Quad source surface changed.");
  const positions = original.getAttribute("position");
  const removed = new Uint8Array(cut.triangles);
  let previous = 0;
  for (const [start, end] of cut.remove) {
    if (
      !Number.isSafeInteger(start) ||
      !Number.isSafeInteger(end) ||
      start < previous ||
      start >= end ||
      end > cut.triangles
    )
      throw new Error("Invalid Memorial Quad cut range.");
    removed.fill(1, start, end);
    previous = end;
  }
  for (const [slot, id, [x, y, z]] of cut.anchors) {
    if (
      !removed[Math.floor(slot / 3)] ||
      indices[slot] !== id ||
      positions.getX(id) !== x ||
      positions.getY(id) !== y ||
      positions.getZ(id) !== z
    )
      throw new Error("A Memorial Quad cut anchor changed.");
  }
  const retained = original.clone();
  retained.setIndex(
    new BufferAttribute(
      indices.filter((_, i) => !removed[Math.floor(i / 3)]),
      1,
    ),
  );
  const merged = mergeGeometries([retained, addition.geometry]);
  retained.dispose();
  if (!merged) throw new Error("Could not merge the Memorial Quad surface.");
  return { mesh, merged };
}

export async function installPavingCorridors(
  base,
  root,
  manifest,
  art,
  exteriorReview,
) {
  const config = art?.config;
  const recipe = config?.paving_corridors_l2;
  if (!recipe || !art.foundationGrade || !exteriorReview) return null;
  try {
    if (recipe.url !== `${directory}/surfaces.json`)
      throw new Error("Invalid route surface path.");
    const data = JSON.parse(
      new TextDecoder().decode(
        await readPinnedScene(base + recipe.url, recipe.sha256),
      ),
    );
    const retired = art.buildingReviews
      .map(({ retiredCorridor }) => retiredCorridor)
      .filter(Boolean);
    if (
      data.url !== `${directory}/surfaces.glb` ||
      data.source_art_sha256 !== config.asset_sha256 ||
      data.source_model_sha256 !== manifest.model.sha256 ||
      data.source_landcover_sha256 !== config.landcover_l2.sha256 ||
      data.required_retired_corridors?.length !== retired.length ||
      !data.required_retired_corridors.every((id) => retired.includes(id)) ||
      data.quad_cuts?.length !== quadNames.length
    )
      throw new Error("The campus surface sources changed.");
    const priorGraph = art.buildingReviews.find(
      ({ navigation }) => navigation,
    )?.navigation;
    const [bytes, graph] = await Promise.all([
      readPinnedScene(base + data.url, data.sha256),
      priorGraph ??
        readPinnedScene(
          base + "navigation.json",
          data.source_navigation_sha256,
        ).then((raw) => JSON.parse(new TextDecoder().decode(raw))),
    ]);
    const navigation = replaceQuadRoutes(graph, data.quad_routes);
    const { scene } = await new GLTFLoader().parseAsync(bytes, base);
    const oldRoads = roadNames.map((name) => root.getObjectByName(name));
    const newRoads = roadNames.map((name) => scene.getObjectByName(name));
    if (
      [...oldRoads, ...newRoads].some(
        (node) => !node?.isMesh || node.userData.asset_kind !== "corridor",
      ) ||
      newRoads.some((node) => !node.geometry.getAttribute("color"))
    )
      throw new Error("The expected road or path mesh is missing.");
    const quad = quadNames.map((name) => {
      const cut = data.quad_cuts.find((part) => part.name === name);
      if (!cut) throw new Error("A Memorial Quad cut is missing.");
      return mergeQuad(
        art.root.getObjectByName(name),
        scene.getObjectByName(`quad-${name}`),
        cut,
      );
    });
    exteriorReview.fitGrade(scene);
    for (const { mesh, merged } of quad) mesh.geometry = merged;
    for (const node of oldRoads) node.removeFromParent();
    for (const node of newRoads) root.add(node);
    return {
      summary: {
        corridors: manifest.corridors.features.length - retired.length,
        quad: true,
      },
      navigation,
      quadActivity: data.quad_activity,
    };
  } catch (error) {
    console.warn(
      "Campus surface refinement unavailable; using the prior surfaces.",
      error,
    );
    return null;
  }
}

export function updateQuadActivity(activity, patch) {
  if (!patch?.routes?.length || activity.version !== 2) return activity;
  const routes = new Map(activity.paths.map((path) => [path.id, path]));
  for (const revision of patch.routes) {
    const route = routes.get(revision.id);
    if (!route || route.surface !== revision.surface) return activity;
    const points = route.points_enu_m;
    if (
      ![points[0], points.at(-1)].every((point, i) =>
        point.every((value, axis) => value === revision.source_ends[i][axis]),
      )
    )
      return activity;
    routes.set(revision.id, { ...route, points_enu_m: revision.points });
  }
  return {
    ...activity,
    paths: [...routes.values()],
    pedestrian_regions: patch.pedestrian_regions,
  };
}
