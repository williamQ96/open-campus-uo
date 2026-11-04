import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const read = (p) => JSON.parse(readFileSync(new URL(p, import.meta.url)));
test("Straub west roof preserves source geometry, identity and navigation", () => {
  const before = read(
    "../../../assets/exterior-refinement/straub-before-roof-2026-11-04.json",
  );
  const after = read("../public/scene/straub-west-detail.json");
  assert.equal(after.building_id, "roof-5ded2bf0");
  assert.equal(after.replace_building, false);
  assert.equal(after.base_asset_sha256, before.base_asset_sha256);
  assert.deepEqual(
    after.objects.slice(0, before.objects.length),
    before.objects,
  );
  assert.equal(after.objects.length, before.objects.length + 2);
  assert.deepEqual(after.collision_boxes_enu_m, before.collision_boxes_enu_m);
  const [attic, roof] = after.objects.slice(-2);
  assert.equal(attic.material, "stone");
  assert.equal(roof.shape, "ridge");
  assert.ok(attic.position[0] - attic.size[0] / 2 > -195.43);
  assert.ok(roof.position[1] >= 13.67 && roof.size[1] > 0);
});
