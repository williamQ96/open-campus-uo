import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
const bytes = readFileSync(
  new URL(
    "../public/scene/gerlinger-east-masonry-detail.json",
    import.meta.url,
  ),
);
const s = JSON.parse(bytes);
test("Gerlinger source-pinned masonry retains clear sash and awning gap", () => {
  const p = JSON.parse(
    readFileSync(new URL("../public/scene/presentation.json", import.meta.url)),
  );
  assert.equal(
    p.exterior_details.find(
      (x) => x.url === "gerlinger-east-masonry-detail.json",
    ).sha256,
    createHash("sha256").update(bytes).digest("hex"),
  );
  assert.equal(s.replace_building, false);
  assert.equal(s.objects.filter((x) => x.role === "quoin").length, 36);
  assert.equal(s.objects.filter((x) => x.role === "window-crown").length, 15);
  for (const o of s.objects.filter((x) => x.role === "window-crown")) {
    const a = Math.abs(o.rotation[0]),
      half = (o.size[1] * Math.cos(a) + o.size[2] * Math.sin(a)) / 2;
    assert.ok(o.position[1] - half > 17.683);
    assert.ok(o.position[1] + half < 18.033);
  }
  const g = createExteriorDetail(
    s,
    s.base_asset_sha256,
    new Set([s.building_id]),
  );
  assert.equal(g.children.length, 1);
  for (const v of g.children[0].geometry.attributes.position.array)
    assert.ok(Number.isFinite(v));
  assert.throws(
    () => createExteriorDetail(s, "wrong", new Set([s.building_id])),
    /does not match/,
  );
});
