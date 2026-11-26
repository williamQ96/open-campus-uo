import { test } from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import { createCampusProp, cycleCollider } from "../src/props.js";

test("rider feet stay on controls across supported height and width variants", () => {
  const color = new THREE.Color(0x39433e);
  const contacts = {
    bicycle: [
      [-0.171, 0.223, -0.124],
      [0.171, 0.373, 0.03],
    ],
    scooter: [
      [-0.049, 0.173, -0.203],
      [0.049, 0.173, 0.074],
    ],
  };
  for (const [kind, feet] of Object.entries(contacts)) {
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
      for (const [x, y, z] of feet) {
        const shoe = shoes.filter((p) => Math.sign(p[0]) === Math.sign(x));
        assert.equal(shoe.length, 36);
        const centerX = shoe.reduce((sum, p) => sum + p[0], 0) / shoe.length;
        const centerZ = shoe.reduce((sum, p) => sum + p[2], 0) / shoe.length;
        const sole = Math.min(...shoe.map((p) => p[1]));
        assert.ok(Math.abs(centerX - x) < 1e-6);
        assert.ok(Math.abs(sole - y) < 1e-6);
        assert.ok(Math.abs(centerZ - z) < 1e-6);
      }
      const { radius, halfLength, height } = cycleCollider(kind, { heightM });
      for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i),
          y = pos.getY(i),
          z = pos.getZ(i);
        assert.ok(y >= -1e-6 && y <= height);
        assert.ok(
          Math.hypot(x, Math.max(0, Math.abs(z) - halfLength)) <= radius,
        );
      }
      mesh.geometry.dispose();
      mesh.material.dispose();
    }
  }
});
