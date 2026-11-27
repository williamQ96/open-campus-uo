# SPDX-License-Identifier: Apache-2.0
"""Rebuild the Frohnmayer east drive and the two walks from East 18th Avenue."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
import trimesh
from shapely import get_parts
from shapely.affinity import rotate, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

east18 = import_module("build-east-18th-west-approach")
green, site = east18.green, east18.site
PACKAGE = "frohnmayer-east-drive-review"
DRIVE = "frohnmayer-east-drive-paving"
WALK = "frohnmayer-east-drive-walks"
DETAIL = "frohnmayer-east-drive-details"
PLANTS = "frohnmayer-east-drive-planting"
ASPHALT_LIFT = 0.094
WALK_LIFT = 0.151


def legacy_road(spec, manifest):
    return next(
        row
        for row in manifest["corridors"]["features"]
        if row["id"] == spec["legacy_road"]["id"]
    )


def retired_road_segments(spec, manifest, graph):
    road = legacy_road(spec, manifest)
    line = LineString(road["centerline_enu_m"])
    low, high = spec["legacy_road"]["south_north_limits_m"]
    # Compare coordinates because the Quad patch can renumber base nodes.
    endpoints = graph["nodes_enu_m"]
    segments = []
    for a, b, _, kind in graph["edges"]:
        pair = [endpoints[a], endpoints[b]]
        if (
            kind == "road"
            and all(line.distance(Point(p)) < 0.004 for p in pair)
            and low <= sum(p[1] for p in pair) / 2 <= high
        ):
            segments.append(pair)
    assert len(segments) > 20
    return segments


def rendered_road_footprint(bounds, legacy):
    path = site.scene / "paving-corridors-l2/surfaces.glb"
    assert site.pin(path) == legacy["rendered_corridor_sha256"]
    installed = trimesh.load(path, force="scene", process=False)
    frame, geometry = installed.graph["corridors-road"]
    assert np.array_equal(frame, np.eye(4))
    triangles = installed.geometry[geometry].triangles[:, :, [0, 2]] * [1, -1]
    low, high = np.array(bounds.bounds).reshape(2, 2)
    nearby = ((triangles.max(1) >= low) & (triangles.min(1) <= high)).all(1)
    return unary_union(
        [
            Polygon(triangle).intersection(bounds)
            for triangle in triangles[nearby]
            if Polygon(triangle).area > 0.000001
        ]
    )


def walk_footprint(row):
    line = LineString(row["points"])
    half = row["width_m"] / 2
    if row.get("square_end"):
        return line.buffer(half, cap_style="flat").union(Point(row["points"][0]).buffer(half))
    return line.buffer(half)


def footprints(spec, manifest, metadata):
    buildings, obstacles = green.east.build_blockers(
        site.scene, spec, manifest, box(*spec["extent"])
    )
    city_spec = site.read(metadata / "east-18th-west-approach.json")
    city, _, _ = east18.site_footprints(city_spec, manifest, metadata)
    city_road, city_parking, city_walk, city_access, city_beds = city
    green_spec = site.read(metadata / "southwest-campus-green.json")
    green_buildings, _ = green.east.build_blockers(
        site.scene, green_spec, manifest, box(*green_spec["extent"])
    )
    _, lot_walk, lot_parking, lot_beds = green.surface_footprints(
        green_spec, green_buildings
    )
    keep = unary_union(
        [city_road, city_parking, city_walk, *city_beds, lot_walk, lot_parking, *lot_beds]
    )
    blocked = buildings.union(obstacles)
    clear = keep.union(blocked)
    beds = [
        Polygon(row["outline"]).difference(clear)
        for row in [*spec["islands"], spec["entry_bed"]]
    ]
    bed_footprint = unary_union(beds)
    walks = unary_union(
        [
            Polygon(spec["building_apron_enu_m"]),
            *(
                walk_footprint(row) for row in spec["walks"]
            ),
        ]
    ).difference(clear.union(bed_footprint))
    drive = Polygon(spec["asphalt_outline_enu_m"]).difference(
        unary_union([clear, bed_footprint, walks])
    )
    drive = unary_union([part for part in get_parts(drive) if part.area > 0.3])
    legacy = spec["legacy_road"]
    low, high = legacy["south_north_limits_m"]
    edge = box(spec["extent"][0], low, legacy["east_limit_m"], high)
    verge = (
        rendered_road_footprint(edge, legacy)
        .buffer(legacy["verge_blend_m"], quad_segs=4)
        .intersection(edge)
        .difference(unary_union([clear, bed_footprint, walks, drive]))
    )
    return drive, walks, beds, city_access, blocked, verge, lot_walk.union(lot_parking)


def raised_curb(parts, field, outline, color, top=0.197):
    for piece in site.landscape.geometry.sections(outline):
        mesh = site.landscape.cap(piece, 0.015, top, color)
        mesh.vertices[:, 1] += [
            site.ground_height(field, east, -south)
            for east, _, south in mesh.vertices
        ]
        parts.append(mesh)


def paint(parts, field, spec, drive):
    def drape(shape, color, lift):
        site.drape(parts, field, shape.intersection(drive), color, ASPHALT_LIFT + lift, 0.45)

    aisle = Polygon(spec["access_aisle_enu_m"])
    lines = unary_union(
        [
            LineString(row).buffer(0.049, cap_style="flat")
            for row in spec["stall_stripes"]
        ]
    ).difference(aisle)
    drape(lines, (203, 177, 108), 0.013)
    start, end = aisle.exterior.coords[:2]
    stripes = []
    for i in range(1, 10):
        ratio = i / 10
        e = start[0] + ratio * (end[0] - start[0])
        n = start[1] + ratio * (end[1] - start[1])
        stripes.append(
            LineString([(e - 2.7, n - 0.15), (e + 2.7, n + 0.15)]).buffer(0.055)
        )
    hatch = aisle.boundary.buffer(0.052).union(unary_union(stripes).intersection(aisle))
    drape(hatch, (228, 224, 211), 0.016)

    wheel = Point(-0.075, -0.08).buffer(0.24).difference(
        Point(-0.075, -0.08).buffer(0.17).union(box(0.03, -0.07, 0.2, 0.25))
    )
    body = LineString(
        [(0.04, 0.27), (0.05, -0.02), (0.24, -0.02), (0.32, -0.22)]
    ).buffer(0.031)
    person = wheel.union(body).union(Point(0.04, 0.34).buffer(0.058))
    for e, n, heading in spec["access_symbols"]:
        def orient(shape):
            return translate(rotate(shape, heading, origin=(0, 0)), e, n)

        drape(orient(box(-0.54, -0.54, 0.54, 0.54)), (76, 116, 151), 0.017)
        drape(orient(person), (231, 232, 221), 0.023)
    return round(aisle.intersection(drive).area, 2)


def append_predecessor(graph, directory):
    entry = site.read(site.scene / directory / "site.json")
    graph["nodes_enu_m"].extend(
        point
        for path in entry["walkable_ground"]["paths"]
        for point in path["points_enu_m"]
    )


def route_line(path):
    end = [path["end_enu_m"]] if "end_enu_m" in path else []
    return LineString([path["anchor_enu_m"], *path["points_enu_m"], *end])


def build(spec, metadata, stage, audit):
    manifest, field, graph = green.east.pinned_site(site.scene, spec)
    drive, walks, beds, city_access, blockers, verge, lot_access = footprints(
        spec, manifest, metadata
    )
    retired_segments = retired_road_segments(spec, manifest, graph)
    assert drive.is_valid and drive.area > 900 and walks.is_valid and walks.area > 55
    closed = [island.bounds for island in beds[:-1]]
    for parent in (east18.PACKAGE, green.PACKAGE):
        append_predecessor(graph, parent)
    access = walks.union(city_access)
    drive_access = access.union(drive).union(lot_access)
    edges, lengths = green.west.check_routes(
        graph, spec["routes"], drive_access,
        blockers.union(unary_union([box(*bounds) for bounds in closed])),
    )
    for branch, surface in zip(
        spec["routes"], [access, access, drive_access], strict=True
    ):
        outside = route_line(branch).difference(surface.buffer(0.13))
        assert outside.length < 0.01, outside.wkt

    ground, sidewalk, detail, plants = [], [], [], []
    site.drape(ground, field, drive, green.ASPHALT, ASPHALT_LIFT, 0.92)
    site.drape(
        ground, field, verge, tuple(spec["legacy_road"]["turf_color_srgb"]), 0.087, 0.72
    )

    def sidewalk_height(east, north):
        point = Point(east, north)
        ramp = max(0.0, 1 - point.distance(Point(-536.03, -587.03)) / 1.65)
        return site.ground_height(field, east, north) + WALK_LIFT - ramp * (WALK_LIFT - ASPHALT_LIFT)

    site.landscape.top_surface(sidewalk, walks, sidewalk_height, green.CONCRETE, cell=0.53)
    for i, (row, bed) in enumerate(zip([*spec["islands"], spec["entry_bed"]], beds, strict=True)):
        assert bed.geom_type == "Polygon" and bed.area > 3
        site.drape(ground, field, bed, (128, 113, 87), 0.117, 0.68)
        if i < len(closed):
            raised_curb(detail, field, bed.boundary.buffer(0.072), (159, 149, 126))
        for e, n, spread in row["shrubs"]:
            assert bed.covers(Point(e, n))
            z = site.ground_height(field, e, n) + 0.117
            site.orb(plants, (e, n, z + spread * 0.42), (spread, spread, spread * 0.54), (107, 127, 75))
    curbs = unary_union([LineString(row) for row in spec["red_curbs"]])
    red_curb_footprint = curbs.buffer(
        0.078, cap_style="flat", join_style="mitre"
    ).difference(blockers)
    for branch in spec["routes"]:
        distance = route_line(branch).distance(red_curb_footprint)
        assert distance > 0.64, (branch["anchor_enu_m"], distance)
    raised_curb(detail, field, red_curb_footprint, (154, 71, 60))
    hatch_area = paint(detail, field, spec, drive)
    assert hatch_area > 10

    stage.mkdir(parents=True, exist_ok=True)
    model, descriptor = stage / "site.glb", stage / "site.json"
    faces = site.export(
        model,
        (DRIVE, ground, "landscape-surface"),
        (WALK, sidewalk, "landscape-surface"),
        (DETAIL, detail, "landscape-detail"),
        (PLANTS, plants, "landscape-vegetation"),
        surface_layer=DRIVE,
    )
    pins = spec["pins"]
    site.fairmount.write_json(
        descriptor,
        {
            "source_presentation_sha256": pins["presentation"],
            "source_base_model_sha256": pins["model"],
            "source_heightfield_sha256": pins["heightfield"],
            "source_navigation_sha256": pins["navigation"],
            "prerequisite_site_sha256": pins["sites"][east18.PACKAGE],
            "ground_node": DRIVE,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(model),
            "buildings": [],
            "walkable_ground": {
                "bounds_enu_m": spec["walkable_bounds"],
                "paths": spec["routes"],
            },
            "closed_site_boxes_enu_m": closed,
        },
        compact=True,
    )
    report = {
        "drive_m2": round(drive.area, 2),
        "walk_m2": round(walks.area, 2),
        "planting_m2": round(sum(bed.area for bed in beds), 2),
        "verge_m2": round(verge.area, 2),
        "retired_route_edges": len(retired_segments),
        "red_curb_m": round(curbs.length, 2),
        "access_aisle_m2": hatch_area,
        "route_edges": edges,
        "route_lengths_m": lengths,
        "shared_drive_length_m": lengths[-1],
        "faces": faces,
        "asset_sha256": site.pin(model),
        "descriptor_sha256": site.pin(descriptor),
    }
    site.fairmount.write_json(audit, report)
    print(report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    build(site.read(metadata / "frohnmayer-east-drive.json"), metadata, args.stage, args.audit)


if __name__ == "__main__":
    main()
