// SPDX-License-Identifier: Apache-2.0
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";

const pawOffsets = [
  [-0.052, 0.026, 0.115],
  [0.052, 0.026, 0.115],
  [-0.071, 0.032, -0.114],
  [0.071, 0.032, -0.114],
];
const tailPoints = [
  [0, 0.12, -0.2],
  [0, 0.151, -0.272],
  [0.007, 0.247, -0.319],
  [0.009, 0.352, -0.296],
  [0.002, 0.405, -0.223],
  [-0.011, 0.387, -0.151],
  [-0.02, 0.332, -0.113],
];
const axisX = new THREE.Vector3(1, 0, 0);
const { lerp, smoothstep } = THREE.MathUtils;
export const squirrelStride = 0.43;
export const squirrelStance = 0.36;
export const squirrelPawPhase = [0, 0.025, 0.55, 0.575];

export function createSquirrelModel() {
  const bones = [];
  function joint(name, offset, parent = null) {
    const bone = new THREE.Bone();
    bone.name = name;
    bone.position.fromArray(offset);
    parent?.add(bone);
    bones.push(bone);
    return bone;
  }
  const pivot = joint("SquirrelPivot", [0, 0, 0]);
  const spine = joint("SquirrelSpine", [0, 0.13, -0.031], pivot);
  const head = joint("SquirrelHead", [0, 0.034, 0.15], spine);
  const tail = joint("SquirrelTail", [0, -0.01, -0.169], spine);
  const tailTip = joint("SquirrelTailTip", [0.007, 0.127, -0.119], tail);
  const paws = pawOffsets.map((offset, i) =>
    joint("SquirrelPaw" + i, offset, pivot),
  );
  const coat = new THREE.Color("#8b6b52");
  const belly = new THREE.Color("#cbb7a0");
  const brown = new THREE.Color("#634e40");
  const shade = new THREE.Color();
  const parts = [];
  function addSkin(
    geometry,
    primary,
    tint,
    secondary = primary,
    mix = () => 0,
  ) {
    const a = bones.indexOf(primary);
    const b = bones.indexOf(secondary);
    const p = geometry.getAttribute("position");
    const colors = new Float32Array(p.count * 3);
    const indices = new Uint16Array(p.count * 4);
    const weights = new Float32Array(p.count * 4);
    for (let i = 0; i < p.count; i++) {
      const share = mix(i, p);
      const offset = i * 4;
      tint(i, p).toArray(colors, i * 3);
      indices[offset] = a;
      indices[offset + 1] = b;
      weights[offset] = 1 - share;
      weights[offset + 1] = share;
    }
    geometry.deleteAttribute("uv");
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute("skinIndex", new THREE.BufferAttribute(indices, 4));
    geometry.setAttribute("skinWeight", new THREE.BufferAttribute(weights, 4));
    parts.push(geometry);
  }
  function ellipsoid(center, radii, color, bone, settings = {}) {
    const {
      segments = [8, 5],
      angle = 0,
      secondary,
      mix,
      underside,
    } = settings;
    const geometry = new THREE.SphereGeometry(1, ...segments);
    geometry.scale(...radii);
    geometry.rotateX(angle);
    geometry.translate(...center);
    addSkin(
      geometry,
      bone,
      (_i, p) =>
        underside
          ? shade
              .copy(underside)
              .lerp(
                color,
                smoothstep(p.getY(_i), center[1] - radii[1], center[1] + 0.015),
              )
          : color,
      secondary,
      mix,
    );
  }
  ellipsoid([0, 0.128, -0.051], [0.083, 0.087, 0.144], coat, spine, {
    segments: [10, 6],
    underside: belly,
  });
  ellipsoid([0, 0.128, -0.119], [0.09, 0.092, 0.087], coat, spine, {
    underside: belly,
  });
  ellipsoid([0, 0.139, 0.062], [0.069, 0.078, 0.078], coat, spine, {
    angle: -0.35,
    underside: belly,
  });
  ellipsoid([0, 0.202, 0.148], [0.063, 0.065, 0.076], coat, head, {
    segments: [10, 6],
    underside: belly,
  });
  ellipsoid([0, 0.177, 0.201], [0.047, 0.034, 0.043], belly, head);
  ellipsoid(
    [0, 0.186, 0.239],
    [0.019, 0.013, 0.012],
    new THREE.Color("#3b2b25"),
    head,
    {
      segments: [6, 4],
    },
  );
  for (const side of [-1, 1]) {
    const eye = new THREE.Color("#201d1b");
    ellipsoid([side * 0.047, 0.219, 0.187], [0.013, 0.016, 0.011], eye, head, {
      segments: [6, 4],
    });
    ellipsoid(
      [side * 0.054, 0.226, 0.194],
      [0.0037, 0.0043, 0.0033],
      new THREE.Color("#dadacf"),
      head,
      {
        segments: [4, 3],
      },
    );
    ellipsoid(
      [side * 0.041, 0.259, 0.109],
      [0.024, 0.045, 0.018],
      brown,
      head,
      {
        angle: -0.27,
        segments: [6, 5],
      },
    );
    ellipsoid(
      [side * 0.043, 0.264, 0.125],
      [0.016, 0.033, 0.007],
      new THREE.Color("#b38a7d"),
      head,
      {
        angle: -0.27,
        segments: [5, 4],
      },
    );
  }
  for (const [i, [x, y, z]] of pawOffsets.entries()) {
    const hind = i > 1;
    ellipsoid(
      [x, hind ? 0.09 : 0.072, z - 0.011],
      hind ? [0.039, 0.064, 0.052] : [0.024, 0.048, 0.026],
      coat,
      paws[i],
      {
        segments: [6, 5],
        angle: hind ? -0.4 : 0.19,
        secondary: spine,
        mix: (index, positions) =>
          smoothstep(positions.getY(index), 0.041, 0.111),
      },
    );
    ellipsoid(
      [x, y, z + 0.011],
      hind ? [0.023, y - 0.003, 0.043] : [0.017, y - 0.003, 0.033],
      brown,
      paws[i],
      {
        segments: [6, 4],
      },
    );
  }

  const curve = new THREE.CatmullRomCurve3(
    tailPoints.map((point) => new THREE.Vector3().fromArray(point)),
  );
  const vertices = [],
    indices = [];
  const rings = 16,
    sides = 9;
  for (let i = 0; i <= rings; i++) {
    const t = i / rings;
    const point = curve.getPoint(t);
    const across = curve.getTangent(t).cross(axisX).normalize();
    const radius = lerp(0.022, 0.007, t) + 0.052 * Math.sin(Math.PI * t);
    for (let j = 0; j < sides; j++) {
      const a = (j / sides) * Math.PI * 2;
      vertices.push(
        ...point
          .clone()
          .addScaledVector(axisX, Math.cos(a) * radius)
          .addScaledVector(across, Math.sin(a) * radius * 0.77)
          .toArray(),
      );
      if (!i) continue;
      const b = (i - 1) * sides + j;
      const next = (i - 1) * sides + ((j + 1) % sides);
      indices.push(b, next, b + sides, next, next + sides, b + sides);
    }
  }
  for (let j = 1; j < sides - 1; j++) {
    indices.push(0, j + 1, j);
    indices.push(rings * sides, rings * sides + j, rings * sides + j + 1);
  }
  const tailGeometry = new THREE.BufferGeometry();
  tailGeometry.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(vertices, 3),
  );
  tailGeometry.setIndex(indices);
  tailGeometry.computeVertexNormals();
  addSkin(
    tailGeometry,
    tail,
    (i) =>
      shade
        .copy(coat)
        .lerp(
          i % sides < 5 ? belly : brown,
          0.19 + Math.floor(i / sides) * 0.017,
        ),
    tailTip,
    (i) => smoothstep(Math.floor(i / sides) / rings, 0.31, 0.64),
  );
  const geometry = mergeGeometries(parts);
  for (const part of parts) part.dispose();
  const mesh = new THREE.SkinnedMesh(
    geometry,
    new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.93 }),
  );
  mesh.name = "CampusSquirrel";
  mesh.add(pivot);
  mesh.updateMatrixWorld(true);
  mesh.bind(new THREE.Skeleton(bones));
  return mesh;
}

export function createSquirrelPose(mesh) {
  const { bones } = mesh.skeleton;
  const [pivot, spine, head, tail, tailTip, ...paws] = bones;
  if (
    pivot?.name !== "SquirrelPivot" ||
    tailTip?.name !== "SquirrelTailTip" ||
    paws.length !== pawOffsets.length ||
    paws.some(({ name }, i) => name !== "SquirrelPaw" + i)
  )
    throw new Error("The squirrel articulation does not match the export.");
  const spineY = spine.position.y;
  return (phase, blend, climbPitch = 0, alert = 0) => {
    const angle = phase * Math.PI * 2;
    pivot.rotation.x = climbPitch;
    const lift = 0.017 * Math.cos(angle * 2 - 0.6) + 0.013;
    spine.position.y = spineY + lift * blend;
    spine.rotation.x = lerp(-0.21, Math.sin(angle) * 0.21, blend);
    head.rotation.x = lerp(-0.13, -Math.sin(angle + 0.25) * 0.16, blend);
    head.rotation.y = alert * (1 - blend) * 0.19;
    tail.rotation.x = lerp(-0.15, Math.sin(angle - 0.6) * 0.23, blend);
    tail.rotation.z = Math.sin(angle) * blend * 0.06;
    tailTip.rotation.x = lerp(-0.1, Math.sin(angle - 1.1) * 0.34, blend);
    for (const [i, paw] of paws.entries()) {
      const [x, y, z] = pawOffsets[i];
      const p = (phase + squirrelPawPhase[i]) % 1;
      const swing = Math.max(0, (p - squirrelStance) / (1 - squirrelStance));
      const swept = swing * swing * (3 - 2 * swing);
      const stride = squirrelStride * squirrelStance;
      const step =
        p <= squirrelStance
          ? stride / 2 - p * squirrelStride
          : stride * (swept - 0.5);
      const airborne = Math.sin(swing * Math.PI) ** 2;
      paw.position.set(
        x,
        y + lerp(i < 2 ? 0.022 : 0, airborne * 0.075, blend),
        z + lerp(i < 2 ? -0.018 : 0.019, step, blend),
      );
      paw.rotation.x = lerp(i < 2 ? -0.19 : 0, airborne * 0.5, blend);
    }
  };
}
