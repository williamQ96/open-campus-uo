# SPDX-License-Identifier: Apache-2.0
"""Reconstruct the East 15th campus promenade and Hayward's Powell Plaza."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
import trimesh
from shapely.affinity import rotate, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

midblock = import_module("build-hayward-midblock")
axis, site, west, east = midblock.axis, midblock.site, midblock.west, midblock.east
PACKAGE = "east-fifteenth-hayward-review"
GROUND = "east-fifteenth-hayward-paving"
DETAIL = "east-fifteenth-hayward-furnishings"
PLANT = "east-fifteenth-hayward-planting"
PAVERS = (150, 149, 140)
CONCRETE = (179, 174, 159)
ASPHALT = (131, 129, 121)
METAL = (51, 61, 58)
BENCH = (184, 153, 45)


def nearby_surfaces(metadata):
    agate = site.read(metadata / "agate-thirteenth-fifteenth.json")
    hayward = site.read(metadata / "hayward-exterior-review.json")
    fields = site.read(metadata / "hayward-midblock.json")
    existing = west.surface(agate["walk_joins"]).intersection(
        box(75.65, -292, 83.5, -221)
    )
    plaza_base = west.surface(hayward["plazas"]).intersection(box(-48, -288, 79, -247))
    south_join = west.surface(fields["src_walks"])
    junction = box(-307.15, -251.5, -300.25, -234.5)
    return unary_union([existing, plaza_base, south_join, junction])


def bed_borders(rows):
    return unary_union(
        [
            box(x0 + 0.57, y0 + 0.57, x1 - 0.57, y1 - 0.57).buffer(0.57, quad_segs=4)
            for x0, y0, x1, y1 in rows
        ]
    )


def paving(ground, field, spec, buildings, prior):
    road = east.band(spec["west_road"]).difference(buildings)
    approach = west.surface(spec["west_paving"]).difference(buildings)
    plaza = Polygon(spec["promenade"]).buffer(0).difference(buildings)
    bed_area = bed_borders(spec["bed_bounds"]).intersection(plaza)
    pavers = plaza.difference(road.union(bed_area).union(prior))
    paved = road.union(approach).union(plaza.difference(bed_area))
    # Use restrained variations on the photographed gray pavers.
    textured = pavers.intersection(box(19.7, -273.3, 75.4, -239.5))
    insets = [[], [], []]
    for row, n in enumerate(np.arange(-273.1, -239.6, 0.68)):
        for col, e in enumerate(np.arange(20.0 + (row % 3) * 0.39, 75.3, 1.49)):
            if (col + row * 3) % 5 < 3:
                tile = box(e, n, e + 1.29, n + 0.54).intersection(textured)
                if not tile.is_empty:
                    insets[(col * 7 + row) % 3].append(tile)
    accents = [unary_union(shapes) for shapes in insets]
    for shape, tint, lift, cell in (
        (road.difference(prior), ASPHALT, 0.092, 1.26),
        (approach.difference(plaza.union(road).union(prior)), CONCRETE, 0.138, 0.85),
        (pavers.difference(unary_union(accents)), PAVERS, 0.133, 1.06),
        (bed_area.difference(prior), (119, 113, 83), 0.114, 0.82),
        *(
            (shape, color, 0.133, 0.93)
            for shape, color in zip(
                accents, ((143, 143, 135), (157, 154, 144), (162, 160, 147))
            )
        ),
    ):
        if not shape.is_empty:
            site.drape(ground, field, shape, tint, lift, cell)
    markings = axis.central.buffered_lines(spec["crossings"], 0.19).intersection(road)
    site.drape(ground, field, markings, (218, 215, 200), 0.155, 0.78)
    return paved, bed_area, [round(s.area, 2) for s in (road, pavers, bed_area)]


def tables_and_lamps(details, field, spec):
    blockers = []
    for e, n, angle in spec["bench"]:
        base = site.ground_height(field, e, n) + 0.13
        shape = translate(
            rotate(box(-1.09, -0.36, 1.09, 0.36), angle, origin=(0, 0)), e, n
        )
        for offset in (-1.01, 1.01):
            plate = rotate(
                box(offset - 0.093, -0.34, offset + 0.093, 0.34), angle, origin=(0, 0)
            )
            site.solid(details, translate(plate, e, n), base, base + 0.79, BENCH)
        site.solid(
            details, shape.buffer(-0.065), base + 0.43, base + 0.56, (87, 87, 77)
        )
        blockers.append(shape.envelope)
    for e, n in spec["lamp"]:
        z = site.ground_height(field, e, n) + 0.13
        site.cylinder_between(
            details, (e, n, z), (e, n, z + 3.75), 0.092, METAL, sides=9
        )
        site.cylinder_between(
            details, (e, n, z + 3.75), (e, n, z + 4.07), 0.091, (207, 204, 182), sides=9
        )
        site.cylinder_between(
            details, (e, n, z + 4.07), (e, n, z + 4.20), 0.096, METAL, sides=9
        )
    for e, n in spec["short_posts"]:
        z = site.ground_height(field, e, n) + 0.13
        site.cylinder_between(details, (e, n, z), (e, n, z + 0.93), 0.1, METAL, sides=9)
    return blockers


def powell(details, field, spec):
    blockers = midblock.practice.fence_run(details, field, spec["gate"], 1.89)
    for e, n in spec["kiosk"]:
        z = site.ground_height(field, e, n) + 0.13
        site.flat_box(details, e, n, 0.86, 0.38, z - 0.24, z + 1.89, METAL)
        site.flat_box(
            details, e, n + 0.197, 0.65, 0.024, z + 0.45, z + 1.68, (113, 129, 123)
        )
        site.flat_box(
            details, e, n + 0.214, 0.49, 0.027, z + 1.46, z + 1.56, (207, 202, 177)
        )
        blockers.append(box(e - 0.43, n - 0.19, e + 0.43, n + 0.19))
    base_line = LineString(spec["seating_line"])
    floor = 0.04
    for width, lift in ((1.49, 0.225), (1.04, 0.36), (0.59, 0.49)):
        seating = base_line.buffer(width, cap_style="flat", join_style="round")
        site.drape(details, field, seating, (111, 113, 103), lift, 0.73)
        ring = list(seating.exterior.coords)
        vertices, faces = [], []
        for (e0, n0), (e1, n1) in zip(ring, ring[1:]):
            z0 = site.ground_height(field, e0, n0)
            z1 = site.ground_height(field, e1, n1)
            first = len(vertices)
            vertices.extend(
                (
                    (e0, z0 + floor, -n0),
                    (e0, z0 + lift, -n0),
                    (e1, z1 + lift, -n1),
                    (e1, z1 + floor, -n1),
                )
            )
            faces.extend(((first, first + 1, first + 2), (first, first + 2, first + 3)))
        fascia = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        fascia.visual.vertex_colors = np.tile((91, 96, 86, 255), (len(vertices), 1))
        details.append(fascia)
        floor = lift
    for j, (e, n, h) in enumerate(spec["flags"]):
        z = site.ground_height(field, e, n) + 0.135
        tip = z + h
        site.cylinder_between(
            details, (e, n, z - 0.22), (e, n, tip), 0.061, (186, 190, 179), sides=10
        )
        site.orb(details, (e, n, tip), (0.088, 0.088, 0.103), (200, 198, 180))
        palette = ((54, 65, 104), (166, 57, 60), (230, 224, 204))
        for section in range(9):
            x = e - (section + 0.5) * 0.19
            drift = 0.19 * np.sin(section * 0.47 + j)
            z0 = tip - 1.35 - section * 0.022
            if j == 1:
                for stripe in range(7):
                    lo = z0 + stripe * 0.155
                    color = (166, 57, 60) if stripe % 2 == 0 else (224, 217, 199)
                    site.flat_box(
                        details, x, n + drift, 0.19, 0.056, lo, lo + 0.155, color
                    )
                if section < 4:
                    site.flat_box(
                        details,
                        x,
                        n + drift + 0.007,
                        0.19,
                        0.065,
                        z0 + 0.51,
                        z0 + 1.085,
                        (54, 65, 104),
                    )
            else:
                site.flat_box(
                    details, x, n + drift, 0.19, 0.056, z0, z0 + 1.085, palette[j]
                )
    return blockers


def plantings(parts, field, beds, trees):
    for i, tree in enumerate(trees):
        site.canopy(parts, field, tree, i)
    county = np.random.default_rng(1530)
    x0, y0, x1, y1 = beds.bounds
    count = 0
    for e in np.arange(x0 + 0.23, x1, 1.17):
        for n in np.arange(y0 + 0.27, y1, 1.11):
            e2, n2 = (e, n) + county.uniform(-0.21, 0.21, 2)
            if not beds.contains(Point(e2, n2)):
                continue
            z = site.ground_height(field, e2, n2)
            h = float(county.uniform(0.24, 0.58))
            site.orb(
                parts,
                (e2, n2, z + h * 0.68),
                (h * 1.04, h * 0.91, h * 0.72),
                (92 + count % 4 * 5, 106 + count % 5 * 4, 68),
            )
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    spec = site.read(metadata / "east-fifteenth-hayward.json")
    manifest, field, graph = east.pinned_site(site.scene, spec)
    buildings, previous = east.build_blockers(
        site.scene, spec, manifest, box(*spec["extent"])
    )
    prior = nearby_surfaces(metadata)
    ground, detail, planting = [], [], []
    paved, beds, areas = paving(ground, field, spec, buildings, prior)
    blockers = tables_and_lamps(detail, field, spec) + powell(detail, field, spec)
    assert len(blockers) <= 16
    trees = [
        row
        for row in spec["trees"]
        if buildings.distance(Point(*row["position_enu_m"])) > 0.34
    ]
    shrubs = plantings(planting, field, beds, trees)
    straub = site.read(metadata / "central-campus-greens-review.json")["zones"][
        "straub"
    ]
    trunks = [
        Point(*row["position_enu_m"]).buffer(0.20) for row in [*trees, *straub["trees"]]
    ]
    edges, lengths = west.check_routes(
        graph,
        spec["routes"],
        paved.union(prior),
        buildings.union(previous).union(unary_union([*blockers, *trunks])),
    )
    padded = unary_union(
        [
            item.buffer(0.501, join_style=2)
            for item in [*blockers, *getattr(previous, "geoms", [previous])]
        ]
    )
    for branch in spec["routes"]:
        points = [branch["anchor_enu_m"], *branch["points_enu_m"]]
        if "end_enu_m" in branch:
            points.append(branch["end_enu_m"])
        line = LineString(points)
        assert not line.intersects(padded), line.intersection(padded).wkt
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        (DETAIL, detail, "landscape-detail"),
        (PLANT, planting, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    pins = spec["pins"]
    bounds = [
        [-308, -267, -220, -223],
        [-221, -268, -132, -222],
        [-133, -268, -44, -222],
        [-45, -278, 43, -220],
        [42, -288, 79, -222],
    ]
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
            context_trees=spec["clear_context_trees"],
            walkable_ground=dict(paths=spec["routes"], bounds_enu_m=bounds),
            closed_site_boxes_enu_m=[
                [round(v, 4) for v in shape.bounds] for shape in blockers
            ],
        ),
        compact=True,
    )
    audit = dict(
        road_m2=areas[0],
        plaza_pavers_m2=areas[1],
        planted_m2=areas[2],
        trees=[row["tree_id"] for row in trees],
        shrubs=shrubs,
        bench_count=len(spec["bench"]),
        lamp_count=len(spec["lamp"]),
        flag_count=len(spec["flags"]),
        fence_m=round(LineString(spec["gate"]).length, 2),
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
