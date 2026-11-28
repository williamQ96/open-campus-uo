# SPDX-License-Identifier: Apache-2.0
"""Generate a small first-frame scene and bounds for the refinement queue."""

import csv
import json
from pathlib import Path

from shapely.geometry import Polygon
import trimesh

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "apps/web-preview/public/scene"


def read(path):
    return json.loads(path.read_bytes())


def main():
    manifest = read(SCENE / "manifest.json")
    config = read(SCENE / "presentation.json")
    field = read(SCENE / manifest["heightfield_url"])
    with (ROOT / "docs/asset-refinement-inventory.csv").open(encoding="utf-8-sig") as stream:
        active = {
            row["asset_id"][4:]
            for row in csv.DictReader(stream)
            if row["asset_id"].startswith("EXT:") and row["level"] == "2"
        }
    buildings = {row["id"]: row for row in manifest["buildings"]}
    priorities = {}
    for candidate in config.values():
        if not isinstance(candidate, dict) or not candidate.get("url", "").endswith("/site.json"):
            continue
        desc = read(SCENE / candidate["url"])
        for row in desc.get("buildings", []):
            if row["id"] in active:
                buildings[row["id"]] = {**buildings.get(row["id"], {}), **row}
        if not desc.get("url", "").endswith(".glb"):
            continue
        content = trimesh.load_scene(SCENE / desc["url"], process=False)
        if content.bounds is not None:
            (east0, _, south0), (east1, _, south1) = content.bounds
            priorities[candidate["url"]] = [
                round(value, 1) for value in (east0, -south1, east1, -south0)
            ]
    assert active <= buildings.keys(), active - buildings.keys()
    footprints = []
    for id in sorted(active):
        record = buildings[id]
        polygon = Polygon(record["footprint_enu_m"]).simplify(0.22)
        ring = [[round(e, 1), round(n, 1)] for e, n in list(polygon.exterior.coords)[:-1]]
        if len(set(map(tuple, ring))) < 3:
            continue
        footprints.append([
            round(record["base_z_m"], 1),
            round(record["roof_z_m"], 1),
            ring,
        ])
    step = 8
    assert (field["nx"] - 1) % step == (field["ny"] - 1) % step == 0
    heights = [
        round(field["heights_m"][j * field["nx"] + i], 1)
        for j in range(0, field["ny"], step)
        for i in range(0, field["nx"], step)
    ]
    output = {
        "version": 1,
        "camera": config["overview"],
        "terrain": [
            field["min_east_m"], field["min_north_m"], field["spacing_m"] * step,
            (field["nx"] - 1) // step + 1, (field["ny"] - 1) // step + 1, heights,
        ],
        "roads": [
            [row["width_m"], [[round(e, 1), round(n, 1)] for e, n in row["centerline_enu_m"]]]
            for row in manifest["corridors"]["features"]
            if row["kind"] == "road"
        ],
        "buildings": footprints,
        "reviewBounds": priorities,
    }
    path = SCENE / "campus-overview.json"
    path.write_bytes((json.dumps(output, separators=(",", ":")) + "\n").encode())
    print(f"{len(footprints)} building outlines, {len(priorities)} review bounds, {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
