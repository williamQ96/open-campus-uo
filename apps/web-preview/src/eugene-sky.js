// SPDX-License-Identifier: Apache-2.0
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { randomSource } from "./npc-templates.js";

const DOME_RADIUS = 6800;
const CLOUD_LAYERS = [
  { count: 12, base: 535, spread: 410, elevation: 235, width: 240, depth: 139 },
  { count: 6, base: 1260, spread: 360, elevation: 66, width: 344, depth: 122 },
];

function colorVertices(geometry, sample) {
  const positions = geometry.attributes.position;
  const color = new THREE.Color();
  const colors = new Float32Array(positions.count * 3);
  for (let i = 0; i < positions.count; i++) {
    sample(positions.getX(i), positions.getY(i), positions.getZ(i), color);
    color.toArray(colors, i * 3);
  }
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
}

function atmosphere() {
  // Reflect the sphere, then invert its normals for an inward glTF surface.
  const geometry = new THREE.SphereGeometry(DOME_RADIUS, 40, 22).scale(
    -1,
    1,
    1,
  );
  const n = geometry.attributes.normal;
  for (let i = 0; i < n.count; i++)
    n.setXYZ(i, -n.getX(i), -n.getY(i), -n.getZ(i));
  const horizon = new THREE.Color(0xc7dfec);
  const midSky = new THREE.Color(0x89b8d1);
  const zenith = new THREE.Color(0x558eb9);
  const warm = new THREE.Color(0xe3e2cf);
  const { clamp, smoothstep } = THREE.MathUtils;
  colorVertices(geometry, (x, y, z, color) => {
    const elevation = y / DOME_RADIUS;
    const towardSun = clamp(
      0.5 - (0.76 * x + 0.65 * z) / (2 * DOME_RADIUS),
      0,
      1,
    );
    const glow =
      0.38 * towardSun ** 4 * (1 - smoothstep(elevation, 0.02, 0.46));
    color
      .copy(horizon)
      .lerp(midSky, smoothstep(elevation, -0.02, 0.41))
      .lerp(zenith, smoothstep(elevation, 0.2, 1))
      .lerp(warm, glow);
  });
  return geometry;
}

function cloudBank(layer, index, band, rng) {
  const angle =
    ((index + (band ? 0.47 : 0)) / layer.count) * Math.PI * 2 +
    (rng() - 0.5) * 0.24;
  const distance = 2450 + band * 430 + rng() * 920;
  const base = layer.base + rng() * layer.spread;
  const heading = angle + Math.PI * (0.32 + rng() * 0.3);
  const width = layer.width * (0.84 + 0.62 * rng());
  const depth = layer.depth * (0.68 + 0.66 * rng());
  const height = layer.elevation * (0.64 + 0.68 * rng());
  const phase = rng() * 2 * Math.PI;
  const offset = 0.2 * (rng() - 0.4);
  const geometry = new THREE.SphereGeometry(1, 24, 10);
  const position = geometry.attributes.position;
  const shade = new THREE.Color(band ? 0xb4cbd7 : 0xa8bac8);
  const light = new THREE.Color(band ? 0xf1f3ed : 0xfcf7e8);
  const haze = new THREE.Color(0xc5deea);
  const { clamp } = THREE.MathUtils;
  colorVertices(geometry, (x, y, z, color) => {
    const sunward = -0.31 * x - 0.16 * z;
    const scatter = clamp(0.62 + y * 0.33 + sunward * 0.31, 0, 1);
    color
      .copy(shade)
      .lerp(light, scatter)
      .lerp(haze, distance / 18000);
  });
  for (let i = 0; i < position.count; i++) {
    const x = position.getX(i);
    const y = position.getY(i);
    const z = position.getZ(i);
    const azimuth = Math.atan2(z, x);
    const edge = Math.hypot(x, z);
    const contour =
      1 +
      edge *
        (0.125 * Math.sin(3 * azimuth + phase) +
          0.074 * Math.cos(5 * azimuth - phase) +
          0.039 * Math.sin(7 * azimuth + phase));
    const main = Math.exp(-6 * ((x + 0.28) ** 2 + (z - 0.2) ** 2));
    const secondary = Math.exp(-9 * ((x - 0.48) ** 2 + (z + 0.25) ** 2));
    const crown = 0.68 + 0.42 * main + 0.32 * secondary;
    position.setXYZ(
      i,
      (x * contour + Math.max(y, 0) * offset) * width,
      y < 0 ? y * height * 0.1 : y * height * crown,
      z * contour * depth,
    );
  }
  geometry.computeVertexNormals();
  // SphereGeometry has duplicate pole vertices that have no indexed faces.
  const normals = geometry.attributes.normal;
  for (let i = 0; i < normals.count; i++) {
    if (normals.getX(i) === 0 && normals.getY(i) === 0 && normals.getZ(i) === 0)
      normals.setXYZ(i, 0, Math.sign(position.getY(i)), 0);
  }
  geometry.rotateY(heading);
  geometry.translate(
    distance * Math.cos(angle),
    base,
    distance * Math.sin(angle),
  );
  return geometry;
}

export function createEugeneSky(scene) {
  const root = new THREE.Group();
  root.name = "Eugene fair-weather sky";
  const material = new THREE.MeshBasicMaterial({
    vertexColors: true,
    depthWrite: false,
    fog: false,
    toneMapped: false,
  });
  const dome = new THREE.Mesh(atmosphere(), material);
  dome.name = "atmosphere";
  dome.renderOrder = -1000;
  const rng = randomSource(19347);
  const banks = CLOUD_LAYERS.flatMap((layer, band) =>
    Array.from({ length: layer.count }, (_, index) =>
      cloudBank(layer, index, band, rng),
    ),
  );
  const cloudCount = banks.length;
  const geometry = mergeGeometries(banks);
  for (const bank of banks) bank.dispose();
  const clouds = new THREE.Mesh(geometry, material);
  clouds.name = "cloud-banks";
  clouds.renderOrder = -999;
  root.add(dome, clouds);
  scene.add(root);

  let previousTime = 0;
  let previouslyReduced = false;
  return {
    update(camera, time, reduced = false) {
      root.position.copy(camera.position);
      if (!reduced && !previouslyReduced) {
        clouds.rotation.y += Math.max(0, time - previousTime) * 0.00044;
      }
      previousTime = time;
      previouslyReduced = reduced;
    },
    state: () => ({
      blue: true,
      clouds: cloudCount,
      roundedEdges: true,
      layers: CLOUD_LAYERS.map(({ count }) => count),
    }),
  };
}
