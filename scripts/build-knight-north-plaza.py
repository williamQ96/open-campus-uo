# SPDX-License-Identifier: Apache-2.0
"""Build Knight Library's north forecourt and the Bailey fountain."""

import argparse
from importlib import import_module
from pathlib import Path

from shapely.geometry import LineString, box
from shapely.ops import unary_union

green = import_module("build-southwest-campus-green")
site = green.site
PACKAGE = "knight-north-plaza-review"
GROUND = "knight-north-plaza-paving"
DETAIL = "knight-bailey-fountain"
PLANTING = "knight-north-plaza-planting"
CONCRETE = (174, 169, 155)
CAST_STONE = (166, 144, 120)
BRICK = (117, 77, 57)
BRONZE = (69, 102, 88)


def solid_footprints(spec):
    return [
        box(*bounds)
        for bounds in [spec["fountain"]["basin"], *spec["planters"], *spec["seats"]]
    ]


def paving_footprint(spec):
    return unary_union([box(*bounds) for bounds in spec["paving_bounds"]]).difference(
        unary_union(solid_footprints(spec))
    )


def control_joints(ground, field, paving):
    west, south, east, north = paving.bounds
    horizontal = [box(west, n - 0.012, east, n + 0.012) for n in range(-191, -174, 3)]
    vertical = [box(x - 0.012, south, x + 0.012, north) for x in range(-577, -513, 3)]
    joints = unary_union(horizontal + vertical).intersection(paving.buffer(-0.045))
    site.drape(ground, field, joints, (158, 151, 136), 0.154, 0.75)


def ground_relative(parts, field, shape, bottom, top, color):
    mesh = site.landscape.cap(shape, bottom, top, color)
    mesh.vertices[:, 1] += [
        site.ground_height(field, east, -south) for east, _, south in mesh.vertices
    ]
    parts.append(mesh)


def planters(ground, details, plants, field, spec):
    for index, bounds in enumerate(spec["planters"]):
        bed = box(*bounds)
        inner = bed.buffer(-0.24, join_style="mitre")
        wall = bed.difference(inner)
        ground_relative(details, field, wall, -0.12, 0.37, BRICK)
        ground_relative(details, field, wall, 0.37, 0.48, CAST_STONE)
        soil = green.SOIL if index < 2 else (146, 154, 108)
        site.drape(ground, field, inner, soil, 0.36, 0.85)
        west, south, east, north = inner.bounds
        hedge = box(west + 0.14, north - 0.76, east - 0.14, north - 0.09)
        ground_relative(plants, field, hedge, 0.34, 0.79, (91, 112, 58))
        for x in range(int(west + 1), int(east), 2):
            n = south + 0.52
            z = site.ground_height(field, x, n)
            site.orb(plants, (x, n, z + 0.47), (0.47, 0.36, 0.26), (106, 126, 66))


def seating(parts, field, spec):
    for west, south, east, north in spec["seats"]:
        for x in (west + 0.23, east - 0.23):
            foot = box(x - 0.1, south + 0.06, x + 0.1, north - 0.06)
            ground_relative(parts, field, foot, 0.10, 0.50, CAST_STONE)
        seat = box(west, south, east, north)
        ground_relative(parts, field, seat, 0.50, 0.63, (185, 165, 142))


def fountain(parts, field, spec):
    info = spec["fountain"]
    west, south, east, north = info["basin"]
    wall_north = info["back_wall_north_m"]
    center = (west + east) / 2
    base = site.ground_height(field, center, north) + 0.151
    basin = box(west, south, east, north)
    inside = box(west + 0.18, south + 0.18, east - 0.18, north - 0.18)
    rim = basin.difference(inside)
    site.solid(parts, inside, base - 0.04, base + 0.04, (106, 109, 101))
    site.solid(parts, rim, base - 0.10, base + 0.13, (152, 137, 119))
    site.solid(parts, rim, base + 0.13, base + 0.22, (182, 165, 141))
    back = box(west + 0.27, south + 0.12, east - 0.27, wall_north)
    site.solid(parts, back, base - 0.05, base + 0.72, CAST_STONE)
    site.solid(
        parts,
        back.buffer(0.035, join_style="mitre"),
        base + 0.72,
        base + 0.81,
        (181, 156, 134),
    )
    for x in (west + 0.32, east - 0.32):
        post = box(x - 0.23, south + 0.08, x + 0.23, wall_north + 0.12)
        site.solid(parts, post, base - 0.06, base + 0.73, CAST_STONE)
        site.solid(
            parts,
            post.buffer(0.04, join_style="mitre"),
            base + 0.73,
            base + 0.86,
            (186, 164, 141),
        )
    for x in info["relief_panel_centers_east_m"]:
        site.flat_box(
            parts, x, wall_north + 0.025, 0.53, 0.048, base + 0.42, base + 0.61, BRONZE
        )
        site.cylinder_between(
            parts,
            (x, wall_north + 0.05, base + 0.51),
            (x, wall_north + 0.22, base + 0.48),
            0.023,
            (88, 113, 90),
            sides=8,
        )
    for x in (west + 1.7, west + 3.0, east - 3.0, east - 1.7):
        site.flat_box(
            parts,
            x,
            wall_north + 0.005,
            0.015,
            0.013,
            base + 0.26,
            base + 0.72,
            (143, 123, 106),
        )
    plaque_east = info["plaque_center_east_m"]
    plaque = box(
        plaque_east - 0.28,
        wall_north - 0.29,
        plaque_east + 0.28,
        wall_north - 0.07,
    )
    site.solid(parts, plaque, base + 0.81, base + 0.823, (127, 106, 66))
    site.text_strokes(
        parts,
        "BAILEY",
        lambda e, n: (plaque_east + e, wall_north - 0.23 + n, base + 0.827),
        0.051,
        0.072,
        (185, 162, 99),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(site.root / "data/metadata/knight-north-plaza.json")
    _, field, graph = green.east.pinned_site(site.scene, spec)
    clip = spec["pilot_tree_clip"]
    assert clip["source_legacy_sha256"] == spec["pins"]["presentation"]
    assert clip["source_refined_sha256"] == site.pin(
        site.scene / "pilot-trees-l2/trees.glb"
    )
    library = site.read(site.scene / "knight-library-review/site.json")["building"]
    paving = paving_footprint(spec)
    obstacles = unary_union(solid_footprints(spec))
    routes = spec["routes"]
    edges, lengths = green.west.check_routes(graph, routes, paving, obstacles)
    for route in routes:
        tail = [route["end_enu_m"]] if "end_enu_m" in route else []
        line = LineString([route["anchor_enu_m"], *route["points_enu_m"], *tail])
        assert line.difference(paving.buffer(0.13)).length < 0.001, line.wkt
    for entrance, route in zip(library["entrances"], routes, strict=False):
        e, _ = entrance["position_enu_m"]
        assert abs(route["points_enu_m"][-1][0] - e) < 0.20

    ground, detail, plants = [], [], []
    site.drape(ground, field, paving, CONCRETE, 0.151, 0.75)
    control_joints(ground, field, paving)
    planters(ground, detail, plants, field, spec)
    seating(detail, field, spec)
    fountain(detail, field, spec)
    args.stage.mkdir(parents=True, exist_ok=True)
    glb, descriptor = (args.stage / name for name in ("site.glb", "site.json"))
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        (DETAIL, detail, "landscape-detail"),
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
            "prerequisite_site_sha256": pins["sites"]["knight-library-review"],
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(glb),
            "ground_node": GROUND,
            "walkable_ground": {"bounds_enu_m": [spec["extent"]], "paths": routes},
            "closed_site_boxes_enu_m": [
                shape.bounds for shape in solid_footprints(spec)
            ],
            "pilot_tree_clip": clip,
            "buildings": [],
        },
        compact=True,
    )
    audit = {
        "paving_m2": round(paving.area, 2),
        "planting_beds": len(spec["planters"]),
        "seats": len(spec["seats"]),
        "fountain_panels": len(spec["fountain"]["relief_panel_centers_east_m"]),
        "removed_inferred_trees": clip["tree_indices"],
        "route_edges": edges,
        "route_lengths_m": lengths,
        "faces": faces,
        "asset_sha256": site.pin(glb),
        "descriptor_sha256": site.pin(descriptor),
    }
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
