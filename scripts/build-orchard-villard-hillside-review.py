# SPDX-License-Identifier: Apache-2.0
"""Export the registered Orchard, Villard and Fairmount hillside exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient


columbia = import_module("build-columbia-moss-frontages-review")
agate, emerald = columbia.agate, columbia.emerald
fairmount, garden, geometry = emerald.fairmount, emerald.garden, emerald.geometry
base, millrace = emerald.base, emerald.millrace
PACKAGE = "orchard-villard-hillside-review"
GROUND = "orchard-villard-approaches"
PANEL = (64, 79, 91)
METAL = (129, 139, 139)


def solar_modules(parts, outline, height, arrays):
    for array in arrays:
        center = np.asarray(array["center"])
        east = np.asarray(array["axis"])
        north = np.array([-east[1], east[0]])
        count, courses = array["columns"], array["rows"]
        width, length = array["module"]
        for column in range(count):
            for course in range(courses):
                local = (
                    center
                    + (column - (count - 1) / 2) * width * east
                    + (course - (courses - 1) / 2) * length * north
                )
                points = [
                    local + x * width * east + y * length * north
                    for x, y in (
                        (-0.46, -0.46),
                        (0.46, -0.46),
                        (0.46, 0.46),
                        (-0.46, 0.46),
                    )
                ]
                panel = orient(Polygon(points))
                if not outline.buffer(-0.035).covers(panel):
                    raise ValueError("Registered solar module extends beyond the roof.")
                bottom = min(height((x, y)) for x, y in points) - 0.08
                mesh = geometry.shell(
                    panel, bottom, lambda x, y: height((x, y)) + 0.117, METAL, PANEL
                )
                low = np.isclose(mesh.vertices[:, 1], bottom, atol=1e-6)
                mesh.vertices[low, 1] = [
                    height((x, -z)) + 0.062 for x, _, z in mesh.vertices[low]
                ]
                parts.append(mesh)


def parking(row, field, paving):
    roof, original = columbia.shell(row)
    wall = orient(original.difference(box(*row["parking_cut"])))
    parts = []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    back = {"near": [569.21, -752.72], "bearing": 0}
    supports, gates = emerald.facades(
        parts,
        paving,
        {**row, "frontages": [*row["frontages"], back]},
        wall,
        field,
        height,
    )
    for e, n in row["parking_posts"]:
        post = orient(box(e - 0.10, n - 0.08, e + 0.10, n + 0.08))
        bottom = emerald.grade(field, (e, n)) - 0.06
        base.flat(parts, post, bottom, height((e, n)) - 0.14, row["trim_color"])
        supports.append(post)
    millrace.western.terrace(paving, field, orient(box(*row["parking_paving"])))
    return agate.output(parts, row, roof, wall, supports, gates)


def build(row, field, paving):
    if "parking_cut" in row:
        return parking(row, field, paving)
    if "solar_arrays" in row or row.get("opaque_outbuilding"):
        roof, wall = columbia.shell(row)
        parts = []
        height = garden.roof_sections(
            parts, roof, wall, row["base_z_m"], row, grid=0.0002
        )
        if "solar_arrays" in row:
            supports, gates = emerald.facades(parts, paving, row, wall, field, height)
            solar_modules(parts, roof, height, row["solar_arrays"])
        else:
            supports, gates = [], []
            for _, (span, add, _, plan, _, _) in fairmount.views(parts, wall):
                lower = emerald.grade(field, plan(span / 2, 0)) - 0.18
                ceiling = min(height(plan(0.08, 0)), height(plan(span - 0.08, 0)))
                millrace.siding(
                    add, span, ceiling - 0.21, lower, row["seam_color"], 0.20
                )
        return agate.output(parts, row, roof, wall, supports, gates)
    return emerald.build(row, field, paving)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "orchard_villard_hillside_site", build
    )


if __name__ == "__main__":
    main()
