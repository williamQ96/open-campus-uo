import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
import {
  segmentHitsBoxes,
  overlayCollisionBoxesForDetail,
} from "../src/collision-supplement.js";
const read = (p) => readFileSync(new URL(p, import.meta.url));
test("Unthank west facade is source pinned and avoids modeled route edges", () => {
  const config = JSON.parse(read("../public/scene/presentation.json")),
    bytes = read("../public/scene/unthank-west-detail.json"),
    spec = JSON.parse(bytes);
  assert.equal(
    config.exterior_details.find((e) => e.url === "unthank-west-detail.json")
      .sha256,
    createHash("sha256").update(bytes).digest("hex"),
  );
  assert.equal(spec.base_asset_sha256, config.asset_sha256);
  assert.equal(spec.building_id, "context-oc-unthank");
  assert.equal(spec.merge_source_vertex_count, 2120);
  assert.ok(
    createExteriorDetail(spec, config.asset_sha256, new Set([spec.building_id]))
      .children.length,
  );
  const boxes = overlayCollisionBoxesForDetail(spec),
    nav = JSON.parse(read("../public/scene/navigation.json"));
  assert.equal(boxes.length, 3);
  assert.equal(
    nav.edges.filter(([a, b]) =>
      segmentHitsBoxes(nav.nodes_enu_m[a], nav.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
});
