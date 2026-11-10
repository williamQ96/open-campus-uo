import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
const bytes = readFileSync(
  new URL(
    "../public/scene/knight-library-window-reveals.json",
    import.meta.url,
  ),
);
const spec = JSON.parse(bytes);
test("Knight seven masonry reveals preserve glazing aperture and use actual depth", () => {
  const p = JSON.parse(
    readFileSync(new URL("../public/scene/presentation.json", import.meta.url)),
  );
  assert.equal(
    p.exterior_details.find(
      (x) => x.url === "knight-library-window-reveals.json",
    ).sha256,
    createHash("sha256").update(bytes).digest("hex"),
  );
  assert.equal(spec.replace_building, false);
  assert.equal(spec.objects.filter((x) => x.role === "jamb").length, 14);
  assert.equal(spec.objects.filter((x) => x.role === "head").length, 7);
  for (const x of spec.objects.filter((x) => x.role === "jamb")) {
    assert.equal(x.size[2], 1);
    assert.equal(x.size[1], 7.9);
  }
  // Existing pane spans +/-1.82 m horizontally; clear opening stays +/-1.90.
  const centers = [-590, -580.6, -571.2, -561.8, -552.4, -543, -533.6];
  for (const c of centers) {
    const jambs = spec.objects.filter(
      (x) => x.role === "jamb" && Math.abs(x.position[0] - c) < 3,
    );
    assert.equal(jambs.length, 2);
    for (const j of jambs)
      assert.ok(Math.abs(j.position[0] - c) - j.size[0] / 2 > 1.89);
  }
  const g = createExteriorDetail(
    spec,
    spec.base_asset_sha256,
    new Set([spec.building_id]),
  );
  assert.equal(g.children.length, 1);
  for (const v of g.children[0].geometry.attributes.position.array)
    assert.ok(Number.isFinite(v));
  assert.throws(
    () => createExteriorDetail(spec, "wrong", new Set([spec.building_id])),
    /does not match/,
  );
});
