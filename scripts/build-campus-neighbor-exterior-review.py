# SPDX-License-Identifier: Apache-2.0
"""Build seven registered exteriors at the University of Oregon's neighborhood edges."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import set_precision, union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh


path = Path(__file__).with_name("build-residential-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
residential = module_from_spec(loader)
loader.loader.exec_module(residential)
base, tools, site = residential.base, residential.tools, residential.site
geometry, science, shared, prior = (
    residential.geometry,
    residential.science,
    residential.shared,
    residential.prior,
)
ROOT, SCENE = residential.ROOT, residential.SCENE
SPEC = ROOT / "data/metadata/campus-neighbor-exterior-review.json"
DIRECTORY = "campus-neighbor-exterior-review"
GROUND = "campus-neighbor-approaches"

PALE = (222, 215, 184)
GLASS = (99, 122, 121)
METAL = (176, 183, 175)
DARK = (63, 73, 72)
GREEN = (73, 106, 69)
MAROON = (131, 76, 70)
CONCRETE = (172, 169, 151)
CREAM = (196, 184, 148)
SHINGLE = (126, 123, 101)
WOOD = (165, 112, 78)
STONE = (171, 172, 157)
MASONRY = (179, 171, 148)
BLUE = (92, 117, 133)
BODY = {
    "coho-south": WOOD,
    "kincaid": STONE,
    "christus": MASONRY,
    "newman": GREEN,
    "hayward": (166, 153, 121),
    "aldersgate": BLUE,
    "agate": CREAM,
}


def divide(plan, fit):
    if "roof_step" not in fit:
        return [(plan, fit["coefficients"][0])]
    rule = fit["roof_step"]
    w, s, e, n = plan.bounds
    q = rule["cut_enu_m"]
    masks = (
        (box(w - 1, s - 1, q, n + 1), box(q, s - 1, e + 1, n + 1))
        if rule["axis"] == 0
        else (box(w - 1, s - 1, e + 1, q), box(w - 1, q, e + 1, n + 1))
    )
    return [
        (part, h)
        for mask, h in zip(masks, rule["heights_m"], strict=True)
        for part in geometry.sections(set_precision(plan.intersection(mask), 0.001))
    ]


def step_caps(parts, outline, fit):
    rim = outline.difference(outline.buffer(-fit["edge_width_m"]))
    pale = tuple(fit["cap_rgb"])
    for area, z in divide(outline, fit):
        base.flat(parts, area, z - 0.007, z + 0.015, PALE, pale)
        edge = set_precision(area.intersection(rim), 0.001)
        base.flat(parts, edge, z - 0.002, z + fit["edge_cap_m"], PALE, pale)
    for row in fit.get("solar_rows", []):
        w, s, e, n = row["bounds_enu_m"]
        z = next(
            height
            for area, height in divide(outline, fit)
            if area.covers(box(w, s, e, n))
        )
        positions = np.linspace(w, e, row["panels"] + 1)
        for a, b in zip(positions, positions[1:]):
            panel = box(a + 0.034, s, b - 0.034, n)
            parts.append(
                geometry.shell(
                    panel,
                    z + 0.032,
                    lambda e, q: z + 0.13 + 0.11 * (q - s) / (n - s),
                    METAL,
                    (74, 91, 103),
                )
            )


def sample(field, point):
    return geometry.sample_ground(field, *point)


def bearing(a, b):
    along = np.asarray(b) - a
    return along[::-1] * [1, -1] / np.linalg.norm(along)


def bays(length, interval, offset=1.16):
    return np.linspace(offset, length - offset, max(2, round(length / interval)))


def window(add, center, width, z, height=1.21, frame=PALE):
    prior.window(add, center, width, z, z + height, frame, GLASS, ribs=1)


def door(add, center, z, color, depth=0):
    add(center - 0.53, center + 0.53, 0.016 + depth, 0.07 + depth, z, z + 2.27, DARK)
    add(
        center - 0.46,
        center + 0.46,
        0.07 + depth,
        0.102 + depth,
        z + 0.055,
        z + 2.16,
        color,
    )
    if color != MAROON:
        add(
            center - 0.36,
            center + 0.36,
            0.103 + depth,
            0.119 + depth,
            z + 1.04,
            z + 1.99,
            GLASS,
        )
    add(
        center + 0.28,
        center + 0.37,
        0.105 + depth,
        0.143 + depth,
        z + 0.95,
        z + 1.015,
        METAL,
    )


def railing(add, left, right, projection, z, tone=DARK):
    add(left, right, projection - 0.054, projection + 0.024, z + 0.88, z + 0.94, tone)
    add(left, right, projection - 0.031, projection + 0.002, z + 0.075, z + 0.12, tone)
    for x in np.linspace(left, right, max(2, round((right - left) / 0.19) + 1)):
        add(
            x - 0.016,
            x + 0.016,
            projection - 0.043,
            projection + 0.012,
            z + 0.10,
            z + 0.918,
            tone,
        )


def side_stair(add, left, projection, floor, rise, reverse=False):
    count = round(rise / 0.174)
    stride = 0.26
    for i in range(count):
        j = count - 1 - i if reverse else i
        u = left + j * stride
        z = floor + (i + 1) * rise / count
        add(u, u + stride + 0.011, projection - 0.99, projection, z - 0.11, z, CONCRETE)
        add(u, u + 0.027, projection - 0.04, projection, z, z + 0.89, DARK)
        add(
            u,
            u + stride + 0.015,
            projection - 0.056,
            projection,
            z + 0.85,
            z + 0.91,
            DARK,
        )


def gallery(parts, plans, field, row, grade, eave, floor, gates, ground):
    kind = row["kind"]
    is_hayward = kind == "hayward"
    side = 1 if is_hayward else -1
    longest = max(
        (
            edge
            for edge in shared.face_edges(plans[0])
            if bearing(*edge)[1] * side > 0.95
        ),
        key=lambda edge: LineString(edge).length,
    )
    front = LineString(longest)
    length, add = tools.face(parts, *longest)
    first = eave - (5.65 if is_hayward else 8.35)
    projection = 1.59 if is_hayward else 1.46
    setback = 2.75 if is_hayward else 3.13
    w, s, e, n = plans[0].bounds
    core_mask = (
        box(w - 1, s - 1, e + 1, n - setback)
        if is_hayward
        else box(w - 1, s + setback, e + 1, n + 1)
    )
    garage_wall = plans[0].intersection(core_mask)
    base.flat(parts, garage_wall, floor, first - 0.12, CONCRETE)
    base.flat(parts, plans[0], first - 0.122, eave - 0.001, BODY[kind])
    # The site approach is anchored at the actual building wall and joins the front gallery.
    hint = row["entrance_hints"][0]
    gate = residential.entrance([], field, [longest], hint)
    u_gate = front.project(Point(gate["position_enu_m"]))
    span = 2.52 if is_hayward else 2.43
    outward = bearing(*longest)
    threshold_ref = np.asarray(gate["position_enu_m"])
    pad_run = 4.1 if is_hayward else 4.75
    target = threshold_ref + pad_run * outward
    rise = first - sample(field, target) - 0.028
    assert 0.45 < rise < 4.7, (row["id"], rise, eave, grade)
    gate.update(
        {
            "landing_m": pad_run,
            "approach_distance_m": pad_run + 0.18,
            "rise_m": round(float(rise), 4),
        }
    )
    # Stair ends at the walkway datum. Its side rails and outer columns leave an open approach.
    toe = first - rise
    total = max(4, round(rise / 0.175))
    for i in range(total):
        top = toe + rise * (i + 1) / total
        end = pad_run - i * (pad_run - projection) / (total - 1)
        add(u_gate - span / 2, u_gate + span / 2, 0.002, end, toe - 0.23, top, CONCRETE)
        for x in (u_gate - span * 0.5 + 0.065, u_gate + span * 0.5 - 0.065):
            add(x - 0.025, x + 0.025, end - 0.07, end + 0.04, top, top + 0.88, DARK)
    gate["threshold_z_m"] = round(first, 3)
    gates.append(gate)
    # A grade-following landing joins the lower tread to the existing street surface.
    foot = target + 0.26 * outward
    base.flat(
        ground,
        Point(foot).buffer(0.70, quad_segs=2),
        sample(field, foot) - 0.17,
        sample(field, foot) + 0.035,
        CONCRETE,
    )
    for i in range(2 if is_hayward else 3):
        z = first + i * (2.83 if is_hayward else 2.69)
        add(0.025, length - 0.025, -0.025, projection, z - 0.19, z, CONCRETE)
        if i:
            railing(add, 0.06, length - 0.06, projection, z)
        else:
            railing(add, 0.065, u_gate - span / 2, projection, z)
            railing(add, u_gate + span / 2, length - 0.065, projection, z)
        add(
            0.024,
            length - 0.024,
            projection - 0.06,
            projection + 0.02,
            z - 0.162,
            z - 0.064,
            WOOD if is_hayward else PALE,
        )
        for u in bays(length, 4.26, 1.61):
            window(add, u - 0.55, 1.51, z + 0.63, 1.19)
            if abs(u + 0.79 - u_gate) > 0.72 or i:
                door(add, u + 0.79, z, WOOD if is_hayward else DARK)
        if not i:
            door(add, u_gate, z, WOOD if is_hayward else DARK)
        if not is_hayward and i < 2:
            side_stair(
                add,
                max(0.26, length * 0.36),
                projection + 0.42,
                z,
                2.69,
                reverse=bool(i),
            )
    if is_hayward:
        for p in (1.22, length - 4.93):
            side_stair(add, p, projection + 0.52, first, 2.83, reverse=p < 2)
    along = (np.asarray(longest[1]) - longest[0]) / length
    supports = []
    for u in bays(length, 4.47, 1.38):
        if abs(u - u_gate) < span * 0.61:
            continue
        point = np.asarray(longest[0]) + u * along + outward * (projection - 0.06)
        z = sample(field, point)
        add(
            u - 0.09,
            u + 0.09,
            projection - 0.155,
            projection + 0.04,
            z - 0.06,
            first - 0.19 if is_hayward else eave - 0.09,
            CONCRETE if is_hayward else METAL,
        )
        supports.append(Point(point).buffer(0.102, quad_segs=2))
    for a, b in shared.face_edges(plans[0]):
        if (a, b) == longest:
            continue
        length, add = tools.face(parts, a, b)
        if length < 4:
            continue
        for u in bays(length, 3.44):
            for z in np.arange(first + 0.69, eave - 1.05, 2.72):
                window(add, u, min(1.69, length / 4), z)
    return [orient(p) for p in geometry.sections(garage_wall)], supports


def coho_south(parts, a, b, grade, eave, gates):
    length, add = tools.face(parts, a, b)
    normal = bearing(a, b)
    if length < 4:
        return
    if abs(normal[0]) > 0.82 and length > 8:
        # The east and west elevations use the same raised ribbed bays on the Coho property.
        residential.coursing(
            add, 0.015, length - 0.015, grade + 0.32, eave - 0.12, 0.195, (145, 102, 73)
        )
        for u in bays(length, 5.16, 1.92):
            low = grade + 2.42
            add(u - 0.93, u + 0.93, 0.008, 0.59, low, eave - 0.12, METAL)
            for x in np.linspace(u - 0.89, u + 0.89, 18):
                add(x - 0.009, x + 0.009, 0.588, 0.619, low + 0.02, eave - 0.18, STONE)
            for z in (low + 0.58, low + 2.98):
                add(u - 0.71, u + 0.71, 0.613, 0.654, z, z + 1.21, PALE)
                add(u - 0.659, u + 0.659, 0.654, 0.686, z + 0.052, z + 1.158, GLASS)
        return
    add(0.02, length - 0.02, 0.012, 0.053, grade - 0.13, grade + 2.56, MAROON)
    residential.coursing(
        add, 0.03, length - 0.03, grade + 2.6, eave - 0.13, 0.17, (139, 100, 70)
    )
    for f in (0.16, 0.46, 0.78):
        for z in (grade + 1.05, grade + 3.25, grade + 5.92):
            if z + 1.24 < eave:
                window(add, length * f, 0.95 if f != 0.16 else 1.15, z)
    if normal[1] < -0.7:
        screen_left, screen_right = length * 0.49, length * 0.85
        add(screen_left, screen_right, 0.05, 0.45, grade - 0.05, grade + 3.07, METAL)
        for x in np.arange(screen_left + 0.04, screen_right, 0.13):
            add(x - 0.014, x + 0.014, 0.448, 0.47, grade + 0.05, grade + 3, STONE)
        for u in np.linspace(screen_left + 0.44, screen_right - 0.44, 2):
            add(u - 0.31, u + 0.31, 0.465, 0.485, grade + 0.65, grade + 2.24, PALE)
            add(u - 0.246, u + 0.246, 0.486, 0.508, grade + 0.71, grade + 2.15, GLASS)
        edge = LineString([a, b])
        for gate in gates:
            p = Point(gate["position_enu_m"])
            if edge.distance(p) < 0.02:
                u = edge.project(p)
                add(u - 0.81, u + 0.81, 0.021, 0.96, grade + 2.54, grade + 2.72, DARK)


def courtyard_facade(parts, edge, grade, lookup, kind, gates):
    a, b = edge
    length, add = tools.face(parts, a, b)
    direction = bearing(a, b)
    n, e = np.mean([a[1], b[1]]), np.mean([a[0], b[0]])
    if length < 3.45:
        return
    top = lookup(e, n)
    add(0.02, length - 0.02, -0.015, 0.074, grade - 0.2, grade + 0.45, CONCRETE)
    add(0.02, length - 0.02, -0.012, 0.18, top - 0.14, top + 0.015, PALE)
    if kind == "kincaid" and direction[0] > 0.6 and n < -208:
        add(0.03, length - 0.03, 0.013, 0.79, grade + 1.06, grade + 1.24, CONCRETE)
        for u in bays(length, 2.19, 1.0):
            window(
                add,
                u,
                min(length / 5, 1.69),
                grade + 1.13,
                min(top - 0.28 - grade - 1.13, 2.56),
            )
        for u in np.arange(0.22, length - 0.11, 0.17):
            if (u % 2.19) < 0.48:
                add(
                    u - 0.016,
                    u + 0.016,
                    0.071,
                    0.107,
                    grade + 1.17,
                    top - 0.19,
                    (113, 107, 90),
                )
        return
    if kind == "kincaid" and direction[0] > 0.72 and n > -204:
        # Plain end wall and the hall's tall window strip toward the court.
        for i in np.arange(grade + 0.54, top - 0.27, 0.25):
            add(0.04, length - 0.04, 0.02, 0.036, i, i + 0.011, CONCRETE)
        return
    if kind == "kincaid" and -207 < n < -198 and direction[1] < -0.35:
        for u in bays(length, 1.15, 0.59):
            window(
                add,
                u,
                min(0.85, length / 4.6),
                grade + 0.68,
                min(3.26, top - grade - 1.02),
                DARK,
            )
        return

    rows = (grade + 0.70, grade + 3.19) if top - grade > 5.1 else (grade + 0.71,)
    for u in bays(length, 3.03):
        for z in rows:
            window(add, u, min(length / 4.9, 1.52), z, 1.06)
    if kind == "christus" and e > -477 and direction[1] > 0.83 and length > 9:
        add(0.04, length - 0.04, 0.02, 0.66, top - 0.26, top - 0.121, PALE)
        add(0.07, length - 0.07, 0.19, 0.6, top - 0.36, top - 0.26, WOOD)
        for u in (length * 0.12, length * 0.87):
            add(u - 0.061, u + 0.061, 0.51, 0.625, grade + 0.04, top - 0.26, WOOD)
    if kind == "christus" and e < -477 and direction[0] > 0.80 and length > 6:
        u = length * 0.34
        for x in np.arange(u - 0.58, u + 0.60, 0.12):
            add(x - 0.04, x + 0.04, 0.05, 0.084, grade + 0.12, top - 0.18, PALE)


def agate(parts, a, b, grade, upper, gates):
    length, add = tools.face(parts, a, b)
    if length < 4:
        return
    normal = bearing(a, b)
    front = normal[1] < -0.88
    if front:
        deck = grade + 2.64
        add(0.03, length - 0.03, -0.015, 1.18, deck - 0.23, deck, MAROON)
        railing(add, 0.055, length - 0.055, 1.15, deck)
        edge = LineString([a, b])
        for i, u in enumerate(
            np.linspace(1.18, length - 1.22, max(2, round(length / 3.28)))
        ):
            if i % 3 == 0 and u > 1.8:
                door(add, u - 0.68, deck + 0.017, MAROON)
                if prior.clear_of_entry(edge, u - 0.68, 0.54, gates):
                    door(add, u - 0.68, grade + 0.07, MAROON)
            window(add, u + 0.60, 1.19, deck + 0.697, 0.98)
            if prior.clear_of_entry(edge, u + 0.60, 0.62, gates):
                window(add, u + 0.60, 1.19, grade + 0.75, 0.98)
        for gate in gates:
            point = Point(gate["position_enu_m"])
            if edge.distance(point) < 0.02:
                door(add, edge.project(point), gate["threshold_z_m"], MAROON)
        if length > 10:
            side_stair(add, length * 0.68, 1.18, grade, 2.63)
            for u in np.arange(length * 0.68, length * 0.68 + 3.93, 0.092):
                add(u - 0.018, u + 0.018, 1.128, 1.182, grade + 0.22, deck - 0.04, DARK)
                add(
                    u - 0.018,
                    u + 0.018,
                    1.128,
                    1.182,
                    deck + 0.96,
                    min(upper - 0.055, deck + 2.51),
                    DARK,
                )
        add(0.025, length - 0.025, -0.015, 0.11, upper - 0.20, upper + 0.008, MAROON)
    else:
        for u in bays(length, 3.32):
            for z in np.arange(grade + 0.62, upper - 1.34, 2.63):
                window(add, u, min(length / 4, 1.28), z)


def newman(parts, outline, plan, eave, grade, floor, gates):
    # The LiDAR fixes the upper roof elevation. The street view resolves the
    # steep east face and reverse dormers below the edge of the flat deck.
    ridge, nose = -81.4, -77.8
    fascia = grade + 3.35
    w, s, e, n = outline.bounds
    cap = outline.intersection(box(w - 1, s - 1, ridge + 0.023, n + 1))
    base.flat(parts, cap, eave - 0.008, eave + 0.015, CONCRETE, (190, 191, 183))
    rim = cap.difference(cap.buffer(-0.20))
    base.flat(parts, rim, eave, eave + 0.22, PALE, (183, 184, 175))
    front = plan.intersection(box(ridge - 0.025, s - 1, nose, n + 1))

    def slope(x, y):
        return fascia + (nose - x) * (eave - fascia) / (nose - ridge)

    for panel in geometry.sections(front):
        parts.append(geometry.shell(panel, fascia - 0.135, slope, SHINGLE, SHINGLE))
    for x in np.arange(ridge + 0.20, nose - 0.05, 0.214):
        strip = front.intersection(box(x, s - 1, x + 0.026, n + 1))
        for panel in geometry.sections(strip):
            z = min(slope(*p) for p in panel.exterior.coords) - 0.03
            parts.append(
                geometry.shell(
                    panel,
                    z,
                    lambda e, n: slope(e, n) + 0.019,
                    (117, 112, 97),
                    (114, 107, 91),
                )
            )
    base.flat(parts, plan, floor, fascia - 0.12, GREEN)
    body = plan.intersection(box(w - 1, s - 1, ridge, n + 1))
    base.flat(parts, body, fascia - 0.16, eave - 0.001, MASONRY)
    edges = list(shared.face_edges(plan))
    for a, b in edges:
        length, add = tools.face(parts, a, b)
        if length < 4:
            continue
        if bearing(a, b)[0] > 0.93:
            add(0.04, length - 0.04, 0.012, 0.111, grade + 0.03, fascia - 0.15, DARK)
            add(0.075, length - 0.075, 0.114, 0.14, grade + 0.26, fascia - 0.26, GLASS)
            for u in np.arange(0.10, length - 0.05, 1.34):
                add(
                    u - 0.041,
                    u + 0.041,
                    0.137,
                    0.175,
                    grade + 0.024,
                    fascia - 0.13,
                    GREEN,
                )
            for z in (grade + 0.45, grade + 2.15, fascia - 0.19):
                add(0.025, length - 0.025, 0.141, 0.163, z - 0.044, z + 0.044, PALE)
            for u in np.linspace(2.18, length - 2.18, 4):
                hood_height = fascia + 2.73
                width = 1.7
                pt = np.asarray(a) + u * (np.asarray(b) - a) / length
                north = pt[1]
                # Tapered cheeks slope back to the shingle panel where it rises behind each hood.
                for side in (-1, 1):
                    lo, hi = north + side * width * 0.50, north + side * width * 0.26
                    shell = Polygon(
                        [
                            (nose - 0.76, hi),
                            (nose + 0.24, lo),
                            (nose + 0.21, lo + side * 0.14),
                            (nose - 0.77, hi + side * 0.14),
                        ]
                    )
                    parts.append(
                        geometry.shell(
                            shell,
                            fascia - 0.023,
                            lambda e, n: fascia + 0.23 + (nose + 0.27 - e) * 2.58,
                            PALE,
                            SHINGLE,
                        )
                    )
                    tools.beam(
                        parts,
                        (nose + 0.23, lo, fascia),
                        (nose - 0.76, hi, hood_height),
                        0.134,
                        PALE,
                    )
                tools.beam(
                    parts,
                    (nose - 0.76, north - width * 0.31, hood_height),
                    (nose - 0.76, north + width * 0.31, hood_height),
                    0.138,
                    PALE,
                )
                add(
                    u - width * 0.39,
                    u + width * 0.39,
                    0.175,
                    0.199,
                    fascia - 0.015,
                    fascia + 1.46,
                    DARK,
                )
        else:
            for u in bays(length, 3.30):
                window(add, u, min(length / 4, 1.57), grade + 0.98, 1.07)
    # The sign and ridgeline marker are part of the photographed upper silhouette.
    marker = box(-80.71, -669.75, -80.17, -669.23)
    base.flat(
        parts,
        marker,
        min(slope(*point) for point in marker.exterior.coords) - 0.05,
        eave + 0.72,
        SHINGLE,
    )
    tools.beam(
        parts,
        (-80.38, -669.51, eave + 0.70),
        (-80.38, -669.51, eave + 1.83),
        0.056,
        METAL,
    )
    tools.beam(
        parts,
        (-80.38, -669.92, eave + 1.44),
        (-80.38, -669.10, eave + 1.44),
        0.051,
        METAL,
    )
    prior.painted_doors(parts, edges, gates, PALE, DARK)


def build(spec, manifest, config, field, graph, recipes, fits):
    originals = {x["id"]: x for x in manifest["buildings"]}
    models, records, ground = {}, [], []
    plans, supports, gates = [], [], []
    for row in spec["models"]:
        id, kind = row["id"], row["kind"]
        outline = orient(Polygon(originals[id]["footprint_enu_m"]))
        plan = orient(outline.buffer(-row["wall_inset_m"], join_style="mitre"))
        assert outline.covers(plan)
        floor, grade = science.earlier.fit_base(field, outline)
        fit = fits[id]
        eave = fit["coefficients"][0]
        pieces, entries, blocks = [], [], []
        edges = list(shared.face_edges(plan))
        if kind in ("hayward", "aldersgate"):
            pieces.append(residential.source_cap(recipes[id]["cap"]))
            poly, blocks = gallery(
                pieces, [plan], field, row, grade, eave, floor, entries, ground
            )
        else:
            entries = [
                residential.entrance(ground, field, edges, hint)
                for hint in row["entrance_hints"]
            ]
            poly = [plan]
            if kind == "newman":
                newman(pieces, outline, plan, eave, grade, floor, entries)
            else:
                zones = divide(plan, fit)
                if fit["type"] == "step":
                    step_caps(pieces, outline, fit)
                else:
                    pieces.append(residential.source_cap(recipes[id]["cap"]))
                for area, z in zones:
                    base.flat(pieces, area, floor, z - 0.001, BODY[kind])

                def lookup(e, n):
                    mark = Point(e, n)
                    return min(zones, key=lambda item: item[0].distance(mark))[1]

                for a, b in edges:
                    if kind == "coho-south":
                        coho_south(pieces, a, b, grade, eave, entries)
                    elif kind == "agate":
                        agate(
                            pieces,
                            a,
                            b,
                            grade,
                            lookup(*np.mean([a, b], axis=0)),
                            entries,
                        )
                    else:
                        courtyard_facade(pieces, (a, b), grade, lookup, kind, entries)
                if kind == "christus":
                    stack = box(-477.23, -648.65, -476.02, -647.42)
                    base.flat(pieces, stack, floor, 21.73, (145, 95, 74))
                if kind != "agate":
                    prior.painted_doors(pieces, edges, entries, PALE, DARK)
        mesh = trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.000008))
        models[id] = science.ordered_mesh(mesh)
        plans.extend(poly)
        supports.extend(blocks)
        gates.extend(entries)
        records.append(
            {
                "id": id,
                "name": row["name"],
                "street_address": row["street_address"],
                "footprint_enu_m": base.ring(outline),
                "area_m2": round(sum(p.area for p in poly), 3),
                "ground_footprints_enu_m": [base.ring(p) for p in poly],
                "support_collision_enu_m": [base.ring(p) for p in blocks],
                "entrances": entries,
                "base_z_m": round(floor, 4),
                "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
            }
        )
    old = union_all([Polygon(originals[id]["footprint_enu_m"]) for id in models])
    route_count, clearance = prior.nearby.shared.graduate.shared.check_routes(
        plans, supports, gates, old, manifest, graph, config, set(models)
    )
    return (
        models,
        records,
        science.ordered_mesh(trimesh.util.concatenate(ground)),
        route_count,
        clearance,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--spec", type=Path, default=SPEC)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_bytes())
    manifest_path, config_path = SCENE / "manifest.json", SCENE / "presentation.json"
    manifest, config = [
        json.loads(path.read_bytes()) for path in (manifest_path, config_path)
    ]
    terrain = SCENE / manifest["heightfield_url"]
    fits_path = ROOT / "data/metadata/context-roof-refinements.json"
    recipe_path = SCENE / "context-roof-refinements.json"
    for path, key in (
        (manifest_path, "source_manifest_sha256"),
        (terrain, "source_heightfield_sha256"),
        (recipe_path, "source_roof_recipe_sha256"),
        (fits_path, "source_roof_fits_sha256"),
    ):
        if tools.digest(path) != spec[key]:
            raise ValueError(f"Neighborhood exterior source changed: {path.name}")
    roof_data = json.loads(recipe_path.read_bytes())
    if roof_data["source_presentation_sha256"] != config["asset_sha256"]:
        raise ValueError("Neighborhood roofs require the same active presentation.")
    recipes = {
        item["id"]: item
        for batch in roof_data["batches"]
        for item in batch["buildings"]
    }
    fits = {item["id"]: item for item in json.loads(fits_path.read_bytes())["fits"]}
    field = json.loads(terrain.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    models, records, ground, edges, clearance = build(
        spec, manifest, config, field, graph, recipes, fits
    )
    appearances = json.loads(
        (ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, appearances
    )
    assert all(row["triangles"] == recipes[row["id"]]["triangles"] for row in removals)
    output = args.stage or SCENE / DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    model, descriptor = output / "site.glb", output / "site.json"
    site.memorial.gerlinger.export(model, models, ground, GROUND, "neighborhood-paving")
    package = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{DIRECTORY}/site.glb",
        "sha256": tools.digest(model),
        "buildings": records,
        "absorbed_ids": [],
        "batch_removals": removals,
    }
    descriptor.write_text(
        json.dumps(package, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    if args.stage is None:
        config["campus_neighbor_exterior_site"] = {
            "url": f"{DIRECTORY}/site.json",
            "sha256": tools.digest(descriptor),
        }
        config_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf8",
            newline="\n",
        )
    audit = {
        "buildings": records,
        "route_edges": edges,
        "nearest_route_m": round(clearance, 4),
        "triangles": {key: len(mesh.faces) for key, mesh in models.items()},
        "batch_removals": removals,
        "glb_sha256": package["sha256"],
        "descriptor_sha256": tools.digest(descriptor),
    }
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(
        {
            key: audit[key]
            for key in ("route_edges", "nearest_route_m", "triangles", "glb_sha256")
        }
    )


if __name__ == "__main__":
    main()
