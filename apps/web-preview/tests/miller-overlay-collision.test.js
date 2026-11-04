import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  overlayCollisionBoxesForDetail,
  attachCollisionBoxes,
  segmentHitsBoxes,
} from "../src/collision-supplement.js";
import { isBlocked, movePlayer } from "../src/world.js";
const read = (n) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${n}`, import.meta.url)));
test("Miller shallow frontage blocks player and stays off navigation routes", () => {
  const d = read("miller-west-detail.json"),
    b = structuredClone(
      read("manifest.json").buildings.find((x) => x.id === d.building_id),
    ),
    boxes = overlayCollisionBoxesForDetail(d);
  assert.equal(isBlocked(-519.25, -184, [b], 1000, 0.01), false);
  attachCollisionBoxes([b], [{ buildingId: b.id, boxes, overlay: true }]);
  assert.equal(isBlocked(-519.25, -184, [b], 1000, 0.01), true);
  assert.equal(isBlocked(-521, -184, [b], 1000, 0.01), false);
  let pos = { x: -521, y: 0, z: -184 };
  movePlayer(pos, { x: 3, z: 0 }, [b], 1000, null, false);
  assert.ok(pos.x < -519.36);
  const g = read("navigation.json");
  assert.equal(
    g.edges.filter(([a, b]) =>
      segmentHitsBoxes(g.nodes_enu_m[a], g.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
});
test("overlay envelopes require thin bounded boxes beside the intended footprint", () => {
  const d = read("miller-west-detail.json"),
    b = structuredClone(
      read("manifest.json").buildings.find((x) => x.id === d.building_id),
    );
  assert.throws(
    () => overlayCollisionBoxesForDetail({ ...d, replace_building: true }),
    /Invalid/,
  );
  assert.throws(
    () =>
      overlayCollisionBoxesForDetail({
        ...d,
        overlay_collision_boxes_enu_m: [[0, 0, 2, 2]],
      }),
    /Invalid/,
  );
  assert.throws(
    () =>
      attachCollisionBoxes(
        [b],
        [{ buildingId: b.id, boxes: [[-600, 100, -599, 110]], overlay: true }],
      ),
    /adjacent/,
  );
  assert.equal(b.collision_extra_enu_m, undefined);
});
