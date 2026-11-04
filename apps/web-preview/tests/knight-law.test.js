import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
import { segmentHitsBoxes } from "../src/collision-supplement.js";
const read = (p) => readFileSync(new URL(p, import.meta.url));
test("law center western study remains pinned and clear of sampled navigation graph", () => {
  const c = JSON.parse(read("../public/scene/presentation.json")),
    a = read("../public/scene/knight-law-west-detail.json"),
    b = read("../public/scene/knight-law-wall-color.json"),
    d = JSON.parse(a),
    patch = JSON.parse(b),
    sha = (x) => createHash("sha256").update(x).digest("hex");
  assert.equal(
    c.exterior_details.find((e) => e.url === "knight-law-west-detail.json")
      .sha256,
    sha(a),
  );
  assert.equal(
    c.wall_color_patches.find((e) => e.url === "knight-law-wall-color.json")
      .sha256,
    sha(b),
  );
  assert.equal(d.base_asset_sha256, c.asset_sha256);
  assert.equal(patch.base_asset_sha256, c.asset_sha256);
  assert.equal(d.building_id, "roof-f52041e8");
  assert.equal(patch.building_id, d.building_id);
  assert.equal(d.replace_building, false);
  assert.equal(d.merge_source_vertex_count, 6200);
  assert.equal(patch.expected_vertices, 424);
  assert.equal(d.objects.filter((o) => o.shape === "gable").length, 2);
  assert.ok(
    createExteriorDetail(d, c.asset_sha256, new Set([d.building_id])).children
      .length,
  );
  const g = JSON.parse(read("../public/scene/navigation.json")),
    boxes = [
      [118.6, -286.5, 119.1, -284.5],
      [118.6, -291, 119.1, -289],
      [118.6, -295.6, 119.1, -294.4],
      [111.6, -321.5, 112.1, -320.5],
      [108.6, -353.5, 109.1, -352.5],
    ];
  assert.equal(
    g.edges.filter(([x, y]) =>
      segmentHitsBoxes(g.nodes_enu_m[x], g.nodes_enu_m[y], boxes, 0.5),
    ).length,
    0,
  );
});
