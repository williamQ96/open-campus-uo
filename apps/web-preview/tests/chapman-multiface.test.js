import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (n) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${n}`, import.meta.url)));
test("Chapman multi-elevation layer is pinned and retains building identity", () => {
  const raw = readFileSync(
      new URL("../public/scene/chapman-west-detail.json", import.meta.url),
    ),
    d = JSON.parse(raw),
    p = read("presentation.json");
  assert.equal(
    p.exterior_details.find((x) => x.url === "chapman-west-detail.json").sha256,
    createHash("sha256").update(raw).digest("hex"),
  );
  assert.equal(d.building_id, "roof-f5cea51d");
  assert.equal(d.replace_building, false);
  const historical = JSON.parse(
    readFileSync(
      new URL(
        "../../../assets/exterior-refinement/chapman-before-west-frieze-2026-11-10.json",
        import.meta.url,
      ),
    ),
  );
  assert.equal(historical.objects.length, 144);
  assert.deepEqual(d.objects.slice(0, 144), historical.objects);
  assert.equal(d.objects.length, 144 + 121);
  assert.equal(d.collision_boxes_enu_m, undefined);
  let g = createExteriorDetail(d, p.asset_sha256, new Set([d.building_id]));
  assert.ok(g.children.some((x) => x.userData.asset_id === d.building_id));
  for (const child of g.children)
    for (const value of child.geometry.attributes.position.array)
      assert.ok(Number.isFinite(value));
});
