// SPDX-License-Identifier: Apache-2.0
// Original, exportable low-poly props. No brands, logos or third-party geometry.
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
const ROAD_VEHICLES = {
  car: {
    length: 4.64,
    width: 1.78,
    mirrors: 2.01,
    height: 1.44,
    axles: [-1.43, 1.27],
    tire: 0.315,
    belt: 0.86,
    hood: 1.03,
    front: 1.44,
    back: -1.64,
    roofFront: 0.57,
    roofBack: -0.81,
  },
  suv: {
    length: 4.69,
    width: 1.87,
    mirrors: 2.1,
    height: 1.68,
    axles: [-1.41, 1.29],
    tire: 0.352,
    belt: 1.03,
    hood: 1.2,
    front: 1.32,
    back: -2.13,
    roofFront: 0.55,
    roofBack: -1.8,
  },
  van: {
    length: 4.73,
    width: 1.73,
    mirrors: 2.04,
    height: 1.87,
    axles: [-1.48, 1.45],
    tire: 0.315,
    belt: 1.02,
    hood: 1.16,
    front: 1.67,
    back: -2.24,
    roofFront: 0.91,
    roofBack: -2.06,
  },
  pickup: {
    length: 5.08,
    width: 1.84,
    mirrors: 2.12,
    height: 1.75,
    axles: [-1.57, 1.51],
    tire: 0.36,
    belt: 1.04,
    hood: 1.23,
    front: 1.54,
    back: -0.83,
    roofFront: 0.71,
    roofBack: -0.51,
  },
};
const TIRE = 0x273334;
const DARK = 0x394543;
const GLASS = 0x69958e;

export function roadVehicleCollider(kind) {
  const { width, length, height } = ROAD_VEHICLES[kind];
  const radius = width / 2;
  return { radius, halfLength: length / 2 - radius, height };
}

function roadVehicle(kind, color, add, box) {
  const {
    length,
    width,
    mirrors,
    height,
    axles,
    tire,
    belt,
    hood,
    front,
    back,
    roofFront,
    roofBack,
  } = ROAD_VEHICLES[kind];
  const end = length / 2,
    edge = width / 2;
  const pickup = kind === "pickup",
    van = kind === "van";
  const sill = tire + 0.014;
  const shoulder = end - 0.085;
  const shell = new THREE.Shape();
  shell.moveTo(-shoulder, sill);
  for (const axle of axles) {
    for (let i = 0; i <= 8; i++) {
      const angle = Math.PI * (1 - i / 8);
      shell.lineTo(
        axle + (tire + 0.073) * Math.cos(angle),
        sill + (tire + 0.073) * Math.sin(angle),
      );
    }
  }
  shell.lineTo(shoulder, sill);
  shell.lineTo(shoulder, hood - 0.14);
  shell.lineTo(front, hood);
  shell.lineTo(back, belt);
  shell.lineTo(-shoulder, belt - 0.04);
  shell.closePath();
  const body = new THREE.ExtrudeGeometry(shell, {
    depth: width - 0.08,
    bevelEnabled: true,
    bevelSize: 0.035,
    bevelThickness: 0.04,
    bevelSegments: 1,
    steps: 1,
  });
  body.translate(0, 0, -(width - 0.08) / 2).rotateY(-Math.PI / 2);
  add(body, 0, 0, 0, color);

  // Trapezoidal cabin panels and inset glass share the same sloped faces.
  const baseWidth = edge - 0.07;
  const roofWidth = edge - (van ? 0.14 : 0.22);
  const baseY = belt - 0.035;
  const point = (side, high, atFront) =>
    new THREE.Vector3(
      side * (high ? roofWidth : baseWidth),
      high ? height : baseY,
      high ? (atFront ? roofFront : roofBack) : atFront ? front : back,
    );
  function panel(points, outward, paint, offset = 0) {
    const n = new THREE.Vector3(...outward);
    const a = points[1].clone().sub(points[0]);
    const b = points[2].clone().sub(points[0]);
    if (a.cross(b).dot(n) < 0) points = [...points].reverse();
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(
        [0, 1, 2, 0, 2, 3].flatMap((i) =>
          points[i].clone().addScaledVector(n, offset).toArray(),
        ),
        3,
      ),
    );
    geometry.computeVertexNormals();
    add(geometry, 0, 0, 0, paint);
  }

  function cabinFace(corners, outward, panes) {
    panel(corners, outward, color);
    const [a, b, c, d] = corners;
    const at = (x, y) => a.clone().lerp(b, x).lerp(d.clone().lerp(c, x), y);
    for (const [left, right] of panes)
      panel(
        [at(left, 0.23), at(right, 0.23), at(right, 0.89), at(left, 0.89)],
        outward,
        GLASS,
        0.012,
      );
  }

  panel(
    [
      point(-1, true, false),
      point(1, true, false),
      point(1, true, true),
      point(-1, true, true),
    ],
    [0, 1, 0],
    color,
  );
  for (const side of [-1, 1]) {
    cabinFace(
      [
        point(side, false, false),
        point(side, false, true),
        point(side, true, true),
        point(side, true, false),
      ],
      [side, 0, 0],
      van
        ? [[0.7, 0.94]]
        : [
            [0.1, 0.48],
            [0.52, 0.94],
          ],
    );
    const halo = van ? 0.07 : 0.125;
    const mirrorY = Math.max(baseY + 0.18, hood + 0.09);
    const mirrorZ = front - 0.24;
    const stalkInner = baseWidth - 0.22;
    const stalkOuter = mirrors / 2 - halo / 2;
    box(
      stalkOuter - stalkInner,
      0.034,
      0.055,
      (side * (stalkOuter + stalkInner)) / 2,
      mirrorY - 0.028,
      mirrorZ,
      DARK,
    );
    box(halo, 0.1, 0.19, (side * (mirrors - halo)) / 2, mirrorY, mirrorZ, DARK);
    for (const axle of axles) {
      const x = side * (edge - 0.11);
      const rotation = [0, 0, Math.PI / 2];
      add(
        new THREE.CylinderGeometry(tire, tire, 0.18, 12),
        x,
        tire,
        axle,
        TIRE,
        rotation,
      );
      add(
        new THREE.CylinderGeometry(tire * 0.56, tire * 0.56, 0.035, 12),
        x + side * 0.095,
        tire,
        axle,
        0x9aa8a2,
        rotation,
      );
      add(
        new THREE.CylinderGeometry(tire * 0.22, tire * 0.22, 0.045, 8),
        x + side * 0.099,
        tire,
        axle,
        DARK,
        rotation,
      );
    }
    const doors = van
      ? [back + 0.13, front - 0.2]
      : [(back + front) / 2, front - 0.3];
    for (const z of doors) {
      box(0.018, 0.2, 0.019, side * (edge - 0.007), belt - 0.13, z, DARK);
      box(
        0.031,
        0.035,
        0.19,
        side * (edge - 0.004),
        belt - 0.063,
        z - 0.14,
        0xb1b9a9,
      );
    }
    if (van)
      box(
        0.023,
        0.035,
        1.62,
        side * (edge + 0.006),
        belt - 0.105,
        back + 1.25,
        DARK,
      );
  }
  for (const atFront of [false, true]) {
    const direction = atFront ? 1 : -1;
    cabinFace(
      [
        point(-1, false, atFront),
        point(1, false, atFront),
        point(1, true, atFront),
        point(-1, true, atFront),
      ],
      [0, 0, direction],
      van && !atFront
        ? [
            [0.085, 0.48],
            [0.52, 0.915],
          ]
        : [[0.08, 0.92]],
    );
    const bumperZ = direction * (end - 0.038);
    box(width - 0.17, 0.1, 0.076, 0, sill + 0.14, bumperZ, DARK);
    for (const side of [-1, 1])
      box(
        0.31,
        atFront ? 0.105 : 0.15,
        0.07,
        side * (edge - 0.23),
        atFront ? hood - 0.255 : belt - 0.195,
        direction * (end - 0.054),
        atFront ? 0xf5edc7 : 0xa95143,
      );
  }
  box(width * 0.37, 0.135, 0.073, 0, hood - 0.24, end - 0.053, DARK);
  box(0.31, 0.075, 0.033, 0, belt - 0.28, -end + 0.034, 0xb9b9a8);

  if (pickup) {
    const bedLength = end + back - 0.09;
    const middle = back - bedLength / 2;
    box(width - 0.29, 0.055, bedLength, 0, belt + 0.025, middle, DARK);
    for (const side of [-1, 1])
      box(
        0.15,
        0.245,
        bedLength,
        side * (edge - 0.092),
        belt + 0.125,
        middle,
        color,
      );
    box(width - 0.04, 0.245, 0.105, 0, belt + 0.125, -shoulder + 0.033, color);
  }
}

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
  if (Object.hasOwn(ROAD_VEHICLES, kind)) {
    roadVehicle(kind, color, add, box);
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
