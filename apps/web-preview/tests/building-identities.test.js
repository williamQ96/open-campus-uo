import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { applyBuildingIdentities } from "../src/building-identities.js";
import { resolveBuildingHit } from "../src/building-highlight.js";
const read = (name) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${name}`, import.meta.url)));
test("proposed identities are source-pinned, explicit and applied atomically", () => {
  const base = read("manifest.json"),
    data = read("building-identities.json"),
    id = "roof-399a0551";
  const valid = structuredClone(base),
    before = JSON.stringify(
      valid.buildings.find((b) => b.id === id).footprint_enu_m,
    );
  assert.equal(applyBuildingIdentities(valid, data), 1);
  const row = valid.buildings.find((b) => b.id === id);
  assert.equal(row.name, "Volcanology (approximate)");
  assert.equal(row.name_match, "approximate-map-match");
  assert.equal(JSON.stringify(row.footprint_enu_m), before);
  for (const modify of [
    (d) => (d.source_model_sha256 = "different"),
    (d) => (d.records[0].expected_footprint_enu_m[0][0] += 1),
    (d) => d.records.push(structuredClone(d.records[0])),
    (d) => (d.records[0].source_url = "https://example.com/"),
  ]) {
    const m = structuredClone(base),
      bad = structuredClone(data);
    modify(bad);
    assert.throws(() => applyBuildingIdentities(m, bad));
    assert.equal(m.buildings.find((b) => b.id === id).name, undefined);
  }
  const m = structuredClone(base);
  m.buildings.find((b) => b.id === id).name = "Already named";
  assert.throws(() => applyBuildingIdentities(m, data));
  assert.equal(m.buildings.find((b) => b.id === id).name, "Already named");
});

test("an annotated building remains selectable inside its existing context batch", () => {
  const manifest = read("manifest.json"),
    data = read("building-identities.json");
  applyBuildingIdentities(manifest, data);
  const row = manifest.buildings.find((b) => b.id === "roof-399a0551");
  const hit = {
    object: {
      userData: { asset_kind: "context-building-batch", asset_ids: [row.id] },
    },
    point: { x: -236, z: -35 },
  };
  assert.equal(resolveBuildingHit(hit, new Map([[row.id, row]])), row.id);
});
