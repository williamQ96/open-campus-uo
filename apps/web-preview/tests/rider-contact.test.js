import { test } from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import { createCampusProp } from "../src/props.js";

test("rider feet stay on controls across supported height and width variants", () => {
  const color = new THREE.Color(0x39433e);
  for (const kind of ["bicycle", "scooter"]) {
    for (const [heightM, bodyWidth] of [
      [1.5, 0.85],
      [2.0, 1.15],
    ]) {
      const mesh = createCampusProp(kind, 0x567a72, {
        shirtColor: "#96506e",
        skinColor: "#b09070",
        heightM,
        bodyWidth,
      });
      const pos = mesh.geometry.attributes.position,
        rgb = mesh.geometry.attributes.color;
      const shoes = [];
      for (let i = 0; i < pos.count; i++)
        if (
          Math.abs(rgb.getX(i) - color.r) < 1e-6 &&
          Math.abs(rgb.getY(i) - color.g) < 1e-6 &&
          Math.abs(rgb.getZ(i) - color.b) < 1e-6
        )
          shoes.push([pos.getX(i), pos.getY(i), pos.getZ(i)]);
      assert.equal(shoes.length, 72, `${kind} shoes are present`);
      for (const side of [-1, 1]) {
        const shoe = shoes.filter((p) => Math.sign(p[0]) === side);
        assert.equal(shoe.length, 36);
        const y = shoe.reduce((sum, p) => sum + p[1], 0) / shoe.length;
        const z = shoe.reduce((sum, p) => sum + p[2], 0) / shoe.length;
        assert.ok(Math.abs(y - (kind === "bicycle" ? 0.46 : 0.29)) < 1e-5);
        assert.ok(
          Math.abs(z - (kind === "bicycle" ? 0 : side < 0 ? -0.25 : 0.14)) <
            1e-5,
        );
      }
      assert.ok([...pos.array].every(Number.isFinite));
      mesh.geometry.dispose();
      mesh.material.dispose();
    }
  }
});
