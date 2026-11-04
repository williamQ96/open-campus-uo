import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const read = (name) =>
  JSON.parse(readFileSync(new URL(`../public/scene/${name}`, import.meta.url)));
test("building information uses known identities and dated official UO sources", () => {
  const data = read("building-info.json"),
    ids = new Set(read("manifest.json").buildings.map((b) => b.id));
  assert.equal(data.version, 1);
  for (const [id, info] of Object.entries(data.records)) {
    assert.ok(ids.has(id), `unknown building ID: ${id}`);
    assert.ok(info.purpose && Array.isArray(info.occupants));
    assert.ok(
      info.occupants.every((name) => typeof name === "string" && name.trim()),
    );
    const url = new URL(info.source.url);
    assert.equal(url.protocol, "https:");
    assert.ok(
      url.hostname === "uoregon.edu" || url.hostname.endsWith(".uoregon.edu"),
    );
    assert.match(info.source.checked_on, /^\d{4}-\d{2}-\d{2}$/);
  }
});
