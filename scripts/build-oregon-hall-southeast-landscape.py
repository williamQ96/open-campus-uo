# SPDX-License-Identifier: Apache-2.0
"""Export the Oregon Hall southeast grounds and Agate corner fixtures."""

import argparse
from importlib import import_module
from math import cos, pi, radians, sin
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

east = import_module("build-east-thirteenth-east")
wayfinding = import_module("build-northeast-campus-wayfinding")
courtyard = import_module("build-hedco-courtyard-landscape")
site = east.site
PACKAGE = "oregon-hall-southeast-landscape-review"
GROUND = "oregon-southeast-grounds"
APRON = "oregon-map-apron"
PLANTS = "oregon-southeast-shrub-clusters"
LAMP = "oregon-agate-corner-lamp"
STOP = "oregon-agate-stop-sign"
MAP = "oregon-hall-campus-map-station"
SEATING = "oregon-hall-seating-fixtures"
GREEN = (61, 89, 76)
STEEL = (115, 119, 112)
RED = (178, 55, 46)
WHITE = (238, 233, 215)


def frame(row):
    bearing = radians(row["front_bearing_degrees"])
    return wayfinding.frame(row["enu_m"], (sin(bearing), cos(bearing)))


def stop_sign(parts, field, row):
    e, n = row["enu_m"]
    base = site.ground_height(field, e, n)
    point = frame(row)
    center = row["plate_center_z_m"]
    radius = row["plate_width_m"] / (2 * cos(pi / 8))
    octagon = Polygon(
        [
            (
                radius * cos(pi / 8 + i * pi / 4),
                center + radius * sin(pi / 8 + i * pi / 4),
            )
            for i in range(8)
        ]
    )
    site.cylinder_between(
        parts, (e, n, base - 0.09), (e, n, base + center + 0.30), 0.038, STEEL
    )
    wayfinding.plate(parts, point, octagon, 0.053, 0.038, base, WHITE)
    wayfinding.plate(parts, point, octagon.buffer(-0.023), 0.056, 0.054, base, RED)
    wayfinding.plate(
        parts, point, box(-0.255, 1.978, 0.255, 2.15), 0.053, 0.038, base, WHITE
    )
    wayfinding.plate(
        parts, point, box(-0.243, 1.99, 0.243, 2.138), 0.056, 0.054, base, RED
    )
    for label, z, glyph, height in (
        ("STOP", center - 0.102, 0.112, 0.195),
        ("ALL WAY", 2.023, 0.047, 0.082),
    ):
        site.text_strokes(
            parts,
            label,
            lambda u, h: point(u, 0.068, base + z + h),
            glyph,
            height,
            WHITE,
        )
    return box(e - 0.08, n - 0.08, e + 0.08, n + 0.08)


def corner_lamp(parts, field, row):
    e, n = row["enu_m"]
    base = site.ground_height(field, e, n)
    top = row["pole_top_z_m"]
    for bottom, upper, radius in (
        (-0.055, 0.11, 0.154),
        (0.10, 0.24, 0.128),
        (0.24, 0.55, 0.093),
        (0.53, 0.61, 0.107),
        (0.60, top, 0.052),
        (top - 0.13, top + 0.019, 0.073),
    ):
        site.cylinder_between(
            parts, (e, n, base + bottom), (e, n, base + upper), radius, GREEN, sides=12
        )
    site.orb(parts, (e, n, base + top + 0.19), (0.13, 0.13, 0.202), (214, 222, 203))
    site.orb(parts, (e, n, base + top + 0.365), (0.15, 0.15, 0.043), GREEN)
    return box(e - 0.16, n - 0.16, e + 0.16, n + 0.16)


def map_station(parts, field, row, manifest):
    point = frame(row)
    base = site.ground_height(field, *row["enu_m"])
    half_span = row["post_spacing_m"] / 2
    for u in (-half_span, half_span):
        for bottom, top, radius in (
            (-0.08, 0.12, 0.113),
            (0.11, 0.58, 0.082),
            (0.58, 2.34, 0.056),
            (2.28, 2.40, 0.078),
        ):
            site.cylinder_between(
                parts,
                point(u, 0, base + bottom),
                point(u, 0, base + top),
                radius,
                GREEN,
            )
        site.orb(parts, point(u, 0, base + 2.455), (0.062, 0.062, 0.068), GREEN)
    for shape, front, back in (
        (box(-0.53, 0.8, 0.53, 1.92), 0.092, -0.091),
        (box(-0.565, 1.93, 0.565, 2.10), 0.077, -0.077),
        (box(-0.61, 2.105, 0.61, 2.256), 0.25, -0.25),
    ):
        wayfinding.plate(parts, point, shape, front, back, base, GREEN)
    site.text_strokes(
        parts,
        "MAP",
        lambda u, h: point(u, 0.261, base + 2.151 + h),
        0.091,
        0.063,
        WHITE,
    )
    wayfinding.map_face(parts, point, base, manifest)
    outer = half_span + 0.118
    plan = Polygon(
        [
            point(u, v, 0)[:2]
            for u, v in (
                (-outer, -0.255),
                (outer, -0.255),
                (outer, 0.255),
                (-outer, 0.255),
            )
        ]
    )
    return box(*plan.bounds)


def slatted_bench(parts, field, row):
    e, n = row["enu_m"]
    base = site.ground_height(field, e, n) + 0.113
    grain = (154, 146, 120)
    frame = (123, 119, 101)
    for x in (-0.72, 0.72):
        site.flat_box(
            parts, e + x, n - 0.18, 0.075, 0.078, base - 0.10, base + 0.66, frame
        )
        site.flat_box(
            parts, e + x, n + 0.19, 0.079, 0.079, base - 0.10, base + 0.88, frame
        )
        site.flat_box(
            parts, e + x, n + 0.015, 0.078, 0.51, base + 0.63, base + 0.683, grain
        )
    for i in range(5):
        site.flat_box(
            parts,
            e,
            n - 0.193 + i * 0.093,
            1.76,
            0.079,
            base + 0.419,
            base + 0.468,
            grain,
        )
    for level in (0.55, 0.825):
        site.flat_box(
            parts, e, n + 0.21, 1.76, 0.065, base + level, base + level + 0.061, frame
        )
    for i in range(13):
        site.flat_box(
            parts,
            e - 0.67 + i * 0.112,
            n + 0.206,
            0.052,
            0.049,
            base + 0.588,
            base + 0.832,
            grain,
        )
    return box(e - 0.9, n - 0.265, e + 0.9, n + 0.265)


def seating_furnishings(parts, field, furnishings):
    boxes = [slatted_bench(parts, field, row) for row in furnishings["benches"]]
    boxes.append(corner_lamp(parts, field, furnishings["map_lamp"]))
    e, n = furnishings["bin"]["enu_m"]
    base = site.ground_height(field, e, n) + 0.113
    for bottom, upper, radius, color in (
        (-0.02, 0.10, 0.279, (47, 75, 62)),
        (0.10, 0.85, 0.281, GREEN),
        (0.78, 0.92, 0.302, (49, 78, 64)),
        (0.92, 0.98, 0.264, (67, 91, 71)),
    ):
        site.cylinder_between(
            parts, (e, n, base + bottom), (e, n, base + upper), radius, color, sides=14
        )
    site.orb(parts, (e, n, base + 0.979), (0.163, 0.163, 0.013), (43, 52, 41))
    boxes.append(box(e - 0.31, n - 0.31, e + 0.31, n + 0.31))
    return boxes


def seating_surfaces(spec, structures, apron):
    furnishings = spec["furnishings"]
    return [
        Polygon(furnishings[f"{place}_seating_pad_enu_m"]).difference(
            structures.buffer(0.045).union(apron)
        )
        for place in ("map", "street")
    ]


def approach_surfaces(spec, metadata, structures):
    source = site.read(metadata / "oregon-jaqua-site-review.json")["oregon_hall"]
    host_walks = unary_union([LineString(row).buffer(1.10) for row in source["walks"]])
    apron = Polygon(spec["map_approach_apron_enu_m"]).difference(
        structures.buffer(0.045)
    )
    return apron, host_walks


def oregon_structures(host):
    oregon = next(row for row in host["buildings"] if row["id"] == "roof-11d15952")
    return unary_union(
        [
            Polygon(ring)
            for ring in [oregon["footprint_enu_m"], *oregon["support_collision_enu_m"]]
        ]
    )


def route_coverage(spec, metadata):
    host = site.read(site.scene / "oregon-jaqua-review/site.json")
    structures = oregon_structures(host)
    apron, walks = approach_surfaces(spec, metadata, structures)
    seating = seating_surfaces(spec, structures, apron)
    corridor = site.read(metadata / "east-thirteenth-east.json")
    sidewalk = east.band(corridor["sidewalk_north"]).intersection(
        box(55, 8, 67.4, 12.6)
    )
    return unary_union(
        [apron, walks.intersection(box(39, 10.5, 43.2, 24.2)), *seating, sidewalk]
    )


def build(spec, metadata, stage, audit):
    descriptors = {}
    for directory, expected in spec["pins"].items():
        path = site.scene / directory / "site.json"
        assert site.pin(path) == expected, directory
        descriptors[directory] = site.read(path)
    host = descriptors["oregon-jaqua-review"]
    structures = oregon_structures(host)
    corridor = site.read(metadata / "east-thirteenth-east.json")
    manifest, field, graph = east.pinned_site(site.scene, corridor)
    extent = box(36, -10, 90, 27)
    corridor_obstacles, _ = east.build_blockers(site.scene, corridor, manifest, extent)
    road, walks, _ = east.surfaces([], [], field, corridor, corridor_obstacles)
    corridor_paving = road.union(walks).intersection(extent)
    apron, host_walks = approach_surfaces(spec, metadata, structures)
    existing_paving = corridor_paving.union(host_walks)
    raw_bed = Polygon(spec["foundation_bed_outline_enu_m"])
    assert raw_bed.is_valid
    assert apron.is_valid and apron.intersection(host_walks).area > 1
    seating_pads = seating_surfaces(spec, structures, apron)
    assert all(pad.is_valid for pad in seating_pads)
    assert seating_pads[0].intersection(host_walks).area > 1
    assert seating_pads[1].intersection(corridor_paving).area > 1
    walk_surfaces = unary_union([apron, *seating_pads])
    bed = raw_bed.difference(
        unary_union([existing_paving, structures, walk_surfaces]).buffer(0.045)
    )
    paving, walkable, plants, stop, lamp, station, seating = [], [], [], [], [], [], []
    site.drape(paving, field, bed, (121, 104, 82), 0.091, 0.7)
    site.drape(walkable, field, apron, (176, 170, 151), 0.113, 0.62)
    site.drape(walkable, field, seating_pads[0], (161, 152, 135), 0.113, 0.62)
    site.drape(walkable, field, seating_pads[1], (176, 170, 151), 0.113, 0.62)
    for index, (e, n, spread, height) in enumerate(spec["shrubs"]):
        assert bed.buffer(-spread * 0.78).covers(Point(e, n)), (e, n)
        courtyard.planted_crown(
            plants, field, e, n, spread, height, index * 1.17, base=0.095
        )

    stop_box = stop_sign(stop, field, spec["stop_sign"])
    lamp_box = corner_lamp(lamp, field, spec["lamp"])
    map_box = map_station(station, field, spec["map_station"], manifest)
    collision = [
        stop_box,
        lamp_box,
        map_box,
        *seating_furnishings(seating, field, spec["furnishings"]),
    ]
    for solid in collision:
        assert solid.distance(structures) > 0.15, solid
    assert map_box.distance(host_walks) > 0.50
    walk = LineString(spec["sidewalk_check_enu_m"])
    assert corridor_paving.buffer(0.13).covers(walk)
    clearance = walk.distance(unary_union([*collision, bed]))
    assert clearance > 0.50, clearance
    anchor = spec["map_route_anchor_enu_m"]
    points = spec["map_approach_check_enu_m"]
    paths = descriptors["east-thirteenth-east-review"]["walkable_ground"]["paths"]
    assert any(anchor in item["points_enu_m"] for item in paths)
    nodes = set(map(tuple, graph["nodes_enu_m"]))
    for path in paths:
        assert tuple(path["anchor_enu_m"]) in nodes
        nodes.update(map(tuple, path["points_enu_m"]))

    approach = LineString([anchor, *points])
    assert existing_paving.union(apron).buffer(0.13).covers(approach)
    approach_clearance = approach.distance(unary_union([*collision, bed]))
    assert approach_clearance > 0.50, approach_clearance

    seat_paths = spec["furnishings"]["seat_routes"]
    nodes.update(map(tuple, points))
    seating_routes = []
    for path in seat_paths:
        assert tuple(path["anchor_enu_m"]) in nodes
        route = LineString([path["anchor_enu_m"], *path["points_enu_m"]])
        assert existing_paving.union(walk_surfaces).buffer(0.13).covers(route)
        gap = route.distance(unary_union([*collision, bed]))
        assert gap > 0.50, gap
        seating_routes.append(
            dict(distance_m=round(route.length, 3), clearance_m=round(gap, 3))
        )

    stage.mkdir(parents=True, exist_ok=True)
    asset, descriptor = stage / "site.glb", stage / "site.json"
    faces = site.export(
        asset,
        (GROUND, paving, "landscape-surface"),
        (APRON, walkable, "landscape-surface"),
        (PLANTS, plants, "landscape-vegetation"),
        (STOP, stop, "landscape-detail"),
        (LAMP, lamp, "landscape-detail"),
        (MAP, station, "landscape-detail"),
        (SEATING, seating, "landscape-detail"),
        surface_layer=GROUND,
    )
    site.fairmount.write_json(
        descriptor,
        {
            "source_presentation_sha256": host["source_presentation_sha256"],
            "source_base_model_sha256": host["source_base_model_sha256"],
            "source_heightfield_sha256": host["source_heightfield_sha256"],
            "source_navigation_sha256": corridor["pins"]["navigation"],
            "prerequisite_site_sha256": spec["pins"]["oregon-jaqua-review"],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(asset),
            "buildings": [],
            "closed_site_boxes_enu_m": [solid.bounds for solid in collision],
            "walkable_ground": {
                "bounds_enu_m": [apron.bounds, *(pad.bounds for pad in seating_pads)],
                "paths": [
                    {"anchor_enu_m": anchor, "points_enu_m": points},
                    *seat_paths,
                ],
            },
        },
        compact=True,
    )
    report = dict(
        foundation_bed_m2=round(bed.area, 2),
        map_approach_apron_m2=round(apron.area, 2),
        approach_minimum_clearance_m=round(approach_clearance, 3),
        map_route_edges=len(points),
        map_route_length_m=round(approach.length, 3),
        seating_surface_m2=[round(pad.area, 2) for pad in seating_pads],
        seat_route_edges=sum(len(path["points_enu_m"]) for path in seat_paths),
        seating_routes=seating_routes,
        shrubs=len(spec["shrubs"]),
        fixture_boxes=len(collision),
        minimum_sampled_walk_clearance_m=round(clearance, 3),
        west_station_to_approach_m=round(map_box.distance(host_walks), 3),
        faces=faces,
        asset_sha256=site.pin(asset),
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(audit, report)
    print(report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    build(
        site.read(metadata / "oregon-hall-southeast-landscape.json"),
        metadata,
        args.stage,
        args.audit,
    )


if __name__ == "__main__":
    main()
