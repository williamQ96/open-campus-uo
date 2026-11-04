import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (n) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${n}`, import.meta.url)));
test("Gerlinger east, north and south layer remains pinned and selectable", () => {
  const raw = readFileSync(
      new URL("../public/scene/gerlinger-east-detail.json", import.meta.url),
    ),
    d = JSON.parse(raw),
    p = read("presentation.json");
  assert.equal(
    p.exterior_details.find((x) => x.url === "gerlinger-east-detail.json")
      .sha256,
    createHash("sha256").update(raw).digest("hex"),
  );
  assert.equal(d.building_id, "roof-9ac93ab7");
  assert.notEqual(d.replace_building, true);
  assert.equal(d.objects.length, 334);
  let g = createExteriorDetail(d, p.asset_sha256, new Set([d.building_id]));
  assert.ok(g.children.some((x) => x.userData.asset_id === d.building_id));
  for (let o of g.children)
    for (let v of o.geometry.attributes.position.array)
      assert.ok(Number.isFinite(v));
});
