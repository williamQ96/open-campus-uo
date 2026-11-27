# SPDX-License-Identifier: Apache-2.0
"""Build the Mays memorial sundial and the visible Science Green approach."""

import argparse
from importlib import import_module
from math import atan2, cos, pi, radians, sin
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

east = import_module("build-east-thirteenth-east")
site = east.site
PACKAGE = "science-green-sundial-review"
GROUND = "science-green-paving"
STONE = "mays-sundial-granite"
DIAL = "mays-sundial-dial"


def granite(parts, row, grade):
    east_m, north_m = row["position_enu_m"]
    width, depth, height = row["width_depth_height_m"]
    rng = np.random.default_rng(1912)
    rings = [
        (-0.09, 0.98, 0.99, 0, 0),
        (0.17, 1, 1, -0.02, 0.01),
        (0.39, 0.93, 0.97, 0.022, -0.01),
        (0.67, 0.88, 0.84, 0.012, 0.013),
        (0.86, 0.83, 0.86, -0.021, 0.018),
        (1, 0.78, 0.81, 0, 0),
    ]
    count = 12
    vertices = []
    for k, (z, rx, ry, dx, dy) in enumerate(rings):
        for j in range(count):
            angle = 2 * pi * j / count
            wobble = rng.uniform(0.91, 1.04)
            e = east_m + dx + width * rx * cos(angle) * wobble / 2
            n = north_m + dy + depth * ry * sin(angle) * wobble / 2
            relief = rng.uniform(-0.069, 0.066) if 0 < k < len(rings) - 1 else 0
            vertices.append((e, grade + z * height + relief, -n))
    mesh = trimesh.Trimesh(
        vertices=vertices, faces=stone_faces(len(rings), count), process=False
    )
    mesh.unmerge_vertices()
    tones = np.array(
        [
            [175, 169, 148],
            [181, 174, 152],
            [159, 153, 135],
            [168, 161, 143],
            [183, 176, 153],
        ],
        dtype=np.uint8,
    )
    rgb = np.repeat(tones[rng.integers(len(tones), size=len(mesh.faces))], 3, axis=0)
    mesh.visual.vertex_colors = np.column_stack(
        [rgb, np.full(len(rgb), 255, dtype=np.uint8)]
    )
    parts.append(mesh)
    return Polygon([(e, -z) for e, _, z in vertices]).convex_hull


def stone_faces(rings, count):
    faces = [(0, j + 1, j) for j in range(1, count - 1)]
    for ring in range(rings - 1):
        for j in range(count):
            i, k = ring * count + j, ring * count + (j + 1) % count
            faces.extend([(i, k, i + count), (k, k + count, i + count)])
    upper = (rings - 1) * count
    faces.extend((upper, upper + j, upper + j + 1) for j in range(1, count - 1))
    return faces


def dial(parts, row, grade):
    e, n = row["position_enu_m"]
    height = row["width_depth_height_m"][2]
    radius = row["dial_diameter_m"] / 2
    level = grade + height
    site.cylinder_between(
        parts,
        (e, n, level - 0.002),
        (e, n, level + 0.028),
        radius,
        (99, 87, 61),
        sides=48,
    )
    site.cylinder_between(
        parts,
        (e, n, level + 0.028),
        (e, n, level + 0.035),
        radius * 0.955,
        (126, 113, 75),
        sides=48,
    )
    face = level + 0.035
    for outer, inner in ((0.92, 0.903), (0.814, 0.798)):
        band = (
            Point(e, n)
            .buffer(outer * radius, quad_segs=24)
            .difference(Point(e, n).buffer(inner * radius, quad_segs=24))
        )
        site.solid(parts, band, face, face + 0.0015, (78, 70, 53))

    latitude = radians(row["latitude_degrees"])
    for hour in range(-6, 7):
        h = hour * pi / 12
        angle = atan2(sin(latitude) * sin(h), cos(h))
        a = (
            e + radius * 0.43 * sin(angle),
            n + radius * 0.43 * cos(angle),
            face + 0.002,
        )
        b = (
            e + radius * 0.79 * sin(angle),
            n + radius * 0.79 * cos(angle),
            face + 0.002,
        )
        site.cylinder_between(parts, a, b, 0.0011, (52, 49, 37), sides=6)

    length = radius * 0.68
    rise = length * sin(latitude) / cos(latitude)
    profile = [(0, 0), (length, 0), (length, rise)]
    vertices = [
        (e + offset, face + above, -(n + along))
        for offset in (-0.009, 0.009)
        for along, above in profile
    ]
    faces = [
        (0, 2, 1),
        (3, 4, 5),
        (0, 1, 3),
        (1, 4, 3),
        (1, 2, 4),
        (2, 5, 4),
        (2, 0, 5),
        (0, 3, 5),
    ]
    plate = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    plate.fix_normals()
    plate.visual.vertex_colors = [95, 82, 59, 255]
    parts.append(plate)


def place_registered_trees(parts, field, rows):
    boxes = []
    for i, tree in enumerate(rows):
        e, n = tree["position_enu_m"]
        z = site.ground_height(field, e, n)
        h, r = tree["height_m"], tree["crown_radius_m"]
        radius = 0.085 if tree["form"] == "rounded" else 0.126
        if tree["form"] == "rounded":
            site.canopy(parts, field, tree, i)
        else:
            site.cylinder_between(
                parts, (e, n, z - 0.08), (e, n, z + h * 0.80), radius, (101, 80, 66)
            )
            for x, y, level, width, tint in (
                (-0.22, 0.17, 0.55, 0.67, (98, 113, 78)),
                (0.18, -0.15, 0.72, 0.67, (108, 122, 84)),
                (0, 0, 0.84, 0.48, (114, 127, 89)),
            ):
                site.orb(
                    parts,
                    (e + x, n + y, z + level * h),
                    (r * width, r * width, h * 0.19),
                    tint,
                )
        boxes.append(
            box(
                e - radius - 0.025,
                n - radius - 0.025,
                e + radius + 0.025,
                n + radius + 0.025,
            )
        )
    return boxes


def forecourt_joints(spec, walk):
    court = Polygon(spec["forecourt_enu_m"])
    w, s, e, n = court.bounds
    lines = [LineString([(x, s), (x, n)]) for x in np.arange(-71.52, e, 1.92)]
    lines += [LineString([(w, y), (e, y)]) for y in (73.27, 75.19, 77.11)]
    return (
        unary_union(lines)
        .buffer(0.011)
        .intersection(court.intersection(walk).buffer(-0.025))
    )


def outdoor_footprint(spec):
    host = site.read(site.scene / "northeast-science-review/site.json")
    manifest = site.read(site.scene / "manifest.json")
    neighbors = {row["id"] for row in host["buildings"]} | set(host["absorbed_ids"])
    extent = box(-83, 6, -36, 82)
    solids = []
    for record in [
        *[b for b in manifest["buildings"] if b["id"] not in neighbors],
        *host["buildings"],
    ]:
        for ring in [
            record["footprint_enu_m"],
            *record.get("support_collision_enu_m", []),
        ]:
            shape = Polygon(ring).buffer(0)
            if shape.intersects(extent):
                solids.append(shape)
    blocked = unary_union(solids)
    path = spec["approach"]
    east_side = LineString([path["anchor_enu_m"], *path["points_enu_m"][:20]])
    court = Polygon(spec["forecourt_enu_m"])
    bed = Polygon(spec["north_bed_enu_m"])
    assert court.is_valid and bed.is_valid
    walk = east_side.buffer(
        spec["approach_width_m"] / 2, cap_style="round", quad_segs=6
    )
    return court.union(walk).difference(
        unary_union([blocked.buffer(0.035), bed.buffer(0.015)])
    ), bed.difference(blocked)


def build(spec, metadata, stage, audit):
    for directory, expected in spec["pins"].items():
        assert site.pin(site.scene / directory / "site.json") == expected, directory
    corridor = site.read(metadata / "east-thirteenth-east.json")
    corridor_desc = site.read(site.scene / "east-thirteenth-east-review/site.json")
    _, field, _ = east.pinned_site(site.scene, corridor)
    walk, bed = outdoor_footprint(spec)
    path = spec["approach"]
    assert any(
        path["anchor_enu_m"] in item["points_enu_m"]
        for item in corridor_desc["walkable_ground"]["paths"]
    )
    route = LineString([path["anchor_enu_m"], *path["points_enu_m"]])
    assert walk.buffer(0.11).covers(route), route.difference(walk.buffer(0.11)).wkt
    paved, rock, instrument, planting, joints, trees = [], [], [], [], [], []
    site.drape(paved, field, walk, (170, 164, 150), 0.112, 0.83)
    row = spec["sundial"]
    e, n = row["position_enu_m"]
    grade = site.ground_height(field, e, n) + 0.112
    plinth = granite(rock, row, grade)
    solid = box(*plinth.buffer(0.028).bounds)
    assert walk.covers(solid)
    tree_boxes = place_registered_trees(trees, field, spec["trees"])
    assert all(walk.intersection(box).area < 0.004 for box in tree_boxes)
    old = Point(*spec["context_retirement"]["position_enu_m"])
    assert walk.contains(old) and route.distance(old) < 0.20
    assert min(old.distance(box) for box in tree_boxes) > 1.5
    clearance = route.distance(unary_union([solid, bed, *tree_boxes]))
    assert clearance >= 0.51, clearance
    dial(instrument, row, grade)
    site.drape(
        joints, field, forecourt_joints(spec, walk), (145, 137, 124), 0.116, 0.68
    )
    site.drape(planting, field, bed, (119, 105, 83), 0.093, 0.69)
    hedco = import_module("build-hedco-courtyard-landscape")
    for i, (e, n, radius) in enumerate(spec["north_shrubs"]):
        assert bed.buffer(-radius * 0.78).covers(Point(e, n))
        hedco.planted_crown(
            planting, field, e, n, radius, 0.45 + 0.07 * (i % 3), i + 0.5, base=0.097
        )

    stage.mkdir(parents=True, exist_ok=True)
    asset, descriptor = stage / "site.glb", stage / "site.json"
    faces = site.export(
        asset,
        (GROUND, paved, "landscape-surface"),
        (STONE, rock, "landscape-detail"),
        (DIAL, instrument, "landscape-detail"),
        ("science-walk-paving-joints", joints, "landscape-detail"),
        ("science-green-registered-trees", trees, "landscape-vegetation"),
        ("science-green-north-bed", planting, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    site.fairmount.write_json(
        descriptor,
        {
            "source_presentation_sha256": corridor_desc["source_presentation_sha256"],
            "source_base_model_sha256": corridor_desc["source_base_model_sha256"],
            "source_heightfield_sha256": corridor_desc["source_heightfield_sha256"],
            "source_navigation_sha256": corridor_desc["source_navigation_sha256"],
            "prerequisite_site_sha256": spec["pins"]["northeast-science-review"],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(asset),
            "buildings": [],
            "context_trees": [spec["context_retirement"]],
            "closed_site_boxes_enu_m": [solid.bounds, *(b.bounds for b in tree_boxes)],
            "walkable_ground": {
                "bounds_enu_m": [(-79.3, 8.25, -38.1, 78.8)],
                "paths": [path],
            },
        },
        compact=True,
    )
    report = dict(
        inventory_trees=[row["id"] for row in spec["trees"]],
        retired_context_tree=spec["context_retirement"]["index"],
        paving_m2=round(walk.area, 2),
        bed_m2=round(bed.area, 2),
        path_edges=len(path["points_enu_m"]),
        path_m=round(route.length, 3),
        clearance_m=round(clearance, 3),
        sundial_grade_m=round(grade, 3),
        faces=faces,
        asset_sha256=site.pin(asset),
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(audit, report)
    print(report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    build(
        site.read(metadata / "science-green-sundial.json"),
        metadata,
        args.stage,
        args.audit,
    )


if __name__ == "__main__":
    main()
