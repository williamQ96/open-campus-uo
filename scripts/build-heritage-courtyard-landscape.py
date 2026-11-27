# SPDX-License-Identifier: Apache-2.0
"""Build the registered Heritage Project landscape and connect it to Hello Walk."""

from importlib import import_module

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

site = import_module("build-pioneer-cemetery-landscape-review")
heritage = import_module("build-heritage-core-site-review")
CONCRETE = (181, 179, 164)
ASPHALT = (130, 130, 116)
RAIL = (69, 76, 67)
WOOD = (124, 105, 78)
GREEN = (47, 83, 62)
SOIL = (110, 86, 64)
FOLIAGE = ((79, 105, 60), (96, 119, 68), (109, 126, 72))


def south_entry(walkable, detail, field, spec):
    e, n = spec["position_enu_m"]
    foot = spec["first_tread_north_m"]
    half = spec["width_m"] / 2
    landing = n - spec["landing_depth_m"]
    base = site.ground_height(field, e, foot) + 0.097
    top = max(base + spec["rise_m"], site.ground_height(field, e, n) + 0.18)
    run = landing - foot
    count = spec["treads"]
    site.solid(
        walkable, box(e - half, landing, e + half, n), base - 0.33, top, CONCRETE
    )
    for i in range(count):
        tread_n = foot + i * run / count
        z = base + (top - base) * (i + 1) / count
        site.solid(
            walkable,
            box(e - half, tread_n, e + half, landing),
            base - 0.33,
            z,
            CONCRETE,
        )
    barriers = []
    for x, rail_end in (
        (e - half + 0.07, landing - 0.29),
        (e + half - 0.07, landing + 0.12),
    ):
        site.beam(
            detail,
            (x, foot + 0.11, base + 1.00),
            (x, rail_end, top + 0.86),
            0.047,
            RAIL,
        )
        barriers.append(box(x - 0.027, foot + 0.11, x + 0.027, rail_end))
        for frac in (0.04, 0.53, 1.0):
            y = foot + frac * (rail_end - foot)
            z = base + 0.96 + frac * (top - base - 0.10)
            site.beam(detail, (x, y, z - 0.91), (x, y, z), 0.042, RAIL)

    west, south, east, north = spec["ramp_bounds_enu_m"]
    low = site.ground_height(field, west, (south + north) / 2) + 0.10
    ramp = box(west, south, east, north)

    def height(x, _):
        return low + (top - low) * (x - west) / (east - west)

    heritage.surface(walkable, ramp, min(low, top) - 0.32, height, CONCRETE, CONCRETE)
    for y in (south, north):
        site.beam(detail, (west, y, low + 0.89), (east, y, top + 0.89), 0.043, RAIL)
        barriers.append(box(west, y - 0.025, east, y + 0.025))
        for x in np.linspace(west + 0.12, east - 0.12, 6):
            z = height(x, y)
            site.beam(detail, (x, y, z), (x, y, z + 0.89), 0.042, RAIL)
    site.solid(
        walkable, box(east, south, e - half + 0.02, north), base - 0.28, top, CONCRETE
    )
    a, b = (e - 2.5, n), (e + 2.5, n)
    frame = heritage.arch(2.5, 2.39, top, top + 3.24)
    heritage.profile(detail, a, b, frame, 0.223, (139, 138, 126))
    heritage.profile(
        detail, a, b, heritage.arch(2.5, 1.93, top, top + 2.97), 0.240, (64, 64, 54)
    )
    for x in (e - 0.46, e + 0.46):
        site.flat_box(detail, x, n - 0.256, 0.88, 0.069, top, top + 2.15, (103, 65, 53))
        site.flat_box(
            detail, x, n - 0.297, 0.62, 0.022, top + 0.92, top + 2.02, (62, 79, 71)
        )
    apron = box(e - half - 0.35, foot - 2.97, e + half + 0.35, foot + 0.013).union(
        box(west - 2.24, south - 2.0, west + 0.02, north)
    )
    return apron, top, barriers


def hall_sign(parts, field, center):
    e, n = center
    base = site.ground_height(field, e, n)
    for x in (e - 0.55, e + 0.55):
        site.flat_box(parts, x, n, 0.079, 0.079, base - 0.07, base + 0.96, GREEN)
    site.flat_box(parts, e, n, 1.46, 0.085, base + 0.46, base + 0.98, GREEN)
    for y in (base + 0.47, base + 0.96):
        site.flat_box(parts, e, n, 1.48, 0.087, y, y + 0.017, (129, 144, 117))
    title = "UNIVERSITY HALL"
    glyphs = site.GLYPHS | {"V": (((0, 1), (0.5, 0), (1, 1)),)}
    for i, letter in enumerate(title):
        if letter == " ":
            continue
        for stroke in glyphs[letter]:
            points = [
                (
                    e + (i - (len(title) - 1) / 2) * 0.089 + (x - 0.5) * 0.074,
                    n - 0.046,
                    base + 0.643 + y * 0.105,
                )
                for x, y in stroke
            ]
            for a, b in zip(points, points[1:]):
                site.beam(parts, a, b, 0.006, (220, 224, 193))
    return box(e - 0.73, n - 0.045, e + 0.73, n + 0.045)


def bench(parts, field, center):
    e, n = center
    z = site.ground_height(field, e, n)
    for x in (e - 0.67, e + 0.67):
        site.flat_box(parts, x, n, 0.07, 0.39, z - 0.08, z + 0.45, RAIL)
        site.flat_box(parts, x, n + 0.2, 0.059, 0.09, z + 0.36, z + 0.89, RAIL)
    for y in np.linspace(n - 0.16, n + 0.16, 5):
        site.flat_box(parts, e, y, 1.62, 0.067, z + 0.43, z + 0.48, WOOD)
    for h in (0.58, 0.72, 0.86):
        site.flat_box(parts, e, n + 0.19, 1.63, 0.055, z + h, z + h + 0.095, WOOD)
    return box(e - 0.82, n - 0.2, e + 0.82, n + 0.24)


def landscape(spec, scene, field, base_access, walkable, detail):
    neighboring_path = scene / "heritage-miller-review/site.json"
    assert site.pin(neighboring_path) == spec["neighbor_descriptor_sha256"]
    buildings = site.read(neighboring_path)["buildings"]
    hall_envelope = unary_union(
        [
            Polygon(ring).buffer(0.02)
            for building in buildings
            for ring in [
                building["footprint_enu_m"],
                *building.get("support_collision_enu_m", []),
            ]
        ]
    )
    paths = []
    available = {tuple(p) for p in base_access["points_enu_m"]}
    for row in spec["route_paths"]:
        anchor, points = row["anchor_enu_m"], row["points_enu_m"]
        assert tuple(anchor) in available
        end = row.get("end_enu_m")
        if end:
            assert tuple(end) in available
        nodes = [anchor, *points, *([end] if end else [])]
        route = LineString(nodes)
        assert route.distance(hall_envelope) >= 0.50
        assert all(
            0.05 < np.linalg.norm(np.subtract(a, b)) < 20
            for a, b in zip(nodes, nodes[1:])
        )
        paths.append(route.buffer(row["width_m"] / 2, cap_style="flat"))
        available.update(map(tuple, points))

    entry, landing, barriers = south_entry(walkable, detail, field, spec["south_entry"])
    lanes = unary_union(paths)
    beds = [
        box(*bounds).buffer(-0.27).buffer(0.27) for bounds in spec["bed_bounds_enu_m"]
    ]
    placements = unary_union(beds).difference(hall_envelope.union(lanes.buffer(0.17)))
    patio = Polygon(spec["patio_enu_m"])
    paved = lanes.union(patio).union(entry).difference(hall_envelope.union(placements))
    assert all(
        paved.covers(Point(tree["position_enu_m"])) for tree in spec["context_trees"]
    )
    parking = Polygon(spec["parking_enu_m"]).difference(paved.union(hall_envelope))
    site.drape(walkable, field, paved, CONCRETE, 0.097, 0.90)
    site.drape(walkable, field, parking, ASPHALT, 0.093, 0.95)
    for e in np.arange(-466.72, -454.25, 2.42):
        line = site.landscape.rect_on((e, 138.3), (e, 143.23), 0.087)
        marking = line.intersection(parking)
        if marking.area > 0:
            site.drape(detail, field, marking, (199, 198, 182), 0.109, 0.82)

    site.drape(detail, field, placements, SOIL, 0.073, 0.76)
    for i, bed in enumerate(beds):
        x0, y0, x1, y1 = bed.bounds
        for x in np.arange(x0 + 0.54, x1, 0.94):
            for y in np.arange(y0 + 0.52, y1, 0.94):
                if not placements.contains(Point(x, y)):
                    continue
                z = site.ground_height(field, x, y)
                radius = 0.30 + (i % 3) * 0.06
                site.orb(
                    detail,
                    (x, y, z + 0.18),
                    (radius, radius * 0.9, radius * 0.82),
                    FOLIAGE[i % 3],
                )
    for i, (e, n) in enumerate(spec["new_tree_positions_enu_m"]):
        assert placements.contains(Point(e, n))
        z = site.ground_height(field, e, n)
        site.cylinder_between(
            detail, (e, n, z - 0.09), (e, n, z + 3.23), 0.091, (98, 80, 56)
        )
        for x, y, h in ((0, 0, 3.55), (0.46, -0.37, 3.16), (-0.44, 0.32, 2.97)):
            site.orb(detail, (e + x, n + y, z + h), (0.91, 0.77, 1.06), FOLIAGE[i % 3])
    obstacles = [*barriers, hall_sign(detail, field, spec["university_sign_enu_m"])]
    obstacles.extend(bench(detail, field, center) for center in spec["benches_enu_m"])
    for e, n in spec["lamps_enu_m"]:
        z = site.ground_height(field, e, n)
        site.flat_box(detail, e, n, 0.32, 0.31, z - 0.1, z + 0.22, GREEN)
        site.cylinder_between(detail, (e, n, z), (e, n, z + 2.54), 0.056, GREEN)
        site.orb(detail, (e, n, z + 2.68), (0.129, 0.124, 0.198), (222, 225, 202))
        obstacles.append(box(e - 0.16, n - 0.155, e + 0.16, n + 0.155))
    for row in spec["route_paths"]:
        points = [row["anchor_enu_m"], *row["points_enu_m"]]
        if end := row.get("end_enu_m"):
            points.append(end)
        assert LineString(points).distance(unary_union(obstacles)) >= 0.52
    x0, y0, x1, y1 = paved.union(parking).bounds
    split = (y0 + y1) / 2
    access = {
        "bounds_enu_m": [
            *base_access["bounds_enu_m"],
            [x0, y0, x1, split],
            [x0, split, x1, y1],
        ],
        "paths": [
            {k: v for k, v in base_access.items() if k != "bounds_enu_m"},
            *[
                {k: v for k, v in row.items() if k != "width_m"}
                for row in spec["route_paths"]
            ],
        ],
    }
    audit = {
        "paved_m2": round(paved.area, 2),
        "parking_m2": round(parking.area, 2),
        "planted_m2": round(placements.area, 2),
        "young_trees": len(spec["new_tree_positions_enu_m"]),
        "stair_landing_z_m": round(float(landing), 3),
        "steps": spec["south_entry"]["treads"],
        "new_edges": sum(
            len(row["points_enu_m"]) + bool(row.get("end_enu_m"))
            for row in spec["route_paths"]
        ),
    }
    return access, [shape.bounds for shape in obstacles], audit
