# SPDX-License-Identifier: Apache-2.0
"""Build the editable pilot furnishing placements into three material batches."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, box
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "apps/web-preview/public/scene"
METADATA = ROOT / "data/metadata/pilot-furnishings-l2.json"
RACK = ROOT / "assets/props/bike-rack-candidate-2026-11-04.glb"
WOOD = (126, 83, 49, 255)
WOOD_END = (109, 71, 42, 255)
GREEN = (30, 58, 48, 255)
FOOTING = (135, 134, 122, 255)
GLOBE = (218, 225, 215, 255)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paint(mesh, color):
    mesh.visual = trimesh.visual.ColorVisuals(mesh, vertex_colors=color)
    return mesh


def beam(start, end, width, depth):
    direction = np.subtract(end, start)
    frame = trimesh.geometry.align_vectors([0, 0, 1], direction)
    frame[:3, 3] = (np.asarray(start) + end) / 2
    return trimesh.creation.box((width, depth, np.linalg.norm(direction)), frame)


def block(position, dimensions, angle=0):
    frame = trimesh.transformations.rotation_matrix(angle, (1, 0, 0))
    frame[:3, 3] = position
    return trimesh.creation.box(dimensions, frame)


def turned(profile, sections=24):
    mesh = trimesh.creation.revolve(profile, sections=sections)
    mesh.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, (1, 0, 0)))
    return mesh


def support_heights(row):
    heights = [p["surface_z_m"] for p in row["supports"]]
    if max(heights) - min(heights) > 0.13:
        raise ValueError(f"{row['id']} crosses a change in grade")
    return heights


def build_bench(row, materials):
    wood, metal, _ = materials
    heights = support_heights(row)
    grade = max(heights)
    for z, lift in (
        (-0.178, 0.015),
        (-0.114, 0.001),
        (-0.05, 0),
        (0.014, 0.003),
        (0.078, 0.012),
        (0.142, 0.022),
    ):
        wood.append(
            paint(block((0, grade + 0.408 + lift, z), (1.434, 0.031, 0.055)), WOOD)
        )
    for index in range(7):
        x = (index - 3) * 0.192
        wood.append(
            paint(
                beam(
                    (x, grade + 0.497, -0.175), (x, grade + 0.901, -0.221), 0.149, 0.032
                ),
                WOOD,
            )
        )
    wood.append(
        paint(block((0, grade + 0.936, -0.224), (1.524, 0.071, 0.065)), WOOD_END)
    )
    wood.append(
        paint(block((0, grade + 0.491, -0.179), (1.434, 0.043, 0.058)), WOOD_END)
    )
    wood.append(
        paint(block((0, grade + 0.369, 0.139), (1.434, 0.058, 0.069)), WOOD_END)
    )
    # ENU support samples run south to north. Scene depth runs north to south.
    for index, x in enumerate((-0.545, 0.545)):
        front, rear = heights[index * 2 : index * 2 + 2]
        for pad, (z, y) in enumerate(((0.219, front), (-0.216, rear))):
            top = grade + (0.642 if z > 0 else 0.942)
            top_z = z - 0.016 if z > 0 else -0.222
            wood.append(
                paint(beam((x, y + 0.011, z), (x, top, top_z), 0.067, 0.055), WOOD_END)
            )
            terrain = row["supports"][index * 2 + pad]["terrain_z_m"]
            bottom, top = min(terrain, y) - 0.013, y + 0.025
            metal.append(
                paint(
                    block((x, (bottom + top) / 2, z), (0.107, top - bottom, 0.09)),
                    GREEN,
                )
            )
        wood.append(paint(block((x, grade + 0.367, 0), (0.063, 0.08, 0.455)), WOOD_END))
        for a, b in zip(
            ((-0.219, 0.685), (-0.132, 0.694), (0.127, 0.672)),
            ((-0.132, 0.694), (0.127, 0.672), (0.221, 0.638)),
        ):
            wood.append(
                paint(
                    beam(
                        (x, grade + a[1], a[0]), (x, grade + b[1], b[0]), 0.087, 0.047
                    ),
                    WOOD,
                )
            )


def build_lamp(row, materials):
    _, metal, glass = materials
    heights = support_heights(row)
    grade = max(heights)
    lowest_support = min(heights)
    if row.get("memorial_quad_registration"):
        # Keep the footing grounded when the Quad or apron surface falls back.
        lowest_support = min(lowest_support, *(p["terrain_z_m"] for p in row["supports"]))
    base = lowest_support - grade - 0.028
    post = (
        (0, base),
        (0.252, base),
        (0.252, 0.043),
        (0.236, 0.063),
        (0.192, 0.063),
        (0.179, 0.083),
        (0.179, 0.121),
        (0.14, 0.16),
        (0.128, 0.217),
        (0.108, 0.645),
        (0.105, 0.697),
        (0.092, 0.731),
        (0.077, 0.752),
        (0.0725, 0.801),
        (0.060, 1.39),
        (0.045, 2.735),
        (0.047, 2.805),
        (0.064, 2.826),
        (0.068, 2.853),
        (0.056, 2.88),
        (0.087, 2.928),
        (0.105, 2.975),
        (0.108, 3.017),
        (0.087, 3.048),
        (0, 3.048),
    )
    metal.append(paint(turned(post[:4] + ((0, 0.063),)), FOOTING))
    metal.append(paint(turned(((0, 0.06),) + post[4:]), GREEN))
    for index, angle in enumerate(np.arange(10) * np.pi / 5):
        x, z = np.cos(angle), np.sin(angle)
        for low, high, inner, outer, width in (
            (0.156, 0.726, 0.136, 0.09, 0.019),
            (0.805, 2.764, 0.07, 0.043, 0.010),
        ):
            metal.append(
                paint(
                    beam(
                        (inner * x, low, inner * z),
                        (outer * x, high, outer * z),
                        width,
                        width,
                    ),
                    GREEN,
                )
            )
        if index in (0, 5):
            metal.append(
                paint(
                    block((0.212 * x, 0.071, 0.212 * z), (0.031, 0.017, 0.031)), GREEN
                )
            )
    lathe = [
        (0, 3.036),
        (0.079, 3.036),
        (0.096, 3.061),
        (0.122, 3.091),
        (0.154, 3.137),
        (0.165, 3.198),
        (0.16, 3.262),
        (0.147, 3.309),
        (0.119, 3.35),
        (0.079, 3.382),
        (0.048, 3.393),
        (0.034, 3.41),
        (0, 3.41),
    ]
    glass.append(paint(turned(lathe), GLOBE))
    metal.append(
        paint(
            turned(
                ((0, 3.407), (0.038, 3.407), (0.032, 3.422), (0.012, 3.433), (0, 3.433))
            ),
            GREEN,
        )
    )
    for face in (*metal, *glass):
        face.apply_translation((0, grade, 0))


def build_rack(row, materials):
    height = support_heights(row)
    metal = materials[1]
    source = trimesh.load_scene(RACK, process=False).to_geometry()
    grade = max(height) + 0.009
    source.apply_translation((0, grade, 0))
    metal.append(paint(source, GREEN))
    for point in row["supports"]:
        x, n = point["offset_enu_m"]
        bottom = min(point["surface_z_m"], point["terrain_z_m"]) - 0.012
        metal.append(
            paint(
                block((x, (bottom + grade) / 2, -n), (0.104, grade - bottom, 0.06)),
                FOOTING,
            )
        )


def memorial_quad_routes(spec):
    sources = spec.get("memorial_quad_sources")
    if sources is None:
        return []
    quad_path = SCENE / "paving-corridors-l2/surfaces.json"
    apron_path = SCENE / "knight-north-plaza-review/site.json"
    if (
        sha(quad_path) != sources["quad_sha256"]
        or sha(apron_path) != sources["knight_apron_sha256"]
    ):
        raise ValueError("Memorial Quadrangle furnishing supports changed")
    quad, apron = (json.loads(path.read_bytes()) for path in (quad_path, apron_path))
    for descriptor in (quad, apron):
        if sha(SCENE / descriptor["url"]) != descriptor["sha256"]:
            raise ValueError("Memorial Quadrangle paving mesh changed")
    routes = quad["quad_routes"]
    nodes = routes["nodes"]
    edges = [LineString((nodes[a], nodes[b])) for a, b, *_ in routes["edges"]]
    for path in apron["walkable_ground"]["paths"]:
        points = [path["anchor_enu_m"], *path["points_enu_m"]]
        if "end_enu_m" in path:
            points.append(path["end_enu_m"])
        edges.extend(LineString((a, b)) for a, b in zip(points, points[1:]))
    return edges


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(METADATA.read_bytes())
    for path, key in (
        (SCENE / "campus-expanded.glb", "source_presentation_sha256"),
        (SCENE / "manifest.json", "source_manifest_sha256"),
        (SCENE / "heightfield.json", "source_heightfield_sha256"),
        (SCENE / "navigation.json", "source_navigation_sha256"),
        (SCENE / "kalapuya-review/site.json", "source_navigation_patch_sha256"),
        (RACK, "source_rack_sha256"),
    ):
        if sha(path) != spec[key]:
            raise ValueError(f"Source changed: {path}")
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    nodes = graph["nodes_enu_m"]
    site = json.loads((SCENE / "kalapuya-review/site.json").read_bytes())
    patch = site["corridor_patch"]
    removed = set(patch["removed_edges"])
    edges = [
        LineString((nodes[a][:2], nodes[b][:2]))
        for i, (a, b, *_) in enumerate(graph["edges"])
        if i not in removed
    ]
    for path in patch["paths"]:
        points = [nodes[path["anchor"]], *path["points"]]
        edges.extend(LineString((a[:2], b[:2])) for a, b in zip(points, points[1:]))
    if len(edges) != spec["navigation_edge_count"]:
        raise ValueError("Navigation graph edge count changed")
    streets = STRtree(edges)
    quad_routes = STRtree(memorial_quad_routes(spec))
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    roads = STRtree(
        [
            LineString(corridor["centerline_enu_m"]).buffer(corridor["width_m"] / 2)
            for corridor in manifest["corridors"]["features"]
            if corridor["kind"] == "road"
        ]
    )
    handlers = {"bench": build_bench, "lamp": build_lamp, "rack": build_rack}
    parts = [[], [], []]
    occupied = []
    for row in spec["models"]:
        geometry = [[], [], []]
        build = handlers[row["kind"]]
        build(row, geometry)
        e, n = row["position_enu_m"]
        for material in geometry:
            for mesh in material:
                mesh.apply_translation((e, 0, -n))
        all_parts = [mesh for material in geometry for mesh in material]
        complete = trimesh.util.concatenate(all_parts)
        (x0, _, z0), (x1, _, z1) = complete.bounds
        area = box(*row["collision_enu_m"])
        if not area.buffer(0.0001).covers(box(x0, -z1, x1, -z0)):
            raise ValueError(f"{row['id']} exceeds its collision envelope")
        clearance = area.buffer(0.6, join_style="mitre")
        if streets.query(clearance, predicate="intersects").size:
            raise ValueError(f"{row['id']} blocks an existing route")
        if row.get("memorial_quad_registration") and quad_routes.query(
            clearance, predicate="intersects"
        ).size:
            raise ValueError(f"{row['id']} blocks a refined Memorial Quad route")
        if roads.query(clearance, predicate="intersects").size:
            raise ValueError(f"{row['id']} enters the modeled road surface")
        if any(area.distance(other) < 0.84 for other in occupied):
            raise ValueError(f"{row['id']} crowds another furnishing")
        occupied.append(area)
        for batch, meshes in zip(parts, geometry):
            batch.extend(meshes)
    result = trimesh.Scene(base_frame="pilot-furnishings-l2")
    for name, meshes in zip(
        ("furnishings-wood", "furnishings-hardware", "furnishings-glass"), parts
    ):
        mesh = trimesh.util.concatenate(meshes)
        mesh.update_faces(mesh.nondegenerate_faces())
        result.add_geometry(mesh, node_name=name, geom_name=name)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(trimesh.exchange.gltf.export_glb(result, include_normals=True))
    print(
        f"{len(spec['models'])} placements, {len(edges)} route edges, {sha(args.out)}"
    )


if __name__ == "__main__":
    main()
