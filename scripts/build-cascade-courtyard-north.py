# SPDX-License-Identifier: Apache-2.0
"""Build the Pacific Hall walkway and the Cascade courtyard arch approach."""

import argparse
from importlib import import_module
from math import hypot, sqrt
from pathlib import Path

import numpy as np
from shapely.affinity import affine_transform
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

south = import_module("build-cascade-courtyard-access")
site = south.site
east_walk = import_module("build-science-walk-east")
PACKAGE = "cascade-courtyard-north-review"
GROUND = "cascade-courtyard-north"


def stations(path):
    points = [path["anchor_enu_m"], *path["points_enu_m"]]
    if "end_enu_m" in path:
        points.append(path["end_enu_m"])
    return points


def stair_coordinates(spec):
    start, end = np.array(spec["centerline_enu_m"])
    axis = end - start
    run = hypot(*axis)
    east, north = axis / run

    def point(length, offset):
        return tuple(
            start + [east * length - north * offset, north * length + east * offset]
        )

    def plan(west, right, south_edge, north_edge):
        return affine_transform(
            box(west, right, south_edge, north_edge),
            [east, -north, north, east, *start],
        )

    return point, plan, run


def footprints(spec):
    blocked = []
    for name in ("cascade-volcanology-review", "lawrence-science-review"):
        descriptor = site.read(site.scene / name / "site.json")
        for row in descriptor["buildings"]:
            for ring in [
                row["footprint_enu_m"],
                *row.get("support_collision_enu_m", []),
            ]:
                blocked.append(Polygon(ring))
    obstacles = unary_union(blocked).buffer(0.065)
    stair = spec["stairs"]
    _, plan, run = stair_coordinates(stair)
    half = stair["width_m"] / 2
    flight = plan(0, -half, run, half)
    zones = [
        LineString(row["paving_axis_enu_m"])
        .buffer(
            row["width_m"] / 2,
            cap_style=row.get("end_cap", "round"),
            join_style="round",
        )
        .difference(obstacles.union(flight))
        for row in spec["surfaces"]
    ]
    assert not flight.intersects(obstacles)
    return zones, flight, obstacles


def route_coverage(spec):
    zones, flight, obstacles = footprints(spec)
    old_cover = unary_union([*zones, flight])
    eastern = site.read(site.root / "data/metadata/science-walk-east.json")
    return old_cover.union(east_walk.walk_footprint(eastern, old_cover, obstacles))


def longitudinal_grade(points, heights):
    distances = np.r_[0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    line = LineString(points)
    assert len(distances) == len(heights)

    def profile(east, north):
        return float(np.interp(line.project(Point(east, north)), distances, heights))

    return profile


def verge_surface(parts, axis, heights, coverage, obstacles, field):
    north_walk = LineString(axis).intersection(box(-266, 74, -253, 124))
    margin = (
        north_walk.buffer(2.22)
        .intersection(box(-266, 74, -252, 124))
        .difference(coverage.union(obstacles))
    )
    profile = longitudinal_grade(axis, heights)

    def grade(east, north):
        fraction = min(1, coverage.distance(Point(east, north)) / 1.095)
        paving = profile(east, north) - 0.018
        ground = site.ground_height(field, east, north) + 0.035
        return paving * (1 - fraction) + ground * fraction

    site.landscape.top_surface(parts, margin, grade, (115, 126, 93), cell=0.55)
    return margin.area


def make_steps(ground, details, stair):
    point, plan, run = stair_coordinates(stair)
    count = stair["treads"]
    start_z, end_z = stair["rise_from_z_m"], stair["rise_to_z_m"]
    rise = (start_z - end_z) / (count + 1)
    assert 0.09 < rise < 0.2
    half = stair["width_m"] / 2
    for index in range(count):
        z = start_z - (index + 1) * rise
        outline = plan(index * run / count, -half, (index + 1) * run / count, half)
        site.solid(ground, outline, end_z - 0.4, z, south.CONCRETE)
    rail_offset = -(half - 0.11)
    rail_height = 0.86
    start, end = (point(d, rail_offset) for d in (0, run))
    site.cylinder_between(
        details,
        (*start, start_z + rail_height),
        (*end, end_z + rail_height),
        0.03,
        south.METAL,
        sides=8,
    )
    for f in (0.06, 0.53, 0.94):
        e, n = point(f * run, rail_offset)
        z = start_z - f * (start_z - end_z)
        site.cylinder_between(
            details,
            (e, n, z - 0.17),
            (e, n, z + rail_height),
            0.024,
            south.METAL,
            sides=8,
        )
    bins = np.linspace(0, run, 9)
    boxes = [
        box(*plan(a, rail_offset - 0.036, b, rail_offset + 0.036).bounds)
        for a, b in zip(bins, bins[1:])
    ]
    return boxes, rise, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    spec = site.read(metadata / "cascade-courtyard-north.json")
    for name, expected in spec["pins"].items():
        assert site.pin(site.scene / name / "site.json") == expected, name
    prior = site.read(site.scene / south.PACKAGE / "site.json")
    old_nodes = {
        tuple(p)
        for record in prior["walkable_ground"]["paths"]
        for p in stations(record)
    }
    routes = []
    for path in spec["paths"]:
        assert tuple(path["anchor_enu_m"]) in old_nodes
        if "end_enu_m" in path:
            assert tuple(path["end_enu_m"]) in old_nodes
        points = stations(path)
        routes.append(LineString(points))
        old_nodes.update(map(tuple, points))

    arch_route = routes[-1]
    zones, stair, obstacles = footprints(spec)
    previous = unary_union([*zones, stair])
    eastern = site.read(metadata / "science-walk-east.json")
    east_points = eastern["points_enu_m"]
    assert tuple(east_points[0]) in old_nodes
    assert not old_nodes.intersection(map(tuple, east_points[1:]))
    extension_path = {"anchor_enu_m": east_points[0], "points_enu_m": east_points[1:]}
    extension_route = LineString(east_points)
    routes.append(extension_route)
    coverage = previous.union(east_walk.walk_footprint(eastern, previous, obstacles))
    for route in routes:
        missing = route.difference(coverage.buffer(0.08))
        assert missing.length < 0.01, missing.wkt

    _, field, _ = south.east.pinned_site(
        site.scene, site.read(metadata / "east-thirteenth-east.json")
    )
    paving, details, verge = [], [], []
    for shape, row in zip(zones, spec["surfaces"], strict=True):
        profile = longitudinal_grade(row["paving_axis_enu_m"], row["z_m"])
        south.pave(paving, details, shape, profile, field, south.CONCRETE)
    rails, rise, run = make_steps(paving, details, spec["stairs"])
    main_walk = spec["surfaces"][0]
    verge_area = verge_surface(
        verge,
        main_walk["paving_axis_enu_m"],
        main_walk["z_m"],
        previous,
        obstacles,
        field,
    )
    portal = spec["surfaces"][-1]
    portal_grade = longitudinal_grade(portal["paving_axis_enu_m"], portal["z_m"])
    east_z = eastern["elevations_z_m"]
    east_grade = longitudinal_grade(east_points, east_z)
    east_paving, east_details, trees, tree_box, east_shape, east_margin = (
        east_walk.make_extension(
            south, field, eastern, previous, portal_grade, east_grade, obstacles
        )
    )
    east_segments = np.linalg.norm(np.diff(east_points, axis=0), axis=1)
    maximum_slope = max(abs(np.diff(east_z)) / east_segments)
    assert maximum_slope < 0.07
    assert extension_route.distance(tree_box) > 3.4
    assert east_shape.intersection(tree_box).is_empty
    obstacle_gap = min(
        route.distance(unary_union([obstacles, *rails, tree_box])) for route in routes
    )
    assert obstacle_gap > 0.54, obstacle_gap
    # Check the part of the fitted route actually crossing the retained arch.
    arch = site.read(metadata / "cascade-volcanology-site.json")["bridge"]["arch"]
    arch_mid = (arch["clear_south_m"] + arch["clear_north_m"]) / 2
    arch_half = (arch["clear_north_m"] - arch["clear_south_m"]) / 2
    span = arch_route.intersection(
        box(
            arch["west_east_m"],
            arch["clear_south_m"],
            arch["east_east_m"],
            arch["clear_north_m"],
        )
    )
    assert span.length > 1.6
    headroom = min(
        arch["spring_z_m"]
        + arch["rise_m"] * sqrt(1 - ((n - arch_mid) / arch_half) ** 2)
        - portal_grade(e, n)
        for e, n in span.coords
    )
    assert headroom > 2.5, headroom

    args.stage.mkdir(parents=True, exist_ok=True)
    asset = args.stage / "site.glb"
    desc = args.stage / "site.json"
    faces = site.export(
        asset,
        (GROUND, [*paving, *east_paving], "landscape-surface"),
        ("cascade-north-paving-edges-rail", details, "landscape-detail"),
        ("science-walk-east-paving-edges", east_details, "landscape-detail"),
        ("science-walk-dawn-redwood", trees, "landscape-vegetation"),
        ("pacific-walk-verge", verge, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    w, s, e, n = coverage.bounds
    site.fairmount.write_json(
        desc,
        {
            **{
                key: prior[key]
                for key in (
                    "source_presentation_sha256",
                    "source_base_model_sha256",
                    "source_heightfield_sha256",
                    "source_navigation_sha256",
                )
            },
            "prerequisite_site_sha256": spec["pins"][south.PACKAGE],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(asset),
            "buildings": [],
            "closed_site_boxes_enu_m": [
                fixture.bounds for fixture in [*rails, tree_box]
            ],
            "walkable_ground": {
                "bounds_enu_m": [(w, s, e, 80), (w, 80, e, n)],
                "paths": [*spec["paths"], extension_path],
            },
        },
        compact=True,
    )
    audit = dict(
        paving_m2=round(coverage.area, 3),
        verge_m2=round(verge_area, 3),
        east_walk_length_m=round(extension_route.length, 3),
        east_walk_paving_m2=round(east_shape.area, 3),
        east_walk_margin_m2=round(east_margin.area, 3),
        east_max_segment_slope=round(float(maximum_slope), 4),
        tree_clearance_m=round(extension_route.distance(tree_box), 3),
        route_edges=sum(
            len(path["points_enu_m"]) + ("end_enu_m" in path)
            for path in [*spec["paths"], extension_path]
        ),
        route_lengths_m=[round(route.length, 3) for route in routes],
        clearance_m=round(obstacle_gap, 3),
        arch_clearance_m=round(headroom, 3),
        stair_treads=spec["stairs"]["treads"],
        stair_rise_m=round(rise, 3),
        tread_depth_m=round(run / spec["stairs"]["treads"], 3),
        faces=faces,
        asset_sha256=site.pin(asset),
        descriptor_sha256=site.pin(desc),
    )
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
