import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
import { segmentHitsBoxes } from "../src/collision-supplement.js";
const read = (n) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${n}`, import.meta.url)));
test("Oregon Hall east-wing layer is pinned, finite and leaves graph edges clear", () => {
  let raw = readFileSync(
      new URL("../public/scene/oregon-south-detail.json", import.meta.url),
    ),
    d = JSON.parse(raw),
    p = read("presentation.json");
  assert.equal(
    p.exterior_details.find((x) => x.url === "oregon-south-detail.json").sha256,
    createHash("sha256").update(raw).digest("hex"),
  );
  assert.equal(d.building_id, "roof-11d15952");
  assert.notEqual(d.replace_building, true);
  assert.equal(d.objects.length, 205);
  assert.equal(d.collision_boxes_enu_m, undefined);
  let group = createExteriorDetail(d, p.asset_sha256, new Set([d.building_id]));
  assert.ok(group.children.some((x) => x.userData.asset_id === d.building_id));
  for (let o of group.children)
    for (let v of o.geometry.attributes.position.array)
      assert.ok(Number.isFinite(v));
  let g = read("navigation.json"),
    boxes = [
      [51, 20.1, 64, 21.4],
      [66.78, 25, 67.9, 50],
      [63, 20, 68, 25],
      [63, 50, 68, 59],
    ];
  assert.equal(
    g.edges.filter(([a, b]) =>
      segmentHitsBoxes(g.nodes_enu_m[a], g.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
});
