import test from "node:test";
import assert from "node:assert/strict";
import { Mesh, Raycaster, Vector3 } from "three";
import { createEntrancePortalParts } from "../src/entrances.js";

test("the storefront portal stays inside its envelope and has working depth cues on both faces", () => {
  const parts = createEntrancePortalParts();
  const frame = new Mesh(parts["portal-trim"].geometry);
  const door = new Mesh(parts["portal-door"].geometry);
  for (const [mesh, triangles] of [
    [frame, 72],
    [door, 216],
  ]) {
    const { geometry } = mesh;
    assert.equal(geometry.index.count / 3, triangles);
    geometry.computeBoundingBox();
    const { min, max } = geometry.boundingBox;
    assert.ok(min.x >= -0.976 && max.x <= 0.976);
    assert.ok(min.y >= -1e-6 && max.y <= 2.881);
    assert.ok(min.z >= -0.121 && max.z <= 0.121);
    assert.equal(
      geometry.attributes.color.count,
      geometry.attributes.position.count,
    );
  }

  const depth = (mesh, x, y, side = 1) =>
    new Raycaster(
      new Vector3(x, y, side),
      new Vector3(0, 0, -side),
    ).intersectObject(mesh)[0]?.point.z;
  const close = (actual, expected) =>
    assert.ok(
      Math.abs(actual - expected) < 1e-6,
      [actual, expected].join(" vs. "),
    );
  for (const side of [-1, 1]) {
    close(depth(door, side * 0.412, 1.5), 0.008);
    close(depth(door, side * 0.79, 1.5), 0.024);
    close(depth(door, side * 0.035, 1.17), 0.1135);
    close(depth(door, side * 0.412, 1.05, -1), -0.0775);
  }
  assert.equal(depth(door, 0, 1.5), undefined);
  close(depth(frame, 0, 2.535), 0.013);
  close(depth(frame, 0, 0.017), 0.12);

  for (const mesh of [frame, door]) {
    mesh.geometry.dispose();
    mesh.material.dispose();
  }
});
