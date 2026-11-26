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

const BICYCLE = {
  radius: 0.347,
  axles: [-0.5285, 0.5285],
  grip: [0.246, 0.971, 0.284],
  hips: [0.994, -0.209],
  shoulderRise: 0.378,
  shoulderZ: 0.028,
  headRise: 0.574,
  headZ: 0.085,
  pedals: [
    [-0.171, 0.21, -0.152],
    [0.171, 0.36, 0.002],
  ],
};
const SCOOTER = {
  radius: 0.127,
  axles: [-0.466, 0.462],
  grip: [0.237, 1.23, 0.277],
  hips: [1.021, -0.067],
  shoulderRise: 0.507,
  shoulderZ: 0.014,
  headRise: 0.741,
  headZ: 0.047,
  deckHeight: 0.173,
  feet: [
    [-0.049, -0.203],
    [0.049, 0.074],
  ],
};
const AXLE_ROTATION = [0, 0, Math.PI / 2];
const WHEEL_ROTATION = [0, Math.PI / 2, 0];
const METAL = 0x91a19c;
const GRIP = 0x253530;
const HELMET_RADIUS = 0.139;

export function cycleCollider(kind, rider) {
  const bike = kind === "bicycle";
  const cycle = bike ? BICYCLE : SCOOTER;
  const radius = bike ? 0.34 : 0.31;
  const heightScale = (rider?.heightM || 1.78) / 1.78;
  const top =
    cycle.hips[0] + cycle.headRise * heightScale + 0.043 + HELMET_RADIUS;
  return {
    radius,
    halfLength: (bike ? 0.9 : 0.64) - radius,
    height: top + 0.025,
  };
}

function drawBicycle({ add, box, beam, color }) {
  const {
    radius: r,
    axles: [rear, front],
    grip,
    pedals,
  } = BICYCLE;
  const bracket = [0, 0.285, -0.075];
  const seat = [0, 0.775, -0.216];
  const headTop = [0, 0.841, 0.267];
  const headBottom = [0, 0.713, 0.312];
  for (const z of BICYCLE.axles) {
    add(
      new THREE.TorusGeometry(r - 0.0175, 0.0175, 8, 24),
      0,
      r,
      z,
      TIRE,
      WHEEL_ROTATION,
    );
    add(
      new THREE.TorusGeometry(r - 0.035, 0.008, 4, 24),
      0,
      r,
      z,
      METAL,
      WHEEL_ROTATION,
    );
    add(
      new THREE.CylinderGeometry(0.026, 0.026, 0.105, 8),
      0,
      r,
      z,
      METAL,
      AXLE_ROTATION,
    );
    add(
      new THREE.CylinderGeometry(0.071, 0.071, 0.009, 12),
      -0.041,
      r,
      z,
      0x9ca9a6,
      AXLE_ROTATION,
    );
    for (let i = 0; i < 8; i++) {
      const a = (i * Math.PI) / 4;
      beam(
        [i % 2 ? -0.025 : 0.025, r, z],
        [0, r + (r - 0.035) * Math.cos(a), z + (r - 0.035) * Math.sin(a)],
        0.0046,
        METAL,
      );
    }
  }
  beam(seat, headTop, 0.022, color);
  beam(bracket, headBottom, 0.027, color);
  beam(bracket, seat, 0.022, color);
  beam(headBottom, headTop, 0.024, color);
  for (const x of [-0.055, 0.055]) {
    beam([x, r, rear], [x * 0.7, 0.285, bracket[2]], 0.013, color);
    beam([x, r, rear], seat, 0.012, color);
    beam([x, r, front], [x * 0.76, 0.678, 0.35], 0.017, color);
  }
  beam([-0.043, 0.678, 0.35], [0.043, 0.678, 0.35], 0.024, color);
  beam([0, 0.678, 0.35], [0, 0.901, 0.247], 0.018, color);
  beam([0, 0.901, 0.247], [0, grip[1], grip[2]], 0.018, DARK);
  beam(seat, [0, 0.911, -0.242], 0.014, METAL);
  box(0.128, 0.028, 0.158, 0, 0.925, -0.27, GRIP);
  box(0.071, 0.025, 0.135, 0, 0.923, -0.153, GRIP);

  const chainX = 0.065;
  for (const [y, z, ring] of [
    [bracket[1], bracket[2], 0.086],
    [r, rear, 0.041],
  ]) {
    add(
      new THREE.TorusGeometry(ring, 0.009, 4, 12),
      chainX,
      y,
      z,
      METAL,
      WHEEL_ROTATION,
    );
  }
  for (const sign of [-1, 1])
    beam(
      [chainX, bracket[1] + sign * 0.086, bracket[2]],
      [chainX, r + sign * 0.041, rear],
      0.008,
      DARK,
    );
  beam(
    [-0.08, bracket[1], bracket[2]],
    [0.08, bracket[1], bracket[2]],
    0.019,
    METAL,
  );
  for (const [x, y, z] of pedals) {
    beam(
      [Math.sign(x) * 0.08, bracket[1], bracket[2]],
      [x, y, z],
      0.014,
      METAL,
    );
    box(0.103, 0.026, 0.092, x, y, z, GRIP);
  }
  drawCycleBars(grip, { box, beam });
  box(0.061, 0.031, 0.033, 0, 0.908, -0.352, 0xb64d42);
}

function drawScooter({ add, box, beam, color }) {
  const {
    radius: r,
    axles: [rear, front],
    grip,
    deckHeight,
  } = SCOOTER;
  const stemBase = [0, 0.438, 0.357];
  box(0.205, 0.082, 0.57, 0, 0.12, -0.075, color);
  box(0.183, 0.016, 0.535, 0, deckHeight - 0.008, -0.075, GRIP);
  for (const z of [-0.299, -0.228, -0.151, -0.074, 0.003, 0.08, 0.157])
    box(0.151, 0.004, 0.014, 0, deckHeight - 0.002, z, 0x586563);
  for (const z of SCOOTER.axles) {
    const width = z === rear ? 0.067 : 0.058;
    add(
      new THREE.CylinderGeometry(r, r, width, 16),
      0,
      r,
      z,
      TIRE,
      AXLE_ROTATION,
    );
    add(
      new THREE.CylinderGeometry(0.067, 0.067, width + 0.008, 12),
      0,
      r,
      z,
      METAL,
      AXLE_ROTATION,
    );
    add(
      new THREE.CylinderGeometry(0.045, 0.045, width + 0.018, 10),
      0,
      r,
      z,
      DARK,
      AXLE_ROTATION,
    );
    for (let i = -2; i <= 2; i++) {
      const a = (i * Math.PI) / 7;
      add(
        new THREE.BoxGeometry(0.085, 0.018, 0.081),
        0,
        r + 0.157 * Math.cos(a),
        z + 0.157 * Math.sin(a),
        GRIP,
        [a, 0, 0],
      );
    }
  }
  for (const sign of [-1, 1]) {
    const x = sign * 0.05;
    beam([x, r, rear], [sign * 0.075, 0.13, -0.312], 0.022, color);
    beam([x, r, rear], [x * 0.75, 0.218, rear - 0.124], 0.012, METAL);
    beam(
      [x, 0.285, front - 0.044],
      [x * 0.75, 0.224, front - 0.12],
      0.012,
      METAL,
    );
    beam([x, r, front], [x, 0.371, 0.381], 0.019, METAL);
    beam([x, 0.371, 0.381], stemBase, 0.024, color);
    box(0.009, 0.026, 0.084, sign * 0.103, 0.123, -0.287, 0xc7874b);
  }
  beam([0, 0.156, 0.174], stemBase, 0.048, color);
  beam(stemBase, [0, grip[1], grip[2]], 0.026, color);
  beam(stemBase, [0, 0.509, 0.35], 0.037, DARK);
  drawCycleBars(grip, { box, beam });
  box(0.098, 0.047, 0.064, 0, 1.113, 0.338, DARK);
  box(0.08, 0.029, 0.007, 0, 1.111, 0.373, 0xf5edc7);
  box(0.069, 0.024, 0.025, 0, 0.218, -0.591, 0xb64d42);
  box(0.071, 0.016, 0.058, 0, 1.25, 0.278, 0x6c8986);
}

function drawCycleBars([x, y, z], { box, beam }) {
  beam([-x, y, z], [x, y, z], 0.014, DARK);
  for (const side of [-1, 1]) {
    beam([side * (x - 0.057), y, z], [side * (x + 0.054), y, z], 0.022, GRIP);
    beam(
      [side * (x - 0.073), y - 0.015, z + 0.004],
      [side * (x + 0.029), y - 0.042, z + 0.054],
      0.008,
      METAL,
    );
    box(0.028, 0.024, 0.029, side * (x - 0.064), y, z, DARK);
  }
}

function drawCycleRider(cycle, rider, { add, box, beam }) {
  const bike = cycle === BICYCLE;
  const shirt = rider?.shirtColor ?? 0x285d43;
  const skin = rider?.skinColor ?? 0xd3b89a;
  const trousers = rider?.trouserColor ?? 0x343f43;
  const height = (rider?.heightM || 1.78) / 1.78;
  const width = rider?.bodyWidth || 1;
  const [hipY, hipZ] = cycle.hips;
  const shoulderY = hipY + cycle.shoulderRise * height;
  const headY = hipY + cycle.headRise * height;
  const [gripX, gripY, gripZ] = cycle.grip;
  box(0.25 * width, 0.106, 0.166, 0, hipY, hipZ, trousers);
  const torso = new THREE.BoxGeometry(
    0.314 * width,
    shoulderY - hipY + 0.095,
    0.191,
  );
  torso.rotateX(Math.atan2(cycle.shoulderZ - hipZ, shoulderY - hipY));
  add(
    torso,
    0,
    (hipY + shoulderY) / 2 + 0.02,
    (hipZ + cycle.shoulderZ) / 2,
    shirt,
  );
  beam([0, shoulderY, cycle.shoulderZ], [0, headY, cycle.headZ], 0.054, skin);
  add(new THREE.SphereGeometry(0.108, 10, 7), 0, headY, cycle.headZ, skin);
  add(
    new THREE.SphereGeometry(
      HELMET_RADIUS,
      12,
      6,
      0,
      Math.PI * 2,
      0,
      Math.PI / 2,
    ),
    0,
    headY + 0.043,
    cycle.headZ,
    0xc6a449,
  );
  box(0.173, 0.018, 0.054, 0, headY + 0.045, cycle.headZ + 0.116, 0xa38234);

  for (const [i, side] of [-1, 1].entries()) {
    const x = side * 0.121 * width;
    const elbow = [
      side * 0.174 * width,
      (shoulderY + gripY) / 2 - 0.062,
      (cycle.shoulderZ + gripZ) / 2 - 0.062,
    ];
    const hand = [side * gripX, gripY + 0.016, gripZ];
    beam([x, shoulderY, cycle.shoulderZ], elbow, 0.055, shirt);
    beam(elbow, hand, 0.034, skin);
    add(new THREE.SphereGeometry(0.042, 8, 6), ...hand, skin);
    const [shoeX, shoeZ] = bike
      ? [cycle.pedals[i][0], cycle.pedals[i][2] + 0.028]
      : cycle.feet[i];
    const sole = bike ? cycle.pedals[i][1] + 0.013 : cycle.deckHeight;
    const knee = [
      side * (bike ? 0.124 : 0.082) * width,
      (hipY + sole) / 2,
      shoeZ + (bike ? 0.207 : 0.081),
    ];
    beam([side * 0.077 * width, hipY, hipZ], knee, 0.067, trousers);
    beam(knee, [shoeX, sole + 0.068, shoeZ - 0.045], 0.047, trousers);
    box(0.09, 0.08, 0.203, shoeX, sole + 0.04, shoeZ, 0x39433e);
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
    const bike = kind === "bicycle";
    const cycle = bike ? BICYCLE : SCOOTER;
    const drawing = { add, box, beam, color };
    if (bike) drawBicycle(drawing);
    else drawScooter(drawing);
    drawCycleRider(cycle, rider, drawing);
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
