import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
const data = readFileSync(
  new URL("../public/scene/volcanology-south-detail.json", import.meta.url),
);
const spec = JSON.parse(data);
const config = JSON.parse(
  readFileSync(new URL("../public/scene/presentation.json", import.meta.url)),
);
test("provisional facade loads against the pinned model and leaves its source building intact", () => {
  const entry = config.exterior_details.find(
    (x) => x.url === "volcanology-south-detail.json",
  );
  assert.equal(entry.sha256, createHash("sha256").update(data).digest("hex"));
  assert.equal(spec.base_asset_sha256, config.asset_sha256);
  assert.equal(spec.building_id, "roof-399a0551");
  assert.equal(spec.replace_building, false);
  assert.ok(
    createExteriorDetail(spec, config.asset_sha256, new Set([spec.building_id]))
      .children.length,
  );
  assert.throws(() =>
    createExteriorDetail(spec, "changed", new Set([spec.building_id])),
  );
});
