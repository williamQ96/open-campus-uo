# SPDX-License-Identifier: Apache-2.0
"""Export the separately registered pair at 360 and 362 Sunset Drive."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient


hillside = import_module("build-fairmount-summit-hamble-review")
agate, columbia, emerald = hillside.agate, hillside.columbia, hillside.emerald
fairmount, garden = hillside.fairmount, hillside.garden
PACKAGE = "sunset-drive-pair-review"
GROUND = "sunset-drive-pair-approaches"


def recessed_wall(wall, setback):
    east, north, depth = setback
    forward = np.array([east, north])
    sideways = np.array([-north, east])
    points = np.asarray(wall.exterior.coords)
    boundary = (points @ forward).min() + depth
    left, right = (points @ sideways).min() - 1, (points @ sideways).max() + 1
    far = (points @ forward).max() + 1
    inside = Polygon(
        [
            d * forward + s * sideways
            for d, s in ((boundary, left), (far, left), (far, right), (boundary, right))
        ]
    )
    return orient(wall.intersection(inside))


def awnings(parts, face, plan, at):
    endpoints = np.asarray(face.coords)
    tangent = (endpoints[1] - endpoints[0]) / face.length
    for u in (at - 1.57, at + 1.57):
        color = (56, 83, 62)
        anchor = np.asarray(plan(u, 0.0))
        normal = np.asarray(plan(u, 1.0)) - anchor
        footprint = orient(fairmount.rectangle(plan, u - 0.82, u + 0.82, -0.015, 0.66))

        def top(east, north):
            distance = (np.asarray((east, north)) - anchor) @ normal
            return 55.09 - 0.49 * distance

        parts.append(hillside.geometry.shell(footprint, 54.71, top, color, color))
        # The narrow front bar reads against the siding from oblique views.
        left, right = anchor - 0.82 * tangent, anchor + 0.82 * tangent
        fairmount.beam(
            parts,
            (*(left + 0.66 * normal), 54.76),
            (*(right + 0.66 * normal), 54.76),
            0.034,
            (45, 68, 49),
        )


def build(row, field, paving):
    roof, wall = columbia.shell(row)
    if "lower_wall_setback" in row:
        wall = recessed_wall(wall, row["lower_wall_setback"])
    parts = []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    supports, gates = emerald.facades(parts, paving, row, wall, field, height)
    face, span, add, _, plan, at = hillside.hill.at_face(
        parts, wall, row, row["frontages"][0]
    )
    trim = row["trim_color"]
    garage_pad = orient(fairmount.rectangle(plan, at - 2.78, at + 2.78, 0.0, 3.05))
    emerald.millrace.western.terrace(paving, field, garage_pad)
    if "balconies" in row:
        for level, depth, width in row["balconies"]:
            lower, upper = max(0.22, at - width), min(span - 0.22, at + width)
            add(lower, upper, -0.06, depth, level - 0.19, level, trim)
            columbia.railing(parts, plan(lower, depth), plan(upper, depth), level, trim)
            for edge in (lower, upper):
                columbia.railing(
                    parts, plan(edge, 0.04), plan(edge, depth), level, trim
                )
                supports.append(
                    hillside.post(
                        parts, field, plan, edge, depth - 0.15, level, 0.074, trim
                    )
                )
    else:
        awnings(parts, face, plan, at)
        _, span, terrace_add, _, terrace_plan, station = hillside.hill.at_face(
            parts, wall, row, row["frontages"][1]
        )
        level, depth, half = row["terrace"]
        left, right = max(0.12, station - half), min(span - 0.14, station + half)
        base_plan = orient(fairmount.rectangle(terrace_plan, left, right, 0, depth))
        bottom = min(emerald.grade(field, point) for point in base_plan.exterior.coords)
        if bottom >= level - 0.12:
            raise ValueError("The street terrace must sit above its hillside.")
        hillside.base.flat(parts, base_plan, bottom - 0.14, level, (199, 195, 178))
        terrace_add(left, right, 0, depth + 0.042, level - 0.19, level, trim)
        columbia.railing(
            parts, terrace_plan(left, depth), terrace_plan(right, depth), level, trim
        )
        for end in (left, right):
            columbia.railing(
                parts, terrace_plan(end, 0.045), terrace_plan(end, depth), level, trim
            )
        supports.append(base_plan)
    return agate.output(parts, row, roof, wall, supports, gates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "sunset_drive_pair_site", build
    )


if __name__ == "__main__":
    main()
