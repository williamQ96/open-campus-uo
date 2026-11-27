# SPDX-License-Identifier: Apache-2.0
"""Build the registered Fenton Hall exterior, entrances and collision envelope."""

import argparse
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-memorial-quad-site-review.py")
loader = spec_from_file_location(source.stem, source)
memorial = module_from_spec(loader)
loader.loader.exec_module(memorial)
tools, geometry = memorial.tools, memorial.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/fenton-site-review.json"
DIRECTORY = "fenton-site-review"
GROUND = "fenton-approaches"
HELLO_WALK = "fenton-hello-walk"
COURTYARD_SPEC = geometry.ROOT / "data/metadata/heritage-courtyard-landscape.json"
courtyard = import_module("build-heritage-courtyard-landscape")
BRICK = (161, 119, 89)
STACK_BRICK = (170, 140, 107)
BRICK_SHADE = (130, 92, 68)
BRICK_LIGHT = (180, 133, 94)
BASE = (150, 145, 128)
STONE = (193, 184, 161)
COPING = (184, 178, 155)
ROOF = (153, 157, 152)
SEAM = (143, 148, 144)
GLASS = (53, 80, 80)
FRAME = (81, 108, 102)
SHADOW = (89, 81, 69)
CONCRETE = (158, 153, 137)
SOIL = (102, 91, 71)
RAIL = (74, 82, 75)
flat, surface = memorial.flat, memorial.roof


def volumes(parts, spec, bottom):
    main = spec["main"]
    west, south, east, north = main["roof_bounds"]
    x = (west + east) / 2
    y0, y1 = main["ridge_northings"]
    eave, ridge = main["eave_z_m"], main["ridge_z_m"]
    rise = ridge - eave
    walls = box(*main["wall_bounds"])
    flat(parts, walls, bottom, eave, BRICK)
    roof_heel = eave - 0.21
    sw, se, ne, nw = (west, south), (east, south), (east, north), (west, north)
    a, b = (x, y0), (x, y1)
    facets = (
        ([sw, se, a], lambda e, n: eave + rise * (n - south) / (y0 - south), 0),
        ([se, ne, b, a], lambda e, n: eave + rise * (east - e) / (east - x), 1),
        ([ne, nw, b], lambda e, n: eave + rise * (north - n) / (north - y1), 0),
        ([nw, sw, a, b], lambda e, n: eave + rise * (e - west) / (x - west), 1),
    )
    for corners, height, axis in facets:
        face = Polygon(corners)
        surface(parts, face, roof_heel, height, SHADOW, ROOF)
        low, high = face.bounds[axis::2]
        for u in np.arange(low + 0.5, high, 0.58):
            line = [(u, south), (u, north)] if axis == 0 else [(west, u), (east, u)]
            rib = face.intersection(LineString(line).buffer(0.014, cap_style="flat"))
            surface(
                parts, rib, eave - 0.035, lambda e, n: height(e, n) + 0.023, SEAM, SEAM
            )
    for start, end in ((sw, a), (se, a), (ne, b), (nw, b), (a, b)):
        h0 = ridge if start == a else eave
        tools.beam(parts, (*start, h0 + 0.037), (*end, ridge + 0.037), 0.059, SEAM)

    _, east_height, _ = facets[1]
    skylight = box(*main["east_skylight_bounds"])
    surface(parts, skylight, eave, lambda e, n: east_height(e, n) + 0.13, FRAME, GLASS)
    min_x, min_y, max_x, max_y = skylight.bounds
    for n in (min_y, (min_y + max_y) / 2, max_y):
        tools.beam(
            parts,
            (min_x, n, east_height(min_x, n) + 0.16),
            (max_x, n, east_height(max_x, n) + 0.16),
            0.054,
            FRAME,
        )

    _, west_height, _ = facets[3]
    for e, n in ((-454.9, 30.95), (-455.8, 35.66)):
        region = box(e - 0.35, n - 0.38, e + 0.35, n + 0.38)
        z = west_height(e, n)
        flat(parts, region, z - 0.23, z + 0.58, STONE, COPING)

    flat(parts, box(*spec["entrance_projection"]), bottom, 17.53, BRICK, COPING)
    flat(parts, box(-436.4, 27.63, -435.22, 34.24), 17.42, 18.55, COPING, ROOF)
    flat(
        parts,
        box(*spec["connector"]["wall_bounds"]),
        bottom,
        spec["connector"]["roof_z_m"],
        BRICK,
    )
    for key in ("stacks", "tower"):
        item = spec[key]
        plan = box(*item["wall_bounds"])
        membrane, top = item["roof_z_m"], item["coping_z_m"]
        flat(
            parts,
            plan,
            bottom,
            membrane,
            STACK_BRICK if key == "stacks" else BRICK,
            (172, 166, 147),
        )
        rim = plan.difference(plan.buffer(-0.24, join_style="mitre"))
        flat(parts, rim, membrane - 0.11, top - 0.14, STACK_BRICK)
        flat(parts, rim.buffer(0.075, join_style="mitre"), top - 0.14, top, COPING)
    for e, n in ((-469.85, 31.39), (-468.40, 32.96)):
        flat(
            parts,
            box(e - 0.48, n - 0.39, e + 0.48, n + 0.39),
            spec["stacks"]["roof_z_m"] - 0.02,
            spec["stacks"]["roof_z_m"] + 0.51,
            STONE,
            ROOF,
        )


def window(add, center, width, low, high, quoins=False):
    left, right = center - width / 2, center + width / 2
    add(left - 0.105, right + 0.105, 0.004, 0.076, low - 0.10, high + 0.10, BRICK_SHADE)
    add(left, right, 0.077, 0.106, low, high, GLASS)
    mid = (low + high) / 2
    for u in (left + 0.022, center, right - 0.022):
        add(u - 0.027, u + 0.027, 0.106, 0.142, low, high, FRAME)
    for z in (low, mid, high):
        add(left, right, 0.110, 0.144, z - 0.029, z + 0.029, FRAME)
    add(left - 0.13, right + 0.13, 0.011, 0.183, low - 0.14, low - 0.061, STONE)
    if quoins:
        add(
            left - 0.107,
            right + 0.107,
            0.017,
            0.134,
            high + 0.051,
            high + 0.16,
            BRICK_LIGHT,
        )


def brackets(add, length, roof):
    add(0, length, 0.012, 0.73, roof - 0.19, roof, SHADOW)
    add(0, length, 0.013, 0.78, roof, roof + 0.115, COPING)
    count = max(1, round(length / 0.83))
    for u in (np.arange(count) + 0.5) * length / count:
        add(u - 0.085, u + 0.085, 0.034, 0.63, roof - 0.47, roof - 0.15, BRICK_LIGHT)


def door(add, center, width, threshold, height):
    left, right = center - width / 2, center + width / 2
    add(
        left - 0.065,
        right + 0.065,
        0.008,
        0.128,
        threshold,
        threshold + height + 0.09,
        STONE,
    )
    add(left, right, 0.129, 0.15, threshold, threshold + height, FRAME)
    for u in (left + 0.08, center + 0.029):
        for z, size in ((0.52, 0.48), (1.15, 0.76), (height - 0.47, 0.37)):
            add(
                u,
                u + width / 2 - 0.14,
                0.15,
                0.185,
                threshold + z,
                threshold + z + size,
                GLASS,
            )


def east_portal(parts, spec, threshold):
    west, south, east, north = spec["entrance_projection"]
    a, b = (east, south), (east, north)
    width, add = tools.face(parts, a, b)
    center = spec["entrances"][0]["position_enu_m"][1] - south
    brackets(add, width, 17.15)
    for side in (0, width - 0.59):
        add(side, side + 0.59, -0.01, 0.097, threshold, 16.83, BRICK)
        for i, z in enumerate(np.arange(threshold + 0.25, 16.8, 0.36)):
            add(
                side,
                side + (0.59 if i % 2 else 0.44),
                0.098,
                0.148,
                z,
                z + 0.059,
                BRICK_SHADE,
            )
    arch = memorial.museum.arch
    for arch_width, rise, offset, material in (
        (3.59, 1.84, 0.104, BRICK_LIGHT),
        (3.27, 1.69, 0.127, BRICK),
    ):
        outline = arch(south + center, arch_width, threshold, threshold + 4.12, rise)
        memorial.panel(parts, outline, east + offset, 0, 1, material)
    door(add, center, 1.76, threshold, 2.93)
    add(
        center - 1.14,
        center + 1.14,
        0.01,
        0.156,
        threshold + 3.28,
        threshold + 3.67,
        STONE,
    )
    add(center - 3.18, center + 3.18, 0.007, 0.12, 13.77, 14.03, BRICK_LIGHT)
    for offset, sash in ((-2.26, 1.19), (0, 2.87), (2.26, 1.19)):
        window(add, center + offset, sash, 11.46, 12.95)
    for u in (0.31, width - 0.31):
        add(u - 0.29, u + 0.29, -0.58, 0.095, 17.49, 18.36, BRICK_LIGHT)
        add(u - 0.34, u + 0.34, -0.65, 0.137, 18.36, 18.46, STONE)
    add(0.55, width - 0.55, -0.235, -0.105, 18.24, 18.36, STONE)
    for u in np.linspace(0.63, width - 0.63, 37):
        add(u - 0.039, u + 0.039, -0.208, -0.143, 17.53, 18.25, STONE)


def elevations(parts, spec, plan, bottom, thresholds):
    coords = list(orient(plan, sign=1).exterior.coords)
    main, stacks, tower = (
        spec[key]["wall_bounds"] for key in ("main", "stacks", "tower")
    )
    for a, b in zip(coords, coords[1:]):
        u, add = tools.face(parts, a, b)
        x, y = (np.asarray(a) + b) / 2
        if x == spec["entrance_projection"][2]:
            continue
        on_main = x >= main[0]
        on_stack = x <= stacks[2]
        on_tower = not on_main and tower[1] <= y <= tower[3]
        if on_main:
            brackets(add, u, 17.14)
            south_portal = (
                spec["entrances"][1]["position_enu_m"] if y == main[1] else None
            )
            door_center = south_portal[0] - a[0] if south_portal else None
            add(0, u, 0.003, 0.064, bottom, 6.48, BASE)
            band_spans = (
                ((0, door_center - 0.68), (door_center + 0.68, u))
                if south_portal
                else ((0, u),)
            )
            for left, right in band_spans:
                add(left, right, 0.007, 0.207, 6.39, 6.59, COPING)
            for v in (0, u - 0.54):
                for z in np.arange(6.7, 16.9, 0.36):
                    add(v, v + min(0.54, u), 0.003, 0.075, z, z + 0.075, BRICK_LIGHT)
            if u < 4:
                continue
            count = 4 if u > 15 else 2
            if a[0] == b[0] and a[0] == main[0]:
                count = 2 if u < 11 else 3
            for v in (np.arange(count) + 0.5) * u / count:
                xy = np.asarray(a) + (np.asarray(b) - a) * v / u
                is_entry = south_portal and abs(xy[0] - south_portal[0]) < 1.6
                if not is_entry:
                    window(add, v, 1.21, 4.44, 5.77)
                if x == main[2]:
                    memorial.quoin_arch(parts, a, b, v, 1.49, 8.26, 9.82, 0.71, GLASS)
                    add(v - 0.66, v + 0.66, 0.137, 0.165, 9.47, 9.54, FRAME)
                    add(v - 0.032, v + 0.032, 0.137, 0.169, 8.26, 10.36, FRAME)
                else:
                    window(add, v, 1.58, 8.49, 10.49, quoins=True)
                window(add, v, 1.62, 12.87, 14.96, quoins=True)
            if south_portal:
                door(add, door_center, 1.16, thresholds["fenton-south"], 2.30)
        elif on_stack or on_tower:
            coping = spec["stacks" if on_stack else "tower"]["coping_z_m"]
            add(0, u, 0, 0.175, coping - 2.27, coping - 1.99, STONE)
            add(0, u, 0, 0.27, coping - 1.98, coping - 1.77, BRICK_LIGHT)
            if u < 1.35:
                continue
            count = max(1, round(u / (1.60 if on_stack else 2.55)))
            for v in (np.arange(count) + 0.5) * u / count:
                rows = (
                    (5.00, 7.04, 9.08, 11.12, 13.15)
                    if on_stack
                    else (5.5, 8.03, 10.54, 13.04, 15.62)
                )
                for z in rows:
                    window(add, v, min(0.89, u * 0.62), z, z + 1.28)

    for a, b in ((tower[:2], (tower[2], tower[1])), (tower[2:], (tower[0], tower[3]))):
        u, add = tools.face(parts, a, b)
        add(0, u, 0, 0.121, 17.72, 17.94, STONE)
        for center in (u * 0.29, u * 0.69):
            window(add, center, 1.13, 16.49, 17.57)


def approaches(parts, spec, field):
    entries, blockers, heights = [], [], {}
    for entry in spec["entrances"]:
        east = entry["gate"] == "fenton-east"
        e, n = entry["position_enu_m"]
        length, halfwidth, steps = (2.70, 2.64, 5) if east else (3.65, 1.46, 9)
        low = geometry.sample_ground(
            field, e + length if east else e, n if east else n - length
        )
        high = low + (0.74 if east else 1.26)
        heights[entry["gate"]] = round(float(high), 3)
        for i in range(steps):
            depth = length - i * (length - 0.95) / (steps - 1)
            outline = (
                box(e - 0.02, n - halfwidth, e + depth, n + halfwidth)
                if east
                else box(e - halfwidth, n - depth, e + halfwidth, n + 0.02)
            )
            flat(
                parts,
                outline,
                low - 1.07,
                low + (i + 1) * (high - low) / steps,
                CONCRETE,
            )
            if i == 0:
                blockers.append(outline)
        apron = (
            box(e + length - 0.10, n - halfwidth, e + length + 2.05, n + halfwidth)
            if east
            else box(e - halfwidth, n - length - 1.28, e + halfwidth, n - length + 0.10)
        )
        entries.append({"outline": list(apron.exterior.coords), "rgb": CONCRETE})
        if east:
            for y in (n - halfwidth, n + halfwidth):
                cheek = box(e - 0.03, y - 0.16, e + 1.41, y + 0.16)
                flat(parts, cheek, low - 0.55, high + 0.36, BASE, COPING)
                blockers.append(cheek)
        else:
            for x in (e - halfwidth + 0.12, e + halfwidth - 0.12):
                start, end = n - 3.47, n - 1.08
                tools.beam(
                    parts, (x, start, low + 0.97), (x, end, high + 0.91), 0.048, RAIL
                )
                for frac in (0, 0.5, 1):
                    y = start + frac * (end - start)
                    top = low + 0.97 + frac * (high - low - 0.06)
                    flat(
                        parts,
                        box(x - 0.022, y - 0.022, x + 0.022, y + 0.022),
                        top - 0.99,
                        top,
                        RAIL,
                    )
    e, n = spec["entrances"][1]["position_enu_m"]
    for lo, hi in ((-454.76, e - 1.54), (e + 1.54, -437.04)):
        outline = box(lo, n - 3.53, hi, n - 0.78)
        top = geometry.sample_ground(field, (lo + hi) / 2, n - 3.65) + 0.73
        rim = outline.difference(outline.buffer(-0.24, join_style="mitre"))
        flat(parts, outline, top - 1.60, top - 0.14, CONCRETE, SOIL)
        flat(parts, rim, top - 0.17, top, COPING)
        blockers.append(outline)
        for x in np.arange(lo + 0.90, hi - 0.62, 1.55):
            for n_offset, radius, color in (
                (-2.11, 0.63, (90, 109, 68)),
                (-1.63, 0.45, (108, 120, 74)),
            ):
                shrub = trimesh.creation.icosphere(subdivisions=1)
                shrub.apply_scale([radius * 1.24, radius * 0.69, radius])
                shrub.apply_translation([x, top + 0.11, -n - n_offset])
                shrub.visual.vertex_colors = [*color, 255]
                parts.append(shrub)
    return entries, blockers, heights


def drinking_bubbler(parts, field, spec):
    e, n = spec["position_enu_m"]
    half = spec["pad_width_m"] / 2
    pad = box(e - half, n - half, e + half, n + half)
    grade = max(geometry.sample_ground(field, x, y) for x, y in pad.exterior.coords)
    base = grade + 0.08
    bronze = (125, 109, 79)
    rim = (151, 132, 94)
    flat(parts, pad, grade - 0.14, base, CONCRETE)

    def lathe(x, y, profile, color):
        mesh = trimesh.creation.revolve(profile, sections=24)
        mesh.apply_transform(
            trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])
        )
        mesh.apply_translation([x, base, -y])
        mesh.visual.vertex_colors = [*color, 255]
        parts.append(mesh)

    lathe(
        e,
        n,
        [
            [0, 0],
            [0.20, 0],
            [0.20, 0.13],
            [0.177, 0.15],
            [0.18, 0.185],
            [0.137, 0.225],
            [0.096, 0.33],
            [0.079, 0.52],
            [0.099, 0.62],
            [0.141, 0.64],
            [0.147, 0.79],
            [0.126, 0.83],
            [0, 0.83],
        ],
        bronze,
    )
    for angle in np.arange(12) * np.pi / 6:
        x, y = np.cos(angle), np.sin(angle)
        tools.beam(
            parts,
            (e + 0.112 * x, n + 0.112 * y, base + 0.269),
            (e + 0.076 * x, n + 0.076 * y, base + 0.57),
            0.018,
            (148, 127, 88),
        )
    t = np.linspace(0, 1, 11)
    collar, throat, elbow, bowl = np.array(
        [[0.12, 0.72], [0.265, 0.698], [0.35, 0.734], [0.349, 0.91]]
    )
    curve = (
        (1 - t)[:, None] ** 3 * collar
        + (3 * (1 - t) ** 2 * t)[:, None] * throat
        + (3 * (1 - t) * t**2)[:, None] * elbow
        + t[:, None] ** 3 * bowl
    )
    arm_profile = Point(0, 0).buffer(0.045, quad_segs=3)
    for x, y in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        points = [
            [e + x * dist, base + height, -n - y * dist] for dist, height in curve
        ]
        arm = trimesh.creation.sweep_polygon(arm_profile, points, cap=False)
        arm.visual.vertex_colors = [*bronze, 255]
        parts.append(arm)
        cx, cy = e + 0.349 * x, n + 0.349 * y
        lathe(
            cx,
            cy,
            [
                [0, 0.898],
                [0.053, 0.898],
                [0.062, 0.92],
                [0.096, 0.942],
                [0.136, 0.985],
                [0.141, 1.003],
                [0.116, 0.999],
                [0.085, 0.963],
                [0, 0.953],
            ],
            rim,
        )
        lathe(
            cx,
            cy,
            [[0, 0.954], [0.026, 0.954], [0.024, 0.981], [0.014, 0.995], [0, 0.999]],
            (151, 158, 151),
        )
    reach = spec["reach_m"]
    return box(e - reach, n - reach, e + reach, n + reach)


def north_landscape(parts, field, spec, occupied, graph):
    west, south, east, north = spec["fountain_bounds_enu_m"]
    shoulder, step = spec["fountain_shoulder_m"]
    outer = box(west, south + step, east, north - step).union(
        box(west + shoulder, south, east - shoulder, north)
    )
    inner = outer.buffer(-0.19, join_style="mitre")
    center = outer.centroid
    e, n = center.coords[0]
    grade = max(
        geometry.sample_ground(field, x, y) for x, y in [*outer.exterior.coords, (e, n)]
    )
    flat(parts, outer.difference(inner), grade - 0.35, grade + 0.22, STONE, COPING)
    # The adjacent campus lawn overlay sits 0.04 m above the heightfield.
    flat(parts, inner, grade - 0.12, grade + 0.075, (92, 89, 69))
    for x, y in ((e - 0.26, n), (e + 0.26, n), (e, n - 0.26), (e, n + 0.26)):
        tools.beam(parts, (x, y, grade + 0.075), (e, n, grade + 0.39), 0.112, STONE)
    bowl, lip = center.buffer(0.39, quad_segs=12), center.buffer(0.285, quad_segs=12)
    flat(parts, bowl, grade + 0.37, grade + 0.44, STONE)
    flat(parts, bowl.difference(lip), grade + 0.43, grade + 0.48, COPING)
    flat(parts, lip, grade + 0.44, grade + 0.449, (125, 120, 90))
    flat(parts, center.buffer(0.047), grade + 0.445, grade + 0.455, (70, 68, 57))
    bubbler = drinking_bubbler(parts, field, spec["drinking_bubbler"])
    points = spec["hello_walk_centerline_enu_m"]
    anchor = spec["hello_walk_anchor_enu_m"]
    centerline = LineString(points)
    walk = centerline.buffer(spec["hello_walk_width_m"] / 2, cap_style="flat")
    fixtures = outer.union(bubbler)
    assert walk.distance(fixtures) > 0.40
    assert not occupied.intersects(walk.union(fixtures))
    nodes = graph["nodes_enu_m"]
    assert anchor in nodes
    route = LineString([anchor, *points])
    assert route.distance(occupied) >= 0.50
    assert all(
        0.05 < np.linalg.norm(np.subtract(a, b)) < 20
        for a, b in zip(route.coords, list(route.coords)[1:])
    )
    assert all(
        LineString([nodes[a], nodes[b]]).distance(fixtures) > 0.50
        for a, b, *_ in graph["edges"]
    )
    west, south, east, north = walk.bounds
    middle = (south + north) / 2
    access = {
        "bounds_enu_m": [[west, south, east, middle], [west, middle, east, north]],
        "anchor_enu_m": anchor,
        "points_enu_m": points,
    }
    return walk, outer, bubbler, access, route.length


def build(spec, court_spec, manifest, field, graph):
    plan = union_all(
        [
            box(*spec[key]["wall_bounds"])
            for key in ("main", "stacks", "tower", "connector")
        ]
        + [box(*spec["entrance_projection"])]
    )
    assert plan.is_valid and plan.geom_type == "Polygon"
    for entry in spec["entrances"]:
        assert plan.exterior.distance(Point(entry["position_enu_m"])) < 0.001
    bottom = round(
        min(
            geometry.sample_ground(field, *plan.exterior.interpolate(u).coords[0])
            for u in np.arange(0, plan.exterior.length, 0.4)
        )
        - 0.36,
        3,
    )
    parts = []
    volumes(parts, spec, bottom)
    approach_parts = []
    entries, blockers, thresholds = approaches(approach_parts, spec, field)
    east_portal(parts, spec, thresholds["fenton-east"])
    elevations(parts, spec, plan, bottom, thresholds)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
    occupied = union_all([plan, *blockers])
    walk, fountain, bubbler, access, route_length = north_landscape(
        approach_parts, field, spec["north_landscape"], occupied, graph
    )
    approach_parts.append(tools.approaches(entries, field, occupied))
    path_parts = [
        tools.approaches(
            [{"outline": list(walk.exterior.coords), "rgb": CONCRETE}], field, occupied
        )
    ]
    south_edge_count = len(access["points_enu_m"])
    access, furniture, court_audit = courtyard.landscape(
        court_spec, SCENE, field, access, path_parts, approach_parts
    )

    prior = next(b for b in manifest["buildings"] if b["id"] == spec["id"])
    previous = Polygon(prior["footprint_enu_m"])
    for b in manifest["buildings"]:
        if b["id"] != spec["id"]:
            neighbor = Polygon(b["footprint_enu_m"]).buffer(0)
            assert (
                occupied.intersection(neighbor).area < 0.02
                and walk.intersection(neighbor).area < 0.02
            ), b["id"]
    conflicts = []
    for index, (a, b, *_) in enumerate(graph["edges"]):
        edge = LineString([graph["nodes_enu_m"][a], graph["nodes_enu_m"][b]])
        if edge.distance(occupied) < 0.42 <= edge.distance(previous):
            conflicts.append(index)
    assert not conflicts, conflicts
    record = {
        "id": spec["id"],
        "footprint_enu_m": list(plan.exterior.coords)[:-1],
        "area_m2": round(plan.area, 2),
        "base_z_m": bottom,
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "support_collision_enu_m": [list(p.exterior.coords)[:-1] for p in blockers],
        "entrances": [
            entry | {"threshold_z_m": thresholds[entry["gate"]]}
            for entry in spec["entrances"]
        ],
    }
    return (
        record,
        mesh,
        trimesh.util.concatenate(approach_parts),
        trimesh.util.concatenate(path_parts),
        access,
        [fountain.bounds, bubbler.bounds, *furniture],
        {
            "route_edges": len(graph["edges"]),
            "new_conflicts": conflicts,
            "fountain_bounds_enu_m": fountain.bounds,
            "bubbler_bounds_enu_m": bubbler.bounds,
            "hello_walk_area_m2": round(walk.area, 2),
            "hello_walk_route_m": round(route_length, 2),
            "hello_walk_added_edges": south_edge_count,
            "heritage_courtyard": court_audit,
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    court_spec = json.loads(COURTYARD_SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    record, mesh, ground, path, access, fixtures, audit = build(
        spec, court_spec, manifest, json.loads(field_path.read_bytes()), graph
    )
    assert record["id"] in config["replaces_building_ids"]
    destination = args.stage or SCENE / DIRECTORY
    destination.mkdir(parents=True, exist_ok=True)
    model = destination / "site.glb"
    memorial.gerlinger.export(
        model,
        {record["id"]: mesh},
        ground,
        GROUND,
        "fenton-paving",
        walkable={HELLO_WALK: path},
    )
    site = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": tools.digest(field_path),
        "source_navigation_sha256": tools.digest(SCENE / "navigation.json"),
        "url": f"{DIRECTORY}/site.glb",
        "sha256": tools.digest(model),
        "ground_node": GROUND,
        "buildings": [record],
        "closed_site_boxes_enu_m": fixtures,
        "walkable_ground": access,
        "context_trees": court_spec["context_trees"],
    }
    site_path = destination / "site.json"
    site_path.write_text(
        json.dumps(site, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n"
    )
    if args.stage is None:
        config["fenton_site_review"] = {
            "url": f"{DIRECTORY}/site.json",
            "sha256": tools.digest(site_path),
        }
        config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    audit.update(
        footprint_m2=record["area_m2"],
        model_sha256=site["sha256"],
        site_sha256=tools.digest(site_path),
        triangles=[len(mesh.faces), len(ground.faces)],
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
