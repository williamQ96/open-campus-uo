// SPDX-License-Identifier: Apache-2.0
import test from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import { createRouter, routeSample } from "../src/routing.js";
import { createPavedRouteAccess } from "../src/paved-route-access.js";
import { createRouteView } from "../src/navigation-view.js";

test("routing follows connected paths around an obstacle and rejects disconnected destinations", () => {
  const nodes = [
    [0, 0],
    [0, 30],
    [30, 30],
    [30, 0],
    [500, 0],
    [500, 30],
  ];
  const edges = [
    [0, 1, 30, "path"],
    [1, 2, 30, "path"],
    [2, 3, 30, "path"],
    [4, 5, 30, "path"],
  ];
  const clear = (a, b) => a[0] === b[0] && Math.abs(a[1] - b[1]) < 1;
  const router = createRouter({ version: 1, nodes_enu_m: nodes, edges }, clear);
  const result = router.route([0, 0], [30, 0]);
  assert.equal(result.distance, 90);
  assert.deepEqual(result.points, nodes.slice(0, 4));
  assert.equal(router.route([0, 0], [500, 0]), null);
  assert.equal(router.route([200, 200], [30, 0]), null);
  assert.deepEqual(
    routeSample(
      [
        [0, 0],
        [0, 10],
        [10, 10],
      ],
      15,
    ).point,
    [5, 10],
  );
});
test("an edge filter can retire a road while preserving walking paths", () => {
  const nodes = [
    [0, 0],
    [0, 30],
    [50, 30],
    [50, 0],
  ];
  const edges = [
    [0, 3, 50, "road"],
    [0, 1, 30, "path"],
    [1, 2, 50, "path"],
    [2, 3, 30, "path"],
  ];
  const graph = { version: 1, nodes_enu_m: nodes, edges };
  const exactEndpoint = (a, b) => a[0] === b[0] && a[1] === b[1];
  const walk = createRouter(
    graph,
    exactEndpoint,
    (_a, _b, kind) => kind !== "road",
  );
  assert.deepEqual(walk.route(nodes[0], nodes[3]).points, nodes);
  assert.equal(
    createRouter(graph, exactEndpoint).route(nodes[0], nodes[3]).distance,
    50,
  );
});

test("paved route access catches a short gap at a path join", () => {
  const access = createPavedRouteAccess([
    [
      [
        [-1, -1],
        [0.31, -1],
        [0.31, 1],
        [-1, 1],
      ],
    ],
    [
      [
        [0.38, -1],
        [2, -1],
        [2, 1],
        [0.38, 1],
      ],
    ],
  ]);
  assert.equal(access([0, 0], [1, 0]), false);
});

test("paved route access follows a bend and preserves approximate access from a lawn", () => {
  const access = createPavedRouteAccess([
    [
      [
        [-1, -1],
        [21, -1],
        [21, 21],
        [19, 21],
        [19, 1],
        [-1, 1],
      ],
      [
        [4, -0.5],
        [6, -0.5],
        [6, 0.5],
        [4, 0.5],
      ],
    ],
  ]);
  const graph = {
    version: 1,
    nodes_enu_m: [
      [0, 0.75],
      [20, 0.75],
      [20, 20],
    ],
    edges: [
      [0, 1, 20, "path"],
      [1, 2, 19.25, "path"],
    ],
  };
  const router = createRouter(graph, access);
  const start = [1, 0.75];
  const end = [20, 19];
  assert.equal(access(start, end), false);
  assert.equal(access([2, 0], [8, 0]), false);
  assert.equal(access([9, 3], graph.nodes_enu_m[1]), true);
  assert.deepEqual(router.route(start, end).points, [
    start,
    graph.nodes_enu_m[1],
    end,
  ]);
  assert.deepEqual(router.route(end, start).points, [
    end,
    graph.nodes_enu_m[1],
    start,
  ]);
});

test("route ribbon follows terrain, chevrons advance toward B and clear removes geometry", () => {
  const scene = new THREE.Scene(),
    view = createRouteView(scene, (x, z) => x * 0.01 + z * 0.02);
  view.set({
    points: [
      [0, 0],
      [0, 30],
    ],
    distance: 30,
  });
  assert.equal(view.root.children.length, 4);
  const arrows = view.root.children[1],
    a = new THREE.Matrix4(),
    b = new THREE.Matrix4();
  view.update(0);
  arrows.getMatrixAt(0, a);
  view.update(1);
  arrows.getMatrixAt(0, b);
  assert.ok(b.elements[14] < a.elements[14]);
  assert.ok(Number.isFinite(b.elements[13]));
  assert.equal(arrows.material.color.getHex(), 0xffffff);
  view.clear();
  assert.equal(view.root.children.length, 0);
});
