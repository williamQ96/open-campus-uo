import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import {
  collisionBoxesForDetail,
  attachCollisionBoxes,
  segmentHitsBoxes,
} from "../src/collision-supplement.js";
import { isBlocked } from "../src/world.js";
import { createRouter } from "../src/routing.js";
const read = (n) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${n}`, import.meta.url)));
test("Villard facade is source pinned and conservatively blocks modeled solids", () => {
  const file = readFileSync(
    new URL("../public/scene/villard-east-detail.json", import.meta.url),
  );
  const d = JSON.parse(file),
    p = read("presentation.json");
  assert.equal(
    p.exterior_details.find((x) => x.url === "villard-east-detail.json").sha256,
    createHash("sha256").update(file).digest("hex"),
  );
  const b = structuredClone(
    read("manifest.json").buildings.find((x) => x.id === d.building_id),
  );
  const footprint = structuredClone(b.footprint_enu_m);
  const boxes = collisionBoxesForDetail(d);
  assert.equal(boxes.length, 3);
  attachCollisionBoxes([b], [{ buildingId: b.id, boxes }]);
  assert.equal(isBlocked(-450, -202, [b], 1000), true);
  assert.equal(isBlocked(-438.5, -185, [b], 1000), true);
  assert.deepEqual(b.footprint_enu_m, footprint);
  const graph = read("navigation.json");
  assert.equal(
    graph.edges.filter(([a, b]) =>
      segmentHitsBoxes(graph.nodes_enu_m[a], graph.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
  const router = createRouter(
    graph,
    (a, b) => !segmentHitsBoxes(a, b, boxes, 0.5),
    (a, b) => !segmentHitsBoxes(a, b, boxes, 0.5),
  );
  assert.ok(
    router.route([-448.403, 246.862], [-450, 185], { endBuilding: true }),
  );
});
