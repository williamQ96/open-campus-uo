import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const read = (url) => JSON.parse(readFileSync(new URL(url, import.meta.url)));
test("Fenton corner basement windows replace only the two lower source groups", () => {
  const d = read("../public/scene/fenton-south-detail.json");
  const old = read(
    "../../../assets/exterior-refinement/fenton-before-basement-windows-2026-11-04.json",
  );
  assert.deepEqual(d.objects.slice(0, old.objects.length), old.objects);
  assert.equal(d.objects.length, old.objects.length + 4);
  const previous = new Set(
    old.source_triangle_patch.triangles.map((t) => t[0]),
  );
  const current = d.source_triangle_patch.triangles.filter(
    (t) => !previous.has(t[0]),
  );
  assert.deepEqual(
    current.map((t) => t[0]),
    [
      ...Array.from({ length: 12 }, (_, i) => i + 872),
      ...Array.from({ length: 12 }, (_, i) => i + 1088),
    ],
  );
  assert.deepEqual(
    d.source_triangle_patch.triangles.filter((t) => previous.has(t[0])),
    old.source_triangle_patch.triangles,
  );
  const added = d.objects.slice(-4);
  assert.deepEqual(
    added.map((o) => o.material),
    ["stone", "glass", "stone", "glass"],
  );
  for (const o of added)
    assert.ok(
      o.position[1] === 4.974 &&
        o.size[1] <= 1.15 &&
        Math.abs(o.rotation[1]) > 0.6,
    );
});
