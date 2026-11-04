import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
import { segmentHitsBoxes } from "../src/collision-supplement.js";
const read = (p) => readFileSync(new URL(p, import.meta.url));
test("power station detail and recolor are source pinned and avoid screened navigation graph", () => {
  const c = JSON.parse(read("../public/scene/presentation.json")),
    a = read("../public/scene/power-station-detail.json"),
    b = read("../public/scene/power-station-wall-color.json"),
    d = JSON.parse(a),
    patch = JSON.parse(b),
    sha = (x) => createHash("sha256").update(x).digest("hex");
  assert.equal(
    c.exterior_details.find((e) => e.url === "power-station-detail.json")
      .sha256,
    sha(a),
  );
  assert.equal(
    c.wall_color_patches.find((e) => e.url === "power-station-wall-color.json")
      .sha256,
    sha(b),
  );
  assert.equal(d.base_asset_sha256, c.asset_sha256);
  assert.equal(patch.base_asset_sha256, c.asset_sha256);
  assert.equal(d.building_id, "roof-2518e2a2");
  assert.equal(patch.building_id, d.building_id);
  assert.equal(d.replace_building, false);
  assert.equal(d.merge_source_vertex_count, 2906);
  assert.ok(
    createExteriorDetail(d, c.asset_sha256, new Set([d.building_id])).children
      .length,
  );
  const g = JSON.parse(read("../public/scene/navigation.json")),
    boxes = [
      [-290, 314, -260, 316],
      [-294.2, 318, -292.3, 325],
    ];
  assert.equal(
    g.edges.filter(([x, y]) =>
      segmentHitsBoxes(g.nodes_enu_m[x], g.nodes_enu_m[y], boxes, 0.5),
    ).length,
    0,
  );
});
