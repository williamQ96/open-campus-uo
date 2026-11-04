import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
test("Cascade wall study is source pinned", () => {
  const read = (p) => readFileSync(new URL(p, import.meta.url));
  const c = JSON.parse(read("../public/scene/presentation.json")),
    data = read("../public/scene/cascade-wall-color.json"),
    p = JSON.parse(data);
  assert.equal(
    c.wall_color_patches.find((x) => x.url === "cascade-wall-color.json")
      .sha256,
    createHash("sha256").update(data).digest("hex"),
  );
  assert.equal(p.base_asset_sha256, c.asset_sha256);
  assert.equal(p.building_id, "roof-f42d2ea3");
  assert.equal(p.expected_vertices, 348);
});
