import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createExteriorDetail } from "../src/exterior-detail.js";
import {
  overlayCollisionBoxesForDetail,
  attachCollisionBoxes,
  segmentHitsBoxes,
} from "../src/collision-supplement.js";
import { isBlocked, movePlayer } from "../src/world.js";
const read = (n) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${n}`, import.meta.url)));
test("Ford facade is pinned, adjacent and route-clear", () => {
  const c = read("presentation.json"),
    raw = readFileSync(
      new URL("../public/scene/ford-alumni-detail.json", import.meta.url),
    ),
    d = JSON.parse(raw),
    b = structuredClone(
      read("manifest.json").buildings.find((x) => x.id === d.building_id),
    );
  assert.equal(
    c.exterior_details.find((x) => x.url === "ford-alumni-detail.json").sha256,
    createHash("sha256").update(raw).digest("hex"),
  );
  assert.equal(d.base_asset_sha256, c.asset_sha256);
  assert.equal(d.building_id, "context-b0066");
  assert.equal(d.replace_building, false);
  assert.equal(d.objects.length, 52);
  assert.ok(
    createExteriorDetail(d, c.asset_sha256, new Set([d.building_id])).children
      .length,
  );
  const boxes = overlayCollisionBoxesForDetail(d);
  assert.equal(
    attachCollisionBoxes([b], [{ buildingId: b.id, boxes, overlay: true }])
      .length,
    4,
  );
  assert.equal(isBlocked(274, 18.2, [b], 1000, 0.01), true);
  assert.equal(isBlocked(293.7, 40, [b], 1000, 0.01), true);
  const walker = { x: 274, y: 0, z: 16 };
  movePlayer(walker, { x: 0, z: 4 }, [b], 1000, null, false);
  assert.ok(walker.z < 17.95, `player crossed facade: ${walker.z}`);
  const g = read("navigation.json");
  assert.equal(
    g.edges.filter(([a, b]) =>
      segmentHitsBoxes(g.nodes_enu_m[a], g.nodes_enu_m[b], boxes, 0.5),
    ).length,
    0,
  );
});
