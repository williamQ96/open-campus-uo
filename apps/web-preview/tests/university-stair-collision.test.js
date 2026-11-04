import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as THREE from "three";
import {
  attachCollisionBoxes,
  collisionBoxesForDetail,
  segmentHitsBoxes,
} from "../src/collision-supplement.js";
import { inferEntrances } from "../src/entrances.js";
import { isBlocked, movePlayer } from "../src/world.js";
const read = (url) => JSON.parse(readFileSync(new URL(url, import.meta.url)));
test("University stair collision covers wings and rails while leaving two side lanes and graph clear", () => {
  const detail = read("../public/scene/university-hall-detail.json"),
    old = read(
      "../../../assets/exterior-refinement/university-before-stair-collision-2026-11-04.json",
    );
  const buildings = read("../public/scene/manifest.json").buildings,
    nav = read("../public/scene/navigation.json"),
    boxes = collisionBoxesForDetail(detail);
  assert.deepEqual(detail.objects, old.objects);
  assert.equal(boxes.length, 6);
  const before = inferEntrances(buildings, 1000);
  for (const wing of detail.objects.filter((o) => o.shape === "stair-wing")) {
    const [x, , z] = wing.position;
    assert.ok(
      boxes.some(
        ([x0, n0, x1, n1]) =>
          x0 <= x - wing.size[0] / 2 + 1e-6 &&
          x1 >= x + wing.size[0] / 2 - 1e-6 &&
          n0 <= -z - wing.size[2] / 2 + 1e-6 &&
          n1 >= -z + wing.size[2] / 2 - 1e-6,
      ),
    );
  }
  for (const rail of detail.objects.filter(
    (o) => o.material === "metal" && o.size[0] === 2,
  )) {
    const [x, , z] = rail.position;
    const reach =
      (rail.size[0] * Math.abs(Math.cos(rail.rotation[2])) +
        rail.size[1] * Math.abs(Math.sin(rail.rotation[2]))) /
      2;
    assert.ok(
      boxes.some(
        ([x0, n0, x1, n1]) =>
          x0 <= x - reach &&
          x1 >= x + reach &&
          n0 <= -z - rail.size[2] / 2 &&
          n1 >= -z + rail.size[2] / 2,
      ),
    );
  }
  attachCollisionBoxes(buildings, [{ buildingId: detail.building_id, boxes }]);
  assert.deepEqual(inferEntrances(buildings, 1000), before);
  assert.equal(
    nav.edges.filter(([a, b]) =>
      segmentHitsBoxes(nav.nodes_enu_m[a], nav.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
  for (const x of [-472.5, -441.5])
    assert.deepEqual(
      [-126.77, -125.85, -125, -124.15, -123.23].map((z) =>
        isBlocked(x, z, buildings, 1000),
      ),
      [true, false, true, false, true],
    );
  for (const [start, end] of [
    [-474.2, -471.7],
    [-439.8, -442.3],
  ])
    for (const z of [-125.85, -124.15]) {
      const p = new THREE.Vector3(start, 0, z);
      movePlayer(p, { x: end - start, z: 0 }, buildings, 1000, null, false);
      assert.ok(Math.abs(p.x - end) < 0.01);
    }
});
