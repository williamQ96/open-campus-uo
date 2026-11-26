// SPDX-License-Identifier: Apache-2.0
import { BufferAttribute, BufferGeometry, Matrix4 } from "three";
import { isFootprintRing, readPinnedScene } from "./pinned-scene.js";

const attributes = ["position", "normal", "color"];
const recipeUrl = "context-roof-refinements.json";
const sourceLayouts = new WeakMap();

function triangleCount(geometry) {
  return (
    (geometry.index?.count ?? geometry.getAttribute("position")?.count) / 3
  );
}

function retainedTriangleCount(count, omitted) {
  return count - omitted.reduce((total, [from, to]) => total + to - from, 0);
}

function saveLayout(geometry, count, omitted) {
  const appended =
    triangleCount(geometry) - retainedTriangleCount(count, omitted);
  sourceLayouts.set(geometry, { count, omitted, appended });
}

export function preserveContextPrefix(source, result) {
  const prior = sourceLayouts.get(source);
  saveLayout(
    result,
    prior?.count ?? triangleCount(source),
    prior?.omitted ?? [],
  );
}

export function recordContextOmissions(geometry, count, ranges) {
  const prior = sourceLayouts.get(geometry);
  const omitted = [...(prior?.omitted ?? []), ...ranges].sort(
    ([a], [b]) => a - b,
  );
  saveLayout(geometry, count, omitted);
}

export function retainedContextRange(geometry, range, sourceCount) {
  if (!Array.isArray(range) || range.length !== 2) return null;
  const [start, end] = range;
  if (
    ![start, end].every(Number.isInteger) ||
    start < 0 ||
    end <= start ||
    end > sourceCount
  )
    return null;
  const layout = sourceLayouts.get(geometry);
  const count = triangleCount(geometry);
  if (!layout) return count === sourceCount ? range : null;
  if (
    layout.count !== sourceCount ||
    !Number.isInteger(layout.appended) ||
    layout.appended < 0 ||
    count !==
      retainedTriangleCount(sourceCount, layout.omitted) + layout.appended
  )
    return null;
  let removedBefore = 0;
  for (const [from, to] of layout.omitted) {
    if (from >= end) break;
    if (to > start) return null;
    removedBefore += to - from;
  }
  return [start - removedBefore, end - removedBefore];
}

function stageBatch(root, batch, buildingIds, heights, changedRecords) {
  const target = root.getObjectByName(batch.target);
  const geo = target?.geometry;
  const pos = geo?.getAttribute("position");
  const index = geo?.index;
  const count = (index?.count ?? pos?.count) / 3;
  const end = batch.source_triangle_count;
  const layout = sourceLayouts.get(geo);
  const expectedCount =
    retainedTriangleCount(end, layout?.omitted ?? []) + (layout?.appended ?? 0);
  if (
    !target?.isMesh ||
    target.userData.asset_kind !== "context-building-batch" ||
    !target.matrix.equals(new Matrix4()) ||
    geo.groups.length ||
    !Number.isInteger(count) ||
    !Number.isInteger(end) ||
    end < 1 ||
    count !== expectedCount ||
    Object.keys(geo.attributes).length !== attributes.length ||
    attributes.some((key) => {
      const attr = geo.getAttribute(key);
      return (
        !attr ||
        attr.itemSize !== 3 ||
        attr.count !== pos.count ||
        attr.normalized ||
        !(attr.array instanceof Float32Array)
      );
    }) ||
    !Array.isArray(batch.buildings) ||
    !batch.buildings.length
  )
    throw new Error("Context roof source batch changed.");

  const vertexAt = index ? (offset) => index.getX(offset) : (offset) => offset;
  const belongs = target.userData.asset_ids;
  const dropped = new Uint8Array(count);
  const starts = new Map();
  let additional = 0;
  let previous = 0;
  for (const item of batch.buildings) {
    const {
      id,
      triangles: [from, to],
      footing_z_m: foot,
      old_eave_z_m: eave,
      new_eave_z_m: newEave,
      new_roof_z_m: peak,
      cap,
      source_vertices: anchors,
      keep_wall_triangles: walls,
      replacement,
    } = item;
    const span = retainedContextRange(geo, [from, to], end);
    const capLength = cap?.position?.length;
    if (
      !buildingIds.has(id) ||
      !belongs?.includes(id) ||
      heights.has(id) ||
      !span ||
      ![from, to].every(Number.isInteger) ||
      from < previous ||
      to <= from ||
      to > end ||
      ![foot, eave, newEave, peak].every(Number.isFinite) ||
      eave <= foot ||
      newEave <= foot ||
      peak <= newEave ||
      !Number.isInteger(capLength) ||
      capLength < 9 ||
      capLength % 9 ||
      attributes.some(
        (key) =>
          !Array.isArray(cap[key]) ||
          cap[key].length !== capLength ||
          !cap[key].every(Number.isFinite),
      ) ||
      !Array.isArray(walls) ||
      (replacement
        ? walls.length !== 0 ||
          !isFootprintRing(replacement.footprint_enu_m) ||
          !Array.isArray(replacement.footprint_holes_enu_m) ||
          !replacement.footprint_holes_enu_m.every(isFootprintRing) ||
          typeof replacement.name !== "string" ||
          !replacement.name.trim() ||
          typeof replacement.name_source !== "string" ||
          !replacement.name_source.startsWith("https://")
        : !walls.length) ||
      walls.some(
        (offset, i) =>
          !Number.isInteger(offset) ||
          offset < 0 ||
          offset >= to - from ||
          (i > 0 && offset <= walls[i - 1]),
      ) ||
      !Array.isArray(anchors) ||
      anchors.length !== 3 ||
      anchors.some(([offset, xyz]) => {
        if (
          !Number.isInteger(offset) ||
          offset < 0 ||
          offset >= (to - from) * 3 ||
          !Array.isArray(xyz) ||
          xyz.length !== 3 ||
          !xyz.every(Number.isFinite)
        )
          return true;
        const v = vertexAt(span[0] * 3 + offset);
        return (
          Math.hypot(
            pos.getX(v) - xyz[0],
            pos.getY(v) - xyz[1],
            pos.getZ(v) - xyz[2],
          ) > 0.00002
        );
      })
    )
      throw new Error("Context roof member changed.");

    dropped.fill(1, ...span);
    starts.set(id, span[0]);
    previous = to;
    additional += walls.length * 3 + capLength / 3;
    heights.set(id, peak);
    if (replacement) changedRecords.set(id, { ...replacement, base_z_m: foot });
  }
  const vertices = pos.count + additional;
  const result = new BufferGeometry();
  const values = Object.fromEntries(
    attributes.map((key) => {
      const data = new Float32Array(vertices * 3);
      data.set(geo.getAttribute(key).array);
      result.setAttribute(key, new BufferAttribute(data, 3));
      return [key, data];
    }),
  );
  const keptCount =
    (count - dropped.reduce((sum, value) => sum + value, 0)) * 3;
  const newIndices = new (vertices > 65536 ? Uint32Array : Uint16Array)(
    keptCount + additional,
  );
  let next = 0;
  for (let t = 0; t < count; t++) {
    if (dropped[t]) continue;
    for (let i = 0; i < 3; i++) newIndices[next++] = vertexAt(t * 3 + i);
  }

  let tail = pos.count * 3;
  const oldNormals = geo.getAttribute("normal");
  const oldColors = geo.getAttribute("color").array;
  for (const item of batch.buildings) {
    const foot = item.footing_z_m;
    const scale = (item.new_eave_z_m - foot) / (item.old_eave_z_m - foot);
    for (const wall of item.keep_wall_triangles) {
      for (let i = 0; i < 3; i++, tail += 3) {
        const v = vertexAt((starts.get(item.id) + wall) * 3 + i);
        values.position[tail] = pos.getX(v);
        values.position[tail + 1] = foot + (pos.getY(v) - foot) * scale;
        values.position[tail + 2] = pos.getZ(v);
        const x = oldNormals.getX(v);
        const y = oldNormals.getY(v) / scale;
        const z = oldNormals.getZ(v);
        const length = Math.hypot(x, y, z) || 1;
        values.normal.set([x / length, y / length, z / length], tail);
        values.color.set(oldColors.subarray(v * 3, v * 3 + 3), tail);
      }
    }
    for (const key of attributes) values[key].set(item.cap[key], tail);
    tail += item.cap.position.length;
  }
  for (let v = pos.count; v < vertices; v++) newIndices[next++] = v;
  result.setIndex(new BufferAttribute(newIndices, 1));
  result.computeBoundingSphere();
  // Indices preserve the retained source triangles as a prefix. Later site
  // reviews can translate an unrelated member's original span into that prefix.
  if (layout) sourceLayouts.set(result, layout);
  recordContextOmissions(
    result,
    end,
    batch.buildings.map(({ triangles }) => triangles),
  );
  return { target, geometry: result };
}

export async function installContextRoofRefinements(
  root,
  base,
  config,
  buildingIds,
  replacedIds = new Set(),
) {
  const link = config.context_roof_refinements;
  if (config.verify_source_sha256 !== true || link.url !== recipeUrl)
    throw new Error("Invalid context roof recipe link.");
  const spec = JSON.parse(
    new TextDecoder().decode(
      await readPinnedScene(base + recipeUrl, link.sha256),
    ),
  );
  if (
    spec.version !== 1 ||
    spec.source_presentation_sha256 !== config.asset_sha256 ||
    !Array.isArray(spec.batches) ||
    !spec.batches.length ||
    new Set(spec.batches.map(({ target }) => target)).size !==
      spec.batches.length
  )
    throw new Error("Context roofs do not match the presentation.");
  const heights = new Map();
  const changedRecords = new Map();
  const staged = [];
  for (const batch of spec.batches) {
    if (!Array.isArray(batch.buildings) || !batch.buildings.length)
      throw new Error("Context roof batch has no buildings.");
    const buildings = batch.buildings.filter(({ id }) => !replacedIds.has(id));
    if (buildings.length)
      staged.push(
        stageBatch(
          root,
          { ...batch, buildings },
          buildingIds,
          heights,
          changedRecords,
        ),
      );
  }
  for (const { target, geometry } of staged) {
    target.geometry.dispose();
    target.geometry = geometry;
  }
  return { heights, changedRecords };
}
