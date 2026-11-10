import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  segmentHitsBoxes,
  collisionBoxesForDetail,
  attachCollisionBoxes,
} from "../src/collision-supplement.js";
import { isBlocked } from "../src/world.js";
const read = (p) => JSON.parse(readFileSync(new URL(p, import.meta.url)));
const d = read(
    "../../../assets/exterior-refinement/susan-before-parapet-arches-2026-11-10.json",
  ),
  before = read(
    "../../../assets/exterior-refinement/susan-before-courtyard-2026-11-04.json",
  ),
  nav = read("../public/scene/navigation.json");
test("Susan courtyard study preserves prior geometry and contains its two post envelopes", () => {
  const removed = new Set([5, 6, 7, 8, 210, 211, 212, 213]),
    remaining = before.objects.filter((_, i) => !removed.has(i));
  assert.deepEqual(d.objects.slice(0, remaining.length), remaining);
  assert.equal(d.objects.length, remaining.length + 11);
  assert.deepEqual(
    d.collision_boxes_enu_m.slice(0, 2),
    before.collision_boxes_enu_m,
  );
  const posts = d.objects
    .slice(remaining.length)
    .filter((o) => o.shape === "column");
  assert.equal(posts.length, 2);
  const boxes = d.collision_boxes_enu_m.slice(2);
  assert.equal(boxes.length, 2);
  for (let i = 0; i < 2; i++) {
    const [x, , z] = posts[i].position,
      [x1, n1, x2, n2] = boxes[i];
    assert.ok(x1 < x && x < x2 && n1 < -z && -z < n2);
  }
  const building = structuredClone(
    read("../public/scene/manifest.json").buildings.find(
      (b) => b.id === d.building_id,
    ),
  );
  attachCollisionBoxes(
    [building],
    [{ buildingId: d.building_id, boxes: collisionBoxesForDetail(d) }],
  );
  for (const [x, , z] of posts.map((post) => post.position))
    assert.equal(isBlocked(x, z, [building], 1000), true);
  assert.equal(
    nav.edges.filter(([a, b]) =>
      segmentHitsBoxes(nav.nodes_enu_m[a], nav.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
});
