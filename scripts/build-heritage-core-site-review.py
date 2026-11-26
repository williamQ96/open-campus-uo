# SPDX-License-Identifier: Apache-2.0
"""Build the University and Villard Hall exteriors and their modeled entrances."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-memorial-quad-site-review.py")
loader = spec_from_file_location(source.stem, source)
memorial = module_from_spec(loader)
loader.loader.exec_module(memorial)
tools, geometry = memorial.tools, memorial.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/heritage-core-site-review.json"
DIRECTORY = "heritage-core-review"
GROUND = "heritage-core-approaches"

U_WALL = (122, 117, 108)
U_BAND = (151, 147, 135)
U_SHADE = (99, 96, 87)
V_WALL = (170, 157, 136)
V_BAND = (198, 184, 160)
V_SHADE = (136, 124, 109)
SLATE = (129, 133, 129)
CAP = (161, 163, 153)
IRON = (75, 79, 71)
GLASS = (54, 77, 83)
WOOD = (103, 65, 56)
CONCRETE = (170, 166, 151)
SOIL = (112, 97, 79)
flat, surface = memorial.flat, memorial.roof


def corners(bounds):
    x0, y0, x1, y1 = bounds[:4]
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def roof_segment(parts, lower, upper, limit, rgb, courses=False):
    base, top = corners(lower), corners(upper)
    for i, j in ((0, 1), (1, 2), (2, 3), (3, 0)):
        quad = Polygon([base[i], base[j], top[j], top[i]]).intersection(limit)
        axis = 1 - i % 2
        run = top[i][axis] - base[i][axis]

        def height(e, n):
            progress = ((e, n)[axis] - base[i][axis]) / run
            return lower[4] + progress * (upper[4] - lower[4])

        surface(parts, quad, lower[4] - 0.15, height, SLATE, rgb)
        if courses:
            lo, hi = sorted((base[i][axis], top[i][axis]))
            for v in np.arange(lo + 0.27, hi - 0.08, 0.27):
                span = (
                    box(v - 0.008, -999, v + 0.008, 999)
                    if axis == 0
                    else box(-999, v - 0.008, 999, v + 0.008)
                )
                surface(
                    parts,
                    quad.intersection(span),
                    lower[4] - 0.12,
                    lambda e, n: height(e, n) + 0.012,
                    SLATE,
                    (122, 126, 122),
                )


def mansard(parts, shape, limit):
    lower, turn, upper = (shape[key] for key in ("eave", "break", "cap"))
    roof_segment(parts, lower, turn, limit, SLATE, courses=True)
    roof_segment(parts, turn, upper, limit, (148, 150, 141))
    flat(parts, box(*upper[:4]), upper[4] - 0.15, upper[4] + 0.055, CAP)


def crest(parts, cap, full):
    z = cap[-1] + 0.11
    frame = corners(cap)
    edges = zip(frame, frame[1:] + frame[:1])
    for i, (a, b) in enumerate(edges):
        if not full and i % 2:
            continue
        a, b = np.array(a), np.array(b)
        length = np.linalg.norm(b - a)
        ui = (b - a) / length
        count = max(1, int(length / 0.32))
        tools.beam(parts, (*a, z), (*b, z), 0.047, IRON)
        tools.beam(parts, (*a, z + 0.25), (*b, z + 0.25), 0.04, IRON)
        for offset in np.linspace(0, length, count + 1):
            pt = a + offset * ui
            tools.beam(parts, (*pt, z - 0.05), (*pt, z + 0.32), 0.034, IRON)
        for j, offset in enumerate(np.linspace(0, length, count + 1)[:-1]):
            pt = a + offset * ui
            end = pt + (length / count) * ui
            start_z, end_z = (z, z + 0.25) if j % 2 else (z + 0.25, z)
            tools.beam(parts, (*pt, start_z), (*end, end_z), 0.026, IRON)


def profile(parts, a, b, outline, offset, rgb):
    _, point = memorial.coordinate(a, b)
    vertices = []
    for tri in shapely.constrained_delaunay_triangles(outline).geoms:
        for u, z in list(orient(tri).exterior.coords)[:3]:
            e, n = point(u, offset)
            vertices.append((e, z, -n))
    if vertices:
        mesh = trimesh.Trimesh(
            vertices, np.arange(len(vertices)).reshape(-1, 3), process=False
        )
        mesh.visual.vertex_colors = [*rgb, 255]
        parts.append(mesh)


def arch(center, width, low, high):
    rise = width * 0.5
    return memorial.museum.arch(center, width, low, high - rise, rise)


def arched(parts, a, b, u, width, low, high, band, shade, is_door=False):
    outer = arch(u, width + 0.34, low - 0.10, high + 0.19)
    inner = arch(u, width, low, high)
    profile(parts, a, b, outer, 0.068, shade)
    profile(parts, a, b, outer.difference(inner), 0.104, band)
    profile(parts, a, b, inner, 0.087, GLASS)
    _, add = tools.face(parts, a, b)
    add(
        u - width / 2 - 0.17,
        u + width / 2 + 0.17,
        0.024,
        0.194,
        low - 0.14,
        low - 0.028,
        band,
    )
    if is_door:
        add(
            u - width * 0.48,
            u + width * 0.48,
            0.104,
            0.15,
            low,
            min(high - 0.42, low + 2.35),
            WOOD,
        )
        for x in (u - width * 0.25, u + width * 0.25):
            add(
                x - width * 0.17,
                x + width * 0.17,
                0.15,
                0.17,
                low + 0.63,
                low + 2.17,
                GLASS,
            )
    else:
        add(u - 0.031, u + 0.031, 0.092, 0.141, low, high - 0.063, IRON)
    split = high - (width / 2 if is_door else (high - low) * 0.44)
    add(
        u - width / 2 + 0.029,
        u + width / 2 - 0.029,
        0.093,
        0.143,
        split - 0.046,
        split + 0.046,
        IRON,
    )


def rectangular(add, center, width, lo, hi, band):
    left, right = center - width / 2, center + width / 2
    add(left - 0.15, right + 0.15, 0.028, 0.117, lo - 0.12, hi + 0.13, band)
    add(left, right, 0.118, 0.139, lo, hi, GLASS)
    add(center - 0.024, center + 0.024, 0.14, 0.171, lo, hi, WOOD)
    z = (lo + hi) / 2
    add(left, right, 0.14, 0.176, z - 0.035, z + 0.035, WOOD)


def cornice(add, length, z, trim, shade, width=0.44):
    add(0, length, -0.018, width, z - 0.20, z, trim)
    add(0, length, 0.01, width - 0.08, z - 0.30, z - 0.20, shade)
    count = max(1, round(length / 0.73))
    for u in (np.arange(count) + 0.5) * length / count:
        radius = min(0.092, length / 3)
        add(u - radius, u + radius, 0.027, width - 0.07, z - 0.67, z - 0.25, trim)


def relief(add, length, top, tone, spacing, width):
    for z in np.arange(4.8, top, spacing):
        for a in (0, max(0, length - width)):
            add(a, a + min(width, length), 0.006, 0.053, z, z + 0.070, tone)


def round_window(parts, a, b, u, z, radius, band):
    opening = Point(u, z).buffer(radius, quad_segs=8)
    profile(parts, a, b, opening.buffer(0.14), 0.125, band)
    profile(parts, a, b, opening, 0.139, GLASS)


def university(parts, plan, model, base, thresholds):
    main = model["roof"]
    flat(parts, plan, base, main["eave"][4], U_WALL)
    mansard(parts, main, plan.buffer(0.54, join_style="mitre"))
    gates = {g["position_enu_m"][0]: g for g in model["entrances"]}
    coords = list(orient(plan).exterior.coords)
    for a, b in zip(coords, coords[1:]):
        u, add = tools.face(parts, a, b)
        gate = gates.get(a[0]) if a[0] == b[0] else None
        for z in (8.1, 13.58):
            spans = [(0, u)]
            if gate and thresholds[gate["gate"]] < z < 13.0:
                center = abs(gate["position_enu_m"][1] - a[1])
                spans = [(0, center - 1.25), (center + 1.25, u)]
            for lo, hi in spans:
                add(lo, hi, 0.017, 0.19, z - 0.079, z + 0.089, U_BAND)
                if z > 13:
                    count = max(1, int((hi - lo) / 0.37))
                    radius = min(0.046, (hi - lo) / 3)
                    for dj in (np.arange(count) + 0.5) * (hi - lo) / count:
                        x = lo + dj
                        add(
                            x - radius,
                            x + radius,
                            0.012,
                            0.13,
                            z - 0.26,
                            z - 0.086,
                            U_SHADE,
                        )
        if not gate:
            cornice(add, u, 19.07, U_BAND, U_SHADE)
        if u < 2.55:
            continue
        if gate:
            center = abs(gate["position_enu_m"][1] - a[1])
            threshold = thresholds[gate["gate"]]
            arched(parts, a, b, center, 2.12, threshold, 13.02, U_BAND, U_SHADE, True)
            arched(parts, a, b, center, 2.03, 14.52, 18.18, U_BAND, U_SHADE)
            for x in (0.32, u - 0.32):
                add(x - 0.11, x + 0.11, 0.011, 0.085, threshold, 18.73, U_BAND)
            continue
        count = max(1, round(u / 3.82))
        for v in np.linspace(0.18, u - 0.18, count + 1):
            add(v - 0.13, v + 0.13, 0.018, 0.14, 4.43, 18.85, (136, 132, 121))
        for x in (np.arange(count) + 0.5) * u / count:
            arched(parts, a, b, x, 0.93, max(base + 0.75, 5.32), 7.66, U_BAND, U_SHADE)
            arched(parts, a, b, x, 1.34, 9.12, 12.97, U_BAND, U_SHADE)
            arched(parts, a, b, x, 1.34, 14.58, 18.03, U_BAND, U_SHADE)

    for tower, side in zip(model["towers"], (-1, 1)):
        eave = tower["eave"]
        left, low, right, high, z = eave
        tower_plan = plan.intersection(
            box(left + 0.38, low + 0.47, right - 0.35, high - 0.55)
        )
        flat(parts, tower_plan, 18.91, z, U_WALL)
        mansard(parts, tower, box(*eave[:4]))
        crest(parts, tower["cap"], True)
        ring = list(orient(tower_plan).exterior.coords)
        for a, b in zip(ring, ring[1:]):
            length, add = tools.face(parts, a, b)
            if length < 1.0:
                continue
            cornice(add, length, z + 0.035, U_BAND, U_SHADE, width=0.43)
            if length < 3.0:
                continue
            outward = (b[1] - a[1]) * side > length * 0.90
            for local in ([-1.37, 0.0, 1.37] if outward else [0.0]):
                arched(
                    parts, a, b, length / 2 + local, 0.76, 20.43, 24.26, U_BAND, U_SHADE
                )
            if outward or abs(b[0] - a[0]) > length * 0.9:
                tower_dormer(parts, a, b, box(*tower["break"][:4]), z)
    for side in (-1, 1):
        for e in np.arange(-464.83, -442.8, 3.82):
            university_dormer(parts, e, 114.41 if side < 0 else 133.17, side)
    for e, n, height in (
        (-464.38, 125.2, 26.39),
        (-453.9, 130.54, 26.28),
        (-446.3, 129.95, 26.03),
        (-451.72, 116.79, 26.07),
    ):
        flat(parts, box(e - 0.44, n - 0.39, e + 0.44, n + 0.39), 23.57, height, U_WALL)


def university_dormer(parts, e, n, side):
    front = n - side * 0.63
    parts_end = n - side * 2.37
    e0, e1 = e - 0.71, e + 0.71
    base = box(e0, min(front, parts_end), e1, max(front, parts_end))
    flat(parts, base, 19.59, 22.77, U_WALL)
    a, b = ((e0, front), (e1, front)) if side < 0 else ((e1, front), (e0, front))
    arched(parts, a, b, 0.71, 0.93, 20.16, 22.36, U_BAND, U_SHADE)
    pent = Polygon([(0, 22.59), (1.42, 22.59), (0.71, 23.51)])
    profile(parts, a, b, pent, 0.09, SLATE)
    tools.beam(parts, (e0 - 0.07, front, 22.64), (e, front, 23.54), 0.11, U_BAND)
    tools.beam(parts, (e, front, 23.54), (e1 + 0.07, front, 22.64), 0.11, U_BAND)


def tower_dormer(parts, a, b, upper, z):
    length, at = memorial.coordinate(a, b)
    mid = length / 2
    vertices = [
        at(mid - 0.66, 0.17),
        at(mid + 0.66, 0.17),
        at(mid + 0.66, -2.1),
        at(mid - 0.66, -2.1),
    ]
    outline = Polygon(vertices)
    if not outline.intersects(upper):
        return
    flat(parts, outline, z - 0.09, z + 2.54, SLATE)
    aa, bb = vertices[:2]
    arched(parts, aa, bb, 0.66, 0.95, z + 0.24, z + 2.24, U_BAND, U_SHADE)
    front = Polygon([(0, z + 2.41), (1.32, z + 2.41), (0.66, z + 2.97)])
    profile(parts, aa, bb, front, 0.09, U_BAND)


def villard_east(parts, model, threshold):
    x, n = model["entrances"][0]["position_enu_m"]
    a, b = (x, 173.29), (x, 196.56)
    length, add = tools.face(parts, a, b)
    center = n - a[1]
    balcony = box(x - 0.10, n - 6.23, x + 1.43, n + 6.23)
    flat(parts, balcony, 11.13, 11.65, V_BAND, CAP)
    for u in np.linspace(center - 5.86, center + 5.86, 10):
        add(u - 0.079, u + 0.079, 0.11, 1.35, 10.84, 11.15, V_SHADE)
    add(center - 6.34, center + 6.34, 0.015, 1.36, 20.96, 21.22, V_BAND)
    for u in np.linspace(center - 6.01, center + 6.01, 38):
        add(u - 0.049, u + 0.049, 1.12, 1.31, 21.13, 21.73, V_BAND)
    add(center - 6.22, center + 6.22, 1.06, 1.37, 21.72, 21.88, V_BAND)
    for p in (center - 5.87, center + 5.87):
        for q in (p - 0.21, p + 0.21):
            add(q - 0.125, q + 0.125, 0.015, 0.33, 11.75, 17.32, V_BAND)
    for z in (11.12, 17.19, 19.26):
        add(center - 6.48, center + 6.48, 0.023, 0.39, z - 0.09, z + 0.12, V_BAND)
    for u in (center - 4.36, center, center + 4.36):
        is_door = u == center
        arched(
            parts,
            a,
            b,
            u,
            1.72 if is_door else 1.57,
            threshold if is_door else 6.60,
            10.33,
            V_BAND,
            V_SHADE,
            is_door,
        )
        if is_door:
            add(u - 0.96, u + 0.96, 0.034, 0.11, 12.34, 16.78, V_SHADE)
            add(u - 0.82, u + 0.82, 0.113, 0.14, 12.48, 16.64, (183, 170, 146))
        else:
            rectangular(add, u, 1.71, 12.47, 16.75, V_BAND)
        round_window(parts, a, b, u, 17.81, 0.49, V_BAND)
        profile(
            parts,
            a,
            b,
            arch(u, 2.25, 17.04, 19.07).difference(arch(u, 1.90, 17.04, 18.87)),
            0.20,
            V_BAND,
        )
    for u in (center - 5.68, center - 1.95, center + 1.95, center + 5.68):
        add(u - 0.12, u + 0.12, 0.026, 0.277, 12.16, 16.91, V_BAND)
        add(u - 0.20, u + 0.20, 0.059, 0.34, 16.86, 17.05, V_BAND)
    cornice(add, length, 21.12, V_BAND, V_SHADE)


def villard(parts, plan, model, base, thresholds):
    main = model["roof"]
    flat(parts, plan, base, main["eave"][4], V_WALL)
    mansard(parts, main, plan.buffer(0.58, join_style="mitre"))
    crest(parts, main["cap"], False)
    coords = list(orient(plan).exterior.coords)
    for a, b in zip(coords, coords[1:]):
        length, add = tools.face(parts, a, b)
        if length <= 1.05:
            continue
        x, y = (np.asarray(a) + b) / 2
        corner = y < 173.29 or y > 196.50
        if x > -439 and not corner:
            continue
        cornice(add, length, 21.09, V_BAND, V_SHADE)
        if corner:
            for z in np.arange(5.65, 20.67, 0.63):
                add(0, length, 0.006, 0.068, z, z + 0.062, V_BAND)
        else:
            relief(add, length, 20.70, V_BAND, 0.80, 0.38)
        for z in (5.95, 11.32, 19.82):
            add(0, length, 0.02, 0.18, z - 0.112, z + 0.11, V_BAND)
        if length < 3.01:
            continue
        count = max(1, round(length / (4.15 if corner else 3.1)))
        for u in (np.arange(count) + 0.5) * length / count:
            arched(parts, a, b, u, 1.55, 6.77, 10.53, V_BAND, V_SHADE)
            rectangular(add, u, 1.63, 12.46, 16.59, V_BAND)
            if corner:
                profile(
                    parts,
                    a,
                    b,
                    Polygon([(u - 1.25, 16.60), (u + 1.25, 16.60), (u, 17.61)]),
                    0.18,
                    V_BAND,
                )
            else:
                round_window(parts, a, b, u, 17.85, 0.43, V_BAND)
    villard_east(parts, model, thresholds["villard-east"])
    for i, tower in enumerate(model["towers"]):
        eave = tower["eave"]
        x0, n0, x1, n1, z = eave
        mansard(parts, tower, box(*eave[:4]))
        crest(parts, tower["cap"], True)
        x = x1 - 0.20 if i % 2 else x0 + 0.20
        a, b = ((x, n0), (x, n1)) if i % 2 else ((x, n1), (x, n0))
        center = (n1 - n0) / 2
        _, add = tools.face(parts, a, b)
        add(center - 0.78, center + 0.78, -0.45, 0.11, z - 0.05, z + 0.56, V_BAND)
        round_window(parts, a, b, center, z + 0.88, 0.43, V_BAND)


def entry_steps(parts, field, gate, wide):
    e, n = gate["position_enu_m"]
    direction = -1 if gate["outward_degrees"] < 0 else 1
    length, half, number = (4.35, 1.72, 13) if wide else (3.47, 1.74, 6)
    ground = geometry.sample_ground(field, e + direction * length, n)
    top = float(ground + (2.24 if wide else 0.95))

    def rectangle(u, v, south, north):
        x0, x1 = sorted((e + u * direction, e + v * direction))
        return box(x0, n + south, x1, n + north)

    blocks = [rectangle(-0.024, length, -half, half)]
    for i in range(number):
        depth = length - i * (length - 0.81) / (number - 1)
        height = ground + (i + 1) / number * (top - ground)
        flat(
            parts, rectangle(-0.02, depth, -half, half), ground - 0.91, height, CONCRETE
        )
    for sign in (-1, 1):
        edge = sign * (half + 0.082)
        if wide:
            wall = rectangle(-0.022, length - 0.29, edge - 0.084, edge + 0.084)

            def height(x, y):
                u = (x - e) * direction
                return (
                    top
                    + 0.30
                    - np.clip((u - 0.80) / (length - 1.09), 0, 1)
                    * (top - ground - 0.23)
                )

            surface(parts, wall, ground - 0.42, height, CONCRETE, (193, 190, 172))
            blocks.append(wall)
        y = n + sign * (half - 0.133)
        at = e + direction * 0.86
        end = e + direction * (length - 0.33)
        tools.beam(parts, (at, y, top + 0.82), (end, y, ground + 0.99), 0.047, IRON)
        for frac in (0, 0.5, 1):
            x = at + frac * (end - at)
            z = top + 0.82 + frac * (ground + 0.17 - top)
            tools.beam(parts, (x, y, z - 0.89), (x, y, z), 0.043, IRON)
    paved = rectangle(length - 0.075, length + 2.65, -half - 0.20, half + 0.20)
    for sign in (-1, 1):
        start, end = sorted((sign * (half + 0.34), sign * (5.0 if wide else 6.50)))
        bed = rectangle(0.80, length + 0.19, start, end)
        rim = bed.difference(bed.buffer(-0.13, join_style="mitre"))
        z = ground + (0.30 if wide else 0.42)
        flat(parts, bed, ground - 0.73, z, CONCRETE, SOIL)
        flat(parts, rim, z - 0.04, z + 0.13, (185, 179, 161))
        blocks.append(bed)
        for span in np.arange(start + 0.7, end - 0.39, 1.00):
            for step, radius in ((1.53, 0.43), (2.74, 0.51), (length - 0.43, 0.35)):
                plant = trimesh.creation.icosphere(subdivisions=1)
                plant.apply_scale([radius, radius * 0.81, radius * 1.13])
                plant.apply_translation([e + direction * step, z + 0.04, -n - span])
                plant.visual.vertex_colors = [102, 114, 77, 255]
                parts.append(plant)
    return (
        blocks,
        {"outline": list(paved.exterior.coords), "rgb": CONCRETE},
        round(top, 3),
    )


def build(spec, manifest, config, graph, field, include_temporary_joint=True):
    records, buildings, occupied, approaches, paving = [], {}, [], [], []
    prior = []
    theater = "roof-944fcd46"
    local = {item["id"]: item for item in manifest["buildings"]}
    for key, method in (("university", university), ("villard", villard)):
        model = spec[key]
        plan = Polygon(model["footprint_enu_m"])
        assert plan.is_valid
        previous = Polygon(local[model["id"]]["footprint_enu_m"])
        prior.append(previous)
        base = round(
            min(
                geometry.sample_ground(field, *plan.exterior.interpolate(u).coords[0])
                for u in np.arange(0, plan.exterior.length, 0.47)
            )
            - 0.34,
            3,
        )
        footprint = [plan]
        thresholds, collision = {}, []
        for gate in model["entrances"]:
            assert plan.exterior.distance(Point(gate["position_enu_m"])) < 0.001
            steps, apron, high = entry_steps(
                approaches, field, gate, key == "university"
            )
            collision.extend(steps)
            paving.append(apron)
            thresholds[gate["gate"]] = high
        if key == "villard" and include_temporary_joint:
            theater_join = box(*model["west_join_bounds"])
            theater_plan = Polygon(local[theater]["footprint_enu_m"])
            assert theater_join.intersects(theater_plan) and theater_join.touches(plan)
            membrane = model["west_join_roof_z_m"]
            flat(approaches, theater_join, base - 0.45, membrane, (167, 152, 131), CAP)
            flat(
                approaches,
                theater_join.difference(theater_join.buffer(-0.16)),
                membrane - 0.08,
                membrane + 0.26,
                (164, 153, 136),
                CAP,
            )
            for n, side in ((theater_join.bounds[1], -1), (theater_join.bounds[3], 1)):
                lo = theater_join.bounds[0] + 1.25
                hi = theater_join.bounds[2] - 1.08
                a, b = ((lo, n), (hi, n)) if side < 0 else ((hi, n), (lo, n))
                width, add = tools.face(approaches, a, b)
                for u in np.linspace(0.65, width - 0.65, 5):
                    rectangular(add, u, 1.11, base + 0.70, membrane - 1.32, V_SHADE)
            collision.extend(geometry.sections(theater_join.difference(theater_plan)))
        parts = []
        method(parts, plan, model, base, thresholds)
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        buildings[model["id"]] = mesh
        footprint.extend(collision)
        occupied.append(shapely.union_all(footprint))
        records.append(
            {
                "id": model["id"],
                "footprint_enu_m": model["footprint_enu_m"],
                "area_m2": round(plan.area, 2),
                "base_z_m": base,
                "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
                "support_collision_enu_m": [
                    list(p.exterior.coords)[:-1] for p in collision
                ],
                "entrances": [
                    g | {"threshold_z_m": thresholds[g["gate"]]}
                    for g in model["entrances"]
                ],
            }
        )
    block, old = shapely.union_all(occupied), shapely.union_all(prior)
    for item in records:
        for gate in item["entrances"]:
            e, n = gate["position_enu_m"]
            distance = gate["approach_distance_m"]
            assert 0 < distance < 5, gate["gate"]
            angle = np.deg2rad(gate["outward_degrees"])
            approach = Point(e + distance * np.sin(angle), n + distance * np.cos(angle))
            assert approach.distance(block) >= 0.5, gate["gate"]
    for bid, item in local.items():
        if bid not in buildings:
            assert (
                Polygon(item["footprint_enu_m"]).buffer(0).intersection(block).area
                < 0.02
            ), bid
    conflicts = []
    for i, (a, b, *_) in enumerate(graph["edges"]):
        edge = LineString([graph["nodes_enu_m"][a], graph["nodes_enu_m"][b]])
        if edge.distance(block) < 0.42 <= edge.distance(old):
            conflicts.append(i)
    assert not conflicts, conflicts
    assert set(buildings) <= set(config["replaces_building_ids"])
    approaches.append(tools.approaches(paving, field, block))
    ground = trimesh.util.concatenate(approaches)
    return (
        records,
        buildings,
        ground,
        {"route_edges": len(graph["edges"]), "new_conflicts": conflicts},
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    records, buildings, ground, audit = build(
        spec, manifest, config, graph, json.loads(field_path.read_bytes())
    )
    directory = SCENE / DIRECTORY
    directory.mkdir(exist_ok=True)
    glb = directory / "site.glb"
    memorial.gerlinger.export(glb, buildings, ground, GROUND, "heritage-core-paving")
    site = directory / "site.json"
    site.write_text(
        json.dumps(
            {
                "source_presentation_sha256": config["asset_sha256"],
                "source_base_model_sha256": manifest["model"]["sha256"],
                "source_heightfield_sha256": tools.digest(field_path),
                "url": f"{DIRECTORY}/site.glb",
                "sha256": tools.digest(glb),
                "ground_node": GROUND,
                "buildings": records,
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf8",
        newline="\n",
    )
    config["heritage_core_site"] = {
        "url": f"{DIRECTORY}/site.json",
        "sha256": tools.digest(site),
    }
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit.update(
        footprints={r["id"]: r["area_m2"] for r in records},
        model_sha256=tools.digest(glb),
        descriptor_sha256=tools.digest(site),
        triangles={name: len(mesh.faces) for name, mesh in buildings.items()}
        | {GROUND: len(ground.faces)},
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
