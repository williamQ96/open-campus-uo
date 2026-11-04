import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
import { segmentHitsBoxes } from "../src/collision-supplement.js";
const read = (p) => readFileSync(new URL(p, import.meta.url));
test("Miller west frontage remains pinned and clear of sampled routes", () => {
  const c = JSON.parse(read("../public/scene/presentation.json")),
    a = read("../public/scene/miller-west-detail.json"),
    b = read("../public/scene/miller-wall-color.json"),
    d = JSON.parse(a),
    p = JSON.parse(b),
    sha = (x) => createHash("sha256").update(x).digest("hex");
  assert.equal(
    c.exterior_details.find((e) => e.url === "miller-west-detail.json").sha256,
    sha(a),
  );
  assert.equal(
    c.wall_color_patches.find((e) => e.url === "miller-wall-color.json").sha256,
    sha(b),
  );
  assert.equal(d.base_asset_sha256, c.asset_sha256);
  assert.equal(p.base_asset_sha256, c.asset_sha256);
  assert.equal(d.building_id, "roof-944fcd46");
  assert.equal(p.building_id, d.building_id);
  assert.equal(d.merge_source_vertex_count, 3364);
  assert.equal(p.expected_vertices, 128);
  assert.ok(
    createExteriorDetail(d, c.asset_sha256, new Set([d.building_id])).children
      .length,
  );
  const g = JSON.parse(read("../public/scene/navigation.json")),
    boxes = [[-520.05, 178.5, -519.05, 189.5]];
  assert.equal(
    g.edges.filter(([x, y]) =>
      segmentHitsBoxes(g.nodes_enu_m[x], g.nodes_enu_m[y], boxes, 0.5),
    ).length,
    0,
  );
});
