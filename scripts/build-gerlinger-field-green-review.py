# SPDX-License-Identifier: Apache-2.0
"""Rebuild the Gerlinger Field Green paths, planting and University Street edge."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

site = import_module("build-pioneer-cemetery-landscape-review")
PACKAGE = "gerlinger-field-green-review"
GROUND = "gerlinger-field-green-surface"
LAWN = (112, 134, 87)
PAVING = {"concrete": (158, 153, 135), "asphalt": (105, 108, 96)}
IRON = (68, 72, 63)
# The earlier landscape-lawn occupies the same terrain at +0.07 m.
WALK_OFFSET = 0.147
PLANTED_OFFSET = 0.157


def paving(parts, field, spec, building_envelopes):
    footprint = unary_union(building_envelopes)
    paved = {}
    for row in spec["walks"]:
        shape = LineString(row["centerline_enu_m"]).buffer(
            row["width_m"] / 2, cap_style="flat", join_style="round"
        )
        paved.setdefault(row["material"], []).append(shape)
    apron = Polygon(spec["annex_apron_enu_m"])
    paved["asphalt"].append(apron)
    concrete = unary_union(paved["concrete"]).difference(footprint)
    asphalt = unary_union(paved["asphalt"]).difference(footprint.union(concrete))
    site.drape(parts, field, concrete, PAVING["concrete"], WALK_OFFSET, 1.3)
    site.drape(parts, field, asphalt, PAVING["asphalt"], WALK_OFFSET, 1.3)
    for row in spec["annex_parking_markings_enu_m"]:
        line = LineString(row).buffer(0.042, cap_style="flat")
        site.drape(
            parts,
            field,
            line.intersection(asphalt),
            (157, 133, 70),
            WALK_OFFSET + 0.006,
            1.4,
        )
    for span in spec["walks"]:
        if span["name"] != "Hall south walk":
            continue
        line = LineString(span["centerline_enu_m"])
        for s in np.arange(2.4, line.length, 2.45):
            x, y = line.interpolate(s).coords[0]
            seam = box(x - 0.024, y - 1.35, x + 0.024, y + 1.35)
            site.drape(
                parts,
                field,
                seam.intersection(concrete),
                (121, 120, 108),
                WALK_OFFSET + 0.006,
                1.3,
            )
    return concrete.union(asphalt)


def planting(ground, plants, field, spec, paved):
    lawn = Polygon(spec["lawn_enu_m"]).difference(paved.buffer(0.024))
    edge_trees = [Point(row["position_enu_m"]) for row in spec["registered_edge_trees"]]
    assert all(
        root.distance(paved) > 0.16
        and (not lawn.contains(root) or lawn.boundary.distance(root) < 4.2)
        for root in edge_trees
    )
    lawn = lawn.difference(unary_union([point.buffer(0.36) for point in edge_trees]))
    site.drape(ground, field, lawn, LAWN, PLANTED_OFFSET, 1.85)
    cultivar = {"ivy": (83, 106, 64), "mulch": (113, 98, 76)}
    bed_area = 0
    for i, row in enumerate(spec["planting_areas"]):
        bed = Polygon(row["outline_enu_m"]).difference(paved.union(lawn).buffer(0.05))
        ground_tone = cultivar[row["cover"]]
        site.drape(ground, field, bed, ground_tone, PLANTED_OFFSET, 1.6)
        bed_area += bed.area
        rng = np.random.default_rng(400 + i)
        if row["cover"] == "ivy":
            w, s, e, n = bed.bounds
            patches = rng.uniform([w, s], [e, n], size=(int(bed.area * 1.28), 2))
            covers = bed.buffer(-0.25)
            for x, y in patches:
                if covers.contains(Point(x, y)):
                    z = site.ground_height(field, x, y)
                    leaf = rng.uniform(0.13, 0.33)
                    tone = int(rng.integers(-8, 15))
                    site.orb(
                        plants,
                        (x, y, z + PLANTED_OFFSET + 0.05),
                        (leaf, leaf * 0.72, 0.083),
                        (83 + tone, 108 + tone, 68 + tone),
                        subdivisions=0,
                    )
    for i, row in enumerate(spec["registered_edge_trees"]):
        site.canopy(plants, field, row, i)
    return lawn.area, bed_area


def parking_sign(parts, field, point):
    e, n = point
    z = site.ground_height(field, e, n)
    site.flat_box(parts, e, n, 0.047, 0.053, z - 0.14, z + 1.79, (130, 138, 134))
    site.flat_box(parts, e + 0.021, n, 0.023, 0.285, z + 1.44, z + 1.84, (48, 82, 140))
    white = (216, 223, 209)
    x = e + 0.041
    wheel = [
        (x, n + 0.062 * np.cos(i), z + 1.56 + 0.062 * np.sin(i))
        for i in np.linspace(0, 2 * np.pi, 12)
    ]
    for a, b in zip(wheel, wheel[1:]):
        site.cylinder_between(parts, a, b, 0.008, white, sides=5)
    site.orb(
        parts, (x, n + 0.025, z + 1.737), (0.009, 0.020, 0.020), white, subdivisions=1
    )
    for a, b in (
        ((x, n + 0.023, z + 1.707), (x, n + 0.016, z + 1.621)),
        ((x, n + 0.016, z + 1.621), (x, n - 0.060, z + 1.621)),
        ((x, n - 0.060, z + 1.621), (x, n - 0.091, z + 1.567)),
    ):
        site.cylinder_between(parts, a, b, 0.008, white, sides=5)


def annex_stair(paving_parts, details, field, info):
    west, east = info["east_bounds_enu_m"]
    south, north = info["north_bounds_enu_m"]
    low = site.ground_height(field, east, (south + north) / 2) + WALK_OFFSET
    rise = info["top_height_above_grade_m"]
    steps = info["treads"]
    run = east - west
    top_landing = 1.7
    lower_landing = 1.25
    tread_run = (run - top_landing - lower_landing) / steps
    site.solid(
        paving_parts,
        box(east - lower_landing, south, east, north),
        low - 0.19,
        low,
        (155, 152, 136),
    )
    for i in range(steps):
        edge = east - lower_landing - i * tread_run
        height = low + rise * (i + 1) / steps
        site.solid(
            paving_parts,
            box(edge - tread_run, south, edge, north),
            height - 0.38,
            height,
            (153, 154, 143),
        )
    site.solid(
        paving_parts,
        box(west, south, west + top_landing, north),
        low + rise - 0.28,
        low + rise,
        (154, 153, 140),
    )
    near = east - lower_landing
    far = west + top_landing
    fascia = site.landscape.cap(
        box(far, south - 0.045, near, south + 0.105),
        low - 0.42,
        low + 0.56,
        (124, 128, 119),
    )
    fascia.vertices[:, 1] += rise * (near - fascia.vertices[:, 0]) / (near - far)
    details.append(fascia)
    posts = []
    for x in (west + 0.40, west + 2.15):
        for y in (south + 0.08, north - 0.08):
            base = site.ground_height(field, x, y)
            leg = box(x - 0.063, y - 0.061, x + 0.063, y + 0.061)
            site.solid(details, leg, base - 0.08, low + rise - 0.21, IRON)
            posts.append(list(leg.bounds))
    for y in (south + 0.047, north - 0.047):
        rail = [
            (east, y, low + 0.97),
            (east - lower_landing, y, low + 0.97),
            (west + top_landing, y, low + rise + 0.97),
            (west, y, low + rise + 0.97),
        ]
        for a, b in zip(rail, rail[1:]):
            site.cylinder_between(details, a, b, 0.027, IRON, sides=7)
        for i, x in enumerate(
            np.linspace(east - lower_landing - 0.13, west + top_landing, 6)
        ):
            z = low + rise * min(1, 0.041 + i / 5)
            site.cylinder_between(
                details, (x, y, z), (x, y, z + 0.97), 0.024, IRON, sides=7
            )
    for height in (0.48, 0.97):
        z = low + rise + height
        site.cylinder_between(
            details,
            (west, south + 0.047, z),
            (west, north - 0.047, z),
            0.026,
            IRON,
            sides=7,
        )
    for y in (south + 0.047, north - 0.047):
        site.cylinder_between(
            details,
            (west, y, low + rise),
            (west, y, low + rise + 0.97),
            0.026,
            IRON,
            sides=7,
        )
    return posts


def main():
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("--stage", required=True, type=Path)
    arguments.add_argument("--audit", required=True, type=Path)
    args = arguments.parse_args()
    spec = site.read(site.root / f"data/metadata/{PACKAGE}.json")
    scene = site.scene
    manifest = site.read(scene / "manifest.json")
    config = site.read(scene / "presentation.json")
    heights = scene / manifest["heightfield_url"]
    neighbor = scene / "gerlinger-site-review/site.json"
    pins = spec["pinned_sources"]
    assert pins == {
        "campus": manifest["model"]["sha256"],
        "presentation": config["asset_sha256"],
        "heightfield": site.pin(heights),
        "navigation": site.pin(scene / "navigation.json"),
        "gerlinger_site": site.pin(neighbor),
    }
    assert spec["pilot_tree_clip"]["source_refined_sha256"] == site.pin(
        scene / "pilot-trees-l2/trees.glb"
    )
    assert spec["pilot_tree_clip"]["source_legacy_sha256"] == pins["presentation"]
    field = site.read(heights)
    outlines = [
        Polygon(ring).buffer(0.055)
        for b in site.read(neighbor)["buildings"]
        for ring in [b["footprint_enu_m"], *b["support_collision_enu_m"]]
    ]
    ground, detail, plants = [], [], []
    paths = paving(ground, field, spec, outlines)
    lawn, planting_area = planting(ground, plants, field, spec, paths)
    wall_spans = [*spec["east_wall_enu_m"], *spec["south_east_wall_enu_m"]]
    site.walls(detail, field, wall_spans)
    boxes = [
        list(LineString(span).buffer(0.13, cap_style="flat").bounds)
        for span in wall_spans
    ]
    assert all(paths.intersection(box(*rect)).area < 0.072 for rect in boxes)
    boxes.extend(annex_stair(ground, detail, field, spec["annex_stair"]))
    parking_sign(detail, field, spec["parking_sign_enu_m"])
    walkable = spec["walkable_ground"]
    nav = site.read(scene / "navigation.json")
    assert walkable["anchor_enu_m"] in nav["nodes_enu_m"]
    route = LineString([walkable["anchor_enu_m"], *walkable["points_enu_m"]])
    assert route.distance(unary_union(outlines)) > 0.55
    assert all(
        paths.buffer(0.14).covers(Point(x, y)) for x, y in walkable["points_enu_m"]
    )
    args.stage.mkdir(exist_ok=True, parents=True)
    asset = args.stage / "site.glb"
    faces = site.export(
        asset,
        (GROUND, ground, "landscape-surface"),
        ("gerlinger-field-green-planting", plants, "landscape-vegetation"),
        ("gerlinger-field-green-detail", detail, "landscape-detail"),
        surface_layer=GROUND,
    )
    descriptor = args.stage / "site.json"
    payload = {
        "source_presentation_sha256": pins["presentation"],
        "source_base_model_sha256": pins["campus"],
        "source_heightfield_sha256": pins["heightfield"],
        "source_navigation_sha256": pins["navigation"],
        "url": f"{PACKAGE}/site.glb",
        "sha256": site.pin(asset),
        "ground_node": GROUND,
        "buildings": [],
        "closed_site_boxes_enu_m": boxes,
        "walkable_ground": walkable,
        "pilot_tree_clip": spec["pilot_tree_clip"],
        "pilot_understory_clip": spec["pilot_understory_clip"],
    }
    site.fairmount.write_json(descriptor, payload, compact=True)
    audit = {
        "paths": len(spec["walks"]),
        "path_area_m2": round(paths.area, 2),
        "annex_apron_area_m2": round(Polygon(spec["annex_apron_enu_m"]).area, 2),
        "lawn_area_m2": round(lawn, 2),
        "planting_area_m2": round(planting_area, 2),
        "walls_m": round(sum(LineString(span).length for span in wall_spans), 2),
        "stair_treads": spec["annex_stair"]["treads"],
        "registered_edge_trees": len(spec["registered_edge_trees"]),
        "removed_procedural_pilot_trees": len(spec["pilot_tree_clip"]["tree_indices"]),
        "removed_procedural_shrubs": len(
            spec["pilot_understory_clip"]["understory_1"]["ranges"]
        ),
        "route_m": round(route.length, 2),
        "faces": faces,
        "asset_sha256": site.pin(asset),
        "descriptor_sha256": site.pin(descriptor),
    }
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
