# SPDX-License-Identifier: Apache-2.0
"""Export the two-wing courtyard apartment exterior at 1340 East 19th Avenue."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
northwest = import_module("build-northwest-infill-exterior-review")
base, garden, geometry = fairmount.base, fairmount.garden, fairmount.geometry
PACKAGE = "east-nineteenth-court-exterior-review"
GROUND = "east-nineteenth-court-approach"
CONCRETE = (154, 153, 143)
WALK = (176, 175, 164)
CLAPBOARD = (103, 131, 146)
SHADOW = (86, 112, 127)
STONE = (117, 108, 91)
LAWN = (135, 151, 93)


def windows_and_doors(parts, row, wall, floor, roof_at):
    trim = row["trim_color"]
    deck = floor + row["gallery_rise_m"]
    for line, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 2:
            continue
        x, y = plan(span / 2, 0)
        street = normal[1] > 0.94 and y > -749
        court = (normal[0] > 0.94 and x < -131) or (normal[1] > 0.94 and y < -752)
        head = min(roof_at(plan(u, 0)) for u in (0.1, span - 0.1))
        if street:
            for z in np.arange(deck + 0.12, head - 0.22, 0.17):
                add(0.025, span - 0.025, 0.016, 0.029, z, z + 0.022, SHADOW)
            for u in np.arange(0.22, span - 0.08, 0.25):
                add(u, u + 0.016, 0.012, 0.026, floor + 0.04, deck, SHADOW)
            for level in (floor, deck):
                northwest.window_grid(
                    add, span * 0.27, 2.12, level + 1.03, level + 2.29, 2, 1, trim
                )
                northwest.window_grid(
                    add, span * 0.77, 1.34, level + 1.3, level + 2.22, 2, 1, trim
                )
            door = line.project(Point(row["street_entry_enu_m"]))
            fairmount.millrace.door(add, door, floor, trim)
            continue
        sections = max(1, round(span / (4.65 if court else 4.25)))
        for center in (span * (i + 0.5) / sections for i in range(sections)):
            for level in (floor, deck):
                if level + 2.3 > head - 0.18:
                    continue
                if court:
                    fairmount.millrace.door(add, center - 0.82, level, trim)
                northwest.window_grid(
                    add,
                    center + (0.66 if court else 0),
                    min(span * 0.49, 1.51),
                    level + 1.08,
                    level + 2.16,
                    2,
                    1,
                    trim,
                )


def gallery(parts, row, floor, roof_at):
    trim = row["trim_color"]
    deck = floor + row["gallery_rise_m"]
    for bounds in row["gallery_bounds_m"]:
        base.flat(parts, orient(box(*bounds)), deck - 0.19, deck, trim, WALK)
    for a, b in row["gallery_rail_lines_m"]:
        fairmount.balustrade(parts, a, b, deck, trim)
        for xy in np.linspace(
            a, b, max(2, round(np.linalg.norm(np.subtract(a, b)) / 3.7))
        ):
            top = roof_at(xy) - 0.15
            fairmount.beam(parts, (*xy, deck - 0.04), (*xy, top), 0.085, trim)
    columns = []
    for x, y in row["gallery_columns_m"]:
        fairmount.beam(parts, (x, y, floor - 0.03), (x, y, deck), 0.095, trim)
        columns.append(orient(box(x - 0.052, y - 0.052, x + 0.052, y + 0.052)))
    return deck, columns


def courtyard_stair(parts, row, floor, deck):
    x0, y0, x1, y1 = row["courtyard_stair_bounds_m"]
    rise = (deck - floor) / 14
    steps = np.linspace(y0, y1, 15)
    for i, (a, b) in enumerate(zip(steps[:-1], steps[1:]), 1):
        top = floor + i * rise
        base.flat(parts, orient(box(x0, a - 0.036, x1, b)), top - 0.085, top, WALK)
    for x in (x0 + 0.025, x1 - 0.025):
        a, b = np.array([x, y0, floor]), np.array([x, y1, deck])
        fairmount.beam(
            parts, a - (0, 0, 0.11), b - (0, 0, 0.11), 0.19, row["trim_color"]
        )
        fairmount.beam(
            parts, a + (0, 0, 0.82), b + (0, 0, 0.82), 0.064, row["trim_color"]
        )
        for xy in np.linspace(a, b, 12):
            fairmount.beam(parts, xy, xy + (0, 0, 0.82), 0.042, row["trim_color"])
    return orient(box(x0, y0, x1, y1))


def north_entry(paving, row, floor, field):
    x, y = row["street_entry_enu_m"]
    start = geometry.sample_ground(field, x, y + 3.13)
    points = np.linspace(y + 3.13, y + 1.42, 6)
    for i, (a, b) in enumerate(zip(points[:-1], points[1:]), 1):
        level = start + i * (floor - start) / 5
        base.flat(
            paving, orient(box(x - 0.66, b, x + 0.66, a)), start - 0.19, level, CONCRETE
        )
    base.flat(
        paving,
        orient(box(x - 0.76, y - 0.14, x + 0.76, points[-1])),
        start - 0.21,
        floor,
        CONCRETE,
    )
    for a, b in ((x - 3.8, x - 0.72), (x + 0.72, x + 3.65)):
        base.flat(
            paving,
            orient(box(a, y + 1.73, b, y + 2.04)),
            start - 0.23,
            floor - 0.08,
            STONE,
        )
    return {
        "gate": "north-street-approach",
        "position_enu_m": [x, y],
        "outward_degrees": 0,
        "threshold_z_m": floor,
        "width_m": 1.03,
        "approach_distance_m": 3.55,
        "estimated": True,
        "snap_to_facade": False,
    }


def courtyard(paving, row, field):
    west, south, east, north = row["courtyard_lawn_bounds_m"]
    level = row["level_z_m"] - 0.10
    apron = orient(box(west, south, east, north))
    base.flat(paving, apron, level - 0.9, level, STONE, LAWN)
    lower = geometry.sample_ground(field, east + 1.39, south + 0.72)
    stations = np.linspace(east + 1.39, east, 5)
    for step, (inner, outer) in enumerate(zip(stations[1:], stations[:-1]), 1):
        top = lower + step * (level - lower) / 4
        footprint = orient(box(inner, south + 0.10, outer, south + 1.36))
        base.flat(paving, footprint, lower - 0.13, top, CONCRETE)
    face = orient(box(east - 0.14, south + 1.36, east + 0.035, north))
    base.flat(paving, face, lower - 0.24, level + 0.03, CONCRETE)
    return face


def build(row, field, paving):
    outline = orient(Polygon(row["outline_enu_m"]))
    inset = outline.buffer(-0.2, join_style="mitre")
    wall = orient(inset.difference(box(*row["gallery_recess_bounds_m"])))
    floor = row["level_z_m"]
    foundation = geometry.shell(
        wall, floor - 1.2, lambda *_: floor + 0.045, CONCRETE, CONCRETE
    )
    parts = [foundation]
    roof_at = garden.roof_sections(parts, outline, wall, floor, row, grid=0.0002)
    windows_and_doors(parts, row, wall, floor, roof_at)
    deck, columns = gallery(parts, row, floor, roof_at)
    stair = courtyard_stair(parts, row, floor, deck)
    gate = north_entry(paving, row, floor, field)
    retaining_wall = courtyard(paving, row, field)
    supports = [stair, retaining_wall, *columns]
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{k: row[k] for k in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(wall)],
        "support_collision_enu_m": [base.ring(shape) for shape in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": floor,
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [gate],
    }
    return mesh, record, wall, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "east_nineteenth_court_site", build
    )


if __name__ == "__main__":
    main()
