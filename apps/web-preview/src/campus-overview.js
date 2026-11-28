// SPDX-License-Identifier: Apache-2.0
import * as THREE from "three";

function mesh(positions, color) {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(positions, 3),
  );
  geometry.computeVertexNormals();
  return new THREE.Mesh(
    geometry,
    new THREE.MeshLambertMaterial({ color, side: THREE.DoubleSide }),
  );
}

export function createCampusOverview(data) {
  if (data?.version !== 1) throw new Error("Unsupported campus overview.");
  const [east, north, spacing, width, rows, heights] = data.terrain;
  const land = [],
    roads = [],
    roofs = [],
    walls = [];
  const ground = (x, n, i, j) => [
    east + (x + i) * spacing,
    heights[(n + j) * width + x + i],
    -(north + (n + j) * spacing),
  ];
  const height = (x, n) => {
    const [u, v] = [
      THREE.MathUtils.clamp((x - east) / spacing, 0, width - 1),
      THREE.MathUtils.clamp((n - north) / spacing, 0, rows - 1),
    ];
    const i = Math.min(Math.floor(u), width - 2),
      j = Math.min(Math.floor(v), rows - 2),
      a = u - i,
      b = v - j;
    const h = (dx, dy) => heights[(j + dy) * width + i + dx];
    return a + b <= 1
      ? h(0, 0) + a * (h(1, 0) - h(0, 0)) + b * (h(0, 1) - h(0, 0))
      : h(1, 1) + (1 - a) * (h(0, 1) - h(1, 1)) + (1 - b) * (h(1, 0) - h(1, 1));
  };
  for (let j = 0; j < rows - 1; j++) {
    for (let i = 0; i < width - 1; i++) {
      const a = ground(i, j, 0, 0),
        b = ground(i, j, 1, 0),
        c = ground(i, j, 0, 1),
        d = ground(i, j, 1, 1);
      land.push(...a, ...b, ...c, ...c, ...b, ...d);
    }
  }
  for (const [roadWidth, points] of data.roads) {
    for (let i = 1; i < points.length; i++) {
      const [x, n] = points[i - 1],
        [dx, dn] = [points[i][0] - x, points[i][1] - n],
        length = Math.hypot(dx, dn);
      if (length < 0.01) continue;
      const steps = Math.ceil(length / 9),
        nx = (dn * roadWidth) / (2 * length),
        nn = (-dx * roadWidth) / (2 * length);
      const at = (t, side) => {
        const e = x + dx * t + nx * side,
          y = n + dn * t + nn * side;
        return [e, height(e, y) + 0.78, -y];
      };
      for (let j = 0; j < steps; j++) {
        const a = at(j / steps, -1),
          b = at(j / steps, 1),
          c = at((j + 1) / steps, -1),
          d = at((j + 1) / steps, 1);
        roads.push(...a, ...b, ...c, ...c, ...b, ...d);
      }
    }
  }
  for (const [base, top, ring] of data.buildings) {
    const outline = ring.map(([e, n]) => new THREE.Vector2(e, n));
    const roof = ([e, n]) => [e, top, -n];
    const foot = ([e, n]) => [e, Math.min(base, height(e, n)), -n];
    for (const triangle of THREE.ShapeUtils.triangulateShape(outline, []))
      for (const i of triangle) roofs.push(...roof(ring[i]));
    for (let i = 0; i < ring.length; i++) {
      const a = ring[i],
        b = ring[(i + 1) % ring.length];
      walls.push(
        ...roof(a),
        ...foot(a),
        ...roof(b),
        ...roof(b),
        ...foot(a),
        ...foot(b),
      );
    }
  }
  const root = new THREE.Group();
  root.name = "First-frame campus geometry";
  root.add(
    mesh(land, 0xa4ae87),
    mesh(roads, 0x7c817c),
    mesh(walls, 0xbcb3a3),
    mesh(roofs, 0xd4c5ac),
  );
  return root;
}

export function createReviewPriority(camera, locations) {
  const frustum = new THREE.Frustum(),
    matrix = new THREE.Matrix4(),
    point = new THREE.Vector3(),
    sphere = new THREE.Sphere();
  return (url) => {
    const bounds = locations?.[url];
    if (!bounds) return Number.POSITIVE_INFINITY;
    const [west, south, east, north] = bounds;
    sphere.center.set((west + east) / 2, 8, -(south + north) / 2);
    sphere.radius = Math.max(15, Math.hypot(east - west, north - south) / 2);
    camera.updateMatrixWorld();
    frustum.setFromProjectionMatrix(
      matrix.multiplyMatrices(
        camera.projectionMatrix,
        camera.matrixWorldInverse,
      ),
    );
    point.copy(sphere.center).project(camera);
    const visible = frustum.intersectsSphere(sphere);
    return (
      (visible ? 0 : 10_000) +
      Math.hypot(point.x, point.y) * 200 +
      camera.position.distanceTo(sphere.center) * 0.01
    );
  };
}

export async function loadQueued(jobs, priority, onSettled, limit = 8) {
  const queued = jobs.map((run, i) => ({ run, i }));
  const output = new Array(jobs.length);
  await Promise.all(
    Array.from({ length: Math.min(limit, jobs.length) }, async () => {
      while (queued.length) {
        let closest = 0;
        let score = priority(queued[0].i);
        for (let i = 1; i < queued.length; i++) {
          const candidate = priority(queued[i].i);
          if (candidate < score) {
            score = candidate;
            closest = i;
          }
        }
        const [{ run, i }] = queued.splice(closest, 1);
        try {
          output[i] = await run();
        } catch (error) {
          // An isolated rejection must not stop this worker or its peers.
          console.warn(
            "Exterior refinement unavailable; retaining existing geometry.",
            error,
          );
          output[i] = null;
        } finally {
          onSettled();
        }
      }
    }),
  );
  return output;
}
