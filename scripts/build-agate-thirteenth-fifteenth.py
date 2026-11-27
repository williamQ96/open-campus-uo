# SPDX-License-Identifier: Apache-2.0
"""Export the Agate Street median, crossings and sidewalks south of East 13th."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.affinity import affine_transform, rotate, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

east = import_module("build-east-thirteenth-east")
site, west, central = east.site, east.west, east.central

PACKAGE = "agate-thirteenth-fifteenth-review"
GROUND = "agate-thirteenth-fifteenth-paving"
MARKS = "agate-thirteenth-fifteenth-markings"
DETAILS = "agate-thirteenth-fifteenth-furnishings"
PLANTS = "agate-thirteenth-fifteenth-planting"
ASPHALT = (132, 130, 120)
WALK = (178, 173, 159)
PANEL = (65, 94, 73)
IRON = (65, 75, 66)


def longitudinal_band(rows):
    return affine_transform(east.band(rows[::-1]), [0, 1, 1, 0, 0, 0])


def ground_model(parts, field, spec, buildings, neighbor):
    road = longitudinal_band(spec["road"]).union(Polygon(spec["east_junction"]))
    median = west.surface(spec["median_sections"])
    mid_cross = LineString(
        [
            (79.88, -102.96),
            (86.7, -102.96),
            (88.15, -103.68),
            (88.72, -106.1),
            (89.42, -110.79),
            (91.55, -111.07),
            (97.52, -111.06),
        ]
    )
    refuge = mid_cross.buffer(1.18, quad_segs=7)
    median = median.difference(refuge)
    asphalt = road.difference(median).difference(buildings)
    walks = unary_union(
        [
            longitudinal_band(spec["west_walk"]),
            longitudinal_band(spec["east_walk"]),
            west.surface(spec["walk_joins"]),
        ]
    ).difference(asphalt.union(buildings))
    cross_deck = refuge.intersection(asphalt)
    soil = median.buffer(-0.24)
    for geometry, color, lift, cell in (
        (asphalt.difference(cross_deck), ASPHALT, 0.091, 1.32),
        (cross_deck, (151, 147, 134), 0.121, 0.80),
        (walks, WALK, 0.124, 1.08),
        (median.difference(soil), (165, 160, 148), 0.194, 0.74),
        (soil, (125, 107, 80), 0.168, 1.0),
    ):
        site.drape(parts, field, geometry, color, lift, cell)
    seam = west.surface(neighbor["junctions"]).intersection(box(73, -21.11, 102, -4))
    return asphalt, walks, median, soil, unary_union([asphalt, walks, seam])


def paint(parts, field, spec, road):
    crosswalks = central.buffered_lines(spec["crossings"], 0.185)
    white = central.buffered_lines(spec["white_lines"], 0.124)
    yellow = central.buffered_lines(spec["yellow_lines"], 0.113)
    stop = east.road_text("STOP")
    letters = unary_union(
        [
            translate(rotate(stop, row["angle"], origin=(0, 0)), *row["center"])
            for row in spec["stop_paint"]
        ]
    )
    for shape, color, lift in (
        (crosswalks, central.WHITE, 0.164),
        (white.union(letters), (206, 203, 182), 0.150),
        (yellow, central.YELLOW, 0.149),
    ):
        site.drape(parts, field, shape.intersection(road), color, lift, 0.83)


def chain_run(parts, field, points):
    line = LineString(points)
    positions = [
        line.interpolate(d).coords[0]
        for d in np.linspace(0, line.length, int(np.ceil(line.length / 1.6)) + 1)
    ]
    heads = []
    for e, n in positions:
        z = site.ground_height(field, e, n)
        site.cylinder_between(
            parts, (e, n, z + 0.11), (e, n, z + 0.92), 0.028, IRON, sides=8
        )
        heads.append(np.array((e, n, z + 0.86)))
    for start, stop in zip(heads, heads[1:]):
        prior = start
        for portion in (0.25, 0.5, 0.75, 1.0):
            point = (1 - portion) * start + portion * stop
            point[2] -= 0.12 * (4 * portion * (1 - portion))
            site.cylinder_between(parts, prior, point, 0.013, IRON, sides=5)
            prior = point
    return box(*line.buffer(0.09).bounds)


def sign(parts, field, row):
    e, n = row["position"]
    direction = row["north"]
    z = site.ground_height(field, e, n)
    stop = row["kind"] == "stop"
    site.cylinder_between(
        parts, (e, n, z - 0.10), (e, n, z + 2.58), 0.044, IRON, sides=8
    )
    if stop:
        for index in range(32):
            delta = -0.34 + (index + 0.5) * 0.68 / 32
            width = 2 * min(0.34, 0.485 - abs(delta))
            k = z + 2.49 + delta
            site.flat_box(
                parts, e, n, width, 0.042, k - 0.012, k + 0.012, (175, 54, 47)
            )
        labels = [("STOP", 2.393, 0.103, 0.17)]
    else:
        w = 1.36 if row["kind"] == "parking" else 0.89
        site.flat_box(parts, e, n, w, 0.054, z + 1.89, z + 2.65, PANEL)
        labels = (
            [
                ("EVENT", 2.49, 0.12, 0.097),
                ("VISITOR", 2.35, 0.103, 0.097),
                ("PARKING", 2.21, 0.102, 0.097),
            ]
            if row["kind"] == "parking"
            else [("KNIGHT", 2.48, 0.089, 0.103), ("ARENA", 2.28, 0.093, 0.114)]
        )
        for a, b in (
            ((-0.23, 2.06), (0.25, 2.06)),
            ((0.25, 2.06), (0.13, 2.15)),
            ((0.25, 2.06), (0.13, 1.98)),
        ):
            site.beam(
                parts,
                (e - a[0] * direction, n + 0.035 * direction, z + a[1]),
                (e - b[0] * direction, n + 0.035 * direction, z + b[1]),
                0.016,
                (222, 218, 191),
            )
    for label, lift, width, height in labels:
        site.text_strokes(
            parts,
            label,
            lambda x, h: (e - x * direction, n + 0.033 * direction, z + lift + h),
            width,
            height,
            (224, 221, 205),
        )
    return box(e - 0.11, n - 0.11, e + 0.11, n + 0.11)


def plant(parts, field, soil, trees):
    obstacles = []
    for i, tree in enumerate(trees):
        point = Point(*tree["position_enu_m"])
        assert soil.buffer(0.25).covers(point), tree
        site.canopy(parts, field, tree, i)
        obstacles.append(box(*point.buffer(0.33).bounds))
    pockets = soil.intersection(
        unary_union(
            [
                box(86, -100.5, 92, -92),
                box(86, -125, 92, -112.5),
                box(87, -49, 92, -36),
            ]
        )
    ).buffer(-0.18)
    count = 0
    rng = np.random.default_rng(43)
    for piece in site.geometry.sections(pockets):
        x0, y0, x1, y1 = piece.bounds
        for x in np.arange(x0, x1, 0.68):
            for y in np.arange(y0, y1, 0.66):
                e, n = np.array([x, y]) + rng.uniform(-0.19, 0.19, 2)
                if not piece.covers(Point(e, n)):
                    continue
                z = site.ground_height(field, e, n)
                a = rng.uniform(0.15, 0.25)
                site.orb(
                    parts,
                    (e, n, z + 0.24),
                    (a, a * 0.84, a * 0.61),
                    (124, 131 - count % 4 * 7, 76),
                )
                count += 1
    return obstacles, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(site.root / "data/metadata/agate-thirteenth-fifteenth.json")
    neighbor = site.read(site.root / "data/metadata/east-thirteenth-east.json")
    manifest, field, graph = east.pinned_site(site.scene, spec)
    buildings, previous_boxes = east.build_blockers(
        site.scene, spec, manifest, box(*spec["trim_bounds"])
    )
    ground, marks, details, planting = [], [], [], []
    road, walks, median, soil, walkable = ground_model(
        ground, field, spec, buildings, neighbor
    )
    paint(marks, field, spec, road)
    boxes, shrubs = plant(planting, field, soil, spec["trees"])
    boxes.extend(chain_run(details, field, row) for row in spec["chain_runs"])
    boxes.extend(sign(details, field, row) for row in spec["signs"])
    assert len(boxes) <= 16
    paths = spec["routes"]
    edges, lengths = west.check_routes(
        graph, paths, walkable, unary_union([buildings, previous_boxes, median, *boxes])
    )
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        (MARKS, marks, "landscape-detail"),
        (DETAILS, details, "landscape-detail"),
        (PLANTS, planting, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    pins = spec["pins"]
    descriptor = args.stage / "site.json"
    site.fairmount.write_json(
        descriptor,
        dict(
            source_presentation_sha256=pins["presentation"],
            source_base_model_sha256=pins["model"],
            source_heightfield_sha256=pins["heightfield"],
            source_navigation_sha256=pins["navigation"],
            ground_node=GROUND,
            url=f"{PACKAGE}/site.glb",
            sha256=site.pin(glb),
            buildings=[],
            walkable_ground=dict(
                paths=paths,
                bounds_enu_m=[
                    [69, -85, 114, -6],
                    [69, -162, 114, -84],
                    [69, -236, 114, -161],
                    [69, -263, 114, -235],
                ],
            ),
            closed_site_boxes_enu_m=[
                [round(value, 4) for value in shape.bounds] for shape in boxes
            ],
        ),
        compact=True,
    )
    metrics = dict(
        road_m2=round(road.area, 2),
        walks_m2=round(walks.area, 2),
        median_m2=round(median.area, 2),
        crossing_lines=len(spec["crossings"]),
        trees=len(spec["trees"]),
        shrubs=shrubs,
        route_edges=edges,
        route_lengths_m=lengths,
        faces=faces,
        asset_sha256=site.pin(glb),
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, metrics)
    print(metrics)


if __name__ == "__main__":
    main()
