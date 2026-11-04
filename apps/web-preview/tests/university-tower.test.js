import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const read = (p) => JSON.parse(readFileSync(new URL(p, import.meta.url)));
const current = read(
  "../../../assets/exterior-refinement/university-before-mansard-2026-11-04.json",
);
const latest = read("../public/scene/university-hall-detail.json");
const previous = read(
  "../../../assets/exterior-refinement/university-before-tower-2026-11-04.json",
);
test("University towers retain the existing scene and use aligned triple arches and roof crests", () => {
  assert.equal(current.building_id, previous.building_id);
  assert.equal(current.base_asset_sha256, previous.base_asset_sha256);
  const removed = new Set([154, 155, 158, 159]);
  const unchanged = previous.objects.filter((_, i) => !removed.has(i));
  assert.deepEqual(current.objects.slice(0, unchanged.length), unchanged);
  const additions = current.objects.slice(unchanged.length);
  assert.deepEqual(
    latest.objects.slice(unchanged.length, current.objects.length),
    additions,
  );
  assert.equal(current.objects.length, 480);
  for (const x of [-471.05, -442.95]) {
    const surrounds = additions.filter(
      (o) =>
        o.shape === "arch-x" &&
        o.material === "stone" &&
        Math.abs(o.position[0] - x) < 1e-6,
    );
    assert.deepEqual(
      surrounds.map((o) => o.position[2]),
      [-126.18, -125, -123.82],
    );
    assert.ok(
      additions.some(
        (o) =>
          o.material === "dark" &&
          Math.abs(o.position[0] - (x < -450 ? -468 : -446)) < 1e-6 &&
          o.position[1] === 24.56,
      ),
    );
  }
});
