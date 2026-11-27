# SPDX-License-Identifier: Apache-2.0
"""Export the existing East 13th Avenue west gateway and Lillis Plaza apron."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.affinity import rotate, scale
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

site = import_module("build-pioneer-cemetery-landscape-review")

PACKAGE = "east-thirteenth-west-gateway-review"
SURFACE = "east-thirteenth-west-paving"
ROAD = (131, 132, 124)
WALK = (177, 172, 157)
PAVERS = (151, 143, 128)
JOINT = (154, 151, 141)
PAINT = (232, 228, 211)
BRICK = (140, 86, 72)
BRICK_CAP = (155, 106, 90)
IRON = (52, 83, 74)
BRASS = (214, 176, 102)


def surface(polygons):
    shapes = [Polygon(points) for points in polygons]
    assert all(shape.is_valid and shape.area > 0 for shape in shapes)
    return unary_union(shapes)


def base_layers(parts, marks, field, spec, buildings):
    asphalt = surface(spec["asphalt_enu_m"]).difference(buildings)
    paved_walkway = surface(spec["concrete_enu_m"]).difference(asphalt.union(buildings))
    beds = unary_union(
        [
            Point(tree["position_enu_m"]).buffer(tree["tree_pit_radius_m"])
            for tree in spec["trees"]
            if tree["tree_pit_radius_m"] > 0
        ]
    ).intersection(paved_walkway)
    walkway = paved_walkway.difference(beds)
    pavers = surface(spec["dark_pavers_enu_m"]).intersection(walkway)
    concrete = walkway.difference(pavers)
    for shape, color, lift in [
        (asphalt, ROAD, 0.090),
        (concrete, WALK, 0.106),
        (pavers, PAVERS, 0.107),
    ]:
        site.drape(parts, field, shape, color, lift, 1.25)
    site.drape(marks, field, beds, (118, 99, 77), 0.067, 0.58)

    curbs = unary_union(
        [
            LineString(points).buffer(0.09, cap_style="flat")
            for points in spec["curb_enu_m"]
        ]
    ).difference(buildings)
    site.drape(marks, field, curbs, (183, 173, 151), 0.149, 0.87)

    crossing_shapes = []
    for row in spec["crossings"]:
        n = row["north_center_m"]
        dx = row["width_m"] / 2
        dy = row["length_m"] / 2
        for e in row["east_centers_m"]:
            stripe = box(e - dx, n - dy, e + dx, n + dy)
            crossing_shapes.append(rotate(stripe, row["rotation_degrees"]))
    for e0, n0, e1, n1 in spec["west_crossing_lines_enu_m"]:
        crossing_shapes.append(
            LineString([(e0, n0), (e1, n1)]).buffer(0.092, cap_style="flat")
        )
    for stripe in crossing_shapes:
        mark = stripe.intersection(asphalt)
        assert mark.area > 0.72 * stripe.area, stripe.bounds
        site.drape(marks, field, mark, PAINT, 0.136, 0.70)

    plaza = concrete.intersection(box(-566.0, -9.7, -525.1, 13.05))
    bands = unary_union(
        [
            LineString(points).buffer(0.34, cap_style="flat")
            for points in spec["plaza_bands_enu_m"]
        ]
    )
    site.drape(marks, field, bands.intersection(plaza), JOINT, 0.142, 1.25)
    e, n = spec["plaza_pattern_center_enu_m"]
    inset = box(e - 4.8, n - 1.63, e + 4.05, n + 1.63).union(
        box(e - 1.91, n - 3.92, e + 1.54, n + 4.07)
    )
    for x, y in [(e - 3.23, n + 1.67), (e + 2.49, n - 2.74), (e + 4.02, n + 1.67)]:
        inset = inset.union(box(x, y, x + 1.12, y + 1.12))
    site.drape(marks, field, inset.intersection(plaza), (162, 155, 141), 0.141, 1.1)
    ring = Point(e, n).buffer(1.18).difference(Point(e, n).buffer(1.07))
    site.drape(marks, field, ring, (178, 170, 152), 0.148, 0.58)
    return asphalt, walkway, crossing_shapes


def post(parts, field, e, n):
    z = site.ground_height(field, e, n) + 0.092
    for bottom, top, radius, color in [
        (-0.04, 0.10, 0.112, IRON),
        (0.04, 0.79, 0.076, IRON),
        (0.76, 0.85, 0.093, IRON),
        (0.82, 0.875, 0.101, BRASS),
    ]:
        site.cylinder_between(
            parts, (e, n, z + bottom), (e, n, z + top), radius, color, sides=12
        )
    site.orb(parts, (e, n, z + 0.87), (0.09, 0.09, 0.048), BRASS)
    return box(e - 0.13, n - 0.13, e + 0.13, n + 0.13)


def pylon(parts, field, row):
    e, n = row["position_enu_m"]
    _, end = row["fence_end_enu_m"]
    z = site.ground_height(field, e, n)
    for low, high, width, depth, color in [
        (-0.14, 0.18, 1.51, 1.44, BRICK_CAP),
        (0.14, 0.39, 1.30, 1.24, BRICK),
        (0.39, 2.17, 1.15, 1.10, BRICK),
        (2.17, 2.28, 1.33, 1.27, BRICK_CAP),
        (2.28, 2.40, 1.17, 1.13, BRICK),
        (2.40, 2.49, 1.00, 0.97, BRICK_CAP),
    ]:
        site.flat_box(parts, e, n, width, depth, z + low, z + high, color)
    for h in np.linspace(0.47, 2.10, 17):
        site.flat_box(parts, e, n, 1.158, 1.107, z + h, z + h + 0.012, BRICK_CAP)
    site.cylinder_between(parts, (e, n, z + 2.46), (e, n, z + 2.92), 0.071, IRON)
    site.orb(parts, (e, n, z + 2.98), (0.108, 0.108, 0.173), (224, 222, 200))
    if row["plaque"]:
        site.flat_box(parts, e - 0.588, n, 0.018, 0.68, z + 0.83, z + 1.78, BRASS)
        site.flat_box(parts, e - 0.599, n, 0.015, 0.62, z + 0.87, z + 1.74, IRON)
        site.orb(parts, (e - 0.612, n, z + 1.56), (0.014, 0.094, 0.094), BRASS)
        for text, height, width in [
            ("UNIVERSITY", 1.32, 0.048),
            ("OF OREGON", 1.18, 0.044),
        ]:
            site.text_strokes(
                parts,
                text,
                lambda x, h: (e - 0.613, n - x, z + h + height),
                width,
                0.058,
                PAINT,
            )

    starts = np.linspace(n + np.sign(end - n) * 0.57, end, 13)
    tops = []
    for i, at in enumerate(starts):
        h = site.ground_height(field, e, at)
        rise = 0.89 - min(i, 6) * 0.057 + min(max(i - 6, 0), 3) * 0.048
        tops.append((e, at, h + 0.5 + rise))
        site.beam(parts, (e, at, h + 0.48), tops[-1], 0.038, IRON)
    for a, b in zip(tops, tops[1:]):
        site.beam(parts, a, b, 0.044, IRON)
        site.beam(
            parts, (a[0], a[1], a[2] - 0.12), (b[0], b[1], b[2] - 0.12), 0.030, IRON
        )
    for a, b in zip(starts, starts[1:]):
        middle = (a + b) / 2
        ground = site.ground_height(field, e, middle)
        depth = abs(b - a) + 0.015
        site.flat_box(
            parts, e, middle, 0.48, depth, ground - 0.09, ground + 0.49, BRICK
        )
        site.flat_box(
            parts, e, middle, 0.55, depth, ground + 0.47, ground + 0.54, BRICK_CAP
        )
        site.flat_box(
            parts, e, middle, 0.516, depth, ground + 0.16, ground + 0.19, BRICK_CAP
        )
        site.beam(parts, (e, a, ground + 0.62), (e, b, ground + 0.62), 0.029, IRON)
    return box(e - 0.78, min(n - 0.74, end), e + 0.78, max(n + 0.74, end))


def signs(parts, field, spec):
    e, n = spec["information_enu_m"]
    z = site.ground_height(field, e, n)
    for y in (n - 0.81, n + 0.81):
        site.cylinder_between(parts, (e, y, z - 0.10), (e, y, z + 2.61), 0.071, IRON)
        site.cylinder_between(parts, (e, y, z - 0.02), (e, y, z + 0.24), 0.102, IRON)
        site.orb(parts, (e, y, z + 2.64), (0.085, 0.084, 0.10), IRON)
    site.flat_box(parts, e, n, 0.135, 1.58, z + 0.42, z + 2.36, IRON)
    site.flat_box(parts, e - 0.071, n, 0.019, 1.49, z + 1.30, z + 2.11, (58, 94, 81))
    for y, color in [(n - 0.37, (205, 205, 181)), (n + 0.37, (121, 164, 180))]:
        site.flat_box(parts, e - 0.074, y, 0.023, 0.62, z + 0.52, z + 1.23, color)
        for h in (0.65, 0.76, 1.05, 1.09):
            site.flat_box(
                parts, e - 0.09, y, 0.01, 0.36, z + h, z + h + 0.012, (121, 134, 125)
            )
    site.text_strokes(
        parts,
        "INFORMATION",
        lambda x, h: (e - 0.083, n - x, z + 2.22 + h),
        0.102,
        0.10,
        BRASS,
    )
    kiosk = box(e - 0.14, n - 0.91, e + 0.14, n + 0.91)

    e, n = spec["stop_sign_enu_m"]
    z = site.ground_height(field, e, n)
    site.cylinder_between(
        parts, (e, n, z - 0.10), (e, n, z + 2.82), 0.035, (118, 122, 118)
    )
    for row in range(28):
        h = -0.34 + (row + 0.5) * 0.68 / 28
        avail = min(0.34, 0.49 - abs(h))
        site.flat_box(
            parts,
            e,
            n,
            avail * 2,
            0.031,
            z + 2.65 + h - 0.0123,
            z + 2.65 + h + 0.0123,
            (174, 48, 45),
        )
    border = [
        (0.34, 0.146),
        (0.146, 0.34),
        (-0.146, 0.34),
        (-0.34, 0.146),
        (-0.34, -0.146),
        (-0.146, -0.34),
        (0.146, -0.34),
        (0.34, -0.146),
    ]
    for (ax, az), (bx, bz) in zip(border, [*border[1:], border[0]]):
        site.beam(
            parts,
            (e + ax, n - 0.018, z + 2.65 + az),
            (e + bx, n - 0.018, z + 2.65 + bz),
            0.017,
            PAINT,
        )
    site.flat_box(parts, e, n, 0.49, 0.035, z + 1.79, z + 2.27, PAINT)
    for label, height, width, color in [
        ("STOP", 2.55, 0.106, PAINT),
        ("NO", 2.07, 0.072, IRON),
        ("TURNS", 1.88, 0.058, IRON),
    ]:
        site.text_strokes(
            parts,
            label,
            lambda x, h: (e + x, n - 0.024, z + height + h),
            width,
            0.115,
            color,
        )
    return kiosk, box(e - 0.087, n - 0.087, e + 0.087, n + 0.087)


def plaza_furnishings(details, planting, field, spec):
    barriers = []
    for idx, bounds in enumerate(spec["planters_enu_m"]):
        bed = box(*bounds)
        center = bed.centroid.coords[0]
        z = site.ground_height(field, *center) + 0.10
        soil = bed.buffer(-0.16, join_style="mitre")
        site.solid(details, bed, z - 0.16, z + 0.32, (166, 153, 134))
        site.solid(details, bed.difference(soil), z + 0.26, z + 0.43, (185, 177, 153))
        site.solid(details, soil, z + 0.31, z + 0.339, (114, 94, 72))
        e0, n0, e1, n1 = soil.bounds
        for i, x in enumerate(np.arange(e0 + 0.33, e1, 0.64)):
            for j, y in enumerate(np.arange(n0 + 0.32, n1, 0.56)):
                if soil.contains(Point(x, y)):
                    radius = 0.27 + (i % 3 + j % 2) * 0.055
                    site.orb(
                        planting,
                        (x, y, z + 0.53),
                        (radius, radius * 0.85, radius * 0.86),
                        (76 + idx * 4, 99 + (i + j) % 5 * 4, 54),
                    )
        barriers.append(bed)

    statue = spec["thinker_duck"]
    slab = box(*statue["slab_enu_m"])
    site.drape(details, field, slab, (195, 192, 176), 0.123, 0.76)
    x0, y0, x1, y1 = statue["base_enu_m"]
    e, n = (x0 + x1) / 2, (y0 + y1) / 2
    pedestal = scale(Point(e, n).buffer(1, quad_segs=12), (x1 - x0) / 2, (y1 - y0) / 2)
    z = site.ground_height(field, *pedestal.centroid.coords[0]) + 0.123
    site.solid(details, pedestal, z - 0.05, z + 0.06, (138, 130, 109))
    site.solid(
        details,
        pedestal.buffer(-0.026),
        z + 0.06,
        z + statue["height_m"],
        (132, 122, 101),
    )
    for x in (e - 0.23, e + 0.23):
        site.flat_box(
            details, x, y0 + 0.038, 0.32, 0.026, z + 0.68, z + 0.825, (76, 68, 53)
        )
    return [*barriers, box(*pedestal.bounds)]


def check_routes(graph, routes, walkable, obstacles):
    available = set(map(tuple, graph["nodes_enu_m"]))
    lengths, edge_count = [], 0
    for path in routes:
        assert tuple(path["anchor_enu_m"]) in available
        tail = [path["end_enu_m"]] if "end_enu_m" in path else []
        assert all(tuple(point) in available for point in tail)
        points = [path["anchor_enu_m"], *path["points_enu_m"], *tail]
        line = LineString(points)
        spans = np.linalg.norm(np.diff(points, axis=0), axis=1)
        assert all(0.05 < span < 20 for span in spans), points
        assert line.distance(obstacles) > 0.44, (points, line.distance(obstacles))
        uncovered = line.difference(walkable.buffer(0.13))
        assert uncovered.length < 0.90, (points, uncovered.wkt)
        available.update(map(tuple, path["points_enu_m"]))
        lengths.append(round(line.length, 2))
        edge_count += len(points) - 1
    return edge_count, lengths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    scene = site.scene
    spec = site.read(site.root / "data/metadata/east-thirteenth-west-gateway.json")
    manifest = site.read(scene / "manifest.json")
    config = site.read(scene / "presentation.json")
    field_path = scene / manifest["heightfield_url"]
    nav_path = scene / "navigation.json"
    lillis_path = scene / "lillis-complex-review/site.json"
    dads_path = scene / "dads-gates-landscape-review/site.json"
    pins = {
        "presentation": config["asset_sha256"],
        "base_model": manifest["model"]["sha256"],
        "heightfield": site.pin(field_path),
        "navigation": site.pin(nav_path),
        "lillis": site.pin(lillis_path),
        "dads": site.pin(dads_path),
    }
    assert pins == spec["pinned_sources"], "The source scene or adjacent site changed."
    field = site.read(field_path)
    graph = site.read(nav_path)
    records = [*manifest["buildings"], *site.read(lillis_path)["buildings"]]
    buildings = unary_union(
        [
            Polygon(outline).buffer(0)
            for row in records
            for outline in [
                row["footprint_enu_m"],
                *row.get("support_collision_enu_m", []),
            ]
            if box(-654, -21, -507, 23).intersects(Polygon(outline))
        ]
    )

    paving, marks, furniture, planting = [], [], [], []
    road, walk, stripes = base_layers(paving, marks, field, spec, buildings)
    blockers = [
        *(post(furniture, field, *point) for point in spec["bollards_enu_m"]),
        *(pylon(furniture, field, row) for row in spec["pylons"]),
        *signs(furniture, field, spec),
        *plaza_furnishings(furniture, planting, field, spec),
    ]
    assert len(blockers) <= 16
    hardscape = road.union(walk)
    assert hardscape.intersection(buildings).area < 0.02
    assert all(hardscape.covers(Point(*point)) for point in spec["bollards_enu_m"])
    assert all(footprint.difference(walk).area < 0.04 for footprint in blockers[-4:])
    obstacles = unary_union([buildings, *blockers])
    stems = []
    for index, tree in enumerate(spec["trees"]):
        stem = Point(tree["position_enu_m"])
        assert stem.distance(road.union(obstacles)) > 0.35
        stems.append(stem.buffer(0.36))
        site.canopy(planting, field, tree, index)
    edges, lengths = check_routes(
        graph, spec["routes"], hardscape, obstacles.union(unary_union(stems))
    )
    through = LineString([[-622.956, 2.008], [-617.081, 2.336], [-611.205, 2.664]])
    assert through.distance(obstacles) > 0.8

    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (SURFACE, paving, "landscape-surface"),
        ("east-thirteenth-west-markings", marks, "landscape-detail"),
        ("east-thirteenth-west-gateway", furniture, "landscape-detail"),
        ("east-thirteenth-west-planting", planting, "landscape-vegetation"),
        surface_layer=SURFACE,
    )
    payload = dict(
        source_presentation_sha256=pins["presentation"],
        source_base_model_sha256=pins["base_model"],
        source_heightfield_sha256=pins["heightfield"],
        source_navigation_sha256=pins["navigation"],
        ground_node=SURFACE,
        url=f"{PACKAGE}/site.glb",
        sha256=site.pin(glb),
        buildings=[],
        walkable_ground={
            "paths": spec["routes"],
            "bounds_enu_m": [
                hardscape.intersection(box(-654, -17, -574, 20)).bounds,
                hardscape.intersection(box(-574, -17, -510, 20)).bounds,
            ],
        },
        closed_site_boxes_enu_m=[shape.bounds for shape in blockers],
    )
    descriptor = args.stage / "site.json"
    site.fairmount.write_json(descriptor, payload, compact=True)
    audit = dict(
        asphalt_m2=round(road.area, 2),
        hardscape_m2=round(walk.area, 2),
        crossing_marks=len(stripes),
        bollards=len(spec["bollards_enu_m"]),
        registered_trees=[tree["tree_id"] for tree in spec["trees"]],
        route_edges=edges,
        route_lengths_m=lengths,
        doors_or_buildings_changed=0,
        faces=faces,
        asset_sha256=payload["sha256"],
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
