# SPDX-License-Identifier: Apache-2.0
"""Reconstruct the registered South University and East 20th–21st houses."""

import argparse
from importlib import import_module
from pathlib import Path

from shapely import set_precision
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

residential = import_module("build-bardell-buckingham-review")
agate, fairmount, garden, hilyard, older = (
    residential.agate,
    residential.fairmount,
    residential.garden,
    residential.hilyard,
    residential.older,
)
PACKAGE = "south-university-east-twentieth-review"
GROUND = "south-university-east-twentieth-paving"


def build(row, field, paving):
    patch, _, world = older.transforms(row)
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
    parts, supports = [], []
    porch = row.get("porch")
    if porch:
        cut = patch(porch["bounds"])
        wall = orient(wall.difference(cut))
    roof = garden.roof_sections(parts, outline, wall, row["base_z_m"], row, grid=0.0002)
    views, gate_plan = residential.facade(parts, row, wall, field, world, roof)
    gates = residential.registered_approach(parts, paving, row, field, gate_plan, views)
    if porch:
        threshold = gates[0]["threshold_z_m"]
        platform = outline.intersection(cut).buffer(-0.07)
        hilyard.pier(parts, field, platform, threshold, row["trim_color"])
        for s, t in porch["posts"]:
            post = patch((s - 0.083, t - 0.083, s + 0.083, t + 0.083))
            hilyard.pier(
                parts, field, post, roof(world(s, t)) - 0.12, row["trim_color"]
            )
            supports.append(post)
    older.roof_equipment(parts, row, outline, roof, patch)
    return agate.output(parts, row, outline, wall, supports, gates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(),
        PACKAGE,
        GROUND,
        "south_university_east_twentieth_site",
        build,
    )


if __name__ == "__main__":
    main()
