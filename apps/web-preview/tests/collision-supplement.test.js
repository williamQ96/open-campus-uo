import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  collisionBoxesForDetail,
  attachCollisionBoxes,
  segmentHitsBoxes,
} from "../src/collision-supplement.js";
import { isBlocked, movePlayer } from "../src/world.js";
import { createRouter } from "../src/routing.js";
const read = (name) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${name}`, import.meta.url)));
test("Collier replacement blocks its visible solid envelope while retaining original footprint", () => {
  const spec = read("collier-house-detail.json"),
    manifest = read("manifest.json");
  const b = structuredClone(
    manifest.buildings.find((v) => v.id === spec.building_id),
  );
  const original = structuredClone(b.footprint_enu_m);
  assert.equal(isBlocked(-345, 47, [b], 1000), false);
  const boxes = collisionBoxesForDetail(spec);
  assert.equal(
    attachCollisionBoxes([b], [{ buildingId: b.id, boxes }]).length,
    7,
  );
  assert.equal(isBlocked(-334, 53.5, [b], 1000), true);
  assert.equal(isBlocked(-332, 53.5, [b], 1000), false);
  const east = { x: -331, y: 0, z: 53.5 };
  movePlayer(east, { x: -6, z: 0 }, [b], 1000, null, false);
  assert.ok(east.x > -333.3, `player crossed the east porch: ${east.x}`);
  assert.equal(isBlocked(-345, 47, [b], 1000), true);
  assert.equal(isBlocked(-345, 42, [b], 1000), false);
  assert.deepEqual(b.footprint_enu_m, original);
  const p = { x: -345, y: 0, z: 42 };
  movePlayer(p, { x: 0, z: 10 }, [b], 1000, null, false);
  assert.ok(p.z < 43.535, `player crossed the visible stairs: ${p.z}`);
  assert.throws(
    () => collisionBoxesForDetail({ ...spec, replace_building: false }),
    /Invalid/,
  );
  assert.throws(
    () =>
      collisionBoxesForDetail({
        ...spec,
        collision_boxes_enu_m: [[1, 2, 0, 4]],
      }),
    /Invalid/,
  );
  assert.throws(
    () => attachCollisionBoxes([b], [{ buildingId: "unknown", boxes }]),
    /Invalid/,
  );
});
test("extra collision rectangles reject crossing graph edges without changing this campus graph", () => {
  const boxes = collisionBoxesForDetail(read("collier-house-detail.json"));
  assert.equal(segmentHitsBoxes([-345, -42], [-345, -48], boxes, 0.5), true);
  assert.equal(segmentHitsBoxes([-370, -42], [-370, -48], boxes, 0.5), false);
  const graph = read("navigation.json");
  assert.equal(
    graph.edges.filter(([a, b]) =>
      segmentHitsBoxes(graph.nodes_enu_m[a], graph.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
  const tiny = {
    version: 1,
    nodes_enu_m: [
      [0, 0],
      [1, 0],
      [2, 0],
    ],
    edges: [
      [0, 1, 1, "pedestrian"],
      [1, 2, 1, "pedestrian"],
    ],
  };
  const router = createRouter(
    tiny,
    (a, b) => !segmentHitsBoxes(a, b, [[0.4, -0.1, 0.6, 0.1]]),
    (a, b) => !segmentHitsBoxes(a, b, [[0.4, -0.1, 0.6, 0.1]]),
  );
  assert.equal(router.route([0, 0], [2, 0]), null);
});
