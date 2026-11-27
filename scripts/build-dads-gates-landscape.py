# SPDX-License-Identifier: Apache-2.0
"""Reconstruct the Dads' Gates landscape from the historic plan and modern imagery."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
import trimesh

site = import_module("build-pioneer-cemetery-landscape-review")
southern_axis = import_module("build-normal-gate-axis")
PACKAGE = "dads-gates-landscape-review"
SURFACE = "dads-gates-approach"
IRON = (57, 74, 63)
IRON_EDGE = (83, 94, 75)
BRONZE = (132, 102, 66)
CONCRETE = (176, 173, 158)
ASPHALT = (119, 122, 113)
CURB = (166, 103, 85)
SOIL = (105, 81, 62)


def iron_curve(parts, points, normal, width, color):
    points = np.asarray(points)
    normal = np.array((*normal, 0.0))
    sides = np.cross(np.gradient(points, axis=0), normal)
    sides /= np.linalg.norm(sides, axis=1)[:, None]
    angles = np.arange(3) * (2 * np.pi / 3)
    ring = (
        sides[:, None, :] * np.cos(angles)[None, :, None]
        + normal * np.sin(angles)[None, :, None]
    )
    vertices = (points[:, None, :] + ring * (width / 2)).reshape((-1, 3))
    faces = []
    for i in range(len(points) - 1):
        for j in range(3):
            a, b = i * 3 + j, i * 3 + (j + 1) % 3
            faces.extend(((a, a + 3, b), (b, a + 3, b + 3)))
    mesh = trimesh.Trimesh(
        vertices=vertices[:, [0, 2, 1]] * [1, 1, -1], faces=faces, process=False
    )
    mesh.visual.vertex_colors = [*color, 255]
    parts.append(mesh)


def panel(parts, field, start, end, height, leaf=False, medallion=False):
    a, b = np.asarray(start), np.asarray(end)
    delta = b - a
    length = np.linalg.norm(delta)
    normal = np.array((delta[1], -delta[0])) / length
    ga, gb = site.ground_height(field, *a), site.ground_height(field, *b)

    def point(u, z):
        t = u / length
        return (*(a + delta * t), ga + (gb - ga) * t + z)

    uprights = max(1, round(length / 0.21))
    for i in range(uprights + 1):
        u = i * length / uprights
        thickness = 0.050 if i in (0, uprights) else 0.024
        site.beam(parts, point(u, 0.12), point(u, height - 0.025), thickness, IRON)
        if i not in (0, uprights):
            site.beam(
                parts,
                point(u, height - 0.11),
                point(u, height + 0.015),
                0.030,
                IRON_EDGE,
            )
    for h in (0.15, 0.43, height * 0.42, height * 0.73, height - 0.015):
        site.beam(parts, point(0, h), point(length, h), 0.045, IRON)

    # Short mirrored spirals retain the open pattern of the original ironwork.
    units = max(1, round(length / (0.37 if leaf else 0.62)))
    gap = length / units
    bands = (0.34, 0.60, 0.86) if leaf else (0.58, 0.86)
    for fraction in bands:
        z = height * fraction
        site.beam(parts, point(0, z), point(length, z), 0.011, IRON)
    for i in range(units):
        for frac in bands:
            for direction in (-1, 1):
                center = (i + 0.5) * gap + direction * gap * 0.13
                path = [
                    point(
                        center + direction * gap * 0.29 * t * np.cos(1.8 * np.pi * t),
                        height * frac + 0.098 * t * np.sin(1.8 * np.pi * t),
                    )
                    for t in np.linspace(0.16, 1, 8)
                ]
                iron_curve(parts, path, normal, 0.014, IRON_EDGE)

    if medallion:
        u, z = length * 0.49, height * 0.59
        x, y, height_at = point(u, z)
        site.cylinder_between(
            parts,
            (x - normal[0] * 0.022, y - normal[1] * 0.022, height_at),
            (x + normal[0] * 0.022, y + normal[1] * 0.022, height_at),
            0.29,
            BRONZE,
            sides=32,
        )
        for radius in (0.231, 0.285):
            for side in (-0.032, 0.032):
                rim = [
                    (x + normal[0] * side, y + normal[1] * side, h)
                    for x, y, h in (
                        point(u + radius * np.cos(t), z + radius * np.sin(t))
                        for t in np.linspace(0, 2 * np.pi, 25)
                    )
                ]
                iron_curve(parts, rim, normal, 0.014, (173, 137, 87))


def pylon(parts, field, center, main=False):
    e, n = center
    base = site.ground_height(field, e, n)
    half = 0.218 if main else 0.137
    high = base + (2.44 if main else 1.98)
    foot = box(e - half - 0.07, n - half - 0.07, e + half + 0.07, n + half + 0.07)
    site.solid(parts, foot, base - 0.13, base + 0.092, CONCRETE)
    corners = [
        (e - half, n - half),
        (e + half, n - half),
        (e + half, n + half),
        (e - half, n + half),
    ]
    for x, y in corners:
        site.beam(parts, (x, y, base + 0.08), (x, y, high), 0.043, IRON)
    for a, b in zip(corners, corners[1:] + corners[:1]):
        for z in np.linspace(base + 0.22, high - 0.045, 7):
            site.beam(parts, (*a, z), (*b, z), 0.025, IRON_EDGE)
        for z in np.linspace(base + 0.30, high - 0.36, 6):
            site.beam(parts, (*a, z), (*b, z + 0.20), 0.014, IRON)
            site.beam(parts, (*b, z), (*a, z + 0.20), 0.014, IRON)
    if main:
        site.flat_box(parts, e, n, 0.435, 0.435, high - 0.015, high + 0.072, IRON)
        site.flat_box(
            parts, e, n, 0.278, 0.278, high + 0.061, high + 0.665, (191, 195, 163)
        )
        for x, y in corners:
            dx, dy = (x - e) * 0.75, (y - n) * 0.75
            site.beam(
                parts,
                (e + dx, n + dy, high + 0.04),
                (e + dx, n + dy, high + 0.70),
                0.026,
                IRON,
            )
        site.flat_box(parts, e, n, 0.409, 0.409, high + 0.655, high + 0.748, IRON)
        site.solid(
            parts,
            Point(e, n).buffer(0.155, quad_segs=4),
            high + 0.73,
            high + 0.774,
            IRON_EDGE,
        )
    else:
        site.flat_box(parts, e, n, 0.35, 0.35, high - 0.030, high + 0.060, IRON)


def pedestrian_header(parts, field, hinges):
    (left, n), (right, _) = hinges
    mid = (left + right) / 2
    base = site.ground_height(field, mid, n)
    for height in (2.10, 2.32):
        site.beam(
            parts, (left, n, base + height), (right, n, base + height), 0.032, IRON
        )
    lowest = base + 2.144
    site.text_strokes(
        parts,
        "OREGON DADS 1940",
        lambda x, z: (mid - x, n + 0.015, lowest + z),
        0.084,
        0.115,
        IRON_EDGE,
    )


def gatework(parts, field, spec):
    collisions = []
    pedestrian_hinges = spec["pedestrian_hinges_enu_m"]
    hinges_at = {tuple(point) for pair in pedestrian_hinges for point in pair}
    for run, cuts in zip(
        spec["fence_runs_enu_m"], spec["fence_collision_breaks"], strict=True
    ):
        for a, b in zip(run, run[1:]):
            panel(parts, field, a, b, 1.88)
        for a, b in zip(cuts, cuts[1:]):
            collisions.append(LineString(run[a : b + 1]).buffer(0.235).bounds)
        for at in run[1:-1:2] + [run[-1]]:
            if tuple(at) not in hinges_at:
                pylon(parts, field, at)

    for i, hinge in enumerate(spec["main_hinges_enu_m"]):
        pylon(parts, field, hinge, main=True)
        e, n = hinge
        tip = [e + (-0.066 if i == 0 else 0.066), n - 3.047]
        panel(parts, field, hinge, tip, 2.44, leaf=True, medallion=True)
        collisions.append(LineString([hinge, tip]).buffer(0.096).bounds)
    for hinges in pedestrian_hinges:
        pedestrian_header(parts, field, hinges)
        for i, hinge in enumerate(hinges):
            pylon(parts, field, hinge)
            e, n = hinge
            tip = [e + (0.09 if i == 0 else -0.09), n - 1.063]
            panel(parts, field, hinge, tip, 1.82, leaf=True)
            collisions.append(LineString([hinge, tip]).buffer(0.089).bounds)
    return collisions


def beech(parts, field, info, index):
    e, n = info["position_enu_m"]
    high = info["height_m"]
    radius = info["crown_radius_m"]
    z = site.ground_height(field, e, n)
    bark = (90, 82, 74)
    leaves = ((76, 65, 54), (90, 83, 59), (72, 84, 61), (86, 87, 62))
    site.cylinder_between(
        parts, (e, n, z - 0.10), (e, n, z + high * 0.78), 0.35, bark, sides=9
    )
    for i, fraction in enumerate((0.61, 0.66, 0.69, 0.75, 0.80, 0.91)):
        angle = i * 2.39996 + index * 0.87
        reach = radius * (0.48 if i < 5 else 0.11)
        center = (
            e + reach * np.cos(angle),
            n + reach * np.sin(angle),
            z + fraction * high,
        )
        site.cylinder_between(
            parts, (e, n, z + high * 0.36), center, 0.10, bark, sides=6
        )
        site.orb(
            parts,
            center,
            (radius * 0.61, radius * 0.61, high * 0.18),
            leaves[i % 4],
            subdivisions=2,
        )


def landscape(ground, details, plants, field, spec, buildings):
    island = Polygon(spec["traffic_island_enu_m"])
    crossing_east = spec["crossing_center_east_m"]
    crossing_south, crossing_north = spec["crossing_endpoints_north_m"]
    crossing = box(
        crossing_east - 1.65,
        crossing_south - 0.39,
        crossing_east + 1.65,
        crossing_north + 0.27,
    )
    sidewalks = unary_union(
        [
            LineString(row["points_enu_m"]).buffer(row["width_m"] / 2, cap_style="flat")
            for row in spec["walks"]
        ]
        + [Polygon(spec["approach_enu_m"])]
    ).difference(buildings)
    drive = unary_union(
        [Polygon(spec[key]) for key in ("pullout_enu_m", "service_drive_enu_m")]
        + [crossing]
    ).difference(unary_union([island, sidewalks, buildings]))
    site.drape(ground, field, drive, ASPHALT, 0.094, 0.90)
    site.drape(ground, field, sidewalks, CONCRETE, 0.097, 0.80)
    for x in (crossing_east - 1.47, crossing_east + 1.47):
        stripe = box(x - 0.10, crossing_south + 0.19, x + 0.10, crossing_north - 0.56)
        site.drape(
            details, field, stripe.intersection(drive), (219, 216, 195), 0.110, 0.82
        )
    curb_lines = [LineString(row) for row in spec["curb_lines_enu_m"]]
    curb_lines.append(island.exterior)
    curbs = unary_union([line.buffer(0.09, join_style="round") for line in curb_lines])
    site.drape(details, field, curbs, CURB, 0.147, 0.77)
    for i, outline in enumerate(spec["beds_enu_m"]):
        bed = Polygon(outline).difference(drive.union(sidewalks).buffer(0.11))
        site.drape(details, field, bed, SOIL, 0.070, 0.69)
        x0, y0, x1, y1 = bed.bounds
        for x in np.arange(x0 + 0.34, x1, 0.94):
            for y in np.arange(y0 + 0.37, y1, 0.85):
                if bed.contains(Point(x, y)):
                    z = site.ground_height(field, x, y)
                    tone = (71 + i * 3, 95 + i * 3, 62 + i)
                    site.orb(plants, (x, y, z + 0.18), (0.37, 0.31, 0.25), tone)
    for i, tree in enumerate(spec["trees"]):
        assert Point(tree["position_enu_m"]).distance(drive.union(sidewalks)) > 0.56
        if tree["form"] == "beech":
            beech(plants, field, tree, i)
        else:
            site.canopy(plants, field, tree, i)
    return drive, sidewalks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    scene = site.scene
    spec = site.read(site.root / "data/metadata/dads-gates-landscape.json")
    southern = site.read(site.root / "data/metadata/normal-gate-axis.json")
    manifest = site.read(scene / "manifest.json")
    config = site.read(scene / "presentation.json")
    field_path = scene / manifest["heightfield_url"]
    nav_path = scene / "navigation.json"
    field = site.read(field_path)
    graph = site.read(nav_path)
    neighbor = scene / "heritage-miller-review/site.json"
    assert site.pin(neighbor) == spec["neighbor_descriptor_sha256"]
    lillis = scene / "lillis-complex-review/site.json"
    assert site.pin(lillis) == southern["lillis_descriptor_sha256"]
    new = [*site.read(neighbor)["buildings"], *site.read(lillis)["buildings"]]
    building_shapes = unary_union(
        [
            Polygon(outline).buffer(0)
            for b in [*manifest["buildings"], *new]
            for outline in [b["footprint_enu_m"], *b.get("support_collision_enu_m", [])]
        ]
    )
    ground, details, plants = [], [], []
    normal_gate = []
    collision = gatework(details, field, spec)
    arbor = southern_axis.arbor(normal_gate, field, southern["arbor"])
    collision.append(arbor.buffer(0.09).bounds)
    assert len(collision) <= 16
    drive, sidewalks = landscape(ground, details, plants, field, spec, building_shapes)
    northern_ground = drive.union(sidewalks)
    south_drive, south_walks = southern_axis.landscape(
        ground, details, plants, field, southern, building_shapes, northern_ground
    )
    hardscape = unary_union([northern_ground, south_drive, south_walks])
    assert not arbor.buffer(0.20).intersects(hardscape)
    assert hardscape.intersection(building_shapes).area < 0.02
    obstacles = unary_union([box(*bounds) for bounds in collision]).union(
        building_shapes
    )
    available = set(map(tuple, graph["nodes_enu_m"]))
    route_lengths, edge_count = [], 0
    routes = [*spec["routes"], *southern["routes"]]
    assert len(routes) <= 8
    for path in routes:
        assert tuple(path["anchor_enu_m"]) in available
        end = [path["end_enu_m"]] if "end_enu_m" in path else []
        assert all(tuple(point) in available for point in end)
        points = [path["anchor_enu_m"], *path["points_enu_m"], *end]
        line = LineString(points)
        assert line.distance(obstacles) > 0.47, (points, line.distance(obstacles))
        assert line.difference(hardscape.buffer(0.10)).length < 0.80, points
        spans = np.linalg.norm(np.diff(points, axis=0), axis=1)
        assert all(0.05 < span < 20 for span in spans)
        available.update(map(tuple, path["points_enu_m"]))
        route_lengths.append(round(line.length, 2))
        edge_count += len(points) - 1
    assert all(
        sidewalks.covers(Point(row["position_enu_m"])) for row in spec["context_trees"]
    )
    source_trees = site.read(site.root / "data/metadata/context-trees-l2.json")["trees"]
    tree_id = southern["context_tree_index"]
    retired = next(row for row in source_trees if row["index"] == tree_id)
    e, _, z = retired["origin_gltf_m"]
    assert south_drive.covers(Point(e, -z))
    context_trees = [
        *spec["context_trees"],
        {"index": tree_id, "position_enu_m": [e, -z]},
    ]
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (SURFACE, ground, "landscape-surface"),
        ("dads-gates-ironwork", details, "landscape-detail"),
        ("dads-gates-planting", plants, "landscape-vegetation"),
        ("normal-gate-arbor", normal_gate, "landscape-detail"),
        surface_layer=SURFACE,
    )
    payload = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": site.pin(field_path),
        "source_navigation_sha256": site.pin(nav_path),
        "ground_node": SURFACE,
        "url": f"{PACKAGE}/site.glb",
        "sha256": site.pin(glb),
        "buildings": [],
        "walkable_ground": {
            "bounds_enu_m": [
                hardscape.intersection(box(-600, 158.1, -450, 250)).bounds,
                hardscape.intersection(box(-600, 80, -450, 162)).bounds,
            ],
            "paths": routes,
        },
        "closed_site_boxes_enu_m": collision,
        "context_trees": context_trees,
    }
    descriptor = args.stage / "site.json"
    site.fairmount.write_json(descriptor, payload, compact=True)
    audit = dict(
        asphalt_m2=round(drive.area, 2),
        concrete_m2=round(sidewalks.area, 2),
        route_lengths_m=route_lengths,
        route_edges=edge_count,
        southern_asphalt_m2=round(south_drive.area, 2),
        southern_concrete_m2=round(south_walks.area, 2),
        southern_route_edges=edge_count
        - sum(len(path["points_enu_m"]) for path in spec["routes"]),
        faces=faces,
        asset_sha256=payload["sha256"],
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
