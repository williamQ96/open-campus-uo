# SPDX-License-Identifier: Apache-2.0
"""Build East 18th Avenue along Pioneer Cemetery and tie its sidewalks to University Street."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.affinity import translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

west = import_module("build-east-18th-west-approach")
cemetery, green, site = west.cemetery, west.green, west.site
axis = import_module("build-university-south-axis")
square = import_module("build-hayward-square-track")
PACKAGE = "rankin-frontage-review"
GROUND = "rankin-frontage-paving"
MARKINGS = "rankin-frontage-markings"
WALKABLE = "rankin-frontage-walkable"
FURNISHINGS = "rankin-frontage-junction-fixtures"
WALK_COLOR = (175, 170, 156)
ROAD_COLOR = (94, 93, 89)
SOUTHGATE_ASPHALT = (127, 126, 119)


def footprints(spec, manifest, metadata):
    previous = site.read(metadata / "east-18th-west-approach.json")
    former_surfaces, _, rankin = west.site_footprints(previous, manifest, metadata)
    _, _, previous_walk, previous_access, _ = former_surfaces
    buildings, fixtures = green.east.build_blockers(
        site.scene, spec, manifest, box(*spec["extent"])
    )
    closed = buildings.union(fixtures)
    track = site.read(metadata / "hayward-square-track.json")
    junction = site.read(metadata / "southgate-junction.json")
    square_walk = square.southgate_walks(track, junction)
    square_road = square.southgate_road(track, junction, square_walk, closed)
    square_paving = square_road.union(square_walk).difference(closed)
    crossing = spec["crossing"]
    west_cross = square.crossing_corridor(junction["crossings"]["west"])
    east_cross = square.crossing_corridor(junction["crossings"]["east"])
    asphalt = Polygon(spec["asphalt_outline_enu_m"]).difference(rankin.union(closed))
    assert all(shape.is_valid for shape in (asphalt, west_cross, east_cross))
    half = spec["south_walk_width_m"] / 2
    aprons = unary_union([Polygon(row["outline_enu_m"]) for row in junction["ramps"]])
    sidewalk_trace = LineString(spec["south_sidewalk_enu_m"]).buffer(
        half, cap_style="flat"
    )
    corner = LineString(crossing["south_connection_enu_m"]).buffer(0.88)
    approaches = unary_union([sidewalk_trace, corner, west_cross]).difference(
        rankin.union(closed)
    )
    mouths = unary_union([box(*b) for b in spec["driveway_mouth_bounds_enu_m"]])
    walk_on_road = west_cross.union(sidewalk_trace.intersection(mouths)).intersection(
        asphalt
    )
    new_walk = approaches.difference(
        walk_on_road.union(previous_walk).union(square_paving)
    )
    asphalt = asphalt.difference(new_walk.union(square_paving))
    walk_on_road = walk_on_road.intersection(asphalt)
    east_entry = LineString(crossing["east_north_connection_enu_m"]).buffer(0.96)
    existing_crossing = unary_union(
        [
            west_cross,
            east_cross,
            aprons,
            east_entry,
            corner,
            square.junction_sidewalk_returns(junction),
        ]
    ).intersection(square_paving)
    coverage = unary_union([rankin, new_walk, walk_on_road, existing_crossing])
    return asphalt, new_walk, walk_on_road, rankin, coverage, previous_access, closed


def marks(parts, field, spec, road, junction):
    lines = spec["markings"]
    yellow_base = LineString(lines["double_yellow_enu_m"])
    double = unary_union(
        [
            translate(yellow_base, yoff=offset).buffer(0.060, cap_style="flat")
            for offset in (-0.125, 0.125)
        ]
    )
    breaks = unary_union([box(a, -612, b, -602) for a, b in lines["yellow_gaps_e_m"]])
    curb_spans = unary_union(
        [box(a, -603, b, -601) for a, b in lines["north_curb_paint_spans_e_m"]]
    )
    yellow = double.difference(breaks).union(
        LineString(lines["north_curb_paint_enu_m"])
        .buffer(0.066)
        .intersection(curb_spans)
    )
    north_bike = LineString(lines["north_bike_edge_enu_m"]).buffer(
        0.069, cap_style="flat"
    )
    south_bike = LineString(lines["south_bike_edge_enu_m"]).buffer(
        0.069, cap_style="flat"
    )
    gaps = unary_union(
        [box(a, -615, b, -608) for a, b in lines["south_bike_breaks_e_m"]]
    )
    turnover = [
        LineString(row).buffer(0.068, cap_style="flat")
        for row in [lines["turn_lane_edge_enu_m"], lines["south_stop_bar_enu_m"]]
    ]
    ticks = [
        LineString([(e, n - 0.34), (e, n + 0.34)]).buffer(0.047, cap_style="flat")
        for eastings, n in (
            (lines["north_stall_marks_e_m"], -603.65),
            (lines["south_stall_marks_e_m"], -615.38),
        )
        for e in eastings
    ]
    white = unary_union(
        [
            north_bike,
            south_bike.difference(gaps),
            square.junction_lane_icons(junction),
            *turnover,
            *ticks,
        ]
    )
    for area, tint in ((white, west.WHITE), (yellow, (207, 180, 96))):
        site.drape(
            parts, field, area.intersection(road), tint, west.ROAD_LIFT + 0.015, 0.55
        )


def junction_pole(parts, field, junction):
    pole = junction["pole"]
    e, n = pole["base_enu_m"]
    z = site.ground_height(field, e, n) + 0.115
    site.cylinder_between(
        parts,
        (e, n, z - 0.12),
        (e, n, z + pole["mast_height_m"]),
        0.098,
        (154, 154, 144),
    )
    sign = z + pole["sign_height_m"]
    site.flat_box(
        parts, e - 0.39, n, 0.85, 0.041, sign - 0.103, sign + 0.103, (53, 104, 155)
    )
    for side in (-1, 1):
        site.text_strokes(
            parts,
            pole["lettering"],
            lambda x, y: (e - 0.39 + side * x, n + side * 0.024, sign - 0.052 + y),
            0.046,
            0.104,
            (231, 228, 212),
        )
    signal = z + pole["signal_height_m"]
    site.flat_box(
        parts, e + 0.22, n, 0.32, 0.23, signal - 0.16, signal + 0.17, (46, 49, 45)
    )
    site.flat_box(
        parts,
        e + 0.22,
        n - 0.121,
        0.251,
        0.018,
        signal - 0.111,
        signal + 0.108,
        (64, 60, 52),
    )
    return box(e - 0.14, n - 0.14, e + 0.14, n + 0.14)


def export_site(spec, manifest, corrected, original, graph, metadata, stage):
    road, walk, walk_on_road, rankin, coverage, prior, closed = footprints(
        spec, manifest, metadata
    )
    junction = site.read(metadata / "southgate-junction.json")
    furnishings = []
    pole = junction_pole(furnishings, corrected, junction)
    donors = [west.PACKAGE, square.PACKAGE, axis.PACKAGE]
    donor_points = [
        point
        for directory in donors
        for path in site.read(site.scene / directory / "site.json")["walkable_ground"][
            "paths"
        ]
        for point in path["points_enu_m"]
    ]
    edges, lengths = green.west.check_routes(
        {"nodes_enu_m": [*graph["nodes_enu_m"], *donor_points]},
        spec["routes"],
        coverage.union(prior),
        closed.union(pole),
    )
    for path in spec["routes"]:
        points = [path["anchor_enu_m"], *path["points_enu_m"]]
        if "end_enu_m" in path:
            points.append(path["end_enu_m"])
        trace = LineString(points)
        uncovered = trace.difference(coverage.union(prior).buffer(0.13))
        assert uncovered.length < 0.005, uncovered.wkt

    paving, paint, walk_parts = [], [], []
    site.drape(paving, corrected, road, ROAD_COLOR, west.ROAD_LIFT, 1.08)
    road_mesh = paving[0]
    fade = np.clip((road_mesh.vertices[:, 0] + 343.0) / 17.3, 0, 1)[:, None]
    colors = road_mesh.visual.vertex_colors.copy()
    colors[:, :3] = np.rint(
        np.asarray(ROAD_COLOR) + fade * (np.asarray(SOUTHGATE_ASPHALT) - ROAD_COLOR)
    )
    road_mesh.visual.vertex_colors = colors
    crossing_walk = square.crossing_corridor(junction["crossings"]["west"])

    def walk_level(e, n):
        grade = site.ground_height(corrected, e, n)
        if e < -326:
            return grade + west.WALK_LIFT
        point = Point(e, n)
        road_blend = min(1.0, crossing_walk.distance(point) / 1.35)
        road_level = (
            grade + west.ROAD_LIFT + road_blend * (west.WALK_LIFT - west.ROAD_LIFT)
        )
        blend = min(1.0, rankin.distance(point) / 1.25)
        existing = cemetery.ground_height(original, e, n) + 0.097
        return existing + blend * (road_level - existing)

    site.landscape.top_surface(walk_parts, walk, walk_level, WALK_COLOR, cell=0.68)
    paving.extend(walk_parts)
    marks(paint, corrected, spec, road, junction)
    # Reproduce the original frontage tessellation for exact standing heights.
    # The installed mesh is used for sampling while the cemetery retains its visible sidewalk.
    standing = list(walk_parts)
    cemetery.drape(standing, original, rankin, (150, 147, 134), 0.097, 1.12)
    site.drape(standing, corrected, walk_on_road, ROAD_COLOR, west.ROAD_LIFT, 0.76)

    stage.mkdir(parents=True, exist_ok=True)
    asset, descriptor = (stage / name for name in ("site.glb", "site.json"))
    faces = site.export(
        asset,
        (GROUND, paving, "landscape-surface"),
        (MARKINGS, paint, "landscape-surface"),
        (WALKABLE, standing, "landscape-surface"),
        (FURNISHINGS, furnishings, "landscape-detail"),
        surface_layer=GROUND,
    )
    pins = spec["pins"]
    site.fairmount.write_json(
        descriptor,
        {
            "source_presentation_sha256": pins["presentation"],
            "source_base_model_sha256": pins["model"],
            "source_heightfield_sha256": pins["heightfield"],
            "source_navigation_sha256": pins["navigation"],
            "prerequisite_site_sha256": pins["sites"][cemetery.PACKAGE],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(asset),
            "buildings": [],
            "closed_site_boxes_enu_m": [pole.bounds],
            "walkable_ground": {
                "bounds_enu_m": spec["walkable_bounds"],
                "paths": spec["routes"],
            },
        },
        compact=True,
    )
    return {
        "asphalt_m2": round(road.area, 2),
        "new_sidewalk_m2": round(walk.area, 2),
        "existing_sidewalk_m2": round(rankin.area, 2),
        "route_edges": edges,
        "route_lengths_m": lengths,
        "faces": faces,
        "asset_sha256": site.pin(asset),
        "descriptor_sha256": site.pin(descriptor),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    spec = site.read(metadata / "rankin-frontage.json")
    manifest, corrected, graph = green.east.pinned_site(site.scene, spec)
    original = site.read(site.scene / manifest["heightfield_url"])
    report = export_site(
        spec, manifest, corrected, original, graph, metadata, args.stage
    )
    site.fairmount.write_json(args.audit, report)
    print(report)


if __name__ == "__main__":
    main()
