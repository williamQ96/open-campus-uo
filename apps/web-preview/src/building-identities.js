// SPDX-License-Identifier: Apache-2.0
// Optional, explicitly approximate names for existing source-pinned footprints.
export function applyBuildingIdentities(manifest, dataset) {
  if (
    dataset?.version !== 1 ||
    dataset.source_model_sha256 !== manifest?.model?.sha256 ||
    !Array.isArray(dataset.records) ||
    dataset.records.length > 100
  )
    throw new Error("Invalid building identity dataset");
  const lookup = new Map(manifest.buildings.map((b) => [b.id, b]));
  const pending = [],
    seen = new Set();
  for (const item of dataset.records) {
    const building = lookup.get(item.id);
    let url;
    try {
      url = new URL(item.source_url);
    } catch {
      throw new Error("Invalid identity source");
    }
    if (
      !building ||
      building.name ||
      seen.has(item.id) ||
      typeof item.name !== "string" ||
      !item.name.endsWith(" (approximate)") ||
      item.name.length > 100 ||
      url.protocol !== "https:" ||
      !(
        url.hostname === "uoregon.edu" || url.hostname.endsWith(".uoregon.edu")
      ) ||
      JSON.stringify(item.expected_footprint_enu_m) !==
        JSON.stringify(building.footprint_enu_m)
    )
      throw new Error("Identity target or footprint mismatch");
    seen.add(item.id);
    pending.push([building, item]);
  }
  for (const [building, item] of pending) {
    building.name = item.name;
    building.name_match = "approximate-map-match";
    building.name_source = item.source_url;
    building.anchor_note =
      "Map-based identity proposal; not a surveyed footprint or confirmed match.";
  }
  return pending.length;
}
