// SPDX-License-Identifier: Apache-2.0
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { insidePolygon, isBlocked, sampleGround } from "./world.js";

// Estimated frontage, not a claim about real accessibility or surveyed doors.
// Per-ID ENU overrides can replace this inference without editing the shared viewer.
export function inferEntrances(buildings, half, overrides = {}) {
  return buildings.flatMap((building) => {
    const approachOf = ({ east, north, nx, nn, approachDistance = 2.5 }) => [
      east + nx * approachDistance,
      -north - nn * approachDistance,
    ];
    const clear = (p) => !isBlocked(...approachOf(p), buildings, half, 0.5);
    const describe = (p) => {
      const { east, north, nx, nn, gate, authored, snapToFacade, thresholdZ } =
        p;
      return {
        id: building.id,
        name: building.name || "Campus building",
        position: [east, -north],
        outward: [nx, -nn],
        approach: approachOf(p),
        estimated: !authored,
        walkable: clear(p),
        ...(gate && { gate }),
        ...(snapToFacade === false && { snapToFacade }),
        ...(thresholdZ !== undefined && { thresholdZ }),
      };
    };
    const readOverride = (override) => {
      if (
        !Array.isArray(override?.position_enu_m) ||
        override.position_enu_m.length !== 2 ||
        !override.position_enu_m.every(Number.isFinite) ||
        !Number.isFinite(override.outward_degrees)
      )
        return null;
      const angle = (override.outward_degrees * Math.PI) / 180;
      const distance = override.approach_distance_m;
      return {
        east: override.position_enu_m[0],
        north: override.position_enu_m[1],
        nx: Math.sin(angle),
        nn: Math.cos(angle),
        authored: override.estimated !== true,
        gate: override.gate,
        snapToFacade: override.snap_to_facade,
        approachDistance:
          Number.isFinite(distance) && distance > 0 && distance < 5
            ? distance
            : 2.5,
        thresholdZ: Number.isFinite(override.threshold_z_m)
          ? override.threshold_z_m
          : undefined,
      };
    };
    const override = overrides[building.id];
    if (Array.isArray(override)) {
      const doors = override.map(readOverride).filter(Boolean);
      if (doors.length) return doors.map(describe);
    }
    const ring = building.footprint_enu_m,
      candidates = [];
    for (let i = 0; i < ring.length; i++) {
      const a = ring[i],
        b = ring[(i + 1) % ring.length];
      const dx = b[0] - a[0],
        dn = b[1] - a[1],
        length = Math.hypot(dx, dn);
      if (length < 1.3) continue;
      const east = (a[0] + b[0]) / 2,
        north = (a[1] + b[1]) / 2;
      let nx = -dn / length,
        nn = dx / length;
      if (insidePolygon(east + nx * 0.1, north + nn * 0.1, ring)) {
        nx *= -1;
        nn *= -1;
      }
      candidates.push({ east, north, nx, nn, length });
    }
    candidates.sort((a, b) => b.length - a.length);
    const door = readOverride(override);
    if (door) candidates.unshift(door);
    const candidate = candidates.find(clear) || candidates[0];
    return candidate ? [describe(candidate)] : [];
  });
}

// Shared portal trim for entrances whose building mesh has no modeled doors.
export function createEntranceFrameGeometry() {
  const frameParts = [
    [-0.9, 1.4, 0, 0.15, 2.8, 0.24],
    [0.9, 1.4, 0, 0.15, 2.8, 0.24],
    [0, 2.8, 0, 1.95, 0.16, 0.24],
  ].map(([x, y, z, w, h, d]) =>
    new THREE.BoxGeometry(w, h, d).translate(x, y, z),
  );
  // Thin trim lies just outside each face of the opaque panel. Single-sided
  // planes replace closed boxes so all instances retain detail at lower cost.
  for (const side of [-1, 1]) {
    for (const [x, y, width, height] of [
      [0, 1.35, 0.035, 2.65],
      [-0.14, 1.24, 0.045, 0.28],
      [0.14, 1.24, 0.045, 0.28],
    ]) {
      const part = new THREE.PlaneGeometry(width, height);
      if (side < 0) part.rotateY(Math.PI);
      part.translate(x, y, side * 0.061);
      frameParts.push(part);
    }
  }
  const result = mergeGeometries(frameParts);
  frameParts.forEach((p) => p.dispose());
  return result;
}

export function createEntranceDoorGeometry() {
  return new THREE.BoxGeometry(1.65, 2.65, 0.12).translate(0, 1.35, 0);
}

export function createEntrances({
  scene,
  buildings,
  half,
  field,
  meshesById,
  overrides,
  onEnter,
}) {
  const entries = inferEntrances(buildings, half, overrides);
  const genericEntries = entries.filter((entry) => !entry.gate);
  const modeledEntries = entries.filter((entry) => entry.gate);
  const frameGeometry = createEntranceFrameGeometry();
  const frame = new THREE.InstancedMesh(
    frameGeometry,
    new THREE.MeshStandardMaterial({ color: 0xead5a0, roughness: 0.85 }),
    genericEntries.length,
  );
  const door = new THREE.InstancedMesh(
    createEntranceDoorGeometry(),
    new THREE.MeshStandardMaterial({ color: 0x285d51, roughness: 0.72 }),
    genericEntries.length,
  );
  // Raycast the modeled entries without drawing a second door over their mesh.
  const modeledDoors = modeledEntries.length
    ? new THREE.InstancedMesh(
        door.geometry,
        door.material,
        modeledEntries.length,
      )
    : null;
  if (modeledDoors) {
    modeledDoors.name = "Modeled entrance interaction";
    modeledDoors.visible = false;
  }
  frame.name = "Estimated entrance frames";
  door.name = "Building entrance portals";
  const matrix = new THREE.Matrix4(),
    quaternion = new THREE.Quaternion(),
    ray = new THREE.Raycaster();
  let genericIndex = 0;
  let modeledIndex = 0;
  for (const entry of entries) {
    let [x, z] = entry.position;
    const [nx, nz] = entry.outward;
    let y = sampleGround(field, x, z);
    const target = meshesById.get(entry.id);
    if (target && entry.snapToFacade !== false) {
      target.updateWorldMatrix(true, true);
      ray.set(
        new THREE.Vector3(x + nx * 6, y + 1.35, z + nz * 6),
        new THREE.Vector3(-nx, 0, -nz),
      );
      ray.far = 12;
      const hit = ray
        .intersectObject(target, true)
        .find(
          (h) =>
            Math.abs(
              h.face.normal.clone().transformDirection(h.object.matrixWorld).y,
            ) < 0.35,
        );
      if (hit) {
        x = hit.point.x;
        z = hit.point.z;
        y = sampleGround(field, x, z);
      }
    }
    entry.position = [x + nx * 0.14, z + nz * 0.14];
    entry.ground = y;
    quaternion.setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.atan2(nx, nz));
    matrix.compose(
      new THREE.Vector3(
        entry.position[0],
        entry.thresholdZ ?? y,
        entry.position[1],
      ),
      quaternion,
      new THREE.Vector3(1, 1, 1),
    );
    if (entry.gate) {
      modeledDoors.setMatrixAt(modeledIndex++, matrix);
    } else {
      frame.setMatrixAt(genericIndex, matrix);
      door.setMatrixAt(genericIndex++, matrix);
    }
  }
  frame.computeBoundingSphere();
  door.computeBoundingSphere();
  scene.add(frame, door);
  const pickTargets = [door, frame];
  if (modeledDoors) {
    modeledDoors.computeBoundingSphere();
    scene.add(modeledDoors);
    pickTargets.push(modeledDoors);
  }
  const button = document.createElement("button");
  button.className = "entrance-action";
  button.hidden = true;
  scene.userData.entranceCount = entries.length;
  document.querySelector("#app").append(button);
  let nearby = null;
  button.addEventListener("click", () => nearby && onEnter(nearby));
  return {
    entries,
    update(player, view, paused) {
      let nearest = null,
        best = 5;
      if (view !== "aerial" && !paused)
        for (const entry of entries) {
          const d = Math.hypot(
            player.x - entry.position[0],
            player.z - entry.position[1],
          );
          if (d < best && Math.abs(player.y - entry.ground) < 2.2) {
            best = d;
            nearest = entry;
          }
        }
      if (nearby !== nearest) {
        nearby = nearest;
        button.hidden = !nearby;
        if (nearby) button.textContent = `Enter ${nearby.name} · E`;
      }
    },
    activate() {
      if (nearby) {
        onEnter(nearby);
        return true;
      }
      return false;
    },
    pick(raycaster, wallDistance = Infinity) {
      const hit = raycaster.intersectObjects(pickTargets, false)[0];
      if (hit && hit.distance <= wallDistance + 0.35) {
        const source =
          hit.object === modeledDoors ? modeledEntries : genericEntries;
        onEnter(source[hit.instanceId]);
        return true;
      }
      return false;
    },
    get nearby() {
      return nearby?.id || null;
    },
  };
}
