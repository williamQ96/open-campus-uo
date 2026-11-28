# SPDX-License-Identifier: Apache-2.0
"""Build the Science Green west walk, planting and above-grade glass enclosure."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import get_parts
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

sundial = import_module("build-science-green-sundial")
onyx = import_module("build-onyx-green-walks")
planting = import_module("build-hedco-courtyard-landscape")
site = sundial.site
PACKAGE = "science-green-west-review"
GROUND = "science-green-west-paving"
GLASS = "science-green-stair-glass"
METADATA = site.root / "data/metadata"


def path_line(row):
    return LineString([station[:2] for station in row["stations"]])


def site_layout(spec):
    prior, north_bed = sundial.outdoor_footprint(
        site.read(METADATA / "science-green-sundial.json")
    )
    host = site.read(site.scene / "northeast-science-review/site.json")
    buildings = unary_union(
        [
            Polygon(ring).buffer(0.035)
            for row in host["buildings"]
            for ring in (
                *row.get("ground_footprints_enu_m", [row["footprint_enu_m"]]),
                *row.get("support_collision_enu_m", []),
            )
        ]
    )
    enclosure = box(*spec["enclosure"]["base_extent_enu_m"])
    trunks = [
        Point(*row["position_enu_m"]).buffer(0.13).envelope for row in spec["trees"]
    ]
    reserved = unary_union([buildings, enclosure, *trunks, north_bed])
    walks = unary_union(
        [
            path_line(row).buffer(row["width_m"] / 2, quad_segs=6)
            for row in spec["paths"]
        ]
        + [Polygon(points) for points in spec["paving_additions"]]
    )
    paving = walks.difference(prior.union(reserved))
    beds = [
        Polygon(row["outline"]).difference(
            unary_union(
                [
                    walks.buffer(0.035),
                    prior,
                    north_bed,
                    buildings,
                    enclosure.buffer(0.065),
                ]
            )
        )
        for row in spec["beds"]
    ]
    return paving, prior, beds, enclosure, reserved, buildings, trunks


def route_coverage(spec):
    return site_layout(spec)[0]


def lawn_outline(spec, paving, previous):
    control = Point(*spec["lawn"]["interior_control_enu_m"])
    outlines = [
        Polygon(ring)
        for part in get_parts(paving.union(previous).buffer(0.001))
        if part.geom_type == "Polygon"
        for ring in part.interiors
    ]
    return next(area for area in outlines if area.contains(control))


def lawn_details(spec, lawn, edge_grade, layers):
    control_e, control_n, control_z = spec["median_fit_origin_enu_z_m"]
    east_slope, north_slope = spec["approximate_grade_east_north"]
    boundary = lawn.boundary

    def grade(east, north):
        point = Point(east, north)
        d = min(1, boundary.distance(point) / 2.65)
        fitted = (
            control_z
            + (east - control_e) * east_slope
            + (north - control_n) * north_slope
        )
        return d * fitted + (1 - d) * (edge_grade(east, north) - 0.014)

    site.landscape.top_surface(layers, lawn, grade, (143, 155, 103), cell=0.76)
    bed = Polygon(spec["central_bed_enu_m"])
    row = spec["central_feature"]
    axis = LineString(row["axis_enu_m"])
    footprint = axis.buffer(row["depth_m"] / 2, cap_style="flat")
    assert lawn.contains(bed) and bed.covers(footprint)
    soil, cluster, detail = [], [], []
    site.landscape.top_surface(
        soil, bed, lambda e, n: grade(e, n) + 0.052, (115, 121, 83), cell=0.43
    )
    interior = bed.difference(footprint.buffer(0.50)).buffer(-0.30)
    for east in np.arange(bed.bounds[0] + 0.4, bed.bounds[2], 0.68):
        for north in np.arange(bed.bounds[1] + 0.4, bed.bounds[3], 0.77):
            if interior.covers(Point(east, north)):
                site.orb(
                    cluster,
                    (east, north, grade(east, north) + 0.19),
                    (0.39, 0.40, 0.24),
                    (114, 129, 79),
                )
    top = row["top_z_m"]
    site.solid(detail, footprint, 1.40, top - 0.04, (111, 116, 107))
    cap = axis.buffer(row["depth_m"] / 2 + 0.035, cap_style="flat")
    site.solid(detail, cap, top - 0.04, top, (103, 115, 111))
    return soil, cluster, detail, box(*footprint.bounds), bed.area


def finish_grades(spec, field, prior):
    patterns = []
    for row in spec["paths"]:
        path = np.asarray(row["stations"])
        patterns.append(
            (path_line(row), onyx.north.longitudinal_grade(path[:, :2], path[:, 2]))
        )

    def grade(east, north):
        point = Point(east, north)
        _, nearest = min(patterns, key=lambda pattern: pattern[0].distance(point))
        z = nearest(east, north)
        blend = min(1, prior.distance(point) / 1.85)
        return blend * z + (1 - blend) * (
            site.ground_height(field, east, north) + 0.112
        )

    return grade


def stairs(row):
    base, glaze = [], []
    west, south, east, north = row["base_extent_enu_m"]
    z = row["base_z_m"]
    top = z + row["roof_height_m"]
    slab = box(west, south, east, north)
    rim = (166, 163, 147)
    metal = (76, 83, 79)
    frame = (109, 117, 111)
    site.solid(base, slab, z - 0.27, z + 0.043, rim)
    site.solid(
        base,
        slab.buffer(row["roof_overhang_m"], join_style="mitre"),
        top - 0.026,
        top,
        metal,
    )
    site.solid(base, slab, top - 0.078, top - 0.025, frame)
    for x in (west + 0.075, east - 0.075):
        for n in (south + 0.075, (north + south) / 2, north - 0.075):
            site.cylinder_between(
                base, (x, n, z + 0.035), (x, n, top - 0.062), 0.035, frame, sides=10
            )
    glass_tint = (178, 211, 206)
    segments = [
        ((west + 0.035, south + 0.035), (west + 0.035, north - 0.035), 4),
        ((east - 0.035, south + 0.035), (east - 0.035, north - 0.035), 4),
        ((west + 0.035, south + 0.035), (east - 0.035, south + 0.035), 2),
        ((west + 0.035, north - 0.035), (east - 0.035, north - 0.035), 3),
    ]
    for a, b, bays in segments:
        side = LineString([a, b])
        site.solid(
            base, side.buffer(0.031, cap_style="flat"), z + 0.04, z + 0.095, frame
        )
        for i in range(bays):
            pa, pb = [
                side.interpolate(f / bays, normalized=True).coords[0]
                for f in (i, i + 1)
            ]
            pane = LineString([pa, pb]).buffer(0.008, cap_style="flat")
            site.solid(glaze, pane, z + 0.095, top - 0.078, glass_tint)
            colors = glaze[-1].visual.vertex_colors.copy()
            colors[:, 3] = row["glass_alpha"]
            glaze[-1].visual.vertex_colors = colors
            if i:
                # Narrow joints preserve the mostly frameless appearance.
                width = 0.022 if a[1] == b[1] == north - 0.035 else 0.008
                site.solid(
                    base, Point(*pa).buffer(width), z + 0.096, top - 0.078, frame
                )
    for x in (west + 0.54, east - 0.56):
        for y in (north - 1.11, north - 2.12):
            site.cylinder_between(
                base, (x, y, z + 0.044), (x, y, z + 0.87), 0.021, frame, sides=9
            )
        site.cylinder_between(
            base,
            (x, north - 0.84, z + 0.87),
            (x, north - 2.44, z + 0.87),
            0.024,
            frame,
            sides=9,
        )
    return base, glaze


def vegetation(spec, field, beds, grade):
    soil, edging, shrubs, trees = [], [], [], []
    clusters = []
    for row, shape in zip(spec["beds"], beds, strict=True):
        if row["curb"]:
            cap = shape.difference(shape.buffer(-0.117))
            site.landscape.top_surface(
                edging,
                cap,
                lambda e, n: grade(e, n) + 0.102,
                (153, 148, 131),
                cell=0.36,
            )
        level = 0.06 if row["curb"] else 0.035

        def bed_grade(east, north):
            return grade(east, north) + level

        site.landscape.top_surface(soil, shape, bed_grade, (109, 109, 78), cell=0.52)
        inner = shape.buffer(-0.32)
        left, south, right, north = shape.bounds
        total = 0
        spacing = row["density"]
        for e in np.arange(left + 0.41, right, spacing):
            for n in np.arange(south + 0.42, north, spacing):
                if not inner.covers(Point(e, n)):
                    continue
                radius = 0.28 if row["curb"] else 0.48
                lift = bed_grade(e, n) - site.ground_height(field, e, n) - 0.015
                planting.planted_crown(
                    shrubs,
                    field,
                    e,
                    n,
                    radius,
                    0.26 if row["curb"] else 0.49,
                    e + n,
                    base=lift,
                )
                total += 1
        clusters.append(total)
    for index, row in enumerate(spec["trees"]):
        site.canopy(trees, field, {**row, "form": "rounded"}, index)
    return soil, edging, shrubs, trees, clusters


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(METADATA / "science-green-west.json")
    for key, digest in spec["pins"].items():
        assert site.pin(site.scene / key / "site.json") == digest, key
    east = site.read(site.scene / "science-green-sundial-review/site.json")
    tree_index = spec["context_retirement"]["index"]
    context_tree = site.read(METADATA / "context-trees-l2.json")["trees"][tree_index]
    x, _, south = context_tree["origin_gltf_m"]
    assert np.allclose(
        [x, -south], spec["context_retirement"]["position_enu_m"], atol=0.006
    )

    paving, prior, beds, enclosure, reserved, buildings, trunks = site_layout(spec)
    cover = paving.union(prior).buffer(0.13)
    clearances = []
    for path in spec["paths"]:
        line = path_line(path)
        assert line.difference(cover).length < 0.006, line.difference(cover).wkt
        clearances.append(line.distance(reserved.union(unary_union(beds))))
    assert min(clearances) > 0.49, clearances

    existing = {
        tuple(p)
        for path in east["walkable_ground"]["paths"]
        for p in path["points_enu_m"]
    }
    paths = []
    for row in spec["paths"]:
        a, *points = [p[:2] for p in row["stations"]]
        assert tuple(a) in existing
        end = {"end_enu_m": points.pop()} if tuple(points[-1]) in existing else {}
        assert all(tuple(p) not in existing for p in points)
        existing.update(map(tuple, points))
        paths.append(dict(anchor_enu_m=a, points_enu_m=points, **end))

    _, field, _ = sundial.east.pinned_site(
        site.scene, site.read(METADATA / "east-thirteenth-east.json")
    )
    grade = finish_grades(spec, field, prior)
    ground, curb = [], []
    onyx.south.pave(ground, curb, paving, grade, field, (169, 160, 145))
    lawn = lawn_outline(spec, paving, prior)
    margin = paving.buffer(1.18).difference(
        unary_union([paving, prior, buildings, enclosure, lawn, *beds])
    )

    def verge(east, north):
        share = max(0, 1 - paving.distance(Point(east, north)) / 1.18)
        field_z = site.ground_height(field, east, north) + 0.045
        return (1 - share) * field_z + share * (grade(east, north) - 0.013)

    site.landscape.top_surface(ground, margin, verge, (119, 128, 91), cell=0.54)
    soil, edging, shrubs, trees, clusters = vegetation(spec, field, beds, grade)
    lawn_soil, lawn_plants, lawn_feature, lawn_solid, central_bed_m2 = lawn_details(
        spec["lawn"], lawn, grade, ground
    )
    building, glaze = stairs(spec["enclosure"])
    args.stage.mkdir(parents=True, exist_ok=True)
    asset = args.stage / "site.glb"
    descriptor = args.stage / "site.json"
    faces = site.export(
        asset,
        (GROUND, ground, "landscape-surface"),
        ("science-green-west-paving-edges", curb + edging, "landscape-detail"),
        ("science-green-west-planting-soil", soil + lawn_soil, "landscape-vegetation"),
        ("science-green-west-understory", shrubs + lawn_plants, "landscape-vegetation"),
        ("science-green-west-tree-inventory", trees, "landscape-vegetation"),
        ("science-green-glass-stair-enclosure", building, "landscape-detail"),
        (GLASS, glaze, "landscape-detail"),
        ("science-green-lawn-feature", lawn_feature, "landscape-detail"),
        surface_layer=GROUND,
        translucent_nodes=(GLASS,),
    )
    site.fairmount.write_json(
        descriptor,
        {
            **{
                k: east[k]
                for k in (
                    "source_presentation_sha256",
                    "source_base_model_sha256",
                    "source_heightfield_sha256",
                    "source_navigation_sha256",
                )
            },
            "prerequisite_site_sha256": spec["pins"]["science-green-sundial-review"],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(asset),
            "buildings": [],
            "context_trees": [spec["context_retirement"]],
            "closed_site_boxes_enu_m": [
                enclosure.bounds,
                lawn_solid.bounds,
                *(ring.bounds for ring in trunks),
            ],
            "walkable_ground": {"bounds_enu_m": [paving.bounds], "paths": paths},
        },
        compact=True,
    )
    report = {
        "paving_m2": round(paving.area, 3),
        "transitions_m2": round(margin.area, 3),
        "beds_m2": [round(shape.area, 3) for shape in beds],
        "planted_clusters": clusters,
        "lawn_m2": round(lawn.area, 3),
        "central_bed_m2": round(central_bed_m2, 3),
        "tree_ids": [row["id"] for row in spec["trees"]],
        "navigation_edges": sum(
            len(path["points_enu_m"]) + int("end_enu_m" in path) for path in paths
        ),
        "distances_m": [round(path_line(path).length, 3) for path in spec["paths"]],
        "minimum_centerline_clearance_m": round(min(clearances), 3),
        "faces": faces,
        "asset_sha256": site.pin(asset),
        "descriptor_sha256": site.pin(descriptor),
    }
    site.fairmount.write_json(args.audit, report)
    print(report)


if __name__ == "__main__":
    main()
