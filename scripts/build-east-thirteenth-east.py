# SPDX-License-Identifier: Apache-2.0
"""Reconstruct the existing East 13th Avenue corridor east of University Street."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.affinity import rotate, translate
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

central = import_module("build-east-thirteenth-central")
west = central.west
site = central.site
foundation = import_module("build-paving-corridors-l2")

PACKAGE = "east-thirteenth-east-review"
GROUND = "east-thirteenth-east-paving"
ASPHALT = (129, 130, 121)
WALK = (176, 171, 156)
TURN = (157, 151, 137)
CURB = (183, 173, 150)
RED = (163, 107, 89)


def band(rows):
    assert all(left[0] < right[0] for left, right in zip(rows, rows[1:])), (
        "Corridor stations must increase from west to east."
    )
    shape = Polygon(
        [(e, south) for e, south, _ in rows]
        + [(e, north) for e, _, north in reversed(rows)]
    )
    assert shape.is_valid and shape.area > 0
    return shape


def surfaces(parts, details, field, spec, structures):
    turn = spec["turnaround"]
    center = Point(*turn["center"])
    circle = center.buffer(turn["radius"], quad_segs=22)
    main = band(spec["road_edges"])
    road = unary_union([main, west.surface(spec["junctions"]), circle])
    beds = unary_union([box(*row["bounds"]) for row in spec["beds"]])
    pits = unary_union(
        [
            Point(row["position_enu_m"]).buffer(row["pit"])
            for row in spec["trees"]
            if "pit" in row
        ]
    )
    obstructions = unary_union([structures, beds, pits])
    road = road.difference(obstructions)
    sidewalks = unary_union(
        [
            band(spec["sidewalk_south"]),
            band(spec["sidewalk_north"]),
            west.surface(spec["extra_walks"]),
        ]
    ).difference(road.union(obstructions))
    turning = road.intersection(circle)
    site.drape(parts, field, road.difference(turning), ASPHALT, 0.090, 1.62)
    site.drape(parts, field, turning, TURN, 0.098, 1.02)
    site.drape(parts, field, sidewalks, WALK, 0.108, 1.48)
    site.drape(details, field, pits, (125, 102, 78), 0.075, 0.70)

    rings = unary_union(
        [
            center.buffer(turn["ring_radius"], quad_segs=22).boundary.buffer(0.083),
            center.buffer(turn["outer_band_radius"], quad_segs=22).boundary.buffer(
                0.105
            ),
        ]
    )
    site.drape(details, field, rings.intersection(turning), RED, 0.144, 0.71)
    outer = circle.boundary.difference(main.buffer(0.07)).buffer(0.095)
    site.drape(details, field, outer.difference(obstructions), RED, 0.148, 0.88)

    curves = [
        [(-226.1, -5.52), (-218.0, -5.52), (-205.0, -5.34), (-199.0, -5.34)],
        [(-192.65, -5.35), (-184.0, -5.22), (-174.0, -5.24), (-151.8, -5.31)],
        [(-141.7, -7.77), (-129.0, -8.05), (-121.5, -7.78), (-116.05, -6.01)],
        [(-105.4, -5.41), (-90.0, -5.31), (-70.0, -5.38), (-55.32, -5.28)],
        [(-48.4, -5.12), (-34.1, -5.0), (-25.16, -5.0)],
        [(-7.9, -6.87), (-5.8, -5.46), (15.0, -4.78), (37.0, -4.65), (72.4, -4.51)],
        [(105.1, -4.51), (132.0, -4.8), (157.0, -5.1), (182.0, -5.25), (205.0, -5.23)],
    ]
    color = (CURB, CURB, CURB, CURB, CURB, RED, CURB)
    for anchor, tint in zip(curves, color, strict=True):
        curb = central.buffered_lines([anchor], 0.182).difference(obstructions)
        site.drape(details, field, curb, tint, 0.151, 1.22)
    return road, sidewalks, turning


def road_text(word):
    width = 0.37
    advance = 0.48
    origin = -((len(word) - 1) * advance + width) / 2
    strokes = [
        [(origin + i * advance + x * width, (y - 0.5) * 1.17) for x, y in stroke]
        for i, letter in enumerate(word)
        for stroke in site.GLYPHS[letter]
    ]
    return central.buffered_lines(strokes, 0.09)


def markings(parts, field, spec, road):
    white = central.buffered_lines(
        [*spec["crossing_lines"], *spec["white_lines"]], 0.152
    )
    for row in spec["zebra_crossings"]:
        e, n = row["center"]
        bars = [
            box(
                -row["length"] / 2,
                offset - row["bar_width"] / 2,
                row["length"] / 2,
                offset + row["bar_width"] / 2,
            )
            for offset in (np.arange(row["bars"]) - (row["bars"] - 1) / 2)
            * row["separation"]
        ]
        if "edge_width" in row:
            for x in (-row["edge_width"] / 2, row["edge_width"] / 2):
                bars.append(box(x - 0.070, -5.05, x + 0.070, 5.2))
        white = white.union(
            translate(rotate(unary_union(bars), row["angle"], origin=(0, 0)), e, n)
        )
    stop = road_text("STOP")
    for row in spec["painted_stops"]:
        white = white.union(
            translate(rotate(stop, row["angle"], origin=(0, 0)), *row["center"])
        )
    site.drape(parts, field, white.intersection(road), central.WHITE, 0.159, 0.95)
    yellow = central.buffered_lines(spec["yellow_lines"], 0.187)
    park_marks = central.buffered_lines(
        [
            line
            for e in spec["parking_markers"]
            for line in [[(e - 0.39, 2.97), (e + 0.39, 2.97)], [(e, 2.97), (e, 3.58)]]
        ],
        0.105,
    )
    site.drape(
        parts,
        field,
        yellow.union(park_marks).intersection(road),
        central.YELLOW,
        0.153,
        1.04,
    )


def routes(spec):
    return [
        dict(anchor_enu_m=branch[0], points_enu_m=branch[1:])
        for branch in [spec["north_branch"], spec["south_branch"]]
    ] + spec["branches"]


def pinned_site(scene, spec):
    pins = spec["pins"]
    manifest = site.read(scene / "manifest.json")
    cfg = site.read(scene / "presentation.json")
    field_path = scene / manifest["heightfield_url"]
    nav_path = scene / "navigation.json"
    assert (
        cfg["asset_sha256"],
        manifest["model"]["sha256"],
        site.pin(field_path),
        site.pin(nav_path),
    ) == (pins["presentation"], pins["model"], pins["heightfield"], pins["navigation"])
    for directory, pin in pins["sites"].items():
        assert site.pin(scene / directory / "site.json") == pin, directory
    field = site.read(field_path)
    layer = cfg["landcover_l2"]
    ground_path = scene / layer["url"]
    assert layer["sha256"] == pins["foundation"] == site.pin(ground_path)
    assert layer["source_heightfield_sha256"] == pins["heightfield"]
    document, binary = foundation.gltf(ground_path)
    ground, _ = foundation.source.mesh_arrays(
        document, binary, foundation.locate(document, "Eugene terrain and land cover L2")
    )
    terrain = np.asarray(field["heights_m"])
    assert len(ground) == len(terrain)
    delta = np.round(ground[:, 1].astype(float) - terrain - 0.018, 4)

    # The Columbia approach also overlaps the existing Ford/Arena grade patch.
    arena = cfg["ford_arena_site"]
    grade_path = scene / arena["url"]
    assert arena["sha256"] == pins["ford_arena"] == site.pin(grade_path)
    grade = site.read(grade_path)["grade"]
    row, column = grade["row"], grade["column"]
    arena_deltas = np.asarray(grade["deltas_m"])
    height, width = arena_deltas.shape
    terrain.reshape(field["ny"], field["nx"])[
        row : row + height, column : column + width
    ] += arena_deltas
    field["heights_m"] = (terrain + delta).tolist()
    return manifest, field, site.read(nav_path)


def build_blockers(scene, spec, manifest, extent):
    neighbors = [
        site.read(scene / directory / "site.json")
        for directory in spec["pins"]["sites"]
    ]
    replaced = {
        row["id"] for payload in neighbors for row in payload.get("buildings", [])
    }
    retired = {key for payload in neighbors for key in payload.get("absorbed_ids", [])}
    records = [
        *(row for row in manifest["buildings"] if row["id"] not in replaced | retired),
        *(row for payload in neighbors for row in payload.get("buildings", [])),
    ]
    buildings = unary_union(
        [
            shape
            for row in records
            for ring in [
                row["footprint_enu_m"],
                *row.get("support_collision_enu_m", []),
            ]
            if extent.intersects(shape := Polygon(ring).buffer(0))
        ]
    )
    old_boxes = unary_union(
        [
            shape
            for payload in neighbors
            for bounds in payload.get("closed_site_boxes_enu_m", [])
            if extent.intersects(shape := box(*bounds))
        ]
    )
    return buildings, old_boxes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(site.root / "data/metadata/east-thirteenth-east.json")
    manifest, field, graph = pinned_site(site.scene, spec)
    buildings, old_boxes = build_blockers(
        site.scene, spec, manifest, box(-257, -28, 243, 22)
    )
    ground, paint, details, plants = [], [], [], []
    road, walk, turning = surfaces(ground, paint, field, spec, buildings)
    paved = road.union(walk)
    assert paved.intersection(buildings).area < 0.03
    markings(paint, field, spec, road)
    tree_points = [Point(row["position_enu_m"]) for row in spec["trees"]]
    stems = unary_union(tree_points)
    for i, tree in enumerate(spec["trees"]):
        assert tree_points[i].distance(buildings) > 0.42
        assert tree_points[i].distance(paved) > 0.17
        site.canopy(plants, field, tree, i)

    obstacles = [
        *(central.planter(details, plants, field, row, stems) for row in spec["beds"]),
        *(central.shelter(details, field, row) for row in spec["shelter_pads"]),
        *(west.post(details, field, *point) for point in spec["bollards"]),
    ]
    assert len(obstacles) <= 16
    for row in spec["rack_rows"]:
        for e, n in np.linspace(row["start"], row["end"], row["count"]):
            assert buildings.distance(Point(e, n)) > 0.7
            central.rack(details, field, e, n)
    paths = routes(spec)
    clearance = unary_union([buildings, old_boxes, *obstacles, stems.buffer(0.35)])
    route_count, route_lengths = west.check_routes(graph, paths, paved, clearance)
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        ("east-thirteenth-east-markings", paint, "landscape-detail"),
        ("east-thirteenth-east-furnishings", details, "landscape-detail"),
        ("east-thirteenth-east-planting", plants, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    descriptor = args.stage / "site.json"
    pins = spec["pins"]
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
            closed_site_boxes_enu_m=[shape.bounds for shape in obstacles],
            walkable_ground={
                "paths": paths,
                "bounds_enu_m": [
                    paved.intersection(box(left, -26, right, 22)).bounds
                    for left, right in [
                        (-253, -170),
                        (-170, -88),
                        (-88, -6),
                        (-6, 76),
                        (76, 158),
                        (158, 240),
                    ]
                ],
            },
        ),
        compact=True,
    )
    audit = dict(
        road_m2=round(road.area, 2),
        sidewalk_m2=round(walk.area, 2),
        emu_turnaround_m2=round(turning.area, 2),
        route_edges=route_count,
        route_lengths_m=route_lengths,
        crossing_line_segments=len(spec["crossing_lines"]),
        zebra_crossings=len(spec["zebra_crossings"]),
        landscaped_beds=len(spec["beds"]),
        tree_ids=[row["tree_id"] for row in spec["trees"]],
        faces=faces,
        asset_sha256=site.pin(glb),
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
