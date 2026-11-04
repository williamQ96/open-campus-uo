import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
import {
  segmentHitsBoxes,
  attachCollisionBoxes,
  overlayCollisionBoxesForDetail,
} from "../src/collision-supplement.js";
const read = (p) => readFileSync(new URL(p, import.meta.url));
test("provisional Alder overlay remains pinned, bounded and clear of modeled route edges", () => {
  const bytes = read("../public/scene/alder-north-provisional-detail.json"),
    s = JSON.parse(bytes),
    c = JSON.parse(read("../public/scene/presentation.json")),
    m = JSON.parse(read("../public/scene/manifest.json")),
    g = JSON.parse(read("../public/scene/navigation.json"));
  assert.equal(
    createHash("sha256").update(bytes).digest("hex"),
    c.exterior_details.find(
      (x) => x.url === "alder-north-provisional-detail.json",
    ).sha256,
  );
  assert.equal(s.base_asset_sha256, c.asset_sha256);
  assert.equal(s.building_id, "roof-ee63827c");
  assert.equal(s.merge_batch_target, "context-background-0-1");
  assert.equal(s.merge_source_vertex_count, 36276);
  assert.ok(
    createExteriorDetail(s, c.asset_sha256, new Set([s.building_id])).children
      .length,
  );
  assert.throws(() =>
    createExteriorDetail(s, "wrong", new Set([s.building_id])),
  );
  const boxes = overlayCollisionBoxesForDetail(s),
    record = structuredClone(m.buildings.find((x) => x.id === s.building_id));
  assert.equal(boxes.length, 8);
  attachCollisionBoxes(
    [record],
    [{ buildingId: s.building_id, boxes, overlay: true }],
  );
  assert.equal(
    g.edges.filter(([a, b]) =>
      segmentHitsBoxes(g.nodes_enu_m[a], g.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
});
