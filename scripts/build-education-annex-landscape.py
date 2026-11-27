# SPDX-License-Identifier: Apache-2.0
"""Build the surveyed Education Annex exterior and its raised public approach."""

import argparse
from importlib import import_module
from pathlib import Path

import trimesh
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

kendall = import_module("build-kendall-plaza-landscape")
green, site = kendall.green, kendall.site
PACKAGE = "education-annex-review"
ASSET_ID = "uo-education-annex"
GROUND = "education-annex-approach"
FURNITURE = "education-annex-sign-and-planting"
SIDING = (137, 67, 54)
TRIM = (226, 219, 198)
STONE = (164, 153, 131)
ROOF = (124, 116, 105)


def main_shell(parts, spec):
    west, south, east, north = spec["body_enu_m"]
    eave, ridge = spec["eave_z_m"], spec["ridge_z_m"]
    ridge_e = spec["ridge_e_m"]
    siding = spec["siding_z_m"]
    shell = box(west, south, east, north)
    site.solid(parts, shell, spec["foundation_z_m"], siding, (131, 106, 90))
    site.solid(parts, shell, siding, eave, SIDING)
    for n in (south, north):
        vertices = [[west, eave, -n], [east, eave, -n], [ridge_e, ridge, -n]]
        face = [0, 1, 2] if n == south else [2, 1, 0]
        mesh = trimesh.Trimesh(vertices=vertices, faces=[face], process=False)
        mesh.visual.vertex_colors = [*SIDING, 255]
        parts.append(mesh)
    roof_w, roof_s, roof_e, roof_n = spec["roof_enu_m"]
    for a, b, outer in ((roof_w, ridge_e, roof_w), (ridge_e, roof_e, roof_e)):
        span = abs(ridge_e - outer)
        site.landscape.top_surface(
            parts,
            box(a, roof_s, b, roof_n),
            lambda x, n, start=outer, run=span: (
                eave + (ridge - eave) * abs(x - start) / run
            ),
            ROOF,
            cell=1.3,
        )
        site.flat_box(
            parts,
            outer,
            (roof_s + roof_n) / 2,
            0.072,
            roof_n - roof_s,
            eave - 0.11,
            eave + 0.018,
            TRIM,
        )
    for i in range(1, 17):
        height = siding + i * 0.202
        shade = (128 + (i % 3) * 3, 62 + (i % 3) * 2, 50)
        for x in (west, east):
            site.flat_box(
                parts,
                x,
                (south + north) / 2,
                0.027,
                north - south,
                height,
                height + 0.016,
                shade,
            )
        for n in (south, north):
            site.flat_box(
                parts,
                (west + east) / 2,
                n,
                east - west,
                0.027,
                height,
                height + 0.016,
                shade,
            )
    for x in (west, east):
        for n in (south, north):
            site.flat_box(parts, x, n, 0.115, 0.115, siding, eave, (186, 161, 142))
    for n in (-409.25, -411.65, -419.40, -421.22):
        window(parts, west - 0.033, n, "west")
    for n in (-409.60, -413.20, -417.0, -421.0):
        window(parts, east + 0.033, n, "east")
    for x in (-603.48, -599.85):
        window(parts, x, north + 0.033, "north")
    window(parts, -599.68, south - 0.033, "south")
    for n in (south - 0.04, north + 0.04):
        site.flat_box(parts, ridge_e, n, 0.24, 0.068, 15.82, 16.42, TRIM)
        for step in range(6):
            z = 15.88 + step * 0.077
            site.flat_box(parts, ridge_e, n, 0.16, 0.07, z, z + 0.019, (120, 114, 101))
    return shell


def window(parts, e, n, side):
    width, bottom, top = 0.86, 11.11, 12.65
    long_wall = side in ("west", "east")
    outer = -0.055 if side in ("west", "south") else 0.055

    def pane(offset, w, lower, upper, color, face=0):
        x, y = (e + face, n + offset) if long_wall else (e + offset, n + face)
        dx, dy = (0.075, w) if long_wall else (w, 0.075)
        site.flat_box(parts, x, y, dx, dy, lower, upper, color)

    pane(0, width + 0.12, bottom - 0.065, top + 0.07, TRIM)
    pane(0, width, bottom, top, (71, 93, 92), outer * 0.58)
    for offset in (-width / 6, width / 6):
        pane(offset, 0.032, bottom, top, TRIM, outer)
    for i in (1, 2, 3):
        z = bottom + (top - bottom) * i / 4
        pane(0, width, z - 0.017, z + 0.017, TRIM, outer)


def porch(ground, detail, field, spec):
    west, south, east, north = spec["porch_enu_m"]
    height = spec["porch_z_m"]
    landing = box(west, south, east, north)
    site.solid(ground, landing, height - 0.16, height, (151, 125, 95))
    post_boxes = []
    for n in (south + 0.06, north - 0.06):
        post = box(west + 0.06, n - 0.09, west + 0.24, n + 0.09)
        x = post.centroid.x
        site.solid(detail, post, site.ground_height(field, x, n) - 0.07, 13.64, TRIM)
        post_boxes.append(post)
    door = [east, -414.95]
    site.flat_box(
        detail, east - 0.018, door[1], 0.09, 1.44, height, height + 2.29, TRIM
    )
    site.flat_box(
        detail,
        east - 0.074,
        door[1],
        0.065,
        0.96,
        height,
        height + 2.13,
        (91, 112, 110),
    )
    for n in (door[1] - 0.59, door[1] + 0.59):
        site.flat_box(
            detail,
            east - 0.076,
            n,
            0.067,
            0.106,
            height + 0.29,
            height + 2.08,
            (80, 104, 102),
        )
    center = (south + north) / 2
    for a, b, outer in (
        (south - 0.18, center, south - 0.18),
        (center, north + 0.18, north + 0.18),
    ):
        site.landscape.top_surface(
            detail,
            box(west - 0.30, a, east + 0.16, b),
            lambda x, n, edge=outer: 13.61 + 1.11 * abs(n - edge) / abs(center - edge),
            ROOF,
            cell=0.72,
        )
    site.flat_box(
        detail, west - 0.05, center, 0.22, north - south + 0.32, 13.42, 13.67, TRIM
    )
    gable_e = west - 0.22
    gable = trimesh.Trimesh(
        vertices=[
            [gable_e, 13.61, -(north + 0.14)],
            [gable_e, 13.61, -(south - 0.14)],
            [gable_e, 14.67, -center],
        ],
        faces=[[0, 1, 2]],
        process=False,
    )
    gable.visual.vertex_colors = [*SIDING, 255]
    detail.append(gable)
    for n in (south - 0.15, north + 0.15):
        site.flat_box(
            detail,
            (west + east) / 2 - 0.1,
            n,
            east - west + 0.25,
            0.091,
            13.43,
            13.63,
            TRIM,
        )
    return landing, post_boxes, door


def ramp_footprints(spec):
    west, south, east, north = spec["ramp_enu_m"]
    ramp = box(west, south, east, north)
    lower = box(west - 0.05, south - 0.92, east + 0.10, south + 0.05)
    upper = box(west - 0.05, north - 0.78, spec["body_enu_m"][0], north + 0.29)
    return ramp, lower, upper


def approach_walk(spec):
    approach = LineString(spec["approach_walk_enu_m"][:5]).buffer(
        0.80, cap_style="flat"
    )
    return approach.difference(surveyed_trunks(spec).buffer(0.12))


def surveyed_trunks(spec):
    kendall_spec = site.read(site.root / "data/metadata/kendall-plaza-landscape.json")
    trees = {
        row["id"]: row
        for row in kendall_spec["trees"]
        if row["id"] in spec["tree_record_ids"]
    }
    assert set(trees) == set(spec["tree_record_ids"])
    return unary_union(
        [
            Point(row["position_enu_m"]).buffer(row["crown_radius_m"] * 0.071)
            for row in trees.values()
        ]
    )


def ramp_and_steps(ground, detail, spec):
    height = spec["porch_z_m"]
    west, south, east, north = spec["ramp_enu_m"]
    base = spec["ramp_base_z_m"]
    ramp, lower, upper = ramp_footprints(spec)

    def profile(n):
        return base + (height - base) * (n - south) / (north - south)

    site.landscape.top_surface(ground, ramp, lambda e, n: profile(n), STONE, cell=0.71)
    site.solid(ground, lower, base - 0.23, base, STONE)
    site.solid(ground, upper, height - 0.14, height, (161, 137, 109))
    rails = []
    for x in (west + 0.08, east - 0.08):
        end = north - 1.42
        rail = LineString([(x, south + 0.17), (x, end)])
        rails.append(box(*rail.buffer(0.037).bounds))
        for i in range(4):
            n = south + 0.27 + i * (end - south - 0.27) / 3
            z = profile(n)
            site.cylinder_between(
                detail, (x, n, z), (x, n, z + 0.89), 0.027, TRIM, sides=8
            )
        site.cylinder_between(
            detail,
            (x, south + 0.17, profile(south + 0.17) + 0.89),
            (x, end, profile(end) + 0.89),
            0.035,
            TRIM,
            sides=8,
        )
    x0, n0, x1, n1 = spec["steps_enu_m"]
    count = spec["stair_treads"]
    step = (n1 - n0) / count
    low = spec["steps_low_z_m"]
    for i in range(count):
        top = height - (height - low) * (i + 0.5) / count
        site.solid(
            ground,
            box(x0, n0 + i * step, x1, n0 + (i + 1) * step),
            low - 0.19,
            top,
            (158, 132, 104),
        )
    for e in (x0 + 0.12, x1 - 0.12):
        site.cylinder_between(
            detail,
            (e, n0 + 0.07, height + 0.88),
            (e, n1, low + 0.88),
            0.037,
            TRIM,
            sides=8,
        )
        for n, z in ((n0 + 0.07, height), (n1, low)):
            site.cylinder_between(
                detail, (e, n, z - 0.12), (e, n, z + 0.88), 0.028, TRIM, sides=8
            )
    return ramp.union(lower).union(upper), rails


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    spec = site.read(metadata / "education-annex-landscape.json")
    _, field, graph = green.east.pinned_site(site.scene, spec)
    parts, ground, detail = [], [], []
    shell = main_shell(parts, spec)
    porch_deck, posts, door = porch(ground, parts, field, spec)
    ramp, rails = ramp_and_steps(ground, parts, spec)
    route = spec["approach_walk_enu_m"]
    walk = approach_walk(spec).difference(ramp).difference(shell)
    site.drape(ground, field, walk, STONE, 0.145, 0.68)
    beds = [
        Polygon(ring).difference(walk.union(ramp).union(shell))
        for ring in spec["plant_beds_enu_m"]
    ]
    site.drape(ground, field, unary_union(beds), green.SOIL, 0.096, 0.83)
    shrubs = green.plantings(detail, field, [], beds)
    x, n = spec["sign_enu_m"]
    z = site.ground_height(field, x, n)
    for e in (x - 0.71, x + 0.71):
        site.flat_box(detail, e, n, 0.078, 0.078, z - 0.08, z + 1.13, (57, 75, 62))
    site.flat_box(detail, x, n, 1.50, 0.064, z + 0.63, z + 1.06, (53, 77, 62))
    site.text_strokes(
        detail,
        "EDUCATION ANNEX",
        lambda u, h: (x + u, n - 0.035, z + 0.848 + h),
        0.064,
        0.109,
        TRIM,
    )
    sign = box(x - 0.75, n - 0.05, x + 0.75, n + 0.05)
    trunks = surveyed_trunks(spec)
    assert ramp.disjoint(trunks), "The ramp footprint overlaps a registered trunk."
    obstacles = unary_union([shell, *rails, *posts, trunks, sign])
    route_line = LineString(route)
    # The viewer rejects route edges against boxes expanded by half a metre.
    for west, south, east, north in (shape.bounds for shape in [*rails, *posts, sign]):
        expanded = box(west - 0.5, south - 0.5, east + 0.5, north + 0.5)
        assert route_line.disjoint(expanded), (expanded.bounds, route_line.wkt)
    donor = site.read(site.scene / f"{kendall.PACKAGE}/site.json")
    anchors = [
        p for row in donor["walkable_ground"]["paths"] for p in row["points_enu_m"]
    ]
    paths = [dict(anchor_enu_m=route[0], points_enu_m=route[1:])]
    edges, lengths = green.west.check_routes(
        {"nodes_enu_m": [*graph["nodes_enu_m"], *anchors]},
        paths,
        walk.union(ramp).union(porch_deck),
        obstacles,
    )
    preview = trimesh.util.concatenate(parts)
    args.stage.mkdir(parents=True, exist_ok=True)
    asset, descriptor = (args.stage / file for file in ("site.glb", "site.json"))
    faces = site.export(
        asset,
        (ASSET_ID, [preview], "building"),
        (GROUND, ground, "landscape-surface"),
        (FURNITURE, detail, "landscape-vegetation"),
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
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(asset),
            "buildings": [
                {
                    "id": ASSET_ID,
                    "name": spec["name"],
                    "street_address": spec["street_address"],
                    "footprint_enu_m": list(shell.exterior.coords)[:-1],
                    "base_z_m": spec["foundation_z_m"],
                    "roof_z_m": spec["ridge_z_m"],
                    "support_collision_enu_m": [
                        list(item.exterior.coords)[:-1] for item in posts
                    ],
                    "entrances": [
                        {
                            "gate": "education-annex-west",
                            "position_enu_m": door,
                            "outward_degrees": 270,
                            "approach_distance_m": 2,
                            "threshold_z_m": spec["porch_z_m"],
                            "estimated": True,
                        }
                    ],
                }
            ],
            "new_building_ids": [ASSET_ID],
            "closed_site_boxes_enu_m": [b.bounds for b in [*rails, sign]],
            "walkable_ground": {"bounds_enu_m": [spec["extent"]], "paths": paths},
        },
        compact=True,
    )
    audit = {
        "faces": faces,
        "ordinary_stair_treads": spec["stair_treads"],
        "shrubs": shrubs,
        "route_edges": edges,
        "route_length_m": lengths[0],
        "route_obstacle_clearance_m": round(route_line.distance(obstacles), 3),
        "ramp_rail_trunk_clearance_m": round(unary_union(rails).distance(trunks), 3),
        "ramp_run_m": round(spec["ramp_enu_m"][3] - spec["ramp_enu_m"][1], 2),
        "ramp_elevation_change_m": round(spec["porch_z_m"] - spec["ramp_base_z_m"], 3),
        "asset_sha256": site.pin(asset),
        "descriptor_sha256": site.pin(descriptor),
    }
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
