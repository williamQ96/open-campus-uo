import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
import {
  segmentHitsBoxes,
  overlayCollisionBoxesForDetail,
  attachCollisionBoxes,
} from "../src/collision-supplement.js";
const read = (p) => readFileSync(new URL(p, import.meta.url));
test("HEDCO layer and color patch remain pinned and avoid the route graph", () => {
  const config = JSON.parse(read("../public/scene/presentation.json")),
    data = read("../public/scene/hedco-exterior-detail.json"),
    bytes = read("../public/scene/hedco-wall-color.json"),
    detail = JSON.parse(data),
    patch = JSON.parse(bytes);
  const sha = (b) => createHash("sha256").update(b).digest("hex");
  assert.equal(
    config.exterior_details.find((e) => e.url === "hedco-exterior-detail.json")
      .sha256,
    sha(data),
  );
  assert.equal(
    config.wall_color_patches.find((e) => e.url === "hedco-wall-color.json")
      .sha256,
    sha(bytes),
  );
  assert.equal(detail.base_asset_sha256, config.asset_sha256);
  assert.equal(patch.base_asset_sha256, config.asset_sha256);
  assert.equal(detail.building_id, patch.building_id);
  assert.equal(detail.replace_building, false);
  assert.ok(
    createExteriorDetail(
      detail,
      config.asset_sha256,
      new Set([detail.building_id]),
    ).children.length,
  );
  assert.equal(detail.objects.length, 194);
  assert.equal(detail.merge_source_vertex_count, 1976);
  assert.equal(patch.expected_vertices, 16);
  const boxes = overlayCollisionBoxesForDetail(detail);
  assert.equal(boxes.length, 6);
  const buildings = [
    {
      id: detail.building_id,
      footprint_enu_m: [
        [-694.9119236135739, -442.39182995352894],
        [-634.9119236135739, -442.39182995352894],
        [-634.9119236135739, -390.39182995352894],
        [-694.9119236135739, -390.39182995352894],
      ],
    },
  ];
  attachCollisionBoxes(buildings, [
    { buildingId: detail.building_id, boxes, overlay: true },
  ]);
  assert.equal(buildings[0].collision_extra_enu_m.length, 6);
  const g = JSON.parse(read("../public/scene/navigation.json"));
  assert.equal(
    g.edges.filter(([a, b]) =>
      segmentHitsBoxes(g.nodes_enu_m[a], g.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
});
