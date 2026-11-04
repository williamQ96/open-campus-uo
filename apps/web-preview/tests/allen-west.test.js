import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
import { segmentHitsBoxes } from "../src/collision-supplement.js";
const read = (p) => readFileSync(new URL(p, import.meta.url));
test("Allen west overlay stays pinned and does not cross the screened navigation graph", () => {
  const data = read("../public/scene/allen-west-detail.json"),
    spec = JSON.parse(data),
    config = JSON.parse(read("../public/scene/presentation.json"));
  assert.equal(
    config.exterior_details.find((x) => x.url === "allen-west-detail.json")
      .sha256,
    createHash("sha256").update(data).digest("hex"),
  );
  assert.equal(spec.base_asset_sha256, config.asset_sha256);
  assert.equal(spec.building_id, "roof-7b7893d6");
  assert.equal(spec.replace_building, false);
  assert.ok(
    createExteriorDetail(spec, config.asset_sha256, new Set([spec.building_id]))
      .children.length,
  );
  assert.throws(() =>
    createExteriorDetail(spec, "changed", new Set([spec.building_id])),
  );
  const g = JSON.parse(read("../public/scene/navigation.json"));
  const boxes = [[-368.7, 79, -366.8, 102]];
  assert.equal(
    g.edges.filter(([a, b]) =>
      segmentHitsBoxes(g.nodes_enu_m[a], g.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
});
