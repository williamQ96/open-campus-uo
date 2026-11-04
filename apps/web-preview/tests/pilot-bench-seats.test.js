import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import * as THREE from "three";
import { applyVegetationPatch } from "../src/vegetation-patch.js";
import { createExteriorDetail } from "../src/exterior-detail.js";
const read = (n) =>
    readFileSync(new URL("../public/scene/" + n, import.meta.url)),
  sha = (b) => createHash("sha256").update(b).digest("hex");
test("nine seat patches are pinned, atomic and do not touch other vertices", () => {
  const c = JSON.parse(read("presentation.json")),
    bytes = read("pilot-bench-seat-suppression.json"),
    p = JSON.parse(bytes);
  assert.equal(
    c.additional_environment_patches.find(
      (e) => e.url === "pilot-bench-seat-suppression.json",
    ).sha256,
    sha(bytes),
  );
  assert.equal(p.base_asset_sha256, c.asset_sha256);
  const back = JSON.parse(read("pilot-bench-back-suppression.json"));
  assert.ok(
    p.positions_gltf.every((a) =>
      back.positions_gltf.every(
        (b) => a.reduce((n, v, i) => n + (v - b[i]) ** 2, 0) > 1e-8,
      ),
    ),
  );
  assert.equal(p.positions_gltf.length, 72);
  assert.equal(p.expected_matches, 216);
  const root = new THREE.Group(),
    target = new THREE.Group();
  target.name = "furniture";
  root.add(target);
  const g = new THREE.BufferGeometry(),
    vals = p.positions_gltf.flatMap((x) => [...x, ...x, ...x]);
  vals.push(777, 777, 777);
  g.setAttribute("position", new THREE.Float32BufferAttribute(vals, 3));
  target.add(new THREE.Mesh(g, new THREE.MeshBasicMaterial()));
  const before = Array.from(g.attributes.position.array);
  assert.throws(() => applyVegetationPatch(root, p, "wrong"));
  assert.deepEqual(Array.from(g.attributes.position.array), before);
  assert.equal(applyVegetationPatch(root, p, c.asset_sha256), 216);
  assert.deepEqual(
    [
      g.attributes.position.getX(216),
      g.attributes.position.getY(216),
      g.attributes.position.getZ(216),
    ],
    [777, 777, 777],
  );
  const raw = read("pilot-bench-detail.json"),
    d = JSON.parse(raw);
  assert.equal(
    c.exterior_details.find((e) => e.url === "pilot-bench-detail.json").sha256,
    sha(raw),
  );
  const s = d.objects.slice(-27);
  assert.equal(s.length, 27);
  assert.ok(
    s.every(
      (x) =>
        x.kind === "prop" &&
        x.material === "bench-wood" &&
        JSON.stringify(x.size) === "[3,0.18,0.24]",
    ),
  );
  assert.ok(createExteriorDetail(d, c.asset_sha256, new Set()).children.length);
});
