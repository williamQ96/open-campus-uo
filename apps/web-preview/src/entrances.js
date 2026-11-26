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
      // An explicit empty list represents an exterior without a scene entrance.
      if (override.length === 0) return [];
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

function coloredBoxes(parts) {
  const geometries = parts.map(([w, h, d, x, y, z, tint]) => {
    const geometry = new THREE.BoxGeometry(w, h, d).translate(x, y, z);
    const color = new THREE.Color(tint);
    const rgb = new Float32Array(geometry.attributes.position.count * 3);
    for (let i = 0; i < rgb.length; i += 3) color.toArray(rgb, i);
    geometry.setAttribute("color", new THREE.BufferAttribute(rgb, 3));
    return geometry;
  });
  const merged = mergeGeometries(geometries);
  for (const geometry of geometries) geometry.dispose();
  return merged;
}

// Generic paired storefront leaves, in meters. The full marker keeps its
// existing footprint while the leaf dimensions follow typical narrow stiles.
export function createEntrancePortalParts() {
  const bronze = 0xb59d65,
    threshold = 0x8d8b7e,
    aluminum = 0x345e50,
    glass = 0x354f51,
    hardware = 0xb3a47d;
  const trim = [
    [0.15, 2.72, 0.24, -0.9, 1.36, 0, bronze],
    [0.15, 2.72, 0.24, 0.9, 1.36, 0, bronze],
    [1.95, 0.16, 0.24, 0, 2.8, 0, bronze],
    [1.65, 0.034, 0.24, 0, 0.017, 0, threshold],
    [1.65, 0.074, 0.115, 0, 2.312, 0, bronze],
    [1.65, 0.371, 0.026, 0, 2.535, 0, glass],
  ];
  const leaves = [];
  const bottom = 0.039,
    top = 2.264,
    stile = 0.054,
    topRail = 0.057,
    bottomRail = 0.098,
    width = 0.808,
    halfInfill = (width - 2 * stile) / 2,
    openingBottom = bottom + bottomRail,
    openingTop = top - topRail,
    glassHeight = openingTop - openingBottom,
    glassCenter = (openingBottom + openingTop) / 2;
  for (const side of [-1, 1]) {
    const center = side * 0.412;
    const pull = side * 0.035;
    for (const edge of [-1, 1])
      leaves.push([
        stile,
        top - bottom,
        0.048,
        center + (edge * (width - stile)) / 2,
        (top + bottom) / 2,
        0,
        aluminum,
      ]);
    leaves.push(
      [2 * halfInfill, topRail, 0.048, center, top - topRail / 2, 0, aluminum],
      [
        2 * halfInfill,
        bottomRail,
        0.048,
        center,
        bottom + bottomRail / 2,
        0,
        aluminum,
      ],
      [2 * halfInfill, glassHeight, 0.016, center, glassCenter, 0, glass],
      [0.026, 0.285, 0.025, pull, 1.17, 0.101, hardware],
      [0.026, 0.029, 0.082, pull, 1.04, 0.061, hardware],
      [0.026, 0.029, 0.082, pull, 1.3, 0.061, hardware],
      [0.705, 0.035, 0.061, center, 1.05, -0.047, hardware],
    );
  }
  return {
    "portal-trim": { geometry: coloredBoxes(trim), roughness: 0.59 },
    "portal-door": { geometry: coloredBoxes(leaves), roughness: 0.47 },
  };
}

export function createEntrances({
  scene,
  buildings,
  half,
  field,
  meshesById,
  overrides,
  surfaceHeight,
  onEnter,
}) {
  const entries = inferEntrances(buildings, half, overrides);
  const genericEntries = entries.filter((entry) => !entry.gate);
  const parts = createEntrancePortalParts();
  const marker = (name) => {
    const { geometry, roughness } = parts[name];
    return new THREE.InstancedMesh(
      geometry,
      new THREE.MeshStandardMaterial({ vertexColors: true, roughness }),
      genericEntries.length,
    );
  };
  const frame = marker("portal-trim");
  const door = marker("portal-door");
  // Use the existing full hit surface even through the seams of the new leaves.
  const doorHits = new THREE.InstancedMesh(
    new THREE.BoxGeometry(1.65, 2.65, 0.12).translate(0, 1.35, 0),
    new THREE.MeshBasicMaterial(),
    entries.length,
  );
  doorHits.name = "Entrance interaction";
  doorHits.visible = false;
  frame.name = "Estimated entrance frames";
  door.name = "Building entrance portals";
  const matrix = new THREE.Matrix4(),
    quaternion = new THREE.Quaternion(),
    ray = new THREE.Raycaster();
  let genericIndex = 0;
  for (const [index, entry] of entries.entries()) {
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
    y = Math.max(y, surfaceHeight?.(...entry.position) ?? y);
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
    doorHits.setMatrixAt(index, matrix);
    if (!entry.gate) {
      frame.setMatrixAt(genericIndex, matrix);
      door.setMatrixAt(genericIndex++, matrix);
    }
  }
  frame.computeBoundingSphere();
  door.computeBoundingSphere();
  doorHits.computeBoundingSphere();
  scene.add(frame, door, doorHits);
  const pickTargets = [doorHits, frame];
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
        const source = hit.object === doorHits ? entries : genericEntries;
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
