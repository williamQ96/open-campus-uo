import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as T from "three";
import { applyCanopyTone } from "../src/canopy-tone.js";
const read = (n) =>
  readFileSync(new URL("../public/scene/" + n, import.meta.url));
const config = JSON.parse(read("presentation.json")),
  raw = read("pilot-canopy-tone.json"),
  spec = JSON.parse(raw);
function fixture() {
  let root = new T.Group(),
    group = new T.Group();
  group.name = "vegetation";
  root.add(group);
  for (const [i, r] of spec.meshes.entries()) {
    const g = new T.BufferGeometry();
    g.setAttribute(
      "position",
      new T.Float32BufferAttribute([i, 1, 1, i + 1, 2, 3, i + 2, 3, 5], 3),
    );
    const m = new T.MeshStandardMaterial({ color: "#" + r.color });
    m.name = r.material;
    const o = new T.Mesh(g, m);
    o.name = r.name;
    group.add(o);
  }
  const trunk = new T.Mesh(new T.BoxGeometry(), new T.MeshStandardMaterial());
  trunk.name = "vegetation_1";
  group.add(trunk);
  return { root, group };
}
function small() {
  return { ...spec, meshes: spec.meshes.map((r) => ({ ...r, vertices: 3 })) };
}
test("canopy tone is source pinned, deterministic, bounded, and leaves trunk and positions untouched", () => {
  assert.equal(
    config.additional_environment_patches.find(
      (e) => e.url === "pilot-canopy-tone.json",
    ).sha256,
    createHash("sha256").update(raw).digest("hex"),
  );
  const a = fixture(),
    b = fixture(),
    s = small();
  const before = a.group.children.map((o) => [
    ...o.geometry.attributes.position.array,
  ]);
  assert.equal(applyCanopyTone(a.root, s, s.base_asset_sha256), 9);
  assert.equal(applyCanopyTone(b.root, s, s.base_asset_sha256), 9);
  for (let i = 0; i < 3; i++) {
    const m = a.group.children[i],
      c = m.geometry.attributes.color;
    assert.deepEqual(
      [...c.array],
      [...b.group.children[i].geometry.attributes.color.array],
    );
    assert.deepEqual([...m.geometry.attributes.position.array], before[i]);
    assert.ok([...c.array].every((v) => v >= 1 - s.strength - 1e-6 && v <= 1));
    assert.equal(m.material.vertexColors, true);
  }
  assert.equal(a.group.children[3].geometry.hasAttribute("color"), false);
});
test("source or batch mismatch rejects the entire operation before mutation", () => {
  let f = fixture(),
    s = small();
  s.meshes[1].vertices = 4;
  assert.throws(() => applyCanopyTone(f.root, s, s.base_asset_sha256));
  assert.ok(f.group.children.every((o) => !o.geometry.hasAttribute("color")));
  assert.throws(() => applyCanopyTone(f.root, small(), "wrong"));
  assert.ok(f.group.children.every((o) => !o.geometry.hasAttribute("color")));
});
