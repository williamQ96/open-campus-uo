# SPDX-License-Identifier: Apache-2.0
"""Reconstruct the southern University Street corridor and cemetery approaches."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.affinity import rotate, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

practice = import_module("build-hayward-practice-fields")
east, site, west, central = (
    practice.east,
    practice.site,
    practice.west,
    practice.central,
)
agate = practice.agate
PACKAGE = "university-south-axis-review"
GROUND = "university-south-axis-paving"
MARKINGS = "university-south-axis-markings"
DETAIL = "university-south-axis-furnishings"
PLANTING = "university-south-axis-planting"
ASPHALT = (130, 128, 119)
WALK = (175, 170, 155)
CURB = (163, 158, 141)
IRON = (66, 84, 66)


def band(rows):
    return agate.agate.longitudinal_band(list(reversed(rows)))


def street(parts, field, spec, buildings):
    footprint = band(spec["paving_road"]).difference(buildings)
    west_walk = band(spec["west_walk"])
    east_walk = band(spec["east_walk"])
    joins = west.surface(spec["approach_paving"])
    walks = west_walk.union(east_walk).union(joins).difference(buildings)
    trees = []
    for row in spec["tree_inventory"]:
        loc = Point(*row["position_enu_m"])
        if buildings.distance(loc) > 0.36:
            trees.append(row)
    tree_pits = unary_union(
        [
            Point(*row["position_enu_m"]).buffer(
                0.76 if row["height_m"] < 8 else 0.65, quad_segs=10
            )
            for row in trees
        ]
    )
    threshold = box(-327.6, -388.98, -319.61, -386.6)
    walkway = walks.difference(
        footprint.difference(joins).union(tree_pits).union(threshold)
    )
    road = footprint.difference(tree_pits.union(walkway))
    curb = (
        footprint.buffer(0.145)
        .difference(footprint.union(tree_pits))
        .difference(joins)
        .intersection(box(-324, -584.69, -292, -254.7))
    )
    islands = tree_pits.intersection(footprint.union(walks))
    soil = islands.buffer(-0.105)
    for shape, tint, lift, cell in (
        (road, ASPHALT, 0.093, 1.55),
        (walkway, WALK, 0.137, 1.07),
        (curb, CURB, 0.175, 0.84),
        (islands.difference(soil), CURB, 0.187, 0.6),
        (soil, (132, 114, 82), 0.127, 0.63),
    ):
        if not shape.is_empty:
            site.drape(parts, field, shape, tint, lift, cell)
    return road, walkway, trees, threshold


def parking_lines(spec, groups, edge):
    lines = []
    spans = np.asarray(spec["paving_road"])
    for south, north, pitch in groups:
        for y in np.arange(south, north, pitch):
            outer = float(np.interp(y, spans[:, 0], spans[:, edge]))
            inward = 1 if edge == 1 else -1
            lines.append([(outer + 0.14 * inward, y), (outer + 4.55 * inward, y)])
    return lines


def markings(parts, field, spec, road):
    west_rows = parking_lines(spec, spec["west_parking_groups"], 1)
    east_rows = parking_lines(spec, spec["east_parking_groups"], 2)
    pairs = central.buffered_lines(spec["crosswalk_lines"], 0.202)
    center = LineString(spec["centerline"])
    dashed = [
        [
            center.interpolate(d).coords[0],
            center.interpolate(min(d + 3.5, center.length)).coords[0],
        ]
        for d in np.arange(0.2, center.length - 0.1, 11.8)
    ]
    walk_stripes = []
    for e0, n0, e1, n1 in spec["paint_zones"]:
        for e in np.arange(e0 - 2, e1, 0.47):
            walk_stripes.append([(e, n0), (e + 2.2, n1)])
    hatches = central.buffered_lines(walk_stripes, 0.115).intersection(
        unary_union([box(*bounds) for bounds in spec["paint_zones"]])
    )
    for shape, tint, lift in (
        (pairs, (222, 218, 198), 0.164),
        (central.buffered_lines(west_rows, 0.112), (186, 160, 88), 0.151),
        (
            central.buffered_lines(east_rows, 0.115).union(hatches),
            (203, 199, 179),
            0.152,
        ),
        (central.buffered_lines(dashed, 0.115), (176, 149, 83), 0.151),
    ):
        clipped = shape.intersection(road)
        if not clipped.is_empty:
            site.drape(parts, field, clipped, tint, lift, 0.89)
    icon = agate.bicycle()
    for e, n, angle in (
        (-308.8, -545.2, 180),
        (-304.75, -472.2, 0),
        (-305.55, -371.35, 0),
    ):
        paint = translate(rotate(icon, angle, origin=(0, 0)), e, n)
        site.drape(parts, field, paint.intersection(road), (187, 193, 167), 0.153, 0.75)
    return len(west_rows), len(east_rows)


def furniture(parts, field, spec):
    solids = []
    for row in spec["lights"]:
        e, n = row["position"]
        if row["kind"] != "lamp":
            solids.append(agate.fixture(parts, field, row))
            continue
        z = site.ground_height(field, e, n)
        site.flat_box(parts, e, n, 0.255, 0.255, z - 0.005, z + 0.33, IRON)
        site.cylinder_between(
            parts, (e, n, z + 0.3), (e, n, z + 4.24), 0.053, IRON, sides=9
        )
        site.orb(parts, (e, n, z + 4.32), (0.176, 0.176, 0.21), (222, 213, 184))
        solids.append(box(e - 0.125, n - 0.125, e + 0.125, n + 0.125))
    for row in spec["fences"]:
        solids.extend(practice.fence_run(parts, field, row["line"], row["height"]))
    return solids


def overlaps(prior_square, prior_cemetery, prior_howe, rankin):
    surface = west.surface(prior_square["hardscape"]).union(
        Polygon(prior_square["brick_cross"])
    )
    surface = surface.union(Polygon(prior_square["university_entry"]))
    surface = surface.union(box(-327.6, -388.98, -318.66, -386.6))
    surface = surface.union(
        LineString(rankin["centerline_enu_m"]).buffer(rankin["width_m"] / 2)
    )
    # Existing road approaches are retained for the stair and main stadium entrance.
    surface = surface.union(
        LineString(
            [
                prior_cemetery["walkable_ground"]["paths"][0]["anchor_enu_m"],
                [-318.93, -387.79],
            ]
        ).buffer(0.84)
    )
    path = prior_howe["walkable_ground"]
    return surface.union(
        LineString([path["anchor_enu_m"], path["points_enu_m"][0]]).buffer(0.95)
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(site.root / "data/metadata/university-south-axis.json")
    prior = site.read(site.root / "data/metadata/hayward-square-track.json")
    cem = site.read(site.scene / "pioneer-cemetery-landscape-review/site.json")
    rankin = site.read(
        site.root / "data/metadata/pioneer-cemetery-landscape-review.json"
    )["rankin_fringe"]["sidewalk"]
    howe = site.read(site.scene / "howe-field-gates-review/site.json")
    manifest, field, graph = east.pinned_site(site.scene, spec)
    buildings, old_boxes = east.build_blockers(
        site.scene, spec, manifest, box(*spec["bounds"])
    )
    ground, paint, details, planting = [], [], [], []
    road, walks, trees, stair = street(ground, field, spec, buildings)
    parking = markings(paint, field, spec, road)
    boxes = furniture(details, field, spec)
    assert len(boxes) <= 16
    for index, row in enumerate(trees):
        site.canopy(planting, field, row, index)
    trunks = unary_union([Point(*row["position_enu_m"]).buffer(0.23) for row in trees])
    edges, lengths = west.check_routes(
        graph,
        spec["routes"],
        walks.union(road).union(overlaps(prior, cem, howe, rankin)).union(stair),
        buildings.union(old_boxes).union(unary_union(boxes)).union(trunks),
    )
    # The browser expands each closed site box by 0.5 m when linking routes.
    padded_boxes = unary_union([part.buffer(0.501, join_style=2) for part in boxes])
    for path in spec["routes"]:
        points = [path["anchor_enu_m"], *path["points_enu_m"]]
        if "end_enu_m" in path:
            points.append(path["end_enu_m"])
        assert not LineString(points).intersects(padded_boxes), points
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        (MARKINGS, paint, "landscape-detail"),
        (DETAIL, details, "landscape-detail"),
        (PLANTING, planting, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    pins = spec["pins"]
    descriptor = args.stage / "site.json"
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
            context_trees=spec.get("clear_context_trees", []),
            walkable_ground=dict(
                paths=spec["routes"],
                bounds_enu_m=[
                    [-325, -585, -288, -505],
                    [-324, -506, -287, -425],
                    [-324, -426, -287, -345],
                    [-324, -346, -287, -265],
                    [-323, -266, -291, -237],
                ],
            ),
            closed_site_boxes_enu_m=[
                [round(x, 4) for x in part.bounds] for part in boxes
            ],
        ),
        compact=True,
    )
    audit = dict(
        road_m2=round(road.area, 2),
        sidewalk_m2=round(walks.area, 2),
        parking_strokes=list(parking),
        trees=[tree["tree_id"] for tree in trees],
        cleared_context=[row["index"] for row in spec.get("clear_context_trees", [])],
        fixtures=len(spec["lights"]),
        fence_m=round(sum(LineString(row["line"]).length for row in spec["fences"]), 2),
        route_edges=edges,
        route_lengths_m=lengths,
        faces=faces,
        asset_sha256=site.pin(glb),
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
