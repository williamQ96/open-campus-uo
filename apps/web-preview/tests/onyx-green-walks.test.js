// SPDX-License-Identifier: Apache-2.0
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createPavedRouteAccess } from "../src/paved-route-access.js";

const read = (url) => JSON.parse(readFileSync(new URL(url, import.meta.url)));

test("the Onyx Green connection follows the East 13th sidewalk tie", () => {
  const surfaces = read("../data/campus-route-surfaces.json");
  const site = read("../public/scene/onyx-green-walks-review/site.json");
  const coverage = surfaces.find(
    ({ package: name }) => name === "onyx-green-walks-review",
  );
  assert.equal(coverage.sha256, site.sha256);
  const walk = site.walkable_ground.paths.find(({ end_enu_m }) => end_enu_m);
  const access = createPavedRouteAccess(coverage.polygons_enu_m);
  assert.deepEqual(walk.end_enu_m, [-212.89, 8.72]);
  assert.equal(access(walk.end_enu_m, [-220.57, 27.25]), false);
  assert.equal(access(walk.end_enu_m, walk.points_enu_m.at(-1)), true);
  assert.equal(access(walk.points_enu_m.at(-1), walk.end_enu_m), true);
});
