import fs from "node:fs";
import assert from "node:assert/strict";
import { createExteriorDetail } from "../src/exterior-detail.js";
import test from "node:test";
import { createHash } from "node:crypto";
test("Friendly four outer shafts are round; all other geometry, bounds and mesh count stay exact", () => {
  const before = JSON.parse(
    fs.readFileSync(
      new URL(
        "../../../assets/exterior-refinement/friendly-before-round-shafts-2026-11-10.json",
        import.meta.url,
      ),
    ),
  );
  const after = JSON.parse(
    fs.readFileSync(
      new URL("../public/scene/friendly-west-detail.json", import.meta.url),
    ),
  );
  const indices = [10, 11, 23, 24];
  for (const i of indices) assert.equal(after.objects[i].shape, "column");
  const reverted = structuredClone(after);
  for (const i of indices) reverted.objects[i].shape = "box";
  assert.deepEqual(reverted, before);
  const create = (s) =>
    createExteriorDetail(s, s.base_asset_sha256, new Set([s.building_id]));
  const a = create(before),
    b = create(after);
  assert.equal(a.children.length, b.children.length);
  assert.equal(before.objects.length, 490);
  assert.deepEqual(
    a.children.map((m) => m.geometry.attributes.position.count),
    [21828, 3600],
  );
  assert.deepEqual(
    b.children.map((m) => m.geometry.attributes.position.count),
    [22068, 3600],
  );
  assert.deepEqual(
    a.children.map((m) => m.userData),
    b.children.map((m) => m.userData),
  );
  assert.equal(
    createHash("sha256")
      .update(
        fs.readFileSync(
          new URL(
            "../../../assets/exterior-refinement/friendly-before-round-shafts-2026-11-10.json",
            import.meta.url,
          ),
        ),
      )
      .digest("hex"),
    "d8b439add6401343e891aa641fd4d12ae4aebe9a53bbc9cc99667f1bdcebdaba",
  );
  for (let i = 0; i < before.objects.length; i++) {
    const old = create({ ...before, objects: [before.objects[i]] }).children[0];
    const next = create({ ...after, objects: [after.objects[i]] }).children[0];
    if (!indices.includes(i)) {
      for (const k of ["position", "normal", "color"])
        assert.deepEqual(
          old.geometry.attributes[k].array,
          next.geometry.attributes[k].array,
        );
    } else {
      assert.equal(old.geometry.attributes.position.count, 36);
      assert.equal(next.geometry.attributes.position.count, 96);
      const positions = next.geometry.attributes.position,
        item = after.objects[i];
      for (let j = 0; j < positions.count; j++) {
        const radius = Math.hypot(
          positions.getX(j) - item.position[0],
          positions.getZ(j) - item.position[2],
        );
        assert.ok(
          radius <= 0.17503,
          "shaft vertex must stay in round cross section",
        );
      }
      old.geometry.computeBoundingBox();
      next.geometry.computeBoundingBox();
      assert.deepEqual(old.geometry.boundingBox, next.geometry.boundingBox);
    }
  }

  console.log(
    JSON.stringify({
      objects: 490,
      unchangedObjects: 486,
      changedIndices: indices,
      before: a.children.map((m) => ({
        kind: m.userData.asset_kind,
        vertices: m.geometry.attributes.position.count,
      })),
      after: b.children.map((m) => ({
        kind: m.userData.asset_kind,
        vertices: m.geometry.attributes.position.count,
      })),
      sameMeshCount: true,
    }),
  );
});
