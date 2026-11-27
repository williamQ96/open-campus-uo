# SPDX-License-Identifier: Apache-2.0
"""Build the surveyed Kincaid Green paths and the Lokey Education courtyard."""

import argparse
from importlib import import_module
from pathlib import Path

from shapely.affinity import rotate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

green = import_module("build-southwest-campus-green")
site = green.site
PACKAGE = "kincaid-education-landscape-review"
GROUND = "kincaid-education-paving"
DETAIL = "kincaid-education-furnishings"
PLANTING = "kincaid-education-planting"
BRICK = (153, 104, 84)
CONCRETE = (175, 170, 156)


def surfaces(spec, buildings):
    walks = {
        kind: unary_union(
            [
                LineString(row["line"]).buffer(row["width"] / 2, cap_style="flat")
                for row in spec["walks"]
                if row["kind"] == kind
            ]
        ).difference(buildings)
        for kind in ("brick", "concrete")
    }
    brick = walks["brick"].union(Polygon(spec["brick_plaza"])).difference(buildings)
    concrete = walks["concrete"].difference(brick)
    paved = brick.union(concrete)
    beds = [
        Polygon(outline).difference(paved.union(buildings)) for outline in spec["beds"]
    ]
    lawn = unary_union([Polygon(outline) for outline in spec["lawns"]]).difference(
        unary_union([paved, buildings, *beds])
    )
    return brick, concrete, lawn, beds


def furnishings(parts, field, spec):
    obstacles = []
    for row in spec["benches"]:
        center = Point(row["center"])
        length = row["length"]
        base = row.get(
            "surface_z_m", site.ground_height(field, *center.coords[0]) + 0.105
        )
        line = site.landscape.rect_on(
            (center.x - length / 2, center.y), (center.x + length / 2, center.y), 0.43
        )
        seat = rotate(line, row["bearing"] - 90, origin=center)
        brick = row["form"] == "brick"
        if brick:
            site.solid(
                parts,
                seat.buffer(-0.048, join_style="mitre"),
                base - 0.12,
                base + 0.38,
                BRICK,
            )
        else:
            for x in (center.x - length * 0.34, center.x + length * 0.34):
                foot = rotate(
                    box(x - 0.06, center.y - 0.16, x + 0.06, center.y + 0.16),
                    row["bearing"] - 90,
                    origin=center,
                )
                site.solid(parts, foot, base - 0.09, base + 0.40, green.METAL)
        site.solid(parts, seat, base + 0.38, base + 0.455, (146, 112, 81))
        obstacles.append(box(*seat.bounds))
    for x, n in spec["lamps"]:
        height = site.ground_height(field, x, n)
        site.cylinder_between(
            parts,
            (x, n, height - 0.10),
            (x, n, height + 3.24),
            0.063,
            green.METAL,
            sides=10,
        )
        site.orb(parts, (x, n, height + 3.37), (0.17, 0.17, 0.197), (221, 215, 189))
        obstacles.append(box(x - 0.09, n - 0.09, x + 0.09, n + 0.09))
    return obstacles


def scholar_walk(parts, field, spec):
    x, south, north, width = spec["scholar_walk"]
    posts = []
    trim = (194, 190, 171)
    for east in (x - 1.34, x + 1.34):
        for n in (-358.0, -353.3, -346.8, -339.5, -333.0):
            z = site.ground_height(field, east, n)
            post = box(east - 0.085, n - 0.085, east + 0.085, n + 0.085)
            site.solid(parts, post, z - 0.18, z + 2.74, trim)
            posts.append(post)
    for east in (x - width / 2, x + width / 2):
        fascia = box(east - 0.035, south, east + 0.035, north)
        site.landscape.top_surface(
            parts,
            fascia,
            lambda e, n: site.ground_height(field, x, n) + 2.77,
            trim,
            cell=1.15,
        )

    def roof(e, n):
        ridge = 1 - abs(e - x) / (width / 2)
        return site.ground_height(field, x, n) + 2.72 + 0.42 * ridge

    for west, east in ((x - width / 2, x), (x, x + width / 2)):
        site.landscape.top_surface(
            parts, box(west, south, east, north), roof, (117, 110, 98), cell=1.1
        )
    return posts


def south_pavilion(ground, detail, field, spec):
    info = spec["south_pavilion"]
    center = Point(info["center"])
    half = info["roof_width_m"] / 2
    roof = rotate(
        box(center.x - half, center.y - half, center.x + half, center.y + half),
        info["bearing_degrees"],
        origin=center,
    )
    deck = roof.buffer(-0.32, join_style="mitre")
    deck_z, eave, peak = info["elevations_m"]
    site.solid(ground, deck, deck_z - 0.17, deck_z, (163, 146, 125))
    rim = list(roof.exterior.coords)
    trim = (201, 194, 177)
    posts = []
    for corner in list(deck.buffer(-0.11, join_style="mitre").exterior.coords)[:-1]:
        x, n = corner
        support = box(x - 0.08, n - 0.08, x + 0.08, n + 0.08)
        site.solid(detail, support, site.ground_height(field, x, n) - 0.18, eave, trim)
        posts.append(support)
    for a, b in zip(rim, rim[1:]):
        edge = LineString([a, b])
        face = Polygon([a, b, center.coords[0]])
        run = edge.distance(center)
        site.landscape.top_surface(
            detail,
            face,
            lambda x, y: eave + (peak - eave) * edge.distance(Point(x, y)) / run,
            (123, 115, 102),
            cell=0.55,
        )
    occupied = [deck]
    for leg in info["flights"]:
        a, b = leg["line"]
        axis = LineString([a, b])
        start, finish = leg["elevations_m"]
        count = leg["treads"]
        width = leg["width_m"]
        occupied.append(axis.buffer(width / 2, cap_style="flat"))
        for i in range(count):
            left = axis.interpolate(i / count, normalized=True).coords[0]
            right = axis.interpolate((i + 1) / count, normalized=True).coords[0]
            height = start + (finish - start) * (i + 1) / count
            span = site.landscape.rect_on(left, right, width)
            site.solid(ground, span, height - 0.24, height, (178, 168, 151))
        de, dn = (b[0] - a[0]) / axis.length, (b[1] - a[1]) / axis.length
        for side in (-1, 1):
            offset = side * (width / 2 - 0.055)
            low = (a[0] - dn * offset, a[1] + de * offset, start)
            high = (b[0] - dn * offset, b[1] + de * offset, finish)
            for x, y, z in (low, high):
                site.cylinder_between(
                    detail, (x, y, z), (x, y, z + 0.92), 0.033, trim, sides=8
                )
            site.cylinder_between(
                detail,
                (low[0], low[1], low[2] + 0.92),
                (high[0], high[1], high[2] + 0.92),
                0.042,
                trim,
                sides=8,
            )
    return unary_union(occupied), posts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    spec = site.read(metadata / "kincaid-education-landscape.json")
    manifest, field, graph = green.east.pinned_site(site.scene, spec)
    buildings, old_boxes = green.east.build_blockers(
        site.scene, spec, manifest, box(*spec["extent"])
    )
    older = site.read(metadata / "southwest-campus-green.json")
    _, shared_paving, _, _ = green.surface_footprints(older, buildings)
    brick, concrete, lawn, beds = surfaces(spec, buildings)
    ground, detail, plants = [], [], []
    pavilion, pavilion_posts = south_pavilion(ground, detail, field, spec)
    assert pavilion.intersection(buildings).area < 0.02
    beds = [bed.difference(pavilion.buffer(0.13)) for bed in beds]
    for shape, color, lift, step in (
        (brick, BRICK, 0.143, 0.77),
        (concrete.difference(shared_paving), CONCRETE, 0.143, 0.91),
        (lawn.difference(shared_paving.union(pavilion)), (143, 159, 102), 0.064, 1.75),
        (unary_union(beds), green.SOIL, 0.107, 0.86),
    ):
        site.drape(ground, field, shape, color, lift, step)
    fixtures = furnishings(detail, field, spec)
    posts = scholar_walk(detail, field, spec)
    # Posts adjoining the crossing are included in the geometry screen.
    # Use the descriptor limit for the ten posts and four benches.
    solid_boxes = fixtures[: len(spec["benches"])] + posts + pavilion_posts[:2]
    shrubs = green.plantings(plants, field, spec["trees"], beds)
    donor = site.read(site.scene / f"{green.PACKAGE}/site.json")
    anchors = [
        point
        for route in donor["walkable_ground"]["paths"]
        for point in route["points_enu_m"]
    ]
    trees = unary_union(
        [Point(row["position_enu_m"]).buffer(0.22) for row in spec["trees"]]
    )
    obstacles = unary_union([buildings, old_boxes, trees, pavilion, *fixtures, *posts])
    edges, lengths = green.west.check_routes(
        {"nodes_enu_m": [*graph["nodes_enu_m"], *anchors]},
        spec["routes"],
        brick.union(concrete).union(shared_paving),
        obstacles,
    )
    assert len(solid_boxes) <= 16
    args.stage.mkdir(parents=True, exist_ok=True)
    asset = args.stage / "site.glb"
    descriptor = args.stage / "site.json"
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
            "closed_site_boxes_enu_m": [b.bounds for b in solid_boxes],
            "context_trees": spec["clear_context_trees"],
            "pilot_tree_clip": spec["pilot_tree_clip"],
        },
        compact=True,
    )
    audit = {
        "brick_m2": round(brick.area, 2),
        "concrete_m2": round(concrete.difference(shared_paving).area, 2),
        "lawn_m2": round(lawn.area, 2),
        "planting_beds": len(beds),
        "trees": len(spec["trees"]),
        "bench_count": len(spec["benches"]),
        "lamp_count": len(spec["lamps"]),
        "scholar_walk_m": round(spec["scholar_walk"][2] - spec["scholar_walk"][1], 2),
        "south_pavilion_plan_m2": round(pavilion.area, 2),
        "south_pavilion_stair_treads": sum(
            row["treads"] for row in spec["south_pavilion"]["flights"]
        ),
        "shrubs": shrubs,
        "route_edges": edges,
        "route_lengths_m": lengths,
        "faces": face_counts,
        "asset_sha256": site.pin(asset),
        "descriptor_sha256": site.pin(descriptor),
    }
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
