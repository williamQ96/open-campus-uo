import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
const read = (n) =>
  readFileSync(new URL("../public/scene/" + n, import.meta.url));
const cfg = JSON.parse(read("presentation.json")),
  bytes = read("pilot-plaza-plant-suppression.json"),
  patch = JSON.parse(bytes),
  fern = JSON.parse(read("pilot-fern-suppression.json"));
test("plaza plant suppression is independently source-pinned and disjoint from refined ferns", () => {
  const entry = cfg.additional_environment_patches.find(
    (e) => e.url === "pilot-plaza-plant-suppression.json",
  );
  assert.equal(createHash("sha256").update(bytes).digest("hex"), entry.sha256);
  assert.equal(patch.base_asset_sha256, cfg.asset_sha256);
  assert.equal(patch.target_name, "understory");
  assert.equal(patch.positions_gltf.length, 192);
  assert.equal(patch.expected_matches, 720);
  for (const p of patch.positions_gltf)
    assert.ok(
      !fern.positions_gltf.some(
        (q) => q.reduce((s, v, i) => s + (v - p[i]) ** 2, 0) < 1e-8,
      ),
    );
});
