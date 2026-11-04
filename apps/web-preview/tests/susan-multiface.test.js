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
const read = (n) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${n}`, import.meta.url)));
test("Susan replacement retains identity and collision footprints", () => {
  let f = readFileSync(
      new URL("../public/scene/susan-roof-detail.json", import.meta.url),
    ),
    d = JSON.parse(f);
  assert.equal(
    read("presentation.json").exterior_details.find(
      (x) => x.url === "susan-roof-detail.json",
    ).sha256,
    createHash("sha256").update(f).digest("hex"),
  );
  let b = structuredClone(
      read("manifest.json").buildings.find((x) => x.id === d.building_id),
    ),
    original = structuredClone(b.footprint_enu_m),
    boxes = collisionBoxesForDetail(d);
  assert.equal(boxes.length, 4);
  attachCollisionBoxes([b], [{ buildingId: b.id, boxes }]);
  assert.equal(isBlocked(-451, 150, [b], 1000), true);
  assert.equal(isBlocked(-437, 163, [b], 1000), true);
  assert.deepEqual(b.footprint_enu_m, original);
  let g = read("navigation.json");
  assert.equal(
    g.edges.filter(([a, c]) =>
      segmentHitsBoxes(g.nodes_enu_m[a], g.nodes_enu_m[c], boxes, 0.5),
    ).length,
    0,
  );
});
