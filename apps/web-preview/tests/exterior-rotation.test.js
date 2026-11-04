import test from "node:test";
import assert from "node:assert/strict";
import { createExteriorDetail } from "../src/exterior-detail.js";
const spec = {
  version: 1,
  base_asset_sha256: "source",
  building_id: "b",
  objects: [
    {
      kind: "prop",
      material: "glass",
      shape: "box",
      position: [0, 0, 0],
      size: [2, 0.1, 2],
      rotation: [0, 0, 0.2],
    },
  ],
};
test("exterior geometry rotates and rejects malformed rotations", () => {
  const rotated = createExteriorDetail(spec, "source", new Set(["b"]));
  const unrotated = createExteriorDetail(
    { ...spec, objects: [{ ...spec.objects[0], rotation: [0, 0, 0] }] },
    "source",
    new Set(["b"]),
  );
  rotated.children[0].geometry.computeBoundingBox();
  unrotated.children[0].geometry.computeBoundingBox();
  const a = rotated.children[0].geometry.boundingBox,
    b = unrotated.children[0].geometry.boundingBox;
  assert.ok(a.max.y - a.min.y > b.max.y - b.min.y + 0.25);
  for (const rotation of [[0, 0, 4], [0, 1], [0, 0, NaN], "bad"])
    assert.throws(
      () =>
        createExteriorDetail(
          { ...spec, objects: [{ ...spec.objects[0], rotation }] },
          "source",
          new Set(["b"]),
        ),
      /Invalid/,
    );
  assert.throws(
    () =>
      createExteriorDetail(
        {
          ...spec,
          objects: [
            { ...spec.objects[0], kind: "building", shape: "label", text: "A" },
          ],
        },
        "source",
        new Set(["b"]),
      ),
    /Invalid/,
  );
});
