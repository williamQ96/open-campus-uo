// SPDX-License-Identifier: Apache-2.0
// Original, exportable low-poly props. No brands, logos or third-party geometry.
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
export function createCampusProp(kind = "car", color = 0x567a72, rider = null) {
  const parts = [];
  function add(geometry, x, y, z, c, rotation = [0, 0, 0]) {
    geometry.rotateX(rotation[0]);
    geometry.rotateY(rotation[1]);
    geometry.rotateZ(rotation[2]);
    geometry.translate(x, y, z);
    if (geometry.index) geometry = geometry.toNonIndexed();
    const rgb = new THREE.Color(c),
      colors = [];
    for (let i = 0; i < geometry.attributes.position.count; i++)
      colors.push(rgb.r, rgb.g, rgb.b);
    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    geometry.deleteAttribute("uv");
    parts.push(geometry);
  }
  const box = (w, h, d, x, y, z, c) =>
    add(new THREE.BoxGeometry(w, h, d), x, y, z, c);
  const wheel = (x, y, z, r = 0.32) =>
    add(new THREE.CylinderGeometry(r, r, 0.16, 10), x, y, z, 0x273334, [
      0,
      0,
      Math.PI / 2,
    ]);
  const beam = (a, b, r, c) => {
    const va = new THREE.Vector3(...a),
      vb = new THREE.Vector3(...b),
      g = new THREE.CylinderGeometry(r, r, va.distanceTo(vb), 6);
    g.applyQuaternion(
      new THREE.Quaternion().setFromUnitVectors(
        new THREE.Vector3(0, 1, 0),
        vb.sub(va).normalize(),
      ),
    );
    add(
      g,
      ...va
        .add(new THREE.Vector3(...b))
        .multiplyScalar(0.5)
        .toArray(),
      c,
    );
  };
  if (["car", "suv", "van", "pickup"].includes(kind)) {
    const van = kind === "van",
      suv = kind === "suv",
      pickup = kind === "pickup";
    box(1.8, 0.65, van ? 4.7 : 4.2, 0, 0.7, 0, color);
    box(
      1.6,
      van ? 1.35 : suv ? 1.05 : 0.7,
      van ? 3.3 : pickup ? 1.55 : 2.1,
      0,
      van ? 1.5 : suv ? 1.5 : 1.35,
      van ? -0.35 : pickup ? 0.45 : -0.1,
      color,
    );
    // Front glass sits just outside each cabin; the pickup cabin ends further forward.
    const windshieldY = van || suv ? 1.65 : 1.43,
      windshieldZ = van ? 1.32 : pickup ? 1.25 : 1.0;
    box(1.62, 0.5, 0.045, 0, windshieldY, windshieldZ, 0x69958e);
    // A low windscreen rail and wiper pair make the front legible at walking scale.
    for (const x of [-0.4, 0.4])
      box(
        0.56,
        0.035,
        0.025,
        x,
        windshieldY - 0.2,
        windshieldZ + 0.035,
        0x34433d,
      );
    box(
      1.62,
      0.5,
      0.045,
      0,
      van ? 1.65 : 1.43,
      van ? -2 : pickup ? -0.36 : -1.2,
      0x69958e,
    );
    for (const x of [-0.815, 0.815])
      box(
        0.045,
        0.48,
        van ? 2.6 : pickup ? 1.25 : 1.8,
        x,
        van ? 1.65 : 1.43,
        pickup ? 0.45 : -0.13,
        0x69958e,
      );
    for (const x of [-0.91, 0.91])
      for (const z of [-1.3, 1.3]) {
        wheel(x, 0.39, z, 0.36);
        add(
          new THREE.CylinderGeometry(0.19, 0.19, 0.018, 10),
          x + Math.sign(x) * 0.09,
          0.39,
          z,
          0x9aa8a2,
          [0, 0, Math.PI / 2],
        );
      }
    for (const x of [-0.62, 0.62]) {
      box(0.35, 0.17, 0.055, x, 0.78, van ? 2.37 : 2.13, 0xf5edc7);
      box(0.35, 0.17, 0.055, x, 0.78, van ? -2.37 : -2.13, 0xa95143);
    }
    // Generic bumpers, mirrors and side-window pillars improve the vehicle silhouette.
    for (const z of [van ? -2.39 : -2.15, van ? 2.39 : 2.15])
      box(1.65, 0.13, 0.09, 0, 0.48, z, 0x465450);
    for (const side of [-1, 1]) {
      box(0.22, 0.18, 0.18, side * 0.98, van ? 1.42 : 1.28, 0.83, 0x34433d);
      box(
        0.055,
        0.48,
        0.08,
        side * 0.845,
        van ? 1.65 : 1.43,
        pickup ? 0.45 : -0.13,
        0x465450,
      );
    }
    // Body features are bounded within the existing vehicle envelopes. They are
    // generic original geometry rather than models of particular UO vehicles.
    const frontZ = van ? 2.37 : 2.13;
    box(0.82, 0.19, 0.055, 0, 0.71, frontZ, 0x34433d);
    for (const x of [-0.25, 0, 0.25])
      box(0.025, 0.15, 0.018, x, 0.71, frontZ + 0.035, 0x9aa8a2);
    for (const side of [-1, 1]) {
      const x = side * 0.915;
      box(0.035, 0.42, 0.035, x, 0.77, 0.82, 0x465450);
      box(0.035, 0.42, 0.035, x, 0.77, pickup ? -0.43 : -0.9, 0x465450);
      box(0.04, 0.045, 0.24, x, 0.95, 0.45, 0xc2c5b4);
      if (!pickup) box(0.04, 0.045, 0.24, x, 0.95, -0.5, 0xc2c5b4);
      box(0.035, 0.055, van ? 3.7 : 3.25, x, 0.49, 0, 0x465450);
    }
    if (van)
      for (const side of [-1, 1])
        box(0.035, 0.045, 1.9, side * 0.92, 0.83, -0.85, 0x9aa8a2);
    if (kind === "pickup") {
      box(1.44, 0.07, 1.65, 0, 1.055, -1.22, 0x394543);
      for (const x of [-0.79, 0.79]) box(0.16, 0.3, 1.7, x, 1.18, -1.22, color);
      box(1.72, 0.3, 0.14, 0, 1.18, -2.02, color);
    }
  } else {
    const bike = kind === "bicycle",
      r = bike ? 0.32 : 0.16,
      front = bike ? 0.65 : 0.58,
      back = -front;
    if (bike) {
      // Low-poly tire, rim and crossed spokes keep the wheel open in silhouette.
      for (const z of [front, back]) {
        add(
          new THREE.TorusGeometry(r - 0.025, 0.025, 5, 12),
          0,
          r,
          z,
          0x273334,
          [0, Math.PI / 2, 0],
        );
        add(
          new THREE.TorusGeometry(r - 0.055, 0.012, 4, 12),
          0,
          r,
          z,
          0xaab3a6,
          [0, Math.PI / 2, 0],
        );
        for (let i = 0; i < 6; i++) {
          const a = (i * Math.PI) / 3;
          beam(
            [0, r, z],
            [0, r + (r - 0.055) * Math.cos(a), z + (r - 0.055) * Math.sin(a)],
            0.008,
            0xaab3a6,
          );
        }
      }
    } else {
      wheel(0, r, front, r);
      wheel(0, r, back, r);
    }
    if (bike) {
      beam([0, r, back], [0, 0.9, -0.2], 0.045, color);
      beam([0, 0.9, -0.2], [0, r, front], 0.045, color);
      beam([0, r, back], [0, 0.45, 0], 0.045, color);
      beam([0, 0.45, 0], [0, r, front], 0.045, color);
      beam([0, 0.45, 0], [0, 0.9, -0.2], 0.04, color);
      beam([0, 0.45, 0], [0, r, back], 0.035, color);
      beam([0, 0.9, -0.2], [0, 0.98, -0.2], 0.025, 0x4c5e57);
      box(0.32, 0.1, 0.36, 0, 1.01, -0.2, 0x34433d);
      // A simplified right-side drivetrain and wheel hubs make this generic
      // bike legible without changing its route, rider or visual envelope.
      for (const z of [front, back])
        add(
          new THREE.CylinderGeometry(0.045, 0.045, 0.12, 8),
          0,
          r,
          z,
          0x9aa99e,
          [0, 0, Math.PI / 2],
        );
      add(
        new THREE.TorusGeometry(0.12, 0.012, 4, 12),
        0.095,
        0.45,
        0,
        0x9aa99e,
        [0, Math.PI / 2, 0],
      );
      add(
        new THREE.TorusGeometry(0.052, 0.009, 4, 10),
        0.095,
        r,
        back,
        0x9aa99e,
        [0, Math.PI / 2, 0],
      );
      beam([0.095, 0.56, 0], [0.095, 0.37, back], 0.009, 0x9aa99e);
      beam([0.095, 0.34, 0], [0.095, 0.27, back], 0.009, 0x9aa99e);
      // A small crank and pedals give the rider a readable connection to the bike.
      beam([-0.14, 0.45, 0], [0.14, 0.45, 0], 0.025, 0x9aa99e);
      for (const x of [-0.19, 0.19])
        box(0.12, 0.04, 0.12, x, 0.45, 0, 0x34433d);
    } else {
      box(0.3, 0.1, 1.15, 0, 0.18, 0, color);
      box(0.25, 0.025, 0.7, 0, 0.24, -0.08, 0x34433d);
      for (const z of [front, back]) {
        box(0.21, 0.04, 0.24, 0, 0.34, z, 0x34433d);
        // Visible hub caps on both sides of the small solid wheel.
        for (const side of [-1, 1])
          add(
            new THREE.CylinderGeometry(0.07, 0.07, 0.018, 10),
            side * 0.09,
            r,
            z,
            0xaab3a6,
            [0, 0, Math.PI / 2],
          );
      }
      // Generic wheel supports, deck edge rails and grip marks, kept within
      // the existing scooter envelope; no branded or model-specific features.
      for (const side of [-1, 1]) {
        beam(
          [side * 0.12, 0.18, back],
          [side * 0.12, 0.32, back + 0.22],
          0.025,
          0x9aa8a2,
        );
        beam(
          [side * 0.12, 0.16, front],
          [side * 0.12, 0.49, front - 0.025],
          0.025,
          0x9aa8a2,
        );
        beam(
          [side * 0.12, 0.46, front - 0.025],
          [0, 0.46, front - 0.025],
          0.022,
          0x9aa8a2,
        );
        box(0.025, 0.035, 0.83, side * 0.14, 0.245, -0.04, 0x9aa8a2);
      }
      for (const z of [-0.34, -0.18, -0.02, 0.14, 0.3])
        box(0.2, 0.008, 0.025, 0, 0.258, z, 0x71817b);
      box(0.13, 0.06, 0.04, 0, 0.35, back - 0.13, 0xa95143);
      add(
        new THREE.SphereGeometry(0.055, 8, 6),
        0,
        0.95,
        front + 0.02,
        0xf5edc7,
      );
    }
    beam([0, r, front], [0, 1.1, front - 0.1], 0.045, color);
    beam([-0.3, 1.1, front - 0.1], [0.3, 1.1, front - 0.1], 0.035, 0x283a34);
    if (bike)
      for (const side of [-1, 1]) {
        beam(
          [side * 0.21, 1.1, front - 0.1],
          [side * 0.29, 1.1, front - 0.1],
          0.045,
          0x1f2c2b,
        );
        beam(
          [side * 0.17, 1.08, front - 0.09],
          [side * 0.23, 1.02, front - 0.04],
          0.012,
          0xaab3a6,
        );
      }
    if (!bike) {
      for (const side of [-1, 1]) {
        beam(
          [side * 0.2, 1.1, front - 0.1],
          [side * 0.3, 1.1, front - 0.1],
          0.05,
          0x1f2c2b,
        );
        beam(
          [side * 0.18, 1.08, front - 0.09],
          [side * 0.25, 1.02, front - 0.04],
          0.012,
          0xaab3a6,
        );
      }
      box(0.13, 0.075, 0.13, 0, 0.76, front - 0.065, 0x465450);
    }
    const shirt = rider ? new THREE.Color(rider.shirtColor).getHex() : 0x285d43,
      skin = rider ? new THREE.Color(rider.skinColor).getHex() : 0xd3b89a,
      height = rider ? rider.heightM / 1.78 : 1,
      width = rider ? rider.bodyWidth : 1;
    // Scale the upper body around the seat/deck while keeping hands and feet
    // connected to fixed vehicle controls for every supported rider height.
    box(
      0.4 * width,
      0.54 * height,
      0.25,
      0,
      1 + 0.35 * height,
      bike ? -0.16 : 0,
      shirt,
    );
    add(
      new THREE.SphereGeometry(0.16, 8, 6),
      0,
      1 + 0.81 * height,
      bike ? -0.08 : 0,
      skin,
    );
    add(
      new THREE.SphereGeometry(0.18, 8, 6, 0, Math.PI * 2, 0, Math.PI / 2),
      0,
      1 + 0.85 * height,
      bike ? -0.08 : 0,
      0xd3b64b,
    );
    for (const side of [-1, 1]) {
      const x = side * 0.14 * width,
        shoeX = side * (bike ? 0.19 : 0.1),
        shoeZ = bike ? 0 : side < 0 ? -0.25 : 0.14,
        shoeY = bike ? 0.46 : 0.29;
      beam(
        [x, 1 + 0.45 * height, bike ? -0.08 : 0],
        [side * 0.25, 1.1, front - 0.1],
        0.065,
        shirt,
      );
      beam(
        [x, 1 + 0.08 * height, bike ? -0.1 : 0],
        [x, 0.75, bike ? 0.27 : shoeZ],
        0.075,
        0x333e42,
      );
      beam(
        [x, 0.75, bike ? 0.27 : shoeZ],
        [shoeX, shoeY, shoeZ],
        0.065,
        0x333e42,
      );
      box(0.16, 0.1, 0.23, shoeX, shoeY, shoeZ, 0x39433e);
    }
  }
  const geometry = mergeGeometries(parts, false);
  parts.forEach((g) => g.dispose());
  const mesh = new THREE.Mesh(
    geometry,
    new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.85 }),
  );
  mesh.name = `Original campus ${kind}`;
  mesh.receiveShadow = true;
  mesh.userData = {
    asset_kind: "campus-prop",
    license: "CC-BY-4.0",
    author: "Open Campus contributors",
    kind,
  };
  return mesh;
}
