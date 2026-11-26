# SPDX-License-Identifier: Apache-2.0
"""Export verified shapes around southern Fairmount, Summit and Hamble."""

import argparse
from importlib import import_module
from pathlib import Path

from shapely.geometry import LineString, Polygon, box
from shapely.geometry.polygon import orient


hill = import_module("build-fairmount-moss-slope-review")
agate, emerald, columbia = hill.agate, hill.emerald, hill.columbia
fairmount, garden, geometry = emerald.fairmount, emerald.garden, emerald.geometry
base, potter, chapter = emerald.base, emerald.potter, emerald.chapter
northwest = emerald.northwest
PACKAGE = "fairmount-summit-hamble-review"
GROUND = "fairmount-summit-hamble-approaches"
BRICK = (154, 96, 74)
MORTAR = (188, 150, 119)


def entrance(paving, row, field, face, at, bearing, floor, distance, run, width):
    dimensions = {
        "gate": "fairmount-front-porch",
        "threshold_z_m": floor,
        "distance_m": distance,
        "stair_run_m": run,
        "width_m": width,
    }
    return emerald.frontages.estimated_entry(
        paving,
        {
            **row,
            "entry": {**dimensions, "bearing": bearing},
            "entry_finish": "theta-brick",
        },
        field,
        face,
        face.interpolate(at),
    )


def post(parts, field, plan, at, d, top, width, color):
    footprint = orient(
        fairmount.rectangle(plan, at - width, at + width, d - width, d + width)
    )
    low = emerald.grade(field, plan(at, d))
    base.flat(parts, footprint, low - 0.10, top, color)
    return footprint


def craftsman(row, field, paving):
    roof, wall = columbia.shell(row)
    spec = row["craftsman"]
    floor = spec["threshold"]
    parts = []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    emerald.facades(parts, paving, {**row, "frontages": [spec]}, wall, field, height)
    face, _, add, _, plan, at = hill.at_face(parts, wall, row, spec)
    trim = row["trim_color"]
    potter.door(add, at, floor, (136, 90, 64))
    for u in (at - 0.98, at + 0.98):
        northwest.window_grid(add, u, 0.47, floor + 0.37, floor + 1.79, 1, 2, trim)
    add(at - 1.46, at + 1.46, -0.025, 1.42, floor - 0.35, floor, BRICK)
    chapter.gabled_canopy(
        parts, plan, at, 1.69, -0.19, 1.66, 25.47, 1.05, row["roof_color"], trim
    )
    add(at - 1.52, at + 1.52, 1.40, 1.55, 25.20, 25.44, trim)
    columns = [
        post(parts, field, plan, u, 1.32, 25.43, 0.12, trim)
        for u in (at - 1.28, at + 1.28)
    ]
    for u in (at - 1.28, at + 1.28):
        add(u - 0.18, u + 0.18, 1.13, 1.53, floor - 0.43, floor + 0.17, BRICK)
    for u, v in ((at - 1.16, at - 0.80), (at + 0.80, at + 1.16)):
        columbia.railing(parts, plan(u, 1.32), plan(v, 1.32), floor, trim, 0.15, 0.72)
    for dormer in row["dormer_set"]:
        _, _, edge_add, _, edge_plan, station = hill.at_face(parts, wall, row, dormer)
        emerald.dormer(
            parts,
            edge_add,
            row,
            edge_plan,
            station,
            dormer["width"],
            dormer["low"],
            1.28,
            dormer["rise"],
        )
    x, n, w, d, rise, brick = row["chimney"]
    z = height((x, n))
    base.flat(
        parts,
        orient(box(x - w / 2, n - d / 2, x + w / 2, n + d / 2)),
        z - 0.59,
        z + rise,
        brick,
    )
    base.flat(
        parts,
        orient(
            box(x - w / 2 - 0.06, n - d / 2 - 0.06, x + w / 2 + 0.06, n + d / 2 + 0.06)
        ),
        z + rise,
        z + rise + 0.14,
        MORTAR,
    )
    approaches = [
        entrance(paving, row, field, face, at, spec["bearing"], floor, 6.8, 2.34, 1.43)
    ]
    return agate.output(parts, row, roof, wall, columns, approaches)


def terrace_wall(parts, field, coordinates, rise):
    path = LineString(coordinates)
    footprint = orient(path.buffer(0.145, cap_style="flat", join_style="round"))

    def top(e, n):
        return emerald.grade(field, (e, n)) + rise

    bottom = min(top(e, n) for e, n in footprint.exterior.coords) - rise - 0.12
    parts.append(geometry.shell(footprint, bottom, top, BRICK, MORTAR))
    return footprint


def terrace_lawn(paving, field, coordinates, rise, depth):
    back = [(e, n - depth) for e, n in reversed(coordinates)]
    footprint = orient(Polygon([*coordinates, *back]))

    def surface(e, n):
        return emerald.grade(field, (e, n)) + rise - 0.055

    bottom = min(surface(e, n) for e, n in footprint.exterior.coords) - rise - 0.07
    lawn = (133, 149, 112)
    paving.append(geometry.shell(footprint, bottom, surface, lawn, lawn))


def renovated(row, field, paving):
    roof, shell = columbia.shell(row)
    west, south, east, north = row["foyer"]
    wall = orient(shell.difference(box(west, south, east, north)))
    parts = []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    entries = [
        {
            "near": [582.08, -975.86],
            "bearing": 0,
            "minimum": 8.5,
            "windows": [
                [-3.0, 1.63, 26.82, 28.51],
                [0.0, 1.96, 26.70, 28.54],
                [3.04, 1.60, 26.83, 28.48],
            ],
        },
        {"near": [589.67, south], "bearing": 0, "minimum": 3.8},
    ]
    emerald.facades(parts, paving, {**row, "frontages": entries}, wall, field, height)
    face, _, add, _, plan, at = hill.at_face(parts, wall, row, entries[1])
    floor = 26.02
    trim = row["trim_color"]
    potter.door(add, at, floor, (65, 74, 69))
    for u in (at - 1.14, at + 1.14):
        northwest.window_grid(add, u, 0.81, floor + 0.38, floor + 1.93, 2, 2, trim)
    add(at - 2.05, at + 2.05, -0.04, 2.72, floor - 0.22, floor, BRICK)
    add(at - 2.11, at + 2.10, 0.08, 2.24, 28.80, 28.98, trim)
    # Two posts frame the visible span while the entrance passage stays clear.
    columns = [
        post(parts, field, plan, u, 1.96, 28.85, 0.10, (90, 99, 96))
        for u in (at - 1.78, at + 1.68)
    ]
    for i, points in enumerate(row["brick_terraces"]):
        rise = 0.56 if i < 2 else 0.61
        columns.append(terrace_wall(parts, field, points, rise))
        terrace_lawn(paving, field, points, rise, 1.32 if i < 2 else 1.72)
    path = entrance(
        paving,
        {**row, "street_steps_m": [6.26, 8.41]},
        field,
        face,
        at,
        0,
        floor,
        10.7,
        4.22,
        1.46,
    )
    emerald.terrain_apron(paving, field, *row["terrain_apron"])
    return agate.output(parts, row, roof, wall, columns, [path])


def build(row, field, paving):
    if "craftsman" in row:
        return craftsman(row, field, paving)
    if "foyer" in row:
        return renovated(row, field, paving)
    return emerald.build(row, field, paving)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "fairmount_summit_hamble_site", build
    )


if __name__ == "__main__":
    main()
