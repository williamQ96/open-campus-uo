// SPDX-License-Identifier: Apache-2.0
import { writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import {
  AnimationClip,
  QuaternionKeyframeTrack,
  VectorKeyframeTrack,
} from "three";
import { GLTFExporter } from "three/addons/exporters/GLTFExporter.js";
import {
  createSquirrelModel,
  createSquirrelPose,
} from "../src/squirrel-model.js";

// The texture-free binary exporter only reads Blob data as ArrayBuffers.
globalThis.FileReader ??= class {
  async readAsArrayBuffer(blob) {
    this.result = await blob.arrayBuffer();
    this.onloadend();
  }
};

function clip(mesh, name, duration, sample) {
  const bones = mesh.skeleton.bones;
  const times = [];
  const samples = bones.map(() => ({ position: [], quaternion: [] }));
  for (let i = 0; i <= 40; i++) {
    const phase = i / 40;
    times.push(phase * duration);
    sample(phase);
    for (const [index, bone] of bones.entries()) {
      samples[index].position.push(...bone.position.toArray());
      samples[index].quaternion.push(...bone.quaternion.toArray());
    }
  }
  const tracks = samples.flatMap(({ position, quaternion }, index) => [
    new VectorKeyframeTrack(bones[index].name + ".position", times, position),
    new QuaternionKeyframeTrack(
      bones[index].name + ".quaternion",
      times,
      quaternion,
    ),
  ]);
  return new AnimationClip(name, duration, tracks);
}

const output = resolve(
  process.argv[2] || "public/animals/campus-squirrel-l2.glb",
);
const mesh = createSquirrelModel();
const pose = createSquirrelPose(mesh);
const animations = [
  clip(mesh, "Bound", 0.32, (phase) => pose(phase, 1)),
  clip(mesh, "Perch", 2.6, (phase) =>
    pose(0, 0, 0, Math.sin(phase * Math.PI * 2)),
  ),
  clip(mesh, "Climb", 0.36, (phase) => pose(phase, 1, -Math.PI / 2)),
];
mesh.skeleton.pose();
const glb = await new GLTFExporter().parseAsync(mesh, {
  binary: true,
  animations,
});
await writeFile(output, new Uint8Array(glb));
console.log(output);
