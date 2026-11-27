# SPDX-License-Identifier: Apache-2.0
"""Build the Cascade courtyard south walk, southwest stair and dry fountain."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
import trimesh
from shapely import get_parts
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

east = import_module("build-east-thirteenth-east")
site = east.site
fountain = import_module("build-cascade-charley-fountain")
PACKAGE = "cascade-courtyard-access-review"
GROUND = "cascade-courtyard-access"
CONCRETE = (164, 158, 145)
METAL = (105, 111, 107)


def footprints(spec, host):
    flight = box(*spec["stair"]["bounds_enu_m"])
    exclusion = box(*spec["fountain_reservation_enu_m"])
    structures = unary_union(
        [
            Polygon(ring)
            for row in host["buildings"]
            for ring in [
                row["footprint_enu_m"],
                *row.get("support_collision_enu_m", []),
            ]
        ]
    )
    blocked = exclusion.union(structures.buffer(0.04))
    approach = Polygon(spec["south_paving_enu_m"]).difference(blocked.union(flight))
    court = Polygon(spec["court_paving_enu_m"]).difference(blocked.union(flight))
    return approach, flight, court, exclusion, structures


def route_coverage(spec):
    host = site.read(site.scene / "cascade-volcanology-review/site.json")
    approach, flight, court, _, _ = footprints(spec, host)
    return unary_union([approach, flight, court])


def add_stair(ground, details, spec):
    west, south, east, north = spec["bounds_enu_m"]
    upper, lower = spec["south_z_m"], spec["north_z_m"]
    count = spec["treads"]
    run = (north - south) / count
    rise = (upper - lower) / (count + 1)
    rails = []
    for step in range(count):
        top = upper - (step + 1) * rise
        start = south + step * run
        end = north if step == count - 1 else south + (step + 1) * run
        site.solid(ground, box(west, start, east, end), lower - 0.28, top, CONCRETE)
    for e in (west + 0.08, east - 0.08):
        site.cylinder_between(
            details,
            (e, south, upper + 0.84),
            (e, north, lower + 0.84),
            0.035,
            METAL,
            sides=8,
        )
        for f in (0.08, 0.52, 0.92):
            n = south + f * (north - south)
            z = upper + f * (lower - upper)
            site.cylinder_between(
                details, (e, n, z - 0.15), (e, n, z + 0.84), 0.026, METAL, sides=8
            )
        rails.append(box(e - 0.04, south, e + 0.04, north))
    return rails, rise, run


def grade_profile(rows, north):
    stations, heights = zip(*rows, strict=True)
    return float(np.interp(north, stations, heights))


def pave(parts, detail, footprint, profile, field, color):
    site.landscape.top_surface(parts, footprint, profile, color, cell=0.57)
    vertices = []
    for shape in get_parts(footprint):
        shape = orient(shape)
        for ring in (shape.exterior, *shape.interiors):
            line = LineString(ring)
            distances = sorted(
                set(np.arange(0, line.length, 0.38))
                | {line.project(Point(point)) for point in ring.coords}
                | {line.length}
            )
            points = [line.interpolate(distance).coords[0] for distance in distances]
            for (a, b), (c, d) in zip(points, points[1:]):
                top_a, top_b = profile(a, b), profile(c, d)
                base_a = min(top_a - 0.05, site.ground_height(field, a, b) - 0.035)
                base_b = min(top_b - 0.05, site.ground_height(field, c, d) - 0.035)
                lower_a, lower_b = (a, base_a, -b), (c, base_b, -d)
                upper_a, upper_b = (a, top_a, -b), (c, top_b, -d)
                vertices.extend((lower_a, lower_b, upper_b, lower_a, upper_b, upper_a))
    if vertices:
        mesh = trimesh.Trimesh(
            vertices, np.arange(len(vertices)).reshape((-1, 3)), process=False
        )
        mesh.visual.vertex_colors = [139, 132, 118, 255]
        detail.append(mesh)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    spec = site.read(metadata / "cascade-courtyard-access.json")
    for name, digest in spec["pins"].items():
        assert site.pin(site.scene / name / "site.json") == digest, name
    host = site.read(site.scene / "cascade-volcanology-review/site.json")
    source = site.read(site.scene / "east-thirteenth-east-review/site.json")
    corridor = site.read(metadata / "east-thirteenth-east.json")
    _, field, _ = east.pinned_site(site.scene, corridor)
    assert any(
        spec["paths"][0]["anchor_enu_m"] in row["points_enu_m"]
        for row in source["walkable_ground"]["paths"]
    )
    approach, flight, court, exclusion, structures = footprints(spec, host)
    assert approach.is_valid and court.is_valid and flight.disjoint(structures)
    assert approach.intersection(flight).area < 0.001
    coverage = unary_union([approach, flight, court])
    lines = [
        LineString([row["anchor_enu_m"], *row["points_enu_m"]]) for row in spec["paths"]
    ]
    assert all(coverage.buffer(0.08).covers(line) for line in lines)
    ground, details, beds, planting = [], [], [], []
    pave(
        ground,
        details,
        approach,
        lambda e, n: grade_profile(spec["south_grade"], n),
        field,
        CONCRETE,
    )
    pave(
        ground,
        details,
        court,
        lambda e, n: grade_profile(spec["court_grade"], n),
        field,
        (166, 156, 143),
    )
    rails, rise, run = add_stair(ground, details, spec["stair"])
    fountain_spec = site.read(metadata / "cascade-charley-fountain.json")
    concrete, lining, stones, fountain_blockers = fountain.build_fountain(fountain_spec)
    blockers = unary_union([*fountain_blockers, *rails])
    clearance = min(line.distance(blockers) for line in lines)
    assert clearance > 0.54, clearance
    bed = unary_union([Polygon(ring) for ring in spec["verge_enu_m"]]).difference(
        coverage.buffer(0.025).union(exclusion)
    )
    site.drape(beds, field, bed, (108, 101, 79), 0.086, 0.66)
    hedco = import_module("build-hedco-courtyard-landscape")
    for i, (e, n, radius) in enumerate(spec["shrubs"]):
        assert bed.buffer(-radius * 0.75).covers(Point(e, n))
        hedco.planted_crown(
            planting, field, e, n, radius, 0.46 + 0.045 * (i % 3), i + 0.35, base=0.09
        )
    args.stage.mkdir(parents=True, exist_ok=True)
    asset = args.stage / "site.glb"
    descriptor = args.stage / "site.json"
    faces = site.export(
        asset,
        (GROUND, ground, "landscape-surface"),
        ("cascade-courtyard-edges-and-rails", details, "landscape-detail"),
        ("cascade-volcanology-walk-verge", beds, "landscape-vegetation"),
        ("cascade-volcanology-walk-shrubs", planting, "landscape-vegetation"),
        ("cascade-charley-concrete", concrete, "landscape-detail"),
        ("cascade-charley-blue-tile", lining, "landscape-detail"),
        ("cascade-charley-stones", stones, "landscape-detail"),
        surface_layer=GROUND,
    )
    site.fairmount.write_json(
        descriptor,
        {
            **{
                key: source[key]
                for key in (
                    "source_presentation_sha256",
                    "source_base_model_sha256",
                    "source_heightfield_sha256",
                    "source_navigation_sha256",
                )
            },
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(asset),
            "buildings": [],
            "closed_site_boxes_enu_m": [
                blocker.bounds for blocker in [*fountain_blockers, *rails]
            ],
            "walkable_ground": {
                "bounds_enu_m": [coverage.bounds],
                "paths": spec["paths"],
            },
        },
        compact=True,
    )
    result = dict(
        paving_m2=round(coverage.area, 2),
        south_paving_m2=round(approach.area, 2),
        court_paving_m2=round(court.area, 2),
        verge_m2=round(bed.area, 2),
        shrubs=len(spec["shrubs"]),
        stair_treads=spec["stair"]["treads"],
        stair_rise_m=round(rise, 3),
        stair_run_m=round(run, 3),
        route_lengths_m=[round(line.length, 3) for line in lines],
        route_edges=sum(len(row["points_enu_m"]) for row in spec["paths"]),
        clearance_m=round(clearance, 3),
        basin_m2=round(box(*fountain_spec["basin"]["bounds_enu_m"]).area, 2),
        basin_opening_m2=round(box(*fountain_spec["basin"]["opening_enu_m"]).area, 2),
        basin_depth_m=round(
            fountain_spec["basin"]["rim_z_m"] - fountain_spec["basin"]["floor_z_m"],
            3,
        ),
        fountain_stones=len(fountain_spec["stones"]),
        faces=faces,
        asset_sha256=site.pin(asset),
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, result)
    print(result)


if __name__ == "__main__":
    main()
