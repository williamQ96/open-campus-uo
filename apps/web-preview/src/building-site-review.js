// SPDX-License-Identifier: Apache-2.0
import { BufferAttribute } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import {
  recordContextOmissions,
  retainedContextRange,
} from "./context-roof-refinements.js";
import { isFootprintRing, readPinnedScene } from "./pinned-scene.js";
import { sampleSurface } from "./pilot-hardscape.js";

function validBuilding(building) {
  const supports = building?.support_collision_enu_m ?? [];
  const holes = building?.footprint_holes_enu_m ?? [];
  const ground = building?.ground_footprints_enu_m;
  return (
    isFootprintRing(building?.footprint_enu_m) &&
    Array.isArray(holes) &&
    holes.every(isFootprintRing) &&
    Array.isArray(supports) &&
    supports.every(isFootprintRing) &&
    (ground === undefined ||
      (Array.isArray(ground) &&
        ground.length > 0 &&
        ground.every(isFootprintRing))) &&
    [building.roof_z_m, building.base_z_m].every(Number.isFinite) &&
    building.roof_z_m > building.base_z_m &&
    Array.isArray(building.entrances) &&
    building.entrances.every(
      ({ gate, position_enu_m: point, outward_degrees }) =>
        /^[a-z][a-z-]+$/.test(gate) &&
        Array.isArray(point) &&
        point.length === 2 &&
        point.every(Number.isFinite) &&
        Number.isFinite(outward_degrees),
    )
  );
}

function stageContextTreeRemoval(root, trees) {
  if (!trees.length) return null;
  const mesh = root.getObjectByName("campus-trees");
  const geometry = mesh?.geometry;
  const position = geometry?.getAttribute("position");
  const index = geometry?.index;
  if (
    !mesh?.userData.contextTrunkVariation ||
    position?.count !== 55200 ||
    !index
  )
    throw new Error("Exterior review context tree changed.");

  const removed = new Set();
  for (const {
    index: tree,
    position_enu_m: [e, n],
  } of trees) {
    const start = 45600 + tree * 32;
    if (
      Math.hypot(
        (position.getX(start) + position.getX(start + 16)) / 2 - e,
        (position.getZ(start) + position.getZ(start + 16)) / 2 + n,
      ) > 0.005
    )
      throw new Error("Exterior review context tree changed.");
    removed.add(tree);
  }
  const updated = index.array.filter((vertex) => {
    const tree =
      vertex < 45600
        ? Math.floor(vertex / 152)
        : Math.floor((vertex - 45600) / 32);
    return !removed.has(tree);
  });
  if (index.count - updated.length !== trees.length * 240)
    throw new Error("Exterior review context tree triangles changed.");
  return { geometry, index: new BufferAttribute(updated, 1) };
}

function removeVegetationRanges(root, targets, expectedName) {
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

function removePilotTrees(root, recipe, sourceSha, refined) {
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

function checkedBatchRange(mesh, item, position, index, sourceCount) {
  const range = retainedContextRange(
    mesh.geometry,
    item.triangles,
    item.source_triangle_count,
  );
  if (!range) throw new Error("Exterior review context source range changed.");
  const [start, end] = range;
  if (
    !mesh.userData.asset_ids.includes(item.id) ||
    end * 3 > sourceCount ||
    !Array.isArray(item.source_vertices) ||
    item.source_vertices.length !== 3 ||
    item.source_vertices.some(([offset, point]) => {
      if (
        !Number.isInteger(offset) ||
        offset < 0 ||
        offset >= (end - start) * 3 ||
        !Array.isArray(point) ||
        point.length !== 3 ||
        !point.every(Number.isFinite)
      )
        return true;
      const slot = start * 3 + offset;
      const vertex = index?.getX(slot) ?? slot;
      return (
        Math.hypot(
          position.getX(vertex) - point[0],
          position.getY(vertex) - point[1],
          position.getZ(vertex) - point[2],
        ) > 0.00002
      );
    })
  )
    throw new Error("Exterior review context source batch changed.");
  return [start * 3, end * 3];
}

function stageBatchRemoval(root, items) {
  const mesh = root.getObjectByName(items[0].target);
  const geometry = mesh?.geometry;
  const position = geometry?.getAttribute("position");
  const index = geometry?.index;
  const triangles = items[0].source_triangle_count;
  if (
    mesh?.userData.asset_kind !== "context-building-batch" ||
    !Array.isArray(mesh.userData.asset_ids) ||
    !position ||
    geometry.groups.length ||
    items.some((item) => item.source_triangle_count !== triangles)
  )
    throw new Error("Exterior review context source batch changed.");
  const sourceCount = index?.count ?? position.count;
  const ranges = items
    .map((item) => checkedBatchRange(mesh, item, position, index, sourceCount))
    .sort(([a], [b]) => a - b);
  const removed = new Set(items.map(({ id }) => id));
  const ids = mesh.userData.asset_ids.filter((id) => !removed.has(id));
  const remainingCount =
    sourceCount -
    ranges.reduce((count, [start, end]) => count + end - start, 0);
  if (
    ranges.some(([start], i) => i !== 0 && start < ranges[i - 1][1]) ||
    (remainingCount === 0) !== (ids.length === 0)
  )
    throw new Error(
      "Exterior review context source ranges overlap or omit a member.",
    );
  const existing =
    index?.array ?? Uint32Array.from({ length: sourceCount }, (_, i) => i);
  const remaining = new existing.constructor(remainingCount);
  let cursor = 0;
  let write = 0;
  for (const [start, end] of ranges) {
    remaining.set(existing.subarray(cursor, start), write);
    write += start - cursor;
    cursor = end;
  }
  remaining.set(existing.subarray(cursor), write);
  return {
    mesh,
    ids,
    triangles,
    omitted: items.map(({ triangles }) => triangles),
    index: new BufferAttribute(remaining, 1),
  };
}

function patchedNavigation(graph, { removed_edges, paths }) {
  const nodes = graph.nodes_enu_m.slice();
  const omit = new Set(removed_edges);
  if (
    omit.size !== removed_edges.length ||
    removed_edges.some(
      (i) => !Number.isInteger(i) || graph.edges[i]?.[3] !== "road",
    )
  )
    throw new Error("Exterior review road edges changed.");
  const edges = graph.edges.filter((_, i) => !omit.has(i));
  for (const { anchor, points, end } of paths) {
    if (
      !Number.isInteger(anchor) ||
      !nodes[anchor] ||
      (end !== undefined && (!Number.isInteger(end) || !nodes[end]))
    )
      throw new Error("Exterior review path anchor changed.");
    let previous = anchor;
    function connect(next) {
      const point = nodes[next];
      const length = Math.hypot(
        point[0] - nodes[previous][0],
        point[1] - nodes[previous][1],
      );
      if (!Number.isFinite(length) || length < 0.05 || length > 20)
        throw new Error("Invalid exterior review path segment.");
      edges.push([previous, next, length, "path"]);
      previous = next;
    }
    for (const point of points) {
      nodes.push(point);
      connect(nodes.length - 1);
    }
    if (end !== undefined) connect(end);
  }
  const used = new Set(edges.flatMap(([a, b]) => [a, b]));
  const remap = new Map();
  const retained = nodes.filter((_, i) => {
    if (!used.has(i)) return false;
    remap.set(i, remap.size);
    return true;
  });
  return {
    ...graph,
    nodes_enu_m: retained,
    edges: edges.map(([a, b, length, kind]) => [
      remap.get(a),
      remap.get(b),
      length,
      kind,
    ]),
  };
}

function validWalkableGround(ground) {
  const validPoint = (point) =>
    Array.isArray(point) &&
    point.length === 2 &&
    point.every((value) => Number.isFinite(value) && Math.abs(value) < 1000);
  const bounds = ground?.bounds_enu_m;
  const paths = ground?.paths ?? [ground];
  return (
    Array.isArray(bounds) &&
    bounds.length > 0 &&
    bounds.length <= 8 &&
    bounds.every(
      (box) =>
        Array.isArray(box) &&
        box.length === 4 &&
        box.every(
          (value) => Number.isFinite(value) && Math.abs(value) < 1000,
        ) &&
        box[0] < box[2] &&
        box[1] < box[3] &&
        box[2] - box[0] < 90 &&
        box[3] - box[1] < 90,
    ) &&
    Array.isArray(paths) &&
    paths.length > 0 &&
    paths.length <= 8 &&
    paths.every(
      (path) =>
        validPoint(path?.anchor_enu_m) &&
        Array.isArray(path.points_enu_m) &&
        path.points_enu_m.length > 0 &&
        path.points_enu_m.length <= 96 &&
        path.points_enu_m.every(validPoint) &&
        (path.end_enu_m === undefined || validPoint(path.end_enu_m)),
    )
  );
}

function appendWalkablePath(graph, ground) {
  return (ground.paths ?? [ground]).reduce((current, path) => {
    const locate = ([east, north]) =>
      current.nodes_enu_m.findIndex(
        ([e, n]) => Math.hypot(e - east, n - north) < 0.025,
      );
    return patchedNavigation(current, {
      removed_edges: [],
      paths: [
        {
          anchor: locate(path.anchor_enu_m),
          points: path.points_enu_m,
          end: path.end_enu_m && locate(path.end_enu_m),
        },
      ],
    });
  }, graph);
}

function stageCorridor(root, patch) {
  const mesh = root?.getObjectByName("corridors-road");
  const {
    triangle_count: triangleCount,
    anchors,
    removed_triangles: removed,
  } = patch;
  const index = mesh?.geometry?.index;
  const position = mesh?.geometry?.getAttribute("position");
  const retired = new Set(removed);
  if (
    mesh?.userData?.asset_kind !== "corridor" ||
    mesh.userData.corridor_kind !== "road" ||
    !position ||
    index?.count !== triangleCount * 3 ||
    retired.size !== removed.length ||
    removed.some((i) => !Number.isInteger(i) || i < 0 || i >= triangleCount) ||
    anchors.length !== 3 ||
    anchors.some(([slot, point]) => {
      if (!Number.isInteger(slot) || !retired.has(Math.floor(slot / 3)))
        return true;
      const v = index.getX(slot);
      return (
        Math.hypot(
          position.getX(v) - point[0],
          position.getY(v) - point[1],
          position.getZ(v) - point[2],
        ) > 0.00002
      );
    })
  )
    throw new Error("Exterior review source road mesh changed.");
  return {
    mesh,
    index: new BufferAttribute(
      index.array.filter((_, i) => !retired.has(Math.floor(i / 3))),
      1,
    ),
  };
}

export async function loadBuildingSiteReview(
  base,
  manifest,
  config,
  {
    descriptor,
    directory,
    ids,
    groundNode,
    walkableGroundNode,
    absorbedIds = [],
    replacedDetails = [],
    identityMoves = {},
    splitBuildings = {},
    newBuildingIds = [],
    routeToApproaches = false,
    registeredNames = {},
    registeredAddresses = {},
    sourceBatchIds = [],
    prerequisiteIds = [],
    corridorId,
    navigationUrl,
    navigationPredecessors = [],
  },
) {
  if (
    !config.verify_source_sha256 ||
    !/^[a-z]+(?:-[a-z]+)*-review$/.test(directory) ||
    descriptor.url !== `${directory}/site.json`
  )
    throw new Error("Invalid building site descriptor.");

  const site = JSON.parse(
    new TextDecoder().decode(
      await readPinnedScene(base + descriptor.url, descriptor.sha256),
    ),
  );
  const buildings = site.buildings ?? [site.building];
  if (!Array.isArray(buildings) || buildings.length !== ids.length)
    throw new Error("Unexpected buildings in exterior review.");
  const replacements = new Map(buildings.map((item) => [item?.id, item]));
  const originals = new Map(
    manifest.buildings.map((record) => [record.id, record]),
  );
  const moves = Object.entries(identityMoves);
  const movedIds = new Set(moves.map(([, id]) => id));
  const declaredMoves = Object.entries(site.identity_moves ?? {});
  const splits = Object.entries(splitBuildings);
  const declaredSplits = Object.entries(site.split_buildings ?? {});
  const splitIds = splits.map(([id]) => id);
  const declaredNewIds = site.new_building_ids ?? [];
  const addedIds = [...movedIds, ...splitIds, ...newBuildingIds];
  const trees =
    site.context_trees ?? (site.context_tree ? [site.context_tree] : []);
  const batches = site.batch_removals ?? [];
  const closedSiteBoxes = site.closed_site_boxes_enu_m ?? [];
  const pilotTreeClip = site.pilot_tree_clip;
  const pilotUnderstory = site.pilot_understory_clip;
  const walkableGround = site.walkable_ground;
  const corridor = site.corridor_patch;
  if (
    site.source_presentation_sha256 !== config.asset_sha256 ||
    site.source_base_model_sha256 !== manifest.model.sha256 ||
    site.url !== `${directory}/site.glb` ||
    site.ground_node !== groundNode ||
    Boolean(walkableGroundNode) !== (walkableGround !== undefined) ||
    (walkableGroundNode &&
      (!navigationUrl || !validWalkableGround(walkableGround))) ||
    !Array.isArray(batches) ||
    !Array.isArray(closedSiteBoxes) ||
    closedSiteBoxes.length > 16 ||
    closedSiteBoxes.some(
      (box) =>
        !Array.isArray(box) ||
        box.length !== 4 ||
        !box.every(
          (value) => Number.isFinite(value) && Math.abs(value) <= 2000,
        ) ||
        box[0] >= box[2] ||
        box[1] >= box[3] ||
        box[2] - box[0] > 100 ||
        box[3] - box[1] > 100,
    ) ||
    new Set(batches.map((item) => item?.id)).size !== batches.length ||
    batches.some(
      (item) =>
        !absorbedIds.includes(item?.id) && !sourceBatchIds.includes(item?.id),
    ) ||
    sourceBatchIds.some(
      (id) => !ids.includes(id) || !batches.some((item) => item.id === id),
    ) ||
    (corridor?.id ?? undefined) !== corridorId ||
    (corridor &&
      (!navigationUrl ||
        !manifest.corridors?.features.some(({ id }) => id === corridorId))) ||
    (site.absorbed_ids ?? []).join(",") !== absorbedIds.join(",") ||
    declaredMoves.length !== moves.length ||
    movedIds.size !== moves.length ||
    moves.some(
      ([previousId, id]) =>
        site.identity_moves?.[previousId] !== id ||
        ids.includes(previousId) ||
        absorbedIds.includes(previousId) ||
        !ids.includes(id) ||
        originals.has(id) ||
        !originals.get(previousId)?.name ||
        originals.get(previousId).name !== replacements.get(id)?.name ||
        originals.get(previousId).campus_id !== replacements.get(id)?.campus_id,
    ) ||
    !Array.isArray(declaredNewIds) ||
    declaredNewIds.length !== newBuildingIds.length ||
    newBuildingIds.some(
      (id, index) =>
        declaredNewIds[index] !== id ||
        originals.has(id) ||
        !ids.includes(id) ||
        !Object.hasOwn(registeredAddresses, id),
    ) ||
    new Set(addedIds).size !== addedIds.length ||
    declaredSplits.length !== splits.length ||
    splits.some(
      ([id, sourceId]) =>
        site.split_buildings?.[id] !== sourceId ||
        originals.has(id) ||
        movedIds.has(id) ||
        !ids.includes(id) ||
        !originals.has(sourceId) ||
        !sourceBatchIds.includes(sourceId) ||
        !Object.hasOwn(registeredAddresses, id) ||
        !Object.hasOwn(registeredAddresses, sourceId),
    ) ||
    absorbedIds.some((id) => ids.includes(id) || !originals.has(id)) ||
    Object.entries(registeredNames).some(([id, name]) => {
      const authored = replacements.get(id);
      return (
        !ids.includes(id) ||
        originals.get(id)?.name ||
        authored?.name !== name ||
        !/^B\d{4}[A-Z]?$/.test(authored.campus_id)
      );
    }) ||
    Object.entries(registeredAddresses).some(([id, [name, address]]) => {
      const authored = replacements.get(id);
      return (
        !ids.includes(id) ||
        originals.get(id)?.name ||
        Object.hasOwn(registeredNames, id) ||
        authored?.name !== name ||
        authored?.street_address !== address ||
        authored?.campus_id !== undefined
      );
    }) ||
    (site.context_tree && site.context_trees !== undefined) ||
    !Array.isArray(trees) ||
    trees.some(
      (tree) =>
        !tree ||
        !Number.isInteger(tree.index) ||
        tree.index < 0 ||
        tree.index >= 300 ||
        !Array.isArray(tree.position_enu_m) ||
        tree.position_enu_m.length !== 2 ||
        !tree.position_enu_m.every(Number.isFinite),
    ) ||
    new Set(trees.map(({ index }) => index)).size !== trees.length ||
    ids.some(
      (id) =>
        !validBuilding(replacements.get(id)) ||
        (!addedIds.includes(id) && !originals.has(id)),
    )
  )
    throw new Error("Exterior review does not match the base scene.");

  const [bytes, , graph] = await Promise.all([
    readPinnedScene(base + site.url, site.sha256),
    readPinnedScene(
      base + manifest.heightfield_url,
      site.source_heightfield_sha256,
    ),
    (corridor || walkableGroundNode) &&
      readPinnedScene(
        base + navigationUrl,
        corridor?.source_navigation_sha256 ?? site.source_navigation_sha256,
      ).then(async (data) => {
        const original = JSON.parse(new TextDecoder().decode(data));
        if (walkableGroundNode) {
          let baseGraph = original;
          for (const predecessorPin of navigationPredecessors) {
            const predecessorBytes = await readPinnedScene(
              base + predecessorPin.url,
              predecessorPin.sha256,
            );
            const predecessor = JSON.parse(
              new TextDecoder().decode(predecessorBytes),
            );
            if (
              predecessor.source_navigation_sha256 !==
                site.source_navigation_sha256 ||
              !validWalkableGround(predecessor.walkable_ground)
            )
              throw new Error("Exterior review path predecessor changed.");
            baseGraph = appendWalkablePath(
              baseGraph,
              predecessor.walkable_ground,
            );
          }
          appendWalkablePath(baseGraph, walkableGround);
        }
        return corridor && patchedNavigation(original, corridor);
      }),
  ]);
  const { scene } = await new GLTFLoader().parseAsync(bytes, base);
  const ground = groundNode ? scene.getObjectByName(groundNode) : undefined;
  const surface = walkableGroundNode
    ? scene.getObjectByName(walkableGroundNode)
    : undefined;
  const roadRemainder = corridor && scene.getObjectByName("corridor-remainder");
  const matches = (object, id) =>
    object?.isMesh && object.userData.asset_id === id;
  if (
    ids.some((id) => !matches(scene.getObjectByName(id), id)) ||
    (groundNode && !ground?.isMesh) ||
    (walkableGroundNode &&
      (!matches(surface, walkableGroundNode) ||
        surface.userData.asset_kind !== "landscape-surface")) ||
    (corridor && !roadRemainder?.isMesh)
  )
    throw new Error("Missing exterior review building or ground.");

  return {
    ids,
    absorbedIds,
    replacedDetails,
    identityMoves,
    addedIds,
    newBuildingIds,
    assetSha: site.sha256,
    descriptorSha: descriptor.sha256,
    routeApproachIds: routeToApproaches ? ids : newBuildingIds,
    ground,
    closedSiteBoxes,
    clipPilotTrees:
      pilotTreeClip &&
      ((root, sourceSha, refined) =>
        removePilotTrees(root, pilotTreeClip, sourceSha, refined)),
    clipPilotUnderstory:
      pilotUnderstory &&
      ((root) =>
        removeVegetationRanges(root, pilotUnderstory, /^understory_1$/)),
    walkableHeight:
      surface && sampleSurface(surface, walkableGround.bounds_enu_m),
    appendNavigation:
      surface && ((graph) => appendWalkablePath(graph, walkableGround)),
    navigation: graph,
    retiredCorridor: corridorId,
    entrances: Object.fromEntries(
      buildings.map((item) => [item.id, item.entrances]),
    ),
    records(source) {
      const records = source
        .concat(
          moves.map(([, id]) => ({
            id,
            kind: "building",
            status: "registered-exterior",
            name: replacements.get(id).name,
            campus_id: replacements.get(id).campus_id,
          })),
          splits.map(([id, sourceId]) => ({
            id,
            kind: "building",
            status: "registered-exterior",
            split_source_id: sourceId,
          })),
          newBuildingIds.map((id) => ({
            id,
            kind: "building",
            status: "registered-exterior",
          })),
        )
        .filter(({ id }) => !absorbedIds.includes(id))
        .map((record) => {
          const building = replacements.get(record.id);
          if (Object.hasOwn(identityMoves, record.id)) {
            const candidate = { ...record };
            for (const key of [
              "name",
              "campus_id",
              "name_source",
              "name_match",
              "name_anchor_lon_lat",
              "anchor_note",
            ])
              delete candidate[key];
            return candidate;
          }
          return building
            ? {
                ...record,
                ...(Object.hasOwn(registeredNames, record.id) && {
                  name: building.name,
                  campus_id: building.campus_id,
                  name_match: "registered-campus-outline",
                }),
                ...(Object.hasOwn(registeredAddresses, record.id) && {
                  name: building.name,
                  street_address: building.street_address,
                  name_match: "registered-municipal-address",
                }),
                footprint_enu_m: building.footprint_enu_m,
                footprint_holes_enu_m: building.footprint_holes_enu_m ?? [],
                ...(building.ground_footprints_enu_m && {
                  ground_footprints_enu_m: building.ground_footprints_enu_m,
                }),
                area_m2: building.area_m2 ?? record.area_m2,
                base_z_m: building.base_z_m,
                roof_z_m: building.roof_z_m,
                height_m: building.roof_z_m - building.base_z_m,
                collision_extra_enu_m: building.support_collision_enu_m ?? [],
              }
            : record;
        });
      return records;
    },
    install(root, baseRoot, installedReviews = []) {
      if (
        navigationPredecessors.some(
          ({ sha256 }) =>
            !installedReviews.some((review) => review.descriptorSha === sha256),
        )
      )
        throw new Error("Exterior review path predecessor was not installed.");
      if (
        prerequisiteIds.some(
          (id) => root.getObjectByName(id)?.userData.asset_id !== id,
        )
      )
        throw new Error("Missing registered predecessor for exterior review.");
      if (addedIds.some((id) => root.getObjectByName(id)))
        throw new Error(
          "An exterior review attempted to add an existing building.",
        );
      const batchIds = new Set(batches.map(({ id }) => id));
      const sources = [
        ...ids.filter((id) => !addedIds.includes(id) && !batchIds.has(id)),
        ...absorbedIds.filter((id) => !batchIds.has(id)),
      ];
      const prior = sources.map((id) => root.getObjectByName(id));
      if (
        prior.some(
          (node, i) =>
            node?.userData.asset_id !== sources[i] ||
            !(
              node.isMesh ||
              (node.isGroup &&
                node.children.length &&
                node.children.every((child) => child.isMesh))
            ),
        )
      )
        throw new Error("Missing source building mesh for exterior review.");
      const byTarget = new Map();
      for (const item of batches) {
        if (!byTarget.has(item.target)) byTarget.set(item.target, []);
        byTarget.get(item.target).push(item);
      }
      const stagedBatches = Array.from(byTarget.values(), (items) =>
        stageBatchRemoval(root, items),
      );
      const road = corridor && stageCorridor(baseRoot, corridor);
      const treeRemoval = stageContextTreeRemoval(root, trees);
      if (treeRemoval) treeRemoval.geometry.setIndex(treeRemoval.index);
      for (const { mesh, ids, index, triangles, omitted } of stagedBatches) {
        if (ids.length) {
          mesh.geometry.setIndex(index);
          mesh.userData.asset_ids = ids;
          recordContextOmissions(mesh.geometry, triangles, omitted);
        } else {
          mesh.removeFromParent();
        }
      }
      if (road) {
        road.mesh.geometry.setIndex(road.index);
        roadRemainder.userData = { ...road.mesh.userData };
        roadRemainder.material = road.mesh.material;
        road.mesh.add(roadRemainder);
      }
      for (const mesh of prior) mesh.removeFromParent();
      root.add(scene);
      return trees.length;
    },
  };
}
