# SPDX-License-Identifier: Apache-2.0
"""Register the Old Campus Quad crosswalks and the Class of 1893 stone."""

import argparse
from importlib import import_module
from math import cos, radians, sin
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

sundial = import_module("build-science-green-sundial")
onyx = import_module("build-onyx-green-walks")
site = sundial.site
PACKAGE = "old-campus-quad-landscape-review"
GROUND = "old-campus-quad-crosswalks"
METADATA = site.root / "data/metadata"


def points(row):
    return [
        row["anchor_enu_m"],
        *row["points_enu_m"],
        *([row["end_enu_m"]] if "end_enu_m" in row else []),
    ]


def layout(spec):
    fenton = site.read(METADATA / "fenton-site-review.json")["north_landscape"]
    courtyard = site.read(METADATA / "heritage-courtyard-landscape.json")
    hello_walk = LineString(fenton["hello_walk_centerline_enu_m"]).buffer(
        fenton["hello_walk_width_m"] / 2, cap_style="flat"
    )
    prior = unary_union(
        [
            hello_walk,
            Polygon(courtyard["patio_enu_m"]),
            *[
                LineString(points(row)).buffer(row["width_m"] / 2, cap_style="flat")
                for row in courtyard["route_paths"]
            ],
        ]
    )
    hosts = [
        b
        for key in spec["pins"]
        for b in site.read(site.scene / key / "site.json")["buildings"]
    ]
    buildings = unary_union(
        [
            Polygon(ring).buffer(0.035)
            for b in hosts
            for ring in (
                *b.get("ground_footprints_enu_m", [b["footprint_enu_m"]]),
                *b.get("support_collision_enu_m", []),
            )
        ]
    )
    walks = unary_union(
        [
            LineString(points(row)).buffer(row["width_m"] / 2, quad_segs=6)
            for row in spec["paths"]
        ]
    )
    return walks.difference(prior.union(buildings)), prior, buildings


def route_coverage(spec):
    paving, hello_walk, _ = layout(spec)
    return paving.union(hello_walk)


def fit_grade(spec, field, prior):
    medians = {(e, n): median for e, n, median in spec["dem_samples_enu_m"]}
    profiles = []
    for row in spec["paths"]:
        xy = points(row)
        line = LineString(xy)
        heights = [
            float(
                np.clip(
                    medians[e, n] - 0.33,
                    site.ground_height(field, e, n) + 0.085,
                    site.ground_height(field, e, n) + 0.24,
                )
            )
            for e, n in xy
        ]
        profiles.append((line, onyx.north.longitudinal_grade(np.array(xy), heights)))

    def surface(east, north):
        pivot = Point(east, north)
        _, profile = min(profiles, key=lambda row: row[0].distance(pivot))
        base = site.ground_height(field, east, north)
        share = min(1.0, prior.distance(pivot) / 2.15)
        return (1 - share) * (base + 0.097) + share * profile(east, north)

    return surface


def carve_marker(spec, field):
    e, n = spec["position_enu_m"]
    w, d, h = spec["width_depth_height_m"]
    a = radians(spec["face_azimuth_degrees"])
    out = np.array([sin(a), cos(a)])
    right = np.array([-out[1], out[0]])
    grade = site.ground_height(field, e, n) + 0.036
    center = np.array([e, n])

    def position(x, depth, height):
        p, q = center + right * x + out * depth
        return p, grade + height, -q

    # The broad face remains nearly planar and the other three faces keep the
    # irregular outline of the field photograph.
    angles = [
        (-0.50, 0.18),
        (-0.39, 0.5),
        (0.38, 0.5),
        (0.50, 0.21),
        (0.45, -0.29),
        (0.23, -0.5),
        (-0.31, -0.46),
        (-0.50, -0.23),
    ]
    rings = [
        (-0.09, 0.84, 0.82),
        (0.08, 0.92, 0.96),
        (0.34, 0.97, 1),
        (0.65, 1, 1),
        (0.91, 0.98, 0.96),
        (1.0, 0.86, 0.89),
    ]
    rng = np.random.default_rng(1893)
    vertices = []
    for z, spread, thickness in rings:
        for index, (x, y) in enumerate(angles):
            if index not in (1, 2):
                x += rng.uniform(-0.065, 0.065)
                y += rng.uniform(-0.04, 0.04)
            lip = rng.uniform(-0.03, 0.03) if z == 1.0 else 0
            vertices.append(position(x * w * spread, y * d * thickness, z * h + lip))
    mesh = trimesh.Trimesh(
        vertices=vertices,
        faces=sundial.stone_faces(len(rings), len(angles)),
        process=False,
    )
    mesh.fix_normals()
    mesh.unmerge_vertices()
    tones = np.array(
        [
            (119, 115, 99),
            (99, 103, 88),
            (131, 127, 111),
            (111, 116, 98),
            (85, 94, 77),
            (142, 140, 120),
        ],
        dtype=np.uint8,
    )
    rgb = np.repeat(tones[rng.integers(len(tones), size=len(mesh.faces))], 3, axis=0)
    mesh.visual.vertex_colors = np.column_stack(
        [rgb, np.full(len(rgb), 255, dtype=np.uint8)]
    )
    letters, soil = [], []
    for label, low in zip(spec["inscription"], (0.72, 0.59, 0.435), strict=True):
        gap = 0.068
        width = 0.048
        glyph_h = 0.076
        for j, letter in enumerate(label):
            origin = (j - (len(label) - 1) / 2) * gap - width / 2
            for stroke in site.GLYPHS[letter]:
                for (x, y), (x2, y2) in zip(stroke, stroke[1:]):
                    path = [
                        position(
                            origin + width * u, d / 2 + 0.002, (low + v * glyph_h) * h
                        )
                        for u, v in ((x, y), (x2, y2))
                    ]
                    site.cylinder_between(
                        letters,
                        *((p, -q, z) for p, z, q in path),
                        0.0042,
                        (62, 68, 57),
                        sides=6,
                    )
    bed = Point(e, n).buffer(0.46, quad_segs=8)
    site.drape(soil, field, bed, (103, 96, 76), 0.059, 0.32)
    corners = [position(x, y, 0) for x in (-w / 2, w / 2) for y in (-d / 2, d / 2)]
    footprint = Polygon([(p, -q) for p, _, q in corners]).convex_hull
    return [mesh], letters, soil, footprint.envelope.buffer(0.022).envelope


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(METADATA / "old-campus-quad-landscape.json")
    for key, digest in spec["pins"].items():
        assert site.pin(site.scene / key / "site.json") == digest, key
    fenton = site.read(site.scene / "fenton-site-review/site.json")
    original = {
        tuple(p) for path in fenton["walkable_ground"]["paths"] for p in points(path)
    }
    for path in spec["paths"]:
        assert tuple(path["anchor_enu_m"]) in original
        if "end_enu_m" in path:
            assert tuple(path["end_enu_m"]) in original
        assert not original.intersection(map(tuple, path["points_enu_m"]))
        original.update(map(tuple, path["points_enu_m"]))
    paving, prior, buildings = layout(spec)
    cover = paving.union(prior).buffer(0.13)
    traces = [LineString(points(row)) for row in spec["paths"]]
    for trace in traces:
        assert trace.difference(cover).length < 0.007
        assert trace.distance(buildings) > 0.5
    trees = site.read(METADATA / "context-trees-l2.json")["trees"]
    for row in spec["retired_context"]:
        e, _, z = trees[row["index"]]["origin_gltf_m"]
        assert np.allclose([e, -z], row["position_enu_m"], atol=0.007)
        assert paving.buffer(0.71).covers(Point(e, -z))
    _, field, _ = sundial.east.pinned_site(
        site.scene, site.read(METADATA / "east-thirteenth-east.json")
    )
    grade = fit_grade(spec, field, prior)
    ground, edges = [], []
    onyx.south.pave(ground, edges, paving, grade, field, (164, 158, 144))
    margins = paving.buffer(0.79).difference(unary_union([paving, prior, buildings]))

    def slope(e, n):
        ratio = min(1.0, paving.distance(Point(e, n)) / 0.79)
        return ratio * (site.ground_height(field, e, n) + 0.038) + (1 - ratio) * (
            grade(e, n) - 0.016
        )

    site.landscape.top_surface(ground, margins, slope, (123, 133, 100), cell=0.73)
    stone, letters, dirt, collider = carve_marker(spec["class_stone"], field)
    inventoried_trees = []
    trunk_bounds = []
    for index, tree in enumerate(spec["trees"]):
        site.canopy(inventoried_trees, field, tree, index)
        radius = max(0.18, min(0.58, tree["crown_radius_m"] * 0.088))
        stem = Point(*tree["position_enu_m"]).buffer(radius).envelope
        assert min(line.distance(stem) for line in traces) > 0.61
        trunk_bounds.append(stem.bounds)
    args.stage.mkdir(parents=True, exist_ok=True)
    asset, descriptor = args.stage / "site.glb", args.stage / "site.json"
    counts = site.export(
        asset,
        (GROUND, ground, "landscape-surface"),
        ("old-campus-quad-paving-edges", edges, "landscape-detail"),
        ("class-of-1893-stone", stone, "landscape-detail"),
        ("class-of-1893-inscription", letters, "landscape-detail"),
        ("class-of-1893-stone-setting", dirt, "landscape-vegetation"),
        ("old-campus-quad-inventory-trees", inventoried_trees, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    paths = [{k: v for k, v in row.items() if k != "width_m"} for row in spec["paths"]]
    doc = {
        **{
            key: fenton[key]
            for key in (
                "source_presentation_sha256",
                "source_base_model_sha256",
                "source_heightfield_sha256",
                "source_navigation_sha256",
            )
        },
        "prerequisite_site_sha256": spec["pins"]["fenton-site-review"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": site.pin(asset),
        "buildings": [],
        "context_trees": spec["retired_context"],
        "closed_site_boxes_enu_m": [collider.bounds, *trunk_bounds],
        "walkable_ground": {"bounds_enu_m": [paving.bounds], "paths": paths},
    }
    site.fairmount.write_json(descriptor, doc, compact=True)
    audit = dict(
        paving_m2=round(paving.area, 3),
        shoulder_m2=round(margins.area, 3),
        distances_m=[round(trace.length, 3) for trace in traces],
        navigation_edges=sum(len(points(row)) - 1 for row in paths),
        faces=counts,
        asset_sha256=site.pin(asset),
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
