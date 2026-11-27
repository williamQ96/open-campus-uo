# SPDX-License-Identifier: Apache-2.0
"""Build the Women's Memorial, Gerlinger Entrance and Straub Hall greens."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

site = import_module("build-pioneer-cemetery-landscape-review")
PACKAGE = "central-campus-greens-review"
GROUND = "central-campus-greens-surface"
DETAIL = "central-campus-greens-detail"
PLANTS = "central-campus-greens-planting"
ART = "straub-art-installation"
WALK = (175, 171, 151)
DRIVE = (125, 124, 109)
STONE = (164, 157, 137)
BRICK = (111, 72, 58)
IRON = (60, 66, 58)
# The older landscape lawn is 0.07 m above terrain.
PAVING_LIFT = 0.166
LAWN_LIFT = 0.152


def drape(parts, field, shape, color, lift, cell=1.4):
    if not shape.is_empty and shape.area > 0.00001:
        site.drape(parts, field, shape, color, lift, cell)


def terrain_cap(parts, field, shape, bottom, top, color):
    for piece in site.geometry.sections(shape):
        cap = site.landscape.cap(piece, bottom, top, color)
        cap.vertices[:, 1] += [
            site.ground_height(field, east, -south) for east, _, south in cap.vertices
        ]
        parts.append(cap)


def walk_outline(row):
    return LineString(row["centerline_enu_m"]).buffer(
        row["width_m"] / 2, cap_style="round", join_style="round"
    )


def paved_zone(ground, planting, field, key, zone, footprint):
    walks = unary_union([walk_outline(row) for row in zone["walks"]])
    lawn = unary_union([Polygon(shape).buffer(0) for shape in zone["lawns"]])
    drives = unary_union([Polygon(shape) for shape in zone.get("drives", [])])
    drives = drives.difference(lawn.union(walks).union(footprint))
    walks = walks.difference(footprint)
    lawn_zone = lawn.difference(walks.union(footprint).buffer(0.025))
    reserved = unary_union(
        [Point(tree["position_enu_m"]).buffer(0.45) for tree in zone["trees"]]
    )
    if key == "straub":
        reserved = reserved.union(Polygon(zone["bike_rack_pad"])).union(
            Polygon(zone["art_installation"]["platform_enu_m"])
        )
    turf_shades = {
        "womens": (121, 137, 88),
        "gerlinger": (117, 139, 87),
        "straub": (118, 136, 87),
    }
    occupied = []
    for stair in zone.get("stairs", []):
        x, n = stair["e"], stair["n"]
        w, run = stair["width"] / 2, stair["run"] / 2
        occupied.append(box(x - w, n - run, x + w, n + run))
    under_steps = unary_union(occupied)
    drape(ground, field, walks.difference(under_steps), WALK, PAVING_LIFT)
    drape(ground, field, drives, DRIVE, PAVING_LIFT, 1.6)
    beds = unary_union([Polygon(shape).buffer(0) for shape in zone["beds"]])
    beds = beds.difference(walks.union(footprint).buffer(0.11))
    drape(
        ground,
        field,
        lawn_zone.difference(beds.union(reserved)),
        turf_shades[key],
        LAWN_LIFT,
        1.55,
    )
    drape(ground, field, beds, (111, 101, 79), LAWN_LIFT + 0.004)
    for i, tree in enumerate(zone["trees"]):
        site.canopy(planting, field, tree, i)
    for i, bed in enumerate(site.geometry.sections(beds)):
        west, south, east, north = bed.bounds
        rng = np.random.default_rng(214 + i)
        inner = bed.buffer(-0.22)
        for x, n in rng.uniform([west, south], [east, north], (int(bed.area * 1.6), 2)):
            if not inner.contains(Point(x, n)):
                continue
            base = site.ground_height(field, x, n) + LAWN_LIFT
            width = rng.uniform(0.15, 0.41)
            tone = int(rng.integers(-8, 13))
            site.orb(
                planting,
                (x, n, base + width * 0.4),
                (width, width * 0.73, width * 0.57),
                (86 + tone, 107 + tone, 67 + tone),
                subdivisions=0,
            )
    return walks.union(drives), lawn_zone.area, beds.area


def bench(parts, field, row):
    center = np.asarray([row["e"], row["n"]])
    angle = np.deg2rad(row["bearing"])
    direction = np.array([np.sin(angle), np.cos(angle)])
    length = row["len"]
    line = LineString(
        [center - direction * length / 2, center + direction * length / 2]
    )
    base = site.ground_height(field, *center) + LAWN_LIFT
    for part in range(3):
        a = line.interpolate(part / 3, normalized=True).coords[0]
        b = line.interpolate((part + 1) / 3 - 0.014, normalized=True).coords[0]
        site.solid(
            parts, site.landscape.rect_on(a, b, 0.41), base + 0.39, base + 0.53, STONE
        )
    for offset in (-0.36, 0, 0.36):
        stem = center + offset * length * direction
        region = site.landscape.rect_on(
            stem - direction * 0.075, stem + direction * 0.075, 0.287
        )
        site.solid(parts, region, base - 0.10, base + 0.42, (137, 132, 119))
    return list(line.buffer(0.205, cap_style="flat").bounds)


def memorial_wall(parts, field, chains):
    collision = []
    for chain in chains:
        line = LineString(chain)
        collision.append(list(line.buffer(0.16, cap_style="flat").bounds))
        terrain_cap(
            parts, field, line.buffer(0.17, join_style="mitre"), -0.21, 0.51, BRICK
        )
        terrain_cap(
            parts, field, line.buffer(0.207, join_style="mitre"), 0.49, 0.58, STONE
        )
        if len(chain) > 4:
            terrain_cap(parts, field, line.buffer(0.157), 0.56, 0.80, BRICK)
            terrain_cap(parts, field, line.buffer(0.193), 0.78, 0.872, STONE)
        else:
            for d in np.arange(0.35, line.length - 0.23, 0.36):
                e, n = line.interpolate(d).coords[0]
                z = site.ground_height(field, e, n)
                site.flat_box(parts, e, n, 0.11, 0.131, z + 0.56, z + 0.87, STONE)
            terrain_cap(parts, field, line.buffer(0.144), 0.85, 0.937, STONE)
        for end in (chain[0], chain[-1]):
            e, n = end
            z = site.ground_height(field, e, n)
            site.flat_box(parts, e, n, 0.44, 0.46, z - 0.23, z + 0.94, BRICK)
            site.flat_box(parts, e, n, 0.525, 0.542, z + 0.93, z + 1.042, STONE)
            site.orb(parts, (e, n, z + 1.09), (0.073, 0.073, 0.08), STONE)
    return collision


def stair_steps(ground, details, field, row):
    e, n = row["e"], row["n"]
    left, right = e - row["width"] / 2, e + row["width"] / 2
    north, south = n + row["run"] / 2, n - row["run"] / 2
    base = site.ground_height(field, e, north) + PAVING_LIFT
    top = max(base + 0.29, site.ground_height(field, e, south) + PAVING_LIFT)
    count = row["treads"]
    for i in range(count):
        edge = north - row["run"] * i / count
        step = base + (i + 1) * (top - base) / count
        site.solid(
            ground,
            box(left, edge - row["run"] / count, right, edge),
            base - 0.30,
            step,
            STONE,
        )
        site.solid(
            details,
            box(left, edge - 0.019, right, edge + 0.001),
            step - 0.018,
            step + 0.003,
            (136, 133, 116),
        )


def entrance_detail(ground, details, field, zone, paths):
    border = Polygon(zone["lawns"][0]).boundary
    gaps = unary_union([walk_outline(row) for row in zone["walks"]])
    curb = border.buffer(0.074).difference(gaps.buffer(0.09))
    terrain_cap(
        details, field, curb, PAVING_LIFT - 0.04, PAVING_LIFT + 0.11, (151, 108, 78)
    )
    for a, b in zone["parking_marks"]:
        line = site.landscape.rect_on(a, b, 0.083)
        drape(
            ground, field, paths.intersection(line), (162, 143, 79), PAVING_LIFT + 0.009
        )
    points = []
    for e, n in zone["bollards"]:
        base = site.ground_height(field, e, n) + PAVING_LIFT
        site.cylinder_between(
            details, (e, n, base - 0.06), (e, n, base + 0.57), 0.036, IRON, sides=9
        )
        points.append((e, n, base + 0.46))
    for a, b in zip(points, points[1:]):
        mid = (np.array(a) + b) / 2
        mid[2] -= 0.13
        site.cylinder_between(details, a, mid, 0.013, IRON, sides=5)
        site.cylinder_between(details, mid, b, 0.013, IRON, sides=5)


def lettering(parts, title, point, size):
    e, n, z = point
    for j, letter in enumerate(title):
        if letter == " ":
            continue
        lines = (
            (((0.52, 1.03), (0.39, 0.78)),) if letter == "’" else site.GLYPHS[letter]
        )
        for line in lines:
            points = [
                (e, n + size * 0.48 * len(title) - size * (j + 0.68 * u), z + size * v)
                for u, v in line
            ]
            for a, b in zip(points, points[1:]):
                site.cylinder_between(
                    parts, a, b, size * 0.087, (221, 220, 191), sides=6
                )


def straub_detail(ground, details, art, field, zone):
    platform = Polygon(zone["art_installation"]["platform_enu_m"])
    pad = Polygon(zone["bike_rack_pad"])
    terrain_cap(art, field, platform, -0.07, 0.219, (160, 156, 139))
    drape(ground, field, pad, (150, 150, 136), PAVING_LIFT)
    for e, n in zone["bicycle_hoops"]:
        z = site.ground_height(field, e, n) + PAVING_LIFT - 0.025
        posts = [
            (e - 0.14, n - 0.31, z),
            (e - 0.14, n - 0.31, z + 0.62),
            (e + 0.14, n + 0.31, z + 0.62),
            (e + 0.14, n + 0.31, z),
        ]
        for a, b in zip(posts, posts[1:]):
            site.cylinder_between(details, a, b, 0.030, IRON, sides=8)
    e, n = zone["west_sign"]
    z = site.ground_height(field, e, n)
    site.flat_box(details, e, n, 0.085, 1.27, z + 0.18, z + 0.64, (37, 68, 49))
    for offset in (-0.49, 0.49):
        site.flat_box(
            details, e, n + offset, 0.105, 0.061, z - 0.06, z + 0.60, (46, 57, 45)
        )
    lettering(details, "STRAUB HALL", (e - 0.046, n, z + 0.363), 0.089)
    p = platform.exterior.interpolate(0.16, normalized=True)
    z = site.ground_height(field, p.x, p.y)
    site.flat_box(art, p.x, p.y, 0.071, 0.071, z + 0.18, z + 0.53, IRON)
    site.flat_box(art, p.x, p.y, 0.045, 0.76, z + 0.43, z + 0.65, (89, 93, 83))
    lettering(art, "AKBAR’S GARDEN", (p.x - 0.028, p.y, z + 0.523), 0.048)
    e, n = zone["stafford_plaque"]
    z = site.ground_height(field, e, n)
    site.flat_box(details, e, n, 0.36, 0.23, z - 0.05, z + 0.13, (143, 135, 111))
    site.flat_box(details, e, n, 0.31, 0.19, z + 0.13, z + 0.154, (98, 107, 91))
    return bench(details, field, zone["historic_bench"]), platform.area


def count_paths(graph, spec, surfaces, obstacles):
    nodes = {tuple(value) for value in graph["nodes_enu_m"]}
    edges = 0
    distances = {}
    for route in spec["paths"]:
        anchor = tuple(route["anchor_enu_m"])
        points = [tuple(p) for p in route["points_enu_m"]]
        assert anchor in nodes and not any(p in nodes for p in points), route["name"]
        end = route.get("end_enu_m")
        if end:
            assert tuple(end) in nodes
        planned = [anchor, *points, *([tuple(end)] if end else [])]
        edge_lengths = np.linalg.norm(np.diff(planned, axis=0), axis=1)
        assert ((edge_lengths >= 0.05) & (edge_lengths <= 20)).all()
        chain = LineString(planned)
        centerline = LineString(points)
        assert centerline.difference(surfaces.buffer(0.38)).length < 2.1, (
            route["name"],
            centerline.difference(surfaces.buffer(0.38)).length,
        )
        assert chain.intersection(obstacles).length < 0.15, route["name"]
        nodes.update(points)
        edges += len(edge_lengths)
        distances[route["name"]] = round(chain.length, 2)
    return edges, distances


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    scene = site.scene
    spec = site.read(site.root / f"data/metadata/{PACKAGE}.json")
    cfg = site.read(scene / "presentation.json")
    manifest = site.read(scene / "manifest.json")
    field_path = scene / manifest["heightfield_url"]
    nav = scene / "navigation.json"
    pins = spec["pinned_sources"]
    assert (
        pins["campus"],
        pins["presentation"],
        pins["heightfield"],
        pins["navigation"],
    ) == (
        manifest["model"]["sha256"],
        cfg["asset_sha256"],
        site.pin(field_path),
        site.pin(nav),
    )
    assert spec["pilot_tree_clip"]["source_legacy_sha256"] == pins["presentation"]
    assert spec["pilot_tree_clip"]["source_refined_sha256"] == site.pin(
        scene / "pilot-trees-l2/trees.glb"
    )
    envelopes = []
    for directory, digest in pins["neighbors"].items():
        descriptor = scene / directory / "site.json"
        assert site.pin(descriptor) == digest
        for row in site.read(descriptor)["buildings"]:
            for ring in (
                row["footprint_enu_m"],
                *row.get("support_collision_enu_m", []),
            ):
                envelopes.append(Polygon(ring).buffer(0.035))
    footprint = unary_union(envelopes)
    field = site.read(field_path)
    ground, details, plants, art = [], [], [], []
    all_paths, meters = {}, {}
    zones = spec["zones"]
    for key, zone in zones.items():
        paved, lawn, beds = paved_zone(ground, plants, field, key, zone, footprint)
        all_paths[key] = paved
        meters[key] = {
            "walks": len(zone["walks"]),
            "paved_area_m2": round(paved.area, 2),
            "lawn_area_m2": round(lawn, 2),
            "planting_area_m2": round(beds, 2),
            "registered_trees": len(zone["trees"]),
        }
    womens = zones["womens"]
    collisions = memorial_wall(details, field, womens["wall_chains_enu_m"])
    collisions.extend(bench(details, field, row) for row in womens["stone_benches"])
    for row in womens["stairs"]:
        stair_steps(ground, details, field, row)
    entrance_detail(ground, details, field, zones["gerlinger"], all_paths["gerlinger"])
    senior_bench, art_area = straub_detail(ground, details, art, field, zones["straub"])
    collisions.append(senior_bench)
    street = spec["street_crossing"]
    sidewalks = unary_union(list(all_paths.values()))
    ramps = unary_union([Polygon(outline) for outline in street["curb_ramps_enu_m"]])
    asphalt = Polygon(street["pavement_enu_m"]).difference(ramps.union(sidewalks))
    drape(ground, field, asphalt, (101, 103, 95), PAVING_LIFT)
    drape(ground, field, ramps.difference(sidewalks), WALK, PAVING_LIFT)
    for a, b in spec["street_crosswalk_enu_m"]:
        marking = site.landscape.rect_on(a, b, 0.24)
        drape(ground, field, marking, (205, 205, 187), PAVING_LIFT + 0.006)
    route_count, distances = count_paths(
        site.read(nav),
        spec["walkable_ground"],
        unary_union(list(all_paths.values())),
        footprint.union(unary_union([box(*b) for b in collisions])),
    )
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        (DETAIL, details, "landscape-detail"),
        (PLANTS, plants, "landscape-vegetation"),
        (ART, art, "landscape-detail"),
        surface_layer=GROUND,
    )
    result = dict(
        source_presentation_sha256=pins["presentation"],
        source_base_model_sha256=pins["campus"],
        source_heightfield_sha256=pins["heightfield"],
        source_navigation_sha256=pins["navigation"],
        url=f"{PACKAGE}/site.glb",
        sha256=site.pin(glb),
        ground_node=GROUND,
        buildings=[],
        walkable_ground=spec["walkable_ground"],
        closed_site_boxes_enu_m=collisions,
        pilot_tree_clip=spec["pilot_tree_clip"],
        pilot_understory_clip=spec["pilot_understory_clip"],
    )
    descriptor = args.stage / "site.json"
    site.fairmount.write_json(descriptor, result, compact=True)
    audit = dict(
        zones=meters,
        faces=faces,
        route_edges=route_count,
        registered_route_m=distances,
        ornamental_benches=len(womens["stone_benches"]) + 1,
        wall_length_m=round(
            sum(LineString(c).length for c in womens["wall_chains_enu_m"]), 2
        ),
        stair_treads=[row["treads"] for row in womens["stairs"]],
        art_platform_area_m2=round(art_area, 2),
        crosswalk_markings=len(spec["street_crosswalk_enu_m"]),
        removed_procedural_trees=len(result["pilot_tree_clip"]["tree_indices"]),
        asset_sha256=site.pin(glb),
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
