# SPDX-License-Identifier: Apache-2.0
"""Export the existing campus corridor from Lillis Plaza to University Street."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
import trimesh
from shapely.affinity import rotate, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

west = import_module("build-east-thirteenth-west-gateway")
site = west.site
PACKAGE = "east-thirteenth-central-review"
GROUND = "east-thirteenth-central-paving"
ROAD = (130, 131, 121)
CONCRETE = (176, 171, 154)
PLAZA = (167, 160, 146)
BAND = (150, 144, 132)
WHITE = (230, 227, 212)
YELLOW = (217, 191, 121)
IRON = (57, 77, 71)


def buffered_lines(lines, width):
    return unary_union(
        [LineString(row).buffer(width / 2, cap_style="flat") for row in lines]
    )


def paving(ground, details, field, spec, buildings):
    beds = unary_union([box(*row["bounds"]) for row in spec["beds"]])
    pits = unary_union(
        [
            Point(tree["position_enu_m"]).buffer(tree["pit_radius_m"])
            for tree in spec["trees"]
            if "pit_radius_m" in tree
        ]
    )
    excluded = unary_union([buildings, beds, pits])
    road = west.surface(spec["road"]).difference(excluded)
    apron = box(*spec["heart"]["bounds"]).difference(excluded.union(road))
    walks = (
        west.surface(spec["walk"])
        .union(
            unary_union(
                [box(*row["bounds"]).buffer(0.29) for row in spec["shelter_pads"]]
            )
        )
        .difference(unary_union([excluded, road, apron]))
    )
    for shape, color, lift in [
        (road, ROAD, 0.090),
        (walks, CONCRETE, 0.106),
        (apron, PLAZA, 0.108),
    ]:
        site.drape(ground, field, shape, color, lift, 1.45)
    site.drape(details, field, pits.difference(buildings), (117, 97, 74), 0.068, 0.72)

    curb = buffered_lines(spec["curb_lines"], 0.175).difference(
        buildings.union(unary_union([box(*gap) for gap in spec["curb_gaps"]]))
    )
    site.drape(details, field, curb, (184, 175, 154), 0.151, 1.04)
    return road, walks, apron, excluded


def arrow():
    return Polygon(
        [
            (-0.91, -0.083),
            (0.27, -0.083),
            (0.27, -0.22),
            (0.83, 0),
            (0.27, 0.22),
            (0.27, 0.083),
            (-0.91, 0.083),
        ]
    )


def road_markings(parts, field, spec, road):
    white = buffered_lines([*spec["crossing_lines"], spec["eastern_channel"]], 0.15)
    bicycle = unary_union(
        [
            Point(x, 0).buffer(0.34).difference(Point(x, 0).buffer(0.273))
            for x in (-0.58, 0.57)
        ]
        + [
            buffered_lines(
                [
                    [(-0.58, 0), (-0.22, 0.48), (0.16, 0.07), (-0.58, 0)],
                    [(0.57, 0), (0.27, 0.52), (0.47, 0.55)],
                    [(-0.38, 0.54), (-0.14, 0.54)],
                ],
                0.069,
            )
        ]
    )
    for row in spec["bike_markings"]:
        icon = bicycle.union(translate(arrow(), xoff=1.85))
        white = white.union(
            translate(rotate(icon, row["heading"], origin=(0, 0)), *row["center"])
        )
    for row in spec["arrows"]:
        white = white.union(
            translate(rotate(arrow(), row["heading"], origin=(0, 0)), *row["center"])
        )
    site.drape(parts, field, white.intersection(road), WHITE, 0.142, 0.88)
    for e, n, x, y in spec["parking_corners"]:
        shape = buffered_lines([[(e, y), (e, n), (x, n), (x, y)]], 0.109).intersection(
            road
        )
        site.drape(parts, field, shape, YELLOW, 0.142, 0.88)


def heart_brick(parts, field, row, paved):
    x0, n0, x1, n1 = row["bounds"]
    bands = unary_union(
        [box(x0, n - 0.28, x1, n + 0.28) for n in row["cross_band_n"]]
        + [box(e - 0.28, n0, e + 0.28, n1) for e in row["long_band_e"]]
    )
    site.drape(parts, field, bands.intersection(paved), BAND, 0.163, 1.08)
    west, south, east, north = row["brick_field"]
    nx, ny = row["brick_divisions"]
    courses = np.linspace(south, north, ny + 1)
    for j, (n, y) in enumerate(zip(courses, courses[1:])):
        breaks = np.linspace(west, east, nx + 1)
        if j % 2:
            breaks = np.r_[west, (breaks[:-1] + breaks[1:]) / 2, east]
        for i, (e, x) in enumerate(zip(breaks, breaks[1:])):
            color = [(157, 128, 108), (160, 132, 111), (153, 126, 109)][(i + j) % 3]
            paver = box(e + 0.016, n + 0.015, x - 0.016, y - 0.015)
            site.drape(parts, field, paver.intersection(paved), color, 0.171, 1.02)


def rack(parts, field, e, n):
    z = site.ground_height(field, e, n) + 0.106
    arch = [(-0.31, -0.10)]
    arch.extend(
        (0.31 * np.cos(t), 0.49 + 0.31 * np.sin(t)) for t in np.linspace(np.pi, 0, 10)
    )
    arch.append((0.31, -0.10))
    vertices = [(e, n + u, z + h) for u, h in arch]
    for a, b in zip(vertices, vertices[1:]):
        site.beam(parts, a, b, 0.044, IRON)


def shelter(parts, field, row):
    e0, n0, e1, n1 = row["bounds"]
    center = (n0 + n1) / 2
    radius = (n1 - n0) / 2
    z = site.ground_height(field, (e0 + e1) / 2, center)
    eave = z + row["height"]
    gabled = row.get("profile") == "gable"

    def roof_height(n):
        offset = (n - center) / radius
        slope = abs(offset) if gabled else offset**2
        return eave + row["rise"] * max(0, 1 - slope)

    for e in (e0 + 0.21, e1 - 0.21):
        for n in (n0 + 0.19, n1 - 0.19):
            base = site.ground_height(field, e, n) - 0.10
            site.beam(parts, (e, n, base), (e, n, roof_height(n)), 0.104, IRON)
        site.beam(parts, (e, n0, eave - 0.052), (e, n1, eave - 0.052), 0.09, IRON)

    rings = np.linspace(n0, n1, 11)
    roof_vertices = [(e, roof_height(n), -n) for n in rings for e in (e0, e1)]
    triangles = []
    for i in range(len(rings) - 1):
        j = i * 2
        triangles.extend([(j, j + 1, j + 2), (j + 1, j + 3, j + 2)])
    roof = trimesh.Trimesh(vertices=roof_vertices, faces=triangles, process=False)
    roof.visual.vertex_colors = [125, 130, 125, 255]
    underside = roof.copy()
    underside.invert()
    underside.apply_translation([0, -0.046, 0])
    parts.extend([roof, underside])
    for e in np.linspace(e0, e1, max(6, round((e1 - e0) / 0.41))):
        for a, b in zip(rings, rings[1:]):
            site.beam(
                parts,
                (e, a, roof_height(a)),
                (e, b, roof_height(b)),
                0.026,
                (136, 141, 135),
            )
    for n in (n0, n1):
        site.beam(
            parts, (e0, n, eave - 0.026), (e1, n, eave - 0.026), 0.081, (99, 111, 105)
        )
    if row["racks"]:
        for e in np.linspace(e0 + 0.54, e1 - 0.54, row["racks"]):
            rack(parts, field, e, center)
    return box(e0 + 0.08, n1 - 0.34, e1 - 0.08, n1 - 0.04)


def planter(details, plants, field, row, trees):
    shape = box(*row["bounds"])
    e0, n0, e1, n1 = shape.bounds
    z = site.ground_height(field, *shape.centroid.coords[0]) + 0.083
    inner = shape.buffer(-0.16, join_style="mitre")
    brick = row["material"] == "low brick"
    rim = (155, 109, 86) if brick else (157, 149, 129)
    site.solid(details, shape, z - 0.15, z + 0.18, rim)
    site.solid(details, shape.difference(inner), z + 0.15, z + 0.29, rim)
    site.solid(details, inner, z + 0.17, z + 0.19, (112, 93, 72))
    for j, e in enumerate(np.arange(e0 + 0.42, e1 - 0.27, 0.69)):
        for i, n in enumerate(np.arange(n0 + 0.45, n1 - 0.26, 0.67)):
            if trees.distance(Point(e, n)) > 0.51:
                radius = 0.195 + ((i * 2 + j) % 4) * 0.06
                site.orb(
                    plants,
                    (e, n, z + 0.37),
                    (radius, radius, radius * 0.8),
                    (82 + i % 3 * 4, 102 + j % 4 * 4, 63),
                )
    return shape


def routes(spec):
    return [
        {"anchor_enu_m": row[0], "points_enu_m": row[1:]}
        for row in (spec["south_branch_enu_m"], spec["north_branch_enu_m"])
    ] + spec["routes"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()

    scene = site.scene
    spec = site.read(site.root / "data/metadata/east-thirteenth-central.json")
    manifest = site.read(scene / "manifest.json")
    cfg = site.read(scene / "presentation.json")
    height_path = scene / manifest["heightfield_url"]
    navigation_path = scene / "navigation.json"
    pins = spec["pins"]
    assert (
        cfg["asset_sha256"],
        manifest["model"]["sha256"],
        site.pin(height_path),
        site.pin(navigation_path),
    ) == (pins["presentation"], pins["model"], pins["heightfield"], pins["navigation"])
    neighbors = []
    for name, pin in pins["sites"].items():
        path = scene / name / "site.json"
        assert site.pin(path) == pin, name
        neighbors.append(site.read(path))

    field = site.read(height_path)
    graph = site.read(navigation_path)
    domain = box(-516, -43, -250, 26)
    records = [
        *manifest["buildings"],
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
            if domain.intersects(shape := Polygon(ring).buffer(0))
        ]
    )
    previous_obstacles = unary_union(
        [
            box(*bounds)
            for payload in neighbors
            for bounds in payload.get("closed_site_boxes_enu_m", [])
            if domain.intersects(box(*bounds))
        ]
    )
    ground, markings, furniture, plants = [], [], [], []
    road, walk, apron, excluded = paving(ground, markings, field, spec, buildings)
    paved = unary_union([road, walk, apron])
    assert paved.intersection(excluded).area < 0.03
    pilot_clip = spec["pilot_tree_clip"]
    assert pilot_clip["source_legacy_sha256"] == pins["presentation"]
    assert pilot_clip["source_refined_sha256"] == site.pin(
        scene / "pilot-trees-l2/trees.glb"
    )
    assert walk.covers(Point(*spec["retired_pilot_tree_enu_m"]))
    road_markings(markings, field, spec, road)
    heart_brick(markings, field, spec["heart"], apron)
    tree_points = [Point(row["position_enu_m"]) for row in spec["trees"]]
    for i, (tree, point) in enumerate(zip(spec["trees"], tree_points, strict=True)):
        assert point.distance(paved) >= 0.16, tree["tree_id"]
        assert point.distance(buildings) > 0.40
        site.canopy(plants, field, tree, i)
    stems = unary_union(tree_points)
    obstacles = [
        *(planter(furniture, plants, field, row, stems) for row in spec["beds"]),
        *(shelter(furniture, field, row) for row in spec["shelter_pads"]),
        *(west.post(furniture, field, *point) for point in spec["bollards"]),
    ]
    assert len(obstacles) <= 16
    racks = 0
    for row in spec["rack_rows"]:
        for e, n in np.linspace(row["start"], row["end"], row["count"]):
            assert buildings.distance(Point(e, n)) > 0.7
            rack(furniture, field, e, n)
            racks += 1
    paths = routes(spec)
    clearance = unary_union(
        [
            buildings,
            previous_obstacles,
            *obstacles,
            *(point.buffer(0.33) for point in tree_points),
        ]
    )
    edges, lengths = west.check_routes(graph, paths, paved, clearance)
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        ("east-thirteenth-central-markings", markings, "landscape-detail"),
        ("east-thirteenth-central-furnishings", furniture, "landscape-detail"),
        ("east-thirteenth-central-planting", plants, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    descriptor = args.stage / "site.json"
    site.fairmount.write_json(
        descriptor,
        dict(
            source_presentation_sha256=pins["presentation"],
            source_base_model_sha256=pins["model"],
            source_heightfield_sha256=pins["heightfield"],
            source_navigation_sha256=pins["navigation"],
            url=f"{PACKAGE}/site.glb",
            sha256=site.pin(glb),
            ground_node=GROUND,
            buildings=[],
            closed_site_boxes_enu_m=[shape.bounds for shape in obstacles],
            pilot_tree_clip=pilot_clip,
            walkable_ground={
                "bounds_enu_m": [
                    paved.intersection(box(x0, -42, x1, 24)).bounds
                    for x0, x1 in [
                        (-512, -445),
                        (-445, -380),
                        (-380, -315),
                        (-315, -252),
                    ]
                ],
                "paths": paths,
            },
        ),
        compact=True,
    )
    audit = dict(
        road_m2=round(road.area, 2),
        sidewalk_and_plaza_m2=round(walk.area + apron.area, 2),
        heart_of_campus_m2=round(apron.area, 2),
        route_edges=edges,
        route_lengths_m=lengths,
        bollards=len(spec["bollards"]),
        shelters=len(spec["shelter_pads"]),
        representative_racks=racks + sum(row["racks"] for row in spec["shelter_pads"]),
        tree_ids=[row["tree_id"] for row in spec["trees"]],
        retired_pilot_tree_indices=pilot_clip["tree_indices"],
        faces=faces,
        asset_sha256=site.pin(glb),
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
