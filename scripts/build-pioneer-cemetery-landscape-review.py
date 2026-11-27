# SPDX-License-Identifier: Apache-2.0
"""Rebuild the documented paths and landmarks in Eugene Pioneer Cemetery."""

import argparse
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
import trimesh

landscape = import_module("build-hamilton-dunes-review")
frontage = import_module("build-onyx-university-frontages-review")
fairmount = landscape.fairmount
geometry = landscape.geometry
beam = fairmount.beam
root, scene = fairmount.ROOT, fairmount.SCENE

PACKAGE = "pioneer-cemetery-landscape-review"
GROUND = "pioneer-cemetery-paving"
STAIR = "pioneer-cemetery-east-stairs"
DETAILS = "pioneer-cemetery-monuments"
CANOPY = "pioneer-cemetery-canopy"

GRAVEL = (166, 152, 119)
SHOULDER = (137, 135, 104)
CONCRETE = (179, 170, 148)
STONE = (137, 134, 120)
STONE_DARK = (104, 105, 92)
IRON = (81, 77, 65)
MARBLE = (162, 168, 160)
SOIL = (119, 103, 82)
GLYPHS = {
    **frontage.GLYPHS,
    "0": frontage.GLYPHS["O"],
    "A": (((0, 0), (0.50, 1), (1, 0)), ((0.23, 0.46), (0.77, 0.46))),
    "B": (
        ((0, 0), (0, 1), (0.77, 1), (0.98, 0.83), (0.71, 0.55), (0, 0.55)),
        ((0.71, 0.55), (1, 0.34), (0.86, 0), (0, 0)),
    ),
    "C": (
        (
            (0.92, 0.92),
            (0.71, 1),
            (0.24, 1),
            (0, 0.77),
            (0, 0.23),
            (0.25, 0),
            (0.75, 0),
            (1, 0.17),
        ),
    ),
    "D": (
        (
            (0, 0),
            (0, 1),
            (0.55, 1),
            (0.91, 0.80),
            (0.98, 0.52),
            (0.89, 0.19),
            (0.55, 0),
            (0, 0),
        ),
    ),
    "F": (((0, 0), (0, 1), (1, 1)), ((0, 0.53), (0.82, 0.53))),
    "G": (
        (
            (0.96, 0.86),
            (0.78, 1),
            (0.25, 1),
            (0, 0.77),
            (0, 0.24),
            (0.25, 0),
            (1, 0),
            (1, 0.44),
            (0.58, 0.44),
        ),
    ),
    "K": (((0, 0), (0, 1)), ((1, 1), (0, 0.45), (1, 0))),
    "L": (((0, 1), (0, 0), (1, 0)),),
    "M": (((0, 0), (0, 1), (0.5, 0.43), (1, 1), (1, 0)),),
    "P": (((0, 0), (0, 1), (0.78, 1), (1, 0.80), (0.78, 0.56), (0, 0.56)),),
    "Q": (
        (
            (0.32, 0),
            (0.09, 0.19),
            (0.01, 0.48),
            (0.09, 0.81),
            (0.32, 1),
            (0.69, 1),
            (0.91, 0.81),
            (0.99, 0.48),
            (0.91, 0.19),
            (0.69, 0),
            (0.32, 0),
        ),
        ((0.62, 0.25), (1, -0.04)),
    ),
    "V": (((0, 1), (0.50, 0), (1, 1)),),
    "2": (((0, 0.78), (0.20, 1), (0.79, 1), (1, 0.75), (0.86, 0.50), (0, 0), (1, 0)),),
    "4": (((0.73, 0), (0.73, 1), (0, 0.29), (1, 0.29)),),
    "5": (
        (
            (1, 1),
            (0.1, 1),
            (0.03, 0.53),
            (0.73, 0.53),
            (0.96, 0.38),
            (0.90, 0.15),
            (0.69, 0),
            (0.06, 0.05),
        ),
    ),
    "7": (((0, 1), (1, 1), (0.32, 0)),),
    "8": (
        (
            (0.82, 0.5),
            (1, 0.70),
            (0.83, 1),
            (0.18, 1),
            (0, 0.70),
            (0.18, 0.5),
            (0.82, 0.5),
            (1, 0.30),
            (0.82, 0),
            (0.18, 0),
            (0, 0.30),
            (0.18, 0.5),
        ),
    ),
    ".": (((0.52, 0), (0.52, 0.085)),),
}


def read(path):
    return json.loads(path.read_bytes())


def pin(path):
    return sha256(path.read_bytes()).hexdigest()


def ground_height(field, e, n):
    return landscape.absolute_grade(field, e, n)


def solid(parts, shape, bottom, top, color):
    parts.append(landscape.cap(shape, bottom, top, color))


def flat_box(parts, e, n, width, depth, bottom, top, color):
    solid(
        parts,
        box(e - width / 2, n - depth / 2, e + width / 2, n + depth / 2),
        bottom,
        top,
        color,
    )


def drape(parts, field, shape, color, lift, cell):
    landscape.top_surface(
        parts, shape, lambda e, n: ground_height(field, e, n) + lift, color, cell=cell
    )


def named_paths(parts, field, spec):
    centerlines = [
        (LineString(row["centerline_enu_m"]), row["width_m"]) for row in spec["roads"]
    ]
    bases = [line.buffer(width / 2, cap_style="flat") for line, width in centerlines]
    roads = unary_union(bases)
    approach = Polygon(spec["northwest_refinement"]["west_approach_outline_enu_m"])
    paving = roads.union(approach)
    areas = Polygon(spec["parcel"]["outline_enu_m"])
    shoulders = paving.buffer(0.43).difference(paving).intersection(areas)
    drape(parts, field, roads.difference(approach), GRAVEL, 0.082, 2.0)
    drape(parts, field, approach, (146, 143, 132), 0.096, 1.10)
    drape(parts, field, shoulders, SHOULDER, 0.058, 2.0)
    return paving


def rankin_frontage(parts, field, spec):
    frontage = spec["rankin_fringe"]["sidewalk"]
    line = LineString(frontage["centerline_enu_m"])
    footprint = line.buffer(frontage["width_m"] / 2, cap_style="flat")
    walls = [
        LineString(row).buffer(0.20, cap_style="flat")
        for row in spec["southern_walls"]
    ]
    footprint = footprint.difference(unary_union(walls))
    drape(parts, field, footprint, (150, 147, 134), 0.097, 1.12)
    return footprint.area, [
        unary_union(walls[:2]).bounds,
        unary_union(walls[2:]).bounds,
    ]


def branch_lengths(registered, paths, paving, obstacles):
    available = set(map(tuple, registered))
    lengths = []
    for path in paths:
        assert tuple(path["anchor_enu_m"]) in available
        points = [path["anchor_enu_m"], *path["points_enu_m"]]
        if "end_enu_m" in path:
            assert tuple(path["end_enu_m"]) in available
            points.append(path["end_enu_m"])
        spans = np.linalg.norm(np.diff(points, axis=0), axis=1)
        assert all(0.05 < span < 20 for span in spans)
        line = LineString(points)
        assert line.distance(obstacles) > 0.56
        assert line.difference(paving.buffer(0.13)).length < 0.40
        lengths.append(round(line.length, 2))
        available.update(map(tuple, path["points_enu_m"]))
    return lengths


def internal_landscape(paving, details, field, spec, main_paths):
    curbs = []
    previous = spec["grave_plot_edges"]
    additions = [
        *spec["perimeter_refinement"]["grave_plot_edges"],
        *spec["northwest_refinement"]["grave_plot_edges"],
    ]
    for index, row in enumerate([*previous, *additions]):
        points = row["points_enu_m"]
        line = LineString([*points, points[0]] if row["closed"] else points)
        material = CONCRETE if row["material"] == "concrete" else STONE
        curb = line.buffer(0.105, cap_style="flat", join_style="mitre")
        assert not curb.intersects(main_paths)
        if index >= len(previous):
            assert all(curb.distance(existing) > 0.22 for existing in curbs)
        curbs.append(curb)
        for a, b in zip(line.coords, list(line.coords)[1:]):
            span = LineString([a, b])
            count = max(1, int(np.ceil(span.length / 1.4)))
            for i in range(count):
                part = LineString(
                    [
                        span.interpolate(i / count, normalized=True),
                        span.interpolate((i + 1) / count, normalized=True),
                    ]
                )
                mesh = landscape.cap(
                    part.buffer(0.105, cap_style="flat"), -0.05, 0.14, material
                )
                mesh.vertices[:, 1] += [
                    ground_height(field, e, -z) for e, _, z in mesh.vertices
                ]
                details.append(mesh)
    alleys = []
    for row in spec["inner_alleys"]:
        center = LineString(row["centerline_enu_m"])
        strip = center.buffer(row["width_m"] / 2, cap_style="flat")
        alley = strip.difference(unary_union([main_paths, *curbs]).buffer(0.1))
        assert alley.area / strip.area >= 0.85
        drape(paving, field, alley, (147, 159, 112), 0.086, 1.15)
        alleys.append(alley)
    return unary_union(alleys), sum(edge.area for edge in curbs)


def northwest_planting(ground, field, spec, paving):
    info = spec["northwest_refinement"]
    trail = info["short_grass_track"]
    trace = LineString(trail["centerline_enu_m"])
    grass = trace.buffer(trail["width_m"] / 2, cap_style="flat").difference(
        paving.buffer(0.24)
    )
    drape(ground, field, grass, (152, 154, 112), 0.079, 0.84)
    ivy = []
    for outline in info["north_ivy_outlines_enu_m"]:
        patch = Polygon(outline).difference(paving.buffer(0.62))
        assert patch.is_valid and patch.area > 3
        drape(ground, field, patch, (105, 131, 76), 0.069, 0.64)
        ivy.append(patch)
    return {
        "west_approach_m2": round(Polygon(info["west_approach_outline_enu_m"]).area, 2),
        "grass_trace_m": round(trace.length, 2),
        "grass_trace_m2": round(grass.area, 2),
        "ivy_m2": round(sum(patch.area for patch in ivy), 2),
    }


def perimeter_landscape(ground, details, field, spec, paving, alleys):
    info = spec["perimeter_refinement"]
    parcel = Polygon(spec["parcel"]["outline_enu_m"])
    street = read(root / "data/metadata/university-south-axis.json")
    west = [(e, n) for n, e, _ in street["west_walk"]]
    east = [(e, n) for n, _, e in reversed(street["west_walk"])]
    sidewalk = Polygon([*west, *east])
    stair = spec["east_stair"]
    landing = box(
        stair["top_east_m"] - 0.78,
        stair["north_m"] - 1.38,
        stair["bottom_east_m"] + 0.16,
        stair["north_m"] + 1.38,
    )
    rankin = spec["rankin_fringe"]["sidewalk"]
    frontage = LineString(rankin["centerline_enu_m"]).buffer(
        rankin["width_m"] / 2, cap_style="flat"
    )
    clear = unary_union([paving.buffer(0.43), alleys, sidewalk, landing, frontage])
    keep_open = clear.union(
        unary_union([Polygon(x) for x in street["approach_paving"]])
    ).buffer(0.12)

    corner = info["corner_return"]
    width = corner["width_m"]
    wall_points = corner["points_enu_m"]
    wall = LineString(wall_points)
    wall_footprint = wall.buffer(width / 2 + 0.025)
    assert wall_footprint.distance(clear) > 0.21
    for a, b, rise in zip(wall_points, wall_points[1:], corner["rises_m"]):
        foot = landscape.rect_on(a, b, width)
        cap = LineString([a, b]).buffer(width / 2 + 0.025, cap_style="square")
        for shape, bottom, top, color in (
            (foot, -0.22, rise - 0.064, (176, 173, 161)),
            (cap, rise - 0.064, rise, (155, 153, 138)),
        ):
            mesh = landscape.cap(shape, bottom, top, color)
            mesh.vertices[:, 1] += [
                ground_height(field, e + 0.12, -z) for e, _, z in mesh.vertices
            ]
            details.append(mesh)

    grass = np.array([160, 183, 118])
    palettes = {
        "open": (168, 174, 117),
        "dry": (172, 169, 119),
        "grove": (153, 153, 109),
    }
    planted = Polygon()
    areas = {}
    for row in info["verge_zones"]:
        zone = (
            Polygon(row["outline_enu_m"])
            .intersection(parcel)
            .difference(keep_open.union(wall_footprint).union(planted))
        )
        assert zone.is_valid and zone.area > 10
        begin = len(ground)
        drape(ground, field, zone, grass, 0.068, 0.95)
        xy = ground[begin].vertices[:, [0, 2]]
        points = [Point(e, -z) for e, z in xy]
        strength = np.minimum([p.distance(zone.boundary) for p in points], 1.0)
        variation = np.sin(xy[:, 0] * 0.91 + xy[:, 1] * 0.63)[:, None] * 2.8
        delta = np.array(palettes[row["mood"]]) - grass
        ground[begin].visual.vertex_colors[:, :3] = np.rint(
            grass + strength[:, None] * (delta + variation)
        ).astype(np.uint8)
        planted = planted.union(zone)
        areas[row["id"]] = round(zone.area, 2)

    established = [
        Point(row["position_enu_m"])
        for row in [
            *spec["heritage_rose_positions"],
            *spec["charles_lawson_roses"]["placements"],
        ]
    ]
    leaves = (
        (91, 115, 68),
        (111, 128, 75),
        (94, 112, 69),
        (105, 123, 73),
        (113, 131, 80),
        (121, 135, 79),
    )
    for index, row in enumerate(info["low_planting"]):
        e, n = row["position_enu_m"]
        center = Point(e, n)
        radius, height = row["radius_m"], row["height_m"]
        assert keep_open.distance(center) > radius
        assert parcel.covers(center.buffer(radius))
        assert min(center.distance(p) for p in established) > radius + 1.0
        z = ground_height(field, e, n)
        for i, color in enumerate(leaves):
            angle = index * 1.37 + i * 2 * np.pi / 5
            offset = radius * 0.43 if i < 5 else 0.0
            x, y = e + offset * np.cos(angle), n + offset * np.sin(angle)
            top = height * (0.55 if i < 5 else 0.71)
            cylinder_between(
                details,
                (e, n, z - 0.03),
                (x, y, z + top),
                0.024,
                (100, 89, 71),
                sides=6,
            )
            orb(
                details,
                (x, y, z + top),
                (radius * 0.55, radius * 0.52, height * 0.29),
                color,
            )
    return {
        "verge_areas_m2": areas,
        "corner_return_length_m": round(wall.length, 2),
        "low_planting": len(info["low_planting"]),
    }


def support_structures(paved, details, field, spec, paths):
    info = spec["support_structures"]
    maintenance = box(*info["maintenance_roof_bounds_enu_m"])
    shelter = box(*info["shelter_roof_bounds_enu_m"])
    apron = Polygon(info["apron_enu_m"]).difference(
        unary_union([maintenance, shelter, paths]).buffer(0.06)
    )
    drape(paved, field, apron, (136, 130, 112), 0.074, 1.35)
    wx, sy, ex, ny = maintenance.bounds
    e, n = maintenance.centroid.coords[0]
    base = ground_height(field, e, n)
    eave = base + 2.66
    wall = maintenance.buffer(-0.44, join_style="mitre")
    solid(details, wall, base - 0.48, eave - 0.04, (149, 145, 125))
    solid(details, maintenance, eave - 0.11, eave, (110, 112, 107))
    a, b = (wx + 2.5, n), (ex - 2.5, n)
    roof_regions = (
        (Polygon([(wx, sy), (ex, sy), b, a]), lambda x, y: (y - sy) / (n - sy)),
        (Polygon([(ex, sy), (ex, ny), b]), lambda x, y: (ex - x) / (ex - b[0])),
        (Polygon([(ex, ny), (wx, ny), a, b]), lambda x, y: (ny - y) / (ny - n)),
        (Polygon([(wx, ny), (wx, sy), a]), lambda x, y: (x - wx) / (a[0] - wx)),
    )
    for i, (face, rise) in enumerate(roof_regions):
        shade = (124 + i * 2, 126 + i * 2, 118 + i * 2)
        landscape.top_surface(
            details, face, lambda x, y, r=rise: eave + 1.22 * r(x, y), shade, cell=1.4
        )
    for x in (e - 2.68, e - 1.07):
        flat_box(
            details, x, ny - 0.445, 0.84, 0.06, base + 0.13, base + 2.13, (78, 83, 76)
        )
    for x in (e + 1.26, e + 2.52):
        flat_box(
            details, x, ny - 0.439, 0.46, 0.068, base + 1.08, base + 1.86, (91, 101, 97)
        )
    wx, sy, ex, ny = shelter.bounds
    e, n = shelter.centroid.coords[0]
    base = ground_height(field, e, n)
    eave = base + 3.2
    posts = [
        box(x - 0.07, y - 0.07, x + 0.07, y + 0.07)
        for x in (wx + 0.38, e, ex - 0.38)
        for y in (sy + 0.31, ny - 0.31)
    ]
    for post in posts:
        solid(details, post, base - 0.27, eave, (101, 88, 69))
    for a, b in ((sy, n), (n, ny)):

        def top(x, y):
            return eave + 1.06 * (1 - abs(y - n) / (n - sy))

        landscape.top_surface(
            details, box(wx, a, ex, b), top, (112, 119, 111), cell=1.15
        )
        for x in np.linspace(wx + 0.3, ex - 0.28, 16):
            beam(
                details,
                (x, a, top(x, a) + 0.013),
                (x, b, top(x, b) + 0.013),
                0.019,
                (100, 109, 102),
            )
    beam(details, (wx, n, eave + 1.06), (ex, n, eave + 1.06), 0.044, (137, 144, 130))
    for y in (sy + 0.31, ny - 0.31):
        beam(details, (wx, y, eave - 0.14), (ex, y, eave - 0.14), 0.082, (102, 89, 72))
    return [list(shape.bounds) for shape in [wall, *posts]], apron.area


def stairs(paved, parts, field, spec):
    center = spec["north_m"]
    stop, start = spec["top_east_m"], spec["bottom_east_m"]
    half = spec["width_m"] / 2
    taper = 0.05
    lower_profile = ground_height(field, start + 0.05, center) + 0.049
    upper_profile = ground_height(field, stop, center) + 0.082
    rise = (upper_profile - lower_profile) / spec["treads"]
    supports = []
    cuts = np.linspace(start, stop, spec["treads"] + 1)
    for i, (a, b) in enumerate(zip(cuts, cuts[1:])):
        land = box(b - 0.008, center - half, a + 0.004, center + half)
        z = max(lower_profile + (i + 1) * rise, ground_height(field, b, center) + taper)
        support = min(ground_height(field, a, center), z) - 0.30
        solid(paved, land, support, z, CONCRETE if i % 3 else (174, 166, 144))
        if i in (0, 3, 7, spec["treads"] - 1):
            supports.append((a, z))
    for e in (start, stop):
        land = box(
            e - 0.72 if e == stop else e,
            center - half,
            e if e == stop else e + 0.75,
            center + half,
        )
        drape(paved, field, land, CONCRETE, 0.10 if e == stop else 0.056, 0.50)
    for sign in (-1, 1):
        north = center + sign * (half - 0.06)
        post_caps = [(e, north, z + spec["rail_height_m"]) for e, z in supports]
        for cap, (_, height) in zip(post_caps, supports):
            beam(parts, (cap[0], cap[1], height - 0.025), cap, 0.025, IRON)
        for a, b in zip(post_caps, post_caps[1:]):
            beam(parts, a, b, 0.029, IRON)
            beam(
                parts, (a[0], a[1], a[2] - 0.30), (b[0], b[1], b[2] - 0.30), 0.017, IRON
            )
    return rise


def walls(parts, field, spans):
    colors = [STONE_DARK, (114, 113, 103), (125, 120, 107), (121, 120, 106)]
    for first, last in spans:
        a, b = np.asarray(first), np.asarray(last)
        vector = b - a
        length = np.linalg.norm(vector)
        unit = vector / length
        for i in range(int(np.ceil(length / 3.0))):
            here = a + unit * i * 3.0
            end = a + unit * min(length, (i + 1) * 3.0)
            ground = ground_height(field, *(0.5 * (here + end)))
            solid(
                parts,
                landscape.rect_on(here, end, 0.36),
                ground - 0.28,
                ground + 0.43,
                colors[(i + 1) % len(colors)],
            )
            for level in (0.10, 0.25, 0.40):
                normal = unit[::-1] * [1, -1] * 0.182
                start, finish = here + normal, end + normal
                beam(
                    parts,
                    (*start, ground + level),
                    (*finish, ground + level),
                    0.013,
                    (80, 81, 72),
                )
            solid(
                parts,
                landscape.rect_on(here, end, 0.397),
                ground + 0.425,
                ground + 0.51,
                (139, 137, 121),
            )


def text_strokes(parts, title, point, glyph_width, height, color):
    step = glyph_width * 1.23
    for i, letter in enumerate(title):
        at = (i - (len(title) - 1) / 2) * step - glyph_width / 2
        if letter == " ":
            continue
        for stroke in GLYPHS[letter]:
            points = [point(at + x * glyph_width, y * height) for x, y in stroke]
            for a, b in zip(points, points[1:]):
                beam(parts, a, b, height * 0.065, color)


def square_kiosk(parts, ground, field, info, ways):
    def frame(enu, bearing):
        center = np.array(enu)
        angle = np.deg2rad(bearing)
        axis = np.array([np.sin(angle), np.cos(angle)])
        normal = np.array([-axis[1], axis[0]])

        def xy(e, n):
            return center + e * axis + n * normal

        def plan(west, south, east, north):
            return Polygon(
                [xy(west, south), xy(east, south), xy(east, north), xy(west, north)]
            )

        return xy, plan, normal

    center = info["position_enu_m"]
    xy, plan, normal = frame(center, info["bearing_degrees"])
    base = ground_height(field, *center)
    width, depth = info["roof_width_m"] / 2, info["roof_depth_m"] / 2
    panel = info["board_width_m"] / 2
    wood = (147, 99, 54)
    endgrain = (101, 67, 42)
    roof = (138, 136, 118)
    for side in (-1, 1):
        e = side * panel
        solid(
            parts,
            plan(e - 0.075, -0.07, e + 0.075, 0.07),
            base - 0.12,
            base + info["eave_m"],
            wood,
        )
        for point in (e - side * 0.32, e + side * 0.23):
            beam(
                parts,
                (*xy(e, 0), base + 2.03),
                (*xy(point, -0.01), base + 2.35),
                0.085,
                endgrain,
            )
    solid(parts, plan(-panel, -0.065, panel, 0.047), base + 0.86, base + 1.96, endgrain)
    for i in range(6):
        z = base + 0.885 + i * 0.174
        solid(parts, plan(-panel, 0.04, panel, 0.077), z, z + 0.162, wood)
    solid(
        parts,
        plan(-width, -depth, width, depth),
        base + info["eave_m"] - 0.049,
        base + info["eave_m"],
        wood,
    )
    ridge = info["ridge_m"] - info["eave_m"]

    def roof_height(e, n):
        offset = float((np.asarray([e, n]) - center) @ normal)
        return base + info["eave_m"] + ridge * (1 - abs(offset) / depth)

    for south, north in ((-depth, 0), (0, depth)):
        surface = plan(-width, south, width, north)
        landscape.top_surface(parts, surface, roof_height, roof, cell=0.58)
        for e in np.linspace(-width + 0.07, width - 0.07, 15):
            a, b = xy(e, south), xy(e, north)
            beam(
                parts,
                (*a, roof_height(*a) + 0.008),
                (*b, roof_height(*b) + 0.008),
                0.015,
                (112, 113, 101),
            )
    for i, (e, z, w, h) in enumerate(
        [
            (-0.76, 1.66, 0.22, 0.22),
            (-0.78, 1.13, 0.24, 0.45),
            (-0.46, 1.41, 0.25, 0.36),
            (-0.19, 1.24, 0.17, 0.35),
            (0.30, 1.20, 0.23, 0.23),
            (0.61, 1.20, 0.23, 0.23),
        ]
    ):
        solid(
            parts,
            plan(e, 0.079, e + w, 0.096),
            base + z,
            base + z + h,
            (204 - 5 * (i % 3), 196 - 5 * (i % 3), 163 - 5 * (i % 3)),
        )
        for line in range(3):
            a = xy(e + 0.04, 0.097)
            b = xy(e + w - 0.04, 0.097)
            z0 = base + z + h * (0.34 + 0.17 * line)
            beam(parts, (*a, z0), (*b, z0), 0.005, (129, 130, 101))
    kiosk = plan(-panel - 0.08, -0.115, panel + 0.08, 0.122)
    assert kiosk.distance(ways) > 0.75
    drape(ground, field, plan(-1.44, -0.8, 1.44, 1.42), (151, 150, 106), 0.065, 0.79)

    sign = info["sign_position_enu_m"]
    xy, plan, _ = frame(sign, info["sign_bearing_degrees"])
    base = ground_height(field, *sign)
    for e in (-0.62, 0.62):
        solid(
            parts,
            plan(e - 0.045, -0.043, e + 0.045, 0.043),
            base - 0.10,
            base + 1.67,
            wood,
        )
    solid(parts, plan(-0.69, -0.051, 0.69, 0.068), base + 0.70, base + 1.62, wood)
    solid(
        parts,
        plan(-0.639, 0.066, 0.639, 0.077),
        base + 0.75,
        base + 1.575,
        (49, 88, 63),
    )
    for name, z in (
        ("EUGENE PIONEER", 1.414),
        ("CEMETERY", 1.278),
        ("MEMORIAL SQUARE", 1.001),
    ):
        text_strokes(
            parts,
            name,
            lambda e, h: (*xy(e, 0.084), base + z + h),
            0.049,
            0.075,
            (219, 214, 188),
        )
    banner = plan(-0.70, -0.082, 0.70, 0.081)
    assert banner.distance(ways) > 0.75
    return [list(kiosk.bounds), list(banner.bounds)]


def smith_vault(parts, field, info, ways):
    west, south, east, north = info["bounds_enu_m"]
    footprint = box(west, south, east, north)
    center_e, center_n = footprint.centroid.coords[0]
    grade = ground_height(field, center_e, center_n)
    assert ways.distance(footprint) > 2
    eave = grade + info["wall_height_m"]
    ridge = eave + info["roof_rise_m"]
    plaster = (168, 190, 192)
    solid(parts, footprint, grade - 0.23, eave, plaster)
    hip = (north - south) / 2
    west_tip, east_tip = (west + hip, center_n), (east - hip, center_n)
    planes = (
        ([(west, south), (east, south), east_tip, west_tip], lambda x, y: y - south),
        ([(east, south), (east, north), east_tip], lambda x, y: east - x),
        ([(east, north), (west, north), west_tip, east_tip], lambda x, y: north - y),
        ([(west, north), (west, south), west_tip], lambda x, y: x - west),
    )
    for (corners, run), color in zip(
        planes, ((173, 195, 199), (160, 184, 190), (167, 189, 191), (158, 181, 185))
    ):
        landscape.top_surface(
            parts,
            Polygon(corners),
            lambda x, y: eave + (ridge - eave) * run(x, y) / hip,
            color,
            cell=0.95,
        )
    plaque_bottom = grade + 0.43
    flat_box(
        parts,
        east + 0.009,
        center_n,
        0.039,
        0.46,
        plaque_bottom,
        plaque_bottom + 0.39,
        (184, 176, 153),
    )
    text_strokes(
        parts,
        "SMITH",
        lambda x, y: (east + 0.029, center_n + x, plaque_bottom + 0.245 + y),
        0.050,
        0.061,
        (83, 81, 71),
    )
    return footprint.bounds


def identification_sign(parts, paving, field, info):
    e, n = info["position_enu_m"]
    w, d, h = (info[k] for k in ("width_m", "depth_m", "height_m"))
    z = ground_height(field, e, n)
    bed = Point(e, n).buffer(1.37, quad_segs=10)
    drape(paving, field, bed, SOIL, 0.069, 0.65)
    flat_box(parts, e, n, w + 0.11, d + 0.16, z - 0.12, z + 0.13, STONE_DARK)
    flat_box(parts, e, n, w, d, z + 0.12, z + h - 0.105, STONE)
    flat_box(parts, e, n, w + 0.13, d + 0.18, z + h - 0.105, z + h, CONCRETE)
    face_n = n - d / 2 - 0.027
    flat_box(
        parts, e, face_n, w * 0.705, 0.054, z + 0.205, z + h - 0.218, (196, 189, 168)
    )
    for y in (0.24, 0.48, 0.71):
        for a, b in (
            (e - w / 2 + 0.018, e - w * 0.36),
            (e + w * 0.36, e + w / 2 - 0.018),
        ):
            beam(
                parts,
                (a, n - d / 2 - 0.005, z + y),
                (b, n - d / 2 - 0.005, z + y),
                0.009,
                STONE_DARK,
            )
    for title, base, width, height in (
        ("I.O.O.F.", 0.665, 0.047, 0.059),
        ("EUGENE PIONEER", 0.511, 0.063, 0.093),
        ("CEMETERY", 0.37, 0.076, 0.098),
        ("1872", 0.262, 0.059, 0.065),
    ):
        text_strokes(
            parts,
            title,
            lambda x, y: (e + x, face_n - 0.030, z + base + y),
            width,
            height,
            (58, 62, 56),
        )
    return bed


def cylinder_between(parts, a, b, radius, color, *, sides=11):
    start, end = np.asarray(a), np.asarray(b)
    # The common beam helper emits coordinates in the right GLB axes.
    mesh = trimesh.creation.cylinder(
        radius=radius, segment=[start, end], sections=sides
    )
    mesh.vertices = mesh.vertices[:, [0, 2, 1]] * [1, 1, -1]
    mesh.visual.vertex_colors = np.tile((*color, 255), (len(mesh.vertices), 1))
    parts.append(mesh)


def orb(parts, p, scales, color, subdivisions=1):
    mesh = trimesh.creation.icosphere(subdivisions=subdivisions, radius=1)
    mesh.vertices = mesh.vertices * np.asarray(scales)[[0, 2, 1]] + [p[0], p[2], -p[1]]
    mesh.visual.vertex_colors = np.tile((*color, 255), (len(mesh.vertices), 1))
    parts.append(mesh)


def memorial(parts, field, info):
    e, n = info["position_enu_m"]
    z = ground_height(field, e, n)
    h = info["height_m"]
    for w, y0, y1, shade in (
        (2.64, -0.10, 0.58, STONE_DARK),
        (2.22, 0.57, 0.91, MARBLE),
        (1.86, 0.90, 1.16, (147, 156, 151)),
        (1.61, 1.15, 1.40, MARBLE),
        (1.37, 1.38, 4.56, (151, 159, 152)),
        (1.69, 4.54, 4.80, MARBLE),
        (1.52, 4.79, 5.05, MARBLE),
        (1.12, 5.04, 5.35, (155, 162, 154)),
    ):
        flat_box(parts, e, n, w, w * 0.93, z + y0, z + y1, shade)
    # The historic figure is read at walking distance as part of the monument.
    v = z + 5.34
    for d in (-0.15, 0.15):
        cylinder_between(
            parts,
            (e, n + d, v + 0.061),
            (e + 0.05, n + d * 0.75, v + 0.94),
            0.126,
            MARBLE,
            sides=9,
        )
        orb(parts, (e - 0.08, n + d, v + 0.11), (0.23, 0.115, 0.10), MARBLE)
    orb(parts, (e + 0.03, n, v + 1.26), (0.255, 0.345, 0.49), MARBLE, 2)
    for d in (-0.31, 0.31):
        cylinder_between(
            parts,
            (e + 0.015, n + d, v + 1.47),
            (e - 0.30, n + d * 0.86, v + 1.09),
            0.095,
            MARBLE,
        )
        cylinder_between(
            parts,
            (e - 0.30, n + d * 0.86, v + 1.09),
            (e - 0.39, n + d * 0.50, v + 1.27),
            0.079,
            MARBLE,
        )
    orb(parts, (e - 0.028, n, v + 1.88), (0.184, 0.157, 0.231), MARBLE, 2)
    orb(parts, (e - 0.045, n, z + h - 0.089), (0.216, 0.176, 0.089), MARBLE)


def rose(parts, field, row, index):
    e, n = row["position_enu_m"]
    r = row["radius_m"]
    z = ground_height(field, e, n)
    rng = np.random.default_rng(492 + index)
    foliage = [(76, 107, 63), (93, 119, 77), (115, 134, 83)]
    for i in range(12):
        angle = i * 2.39996
        distance = r * (rng.uniform(0.29, 0.89))
        x, y = e + distance * np.cos(angle), n + distance * np.sin(angle)
        top = z + (r - 0.42 * distance) * rng.uniform(0.84, 1.16)
        cylinder_between(
            parts, (e, n, z + 0.06), (x, y, top - 0.12), 0.018, (99, 101, 64), sides=5
        )
        orb(parts, (x, y, top), (0.255, 0.235, 0.205), foliage[i % 3])
        if i % 3 == 1:
            orb(
                parts,
                (x - 0.035, y, top + 0.17),
                (0.056, 0.05, 0.044),
                row["flower_color"],
            )


def charles_lawson_rose(parts, field, row):
    e, n = row["position_enu_m"]
    radius = row["radius_m"]
    height = row["height_m"]
    base = ground_height(field, e, n)
    rng = np.random.default_rng(row["block"])
    foliage = [(70, 98, 58), (82, 113, 64), (101, 122, 72)]
    for cane in range(11):
        angle = cane * 2.39996
        outward = radius * rng.uniform(0.32, 0.78)
        de, dn = np.cos(angle) * outward, np.sin(angle) * outward
        shoulder = base + height * rng.uniform(0.53, 0.79)
        tip = (e + de, n + dn, shoulder)
        fork = (e + de * 0.58, n + dn * 0.58, shoulder - height * 0.14)
        cylinder_between(
            parts, (e, n, base - 0.035), fork, 0.013, (106, 105, 68), sides=5
        )
        cylinder_between(parts, fork, tip, 0.009, (93, 106, 56), sides=5)
        orb(parts, fork, (0.19, 0.16, 0.14), foliage[(cane + 1) % 3])
        orb(parts, tip, (0.20, 0.17, 0.13), foliage[cane % 3])
        if cane % 3 != 0:
            for flower in range(3):
                phase = angle + flower * 2.1
                x = tip[0] + 0.058 * np.cos(phase)
                y = tip[1] + 0.058 * np.sin(phase)
                z = shoulder + 0.118 + 0.008 * flower
                orb(parts, (x, y, z), (0.038, 0.036, 0.023), (173, 92, 134), 0)
                orb(parts, (x, y, z + 0.013), (0.025, 0.022, 0.018), (207, 136, 172), 0)


def marker(parts, field, row, index):
    e, n = row["position_enu_m"]
    width, depth, height = (row[key] for key in ("width_m", "depth_m", "height_m"))
    z = ground_height(field, e, n)
    stone = ((169, 165, 149), (185, 182, 164), (137, 140, 131), (161, 157, 143))[
        index % 4
    ]
    flat_box(parts, e, n, width * 1.16, depth * 1.1, z - 0.11, z + 0.13, STONE_DARK)
    if row["silhouette"] == "low":
        slab = box(
            e - depth * 0.37, n - width * 0.43, e + depth * 0.37, n + width * 0.43
        )
        tilt = 0.11 / max(depth, 0.19)
        parts.append(
            geometry.shell(
                slab, z + 0.125, lambda x, _: z + height + tilt * (x - e), stone, stone
            )
        )
        return
    _, _, _, _, _, face = fairmount.chapter.setup_face(
        parts, (e, n - width / 2), (e, n + width / 2)
    )
    profile = Polygon(
        [
            (width * x, z + y * height)
            for x, y in (
                (0.08, 0.13),
                (0.92, 0.13),
                (0.92, 0.83),
                (0.79, 0.96),
                (0.50, 1),
                (0.21, 0.96),
                (0.08, 0.83),
            )
        ]
    )
    face(profile, -depth * 0.34, depth * 0.34, stone)


def canopy(parts, field, tree, index):
    e, n = tree["position_enu_m"]
    h = tree["height_m"]
    r = tree["crown_radius_m"]
    z = ground_height(field, e, n)
    phase = index * 2.399963
    bark = (91, 78, 64)
    foliage = ((72, 91, 67), (89, 107, 76), (101, 117, 80), (78, 98, 76))
    if tree["form"] == "rounded":
        cylinder_between(
            parts, (e, n, z - 0.08), (e, n, z + h * 0.73), r * 0.071, bark, sides=8
        )
        for i, height in enumerate((0.69, 0.70, 0.74, 0.77, 0.87)):
            reach = 0.44 * r if i < 4 else 0.075 * r
            x = e + reach * np.cos(phase + i * 1.57)
            y = n + reach * np.sin(phase + i * 1.57)
            cylinder_between(
                parts,
                (e, n, z + h * 0.38),
                (x, y, z + h * height),
                r * 0.036,
                bark,
                sides=6,
            )
            orb(
                parts,
                (x, y, z + h * height),
                (r * 0.66, r * 0.62, h * 0.12),
                foliage[i % 4],
            )
        return
    cylinder_between(
        parts, (e, n, z - 0.11), (e, n, z + h * 0.92), r * 0.091, bark, sides=8
    )
    vertices, faces, colors = [], [], []
    # Broad lower whorls and shorter upper branches give the canopy its taper.
    for i, (low, high, extent) in enumerate(
        (
            (0.31, 0.70, 1),
            (0.44, 0.79, 0.88),
            (0.56, 0.89, 0.71),
            (0.68, 0.96, 0.53),
            (0.80, 1, 0.36),
        )
    ):
        pattern = phase + i * 0.49
        for j in range(10):
            a, b = pattern + j * np.pi / 5, pattern + (j + 1) * np.pi / 5
            x = e + extent * r * np.cos(a) * (0.88 if j % 2 else 1)
            y = n + extent * r * np.sin(a) * (0.88 if j % 2 else 1)
            u = e + extent * r * np.cos(b) * (1 if j % 2 else 0.88)
            v = n + extent * r * np.sin(b) * (1 if j % 2 else 0.88)
            base = len(vertices)
            vertices.extend(
                (
                    (x, z + h * low, -y),
                    (u, z + h * low, -v),
                    (e, z + h * high, -n),
                    (e, z + h * (low - 0.045), -n),
                )
            )
            faces.extend(((base, base + 1, base + 2), (base + 1, base, base + 3)))
            shade = foliage[(i + (index + j) % 3) % 4]
            colors.extend([(*shade, 255)] * 4)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.visual.vertex_colors = np.asarray(colors, dtype=np.uint8)
    parts.append(mesh)


def export(path, *items, surface_layer=GROUND):
    model = trimesh.Scene()
    for name, parts, kind in items:
        mesh = landscape.ordered_mesh(trimesh.util.concatenate(parts))
        colors = mesh.visual.vertex_colors.copy()
        srgb = colors[:, :3] / 255
        linear = np.where(
            srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4
        )
        colors[:, :3] = (linear * 255).round().astype(np.uint8)
        mesh.visual.vertex_colors = colors
        mesh.metadata.update(asset_id=name, asset_kind=kind)
        if name == surface_layer:
            mesh.metadata["surface_layer"] = surface_layer
        model.add_geometry(mesh, node_name=name, geom_name=name)

    def style(tree):
        tree["asset"]["copyright"] = (
            "Open Campus contributors. Original geometry CC BY 4.0."
        )
        tree["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.012, "roughnessFactor": 0.93}}
        ]
        for mesh in tree["meshes"]:
            mesh["primitives"][0]["material"] = 0

    path.write_bytes(
        trimesh.exchange.gltf.export_glb(
            model, include_normals=True, tree_postprocessor=style
        )
    )
    return {name: len(obj.faces) for name, obj in model.geometry.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    spec = read(root / f"data/metadata/{PACKAGE}.json")
    manifest = read(scene / "manifest.json")
    config = read(scene / "presentation.json")
    field_path = scene / manifest["heightfield_url"]
    field = read(field_path)
    pinned = spec["pinned_sources"]
    assert (
        config["asset_sha256"],
        manifest["model"]["sha256"],
        pin(field_path),
        pin(scene / "navigation.json"),
    ) == tuple(
        pinned[k] for k in ("presentation", "campus", "heightfield", "navigation")
    )
    nav = read(scene / "navigation.json")
    route = spec["walkable_ground"]
    assert route["anchor_enu_m"] in nav["nodes_enu_m"]
    assert all(
        0.05 < a < 20
        for a in np.linalg.norm(
            np.diff([route["anchor_enu_m"], *route["points_enu_m"]], axis=0), axis=1
        )
    )
    ground, details, treads, trees, support, kiosk = [], [], [], [], [], []
    site = named_paths(ground, field, spec)
    frontage_area, wall_boxes = rankin_frontage(ground, field, spec)
    alleys, curb_area = internal_landscape(ground, details, field, spec, site)
    support_boxes, apron_area = support_structures(ground, support, field, spec, site)
    kiosk_boxes = square_kiosk(
        kiosk, ground, field, spec["memorial_square_kiosk"], site
    )
    rise = stairs(treads, details, field, spec["east_stair"])
    walls(details, field, spec["southern_walls"])
    bed = identification_sign(details, ground, field, spec["southeast_sign"])
    memorial(details, field, spec["gar_monument"])
    vault_box = smith_vault(details, field, spec["smith_vault"], site)
    rankin_paths = spec["rankin_fringe"]["paths"]
    obstacles = unary_union(
        [box(*b) for b in [*support_boxes, *kiosk_boxes, vault_box, *wall_boxes]]
    )
    rankin_lengths = branch_lengths(
        route["points_enu_m"], rankin_paths, site, obstacles
    )
    northwest = spec["northwest_refinement"]
    northwest_lengths = branch_lengths(
        [
            *route["points_enu_m"],
            *(p for row in rankin_paths for p in row["points_enu_m"]),
        ],
        northwest["paths"],
        site,
        obstacles,
    )
    for i, row in enumerate(spec["heritage_rose_positions"]):
        rose(details, field, row, i)
    perimeter = spec["perimeter_refinement"]
    old_markers = spec["marker_estimates"]
    marker_centers = []
    marker_rows = [
        *old_markers,
        *perimeter["marker_estimates"],
        *northwest["marker_estimates"],
    ]
    for i, row in enumerate(marker_rows):
        center = Point(row["position_enu_m"])
        if i >= len(old_markers):
            assert all(center.distance(existing) > 0.82 for existing in marker_centers)
            assert alleys.distance(center) > 0.3
        marker_centers.append(center)
        marker(details, field, row, i)
        assert site.distance(center) > 0.6
    lawson_roses = spec["charles_lawson_roses"]["placements"]
    for row in lawson_roses:
        center = Point(row["position_enu_m"])
        spread = center.buffer(row["radius_m"] + 0.15)
        assert box(*row["block_bounds_enu_m"]).covers(spread)
        assert not spread.intersects(site)
        charles_lawson_rose(details, field, row)
    for i, row in enumerate(spec["canopy_estimates"]):
        canopy(trees, field, row, i)
        assert site.distance(Point(row["position_enu_m"])) >= 1.1
    assert not site.intersects(bed)
    for row in spec["heritage_rose_positions"]:
        assert not site.contains(Point(row["position_enu_m"]))
    perimeter_audit = perimeter_landscape(ground, details, field, spec, site, alleys)
    northwest_audit = northwest_planting(ground, field, spec, site)
    args.stage.mkdir(parents=True, exist_ok=True)
    asset = args.stage / "site.glb"
    faces = export(
        asset,
        (GROUND, ground, "landscape-surface"),
        (STAIR, treads, "landscape-surface"),
        (DETAILS, details, "landscape-detail"),
        (CANOPY, trees, "landscape-vegetation"),
        ("pioneer-cemetery-support", support, "landscape-detail"),
        ("pioneer-cemetery-kiosk", kiosk, "landscape-detail"),
    )
    stair = spec["east_stair"]
    rail_boxes = []
    for side in (-1, 1):
        n = stair["north_m"] + side * (stair["width_m"] / 2 - 0.06)
        rail_boxes.append(
            [
                stair["top_east_m"] - 0.01,
                n - 0.037,
                stair["bottom_east_m"] + 0.01,
                n + 0.037,
            ]
        )
    landmarks = [
        box(e - r, n - r, e + r, n + r).bounds
        for e, n, r in (
            (*spec["gar_monument"]["position_enu_m"], 1.30),
            (*spec["southeast_sign"]["position_enu_m"], 0.43),
        )
    ]
    payload = {
        "source_presentation_sha256": pinned["presentation"],
        "source_base_model_sha256": pinned["campus"],
        "source_heightfield_sha256": pinned["heightfield"],
        "source_navigation_sha256": pinned["navigation"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": pin(asset),
        "buildings": [],
        "walkable_ground": {
            "bounds_enu_m": route["bounds_enu_m"],
            "paths": [
                {key: route[key] for key in ("anchor_enu_m", "points_enu_m")},
                *rankin_paths,
                *northwest["paths"],
            ],
        },
        "context_trees": spec["procedural_context_trees_to_remove"],
        "closed_site_boxes_enu_m": [
            *rail_boxes,
            *landmarks,
            *support_boxes,
            *kiosk_boxes,
            vault_box,
            *wall_boxes,
        ],
    }
    descriptor = args.stage / "site.json"
    fairmount.write_json(descriptor, payload, compact=True)
    audit = {
        "path_count": len(spec["roads"]),
        "path_area_m2": round(site.area, 2),
        "path_centerline_m": round(
            sum(LineString(x["centerline_enu_m"]).length for x in spec["roads"]), 2
        ),
        "stair_treads": stair["treads"],
        "nominal_rise_m": round(rise, 4),
        "registered_rose_clusters": len(spec["heritage_rose_positions"]),
        "charles_lawson_rose_clusters": len(lawson_roses),
        "registered_canopy_estimates": len(spec["canopy_estimates"]),
        "aerial_marker_estimates": len(marker_centers),
        "rankin_frontage_area_m2": round(frontage_area, 2),
        "rankin_new_route_edges": sum(len(path["points_enu_m"]) for path in rankin_paths),
        "rankin_route_lengths_m": rankin_lengths,
        "inner_alleys": len(spec["inner_alleys"]),
        "inner_alley_area_m2": round(alleys.area, 2),
        "grave_plot_edges": len(spec["grave_plot_edges"])
        + len(perimeter["grave_plot_edges"])
        + len(northwest["grave_plot_edges"]),
        "grave_plot_curb_area_m2": round(curb_area, 2),
        "support_structures": 2,
        "memorial_square_kiosk_and_sign": 2,
        "smith_vault_bounds_enu_m": vault_box,
        "smith_vault_height_m": spec["smith_vault"]["wall_height_m"]
        + spec["smith_vault"]["roof_rise_m"],
        "support_apron_area_m2": round(apron_area, 2),
        "removed_procedural_tree_indices": [
            x["index"] for x in payload["context_trees"]
        ],
        "perimeter": {
            **perimeter_audit,
            "grave_plot_edges": len(perimeter["grave_plot_edges"]),
            "marker_estimates": len(perimeter["marker_estimates"]),
        },
        "northwest": {
            **northwest_audit,
            "grave_plot_edges": len(northwest["grave_plot_edges"]),
            "marker_estimates": len(northwest["marker_estimates"]),
            "route_edges": sum(
                len(row["points_enu_m"]) + ("end_enu_m" in row)
                for row in northwest["paths"]
            ),
            "route_lengths_m": northwest_lengths,
        },
        "faces": faces,
        "asset_sha256": pin(asset),
        "descriptor_sha256": pin(descriptor),
    }
    fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
