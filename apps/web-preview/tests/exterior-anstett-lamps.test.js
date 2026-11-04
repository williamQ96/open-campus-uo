import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
const bytes = readFileSync(
  new URL("../public/scene/anstett-lamps-detail.json", import.meta.url),
);
const spec = JSON.parse(bytes);
const config = JSON.parse(
  readFileSync(new URL("../public/scene/presentation.json", import.meta.url)),
);
test("Anstett landscape geometry is pinned, selectable and retains the original building", () => {
  const entry = config.exterior_details.find(
    (x) => x.url === "anstett-lamps-detail.json",
  );
  assert.equal(entry.sha256, createHash("sha256").update(bytes).digest("hex"));
  assert.equal(spec.base_asset_sha256, config.asset_sha256);
  assert.equal(spec.replace_building, false);
  assert.equal(spec.building_id, "roof-0a498bf7");
  const group = createExteriorDetail(
    spec,
    config.asset_sha256,
    new Set([spec.building_id]),
  );
  assert.ok(group.children.some((x) => x.userData.asset_kind === "prop"));
  assert.ok(group.children.some((x) => x.userData.asset_kind === "vegetation"));
  assert.throws(() =>
    createExteriorDetail(spec, "changed", new Set([spec.building_id])),
  );
});
