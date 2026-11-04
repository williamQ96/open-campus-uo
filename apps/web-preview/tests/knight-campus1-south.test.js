import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
import {
  overlayCollisionBoxesForDetail,
  attachCollisionBoxes,
  segmentHitsBoxes,
} from "../src/collision-supplement.js";
const read = (n) =>
  readFileSync(new URL(`../public/scene/${n}`, import.meta.url));
test("Knight Campus 1 south facade stays pinned, selectable and route-clear", () => {
  const cfg = JSON.parse(read("presentation.json")),
    raw = read("knight-campus1-south-detail.json"),
    d = JSON.parse(raw);
  const building = JSON.parse(read("manifest.json")).buildings.find(
    (b) => b.id === d.building_id,
  );
  assert.equal(d.building_id, "context-oc-knight-1");
  assert.equal(
    cfg.exterior_details.find(
      (e) => e.url === "knight-campus1-south-detail.json",
    ).sha256,
    createHash("sha256").update(raw).digest("hex"),
  );
  assert.equal(d.base_asset_sha256, cfg.asset_sha256);
  const detail = createExteriorDetail(
    d,
    cfg.asset_sha256,
    new Set([building.id]),
  );
  assert.equal(detail.children.length, 1);
  assert.equal(detail.children[0].userData.asset_id, building.id);
  const boxes = overlayCollisionBoxesForDetail(d);
  assert.equal(boxes.length, 3);
  // Keep the overlay away from the unresolved neighboring footprint.
  const neighbor = JSON.parse(read("manifest.json")).buildings.find(
    (b) => b.id === "roof-a79ff330",
  );
  assert.ok(neighbor);
  const neighborWest = Math.min(...neighbor.footprint_enu_m.map((p) => p[0]));
  assert.ok(boxes.every((box) => box[2] <= neighborWest - 3));
  assert.equal(
    attachCollisionBoxes(
      [structuredClone(building)],
      [{ buildingId: building.id, boxes, overlay: true }],
    ).length,
    3,
  );
  const graph = JSON.parse(read("navigation.json"));
  assert.equal(
    graph.edges.filter(([a, b]) =>
      segmentHitsBoxes(graph.nodes_enu_m[a], graph.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
});
