# SPDX-License-Identifier: Apache-2.0
"""Export two registered northeast campus wayfinding sites."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.affinity import scale, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

green = import_module("build-southwest-campus-green")
site = green.site
PACKAGE = "northeast-campus-wayfinding-review"
GROUND = "northeast-wayfinding-paving"
MARKINGS = "northeast-wayfinding-markings"
SIGNS = "northeast-wayfinding-signs"
PLANTING = "northeast-wayfinding-planting"
GREEN = (40, 84, 73)
METAL = (63, 91, 83)
PALE = (221, 218, 198)
GOLD = (207, 170, 86)


def frame(center, front):
    origin = np.asarray(center)
    normal = np.asarray(front, dtype=float)
    normal /= np.linalg.norm(normal)
    tangent = np.array([-normal[1], normal[0]])

    def point(width, depth, height):
        e, n = origin + width * tangent + depth * normal
        return e, n, height

    return point


def plate(parts, point, shape, front, back, base, color):
    for piece in site.landscape.geometry.sections(shape):
        mesh = site.landscape.cap(piece, back, front, color)
        positions = [point(u, depth, base - h) for u, depth, h in mesh.vertices]
        mesh.vertices = [(e, z, -n) for e, n, z in positions]
        parts.append(mesh)


def frame_beam(parts, point, u, start, end, width, color):
    site.beam(parts, point(*u, start), point(*u, end), width, color)


def collision_boxes(spec):
    onyx = spec["onyx"]
    gateway = spec["gateway"]
    bed = Polygon(gateway["bed_outline_enu_m"])
    # The hedge curves vary with the contour. Short envelopes keep its north
    # side closed while leaving the west pedestrian fork clear.
    ranges = [(94.83, 97.35), (97.35, 100.10), (100.10, 103.95)]
    bounds = [bed.intersection(box(30, lo, 44, hi)).bounds for lo, hi in ranges]
    bounds.append(Polygon(onyx["planter_enu_m"]).bounds)
    for e, n in onyx["bollards_enu_m"]:
        bounds.append((e - 0.11, n - 0.11, e + 0.11, n + 0.11))
    for tree in onyx["trees"]:
        e, n = tree["position_enu_m"]
        radius = max(tree["trunk_radius_m"], 0.12)
        bounds.append((e - radius, n - radius, e + radius, n + radius))
    return bounds


def footprints(spec, field_blockers):
    gateway = spec["gateway"]
    bed = Polygon(gateway["bed_outline_enu_m"])
    blocked = field_blockers.union(bed)
    paths = unary_union(
        [
            LineString(row["centerline_enu_m"]).buffer(
                row["width_m"] / 2, cap_style="flat"
            )
            for row in gateway["walks"]
        ]
        + [Polygon(gateway["apron_enu_m"])]
    ).difference(blocked)
    crossing = Polygon(gateway["crossing_coverage_enu_m"]).difference(field_blockers)
    return paths, crossing, bed


def onyx_footprints(onyx, field_blockers):
    planter = Polygon(onyx["planter_enu_m"])
    structures = field_blockers.union(planter)
    entrance = Polygon(onyx["entry_enu_m"]).difference(structures)
    drive = Polygon(onyx["drive_enu_m"]).difference(structures.union(entrance))
    beds = unary_union([Polygon(outline) for outline in onyx["planting_beds_enu_m"]])
    beds = beds.difference(unary_union([structures, entrance, drive]))
    return entrance, drive, beds, planter


def wayfinding_blockers(scene, spec, manifest):
    blocking = [
        green.east.build_blockers(scene, spec, manifest, box(*bounds))
        for bounds in spec["extents"]
    ]
    return unary_union([shape for group in blocking for shape in group])


def gateway_sign(parts, field, row):
    a, b = (np.asarray(point) for point in row["post_centers_enu_m"])
    vector = b - a
    width = np.linalg.norm(vector)
    tangent = vector / width
    middle = (a + b) / 2
    point = frame(middle, (tangent[1], -tangent[0]))
    base = site.ground_height(field, *middle) + 0.16
    half = width / 2 - 0.24
    arch = [
        (x, 2.34 + 0.23 * (1 - (x / half) ** 2)) for x in np.linspace(-half, half, 19)
    ]
    face = Polygon([(-half, 0.43), (half, 0.43), *reversed(arch)])
    plate(parts, point, face, 0.069, -0.068, base, (37, 79, 77))
    outline = face.boundary.buffer(0.026, join_style="mitre")
    plate(parts, point, outline, 0.082, 0.063, base, (171, 184, 166))
    for side in (-1, 1):
        x = side * width / 2
        e, n, _ = point(x, 0, 0)
        bottom = site.ground_height(field, e, n) - 0.10
        for dx in (-0.114, 0.114):
            for depth in (-0.094, 0.094):
                frame_beam(
                    parts, point, (x + dx, depth), bottom, base + 2.72, 0.042, METAL
                )
        for z in np.arange(0.47, 2.50, 0.29):
            for start, end in ((-0.10, 0.10), (0.10, -0.10)):
                site.beam(
                    parts,
                    point(x + start, 0.096, base + z),
                    point(x + end, 0.096, base + z + 0.24),
                    0.018,
                    (151, 163, 146),
                )
        for low, high, span in ((2.69, 2.76, 0.33), (2.76, 2.86, 0.22)):
            plate(
                parts,
                point,
                box(x - span / 2, low, x + span / 2, high),
                0.15,
                -0.15,
                base,
                METAL,
            )
    # The gold disc uses a plain relief ring sized from the dated photograph.
    medallion = Point(0.01, 1.96).buffer(0.339, quad_segs=25)
    plate(parts, point, medallion, 0.094, 0.069, base, GOLD)
    ring = medallion.buffer(-0.045).boundary.buffer(0.011)
    plate(parts, point, ring, 0.104, 0.094, base, (168, 133, 69))
    site.text_strokes(
        parts,
        "UNIVERSITY OF OREGON",
        lambda u, h: point(u, 0.092, base + 0.87 + h),
        0.262,
        0.30,
        (234, 225, 185),
    )


def map_face(parts, point, base, manifest):
    map_extent = (-282, -99, 118, 157)
    region = box(*map_extent)
    panel = box(-0.443, 0.87, 0.443, 1.89)
    plate(parts, point, panel, 0.099, 0.084, base, (218, 216, 195))

    def plot(poly, depth, color):
        projected = scale(poly.intersection(region), 0.00193, 0.00300, origin=(-82, 28))
        placed = translate(projected, xoff=82, yoff=-28 + 1.39)
        clipped = placed.intersection(panel.buffer(-0.035))
        if not clipped.is_empty:
            plate(parts, point, clipped, depth + 0.006, depth, base, color)

    walks = unary_union(
        [
            LineString(row["centerline_enu_m"]).buffer(3.4)
            for row in manifest["corridors"]["features"]
            if len(row["centerline_enu_m"]) > 1
            and LineString(row["centerline_enu_m"]).intersects(region)
        ]
    )
    plot(walks, 0.099, (184, 176, 146))
    blocks = unary_union(
        [
            Polygon(row["footprint_enu_m"]).buffer(0)
            for row in manifest["buildings"]
            if region.intersects(Polygon(row["footprint_enu_m"]).buffer(0))
        ]
    )
    plot(blocks, 0.107, (88, 113, 87))
    pin = Point(-0.218, 1.72).buffer(0.043, quad_segs=8)
    plate(parts, point, pin, 0.119, 0.109, base, GOLD)


def onyx_station(parts, field, row, manifest):
    e, n = row["center_enu_m"]
    bearing = np.radians(row["front_bearing_degrees"])
    point = frame((e, n), (np.sin(bearing), np.cos(bearing)))
    base = site.ground_height(field, e, n) + 0.36
    for side in (-1, 1):
        x = side * 0.6858  # UO standard post spacing is 54 inches on center.
        for bottom, top, radius, color in (
            (-0.08, 0.055, 0.113, GREEN),
            (0.055, 0.78, 0.087, GREEN),
            (0.78, 2.35, 0.058, METAL),
            (2.31, 2.39, 0.081, GREEN),
            (2.39, 2.48, 0.051, GREEN),
        ):
            site.cylinder_between(
                parts,
                point(x, 0, base + bottom),
                point(x, 0, base + top),
                radius,
                color,
            )
        site.orb(parts, point(x, 0, base + 2.52), (0.056, 0.056, 0.056), GREEN)
    plate(parts, point, box(-0.530, 0.80, 0.530, 1.911), 0.091, -0.087, base, GREEN)
    plate(
        parts,
        point,
        box(-0.538, 1.929, 0.538, 2.078),
        0.075,
        -0.075,
        base,
        (65, 99, 78),
    )
    plate(parts, point, box(-0.587, 2.124, 0.587, 2.281), 0.305, -0.305, base, GREEN)
    for label, y, size, height, depth in (
        ("MAP", 2.155, 0.085, 0.080, 0.315),
        ("UNIVERSITY OF OREGON", 1.987, 0.034, 0.043, 0.089),
    ):
        site.text_strokes(
            parts,
            label,
            lambda u, h: point(u, depth, base + y + h),
            size,
            height,
            PALE,
        )
    map_face(parts, point, base, manifest)
    for e, n in row["bollards_enu_m"]:
        grade = site.ground_height(field, e, n)
        site.cylinder_between(
            parts, (e, n, grade - 0.12), (e, n, grade + 0.82), 0.065, GREEN
        )
        site.cylinder_between(
            parts, (e, n, grade + 0.80), (e, n, grade + 0.86), 0.070, (168, 154, 95)
        )


def plant_gateway(parts, field, row, bed):
    palette = [(107, 132, 77), (132, 150, 89), (94, 123, 72), (118, 139, 81)]
    for axis in row["hedge_centerlines_enu_m"]:
        hedge = LineString(axis)
        for i, distance in enumerate(np.arange(0.12, hedge.length, 0.48)):
            e, n = hedge.interpolate(distance).coords[0]
            assert bed.buffer(0.19).covers(Point(e, n))
            z = site.ground_height(field, e, n)
            spread = 0.45 + 0.031 * (i % 4)
            site.orb(parts, (e, n, z + 0.36), (spread, spread, 0.31), palette[i % 4])
            site.orb(
                parts,
                (e + 0.16, n + 0.09, z + 0.51),
                (0.32, 0.34, 0.24),
                palette[(i + 2) % 4],
            )


def build(spec, stage, audit):
    manifest, field, graph = green.east.pinned_site(site.scene, spec)
    blockers = wayfinding_blockers(site.scene, spec, manifest)
    paths, crossing, bed = footprints(spec, blockers)
    onyx = spec["onyx"]
    entrance, drive, beds, planter = onyx_footprints(onyx, blockers)
    closed = collision_boxes(spec)
    coverage = paths.union(crossing)
    edges, lengths = green.west.check_routes(
        graph,
        spec["routes"],
        coverage,
        blockers.union(unary_union([box(*b) for b in closed])),
    )
    for branch in spec["routes"]:
        route = LineString([branch["anchor_enu_m"], *branch["points_enu_m"]])
        outside = route.difference(coverage.buffer(0.13))
        assert outside.length < 0.01, outside.wkt

    paving, paint, signs, plants = [], [], [], []
    site.drape(paving, field, paths, (173, 168, 153), 0.124, 0.88)
    site.drape(paving, field, entrance.union(drive), (110, 107, 100), 0.105, 0.80)
    site.drape(paving, field, beds, (120, 106, 78), 0.067, 0.72)
    site.drape(paving, field, bed, (129, 116, 86), 0.046, 0.66)
    site.drape(
        paving,
        field,
        Polygon(spec["gateway"]["base_enu_m"]),
        (155, 149, 129),
        0.105,
        0.63,
    )
    gateway = spec["gateway"]
    stripes = unary_union(
        [
            LineString(row).buffer(gateway["crossing_width_m"] / 2, cap_style="flat")
            for row in gateway["crossing_edges_enu_m"]
        ]
    )
    site.drape(paint, field, stripes.difference(blockers), PALE, 0.083, 0.71)
    red_curbs = unary_union(
        [
            LineString(row).buffer(0.088, cap_style="flat", join_style="mitre")
            for row in onyx["curb_paths_enu_m"]
        ]
    ).difference(blockers)
    for curb in site.landscape.geometry.sections(red_curbs):
        mesh = site.landscape.cap(curb, 0.015, 0.205, (154, 65, 55))
        mesh.vertices[:, 1] += [
            site.ground_height(field, e, -z) for e, _, z in mesh.vertices
        ]
        signs.append(mesh)
    base = site.ground_height(field, *onyx["center_enu_m"])
    site.solid(signs, planter, base - 0.20, base + 0.352, (110, 107, 99))
    rim = planter.difference(planter.buffer(-0.17))
    site.solid(signs, rim, base + 0.33, base + 0.43, (128, 123, 111))
    gateway_sign(signs, field, gateway)
    onyx_station(signs, field, onyx, manifest)
    plant_gateway(plants, field, gateway, bed)
    for e, n, spread in (
        (-198.28, 155.40, 0.42),
        (-197.84, 156.53, 0.36),
        (-195.3, 155.72, 0.34),
    ):
        site.orb(plants, (e, n, base + 0.52), (spread, spread, 0.25), (112, 132, 78))
    for index, (e, n, spread) in enumerate(onyx["low_plant_points"]):
        point = Point(e, n)
        assert beds.covers(point) and entrance.distance(point) > 0.34
        z = site.ground_height(field, e, n)
        color = [(106, 127, 73), (89, 114, 68), (119, 134, 84)][index % 3]
        site.orb(
            plants, (e, n, z + spread * 0.48), (spread, spread, spread * 0.55), color
        )
    for index, tree in enumerate(onyx["trees"]):
        point = Point(tree["position_enu_m"])
        assert beds.covers(point) and entrance.distance(point) > tree["trunk_radius_m"]
        site.canopy(plants, field, tree, index)

    stage.mkdir(parents=True, exist_ok=True)
    glb, desc = (stage / name for name in ("site.glb", "site.json"))
    faces = site.export(
        glb,
        (GROUND, paving, "landscape-surface"),
        (MARKINGS, paint, "landscape-surface"),
        (SIGNS, signs, "landscape-detail"),
        (PLANTING, plants, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    pins = spec["pins"]
    site.fairmount.write_json(
        desc,
        {
            "source_presentation_sha256": pins["presentation"],
            "source_base_model_sha256": pins["model"],
            "source_heightfield_sha256": pins["heightfield"],
            "source_navigation_sha256": pins["navigation"],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(glb),
            "buildings": [],
            "walkable_ground": {
                "bounds_enu_m": spec["walkable_bounds"],
                "paths": spec["routes"],
            },
            "closed_site_boxes_enu_m": closed,
        },
        compact=True,
    )
    report = {
        "gateway_pavement_m2": round(paths.area, 2),
        "onyx_apron_m2": round(entrance.area, 2),
        "onyx_drive_m2": round(drive.area, 2),
        "onyx_planting_m2": round(beds.area, 2),
        "onyx_trees": [tree["inventory_id"] for tree in onyx["trees"]],
        "sign_post_spacing_m": round(
            LineString(gateway["post_centers_enu_m"]).length, 3
        ),
        "route_edges": edges,
        "route_lengths_m": lengths,
        "faces": faces,
        "asset_sha256": site.pin(glb),
        "descriptor_sha256": site.pin(desc),
    }
    site.fairmount.write_json(audit, report)
    print(report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(site.root / "data/metadata/northeast-campus-wayfinding.json")
    build(spec, args.stage, args.audit)


if __name__ == "__main__":
    main()
