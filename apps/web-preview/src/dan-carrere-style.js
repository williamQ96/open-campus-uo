// SPDX-License-Identifier: Apache-2.0
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";

const { lerp, clamp } = THREE.MathUtils;

export const danCarrereAppearance = Object.freeze({
  heightM: 1.88,
  bodyWidth: 1.02,
  skinColor: "#cda98e",
  hair: "none",
  bag: "none",
  shirtColor: "#64574e",
  trouserColor: "#394342",
  gait: "walk",
});

function colored(geometry, tint) {
  geometry.deleteAttribute("uv");
  const vertices = geometry.getAttribute("position");
  const colors = new Float32Array(vertices.count * 3);
  for (let i = 0; i < vertices.count; i++) tint(i).toArray(colors, i * 3);
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  return geometry;
}

function surface(rows, columns, vertex, tint) {
  const points = [];
  const triangles = [];
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < columns; col++) {
      points.push(...vertex(row, col));
      if (row === 0 || col === 0) continue;
      const c = row * columns + col;
      triangles.push(
        c - columns - 1,
        c - columns,
        c,
        c - columns - 1,
        c,
        c - 1,
      );
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(points, 3),
  );
  geometry.setIndex(triangles);
  geometry.computeVertexNormals();
  return colored(geometry, tint);
}

function ellipsoid(center, scale, hex, rotZ = 0) {
  const [width, height] = Math.max(...scale) < 0.025 ? [8, 5] : [12, 8];
  const geometry = new THREE.SphereGeometry(1, width, height);
  geometry
    .scale(...scale)
    .rotateZ(rotZ)
    .translate(...center);
  const color = new THREE.Color(hex);
  return colored(geometry, () => color);
}

function roundedProfile(rows, palette, shape = (y) => y) {
  const colors = palette.map((hex) => new THREE.Color(hex));
  const steps = 32;
  return surface(
    rows.length,
    steps + 1,
    (row, col) => {
      const [y, width, depth, z] = rows[row];
      const angle = (col / steps) * Math.PI * 2;
      return [
        width * Math.sin(angle),
        shape(y, angle),
        z + depth * Math.cos(angle),
      ];
    },
    (i) => colors[Math.floor(i / (steps + 1)) % colors.length],
  );
}

const face = [
  [-0.14, 0.065, 0.059, -0.014],
  [-0.072, 0.073, 0.069, -0.008],
  [-0.018, 0.086, 0.089, 0.011],
  [0.025, 0.124, 0.109, 0.027],
  [0.08, 0.144, 0.136, 0.032],
  [0.157, 0.161, 0.148, 0.026],
  [0.223, 0.177, 0.165, 0.021],
  [0.302, 0.172, 0.163, 0.018],
  [0.366, 0.176, 0.168, 0.008],
  [0.435, 0.178, 0.167, -0.003],
  [0.485, 0.153, 0.144, -0.022],
  [0.529, 0.077, 0.086, -0.033],
  [0.536, 0.002, 0.002, -0.033],
];

function facePoint(y, angle, thickness) {
  const top = face.findIndex(([height]) => height > y);
  const lo = face[top - 1];
  const hi = face[top];
  const u = (y - lo[0]) / (hi[0] - lo[0]);
  return [
    (lerp(lo[1], hi[1], u) + thickness) * Math.sin(angle),
    y,
    lerp(lo[3], hi[3], u) +
      (lerp(lo[2], hi[2], u) + thickness) * Math.cos(angle),
  ];
}

function beardSurface() {
  const tones = ["#746a61", "#8d8279", "#a99d8c", "#6d645d"].map(
    (color) => new THREE.Color(color),
  );
  const tint = new THREE.Color();
  const sections = 7;
  const columns = 39;
  return surface(
    sections,
    columns,
    (row, col) => {
      const t = row / (sections - 1);
      const angle = ((col / (columns - 1)) * 2 - 1) * 2.04;
      const side = Math.abs(Math.sin(angle));
      const taper = THREE.MathUtils.smoothstep(Math.abs(angle), 1.42, 2.04);
      const base = lerp(-0.019 + 0.109 * side ** 1.55, 0.187, taper);
      const upper = lerp(0.154 + 0.112 * side, 0.192, taper);
      const extra =
        (0.004 + 0.026 * Math.sin(t * Math.PI)) *
        (1 - Math.abs(angle / 2.04) ** 8);
      return facePoint(lerp(base, upper, t), angle, extra);
    },
    (i) => {
      const row = Math.floor(i / columns);
      const col = i % columns;
      return tint
        .copy(tones[(3 * col + Math.floor((row + col) / 4)) % tones.length])
        .lerp(tones[0], clamp(row / sections, 0, 0.65));
    },
  );
}

function scalpHair() {
  const shades = ["#70675f", "#635952", "#6a6159"].map(
    (hex) => new THREE.Color(hex),
  );
  return surface(
    5,
    33,
    (row, col) => {
      const angle = lerp(1.28, Math.PI * 2 - 1.28, col / 32);
      const lower = 0.345 - 0.085 * Math.max(0, -Math.cos(angle));
      const t = row / 4;
      return facePoint(lerp(lower, 0.461, t), angle, 0.007 + 0.01 * t);
    },
    (i) => shades[Math.floor(i / 11) % shades.length],
  );
}

function cap() {
  const wave = (y, angle) =>
    y - 0.024 * Math.cos(angle) + 0.012 * Math.sin(angle);
  const brim = roundedProfile(
    [
      [0.435, 0.18, 0.16, -0.015],
      [0.424, 0.222, 0.206, -0.009],
      [0.417, 0.273, 0.256, -0.006],
      [0.423, 0.279, 0.259, -0.006],
      [0.434, 0.275, 0.256, -0.006],
      [0.451, 0.216, 0.204, -0.012],
      [0.449, 0.179, 0.162, -0.015],
    ],
    ["#343230", "#4e4a43", "#46423d", "#625c51"],
    wave,
  );
  const crown = roundedProfile(
    [
      [0.438, 0.185, 0.196, -0.018],
      [0.466, 0.191, 0.196, -0.019],
      [0.507, 0.187, 0.181, -0.024],
      [0.555, 0.17, 0.155, -0.032],
      [0.602, 0.14, 0.123, -0.039],
      [0.624, 0.102, 0.098, -0.041],
      [0.613, 0.058, 0.063, -0.041],
      [0.594, 0.002, 0.002, -0.038],
    ],
    ["#57524a", "#625d54", "#675f55"],
    (y, angle) => lerp(y, wave(y, angle), 1 - clamp((y - 0.44) / 0.15, 0, 1)),
  );
  const band = roundedProfile(
    [
      [0.447, 0.186, 0.2, -0.017],
      [0.451, 0.196, 0.203, -0.019],
      [0.478, 0.193, 0.198, -0.02],
      [0.484, 0.19, 0.194, -0.022],
    ],
    ["#55514b", "#3a3836", "#403c38", "#716659"],
    wave,
  );
  return [brim, crown, band];
}

function faceParts() {
  const parts = [
    roundedProfile(face, [
      "#bc937b",
      "#c29a81",
      "#bd947b",
      "#c7a18a",
      "#c29a83",
      "#cca68f",
      "#d1aa92",
      "#caa28b",
      "#c79f86",
      "#c29b81",
    ]),
    beardSurface(),
    scalpHair(),
    roundedProfile(
      [
        [0.229, 0.011, 0.014, 0.198],
        [0.237, 0.028, 0.023, 0.207],
        [0.258, 0.037, 0.032, 0.209],
        [0.286, 0.028, 0.032, 0.207],
        [0.321, 0.023, 0.031, 0.196],
        [0.357, 0.01, 0.013, 0.164],
      ],
      ["#af816e", "#bc8f79", "#d3a48b", "#d5ae98", "#cca18a"],
    ),
    ellipsoid([0, 0.135, 0.193], [0.039, 0.008, 0.009], "#5a4238"),
    ...cap(),
  ];
  for (const s of [-1, 1]) {
    parts.push(
      ellipsoid(
        [s * 0.174, 0.273, 0.019],
        [0.03, 0.061, 0.033],
        "#b78875",
        s * -0.14,
      ),
      ellipsoid(
        [s * 0.182, 0.276, 0.041],
        [0.015, 0.035, 0.009],
        "#96665b",
        s * -0.15,
      ),
      ellipsoid(
        [s * 0.069, 0.305, 0.165],
        [0.036, 0.017, 0.013],
        "#b98d78",
        s * 0.1,
      ),
      ellipsoid([s * 0.069, 0.31, 0.176], [0.022, 0.008, 0.009], "#d5c8b6"),
      ellipsoid([s * 0.065, 0.31, 0.182], [0.008, 0.008, 0.005], "#4c463b"),
      ellipsoid([s * 0.063, 0.311, 0.186], [0.004, 0.005, 0.002], "#292824"),
      ellipsoid(
        [s * 0.068, 0.334, 0.17],
        [0.031, 0.008, 0.012],
        "#695e54",
        s * -0.14,
      ),
      ellipsoid([s * 0.021, 0.245, 0.228], [0.009, 0.004, 0.006], "#78554b"),
      ellipsoid(
        [s * 0.029, 0.16, 0.184],
        [0.04, 0.017, 0.024],
        "#746760",
        s * -0.23,
      ),
    );
  }
  return parts;
}

function retainStockNeckAndHands(skin) {
  const original = skin.geometry;
  const { skinIndex, skinWeight } = original.attributes;
  const head = skin.skeleton.bones.findIndex(({ name }) => name === "Head");
  const usesHead = (id) => {
    for (let j = 0; j < 4; j++)
      if (
        skinIndex.getComponent(id, j) === head &&
        skinWeight.getComponent(id, j) > 0.5
      )
        return true;
    return false;
  };
  const indices = original.index.array;
  const retained = [];
  for (let i = 0; i < indices.length; i += 3) {
    const a = indices[i],
      b = indices[i + 1],
      c = indices[i + 2];
    if (!(usesHead(a) && usesHead(b) && usesHead(c))) retained.push(a, b, c);
  }
  const trimmed = original.clone();
  trimmed.setIndex(retained);
  skin.geometry = trimmed;
  return trimmed;
}

function wovenCloth() {
  const swatch = document.createElement("canvas");
  swatch.width = swatch.height = 128;
  const ctx = swatch.getContext("2d");
  ctx.fillStyle = "#494441";
  ctx.fillRect(0, 0, 128, 128);
  for (const [width, position, color] of [
    [48, 0, "rgba(145, 125, 109, 0.27)"],
    [10, 14, "rgba(184, 167, 148, 0.25)"],
    [2, 19, "rgba(222, 198, 169, 0.32)"],
    [4, 79, "rgba(28, 29, 30, 0.28)"],
  ]) {
    ctx.fillStyle = color;
    ctx.fillRect(position, 0, width, 128);
    ctx.fillRect(0, position, 128, width);
  }
  ctx.fillStyle = "rgba(31, 30, 29, 0.19)";
  for (let i = 0; i < 128; i += 4) ctx.fillRect(0, i, 128, 1);
  const texture = new THREE.CanvasTexture(swatch);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.flipY = false;
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(13, 13);
  return texture;
}

function coatCollar() {
  const parts = [];
  const fabric = new THREE.Color("#3b3835");
  for (const s of [-1, 1]) {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(
        [
          s * 0.062,
          0.3,
          0.082,
          s * 0.024,
          0.242,
          0.124,
          s * 0.076,
          0.176,
          0.144,
          s * 0.114,
          0.254,
          0.116,
        ],
        3,
      ),
    );
    geometry.setIndex(s > 0 ? [0, 1, 2, 0, 2, 3] : [0, 2, 1, 0, 3, 2]);
    geometry.computeVertexNormals();
    parts.push(colored(geometry, () => fabric));
  }
  parts.push(
    ellipsoid([0, 0.097, 0.15], [0.013, 0.091, 0.007], "#48433d"),
    ellipsoid([0, 0.174, 0.159], [0.009, 0.009, 0.004], "#706356"),
    ellipsoid([0, 0.111, 0.158], [0.008, 0.008, 0.004], "#786b5e"),
  );
  return parts;
}

export function styleDanCarrere(root) {
  const head = root.getObjectByName("Head");
  const chest = root.getObjectByName("Chest");
  const skin = root
    .getObjectsByProperty("isSkinnedMesh", true)
    .find(({ material }) => material.name.includes("face and hands"));
  if (!head || !chest || !skin)
    throw new Error("The named person rig has changed.");
  const owned = [retainStockNeckAndHands(skin)];
  const texture = wovenCloth();
  owned.push(texture);
  for (const { material } of root.getObjectsByProperty("isSkinnedMesh", true)) {
    if (
      material.name.includes("Forest green") ||
      material.name.includes("Gold collar")
    ) {
      material.color.set("#ffffff");
      material.map = texture;
      material.roughness = 0.98;
      material.needsUpdate = true;
    }
    if (material.name.includes("sneakers")) material.color.set("#8f8b80");
  }
  function attach(name, bone, parts, doubleSided = false) {
    const geometry = mergeGeometries(parts);
    parts.forEach((part) => part.dispose());
    const material = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 0.92,
      side: doubleSided ? THREE.DoubleSide : THREE.FrontSide,
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.name = name;
    bone.getWorldPosition(mesh.position);
    root.add(mesh);
    bone.attach(mesh);
    owned.push(geometry, material);
  }
  attach("CarrereHeadAndHat", head, faceParts());
  attach("CarrereCollarAndPlacket", chest, coatCollar(), true);
  return () => owned.forEach((asset) => asset.dispose());
}
