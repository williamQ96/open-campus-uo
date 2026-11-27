# SPDX-License-Identifier: Apache-2.0
"""Export registered exteriors for the southwest campus blocks."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

hilyard = import_module("build-hilyard-blocks-review")
older = hilyard.older
agate, base, fairmount, garden, geometry = (
    hilyard.agate,
    hilyard.base,
    hilyard.fairmount,
    hilyard.garden,
    hilyard.geometry,
)
PACKAGE = "southwest-exterior-review"
PAVING = "southwest-exterior-paving"
LIME = (198, 199, 180)
STONE = (166, 158, 143)
BROWN = (137, 124, 106)
GRAY = (116, 132, 129)
BLUE = (71, 98, 130)
DARK = (76, 89, 88)
GREEN = (107, 140, 119)
PINK = (166, 112, 99)


def paving_slab(parts, area, field, color):
    def top(e, n):
        return hilyard.grade(field, (e, n)) + 0.045

    low = min(top(*p) for p in area.exterior.coords) - 0.13
    parts.append(geometry.shell(orient(area), low, top, color, color))


def pattern_facade(parts, row, poly, field, height, *, raised=None):
    style = row["treatment"]
    levels = row["levels_z_m"]
    for edge, (span, add, normal, plan, point, panel) in fairmount.views(parts, poly):
        if span < 0.86:
            continue
        if style in ("stores", "blue-screen", "green-entrance", "alley-panels"):
            direction = np.asarray(hilyard.DIRECTION[row["front_side"]])
            if direction @ normal > 0.90 or style == "stores" and normal[0] > 0.90:
                continue
        x = plan(span / 2, 0)
        floor = hilyard.grade(field, x)
        n = max(1, round(span / (3.45 if style in ("alder-court", "heron") else 2.85)))
        width = span / n
        for j in range(n):
            left, right = j * width + 0.035, (j + 1) * width - 0.035
            middle = (left + right) / 2
            p = plan(middle, 0)
            z = hilyard.grade(field, p)
            ceiling = min(height(plan(v, 0)) for v in (left, middle, right)) - 0.18
            opening = raised is not None and raised[0].covers(Point(p))
            if opening:
                z = max(z, raised[1] - 0.045)
            if ceiling <= z + 0.73 or right - left < 0.61:
                continue
            trim = row["trim_color"]
            tones = {
                "alder-court": (row["wall_color"], (155, 168, 173), (173, 182, 179)),
                "heron": ((187, 186, 169), (163, 171, 162), (199, 193, 174)),
                "urban-bays": ((111, 127, 128), (186, 185, 164), (96, 115, 120)),
                "linked-wings": ((149, 149, 131), (154, 151, 128), (137, 142, 124)),
            }.get(style, (row["wall_color"],))
            color = tones[j % len(tones)]
            if style == "blue-panels":
                color = LIME if j % 3 else BLUE
            safe_add = hilyard.elevate(add, 0.027)
            if style in ("blue-panels", "heron") and not opening:
                dado = min(ceiling - 0.21, levels[0] + 1.74)
                if dado > z + 0.23:
                    add(left, right, 0.003, 0.042, z - 0.12, dado, STONE)
                    for y in np.arange(z + 0.10, dado - 0.13, 0.16):
                        add(left, right, 0.041, 0.054, y, y + 0.013, (147, 142, 128))
            if style in (
                "alder-court",
                "heron",
                "urban-bays",
                "linked-wings",
                "blue-panels",
            ):
                base_level = (
                    levels[0] + 1.74 if style in ("blue-panels", "heron") else z + 0.12
                )
                bottom = max(z + 0.12, base_level)
                if ceiling > bottom + 0.28:
                    add(left, right, 0.003, 0.028, bottom, ceiling, color)
            if (
                style == "linked-wings"
                or style == "urban-bays"
                and (abs(normal[0]) > 0.88)
            ):
                shade = LIME if style == "linked-wings" else (78, 98, 109)
                add(left - 0.022, left + 0.097, 0.024, 0.13, z + 0.018, ceiling, shade)
            if style == "alder-court":
                for y in np.arange(z + 0.29, ceiling - 0.1, 0.204):
                    add(left, right, 0.025, 0.039, y, y + 0.012, (142, 154, 155))
            for y in levels:
                sill = y + 0.62
                head = min(sill + 1.33, ceiling - 0.18)
                if sill <= z + 0.36 or head - sill < 0.48:
                    continue
                span_window = min(1.77, width * 0.61)
                if style == "urban-bays" and abs(normal[0]) > 0.87 and j % 3 in (0, 1):
                    inset = right - left
                    add(
                        middle - inset * 0.44,
                        middle + inset * 0.44,
                        0.029,
                        0.072,
                        sill - 0.41,
                        head + 0.29,
                        (88, 110, 121),
                    )
                    hilyard.older.framed(
                        hilyard.elevate(add, 0.071),
                        middle,
                        span_window,
                        sill,
                        head,
                        2,
                        LIME,
                    )
                else:
                    older.framed(safe_add, middle, span_window, sill, head, 2, trim)
                if (
                    style == "heron"
                    and normal[0] > 0.92
                    and y >= levels[2]
                    and j % 3 == 1
                ):
                    hilyard.balcony(
                        parts,
                        add,
                        plan,
                        left + 0.08,
                        right - 0.07,
                        y - 0.08,
                        0.76,
                        trim,
                    )
        if style == "urban-bays" and floor < levels[0] + 0.16:
            add(
                0.015,
                span - 0.015,
                0.005,
                0.045,
                floor - 0.104,
                levels[0] + 0.14,
                (112, 99, 82),
            )


def slope_gables(parts, row, wall, field, world, height):
    for side, stations in row["projecting_bays"].items():
        for station in stations:
            target = (-14.9, station) if side == "W" else (station, -22.35)
            edge, view = hilyard.face_on(parts, wall, world, side, target)
            span, add, _, plan, point, panel = view
            u = edge.project(Point(world(*target)))
            half = min(1.32, u - 0.07, span - u - 0.07)
            if half < 0.63:
                continue
            lo, hi = u - half, u + half
            threshold = max(
                row["levels_z_m"][0], hilyard.grade(field, plan(u, 0)) + 0.11
            )
            bottom = max(threshold + 2.02, 7.35)
            top = min(
                height(plan(u, 0)) - 0.34, 12.05 if round(abs(station)) % 2 else 12.62
            )
            if top < bottom + 2.10:
                continue
            peak = top + 0.86
            outline = orient(
                Polygon(((lo, bottom), (hi, bottom), (hi, top), (u, peak), (lo, top)))
            )
            panel(outline, 0.038, 0.69, (150, 165, 173))
            for t in np.arange(lo + 0.105, hi, 0.219):
                z = top + (1 - abs(u - t) / half) * 0.86
                add(t - 0.021, t + 0.021, 0.68, 0.705, bottom, z, (136, 150, 154))
            older.framed(
                hilyard.elevate(add, 0.702),
                u,
                1.28,
                bottom + 0.49,
                bottom + 1.74,
                2,
                LIME,
            )
            for a, b in (
                (point(lo, 0.76, top), point(u, 0.76, peak)),
                (point(u, 0.76, peak), point(hi, 0.76, top)),
            ):
                fairmount.beam(parts, a, b, 0.099, (98, 119, 124))
            hilyard.potter.door(add, u, threshold, (97, 111, 105))


def retail(parts, row, wall, world, field):
    style = row["treatment"]
    side = row["front_side"]
    targets = {
        "green-entrance": (13.49, 0),
        "blue-screen": (3.6, -14.54),
        "stores": (-0.04, -7.01),
        "alley-panels": (8.92, 0),
    }
    edge, (span, add, _, plan, point, panel) = hilyard.face_on(
        parts, wall, world, side, targets[style]
    )
    floor = hilyard.grade(field, plan(span * 0.52, 0)) + 0.075
    left, right = 0.08, span - 0.08
    if style == "green-entrance":
        for u in np.linspace(span * 0.20, span * 0.80, 3):
            shape = garden.chapter.arch(u, floor, 0.97, 2.77, 0.50)
            panel(orient(shape), 0.02, 0.073, GREEN)
        older.framed(add, span * 0.20, 0.71, floor + 1.65, floor + 2.36, 1, LIME)
        older.framed(add, span * 0.80, 0.71, floor + 1.65, floor + 2.36, 1, LIME)
        return
    if style == "blue-screen":
        panel_w = min(5.16, span * 0.57)
        middle = span * 0.54
        bottom, top = floor + 0.40, floor + 2.16
        add(left, right, 0.01, 0.065, floor - 0.095, top + 0.22, (82, 109, 148))
        shape = Polygon(
            (
                (middle - panel_w / 2, bottom),
                (middle + panel_w / 2, bottom),
                (middle + panel_w / 2, top),
                (middle - panel_w / 2, top),
            )
        )
        holes = [
            Point((x, z)).buffer(0.087, quad_segs=2)
            for z in np.linspace(bottom + 0.18, top - 0.16, 6)
            for x in np.linspace(middle - panel_w * 0.45, middle + panel_w * 0.45, 13)
        ]
        panel(
            orient(shape.difference(unary_union(holes))), 0.087, 0.211, (109, 142, 191)
        )
        add(left, right, 0.019, 0.15, top + 0.35, top + 0.72, (198, 191, 170))
        return
    if style == "stores":
        hilyard.glazed(
            add, left + 0.15, right - 0.15, floor + 0.57, floor + 2.10, (96, 105, 90)
        )
        for u in np.linspace(span * 0.20, span * 0.80, 2):
            hilyard.potter.door(add, u, floor, (108, 101, 81))
        add(left, right, 0.015, 0.64, floor + 2.16, floor + 2.49, (149, 128, 96))
        e, (length, rib, _, _, _, _) = hilyard.face_on(
            parts, wall, world, "E", (14.17, 5.34)
        )
        if length > 1.5:
            for u in np.arange(0.12, length - 0.07, 0.22):
                rib(u - 0.020, u + 0.021, 0.007, 0.071, floor + 0.18, 2.95, LIME)
        return
    for u in (span * 0.22, 0.54 * span, span * 0.82):
        add(
            u - 0.73,
            u + 0.73,
            0.006,
            0.067,
            floor - 0.06,
            floor + 5.44,
            (128, 163, 152),
        )
        for dz in (0.76, 3.82):
            older.framed(
                hilyard.elevate(add, 0.074),
                u,
                1.0,
                floor + dz,
                floor + dz + 1.01,
                2,
                LIME,
            )


def courtyard(parts, roof, wall, row, field, world, height):
    hole = orient(Polygon(roof.interiors[0]))
    paving_slab(parts, hole, field, (150, 147, 131))
    for ring in wall.interiors:
        for c, d in zip(ring.coords, list(ring.coords)[1:]):
            span, add, _, plan, _, _ = garden.chapter.setup_face(parts, c, d)
            if span < 1.45:
                continue
            for u in (
                (np.arange(round(span / 2.75)) + 0.5)
                * span
                / max(1, round(span / 2.75))
            ):
                for z in row["levels_z_m"]:
                    cap = min(z + 1.97, height(plan(u, 0)) - 0.36)
                    older.framed(add, u, min(1.29, span * 0.62), z + 0.68, cap, 2, LIME)
    # The photographed screen is an open masonry panel on the Alder side of
    # the entry recess. Its adjacent passage remains clear.
    edge, view = hilyard.face_on(parts, wall, world, "E", (12.70, -0.03))
    span, add, _, plan, _, panel = view
    center = span * 0.59
    y = hilyard.grade(field, plan(center, 0.30))
    left, right = center - 1.19, center + 1.19
    bottom, top = y + 0.06, y + 2.26
    outline = Polygon(((left, bottom), (right, bottom), (right, top), (left, top)))
    voids = [
        Point((u, z)).buffer(0.115, quad_segs=2)
        for u in np.linspace(left + 0.26, right - 0.26, 6)
        for z in np.linspace(bottom + 0.24, top - 0.21, 6)
    ]
    panel(orient(outline.difference(unary_union(voids))), 0.74, 0.83, PINK)
    add(left - 0.04, right + 0.04, 0.72, 0.87, bottom - 0.08, bottom + 0.097, PINK)
    return [orient(fairmount.rectangle(plan, left, right, 0.72, 0.87))]


def linked_wings(row, field, paving, roof, patch, world):
    west, east = row["split_slot"]
    parts, walls, supports = [], [], []
    wings = [
        (patch((-23, -12, west, 12)), 9.69, 4.43, (-19.10, -13.38, -7.22, -2.69)),
        (patch((east, -12, 23, 12)), 10.91, 5.16, (3.36, 8.21, 14.52, 19.68)),
    ]
    for window, cap, floor, posts in wings:
        outline = orient(roof.intersection(window))
        nominal = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
        limit = -10.60 + row["parking_depth"]
        opening = patch((-23, -12, 23, limit))
        wall = orient(nominal.difference(opening))
        wing = {
            **row,
            "raised_wall_enu_m": list(nominal.exterior.coords)[:-1],
            "raised_wall_bottom_z_m": floor,
            "levels_z_m": [floor + 0.02, floor + 2.72],
            "roof_zones": [
                {"bounds_m": [-23, -12, 23, 12], "planes": [[0, 0, cap, 0, 0]]}
            ],
        }
        height = garden.roof_sections(
            parts, outline, wall, row["base_z_m"], wing, grid=0.0002
        )
        pattern_facade(parts, wing, nominal, field, height, raised=(opening, floor))
        paving_slab(paving, outline.intersection(opening), field, (145, 145, 129))
        for x in posts:
            pier = patch((x - 0.14, -9.67, x + 0.14, -9.39))
            hilyard.pier(parts, field, pier, floor, LIME)
            supports.append(pier)
        walls.append(wall)
    for level, index in zip(row["link_levels"], range(2)):
        from_t = -7.82 + index * 0.20
        slab = patch((west - 0.11, from_t, east + 0.11, from_t + 0.93))
        base.flat(parts, slab, level - 0.16, level, LIME)
        for t in (from_t + 0.07, from_t + 0.85):
            a, b = world(west + 0.05, t), world(east - 0.05, t)
            older.columbia.railing(parts, a, b, level, GREEN, spacing=0.21, height=0.85)
    west_stair = world(west + 0.44, -10.25)
    first = world(east - 0.46, -7.30)
    second = world(west + 0.45, -6.88)
    low = hilyard.grade(field, west_stair) + 0.07
    hilyard.northwest.stair(
        parts, west_stair, first, low, row["link_levels"][0], 0.84, steps=12
    )
    hilyard.northwest.stair(
        parts,
        first,
        second,
        row["link_levels"][0],
        row["link_levels"][1],
        0.81,
        steps=15,
    )
    for s, t in ((west + 0.07, -8.77), (east - 0.06, -7.73)):
        pier = patch((s - 0.075, t - 0.075, s + 0.075, t + 0.075))
        hilyard.pier(parts, field, pier, row["link_levels"][0] - 0.17, GREEN)
        supports.append(pier)
    mesh, record, _, _ = agate.output(parts, row, roof, walls[0], supports, [])
    record["ground_footprints_enu_m"] = [base.ring(wall) for wall in walls]
    return mesh, record, unary_union(walls), supports


def heron_entry(parts, paving, row, wall, field, world):
    config = row["entrance"]
    edge, view = hilyard.face_on(parts, wall, world, config["side"], config["near"])
    span, add, normal, plan, _, _ = view
    point = edge.interpolate(edge.project(Point(world(*config["near"]))))
    u = edge.project(point)
    top = config["height"] + 2.62
    supports = []
    lower = hilyard.grade(field, plan(u, 1.25)) + 0.07
    start, stop = max(0.17, u - 1.33), min(span - 0.17, u + 1.33)
    if stop - start > 1.40:
        hilyard.lintel(add, start, stop, top, 1.32, DARK)
        for p in (start + 0.15, stop - 0.15):
            pier = orient(fairmount.rectangle(plan, p - 0.095, p + 0.095, 1.03, 1.19))
            hilyard.pier(parts, field, pier, top - 0.06, STONE)
            supports.append(pier)
        paving_slab(
            paving,
            orient(fairmount.rectangle(plan, start, stop, 0, 2.32)),
            field,
            STONE,
        )
    hilyard.potter.door(add, u, max(lower, config["height"]), config["door"])
    direction = float(np.degrees(np.arctan2(normal[0], normal[1])) % 360)
    gate = hilyard.frontages.estimated_entry(
        paving,
        {
            **row,
            "entry": dict(
                gate=config["gate"],
                bearing=direction,
                threshold_z_m=config["height"],
                width_m=1.13,
                distance_m=config["distance"],
                stair_run_m=1.61,
            ),
            "entry_finish": "stone",
        },
        field,
        edge,
        point,
    )
    return supports, [gate]


def build(row, field, paving):
    style = row.get("treatment")
    if style is None:
        return hilyard.build(row, field, paving)
    roof = orient(
        set_precision(
            Polygon(row["outline_enu_m"], row["courtyard_rings_enu_m"]), 0.002
        )
    )
    patch, _, world = older.transforms(row)
    if style == "linked-wings":
        return linked_wings(row, field, paving, roof, patch, world)
    wall = orient(roof.buffer(-row["eaves_m"], join_style="mitre"))
    parts = []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    pattern_facade(parts, row, wall, field, height)
    supports, gates = [], []
    if style == "alder-court":
        slope_gables(parts, row, wall, field, world, height)
    elif style == "pink-courtyard":
        supports.extend(courtyard(parts, roof, wall, row, field, world, height))
    elif style == "heron":
        supports, gates = heron_entry(parts, paving, row, wall, field, world)
    elif style in ("green-entrance", "blue-screen", "stores", "alley-panels"):
        retail(parts, row, wall, world, field)
    older.roof_equipment(parts, row, roof, height, patch)
    return agate.output(parts, row, roof, wall, supports, gates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, PAVING, "southwest_exterior_site", build
    )


if __name__ == "__main__":
    main()
