# SPDX-License-Identifier: Apache-2.0
"""Rebuild five registered neighborhood exteriors and the former Patterson YMCA ground."""

import argparse
from importlib import import_module
from math import ceil
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

precedent = import_module("build-franklin-riverfront-closeout-review")
frontage = import_module("build-onyx-university-frontages-review")
fairmount = precedent.fairmount
garden, base = fairmount.garden, fairmount.base
chapter, millrace = fairmount.chapter, fairmount.millrace
grade, mass, ground = precedent.grade, precedent.mass, precedent.grade_surface
PACKAGE = "neighborhood-exterior-closeout-review"
GROUND = "neighborhood-exterior-ground"
CEMENT = (158, 154, 136)
WOOD = (125, 101, 84)
VERTICAL_WOOD = (115, 88, 71)
WHITE = (217, 214, 194)
DARK = (74, 79, 74)
GLASS = (80, 104, 109)
GREEN_METAL = (78, 103, 102)
STATION_GLYPHS = {
    **frontage.GLYPHS,
    "A": (((0, 0), (0.5, 1), (1, 0)), ((0.21, 0.42), (0.79, 0.42))),
    "V": (((0, 1), (0.5, 0), (1, 1)),),
}


def rail(parts, a, b, color):
    a, b = np.asarray(a), np.asarray(b)
    for height in (0.08, 0.90):
        fairmount.beam(parts, a + [0, 0, height], b + [0, 0, height], 0.025, color)
    count = max(2, ceil(np.linalg.norm((b - a)[:2]) / 0.18))
    for point in np.linspace(a, b, count):
        fairmount.beam(parts, point + [0, 0, 0.07], point + [0, 0, 0.90], 0.016, color)


def exterior_stairs(
    parts, plan, low_u, high_u, inner, outer, low_z, high_z, tread, trim
):
    """Build a flight along a wall, with open risers and rails."""
    count = ceil((high_z - low_z) / 0.185)
    step = (high_u - low_u) / count
    rise = (high_z - low_z) / count
    for index in range(count):
        u = low_u + step * index
        lo, hi = sorted((u, u + step * 1.13))
        z = low_z + (index + 1) * rise
        patch = fairmount.rectangle(plan, lo, hi, inner, outer)
        base.flat(parts, patch, z - 0.09, z, tread)
    for side in (inner + 0.055, outer - 0.045):
        first, last = (*plan(low_u, side), low_z), (*plan(high_u, side), high_z)
        fairmount.beam(parts, first, last, 0.067, trim)
        rail(parts, first, last, trim)


def gallery(parts, plan, start, stop, inner, outer, level, field, colors):
    tread, trim = colors
    mass(
        parts,
        fairmount.rectangle(plan, start, stop, inner, outer),
        level - 0.19,
        level,
        tread,
    )
    for u in (start + 0.11, stop - 0.13):
        post = fairmount.rectangle(
            plan, u - 0.073, u + 0.073, outer - 0.22, outer - 0.074
        )
        mass(
            parts,
            post,
            grade(field, post.centroid.coords[0]) - 0.08,
            level - 0.16,
            trim,
        )
    rail(
        parts,
        (*plan(start, outer - 0.04), level),
        (*plan(stop, outer - 0.04), level),
        trim,
    )


def window(add, span, u, width, bottom, height, top, trim, ribs=2):
    if min(u, span - u) > width / 2 + 0.05 and bottom + height < top - 0.10:
        millrace.window(add, u, width, bottom, height, trim, ribs=ribs)


def siding(add, span, level, top, row, partition=False):
    if top > level + 0.12:
        millrace.siding(
            add, span, top - 0.11, level, np.asarray(row["wall_color"]) * 0.92, 0.23
        )
    if partition and top > level + 2.55:
        add(
            0.028,
            span - 0.028,
            0.025,
            0.087,
            level + 2.46,
            level + 2.58,
            row["trim_color"],
        )


def chapter_house(parts, paving, row, wall, field, roof_at):
    spec = row["entry"]
    entry_row = {
        **row,
        "front": {"bearing": spec["bearing"]},
        "entry": {
            "near": spec["near"],
            "gate": "street-entry",
            "approach_m": spec["distance"],
            "rise_m": spec["rise"],
        },
        "porch": {"style": "porch", "half_width": 1.27, "depth": 1.54, "rise": 1.06},
    }
    gate, door_edge, point, supports = fairmount.entrance(
        parts, entry_row, wall, field, paving
    )
    trim = row["trim_color"]
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.5:
            continue
        z = grade(field, plan(span / 2, 0))
        top = min(roof_at(plan(u, 0)) for u in np.linspace(0.1, span - 0.1, 7))
        siding(add, span, z + 0.32, top, row, partition=True)
        add(0.026, span - 0.026, 0.008, 0.072, z - 0.15, z + 0.39, CEMENT)
        main = normal[0] > 0.94 and span > 15
        door = edge.project(point) if edge.equals(door_edge) else -10
        low = (
            (0.12, 0.22, 0.33, 0.76, 0.88)
            if main
            else np.linspace(0.22, 0.78, max(1, round(span / 2.65)))
        )
        for f in low:
            u = span * f
            if abs(u - door) > 1.58:
                window(add, span, u, 1.35, z + 0.94, 1.41, top, trim, 2)
        if main:
            add(0.035, span - 0.035, 0.045, 0.31, z + 3.12, z + 3.31, WOOD)
        for u in np.linspace(span * 0.10, span * 0.90, max(1, round(span / 2.25))):
            window(add, span, u, 1.46 if main else 1.12, z + 3.85, 1.27, top, trim, 2)
            if main:
                add(u - 0.048, u + 0.048, 0.039, 0.25, top - 0.58, top - 0.17, trim)
        if main:
            for a, b in ((door - 4.9, door - 1.32), (door + 1.28, door + 4.1)):
                bed = fairmount.rectangle(plan, a, b, 0.16, 0.97)
                ground(paving, field, bed, (125, 116, 94))
            for f, width in ((0.23, 3.72), (0.72, 2.75)):
                u = span * f
                cross = z + 6.86
                local_height = roof_at(plan(u, 0))
                if cross + 0.48 < local_height:
                    add(
                        u - width / 2,
                        u + width / 2,
                        0.018,
                        0.081,
                        cross - 0.21,
                        cross + 0.58,
                        trim,
                    )
                    millrace.window(
                        add, u, width - 0.35, cross - 0.09, 0.52, trim, ribs=3
                    )
                    chapter.gabled_canopy(
                        parts,
                        plan,
                        u,
                        width / 2 + 0.14,
                        -0.38,
                        0.21,
                        cross + 0.61,
                        0.52,
                        row["roof_color"],
                        trim,
                    )
    return [gate], supports


def vehicle_door(add, center, width, z, head):
    a, b = center - width / 2, center + width / 2
    add(a - 0.11, b + 0.11, 0.008, 0.085, z - 0.04, head + 0.12, CEMENT)
    add(a, b, 0.086, 0.111, z + 0.025, head, WHITE)
    for y in np.arange(z + 0.20, head - 0.14, 0.17):
        add(a + 0.01, b - 0.01, 0.112, 0.122, y, y + 0.015, (170, 168, 151))
    for left, right in zip(
        np.linspace(a + 0.16, b - 0.16, 5)[:-1], np.linspace(a + 0.16, b - 0.16, 5)[1:]
    ):
        add(
            left + 0.03,
            right - 0.036,
            0.125,
            0.139,
            z + 1.25,
            min(z + 2.16, head - 0.28),
            GLASS,
        )
        add(left + 0.03, right - 0.036, 0.140, 0.153, z + 1.67, z + 1.71, WHITE)


def station_inscription(parts, plan, center, level):
    title = "UNIVERSITY STATION"
    for index, letter in enumerate(title):
        at = center + (index - (len(title) - 1) / 2) * 0.34
        for stroke in STATION_GLYPHS.get(letter, ()):
            points = [
                (*plan(at + x * 0.21, 0.244), level + y * 0.27) for x, y in stroke
            ]
            for a, b in zip(points, points[1:]):
                fairmount.beam(parts, a, b, 0.030, (193, 192, 174))


def station(parts, paving, row, wall, field, roof_at):
    trim = row["trim_color"]
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 2.0:
            continue
        z = grade(field, plan(span / 2, 0))
        top = min(roof_at(plan(u, 0)) for u in np.linspace(0.12, span - 0.12, 6))
        main = normal[0] < -0.96 and edge.centroid.x < 111.2 and span > 9
        office = normal[0] < -0.96 and edge.centroid.x < 107.2 and span > 5
        for y in np.arange(z + 0.10, top - 0.23, 0.14):
            add(0.023, span - 0.023, 0.002, 0.022, y, y + 0.012, (135, 94, 77))
        if main or office:
            fascia = 0.91 if main else 0.38
            add(0.02, span - 0.02, 0.022, 0.21, top - fascia, top - 0.04, GREEN_METAL)
            for u in np.arange(0.10, span - 0.10, 0.24):
                add(
                    u,
                    u + 0.014,
                    0.208,
                    0.23,
                    top - fascia + 0.035,
                    top - 0.079,
                    (65, 93, 92),
                )
        if main:
            station_inscription(parts, plan, span * 0.49, top - 0.56)
            for f in (0.28, 0.68):
                vehicle_door(
                    add, span * f, min(3.62, span * 0.32), z + 0.045, top - 1.02
                )
            apron = fairmount.rectangle(plan, 0.14, span - 0.09, 0.03, 11.0)
            ground(paving, field, apron, (166, 162, 145))
            for f in (0.14, 0.49, 0.86):
                line = fairmount.rectangle(
                    plan, span * f, span * f + 0.027, 0.12, 10.94
                )
                ground(paving, field, line, (140, 140, 125), 0.099)
        elif office:
            millrace.door(add, span * 0.26, z + 0.13, (92, 116, 109))
        elif normal[0] > 0.93:
            add(0.03, span - 0.03, 0.01, 0.095, z + 0.12, top - 0.22, (174, 176, 155))
            for u in np.linspace(span * 0.22, span * 0.77, max(1, round(span / 4.1))):
                window(add, span, u, 1.15, z + 1.02, 0.91, top, trim)
        elif normal[1] < -0.95:
            for u in np.linspace(span * 0.19, span * 0.81, max(1, round(span / 2.65))):
                window(add, span, u, 1.03, z + 1.15, 1.03, top, trim)

    # The East 17th fence follows the visible line in front of the low extension.
    a, b = np.asarray([117.6, -478.95]), np.asarray([135.8, -478.90])
    for start, stop in zip(np.linspace(a, b, 8)[:-1], np.linspace(a, b, 8)[1:]):
        z = grade(field, (start + stop) / 2)
        patch = Polygon([start, stop, stop + [0, 0.12], start + [0, 0.12]])
        mass(parts, patch, z - 0.09, z + 0.38, (145, 92, 74))
        mass(
            parts,
            patch.buffer(-0.018, join_style="mitre"),
            z + 0.38,
            z + 1.48,
            (163, 169, 161),
        )
        post = Polygon(
            [
                start + [dx, dy]
                for dx, dy in (
                    (-0.061, -0.024),
                    (0.061, -0.024),
                    (0.061, 0.142),
                    (-0.061, 0.142),
                )
            ]
        )
        mass(parts, post, z + 0.36, z + 1.55, WHITE)
    return [], []


def duplex(parts, paving, row, wall, field, roof_at):
    trim = row["trim_color"]
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.8:
            continue
        z = grade(field, plan(span / 2, 0))
        top = min(roof_at(plan(u, 0)) for u in np.linspace(0.12, span - 0.12, 7))
        siding(add, span, z + 0.28, top, row)
        if normal[1] > 0.95 and edge.centroid.x > 888 and span > 9:
            level = z + 2.85
            gallery(
                parts, plan, 0.49, span - 2.21, 0.02, 1.24, level, field, (WOOD, trim)
            )
            exterior_stairs(
                parts,
                plan,
                span - 0.35,
                span - 3.83,
                1.28,
                2.40,
                grade(field, plan(span - 0.35, 2.0)),
                level,
                WOOD,
                DARK,
            )
            for f in (0.19, 0.46):
                vehicle_door(add, span * f, 2.28, z + 0.04, z + 2.08)
            for f in (0.19, 0.43, 0.64):
                window(add, span, span * f, 1.16, level + 0.68, 1.26, top, trim)
            for f in (0.30, 0.68):
                millrace.door(add, span * f, level + 0.02, trim)
            ground(
                paving,
                field,
                fairmount.rectangle(plan, 0.20, span - 0.11, 0.1, 5.25),
                (138, 141, 127),
            )
        elif normal[1] > 0.95 and span > 4.3:
            level = z + 0.30
            gallery(
                parts,
                plan,
                span * 0.15,
                span * 0.79,
                0.02,
                0.93,
                level,
                field,
                (WOOD, trim),
            )
            millrace.door(add, span * 0.56, level + 0.01, trim)
            window(add, span, span * 0.22, 1.2, level + 0.82, 0.95, top, trim)
        else:
            for u in np.linspace(span * 0.23, span * 0.77, max(1, round(span / 3.4))):
                window(add, span, u, 1.09, z + 0.79, 1.12, top, trim)
                window(add, span, u, 1.07, z + 3.44, 1.14, top, trim)
    return [], []


def hillside_house(parts, paving, row, wall, field, roof_at):
    trim = row["trim_color"]
    fairmount_style = row["kind"] == "fairmount-house"
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.55:
            continue
        z = grade(field, plan(span / 2, 0))
        top = min(roof_at(plan(u, 0)) for u in np.linspace(0.13, span - 0.13, 8))
        siding(add, span, z + 0.38, top, row, partition=not fairmount_style)
        add(0.016, span - 0.016, 0.008, 0.047, z - 0.28, z + 0.36, CEMENT)
        front = (
            normal[0] < -0.95
            if fairmount_style
            else normal[1] > 0.30 or normal[0] < -0.55
        )
        center = span * 0.5
        if (
            fairmount_style
            and front
            and edge.centroid.y < -349
            and edge.centroid.y > -354
        ):
            entry = z + 0.55
            millrace.door(add, center, entry, trim)
            fairmount.landing(parts, plan, center, row, entry, z)
            ground(
                paving,
                field,
                fairmount.rectangle(plan, center - 0.60, center + 0.60, 0.18, 4.8),
                CEMENT,
            )
            window(
                add,
                span,
                center,
                min(2.14, span * 0.54),
                z + 3.85,
                1.10,
                roof_at(plan(center, 0)),
                trim,
            )
            add(
                center - 1.19,
                center + 1.19,
                0.012,
                0.086,
                z + 3.62,
                z + 3.75,
                VERTICAL_WOOD,
            )
            continue
        for u in np.linspace(
            span * 0.23, span * 0.77, max(1, min(5, round(span / 3.15)))
        ):
            grade_at = grade(field, plan(u, 0))
            low = z + 1.07 if fairmount_style else 33.20
            if low > grade_at + 0.21:
                window(add, span, u, min(1.24, span * 0.40), low, 1.14, top, trim)
            upper = z + 3.21 if fairmount_style else 35.77
            at_top = roof_at(plan(u, 0))
            if (
                not fairmount_style
                and front
                and min(u, span - u) > 1.04
                and upper + 1.30 < at_top
            ):
                add(
                    u - 0.84,
                    u - 0.57,
                    0.035,
                    0.062,
                    upper - 0.015,
                    upper + 1.28,
                    (141, 83, 76),
                )
                add(
                    u + 0.57,
                    u + 0.84,
                    0.035,
                    0.062,
                    upper - 0.015,
                    upper + 1.28,
                    (141, 83, 76),
                )
            if upper > grade_at + 0.21:
                window(
                    add, span, u, min(1.22, span * 0.40), upper, 1.17, at_top, trim, 2
                )
    return [], []


def former_ymca(paving, field, site):
    materials = {
        "cleared_ground": (143, 144, 112),
        "remaining_concrete": (167, 160, 138),
        "remaining_asphalt": (133, 134, 115),
    }
    for key, color in materials.items():
        region = Polygon(site["geometry"][key]["outline_enu_m"])
        ground(paving, field, region, color)


def build_model(row, field, paving):
    outline = orient(Polygon(row["outline_enu_m"]))
    wall = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
    floor, _ = garden.science.earlier.fit_base(field, wall)
    parts = []
    roof_at = garden.roof_sections(parts, outline, wall, floor, row, grid=0.0002)
    facade = {
        "chapter": chapter_house,
        "station": station,
        "birch-duplex": duplex,
        "fairmount-house": hillside_house,
        "hill-house": hillside_house,
    }[row["kind"]]
    gates, supports = facade(parts, paving, row, wall, field, roof_at)
    return precedent.record(parts, row, outline, wall, supports, gates, floor)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = precedent.read(fairmount.ROOT / f"data/metadata/{PACKAGE}.json")

    def build(row, field, paving):
        if row["id"] == spec["models"][0]["id"]:
            former_ymca(paving, field, spec["former_ymca"])
        return build_model(row, field, paving)

    fairmount.export_review(
        args,
        PACKAGE,
        GROUND,
        "neighborhood_exterior_closeout_site",
        build,
        source_removals=precedent.certify,
    )


if __name__ == "__main__":
    main()
