import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (n) =>
  readFileSync(new URL("../public/scene/" + n, import.meta.url));
const cfg = JSON.parse(read("presentation.json")),
  bytes = read("anstett-south-detail.json"),
  spec = JSON.parse(bytes);
test("Anstett south elevation remains pinned and preserves landscape components", () => {
  const e = cfg.exterior_details.find(
    (x) => x.url === "anstett-south-detail.json",
  );
  assert.equal(createHash("sha256").update(bytes).digest("hex"), e.sha256);
  assert.equal(spec.building_id, "roof-0a498bf7");
  assert.equal(spec.replace_building, false);
  const group = createExteriorDetail(
    spec,
    cfg.asset_sha256,
    new Set([spec.building_id]),
  );
  assert.ok(group.children.some((x) => x.userData.asset_kind === "building"));
  assert.ok(group.children.some((x) => x.userData.asset_kind === "vegetation"));
  assert.ok(group.children.some((x) => x.userData.asset_kind === "prop"));
  assert.throws(() =>
    createExteriorDetail(spec, "changed", new Set([spec.building_id])),
  );
});
