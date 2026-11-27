# SPDX-License-Identifier: Apache-2.0
"""Build the restored Howe Field walls, fixed gates and plaza landscape."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.affinity import rotate, scale
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

site = import_module("build-pioneer-cemetery-landscape-review")
PACKAGE = "howe-field-gates-review"
GROUND = "howe-field-gates-plaza"
WALL = (156, 158, 148)
CAP = (173, 171, 155)
CONCRETE = (169, 166, 149)
IRON = (55, 67, 61)


def span(a, b, width):
    return LineString([a, b]).buffer(width / 2, cap_style="flat")


def grade(field, area):
    return max(site.ground_height(field, *p) for p in area.exterior.coords)


def wall(parts, field, segment, height, width):
    a, b = np.asarray(segment)
    direction = (b - a) / np.linalg.norm(b - a)
    body = span(a, b, width)
    top = grade(field, body) + height
    site.solid(parts, body, top - height - 0.22, top - 0.14, WALL)
    site.solid(parts, span(a, b, width + 0.13), top - 0.16, top, CAP)
    for start, end in [(a, a + direction * 0.51), (b - direction * 0.51, b)]:
        pilaster = span(start, end, width + 0.36)
        site.solid(parts, pilaster, top - height - 0.23, top - 0.04, WALL)
        site.solid(parts, span(start, end, width + 0.43), top - 0.05, top + 0.075, CAP)
    for x in np.linspace(0.31, 0.82, 3):
        at = a + (b - a) * x
        site.solid(
            parts,
            span(at, at + direction * 0.023, width + 0.011),
            top - height - 0.1,
            top - 0.16,
            (145, 148, 140),
        )
    knots = np.linspace(a, b, 4)
    return [
        span(start, end, width + 0.37).bounds for start, end in zip(knots, knots[1:])
    ]


def ticket_wall(parts, field, start, end, height, width):
    delta = np.subtract(end, start)
    length = np.linalg.norm(delta)
    axis = delta / length
    west = np.array([axis[1], -axis[0]])
    assert west[0] < 0
    center = length * 0.48
    grade_z = grade(field, span(start, end, width))
    top = grade_z + height

    def segment(a, b, thickness=width):
        return span(start + axis * a, start + axis * b, thickness)

    aperture = 0.42
    for a, b in [(0, center - aperture / 2), (center + aperture / 2, length)]:
        site.solid(parts, segment(a, b), grade_z - 0.21, top - 0.13, WALL)
    opening = segment(center - aperture / 2, center + aperture / 2)
    site.solid(parts, opening, grade_z - 0.21, grade_z + 0.99, WALL)
    site.solid(parts, opening, grade_z + 1.41, top - 0.13, WALL)
    site.solid(parts, segment(0, length, width + 0.15), top - 0.13, top, CAP)
    shelf = segment(center - 0.36, center + 0.36, width + 0.20)
    site.solid(parts, shelf, grade_z + 0.93, grade_z + 1.00, CAP)
    mid = start + axis * center
    for side in (-1, 1):
        grille = mid + west * side * (width / 2 - 0.045)
        for u in (-0.14, 0, 0.14):
            x, y = grille + axis * u
            site.beam(
                parts, (x, y, grade_z + 1.01), (x, y, grade_z + 1.40), 0.024, IRON
            )
        for z in (1.075, 1.315):
            a, b = grille - axis * 0.20, grille + axis * 0.20
            site.beam(parts, (*a, grade_z + z), (*b, grade_z + z), 0.021, IRON)
    plaque = [
        start + axis * t + west * side
        for t, side in [
            (length - 0.74, width / 2),
            (length - 0.19, width / 2),
            (length - 0.19, width / 2 + 0.035),
            (length - 0.74, width / 2 + 0.035),
        ]
    ]
    site.solid(parts, Polygon(plaque), grade_z + 0.89, grade_z + 1.29, (100, 88, 63))
    knots = np.linspace(0, length, 4)
    return [segment(a, b).bounds for a, b in zip(knots, knots[1:])]


def fixed_gate(parts, field, start, end, length, height):
    a, b = np.asarray(start), np.asarray(end)
    base = site.ground_height(field, *a) + 0.07

    def at(x, z):
        p = a + (b - a) * x / length
        return (*p, base + z)

    for z in (0.07, 0.56, 1.71, height):
        site.beam(parts, at(0, z), at(length, z), 0.041, IRON)
    for x in np.linspace(0, length, 15):
        site.beam(
            parts, at(x, 0.07), at(x, height), 0.023 if 0 < x < length else 0.060, IRON
        )
    for x in np.linspace(0.11, length - 0.11, 6):
        for z in (0.34, 1.87):
            points = [
                at(x + 0.071 * np.sin(t), z + 0.094 * np.cos(t))
                for t in np.linspace(0, 2 * np.pi, 9)
            ]
            for p, q in zip(points, points[1:]):
                site.beam(parts, p, q, 0.018, IRON)
    return span(a, b, 0.075).bounds


def rain_garden(details, plants, field, spec):
    e, n = spec["center_enu_m"]
    rx, ry = spec["radii_m"]
    circle = Point(e, n).buffer(1, quad_segs=18)
    outline = rotate(
        scale(circle, rx, ry, origin=(e, n)), spec["rotation_degrees"], origin=(e, n)
    )
    inside = outline.buffer(-0.17)
    z = grade(field, outline)
    site.solid(details, outline.difference(inside), z - 0.26, z + 0.265, CONCRETE)
    site.solid(details, inside, z - 0.19, z + 0.120, (113, 104, 78))
    for i in range(37):
        a = i * 2.399963
        rad = np.sqrt((i + 0.8) / 37)
        e1 = e + 2.9 * np.cos(a) * rad
        n1 = n + 1.65 * np.sin(a) * rad
        p = rotate(Point(e1, n1), spec["rotation_degrees"], origin=(e, n))
        if inside.contains(p):
            for k in (-1, 0, 1):
                site.beam(
                    plants,
                    (*p.coords[0], z + 0.12),
                    (p.x + k * 0.15, p.y + k * 0.055, z + 0.37 + 0.04 * (i % 4)),
                    0.018,
                    (94 + 9 * (i % 3), 111 + 11 * (i % 3), 64),
                )
    return outline


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    spec = site.read(site.root / f"data/metadata/{PACKAGE}.json")
    scene = site.scene
    manifest = site.read(scene / "manifest.json")
    config = site.read(scene / "presentation.json")
    field_path = scene / manifest["heightfield_url"]
    field = site.read(field_path)
    nav = scene / "navigation.json"
    route = dict(spec["route"])
    nodes = site.read(nav)["nodes_enu_m"]
    assert route["anchor_enu_m"] in nodes
    ground, details, plants = [], [], []
    height, thickness = spec["wall_height_m"], spec["wall_thickness_m"]
    boxes = []
    for segment in spec["wall_segments_enu_m"]:
        boxes.extend(wall(details, field, segment, height, thickness))
    north, south = spec["ticket_booth_enu_m"]
    boxes.extend(
        ticket_wall(details, field, north, south, height, spec["ticket_booth_width_m"])
    )
    size = spec["side_gate_length_m"]
    for (e, n), direction in [(north, -1), (south, 1)]:
        hinge = np.array([e + 0.33, n + 0.05 * direction])
        tip = hinge + size * np.array([0.66, direction * np.sqrt(1 - 0.66**2)])
        boxes.append(
            fixed_gate(
                details,
                field,
                hinge,
                tip,
                size,
                spec["side_gate_height_m"],
            )
        )
    garden = rain_garden(details, plants, field, spec["filtration_planter"])
    boxes.append(garden.bounds)
    walks = [
        LineString(row["centerline"]).buffer(row["width"] / 2, cap_style="flat")
        for row in spec["diagonal_walks"]
    ]
    plaza = Polygon(spec["pavement_enu_m"])
    apron = Polygon(spec["parking_apron_enu_m"])
    planted = [Point(p).buffer(0.71) for p in spec["bed_centers_enu_m"]]
    blockers = unary_union([box(*bounds) for bounds in boxes])
    paving = unary_union([plaza, *walks]).difference(garden)
    asphalt = apron.difference(paving)
    site.drape(ground, field, paving, CONCRETE, 0.099, 0.85)
    site.drape(ground, field, asphalt, (116, 116, 105), 0.095, 0.85)
    for a, b in spec["access_aisle_hatches_enu_m"]:
        site.drape(
            details,
            field,
            span(a, b, 0.106).intersection(asphalt),
            (203, 202, 185),
            0.11,
            0.80,
        )
    hardscape = paving.union(asphalt)
    for i, bed in enumerate(planted):
        if paving.intersects(bed):
            bed = bed.difference(paving.buffer(0.08))
        site.drape(details, field, bed, (110, 92, 68), 0.059, 0.65)
        for angle in np.linspace(0, 2 * np.pi, 5, endpoint=False):
            e, n = np.subtract(
                spec["bed_centers_enu_m"][i],
                [0.32 * np.cos(angle), 0.32 * np.sin(angle)],
            )
            if bed.contains(Point(e, n)) and not blockers.contains(Point(e, n)):
                z = site.ground_height(field, e, n)
                site.orb(
                    plants,
                    (e, n, z + 0.27),
                    (0.31, 0.30, 0.38),
                    (79 + i * 4, 108 + i * 3, 63),
                    subdivisions=1,
                )
    line = LineString([route["anchor_enu_m"], *route["points_enu_m"]])
    assert line.distance(blockers) >= 0.50
    assert line.difference(paving).length < 10.5
    assert (
        max(
            np.linalg.norm(np.subtract(a, b))
            for a, b in zip(line.coords, list(line.coords)[1:])
        )
        < 20
    )
    near_buildings = [
        Polygon(b["footprint_enu_m"]).buffer(0) for b in manifest["buildings"]
    ]
    assert all(
        line.distance(b) > 0.65 and hardscape.intersection(b).area < 0.03
        for b in near_buildings
    )
    route["bounds_enu_m"] = [hardscape.bounds]
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        ("howe-field-gates-detail", details, "landscape-detail"),
        ("howe-field-gates-planting", plants, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    payload = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": site.pin(field_path),
        "source_navigation_sha256": site.pin(nav),
        "url": f"{PACKAGE}/site.glb",
        "sha256": site.pin(glb),
        "ground_node": GROUND,
        "buildings": [],
        "walkable_ground": route,
        "closed_site_boxes_enu_m": boxes,
    }
    descriptor = args.stage / "site.json"
    site.fairmount.write_json(descriptor, payload, compact=True)
    audit = dict(
        faces=faces,
        paving_m2=round(paving.area, 2),
        asphalt_m2=round(asphalt.area, 2),
        planted_pockets=len(planted),
        rain_garden_m2=round(garden.area, 2),
        route_m=round(line.length, 2),
        route_edges=len(route["points_enu_m"]),
        fixed_iron_leaves=2,
        asset_sha256=payload["sha256"],
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
