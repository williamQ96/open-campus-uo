// SPDX-License-Identifier: Apache-2.0
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { clone } from "three/addons/utils/SkeletonUtils.js";
import { readPinnedScene } from "./pinned-scene.js";
import { addSquirrelEyes } from "./squirrel-detail.js";
import { createSquirrelPose, squirrelStride } from "./squirrel-model.js";

async function loadArticulatedSquirrel(url, sha256) {
  const bytes = await readPinnedScene(url, sha256);
  const gltf = await new GLTFLoader().parseAsync(bytes, "");
  const source = gltf.scene.getObjectByName("CampusSquirrel");
  if (
    !source?.isSkinnedMesh ||
    !source.material?.vertexColors ||
    gltf.scene.getObjectsByProperty("isMesh", true).length !== 1
  )
    throw new Error("Expected one articulated squirrel mesh.");
  createSquirrelPose(source);
  return (properties = {}) => {
    const root = new THREE.Group();
    const body = clone(gltf.scene);
    const mesh = body.getObjectByName(source.name);
    const scale = properties.scale || 1;
    const pose = createSquirrelPose(mesh);
    const ownMaterial = properties.furColor ? mesh.material.clone() : null;
    if (ownMaterial) {
      ownMaterial.color.lerp(new THREE.Color(properties.furColor), 0.32);
      mesh.material = ownMaterial;
    }
    mesh.receiveShadow = true;
    mesh.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 0.58);
    body.scale.setScalar(scale);
    root.name = "Articulated campus squirrel";
    root.add(body);
    let last = null;
    let phase = ((properties.seed ?? 0) % 97) / 97;
    let blend = 0;
    let pitch = 0;
    pose(phase, 0);
    return {
      root,
      animate(time, moving, { distanceM = 0, climbRiseM = 0 } = {}) {
        const dt = last === null ? 1 / 60 : Math.min(0.1, time - last);
        last = time;
        const ease = 1 - Math.exp(-dt * 15);
        blend += (Number(moving) - blend) * ease;
        if (moving && distanceM > 0.0001) {
          phase = (phase + distanceM / (squirrelStride * scale)) % 1;
          const climb = THREE.MathUtils.clamp(climbRiseM / distanceM, -1, 1);
          pitch += (-Math.asin(climb) - pitch) * ease;
        }
        pose(phase, blend, pitch, Math.sin(time * 2 + phase));
      },
      dispose() {
        mesh.skeleton.dispose();
        ownMaterial?.dispose();
        root.removeFromParent();
      },
    };
  };
}

export async function loadWildlifeFactory(
  url,
  yawCorrection = -Math.PI / 2,
  { refinedUrl, sha256 } = {},
) {
  if (refinedUrl && sha256) {
    try {
      return await loadArticulatedSquirrel(refinedUrl, sha256);
    } catch (error) {
      console.warn("Campus squirrel articulation unavailable.", error);
    }
  }
  const asset = await new GLTFLoader().loadAsync(url);
  addSquirrelEyes(asset.scene);
  return (properties = {}) => {
    const root = new THREE.Group(),
      body = asset.scene.clone(true);
    body.rotation.y = yawCorrection;
    body.scale.setScalar(properties.scale || 1);
    const materials = [];
    body.traverse((o) => {
      if (o.isMesh) {
        o.castShadow = false;
        o.receiveShadow = true;
        if (properties.furColor) {
          o.material = o.material.clone();
          o.material.color.set(properties.furColor);
          materials.push(o.material);
        }
      }
    });
    root.add(body);
    root.name = "Low-poly campus squirrel";
    return {
      root,
      dispose() {
        for (const m of materials) m.dispose();
        root.removeFromParent();
      },
    };
  };
}
