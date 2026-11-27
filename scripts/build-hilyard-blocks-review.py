# SPDX-License-Identifier: Apache-2.0
"""Export the Hilyard, Alder and East 14th–18th exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient

older = import_module("build-garden-franklin-review")
agate, emerald = older.agate, older.emerald
base, fairmount, garden, geometry = (
    older.base,
    older.fairmount,
    older.garden,
    older.geometry,
)
frontages, northwest, potter = emerald.frontages, emerald.northwest, emerald.potter
PACKAGE = "hilyard-blocks-review"
PAVING = "hilyard-blocks-paving"
DIRECTION = {"N": (0, 1), "E": (1, 0), "S": (0, -1), "W": (-1, 0)}
STONE = (170, 165, 146)
STEEL = (85, 97, 99)
WHITE = (206, 201, 178)
WOOD = (113, 93, 74)
BLUE = (108, 155, 182)


def grade(field, point):
    east, north = point
    # The west wing at 648 East 17th straddles the edge of the source terrain.
    return geometry.sample_ground(field, max(east, field["min_east_m"]), north)


def face_on(parts, shell, world, side, target):
    coordinate = Point(world(*target))
    direction = np.array(DIRECTION[side])
    choices = [
        (edge, view)
        for edge, view in fairmount.views(parts, shell)
        if view[0] > 0.77 and view[2] @ direction > 0.90
    ]
    return min(choices, key=lambda pair: pair[0].distance(coordinate))


def side_position(edge, world, feature, value):
    s, t = feature["target"]
    if feature["side"] in ("N", "S"):
        s = value
    else:
        t = value
    return edge.project(Point(world(s, t)))


def span_on(edge, world, feature):
    return sorted(
        side_position(edge, world, feature, value) for value in feature["span"]
    )


def elevate(add, distance):
    def offset(a, b, c, d, e, f, color):
        add(a, b, c + distance, d + distance, e, f, color)

    return offset


def pier(parts, field, polygon, top, color):
    bottom = min(grade(field, p) for p in polygon.exterior.coords) - 0.17
    if top <= bottom + 0.05:
        raise ValueError(f"Invalid column height at {polygon.bounds}.")
    base.flat(parts, orient(polygon), bottom, top, color)


def facade(parts, row, nominal, field, height):
    trim = row["trim_color"]
    seen = row["front_side"]
    occupied = row.get("clearance")
    patch, local, _ = older.transforms(row)
    gap = patch(occupied["bounds"]).buffer(0.01) if occupied else Polygon()
    specials = {
        f["side"]
        for f in row.get("features", [])
        if f["shape"]
        in {
            "shop",
            "brick-entry",
            "gallery",
            "panels",
            "garage-gallery",
            "red-porch",
            "awnings",
        }
    }
    for edge, (span, add, normal, plan, _, panel) in fairmount.views(parts, nominal):
        if span < 1.36:
            continue
        facing = normal @ DIRECTION[seen] > 0.89
        side = max(DIRECTION, key=lambda key: normal @ DIRECTION[key])
        mid = plan(span / 2, 0)
        y = grade(field, mid)
        top = min(height(plan(u, 0)) for u in np.linspace(0.09, span - 0.09, 7))
        if top - y < 0.55:
            continue
        for z in row["levels_z_m"][1:]:
            if y < z < top - 0.22 and not gap.covers(edge):
                add(0.06, span - 0.06, 0.004, 0.041, z - 0.045, z + 0.066, trim)
        city = row["city_objectid"]
        s, t = local(mid)
        is_brick = city == 170368 or (city == 170479 and s > -4.7)
        late_wood = city in (170358, 170390)
        if city == 170479 and not is_brick:
            add(
                0.012,
                span - 0.012,
                0.001,
                0.028,
                y - 0.075,
                top - 0.16,
                (188, 186, 169),
            )
            for z in np.arange(y + 0.29, top - 0.19, 0.206):
                add(0.016, span - 0.016, 0.026, 0.037, z, z + 0.017, (174, 177, 162))
        if late_wood:
            level = row["levels_z_m"][-1]
            if top - level > 0.29:
                add(0.012, span - 0.012, 0.005, 0.024, level, top - 0.14, (68, 77, 78))
                for z in np.arange(level + 0.15, top - 0.17, 0.205):
                    add(0.016, span - 0.016, 0.022, 0.032, z, z + 0.013, (86, 96, 95))
        if is_brick:
            tone = tuple(round(v * 0.92) for v in row["wall_color"])
            for z in np.arange(y + 0.30, top - 0.18, 0.24):
                add(0.017, span - 0.017, 0.005, 0.017, z, z + 0.011, tone)
        if side in specials or (city == 170479 and side == "E" and abs(t) < 5.8):
            continue
        count = max(1, round(span / (2.66 if facing else 3.87)))
        width = min(1.52, span / count * 0.64)
        for u in (np.arange(count) + 0.5) * span / count:
            p = plan(u, 0)
            ground = grade(field, p)
            if gap.covers(Point(p)):
                if not occupied or "bottom" not in occupied:
                    continue
                ground = max(ground, occupied["bottom"] - 0.19)
            cap = min(height(plan(q, 0)) for q in (u - width / 2, u, u + width / 2))
            for z in row["levels_z_m"]:
                if city == 170402 and side == "S" and z < 3 and abs(local(p)[0]) < 2.81:
                    continue
                lo = z + (0.68 if facing else 0.76)
                hi = min(lo + (1.33 if facing else 1.08), cap - 0.25)
                if lo > ground + 0.38 and hi > lo + 0.52:
                    glazed_add = elevate(add, 0.034) if late_wood else add
                    older.framed(glazed_add, u, width, lo, hi, 2, trim)
                    if city == 170479 and facing and z < 4:
                        head = garden.chapter.arch(
                            u, hi + 0.027, width + 0.28, 0.54, 0.43
                        )
                        # Project a narrow arched lintel above each exterior window.
                        panel(orient(head), 0.019, 0.064, trim)
        if (
            facing
            and span > 4.2
            and seen not in specials
            and row.get("entrance") is None
        ):
            at = span * 0.48
            p = plan(at, 0)
            if not gap.covers(Point(p)):
                floor = max(grade(field, p) + 0.08, row["levels_z_m"][0])
                if floor + 2.15 < height(p) - 0.17:
                    potter.door(add, at, floor, (115, 107, 91))


def balcony(parts, add, plan, start, stop, z, depth, trim):
    add(start, stop, -0.017, depth, z - 0.155, z, trim)
    add(start, stop, depth - 0.07, depth, z + 0.91, z + 0.975, trim)
    add(start, stop, depth - 0.061, depth, z + 0.135, z + 0.193, trim)
    for u in np.linspace(
        start + 0.06, stop - 0.06, max(2, round((stop - start) / 0.18) + 1)
    ):
        add(u - 0.018, u + 0.018, depth - 0.062, depth, z + 0.17, z + 0.93, trim)
    for u in (start + 0.05, stop - 0.05):
        add(u - 0.025, u + 0.025, 0.08, depth, z + 0.91, z + 0.98, trim)
    for u in np.linspace(
        start + 0.13, stop - 0.13, max(2, round((stop - start) / 4.2) + 1)
    ):
        add(
            u - 0.049, u + 0.049, depth - 0.10, depth - 0.013, z - 0.12, z + 0.985, trim
        )


def lintel(add, start, stop, level, depth, color):
    add(start, stop, -0.012, depth, level - 0.083, level + 0.084, color)


def arch_panel(panel, u, width, level, top, outer, inside):
    shape = garden.chapter.arch(u, level, width, top - level, (top - level) * 0.30)
    panel(orient(shape), 0.027, 0.076, outer)
    panel(orient(shape.buffer(-0.075)), 0.081, 0.098, inside)


def stairs(parts, f, field, world):
    start, end = world(*f["start"]), world(*f["end"])
    bottom = grade(field, start) + 0.093
    top = f["top"]
    if top - bottom > 0.35:
        northwest.stair(
            parts,
            start,
            end,
            bottom,
            top,
            f["width"],
            steps=max(4, round((top - bottom) / 0.175)),
        )
    # Two supports leave the space beneath the upper flight clear.
    center = np.asarray(end) * 0.85 + np.asarray(start) * 0.15
    out = Point(center).buffer(0.098, quad_segs=3)
    pier(parts, field, out, top - 0.36, STEEL)
    return [out]


def porch(parts, field, view, edge, row, f, world):
    span, add, _, plan, _, _ = view
    supports = []
    for station in f["stations"]:
        u = side_position(edge, world, f, station)
        lo, hi = max(0.06, u - f["width"] / 2), min(span - 0.06, u + f["width"] / 2)
        p = plan(u, 0)
        top, depth = f["height"], f["depth"]
        floor = max(row["levels_z_m"][0] + 0.14, grade(field, p) + 0.12)
        door_threshold = row.get("entrance", {}).get("height", floor)
        if top - door_threshold < 1.88:
            top = door_threshold + 2.18
        if row.get("entrance") is None:
            potter.door(add, u, floor, (114, 103, 81))
        lintel(add, lo, hi, top, depth, row["trim_color"])
        # A thin slab leaves the clear entry path between the outer columns.
        slab = fairmount.rectangle(plan, lo, hi, 0.01, depth)
        pier(parts, field, slab, floor, STONE)
        for x in (lo + 0.15, hi - 0.15):
            stem = fairmount.rectangle(
                plan, x - 0.069, x + 0.069, depth - 0.167, depth - 0.031
            )
            pier(parts, field, stem, top - 0.043, row["trim_color"])
            supports.append(stem)
    return supports


def galeried(parts, row, f, edge, view, field, world, height):
    span, add, _, plan, _, _ = view
    lo, hi = span_on(edge, world, f)
    lo, hi = max(0.065, lo), min(span - 0.065, hi)
    z = f["deck_levels"]
    depth = f["depth"]
    trim = row["trim_color"]
    distance = hi - lo
    if distance < 1.25:
        return
    for y in z:
        balcony(parts, add, plan, lo, hi, y, depth, trim)
    count = max(1, round(distance / f["rhythm"]))
    for u in lo + (np.arange(count) + 0.5) * distance / count:
        cap = min(height(plan(q, 0)) for q in (u - 0.67, u, u + 0.67))
        bottom = max(grade(field, plan(u, 0)) + 0.12, row["levels_z_m"][0])
        podium = row.get("clearance", {}).get("bottom", bottom)
        for y in ([bottom] if bottom > podium - 0.30 else []) + z:
            if cap > y + 2.11:
                if u - distance / count * 0.22 > 0.45:
                    potter.door(add, u - distance / count * 0.22, y, f["door_color"])
                w = min(1.39, distance / count * 0.40)
                older.framed(
                    add,
                    u + distance / count * 0.22,
                    w,
                    y + 0.67,
                    min(y + 1.97, cap - 0.15),
                    2,
                    trim,
                )
    for u in np.linspace(lo + 0.10, hi - 0.10, count + 1):
        if len(z) > 1:
            col_low = z[0] - 0.13
        else:
            col_low = grade(field, plan(u, depth)) + 0.03
        high = min(height(plan(u, 0)) - 0.10, z[-1] + 2.42)
        if high > col_low + 0.20:
            add(u - 0.057, u + 0.057, depth - 0.106, depth + 0.024, col_low, high, trim)


def glazed(add, lo, hi, level, head, trim):
    intervals = max(1, round((hi - lo) / 1.38))
    for u in lo + (np.arange(intervals) + 0.5) * (hi - lo) / intervals:
        width = 0.92 * (hi - lo) / intervals
        older.framed(add, u, width, level, head, 2, trim)


def commercial(row, f, view, extent):
    span, add, _, _, _, _ = view
    lo, hi = extent or (0.14, span - 0.14)
    trim = row["trim_color"]
    if f["shape"] == "shop":
        level, head = f["level"], f["head"]
        glazed(add, lo, hi, level + 0.59, head, trim)
        potter.door(add, hi - min(1.02, (hi - lo) * 0.20), level, (106, 97, 77))
        add(lo, hi, 0.009, 0.26, head + 0.25, head + 0.50, (123, 115, 90))
    elif f["shape"] == "brick-entry":
        level, top = f["level"], f["top"]
        add(lo, hi, 0.026, 0.07, level + 0.17, top, (101, 130, 116))
        glazed(elevate(add, 0.062), lo, hi, level + 0.27, top - 0.12, (85, 109, 106))
        potter.door(elevate(add, 0.143), (lo + hi) / 2, level, (87, 103, 93))
        for u in np.arange(lo + 0.20, hi - 0.11, 0.43):
            add(
                u - 0.035,
                u + 0.035,
                0.119,
                0.19,
                level + 0.16,
                top - 0.03,
                (87, 110, 104),
            )
    elif f["shape"] == "panels":
        for u in (lo + 0.5, (lo + hi) * 0.57, hi - 0.42):
            add(
                u - 0.24,
                u + 0.24,
                0.027,
                0.096,
                row["base_z_m"] + 0.16,
                f["height"],
                f["color"],
            )
            add(
                u - 0.23,
                u + 0.24,
                0.099,
                0.116,
                row["base_z_m"] + 0.20,
                f["height"],
                (71, 96, 86),
            )


def awnings(parts, row, f, edge, view, world):
    span, add, _, plan, point, _ = view
    floor = f["door_floor"]
    for station in f["stations"]:
        u = side_position(edge, world, f, station)
        w = 1.24 if station < 0 else 1.36
        h = f["head"]
        if h > floor + 2:
            for at in (-w, w):
                fairmount.beam(
                    parts,
                    point(u + at, 0.009, h),
                    point(u + at, 0.75, h - 0.29),
                    0.084,
                    BLUE,
                )
            # A shallow metal plane slopes toward the pavement.
            area = fairmount.rectangle(plan, u - w, u + w, 0, 0.77)
            near = np.asarray(plan(u, 0))
            normal = np.asarray(plan(u, 1)) - near
            mesh = geometry.shell(
                orient(area),
                h - 0.357,
                lambda e, n: h - 0.39 * (np.array([e, n]) - near) @ normal,
                BLUE,
                BLUE,
            )
            mesh.vertices[:, 1] = np.where(
                np.isclose(mesh.vertices[:, 1], h - 0.357),
                h
                - 0.39 * ((mesh.vertices[:, (0, 2)] * [1, -1] - near) @ normal)
                - 0.06,
                mesh.vertices[:, 1],
            )
            parts.append(mesh)
        if all(abs(station - t) > 1.27 for t in f["door_stations"]):
            older.framed(
                add,
                u,
                min(1.61, 2 * w),
                floor + 0.76,
                floor + 1.88,
                2,
                row["trim_color"],
            )
    for station in f["door_stations"]:
        u = side_position(edge, world, f, station)
        potter.door(add, u, floor, (145, 85, 69))
        approach = fairmount.rectangle(
            plan, max(0.04, u - 0.55), min(span - 0.04, u + 0.55), 0.01, 0.59
        )
        base.flat(parts, orient(approach), floor - 0.19, floor, STONE)


def decorative_entry(parts, row, f, edge, view, field, world):
    span, add, _, plan, point, panel = view
    if f["shape"] == "tudor":
        center = span / 2
        gable_base = f["peak"] + 0.79
        gable_top = 10.93
        half = min(2.19, span * 0.417)
        for a, b in (
            ((center - half, gable_base), (center, gable_top)),
            ((center, gable_top), (center + half, gable_base)),
            ((center - half, gable_base), (center + half, gable_base)),
            ((center, gable_base), (center, gable_top - 0.12)),
        ):
            fairmount.beam(
                parts,
                point(a[0], 0.09, a[1]),
                point(b[0], 0.09, b[1]),
                0.078,
                (84, 77, 65),
            )
        for u in (center - 0.89, center + 0.89):
            older.framed(
                add, u, 0.90, gable_base + 0.24, gable_base + 1.39, 2, (91, 91, 78)
            )
        for station in f["positions"]:
            u = side_position(edge, world, f, station)
            floor = f["level"]
            arch_panel(panel, u, 1.15, floor, floor + 1.96, (82, 67, 53), (139, 98, 62))
            w = f["width"] / 2
            p = np.asarray(plan(u, 0.82))
            stand = Point(p).buffer(0.12, quad_segs=2)
            pier(parts, field, stand, floor + 2.18, WHITE)
            triangle = Polygon(
                ((u - w, floor + 2.19), (u + w, floor + 2.19), (u, f["peak"]))
            )
            panel(orient(triangle), -0.025, 0.94, WHITE)
            for a, b in (
                (point(u - w, 0.949, floor + 2.18), point(u, 0.949, f["peak"])),
                (point(u, 0.949, f["peak"]), point(u + w, 0.949, floor + 2.18)),
            ):
                fairmount.beam(parts, a, b, 0.11, (81, 79, 67))
        return
    if f["shape"] == "stone-piers":
        for station in f["stations"]:
            u = side_position(edge, world, f, station)
            low = max(grade(field, plan(u, 0)) - 0.15, row["base_z_m"])
            for z in np.arange(low, 7.89, 0.31):
                start, stop = (
                    max(0.025, u - f["span"] / 2),
                    min(span - 0.02, u + f["span"] / 2),
                )
                add(
                    start,
                    stop,
                    0.015,
                    0.25,
                    z,
                    z + 0.29,
                    STONE if round(z / 0.31) % 3 else (141, 134, 116),
                )
        return
    lo, hi = span_on(edge, world, f)
    floor, top, depth = f["level"], f["top"], f["deck_depth"]
    for u in np.linspace(lo + 0.58, hi - 0.56, 4):
        potter.door(add, u, floor, (136, 66, 54))
    low = grade(field, plan((lo + hi) / 2, depth))
    landing = orient(fairmount.rectangle(plan, lo, hi, 0, depth))
    base.flat(parts, landing, min(low, floor - 0.16), floor, STONE)
    lintel(add, lo, hi, top, depth, (155, 132, 102))
    for u in (lo + 0.17, hi - 0.20):
        add(u - 0.10, u + 0.10, depth - 0.22, depth - 0.05, floor, top - 0.07, WOOD)


def portico(parts, row, f, edge, view, field, world):
    span, add, _, plan, point, panel = view
    lo, hi = span_on(edge, world, f)
    low, high = f["floor"], f["height"]
    supports = []
    stone = row["trim_color"]
    # The entablature spans the outer line of four columns.
    for z, depth, thickness in (
        (high - 0.28, 2.96, 0.18),
        (high - 0.05, 3.14, 0.15),
        (high + 0.13, 3.19, 0.12),
    ):
        add(lo, hi, -0.039, depth, z, z + thickness, stone)
    add(lo, hi, 0.08, 3.0, high - 0.78, high - 0.28, stone)
    platform = orient(fairmount.rectangle(plan, lo, hi, 0, 2.84))
    pier(parts, field, platform, low, STONE)
    for t in f["columns"]:
        u = side_position(edge, world, f, t)
        position = Point(plan(u, 2.62))
        shaft = orient(position.buffer(0.225, quad_segs=5))
        base.flat(parts, shaft, low + 0.15, high - 0.92, stone)
        for z, r, w in (
            (low, 0.32, 0.12),
            (low + 0.12, 0.26, 0.11),
            (high - 0.98, 0.29, 0.16),
            (high - 0.80, 0.34, 0.17),
        ):
            ring = orient(position.buffer(r, quad_segs=3))
            base.flat(parts, ring, z, z + w, stone)
        supports.append(shaft)
    for u in np.linspace(lo + 0.85, hi - 0.87, 6):
        if abs(u - span / 2) > 1.12:
            arch_panel(panel, u, 1.25, low + 0.47, low + 2.75, stone, (125, 130, 111))
        older.framed(add, u, 1.13, low + 4.46, low + 6.03, 2, stone)
    balcony(parts, add, plan, span / 2 - 1.02, span / 2 + 1.02, low + 3.19, 0.43, stone)
    # End bays have the same belt courses and tall arched ground-floor surrounds.
    for offset in (-1, 1):
        u = (lo if offset < 0 else hi) + offset * 0.60
        if 0.75 < u < span - 0.75:
            arch_panel(panel, u, 1.04, low + 0.46, low + 2.65, stone, (120, 127, 112))
    return supports


def garage_gallery(parts, row, f, view, edge, world, height):
    span, add, _, plan, _, _ = view
    lo, hi = span_on(edge, world, f)
    trim = row["trim_color"]
    floor = f["z"]
    top = f["enclosure_top"]
    balcony(parts, add, plan, lo, hi, f["level"], f["depth"], trim)
    add(lo - 0.13, hi + 0.13, -0.03, 0.114, floor - 0.12, floor + 0.06, trim)
    for u in (lo - 0.10, hi + 0.1):
        y = row["levels_z_m"][0]
        add(u - 0.065, u + 0.065, 0.004, 0.104, y, floor, trim)
        add(u - 0.075, u + 0.075, 0.055, 0.12, f["level"], top - 0.15, trim)
    for u in np.linspace(lo + 0.56, hi - 0.54, 3):
        cap = height(plan(u, 0)) - 0.28
        older.framed(add, u, 1.12, floor + 0.66, min(floor + 2.09, cap), 2, trim)


def details(parts, row, wall, nominal, field, world, height):
    supports = []
    for f in row.get("features", []):
        name = f["shape"]
        if name == "stairs":
            supports.extend(stairs(parts, f, field, world))
            continue
        access = (
            row["city_objectid"] == 170359 and name == "gallery" or name == "portico"
        )
        edge, view = face_on(
            parts, wall if access else nominal, world, f["side"], f["target"]
        )
        _, add, _, plan, _, _ = view
        if name == "gallery":
            galeried(parts, row, f, edge, view, field, world, height)
        elif name == "porch":
            supports.extend(porch(parts, field, view, edge, row, f, world))
        elif name == "awnings":
            awnings(parts, row, f, edge, view, world)
        elif name in ("shop", "brick-entry", "panels"):
            commercial(row, f, view, span_on(edge, world, f) if "span" in f else None)
        elif name in ("tudor", "red-porch", "stone-piers"):
            decorative_entry(parts, row, f, edge, view, field, world)
        elif name == "portico":
            supports.extend(portico(parts, row, f, edge, view, field, world))
        elif name == "garage-gallery":
            garage_gallery(parts, row, f, view, edge, world, height)
        elif name in ("gate", "fins", "bay-trim"):
            lo, hi = span_on(edge, world, f)
            if name == "bay-trim":
                lintel(add, lo, hi, f["height"], 0.14, row["trim_color"])
                continue
            low, top = (
                (f["level"], f["top"]) if name == "gate" else (f["floor"], f["top"])
            )
            for u in np.arange(
                lo + 0.05, hi - 0.04, 0.15 if name == "gate" else f["step"]
            ):
                add(
                    u - 0.026,
                    u + 0.026,
                    -0.019,
                    0.087,
                    low,
                    top,
                    STEEL if name == "gate" else (126, 145, 105),
                )
            if name == "gate":
                lintel(add, lo, hi, top, 0.13, STEEL)
                supports.append(orient(fairmount.rectangle(plan, lo, hi, -0.04, 0.055)))
        else:
            raise ValueError(f"Unknown facade detail {name}.")
    return supports


def edge_apron(paving, field, roof):
    boundary = field["min_east_m"]
    west, south, _, north = roof.bounds
    step = field["spacing_m"]
    y = (
        np.floor((south - 6 - field["min_north_m"]) / step) * step
        + field["min_north_m"]
    )
    for n in np.arange(y, north + 6, step):
        piece = orient(box(west - 3.0, n, boundary + 0.034, n + step))

        def surface(e, north):
            return grade(field, (e, north)) - 0.014

        bottom = min(surface(*p) for p in piece.exterior.coords) - 0.17
        mesh = geometry.shell(piece, bottom, surface, (143, 148, 112), (143, 148, 112))
        mesh.update_faces(mesh.face_normals[:, 1] > 0.05)
        mesh.remove_unreferenced_vertices()
        paving.append(mesh)


def build(row, field, paving):
    patch, _, world = older.transforms(row)
    roof = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    nominal = orient(roof.buffer(-row["eaves_m"], join_style="mitre"))
    collar = row.get("clearance")
    parts, supports = [], []
    wall = nominal
    if collar:
        opening = patch(collar["bounds"])
        wall = orient(nominal.difference(opening))
        if "bottom" in collar:
            area = orient(opening.intersection(roof).buffer(-0.026))

            def surface(e, n):
                return grade(field, (e, n)) + 0.047

            low = min(surface(*p) for p in area.exterior.coords) - 0.16
            paving.append(geometry.shell(area, low, surface, STONE, STONE))
            row = {
                **row,
                "raised_wall_enu_m": list(nominal.exterior.coords)[:-1],
                "raised_wall_bottom_z_m": collar["bottom"],
            }
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    facade(parts, row, nominal if "bottom" in (collar or {}) else wall, field, height)
    if collar:
        for s, t in collar.get("posts", []):
            foot = patch((s - 0.105, t - 0.10, s + 0.105, t + 0.10))
            top = collar.get(
                "post_top", collar.get("bottom", height(world(s, t)) - 0.15)
            )
            pier(parts, field, foot, top, row["trim_color"])
            supports.append(foot)
    supports.extend(details(parts, row, wall, nominal, field, world, height))
    older.roof_equipment(parts, row, roof, height, patch)
    gates = []
    entrance = row.get("entrance")
    if entrance:
        edge, view = face_on(parts, wall, world, entrance["side"], entrance["near"])
        point = edge.interpolate(edge.project(Point(world(*entrance["near"]))))
        _, add, normal, _, _, _ = view
        potter.door(add, edge.project(point), entrance["height"], entrance["door"])
        bearing = float(np.degrees(np.arctan2(normal[0], normal[1])) % 360)
        gate = dict(
            gate=entrance["gate"],
            bearing=bearing,
            threshold_z_m=entrance["height"],
            width_m=1.13,
            distance_m=entrance["distance"],
            stair_run_m=min(2.1, entrance["distance"] * 0.46),
        )
        gates.append(
            frontages.estimated_entry(
                paving,
                {**row, "entry": gate, "entry_finish": "stone"},
                field,
                edge,
                point,
            )
        )
    if row.get("terrain_extension"):
        edge_apron(paving, field, roof)
    return agate.output(parts, row, roof, wall, supports, gates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, PAVING, "hilyard_blocks_site", build
    )


if __name__ == "__main__":
    main()
