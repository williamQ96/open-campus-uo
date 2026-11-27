# SPDX-License-Identifier: Apache-2.0
"""Build the Memorial Quad surfaces and measured-width campus corridors."""

import argparse
from collections import defaultdict
from hashlib import sha256
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import struct

import numpy as np
from shapely import constrained_delaunay_triangles, get_parts, make_valid, union_all
from shapely.affinity import rotate, scale, translate
from shapely.geometry import LineString, Point, Polygon, box, mapping, shape
from shapely.geometry.polygon import orient
from shapely.ops import nearest_points, substring
import trimesh

source = import_module("build-pilot-tree-clearance")
bailey = import_module("build-memorial-quad-bailey-oaks")
ROOT = source.ROOT
SCENE = source.SCENE
SPEC = ROOT / "data/metadata/paving-corridors-l2.json"
DIRECTORY = "paving-corridors-l2"
DRAPE_SHA = "841412e2a6111d9f6a9ab09ce74f44469e7c7af5251bdaeb296526522764625f"


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def gltf(path):
    raw = path.read_bytes()
    size, tag = struct.unpack_from("<I4s", raw, 12)
    assert tag == b"JSON" and raw[24 + size : 28 + size] == b"BIN\0"
    return json.loads(raw[20 : 20 + size]), memoryview(raw)[28 + size :]


def locate(document, name):
    node = next(node for node in document["nodes"] if node.get("name") == name)
    (surface,) = document["meshes"][node["mesh"]]["primitives"]
    return surface


def mesh(geometry, field, drape, lift, palette=None):
    vertices, faces = drape.drape_surface(geometry, field, lift)
    vertices = np.asarray(vertices)[:, [0, 2, 1]] * [1, 1, -1]
    result = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    if palette:
        color = np.asarray(palette) / 255
        linear = np.where(
            color <= 0.04045, color / 12.92, ((color + 0.055) / 1.055) ** 2.4
        )
        result.visual.vertex_colors = [*np.round(linear * 255).astype(np.uint8), 255]
    return result


def quad_shapes(spec, buildings):
    local = spec["quad"]
    oaks = read(bailey.SPEC)
    window = box(*local["window_enu_m"]).union(
        box(*oaks["east_walk_extent_enu_m"])
    )
    tree_roots = bailey.roots(oaks)
    ring = local["ring"]
    disk = scale(Point(*ring["center_enu_m"]).buffer(1, quad_segs=20), *ring["radii_m"])
    half = ring["width_m"] / 2
    outer = disk.buffer(half, quad_segs=4)
    inner = disk.buffer(-half, quad_segs=4)
    lines = [
        LineString(walk["center_enu_m"]).buffer(walk["width_m"] / 2, quad_segs=4)
        for walk in local["walks"]
    ]
    inventory = read(ROOT / "data/metadata/pilot-trees-l2.json")
    stems = {tree["index"]: tree["origin_gltf_m"] for tree in inventory["trees"]}
    pits = union_all(
        [
            Point(stems[index][0], -stems[index][2]).buffer(0.67, quad_segs=5)
            for index in local["tree_pits"]
        ]
    )
    concrete = (
        union_all([outer.difference(inner), *lines])
        .intersection(window)
        .difference(buildings)
        .difference(pits.union(tree_roots))
    )
    lawn = (
        Polygon(local["lawn_boundary_enu_m"])
        .intersection(window)
        .difference(concrete)
        .difference(buildings)
        .difference(tree_roots)
    )
    return window, concrete, lawn


def quad_routes(spec, window, paving):
    graph = read(SCENE / "navigation.json")
    nodes = graph["nodes_enu_m"]
    south, junction, north = spec["quad"]["route_anchors"]
    retired = [(a, a + 1) for a in range(south, north)]
    assert set(retired) <= {
        (a, b) for a, b, _, kind in graph["edges"] if kind == "path"
    }
    removed = [n for n in range(south + 1, north) if n != junction]
    assert not (
        set(removed)
        & {i for a, b, *_ in graph["edges"] if (a, b) not in retired for i in (a, b)}
    )
    walks = {
        walk["id"]: LineString(walk["center_enu_m"]) for walk in spec["quad"]["walks"]
    }
    ring = spec["quad"]["ring"]
    ellipse = scale(
        Point(*ring["center_enu_m"]).buffer(1, quad_segs=12), *ring["radii_m"]
    ).exterior
    supports = [
        p
        for line in [*walks.values(), ellipse]
        for p in get_parts(line.intersection(paving.buffer(-0.1)))
        if p.length > 0.03
    ]
    for side in ("west", "east"):
        points = nearest_points(walks[side + "-edge"], ellipse)
        line = LineString([point.coords[0] for point in points])
        if line.length > 0.001 and paving.buffer(0.05).covers(line):
            supports.append(line)
    center_paths = union_all(supports)
    ties = [
        LineString(
            [nodes[anchor], nearest_points(Point(*nodes[anchor]), center_paths)[1]]
        )
        for anchor in (south, junction, north)
    ]
    assert all(line.length < 10 for line in ties), [line.length for line in ties]
    noded = union_all([center_paths, *(line for line in ties if line.length > 0.001)])
    edges = set()
    for segment in get_parts(noded.segmentize(5.0)):
        points = [
            tuple(round(float(value), 4) for value in row) for row in segment.coords
        ]
        edges.update(
            tuple(sorted((a, b)))
            for a, b in zip(points, points[1:])
            if Point(a).distance(Point(b)) > 0.01
        )
    coords = sorted({point for edge in edges for point in edge})
    index = {point: i for i, point in enumerate(coords)}
    result = [
        [index[a], index[b], round(Point(a).distance(Point(b)), 4), "path"]
        for a, b in sorted(edges)
    ]
    linked = [index[tuple(nodes[i])] for i in (south, junction, north)]
    neighbors = defaultdict(set)
    for a, b, *_ in result:
        neighbors[a].add(b)
        neighbors[b].add(a)
    connected, queue = set(), [linked[0]]
    while queue:
        a = queue.pop()
        if a in connected:
            continue
        connected.add(a)
        queue.extend(neighbors[a] - connected)
    assert set(linked) <= connected
    assert all(
        LineString(edge).intersection(window).difference(paving.buffer(0.14)).length
        < 0.12
        for edge in edges
    )
    active = sorted(connected)
    reindex = {original: replacement for replacement, original in enumerate(active)}
    return {
        "source_nodes": [[i, nodes[i]] for i in range(south, north + 1)],
        "original_anchors": list(
            zip((south, junction, north), (reindex[i] for i in linked))
        ),
        "retired_edges": retired,
        "retired_nodes": removed,
        "nodes": [coords[i] for i in active],
        "edges": [
            [reindex[a], reindex[b], length, kind]
            for a, b, length, kind in result
            if a in connected
        ],
    }


def route_coverage(paving):
    coverage = paving.buffer(0.13, quad_segs=2).simplify(0.015)
    return [
        [
            [[round(e, 3), round(n, 3)] for e, n in ring.coords[:-1]]
            for ring in [part.exterior, *part.interiors]
        ]
        for part in get_parts(coverage.normalize())
    ]


def quad_activity(spec, window, paving, lawn, field, drape):
    activity = read(SCENE / "activity.json")
    (prior,) = [p for p in activity["paths"] if p["id"] == "sidewalk-0-0"]
    walks = {
        walk["id"]: LineString(walk["center_enu_m"]) for walk in spec["quad"]["walks"]
    }
    west = walks["west-edge"]
    north = walks["north-entrance-link"]
    north_stop = north.interpolate(north.project(Point(-552, -9.5)))
    # Both termini lie inside the verified pavement.
    walkable = paving.buffer(-0.45)
    west_run = max(get_parts(west.intersection(walkable)), key=lambda p: p.length)
    line = LineString([*reversed(west_run.coords), north_stop.coords[0]])
    assert walkable.buffer(0.001).covers(line)
    # Avoid sampling at the outer mask boundary where rounding can flip coverage.
    line = substring(line, 0.1, line.length - 0.1)

    def patch(route, centerline):
        return {
            "id": route["id"],
            "surface": route["surface"],
            "source_ends": [route["points_enu_m"][0], route["points_enu_m"][-1]],
            "points": [
                [round(e, 4), round(n, 4), round(drape.sample_terrain(field, e, n) + 0.075, 4)]
                for e, n in centerline.segmentize(1.0).coords
            ],
        }

    routes = [patch(prior, line)]
    stems = read(ROOT / "data/metadata/pilot-trees-l2.json")["trees"]
    removed = set(read(bailey.SPEC)["retired_pilot_indices"])
    tree_clearance = union_all(
        [
            Point(x, -z).buffer(0.75)
            for row in stems
            if row["index"] not in removed
            for x, _, z in [row["origin_gltf_m"]]
        ]
    )
    green = lawn.buffer(-0.38).difference(tree_clearance)
    offsets = [0, *(sign * step for step in range(1, 15) for sign in [-1, 1])]
    for route in activity["paths"]:
        if route["surface"] != "vegetation":
            continue
        old = LineString([point[:2] for point in route["points_enu_m"]])
        if old.intersection(window).length < 0.01:
            continue
        (ax, ay), (bx, by) = old.coords[0], old.coords[-1]
        norm = np.hypot(bx - ax, by - ay)
        direction = (-(by - ay) / norm, (bx - ax) / norm)
        candidates = (
            rotate(
                translate(
                    old,
                    direction[0] * offset + direction[1] * shift,
                    direction[1] * offset - direction[0] * shift,
                ),
                angle,
            )
            for shift in (0, -4, 4, -8, 8, -12, 12)
            for angle in (0, -25, 25, -50, 50, 90)
            for offset in offsets
        )
        for candidate in candidates:
            segments = [
                part for part in get_parts(candidate.intersection(green))
                if part.geom_type == "LineString" and part.length >= 7.2
            ]
            if segments:
                segment = max(segments, key=lambda part: part.length)
                routes.append(patch(route, substring(segment, 0.1, segment.length - 0.1)))
                break
        else:
            raise ValueError(f"No clear Memorial Quad lawn segment for {route['id']}.")

    region = shape(activity["pedestrian_regions"]).difference(window).union(walkable)
    return {
        "routes": routes,
        "pedestrian_regions": mapping(region.simplify(0.01, preserve_topology=True)),
    }


def quad_cut(document, binary, name, window):
    positions, triangles = source.mesh_arrays(document, binary, locate(document, name))
    lo, hi = triangles.min(), triangles.max()
    assert len(positions) > 0 and lo >= 0 and hi < len(positions)
    remove, corners = [], []
    partial_count = 0
    for i, indices in enumerate(triangles):
        xyz = positions[indices].astype(float)
        enu = xyz[:, [0, 2]] * [1, -1]
        footprint = Polygon(enu)
        if not footprint.is_valid or footprint.intersection(window).area < 1e-8:
            continue
        remove.append(i)
        kept = footprint.difference(window)
        if kept.is_empty or kept.area < 1e-8:
            continue
        partial_count += 1
        coefficients = np.linalg.solve(np.column_stack((enu, np.ones(3))), xyz[:, 1])
        for polygon in get_parts(kept):
            for piece in constrained_delaunay_triangles(polygon).geoms:
                if piece.area < 1e-8:
                    continue
                for e, n in list(orient(piece).exterior.coords)[:3]:
                    corners.append([e, np.dot(coefficients, [e, n, 1]), -n])
    assert remove
    stride = np.arange(len(corners)).reshape(-1, 3)
    border = trimesh.Trimesh(vertices=corners, faces=stride, process=False)
    groups = []
    for index in remove:
        if groups and index == groups[-1][1]:
            groups[-1][1] += 1
        else:
            groups.append([index, index + 1])
    flat = triangles.ravel()
    samples = np.linspace(0, len(remove) - 1, num=8, dtype=int)
    anchors = [
        [(slot := 3 * remove[t]), int(id := flat[slot]), positions[id].tolist()]
        for t in samples
    ]
    return border, {
        "name": name,
        "vertices": len(positions),
        "triangles": len(triangles),
        "remove": groups,
        "anchors": anchors,
        "reclipped_triangles": partial_count,
    }


def corridors(rows, buildings, field, drape, palette):
    categories = defaultdict(list)
    for feature in rows:
        spans = feature["spans"]
        widths = [piece["width_m"] for piece in spans]
        joints = [
            widths[0],
            *((a + b) / 2 for a, b in zip(widths, widths[1:])),
            widths[-1],
        ]
        for i, piece in enumerate(spans):
            color = piece["material"]
            assert color in palette
            center = LineString(piece["coordinates_enu_m"])
            distances = [
                0,
                *np.cumsum(
                    [
                        Point(a).distance(Point(b))
                        for a, b in zip(center.coords, list(center.coords)[1:])
                    ]
                ),
            ]
            diameters = np.interp(distances, [0, center.length], joints[i : i + 2])
            circles = [
                Point(point).buffer(width / 2, quad_segs=3)
                for point, width in zip(center.coords, diameters)
            ]
            surface = union_all(
                [a.union(b).convex_hull for a, b in zip(circles, circles[1:])]
            )
            categories[feature["kind"], color].append(surface)
    taken = Polygon()
    regions = defaultdict(list)
    measurements = {}
    extent = box(-1000, -1000, 1000, 1000)
    for kind, color in sorted(
        categories, key=lambda pair: (pair[0] != "road", list(palette).index(pair[1]))
    ):
        candidate = (
            union_all(categories[kind, color], grid_size=0.001)
            .intersection(extent)
            .difference(buildings)
        )
        candidate = make_valid(candidate).difference(taken)
        if candidate.area < 0.5:
            continue
        taken = taken.union(candidate)
        regions[kind].append(mesh(candidate, field, drape, 0.055, palette[color]))
        measurements[f"{kind}:{color}"] = round(candidate.area, 2)
    return {
        key: trimesh.util.concatenate(parts) for key, parts in regions.items()
    }, measurements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--grade-ties", type=Path, required=True)
    parser.add_argument("--drape", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    args = parser.parse_args()
    assert digest(args.drape) == DRAPE_SHA
    loader = spec_from_file_location("pinned_corridors", args.drape)
    drape = module_from_spec(loader)
    loader.loader.exec_module(drape)

    spec = read(SPEC)
    manifest = read(SCENE / "manifest.json")
    config = read(SCENE / "presentation.json")
    raw_field = SCENE / manifest["heightfield_url"]
    field = read(raw_field)
    foundation = SCENE / config["landcover_l2"]["url"]
    assert digest(foundation) == config["landcover_l2"]["sha256"]
    document, binary = gltf(foundation)
    ground, _ = source.mesh_arrays(
        document, binary, locate(document, "Eugene terrain and land cover L2")
    )
    assert len(ground) == len(field["heights_m"])
    terrain = np.asarray(field["heights_m"])
    delta = np.round(ground[:, 1].astype(float) - terrain - 0.018, 4)
    field["heights_m"] = (terrain + delta).tolist()
    ties = read(args.grade_ties)
    buildings = union_all(
        [
            make_valid(Polygon(b["footprint_enu_m"]))
            for b in ties["buildings"] + manifest["buildings"]
        ]
    )
    window, walk, lawn = quad_shapes(spec, buildings)
    route_patch = quad_routes(spec, window, walk)
    projected = np.stack([ground[:, 0], -ground[:, 2]], axis=1)
    west, south, east, north = window.buffer(8).bounds
    near_quad = ((projected >= (west, south)) & (projected <= (east, north))).all(
        axis=1
    )
    assert abs(delta[near_quad]).max() < 0.0001
    activity_patch = quad_activity(spec, window, walk, lawn, field, drape)
    art = SCENE / config["asset_url"]
    assert digest(art) == config["asset_sha256"]
    art_doc, art_bin = gltf(art)
    geometries, cuts = {}, []
    for name, region in (("landscape-paving", walk), ("landscape-lawn", lawn)):
        border, cut = quad_cut(art_doc, art_bin, name, window)
        geometries["quad-" + name] = trimesh.util.concatenate(
            [border, mesh(region, field, drape, 0.07)]
        )
        cuts.append(cut)

    oaks = read(bailey.SPEC)
    clip = oaks["pilot_tree_clip"]
    assert clip["source_legacy_sha256"] == config["asset_sha256"]
    assert clip["source_refined_sha256"] == digest(SCENE / "pilot-trees-l2/trees.glb")
    wood, crowns = bailey.branches_and_leaves(oaks, field)
    root_soil = bailey.roots(oaks)
    assert window.covers(root_soil) and not root_soil.intersects(walk.buffer(-0.01))
    soil = mesh(root_soil, field, drape, 0.074, (124, 102, 78))
    geometries.update(zip(bailey.NAMES, (wood, crowns, soil), strict=True))
    tree_boxes = bailey.collision_boxes(oaks)
    clearance = min(
        LineString([route_patch["nodes"][a], route_patch["nodes"][b]]).distance(box(*bounds))
        for bounds in tree_boxes
        for a, b, *_ in route_patch["edges"]
    )
    assert clearance > 0.53, clearance

    rows = read(args.candidate)
    current = {item["id"] for item in manifest["corridors"]["features"]}
    missing = sorted(current.difference(item["id"] for item in rows))
    assert len(rows) == 139 and len(missing) == 1
    road_parts, areas = corridors(
        rows, buildings, field, drape, spec["pavement_materials_srgb"]
    )
    assert set(road_parts) == {"road", "path"}
    geometries.update(
        {"corridors-" + kind: value for kind, value in road_parts.items()}
    )
    output = trimesh.Scene(base_frame=DIRECTORY)
    for name, geometry in geometries.items():
        output.add_geometry(geometry, node_name=name, geom_name=name)

    def annotate(doc):
        for node in doc["nodes"]:
            if node.get("name") in bailey.NAMES:
                name = node["name"]
                node["extras"] = {
                    "asset_id": name,
                    "asset_kind": (
                        "landscape-surface"
                        if name == bailey.NAMES[2]
                        else "landscape-vegetation"
                    ),
                }
            if node.get("name") in ("corridors-road", "corridors-path"):
                name = node["name"]
                node["extras"] = {
                    "asset_id": name,
                    "asset_kind": "corridor",
                    "corridor_kind": name.split("-")[1],
                }

    args.stage.mkdir(parents=True, exist_ok=True)
    asset = args.stage / "surfaces.glb"
    asset.write_bytes(
        trimesh.exchange.gltf.export_glb(
            output, include_normals=True, tree_postprocessor=annotate
        )
    )
    payload = {
        "url": f"{DIRECTORY}/surfaces.glb",
        "sha256": digest(asset),
        "source_art_sha256": digest(art),
        "source_model_sha256": manifest["model"]["sha256"],
        "source_landcover_sha256": digest(foundation),
        "source_navigation_sha256": digest(SCENE / "navigation.json"),
        "required_retired_corridors": missing,
        "quad_cuts": cuts,
        "quad_routes": route_patch,
        "quad_activity": activity_patch,
        "quad_route_coverage": route_coverage(walk),
        "quad_oaks": {
            "pilot_tree_clip": clip,
            "ids": [tree["id"] for tree in oaks["trees"]],
            "collision_boxes_enu_m": tree_boxes,
        },
    }
    descriptor_path = args.stage / "surfaces.json"
    descriptor_path.write_bytes(
        (json.dumps(payload, separators=(",", ":")) + "\n").encode()
    )
    report = {
        "glb_sha256": digest(asset),
        "descriptor_sha256": digest(descriptor_path),
        "glb_bytes": asset.stat().st_size,
        "triangles": {name: len(geom.faces) for name, geom in geometries.items()},
        "quad_surface_m2": {"walk": round(walk.area, 2), "lawn": round(lawn.area, 2)},
        "quad_source_triangles_replaced": {
            cut["name"]: sum(b - a for a, b in cut["remove"]) for cut in cuts
        },
        "road_and_path_material_areas_m2": areas,
        "quad_route_nodes": len(route_patch["nodes"]),
        "quad_route_edges": len(route_patch["edges"]),
        "oak_ids": payload["quad_oaks"]["ids"],
        "oak_soil_m2": round(root_soil.area, 3),
        "minimum_oak_route_gap_m": round(clearance, 3),
        "quad_retired_route_edges": len(route_patch["retired_edges"]),
        "quad_activity_points": {
            route["id"]: len(route["points"]) for route in payload["quad_activity"]["routes"]
        },
    }
    (args.stage / "audit.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
