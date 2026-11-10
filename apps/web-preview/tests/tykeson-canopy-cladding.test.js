import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (p) => JSON.parse(readFileSync(new URL(p, import.meta.url)));
const d = read("../public/scene/tykeson-north-detail.json");
const old = read(
  "../../../assets/exterior-refinement/tykeson-before-canopy-cladding-2026-11-10.json",
);
test("Tykeson canopy frame and pane envelope preserve all unrelated original components", () => {
  assert.equal(old.objects.length, 52);
  assert.equal(d.objects.length, 171);
  for (let i = 0; i < 52; i++)
    if (i !== 34 && i !== 35) assert.deepEqual(d.objects[i], old.objects[i]);
  const parts = d.objects.filter((x) => x.role?.startsWith("canopy-"));
  assert.equal(parts.filter((x) => x.role === "canopy-rib").length, 16);
  assert.equal(parts.filter((x) => x.role === "canopy-pane").length, 15);
  for (const o of parts) {
    const lo = o.position.map((v, i) => v - o.size[i] / 2),
      hi = o.position.map((v, i) => v + o.size[i] / 2);
    assert.ok(lo[0] >= -457.1 - 1e-6 && hi[0] <= -437.9 + 1e-6);
    assert.ok(lo[2] >= 27 - 1e-6 && hi[2] <= 30.2 + 1e-6);
    assert.ok(lo[1] >= 6.875 && hi[1] <= 7.22);
  }
});
test("Tykeson cladding seams do not cross either existing upper window row", () => {
  const seams = d.objects.filter((x) => x.role === "cladding-seam");
  assert.ok(seams.length > 50);
  const wins = old.objects.filter(
    (x) => x.material === "dark" && x.position[1] > 15,
  );
  for (const s of seams)
    for (const w of wins) {
      const overlap = [0, 1].every(
        (i) =>
          Math.abs(s.position[i] - w.position[i]) < (s.size[i] + w.size[i]) / 2,
      );
      assert.equal(overlap, false);
    }
  const mk = (s) =>
    createExteriorDetail(s, s.base_asset_sha256, new Set([s.building_id]));
  assert.equal(mk(d).children.length, mk(old).children.length);
  const bytes = readFileSync(
    new URL("../public/scene/tykeson-north-detail.json", import.meta.url),
  );
  const p = read("../public/scene/presentation.json");
  assert.equal(
    p.exterior_details.find((x) => x.url === "tykeson-north-detail.json")
      .sha256,
    createHash("sha256").update(bytes).digest("hex"),
  );
});
