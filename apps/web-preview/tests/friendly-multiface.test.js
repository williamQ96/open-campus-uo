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
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (n) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${n}`, import.meta.url)));
test("Friendly multi-elevation layer remains pinned and blocks its modeled mass", () => {
  const raw = readFileSync(
      new URL("../public/scene/friendly-west-detail.json", import.meta.url),
    ),
    d = JSON.parse(raw),
    p = read("presentation.json");
  assert.equal(
    p.exterior_details.find((x) => x.url === "friendly-west-detail.json")
      .sha256,
    createHash("sha256").update(raw).digest("hex"),
  );
  assert.equal(d.objects.length, 490);
  const group = createExteriorDetail(
    d,
    p.asset_sha256,
    new Set([d.building_id]),
  );
  assert.ok(group.children.some((o) => o.userData.asset_id === d.building_id));
  let b = structuredClone(
      read("manifest.json").buildings.find((x) => x.id === d.building_id),
    ),
    foot = structuredClone(b.footprint_enu_m),
    boxes = collisionBoxesForDetail(d);
  assert.equal(boxes.length, 4);
  attachCollisionBoxes([b], [{ buildingId: b.id, boxes }]);
  assert.equal(isBlocked(-356, -60, [b], 1000), true);
  assert.equal(isBlocked(-335, -35, [b], 1000), true);
  assert.deepEqual(b.footprint_enu_m, foot);
  let g = read("navigation.json");
  assert.equal(
    g.edges.filter(([a, c]) =>
      segmentHitsBoxes(g.nodes_enu_m[a], g.nodes_enu_m[c], boxes, 0.5),
    ).length,
    0,
  );
});
