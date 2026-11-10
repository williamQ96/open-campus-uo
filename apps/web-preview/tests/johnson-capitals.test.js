import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createExteriorDetail } from "../src/exterior-detail.js";
import * as T from "three";
const s = JSON.parse(
  readFileSync(
    new URL("../public/scene/johnson-north-capitals.json", import.meta.url),
  ),
);
test("Johnson six paired volutes retain source centers and stay within existing capital envelope", () => {
  assert.equal(s.replace_building, false);
  let d = createExteriorDetail(
    s,
    s.base_asset_sha256,
    new Set([s.building_id]),
  );
  assert.equal(d.children.length, 1);
  const b = new T.Box3().setFromObject(d);
  assert.ok(b.min.y > 14.4 && b.max.y < 15.3);
  assert.ok(b.min.z > 24.7 && b.max.z < 26.5);
  assert.equal(s.objects.filter((x) => x.role === "volute").length, 12);
  assert.deepEqual(
    s.objects.filter((x) => x.role === "abacus").map((x) => x.position[0]),
    [-414, -408.8, -403.6, -398.4, -393.2, -388],
  );
  for (const v of d.children[0].geometry.attributes.position.array)
    assert.ok(Number.isFinite(v));
  assert.throws(() =>
    createExteriorDetail(s, "wrong", new Set([s.building_id])),
  );
  d.children[0].geometry.dispose();
  d.children[0].material.dispose();
});
