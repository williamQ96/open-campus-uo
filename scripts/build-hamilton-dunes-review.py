# SPDX-License-Identifier: Apache-2.0
"""Export the Great Lawn and Duck Dunes redevelopment over former Hamilton Hall."""

import argparse
from importlib import import_module
import json
from pathlib import Path

import numpy as np
from shapely import constrained_delaunay_triangles
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import trimesh

previous = import_module("build-riverfront-plant-infrastructure-review")
terrain = previous.previous
geometry = previous.geometry
grade = terrain.hilyard.grade
cap, digest, read, ring = previous.cap, previous.digest, previous.read, previous.ring
fairmount = previous.fairmount
ordered_mesh = terrain.garden.science.ordered_mesh

PACKAGE = "hamilton-dunes-review"
BUILDING = "uo-duck-dunes-support"
GROUND = "hamilton-dunes-landscape"
WALK = "hamilton-dunes-walkable"
PARK = "hamilton-dunes-park-surface"
NAME = "Duck Dunes Support Building"
ADDRESS = "1680 East 13th Avenue"

CHARCOAL = (54, 59, 58)
METAL = (74, 76, 69)
GOLD = (222, 185, 53)
CONCRETE = (180, 174, 156)
PAVING = (185, 180, 159)
SAND = (214, 192, 151)
TURF = (112, 143, 88)
MEADOW = (133, 150, 102)


def top_surface(parts, plan, elevation, color, cell=2.75):
    west, south, east, north = plan.bounds
    vertices = []
    for x in np.arange(west, east, cell):
        for y in np.arange(south, north, cell):
            tile = plan.intersection(box(x, y, x + cell, y + cell))
            for piece in geometry.sections(tile):
                for triangle in constrained_delaunay_triangles(piece).geoms:
                    if triangle.area > 0.000005:
                        for e, n in list(orient(triangle).exterior.coords)[:3]:
                            vertices.append((e, elevation(e, n), -n))
    if vertices:
        mesh = trimesh.Trimesh(
            vertices=vertices,
            faces=np.arange(len(vertices)).reshape(-1, 3),
            process=False,
        )
        mesh.visual.vertex_colors = np.tile((*color, 255), (len(vertices), 1))
        parts.append(mesh)


def rect_on(a, b, width):
    return LineString([a, b]).buffer(width / 2, cap_style="flat")


def absolute_grade(field, e, n):
    return float(grade(field, (e, n)))


def support_building(spec, field, paving, elevation):
    outline = np.array(spec["support_enu_m"])
    shape = Polygon(outline)
    start = outline[0]
    north = (outline[3] - start) / np.linalg.norm(outline[3] - start)
    east = np.array([north[1], -north[0]])
    width = np.linalg.norm(outline[1] - start)
    length = np.linalg.norm(outline[3] - start)
    base = min(grade(field, p) for p in outline) - 0.14
    slab = elevation(*(start + 2.42 * north - 0.45 * east)) + 0.045
    high = slab + 3.08
    parts = [cap(shape, base, high, CHARCOAL)]

    def local(x, y):
        return start + x * east + y * north

    def panel(lo, hi, bottom, top, color, upper=None):
        x0, y0 = lo
        x1, y1 = hi
        plan = Polygon([local(x0, y0), local(x1, y0), local(x1, y1), local(x0, y1)])
        parts.append(cap(plan, bottom, top, color, upper))

    panel(
        (-0.085, -0.06),
        (width + 0.065, length + 0.06),
        high - 0.22,
        high + 0.06,
        METAL,
        (82, 83, 75),
    )
    for y in np.arange(0.10, length - 0.07, 0.19):
        panel((0.01, y), (-0.024, y + 0.032), slab - 0.17, high - 0.22, METAL)
        panel(
            (width - 0.012, y),
            (width + 0.025, y + 0.032),
            slab - 0.17,
            high - 0.22,
            METAL,
        )
    for x in np.arange(0.065, width - 0.07, 0.19):
        panel((x, 0.009), (x + 0.033, -0.023), slab - 0.17, high - 0.22, METAL)
        panel(
            (x, length - 0.011),
            (x + 0.033, length + 0.023),
            slab - 0.17,
            high - 0.22,
            METAL,
        )
    panel((-0.86, 0.50), (-0.025, length - 0.31), slab + 2.32, slab + 2.43, GOLD)
    for y in (0.59, 3.50, 6.70):
        panel((-0.72, y), (-0.06, y + 0.045), slab + 2.23, slab + 2.32, METAL)
    for y, extent in ((1.30, 0.99), (2.53, 1.20)):
        panel((-0.072, y), (-0.026, y + extent), slab - 0.015, slab + 2.20, METAL)
        panel(
            (-0.094, y + 0.043),
            (-0.069, y + extent - 0.042),
            slab + 0.017,
            slab + 2.14,
            (41, 45, 42),
        )
        panel(
            (-0.119, y + extent - 0.20),
            (-0.092, y + extent - 0.11),
            slab + 0.96,
            slab + 1.00,
            (148, 143, 121),
        )
    # One threshold and a shallow platform immediately below the door.
    apron = Polygon(
        [local(-0.63, 1.12), local(0, 1.12), local(0, 3.91), local(-0.63, 3.91)]
    )
    top_surface(paving, apron, lambda *_: slab, CONCRETE)
    door = local(0, 1.796)
    outward = -east
    bearing = np.rad2deg(np.arctan2(outward[0], outward[1])) % 360
    entry = {
        "gate": "west-approach",
        "position_enu_m": door.round(4).tolist(),
        "outward_degrees": round(float(bearing), 3),
        "approach_distance_m": 1.8,
    }
    data = dict(
        id=BUILDING,
        name=NAME,
        street_address=ADDRESS,
        footprint_enu_m=ring(shape),
        area_m2=round(shape.area, 3),
        base_z_m=round(float(base), 4),
        roof_z_m=round(float(high + 0.06), 4),
        entrances=[entry],
    )
    shell = trimesh.Trimesh(vertices=parts[0].vertices, faces=parts[0].faces)
    assert shell.is_volume and shell.volume > 90
    return ordered_mesh(trimesh.util.concatenate(parts)), data, shape


def court_hardware(spec, parts, collision):
    z = spec["sand_grade_m"]
    sand = box(*spec["sand_enu_m"])
    sizes = []
    for e, n in spec["courts_enu_m"]:
        playing = box(e - 4.0, n - 8.0, e + 4.0, n + 8.0)
        assert sand.buffer(-3.0).covers(playing)
        a, b = (e - 4.55, n), (e + 4.55, n)
        sizes.append(round(playing.area, 3))
        beam = LineString([a, b])
        for point in (a, b):
            parts.append(
                cap(
                    Point(point).buffer(0.084, quad_segs=6),
                    z,
                    z + 2.51,
                    (119, 119, 110),
                )
            )
            parts.append(
                cap(
                    Point(point).buffer(0.137, quad_segs=5),
                    z + 0.04,
                    z + 1.89,
                    CHARCOAL,
                )
            )
        low, high = z + 1.28, z + 2.24
        for level in (low, high):
            parts.append(
                cap(
                    beam.buffer(0.026, cap_style="flat"),
                    level - 0.021,
                    level + 0.022,
                    CHARCOAL,
                )
            )
        for t in np.linspace(0.014, 0.986, 70):
            parts.append(
                cap(
                    beam.interpolate(t, normalized=True).buffer(0.008, quad_segs=1),
                    low,
                    high,
                    (92, 88, 71),
                )
            )
        for level in np.linspace(low + 0.12, high - 0.12, 7):
            parts.append(
                cap(
                    beam.buffer(0.012, cap_style="flat"),
                    level - 0.008,
                    level + 0.008,
                    (92, 88, 71),
                )
            )
        collision.append(list(beam.buffer(0.12, cap_style="square").bounds))
    return sizes


def curbs(spec, field, parts, collision):
    w, s, e, n = spec["sand_enu_m"]
    z = spec["sand_grade_m"]
    runs = [
        ((w, n), (e, n)),
        ((w, s), (e, s)),
        ((w, s), (w, -44.9)),
        ((w, -41.1), (w, n)),
        ((e, s), (e, -26.9)),
        ((e, -22.3), (e, n)),
    ]
    for a, b in runs:
        shape = rect_on(a, b, 0.34)
        low = min(grade(field, p) for p in shape.exterior.coords) - 0.11
        parts.append(cap(shape, low, z + 0.27, (162, 154, 138), CONCRETE))
        collision.append(list(shape.bounds))


def fence(spec, parts, collision, height):
    for a, b in spec["fence_enu_m"]:
        center = LineString([a, b])
        band = center.buffer(0.039, cap_style="flat")

        knots = [
            center.interpolate(t, normalized=True).coords[0]
            for t in np.linspace(0, 1, max(2, round(center.length / 1.55) + 1))
        ]
        for a, b in zip(knots[:-1], knots[1:]):
            segment = rect_on(a, b, 0.065)
            for level in (0.28, 0.94):
                mesh = cap(segment, level - 0.039, level, CHARCOAL)
                mesh.vertices[:, 1] += [height(e, -s) for e, _, s in mesh.vertices]
                parts.append(mesh)
        for i, d in enumerate(
            np.linspace(0.0, center.length, max(2, round(center.length / 0.19) + 1))
        ):
            e, n = center.interpolate(d).coords[0]
            post = box(e - 0.019, n - 0.019, e + 0.019, n + 0.019)
            top = height(e, n)
            parts.append(
                cap(post, top - 0.014, top + (1.16 if i % 11 == 0 else 1.06), CHARCOAL)
            )
        collision.append(list(band.bounds))


def scoreboard(spec, parts, collision, height):
    board = spec["scoreboard"]
    e, n = board["center_enu_m"]
    half = board["width_m"] / 2
    z = height(e, n)
    for t in (-half * 0.67, half * 0.67):
        post = box(e - 0.12, n + t - 0.09, e + 0.12, n + t + 0.09)
        parts.append(cap(post, height(e, n + t) - 0.08, z + 3.14, METAL))
        collision.append(list(post.bounds))
    bottom = z + 1.43
    top = bottom + board["height_m"]
    body = box(e - 0.17, n - half, e + 0.17, n + half)
    parts.append(cap(body, bottom, top, (39, 44, 43)))
    title = box(e - 0.186, n - half + 0.18, e - 0.167, n + half - 0.18)
    parts.append(cap(title, top - 0.48, top - 0.36, GOLD))
    for p in np.linspace(-half + 0.65, half - 0.65, 6):
        for level in (0.38, 1.05):
            cell = box(e - 0.19, n + p - 0.27, e - 0.163, n + p + 0.27)
            parts.append(
                cap(cell, bottom + level, bottom + level + 0.21, (117, 118, 92))
            )


def fittings(parts, height, path):
    for e, n in (
        (130, -69.5),
        (139.5, -70.7),
        (170, -70.8),
        (173.5, -82),
        (127, -123.6),
        (178.1, -124.4),
    ):
        p = Point(e, n)
        if path.distance(p) < 0.60:
            continue
        top = height(e, n) + 0.44
        for a in (-0.60, 0.60):
            plan = box(e + a - 0.083, n - 0.16, e + a + 0.083, n + 0.16)
            parts.append(cap(plan, height(e + a, n), top, METAL))
        for shift in (-0.15, 0, 0.15):
            board = box(e - 0.91, n + shift - 0.064, e + 0.91, n + shift + 0.064)
            parts.append(cap(board, top, top + 0.077, (125, 103, 73), (145, 120, 82)))
    for e, n in (
        (125.1, -55.7),
        (141.1, -73.8),
        (166.1, -76.2),
        (185.0, -85.3),
        (184.0, -11.2),
        (126.8, -10.9),
    ):
        z = height(e, n)
        point = Point(e, n)
        parts.append(
            cap(point.buffer(0.062, quad_segs=4), z - 0.13, z + 3.01, (64, 77, 60))
        )
        globe = trimesh.creation.icosphere(subdivisions=2, radius=0.148)
        globe.apply_translation((e, z + 3.09, -n))
        globe.visual.vertex_colors = np.tile(
            (227, 220, 185, 255), (len(globe.vertices), 1)
        )
        parts.append(globe)


def land(spec, field):
    sand = box(*spec["sand_enu_m"])
    level = spec["sand_grade_m"]
    lawn = Polygon(spec["lawn_enu_m"]).intersection(box(0, -133.6, 500, 500))
    park = Polygon(spec["landscape_enu_m"])
    building = Polygon(spec["support_enu_m"])
    route = spec["visit_route"]
    lane = LineString(route["points_enu_m"])
    a, b, c, d = spec["sand_enu_m"]
    walk_region = box(a - 8.7, b - 11.75, c + 17.75, -5.0)
    paths = [
        LineString(row["centerline_enu_m"]).buffer(row["width_m"] / 2, quad_segs=6)
        for row in (*spec["planned_paths"], *spec["joining_paths"])
    ]
    paths.extend(
        [
            lane.buffer(1.65, quad_segs=6),
            rect_on((a - 2, -14.75), (191.4, -14.75), 2.24).difference(
                box(174.6, -16.0, 181.6, -12.7)
            ),
            box(179.55, -25.8, 183.14, -15.6),
            lawn.buffer(2.85, quad_segs=9).difference(lawn),
        ]
    )
    paving = unary_union(paths).difference(sand.union(building))
    lawn = lawn.difference(paving)
    colors = ([], [], [])
    walk, base, detail = colors

    def terrain_z(e, n):
        return absolute_grade(field, e, n) + 0.134

    def slope_z(e, n):
        return max(terrain_z(e, n), level - 0.091 * sand.distance(Point(e, n)))

    lines = unary_union(
        [
            box(e - 4, n - 8, e + 4, n + 8).boundary.buffer(0.036)
            for e, n in spec["courts_enu_m"]
        ]
    )
    top_surface(walk, sand.difference(lines), lambda *_: level, SAND, cell=2.65)
    top_surface(walk, lines, lambda *_: level, (82, 77, 64), cell=2.65)
    top_surface(walk, paving.intersection(walk_region), slope_z, PAVING)
    top_surface(base, paving.difference(walk_region), terrain_z, PAVING, cell=1.8)
    top_surface(base, lawn, lambda e, n: terrain_z(e, n) - 0.019, TURF, cell=1.55)
    landscape = park.difference(unary_union((lawn, paving, building, sand)))
    verge = landscape.intersection(sand.buffer(8.25, quad_segs=6)).intersection(
        walk_region
    )
    top_surface(
        walk,
        verge,
        lambda e, n: slope_z(e, n) - min(0.032, 0.06 * sand.distance(Point(e, n))),
        MEADOW,
    )
    top_surface(
        base,
        landscape.difference(verge),
        lambda e, n: terrain_z(e, n) - 0.036,
        MEADOW,
        cell=1.95,
    )

    collision = []
    areas = court_hardware(spec, detail, collision)
    curbs(spec, field, detail, collision)
    fence(spec, detail, collision, slope_z)
    scoreboard(spec, detail, collision, slope_z)
    fittings(detail, terrain_z, paving)
    model, record, footprint = support_building(spec, field, walk, slope_z)
    assert len(collision) <= 16
    assert paving.buffer(0.025).covers(lane)
    across = LineString([(177.4, -24.15), (181.2, -23.25)])
    assert all(across.distance(box(*r)) >= 0.55 for r in collision)
    clearance_line = LineString([route["anchor_enu_m"], *route["points_enu_m"]])
    assert clearance_line.distance(footprint) > 1.58
    assert all(clearance_line.distance(box(*r)) >= 0.55 for r in collision)

    measurements = dict(
        sand_area_m2=round(sand.area, 3),
        sand_surface_z_m=level,
        lawn_area_m2=round(lawn.area, 3),
        paved_area_m2=round(paving.area, 3),
        playing_areas_m2=areas,
        route_branch_m=round(clearance_line.length, 3),
        minimum_route_obstacle_clearance_m=round(
            min(clearance_line.distance(box(*r)) for r in collision), 3
        ),
    )
    return model, record, walk, base, detail, walk_region, collision, measurements


def verify_sources(spec, config):
    audit = spec["batch"]
    source = fairmount.SCENE / config["asset_url"]
    assert digest(source) == audit["source_asset_sha256"] == config["asset_sha256"]
    batch = read(fairmount.ROOT / "data/metadata/campus-expansion-audit.json")[
        "context_batches"
    ]
    removals = audit["batch_removals"]
    target = removals[0]["target"]
    model = trimesh.load(source, force="scene", process=False)
    matrix, key = model.graph[target]
    assert np.array_equal(matrix, np.eye(4))
    tri = model.geometry[key].triangles
    all_ranges = audit["range_order"]
    assert list(batch[target]) == [key for key, a, b in all_ranges]
    assert all_ranges[0][1] == 0 and all_ranges[-1][2] == len(tri)
    assert all(a[2] == b[1] for a, b in zip(all_ranges[:-1], all_ranges[1:]))
    lookup = {key: (a, b) for key, a, b in all_ranges}
    for row in removals:
        a, b = row["triangles"]
        assert (a, b) == lookup[row["id"]] and row["target"] == target
        assert len(tri) == row["source_triangle_count"]
        vertices = tri[a:b].reshape(-1, 3)
        for i, point in row["source_vertices"]:
            assert np.linalg.norm(vertices[i] - point) <= 0.000002
    return removals


def export_glb(path, model, walk, park, details):
    scene = trimesh.Scene()
    for name, mesh, kind in (
        (BUILDING, model, "building"),
        (WALK, walk, "landscape-surface"),
        (PARK, park, "landscape-surface"),
        (GROUND, details, "landscape-detail"),
    ):
        colors = mesh.visual.vertex_colors.copy()
        srgb = colors[:, :3] / 255
        linear = np.where(
            srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4
        )
        colors[:, :3] = (linear * 255).round().astype(np.uint8)
        mesh.visual.vertex_colors = colors
        mesh.metadata.update(asset_id=name, asset_kind=kind)
        scene.add_geometry(mesh, node_name=name, geom_name=name)

    def materials(tree):
        tree["asset"]["copyright"] = (
            "Open Campus contributors. Original geometry CC BY 4.0."
        )
        tree["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.025, "roughnessFactor": 0.86}}
        ]
        for mesh in tree["meshes"]:
            mesh["primitives"][0]["material"] = 0

    path.write_bytes(
        trimesh.exchange.gltf.export_glb(
            scene, include_normals=True, tree_postprocessor=materials
        )
    )
    reload = trimesh.load(path, force="scene", process=False)
    assert set(reload.graph.nodes_geometry) == {BUILDING, WALK, PARK, GROUND}
    assert np.allclose(scene.bounds, reload.bounds, atol=0.00005)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()

    scene = fairmount.SCENE
    spec = read(fairmount.ROOT / f"data/metadata/{PACKAGE}.json")
    manifest = read(scene / "manifest.json")
    config = read(scene / "presentation.json")
    graph = read(scene / "navigation.json")
    field = read(scene / manifest["heightfield_url"])
    for key, name in (
        ("manifest", "manifest.json"),
        ("heightfield", manifest["heightfield_url"]),
        ("navigation", "navigation.json"),
    ):
        assert digest(scene / name) == spec[f"source_{key}_sha256"]
    removals = verify_sources(spec, config)
    retired = [r["id"] for r in removals]
    model, record, surfaces, park, details, region, boxes, metrics = land(spec, field)
    route = spec["visit_route"]

    edges, clearance = (
        fairmount.chapter.prior.nearby.shared.graduate.shared.check_routes(
            [Polygon(record["footprint_enu_m"])],
            [box(*b) for b in boxes],
            [record["entrances"][0]],
            unary_union(
                [
                    Polygon(r["footprint_enu_m"]).buffer(0)
                    for r in manifest["buildings"]
                    if r["id"] in retired
                ]
            ),
            manifest,
            graph,
            config,
            retired,
        )
    )
    assert route["anchor_enu_m"] in graph["nodes_enu_m"]
    assert clearance > 0.55
    assert len(Polygon(record["footprint_enu_m"]).exterior.coords) == 5
    walk = ordered_mesh(trimesh.util.concatenate(surfaces))
    park_mesh = ordered_mesh(trimesh.util.concatenate(park))
    context = ordered_mesh(trimesh.util.concatenate(details))
    pa, pb, pc, pd = spec["sand_enu_m"]
    probes = [
        (e, n)
        for e in np.linspace(pa + 0.45, pc - 0.45, 16)
        for n in np.linspace(pb + 0.45, pd - 0.45, 10)
    ]
    baseline = max(grade(field, p) for p in probes)
    assert baseline < spec["sand_grade_m"] - 0.05
    hits, ray_indices, _ = walk.ray.intersects_location(
        [(e, 25, -n) for e, n in probes],
        [(0, -1, 0)] * len(probes),
        multiple_hits=False,
    )
    assert len(ray_indices) == len(probes)
    assert np.allclose(hits[:, 1], spec["sand_grade_m"], atol=0.00005)

    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    export_glb(glb, model, walk, park_mesh, context)
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=spec["source_heightfield_sha256"],
        source_navigation_sha256=spec["source_navigation_sha256"],
        ground_node=GROUND,
        url=f"{PACKAGE}/site.glb",
        sha256=digest(glb),
        buildings=[record],
        absorbed_ids=retired,
        new_building_ids=[BUILDING],
        batch_removals=removals,
        context_trees=spec["context_trees"],
        closed_site_boxes_enu_m=[[round(x, 4) for x in b] for b in boxes],
        walkable_ground=dict(
            bounds_enu_m=[[round(x, 4) for x in region.bounds]],
            anchor_enu_m=route["anchor_enu_m"],
            points_enu_m=route["points_enu_m"],
        ),
    )
    descriptor = args.stage / "site.json"
    fairmount.write_json(descriptor, payload, compact=True)
    metrics.update(
        hashes={"site.glb": digest(glb), "site.json": digest(descriptor)},
        source_legacy_triangles=spec["batch"]["retired_triangles"],
        retained_neighbors=spec["batch"]["neighbors"],
        base_route_edges=edges,
        base_route_clearance_m=round(clearance, 4),
        sand_surface_probes=len(probes),
        max_sampled_legacy_sand_terrain_m=round(float(baseline), 4),
        collision_boxes=len(boxes),
        support_triangles=len(model.faces),
        walkable_triangles=len(walk.faces),
        park_triangles=len(park_mesh.faces),
        detail_triangles=len(context.faces),
    )
    fairmount.write_json(args.audit, metrics)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
