# SPDX-License-Identifier: Apache-2.0
"""Build Kendall Plaza, the east terrace and the south lawn approaches."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

education = import_module("build-kincaid-education-landscape")
green, site = education.green, education.site
PACKAGE = "kendall-plaza-landscape-review"
GROUND = "kendall-plaza-paving"
DETAIL = "kendall-plaza-furnishings"
PLANTING = "kendall-plaza-planting"


def blockers(spec, manifest):
    # The HEDCO descriptor predates multi-building packs and has a singular record.
    hedco = site.read(site.scene / "hedco-exterior-review/site.json")["building"]
    manifest = {
        **manifest,
        "buildings": [
            hedco if row["id"] == hedco["id"] else row for row in manifest["buildings"]
        ],
    }
    return green.east.build_blockers(site.scene, spec, manifest, box(*spec["extent"]))


def footprints(spec, buildings):
    occupied = buildings.union(box(*spec["annex_clearance_enu_m"]))
    brick, concrete, lawn, beds = education.surfaces(spec, occupied)
    south, north = spec["terrace"]["south_north"]
    tiers = [
        box(west, south, east, north) for west, east, _ in spec["terrace"]["tiers"]
    ]
    reserved = unary_union([*tiers, box(*spec["terrace"]["planter_bounds"])])
    return (
        brick.difference(reserved),
        concrete.difference(reserved),
        lawn.difference(reserved),
        beds,
    )


def south_lawn_footprints(spec, buildings):
    lawn = spec["south_lawn"]
    west = lawn["walks"][0]
    seam = Point(west["line"][0]).buffer(west["width_m"] / 2)
    walks = unary_union(
        [
            seam,
            *(
                LineString(row["line"]).buffer(row["width_m"] / 2, cap_style="flat")
                for row in lawn["walks"]
            ),
        ]
    ).difference(buildings)
    access = (
        LineString(lawn["gravel_access_centerline_enu_m"])
        .buffer(lawn["gravel_access_width_m"] / 2, cap_style="square")
        .difference(buildings)
    )
    gravel = (
        Polygon(lawn["gravel_outline_enu_m"])
        .union(access)
        .difference(walks.union(buildings))
    )
    occupied = walks.union(gravel).union(buildings)
    beds = []
    for outline in lawn["beds"]:
        bed = Polygon(outline).difference(occupied)
        assert bed.is_valid and bed.area > 1
        beds.append(bed)
        occupied = occupied.union(bed)
    grass = unary_union([Polygon(ring) for ring in lawn["lawns"]]).difference(occupied)
    return walks, access, gravel, beds, grass


def south_gravel(parts, field, gravel, walks, access):
    site.drape(parts, field, gravel, (127, 125, 115), 0.151, 0.28)
    mesh = parts[-1]
    x, _, z = mesh.vertices.T
    # Small changes in the original vertex colors break up the dry gravel.
    noise = np.sin(x * 16.3 + z * 13.7) * 43758.5453
    variation = 13 * (noise - np.floor(noise) - 0.5)
    colors = np.array([127, 125, 115]) + variation[:, None]
    mesh.visual.vertex_colors[:, :3] = np.rint(colors).astype(np.uint8)
    lip = gravel.boundary.buffer(0.055).intersection(gravel)
    lip = lip.difference(walks.union(access).buffer(0.10))
    site.drape(parts, field, lip, (153, 148, 135), 0.165, 0.37)


def terrace(ground, detail, plants, field, spec):
    info = spec["terrace"]
    south, north = info["south_north"]
    levels = info["tiers"]
    base = levels[-1][2]
    planter = box(*info["planter_bounds"])
    for west, east, z in levels:
        slab = box(west, south, east, north).difference(planter)
        site.solid(ground, slab, z - 0.55, z, education.CONCRETE)
    inner = planter.buffer(-0.16, join_style="mitre")
    site.solid(
        detail, planter.difference(inner), base - 0.10, base + 0.44, (161, 151, 135)
    )
    site.solid(ground, inner, base - 0.14, base + 0.27, green.SOIL)
    east = inner.centroid.x
    for n in (-416.7, -414.3, -413.3, -409.3, -408.5, -405.8):
        site.orb(plants, (east, n, base + 0.52), (0.66, 0.53, 0.36), (116, 131, 82))

    for n in info["rail_northings"]:
        rail = []
        for west, _, z in levels:
            top = (west + 0.09, n, z + 0.88)
            site.cylinder_between(
                detail, (top[0], n, z), top, 0.04, green.METAL, sides=8
            )
            rail.append(top)
        for a, b in zip(rail, rail[1:]):
            site.cylinder_between(detail, a, b, 0.041, green.METAL, sides=8)
    return planter


def plaza_height(field, e, n):
    # LiDAR samples form a mild rise toward the three seating tiers.
    # Leave clearance above the 0.126 m Southwest Green paving at the seam.
    natural = site.ground_height(field, e, n) + 0.180
    grade = 7.77 + 0.028 * (e + 636)
    entrance_blend = max(0, min(1, (e + 645) / 7, (n + 424) / 4, (-397 - n) / 4))
    return natural + max(0, grade - natural) * entrance_blend


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    spec = site.read(metadata / "kendall-plaza-landscape.json")
    manifest, field, graph = green.east.pinned_site(site.scene, spec)
    buildings, old_boxes = blockers(spec, manifest)
    brick, concrete, lawn, beds = footprints(spec, buildings)
    shared_spec = site.read(metadata / "southwest-campus-green.json")
    _, shared_green, _, _ = green.surface_footprints(shared_spec, buildings)
    shared_spec = site.read(metadata / "kincaid-education-landscape.json")
    shared_brick, shared_walk, _, _ = education.surfaces(shared_spec, buildings)
    shared = shared_green.union(shared_brick).union(shared_walk)

    ground, detail, plants = [], [], []
    site.landscape.top_surface(
        ground,
        brick,
        lambda x, y: plaza_height(field, x, y),
        education.BRICK,
        cell=0.74,
    )
    site.drape(
        ground, field, concrete.difference(shared), education.CONCRETE, 0.151, 0.91
    )
    site.drape(ground, field, lawn.difference(shared), (149, 160, 106), 0.068, 1.74)
    site.drape(
        ground, field, unary_union(beds).difference(shared), green.SOIL, 0.112, 1.0
    )
    planter = terrace(ground, detail, plants, field, spec)
    furniture = education.furnishings(detail, field, spec)
    shrubs = green.plantings(plants, field, spec["trees"], beds)

    south = spec["south_lawn"]
    south_paths, access, gravel, south_beds, south_grass = south_lawn_footprints(
        spec, buildings
    )
    previous_beds = unary_union(beds)
    south_beds = [bed.difference(previous_beds) for bed in south_beds]
    new_paving = south_paths.difference(brick.union(concrete).union(shared))
    site.drape(ground, field, new_paving, education.CONCRETE, 0.151, 0.80)
    south_gravel(ground, field, gravel, south_paths, access)
    site.drape(
        ground, field, south_grass.difference(lawn), (149, 160, 106), 0.068, 1.46
    )
    site.drape(ground, field, unary_union(south_beds), green.SOIL, 0.112, 0.94)
    furniture.extend(
        education.furnishings(detail, field, {"lamps": south["lamps"], "benches": []})
    )
    shrubs += green.plantings(
        plants, field, south["trees"], south_beds, spacing=(1.10, 0.94)
    )

    anchors = []
    for pack in (green.PACKAGE, education.PACKAGE):
        donor = site.read(site.scene / pack / "site.json")
        anchors.extend(
            point
            for path in donor["walkable_ground"]["paths"]
            for point in path["points_enu_m"]
        )
    trunks = [
        Point(row["position_enu_m"]).buffer(max(0.22, row["crown_radius_m"] * 0.071))
        for row in [*spec["trees"], *south["trees"]]
    ]
    obstacles = unary_union(
        [
            buildings,
            old_boxes,
            box(*spec["annex_clearance_enu_m"]),
            planter,
            *furniture,
            *trunks,
        ]
    )
    covered = unary_union([brick, concrete, shared, south_paths, access])
    edges, lengths = green.west.check_routes(
        {"nodes_enu_m": [*graph["nodes_enu_m"], *anchors]},
        spec["routes"],
        covered,
        obstacles,
    )
    south_walk_routes = [
        LineString(south["walks"][0]["line"]),
        LineString(south["gravel_access_centerline_enu_m"]),
        LineString(south["walks"][1]["line"]),
    ]
    for line in south_walk_routes:
        assert line.difference(covered.buffer(0.13)).length < 0.001, line.wkt
    stair_area = unary_union(
        [
            box(
                a,
                spec["terrace"]["south_north"][0],
                b,
                spec["terrace"]["south_north"][1],
            )
            for a, b, _ in spec["terrace"]["tiers"]
        ]
    )
    assert shared_green.intersection(stair_area).area < 0.02
    args.stage.mkdir(parents=True, exist_ok=True)
    asset, descriptor = (args.stage / name for name in ("site.glb", "site.json"))
    face_counts = site.export(
        asset,
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
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(asset),
            "buildings": [],
            "walkable_ground": {
                "bounds_enu_m": spec["surface_bounds"],
                "paths": spec["routes"],
            },
            "closed_site_boxes_enu_m": [b.bounds for b in [planter, *furniture]],
            "context_trees": spec["clear_context_trees"],
        },
        compact=True,
    )
    audit = {
        "brick_m2": round(brick.area, 2),
        "concrete_m2": round(concrete.difference(shared).area, 2),
        "lawn_m2": round(lawn.area, 2),
        "planting_beds": len(beds) + len(south_beds) + 1,
        "trees": len(spec["trees"]) + len(south["trees"]),
        "terrace_levels_m": [row[2] for row in spec["terrace"]["tiers"]],
        "bench_count": len(spec["benches"]),
        "lamp_count": len(spec["lamps"]) + len(south["lamps"]),
        "low_plants": shrubs + 6,
        "route_edges": edges,
        "route_lengths_m": lengths,
        "faces": face_counts,
        "south_lawn": {
            "paving_m2": round(new_paving.area, 2),
            "gravel_m2": round(gravel.area, 2),
            "grass_m2": round(south_grass.difference(lawn).area, 2),
            "beds_m2": round(sum(bed.area for bed in south_beds), 2),
            "route_edges": sum(len(line.coords) - 1 for line in south_walk_routes),
            "route_lengths_m": [round(line.length, 2) for line in south_walk_routes],
        },
        "asset_sha256": site.pin(asset),
        "descriptor_sha256": site.pin(descriptor),
    }
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
