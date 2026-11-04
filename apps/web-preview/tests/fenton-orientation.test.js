import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
import { segmentHitsBoxes } from "../src/collision-supplement.js";
const read = (n) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${n}`, import.meta.url)));
test("Fenton east entrance and west stacks remain pinned and selectable", () => {
  let raw = readFileSync(
      new URL("../public/scene/fenton-south-detail.json", import.meta.url),
    ),
    d = JSON.parse(raw),
    p = read("presentation.json");
  assert.equal(
    p.exterior_details.find((x) => x.url === "fenton-south-detail.json").sha256,
    createHash("sha256").update(raw).digest("hex"),
  );
  assert.equal(d.building_id, "roof-4f0c798e");
  assert.equal(d.replace_building, false);
  assert.equal(d.objects.length, 155);
  assert.ok(
    d.objects.some(
      (x) =>
        x.material === "wood" && x.position[0] > -436 && x.position[2] < -28,
    ),
  );
  let group = createExteriorDetail(d, p.asset_sha256, new Set([d.building_id]));
  assert.ok(group.children.some((x) => x.userData.asset_id === d.building_id));
  let g = read("navigation.json"),
    boxes = [
      [-436.3, 27.3, -435.25, 34.7],
      [-475, 25.45, -466, 26],
      [-479, 27.25, -478, 34.75],
    ];
  assert.equal(
    g.edges.filter(([a, b]) =>
      segmentHitsBoxes(g.nodes_enu_m[a], g.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
});
