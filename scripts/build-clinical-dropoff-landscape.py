# SPDX-License-Identifier: Apache-2.0
"""Build HEDCO's south drop-off, Lot 19 crossings and planted islands."""

import argparse
from importlib import import_module
from pathlib import Path

from shapely.affinity import rotate, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

kendall = import_module("build-kendall-plaza-landscape")
green, site = kendall.green, kendall.site
arrow = import_module("build-east-thirteenth-central").arrow
PACKAGE = "clinical-dropoff-landscape-review"
GROUND = "clinical-dropoff-paving"
DETAIL = "clinical-dropoff-markings"
PLANTING = "clinical-dropoff-planting"
ROAD_LIFT = 0.103
WALK_LIFT = 0.151


def footprints(spec, blockers):
    drive = Polygon(spec["drive_enu_m"]).difference(blockers)
    islands = [Polygon(row["outline"]) for row in spec["islands"]]
    assert all(island.is_valid and drive.covers(island) for island in islands)
    walks = unary_union(
        [
            LineString(row["points"]).buffer(row["width_m"] / 2, cap_style="square")
            for row in spec["walks"]
        ]
    ).difference(blockers.union(unary_union(islands)))
    crossing_shapes = []
    for row in spec["crossings"]:
        south, north = row["south_north_m"]
        e = row["center_east_m"]
        # Keep the sidewalk edges outside the marked crossing on both sides.
        half = row["width_m"] / 2 + 0.21
        crossing_shapes.append(box(e - half, south, e + half, north))
    crossings = unary_union(crossing_shapes).intersection(drive)
    sidewalk = walks.difference(crossings)
    asphalt = drive.difference(sidewalk.union(unary_union(islands)))
    return asphalt, sidewalk, crossings, islands


def walk_height(field, spec, e, n):
    blend = 1.0
    for row in spec["crossings"]:
        if abs(e - row["center_east_m"]) > row["width_m"] / 2 + 0.22:
            continue
        south, north = row["south_north_m"]
        distance = max(south - n, n - north, 0)
        blend = min(blend, distance / 1.30)
    return site.ground_height(field, e, n) + ROAD_LIFT + blend * (WALK_LIFT - ROAD_LIFT)


def painted_lines(parts, field, spec, drive):
    bars, parking, hatch = [], [], []
    for item in spec["crossings"]:
        half = item["width_m"] / 2
        e = item["center_east_m"]
        south, north = item["south_north_m"]
        pitch = (north - south - 0.65) / (item["bars"] - 1)
        for i in range(item["bars"]):
            n = south + 0.325 + pitch * i
            bars.append(box(e - half, n - 0.135, e + half, n + 0.135))
    for item in spec["parking_stripes"]:
        e, n = item["start"]
        for i in range(item["count"]):
            offset = n - i * item["spacing_m"]
            parking.append(box(e, offset - 0.049, item["stop_east_m"], offset + 0.049))
    for e0, n0, e1, n1 in spec["accessible_aisles_enu_m"]:
        lane = box(e0, n0, e1, n1)
        hatch.append(lane.boundary.buffer(0.045))
        for i in range(8):
            e = e0 - 0.8 + 0.72 * i
            diagonal = LineString(((e, n1), (e + 1.05, n0)))
            hatch.append(diagonal.buffer(0.042).intersection(lane))
    directions = [
        translate(rotate(arrow(), row["heading"], origin=(0, 0)), *row["center"])
        for row in spec["arrows"]
    ]
    for shapes, color in (
        (bars + hatch + directions, (221, 219, 199)),
        (parking, (213, 189, 108)),
    ):
        surface = unary_union(shapes).intersection(drive)
        site.drape(parts, field, surface, color, ROAD_LIFT + 0.014, 0.44)


def planted_islands(ground, plants, field, spec, islands):
    for row, island in zip(spec["islands"], islands, strict=True):
        inner = island.buffer(-0.13)
        assert not inner.is_empty
        site.drape(ground, field, inner, (129, 113, 91), 0.133, 0.63)
        site.drape(ground, field, island.difference(inner), (165, 116, 100), 0.224, 0.48)
        edge = list(island.exterior.coords)
        for a, b in zip(edge, edge[1:]):
            # Narrow walls follow the curb edge up from the adjoining asphalt.
            site.cylinder_between(
                ground,
                (*a, site.ground_height(field, *a) + 0.156),
                (*b, site.ground_height(field, *b) + 0.156),
                0.071,
                (162, 118, 105),
                sides=4,
            )
        middle = inner.buffer(-0.23)
        west, south, east, north = middle.bounds
        eastings = [west + (i + 0.55) * (east - west) / 11 for i in range(11)]
        northings = [south + (i + 0.4) * (north - south) / 11 for i in range(11)]
        candidates = [
            (e, n) for e in eastings for n in northings if middle.covers(Point(e, n))
        ]
        assert len(candidates) >= row["shrubs"]
        for i in range(row["shrubs"]):
            e, n = candidates[i * len(candidates) // row["shrubs"]]
            grade = site.ground_height(field, e, n)
            color = ((107, 121, 84), (127, 133, 90), (94, 110, 76))[i % 3]
            site.orb(plants, (e, n, grade + 0.27), (0.28, 0.26, 0.21), color)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    spec = site.read(metadata / "clinical-dropoff-landscape.json")
    manifest, field, graph = green.east.pinned_site(site.scene, spec)
    bounds = box(*spec["extent"])
    blockers, prior_obstacles = green.east.build_blockers(site.scene, spec, manifest, bounds)
    asphalt, sidewalk, crossings, islands = footprints(spec, blockers)
    kendall_spec = site.read(metadata / "kendall-plaza-landscape.json")
    kendall_buildings, _ = kendall.blockers(kendall_spec, manifest)
    prior_paths, _, _, _, _ = kendall.south_lawn_footprints(kendall_spec, kendall_buildings)

    ground, markings, plants = [], [], []
    site.drape(ground, field, asphalt, (96, 94, 91), ROAD_LIFT, 1.02)
    site.landscape.top_surface(
        ground, sidewalk.difference(prior_paths),
        lambda e, n: walk_height(field, spec, e, n),
        (188, 181, 165),
        cell=0.70,
    )
    painted_lines(markings, field, spec, asphalt)
    planted_islands(ground, plants, field, spec, islands)

    donors = [
        site.read(site.scene / directory / "site.json")
        for directory in spec["navigation_predecessors"]
    ]
    anchors = [
        point
        for donor in donors
        for path in donor["walkable_ground"]["paths"]
        for point in path["points_enu_m"]
    ]
    installed_walks = sidewalk.union(crossings).union(prior_paths)
    edges, lengths = green.west.check_routes(
        {"nodes_enu_m": [*graph["nodes_enu_m"], *anchors]},
        spec["routes"],
        installed_walks,
        unary_union([blockers, prior_obstacles, *(box(*island.bounds) for island in islands)]),
    )
    for route in spec["routes"]:
        line = LineString([route["anchor_enu_m"], *route["points_enu_m"]])
        assert line.difference(installed_walks.buffer(0.13)).length < 0.01, line.wkt

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
            "prerequisite_site_sha256": pins["sites"][kendall.PACKAGE],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(asset),
            "buildings": [],
            "walkable_ground": {"bounds_enu_m": [spec["extent"]], "paths": spec["routes"]},
            "closed_site_boxes_enu_m": [island.bounds for island in islands],
        },
        compact=True,
    )
    report = {
        "asphalt_m2": round(asphalt.area, 2),
        "new_sidewalk_m2": round(sidewalk.difference(prior_paths).area, 2),
        "planting_m2": round(sum(i.area for i in islands), 2),
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
