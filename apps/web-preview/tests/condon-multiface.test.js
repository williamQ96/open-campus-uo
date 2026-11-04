import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (n) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${n}`, import.meta.url)));
test("Condon overlay remains source pinned and preserves base identity", () => {
  let bytes = readFileSync(
      new URL("../public/scene/condon-east-detail.json", import.meta.url),
    ),
    d = JSON.parse(bytes),
    config = read("presentation.json");
  assert.equal(
    config.exterior_details.find((x) => x.url === "condon-east-detail.json")
      .sha256,
    createHash("sha256").update(bytes).digest("hex"),
  );
  assert.equal(d.replace_building, false);
  assert.equal(d.building_id, "roof-7ffcf31b");
  assert.equal(d.objects.length, 50);
  assert.equal(d.collision_boxes_enu_m, undefined);
  let group = createExteriorDetail(
    d,
    config.asset_sha256,
    new Set([d.building_id]),
  );
  assert.ok(group.children.some((o) => o.userData.asset_id === d.building_id));
});
