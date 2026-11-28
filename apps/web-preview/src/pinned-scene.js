// SPDX-License-Identifier: Apache-2.0
const pinnedDescriptors = new Map();

export function readPinnedScene(url, expected) {
  if (!url.endsWith(".json")) return verifiedBytes(url, expected);
  const key = JSON.stringify([url, expected]);
  if (!pinnedDescriptors.has(key)) {
    // Review dependencies share the same pinned terrain and graph files.
    pinnedDescriptors.set(
      key,
      verifiedBytes(url, expected).catch((error) => {
        pinnedDescriptors.delete(key);
        throw error;
      }),
    );
  }
  return pinnedDescriptors.get(key);
}

async function verifiedBytes(url, expected) {
  const response = await fetch(url);
  if (!response.ok) throw new Error("Could not load the exterior scene asset.");
  const data = await response.arrayBuffer();
  const hash = await crypto.subtle.digest("SHA-256", data);
  const actual = Array.from(new Uint8Array(hash), (part) =>
    part.toString(16).padStart(2, "0"),
  ).join("");
  if (actual !== expected) throw new Error("Exterior scene asset changed.");
  return data;
}

export function isFootprintRing(points) {
  return (
    Array.isArray(points) &&
    points.length >= 3 &&
    points.every(
      (point) =>
        Array.isArray(point) &&
        point.length === 2 &&
        point.every(Number.isFinite),
    )
  );
}
