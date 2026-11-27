# SPDX-License-Identifier: Apache-2.0
"""Register Southwest Campus Green and the south approach to Knight Library."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

east = import_module("build-east-thirteenth-east")
site, west = east.site, east.west
PACKAGE = "southwest-campus-green-review"
GROUND = "southwest-campus-green-paving"
DETAIL = "southwest-campus-green-furnishings"
PLANTING = "southwest-campus-green-planting"
CONCRETE = (175, 169, 154)
SOIL = (118, 99, 77)
METAL = (59, 70, 60)
ASPHALT = (130, 127, 118)


def surface_footprints(spec, buildings):
    beds = [Polygon(outline).difference(buildings) for outline in spec["beds"]]
    beds = [bed for bed in beds if bed.area > 1]
    soil = unary_union(beds)
    paths = unary_union(
        [
            LineString(row["line"]).buffer(row["width"] / 2, cap_style="flat")
            for row in spec["walks"]
        ]
    )
    terrace = Polygon(spec["terrace"])
    open_space = buildings.union(soil)
    walks = paths.union(terrace).difference(open_space)
    parking = Polygon(spec["parking"]).difference(open_space.union(walks))
    lawn = Polygon(spec["lawn"]).difference(open_space.union(walks).union(parking))
    assert lawn.area > 4800 and walks.area > 750 and parking.area > 750
    return lawn, walks, parking, beds


def surfaces(ground, field, spec, buildings, approach):
    lawn, walks, parking, beds = surface_footprints(spec, buildings)
    site.drape(ground, field, lawn, (146, 161, 100), 0.066, 1.8)
    site.drape(ground, field, parking, ASPHALT, 0.094, 1.12)
    site.drape(ground, field, walks.difference(approach), CONCRETE, 0.126, 1.12)
    for bed in beds:
        site.drape(ground, field, bed, SOIL, 0.117, 0.78)
    return lawn, walks, parking, beds


def markings(detail, field, spec, parking, *, stall_color=(179, 151, 84)):
    spans = [
        LineString([(x, row["south"]), (x, row["north"])])
        for row in spec["stalls"]
        for x in row["eastings"]
    ]
    bay_shapes = [box(*xy) for xy in spec["access_aisles"]]
    aisles = unary_union(bay_shapes)
    lines = unary_union(spans).buffer(0.046, cap_style="flat")
    site.drape(
        detail,
        field,
        lines.intersection(parking).difference(aisles),
        stall_color,
        0.137,
        0.75,
    )
    for band in bay_shapes:
        x0, y0, x1, y1 = band.bounds
        hatches = (
            unary_union(
                [
                    LineString([(x0 - 1, y), (x1 + 1, y + 2.2)])
                    for y in np.arange(y0 - 2.1, y1, 0.61)
                ]
            )
            .buffer(0.043)
            .intersection(band)
        )
        stripe = band.boundary.buffer(0.042).union(hatches).intersection(parking)
        site.drape(detail, field, stripe, (204, 204, 187), 0.142, 0.73)
    for x, n in spec["access_centers"]:
        blue = box(x - 0.56, n - 0.48, x + 0.56, n + 0.48).intersection(parking)
        arcs = LineString(
            [
                (x - 0.07, n + 0.16),
                (x - 0.23, n + 0.05),
                (x - 0.23, n - 0.15),
                (x - 0.13, n - 0.25),
                (x + 0.06, n - 0.24),
                (x + 0.18, n - 0.13),
            ]
        ).buffer(0.029)
        figure = LineString(
            [
                (x + 0.02, n + 0.25),
                (x + 0.045, n - 0.01),
                (x + 0.23, n - 0.01),
                (x + 0.32, n - 0.21),
            ]
        ).buffer(0.029)
        head = Point(x + 0.01, n + 0.31).buffer(0.047)
        site.drape(detail, field, blue, (76, 116, 151), 0.136, 0.6)
        site.drape(
            detail,
            field,
            arcs.union(figure).union(head).intersection(blue),
            (213, 217, 204),
            0.143,
            0.56,
        )
    return len(spans)


def furnishings(detail, field, spec, concrete, built):
    boxes = []
    for x, n in spec["benches"]:
        foot = box(x - 0.83, n - 0.26, x + 0.83, n + 0.26)
        assert built.distance(foot) > 0.05 and concrete.buffer(0.13).covers(foot)
        z = site.ground_height(field, x, n) + 0.12
        for offset in (-0.63, 0.63):
            site.flat_box(detail, x + offset, n, 0.095, 0.38, z - 0.04, z + 0.43, METAL)
        for i in range(4):
            site.flat_box(
                detail,
                x,
                n + 0.112 * (i - 1.5),
                1.66,
                0.084,
                z + 0.41,
                z + 0.466,
                (139, 107, 78),
            )
        site.flat_box(
            detail, x, n + 0.22, 1.66, 0.072, z + 0.69, z + 0.88, (152, 119, 85)
        )
        for offset in (-0.63, 0.63):
            site.flat_box(
                detail, x + offset, n + 0.209, 0.055, 0.08, z + 0.43, z + 0.72, METAL
            )
        boxes.append(foot)
    for x, n in spec["lamps"]:
        z = site.ground_height(field, x, n)
        site.cylinder_between(
            detail, (x, n, z - 0.04), (x, n, z + 3.24), 0.062, METAL, sides=10
        )
        site.orb(detail, (x, n, z + 3.39), (0.175, 0.175, 0.191), (219, 218, 192))
        boxes.append(box(x - 0.095, n - 0.095, x + 0.095, n + 0.095))
    x, n = spec["parking_board"]
    z = site.ground_height(field, x, n)
    site.cylinder_between(
        detail, (x, n, z - 0.08), (x, n, z + 1.46), 0.04, METAL, sides=8
    )
    site.flat_box(detail, x, n, 0.49, 0.074, z + 1.09, z + 1.52, (59, 85, 67))
    site.text_strokes(
        detail,
        "LOT 20",
        lambda u, h: (x + u, n - 0.043, z + 1.32 + h),
        0.054,
        0.081,
        (223, 220, 200),
    )
    boxes.append(box(x - 0.14, n - 0.13, x + 0.14, n + 0.13))
    return boxes


def parking_curbs(detail, field, spec):
    length = 0.0
    for row in spec["curbs"]:
        line = LineString(row["line"])
        length += line.length
        for index, (first, last) in enumerate(zip(line.coords, list(line.coords)[1:])):
            footprint = site.landscape.rect_on(first, last, 0.158)
            color = (
                (177, 147, 79)
                if row["paint"] == "yellow-tip" and index < 2
                else (163, 155, 138)
            )
            curb = site.landscape.cap(footprint, -0.025, 0.196, color)
            curb.vertices[:, 1] += [
                site.ground_height(field, e, -z) for e, _, z in curb.vertices
            ]
            detail.append(curb)
    return round(length, 2)


def plantings(detail, field, trees, beds, *, spacing=(0.86, 0.68)):
    greens = [
        (111, 125, 72),
        (137, 137, 79),
        (94, 117, 67),
        (121, 139, 84),
        (102, 128, 73),
    ]
    count = 0
    for index, bed in enumerate(beds):
        x0, n0, x1, n1 = bed.bounds
        inner = bed.buffer(-0.24)
        for i, e in enumerate(np.arange(x0 + 0.4, x1, spacing[0])):
            for j, n in enumerate(np.arange(n0 + 0.42, n1, spacing[1])):
                x = e + 0.14 * np.sin(index + j * 1.73 + i)
                north = n + 0.11 * np.cos(index + i * 1.19 + j)
                if not inner.covers(Point(x, north)):
                    continue
                seed = (index * 3 + i * 7 + j * 3) % 11
                radius = 0.31 + 0.021 * seed
                z = site.ground_height(field, x, north)
                color = greens[seed % len(greens)]
                site.orb(
                    detail,
                    (x, north, z + 0.29),
                    (radius, radius * 0.82, radius * 0.72),
                    color,
                )
                count += 1
    for index, row in enumerate(trees):
        site.canopy(detail, field, row, index)
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    spec = site.read(metadata / "southwest-campus-green.json")
    scene = site.scene
    manifest, field, graph = east.pinned_site(scene, spec)
    buildings, closed = east.build_blockers(scene, spec, manifest, box(*spec["extent"]))
    cemetery = site.read(metadata / "pioneer-cemetery-landscape-review.json")
    approach = Polygon(cemetery["northwest_refinement"]["west_approach_outline_enu_m"])
    clip = spec["pilot_tree_clip"]
    assert clip["source_legacy_sha256"] == spec["pins"]["presentation"]
    assert clip["source_refined_sha256"] == site.pin(scene / "pilot-trees-l2/trees.glb")

    ground, details, plants = [], [], []
    lawn, walks, parking, beds = surfaces(ground, field, spec, buildings, approach)
    assert all(
        parking.distance(Point(row["position_enu_m"])) > 0.28 for row in spec["trees"]
    )
    lines = markings(details, field, spec, parking)
    curb_length = parking_curbs(details, field, spec)
    furniture_boxes = furnishings(details, field, spec, walks, buildings)
    shrubs = plantings(plants, field, spec["trees"], beds)
    assert len(furniture_boxes) <= 16
    trees = unary_union(
        [Point(row["position_enu_m"]).buffer(0.21) for row in spec["trees"]]
    )
    cemetery_site = site.read(scene / "pioneer-cemetery-landscape-review/site.json")
    predecessor_points = [
        point
        for row in cemetery_site["walkable_ground"]["paths"]
        for point in row["points_enu_m"]
    ]
    navigation = {"nodes_enu_m": [*graph["nodes_enu_m"], *predecessor_points]}
    blocked = unary_union([closed, buildings, trees, *furniture_boxes])
    edges, lengths = west.check_routes(
        navigation, spec["routes"], walks.union(approach), blocked
    )
    assert all(
        LineString([branch["anchor_enu_m"], *branch["points_enu_m"]]).distance(
            unary_union(furniture_boxes).union(closed)
        )
        > 0.50
        for branch in spec["routes"]
    )
    args.stage.mkdir(exist_ok=True, parents=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        (DETAIL, details, "landscape-detail"),
        (PLANTING, plants, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    p = spec["pins"]
    descriptor = args.stage / "site.json"
    site.fairmount.write_json(
        descriptor,
        {
            "source_presentation_sha256": p["presentation"],
            "source_base_model_sha256": p["model"],
            "source_heightfield_sha256": p["heightfield"],
            "source_navigation_sha256": p["navigation"],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(glb),
            "buildings": [],
            "walkable_ground": {
                "bounds_enu_m": spec["bounds"],
                "paths": spec["routes"],
            },
            "closed_site_boxes_enu_m": [b.bounds for b in furniture_boxes],
            "context_trees": spec["clear_context_trees"],
            "pilot_tree_clip": clip,
        },
        compact=True,
    )
    audit = {
        "lawn_m2": round(lawn.area, 2),
        "walks_m2": round(walks.difference(approach).area, 2),
        "parking_m2": round(parking.area, 2),
        "beds": len(beds),
        "bed_m2": round(sum(b.area for b in beds), 2),
        "parking_dividers": lines,
        "parking_curb_m": curb_length,
        "accessible_symbols": len(spec["access_centers"]),
        "route_edges": edges,
        "route_lengths_m": lengths,
        "registered_trees": len(spec["trees"]),
        "low_plants": shrubs,
        "context_removals": [row["index"] for row in spec["clear_context_trees"]],
        "pilot_removals": clip["tree_indices"],
        "faces": faces,
        "asset_sha256": site.pin(glb),
        "descriptor_sha256": site.pin(descriptor),
    }
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
