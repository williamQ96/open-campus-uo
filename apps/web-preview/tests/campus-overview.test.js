// SPDX-License-Identifier: Apache-2.0
import assert from "node:assert/strict";
import test from "node:test";
import { BufferGeometry, Float32BufferAttribute } from "three";
import {
  createOverviewFallback,
  loadQueued,
  missingOverviewBuildings,
} from "../src/campus-overview.js";
import { restoreFoundationLawns } from "../src/foundation-lawn-corrections.js";

test("view priority affects queued jobs while started and offscreen work drains", async () => {
  const starts = [];
  const completed = [];
  let preferred = 2;
  let release;
  const inFlight = new Promise((resolve) => (release = resolve));
  const work = Array.from({ length: 5 }, (_, id) => async () => {
    starts.push(id);
    if (id === 2) await inFlight;
    completed.push(id);
    return id;
  });
  let settled = 0;
  const result = loadQueued(
    work,
    (id) => (id === preferred ? 0 : 10),
    () => settled++,
    1,
  );
  assert.deepEqual(starts, [2]);
  preferred = 4;
  release();
  assert.deepEqual(await result, [0, 1, 2, 3, 4]);
  assert.deepEqual(starts, [2, 4, 0, 1, 3]);
  assert.deepEqual(completed, starts);
  assert.equal(settled, 5);
});

test("confirmed lawn correction preserves geometry and paved control vertices", () => {
  const geometry = new BufferGeometry();
  const positions = [-415, 3, -20, -414, 3, 0, -715, 4, 95];
  geometry.setAttribute("position", new Float32BufferAttribute(positions, 3));
  geometry.setAttribute(
    "color",
    new Float32BufferAttribute(Array(9).fill(0.16), 3),
  );
  const before = [...geometry.getAttribute("color").array];
  assert.equal(restoreFoundationLawns(geometry), 1);
  assert.ok(geometry.getAttribute("color").getY(0) > 0.3);
  assert.deepEqual([...geometry.getAttribute("position").array], positions);
  assert.deepEqual(
    [...geometry.getAttribute("color").array].slice(3),
    before.slice(3),
  );
});

test("an absent new building keeps a solid footprint without duplicating a retained predecessor", () => {
  const ring = [
    [0, 0],
    [2, 0],
    [2, 2],
    [0, 2],
  ];
  const isolated = ring.map(([e, n]) => [e + 10, n]);
  const remaining = [{ id: "previous", footprint_enu_m: ring }];
  const fallback = missingOverviewBuildings(
    {
      buildings: [
        ["replacement", 0, 5, ring],
        ["annex", 0, 5, isolated],
      ],
    },
    remaining,
  );
  assert.deepEqual(
    fallback.map(({ id }) => id),
    ["annex"],
  );
  const mesh = createOverviewFallback(fallback[0], () => 0);
  assert.equal(mesh.userData.asset_id, "annex");
  assert.equal(mesh.geometry.getAttribute("position").count, 30);
  assert.equal(mesh.castShadow, true);
  mesh.geometry.dispose();
  mesh.material.dispose();
});
