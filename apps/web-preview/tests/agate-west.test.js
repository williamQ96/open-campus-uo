import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
import {
  attachCollisionBoxes,
  overlayCollisionBoxesForDetail,
  segmentHitsBoxes,
} from "../src/collision-supplement.js";
const read = (p) => readFileSync(new URL(p, import.meta.url));
test("Agate provisional frontage is source-pinned and clears the modeled navigation graph", () => {
  const raw = read("../public/scene/agate-west-provisional-detail.json"),
    s = JSON.parse(raw),
    c = JSON.parse(read("../public/scene/presentation.json")),
    m = JSON.parse(read("../public/scene/manifest.json")),
    g = JSON.parse(read("../public/scene/navigation.json"));
  assert.equal(
    c.exterior_details.find(
      (x) => x.url === "agate-west-provisional-detail.json",
    ).sha256,
    createHash("sha256").update(raw).digest("hex"),
  );
  assert.equal(s.base_asset_sha256, c.asset_sha256);
  assert.equal(s.building_id, "roof-b068940e");
  assert.equal(s.merge_batch_target, "context-campus-2-0");
  assert.equal(s.merge_source_vertex_count, 2774);
  assert.equal(s.objects.length, 77);
  assert.ok(
    createExteriorDetail(s, c.asset_sha256, new Set([s.building_id])).children
      .length,
  );
  assert.throws(() =>
    createExteriorDetail(s, "wrong", new Set([s.building_id])),
  );
  const boxes = overlayCollisionBoxesForDetail(s),
    record = structuredClone(m.buildings.find((x) => x.id === s.building_id));
  assert.equal(boxes.length, 3);
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
