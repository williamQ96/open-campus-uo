# SPDX-License-Identifier: Apache-2.0
"""Build the East 18th west sidewalks, street crossings and clinic south apron."""

import argparse
from importlib import import_module
from pathlib import Path

from shapely.affinity import translate
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

dropoff = import_module("build-clinical-dropoff-landscape")
green, site = dropoff.green, dropoff.site
cemetery = import_module("build-pioneer-cemetery-landscape-review")
PACKAGE = "east-eighteenth-west-approach-review"
GROUND = "east-18th-west-paving"
DETAIL = "east-18th-west-markings"
PLANTING = "east-18th-west-planting"
ROAD_LIFT, PARKING_LIFT, WALK_LIFT = 0.103, 0.123, 0.151
WHITE = (221, 219, 201)


def crossing_band(row, approach=0.0):
    south, north = row["south_north_m"]
    half = row["width_m"] / 2 + 0.21
    east = row["center_east_m"]
    return box(east - half, south - approach, east + half, north + approach)


def footprints(spec, blockers, cemetery_walk):
    street = Polygon(spec["asphalt_outline_enu_m"])
    parking = Polygon(spec["parking_outline_enu_m"])
    beds = [Polygon(row["outline"]) for row in spec["beds"]]
    assert all(shape.is_valid for shape in [street, parking, *beds])
    blocked = blockers.union(unary_union(beds)).union(cemetery_walk)
    street = street.difference(blocked)
    parking = parking.difference(blocked.union(street))
    side_street_mouths = unary_union(
        [box(*a, *b) for a, b in spec["unmarked_crossings"]]
    )
    walks = unary_union(
        [
            LineString(row["points"]).buffer(row["width_m"] / 2, cap_style="square")
            for row in spec["walks"]
        ]
    ).difference(blocked)
    street_crossings = unary_union(
        [
            crossing_band(row, 1.42)
            for row in spec["crossings"]
            if row["paving"] == "street"
        ]
    )
    parking_crossing = unary_union(
        [crossing_band(row) for row in spec["crossings"] if row["paving"] == "parking"]
    )
    crossing_approaches = street_crossings.difference(blocked)
    # Side-street mouths use the traced sidewalk width as their walking corridor.
    street_walk = street_crossings.union(
        walks.intersection(side_street_mouths)
    ).intersection(street)
    parking_walk = parking_crossing.intersection(parking)
    sidewalk = walks.union(crossing_approaches).difference(
        street_walk.union(parking_walk)
    )
    street = street.difference(sidewalk)
    parking = parking.difference(sidewalk)
    access = unary_union([sidewalk, street_walk, parking_walk])
    return street, parking, sidewalk, access, beds


def walk_height(field, spec, cemetery_walk, street, parking, e, n):
    lift = WALK_LIFT
    point = site.Point(e, n)
    if n > -603 and e > -516:
        blend = min(1.0, cemetery_walk.distance(point) / 2.0)
        lift = 0.097 + blend * (WALK_LIFT - 0.097)
    for row in spec["crossings"]:
        if abs(e - row["center_east_m"]) > row["width_m"] / 2 + 0.22:
            continue
        south, north = row["south_north_m"]
        if south - 2.8 <= n <= north + 2.8:
            surface, base = (
                (street, ROAD_LIFT)
                if row["paving"] == "street"
                else (parking, PARKING_LIFT)
            )
            blend = min(1.0, surface.distance(point) / 1.3)
            lift = min(lift, base + blend * (WALK_LIFT - base))
    return site.ground_height(field, e, n) + lift


def paint(parts, field, spec, street, parking):
    lines = spec["paint"]
    middle = LineString(lines["centerline_enu_m"])
    break_mask = unary_union(
        [box(a, -615, b, -602) for a, b in lines["centerline_breaks_e_m"]]
    )
    yellow = unary_union(
        [
            translate(middle, yoff=offset).buffer(0.060, cap_style="flat")
            for offset in (-0.125, 0.125)
        ]
    ).difference(break_mask)
    bike = [
        translate(middle, yoff=lines[f"bike_white_{side}_offset_m"]).buffer(
            0.069, cap_style="flat"
        )
        for side in ("north", "south")
    ]
    # The marked crossings and turning mouths interrupt the bike edge lines.
    gaps = unary_union(
        [box(a, -615, b, -602) for a, b in lines["bike_line_breaks_e_m"]]
    )
    street_white = (
        unary_union(bike).difference(gaps).union(box(*lines["stop_bar_enu_m"]))
    )
    stop = translate(green.east.road_text("STOP"), *lines["stop_letters_center_enu_m"])
    bars = {"street": [street_white, stop], "parking": []}
    for row in spec["crossings"]:
        low, high = row["paint_bounds_m"]
        step = (high - low) / (row["bars"] - 1)
        e, half = row["center_east_m"], row["width_m"] / 2
        for i in range(row["bars"]):
            n = low + i * step
            bars[row["paving"]].append(box(e - half, n - 0.155, e + half, n + 0.155))
    south, north = lines["parking_stall_south_north_m"]
    for shapes, surface, color, lift in (
        (yellow, street, (207, 180, 96), ROAD_LIFT),
        (unary_union(bars["street"]), street, WHITE, ROAD_LIFT),
        (unary_union(bars["parking"]), parking, WHITE, PARKING_LIFT),
    ):
        site.drape(
            parts, field, shapes.intersection(surface), color, lift + 0.015, 0.49
        )
    green.markings(
        parts,
        field,
        {
            "stalls": [
                {"south": south, "north": north, "eastings": lines["parking_marks_e_m"]}
            ],
            "access_aisles": lines["access_aisles"],
            "access_centers": lines["access_centers"],
        },
        parking,
        stall_color=WHITE,
    )


def site_footprints(spec, manifest, metadata):
    buildings, obstacles = green.east.build_blockers(
        site.scene, spec, manifest, box(*spec["extent"])
    )
    cemetery_spec = site.read(metadata / f"{cemetery.PACKAGE}.json")
    cemetery_walk, _ = cemetery.rankin_frontage_footprint(cemetery_spec)
    surfaces = footprints(spec, buildings.union(obstacles), cemetery_walk)
    return surfaces, buildings.union(obstacles), cemetery_walk


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    spec = site.read(metadata / "east-18th-west-approach.json")
    manifest, field, graph = green.east.pinned_site(site.scene, spec)
    surfaces, blocked, cemetery_walk = site_footprints(spec, manifest, metadata)
    street, parking, sidewalk, access, beds = surfaces
    closed_boxes = [island.bounds for island in beds]
    edges, lengths = green.west.check_routes(
        graph,
        spec["routes"],
        access.union(cemetery_walk),
        blocked.union(unary_union([box(*bounds) for bounds in closed_boxes])),
    )
    for path in spec["routes"]:
        points = [path["anchor_enu_m"], *path["points_enu_m"]]
        if "end_enu_m" in path:
            points.append(path["end_enu_m"])
        uncovered = LineString(points).difference(
            access.union(cemetery_walk).buffer(0.13)
        )
        assert uncovered.length < 0.01, uncovered.wkt

    ground, markings, plants = [], [], []
    site.drape(ground, field, street, (94, 93, 89), ROAD_LIFT, 1.08)
    site.drape(ground, field, parking, (100, 97, 92), PARKING_LIFT, 0.88)
    site.landscape.top_surface(
        ground,
        sidewalk,
        lambda e, n: walk_height(field, spec, cemetery_walk, street, parking, e, n),
        (175, 170, 156),
        cell=0.68,
    )
    paint(markings, field, spec, street, parking)
    dropoff.planted_islands(ground, plants, field, {"islands": spec["beds"]}, beds)
    args.stage.mkdir(parents=True, exist_ok=True)
    asset, descriptor = (args.stage / name for name in ("site.glb", "site.json"))
    faces = site.export(
        asset,
        (GROUND, ground, "landscape-surface"),
        (DETAIL, markings, "landscape-surface"),
        (PLANTING, plants, "landscape-vegetation"),
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
            "prerequisite_site_sha256": pins["sites"][spec["prerequisite"]],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(asset),
            "buildings": [],
            "walkable_ground": {
                "bounds_enu_m": spec["walkable_bounds"],
                "paths": spec["routes"],
            },
            "closed_site_boxes_enu_m": closed_boxes,
        },
        compact=True,
    )
    report = {
        "street_m2": round(street.area, 2),
        "parking_m2": round(parking.area, 2),
        "sidewalk_m2": round(sidewalk.area, 2),
        "planting_m2": round(sum(bed.area for bed in beds), 2),
        "route_edges": edges,
        "route_lengths_m": lengths,
        "faces": faces,
        "asset_sha256": site.pin(asset),
        "descriptor_sha256": site.pin(descriptor),
    }
    site.fairmount.write_json(args.audit, report)
    print(report)


if __name__ == "__main__":
    main()
