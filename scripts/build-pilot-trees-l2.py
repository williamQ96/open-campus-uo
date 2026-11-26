# SPDX-License-Identifier: Apache-2.0
"""Build the pilot canopy and branch geometry at the retained tree anchors."""

import argparse
from collections import Counter
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path

import numpy as np
import trimesh

source = import_module("build-pilot-tree-clearance")
branch = import_module("build-site-planting").branch
SPEC = source.ROOT / "data/metadata/pilot-trees-l2.json"
SCENE = source.SCENE
PACKAGE = "pilot-trees-l2"
FORMS = {
    "rounded": (0.45, 0.48, 0.25, 0.33),
    "vase": (0.54, 0.54, 0.18, 0.39),
    "low-spreading": (0.6, 0.39, 0.31, 0.31),
    "birch": (0.47, 0.45, 0.27, 0.38),
}
GREENS = np.array([(115, 143, 78), (135, 153, 90), (77, 113, 73)])


def vertex_palette(srgb):
    color = np.clip(srgb, 0, 255) / 255
    linear = np.where(color <= 0.04045, color / 12.92, ((color + 0.055) / 1.055) ** 2.4)
    # glTF vertex colors store linear values.
    return np.rint(linear * 255).astype(np.uint8)


def foliage_color(mesh, color, angle):
    xyz = mesh.vertices
    value = np.sin(xyz @ [3.4, 2.9, 4.1] + angle) * 6
    value += 7 * (xyz[:, 1] - xyz[:, 1].mean()) / max(mesh.extents[1], 0.01)
    colors = vertex_palette(color + value[:, None])
    mesh.visual.vertex_colors = np.column_stack(
        [colors, np.full(len(colors), 255, dtype=np.uint8)]
    )


def leaf_lobe(center, radii, phase, color, top=False):
    mesh = trimesh.creation.icosphere(subdivisions=int(top))
    points = mesh.vertices.copy()
    nudge = 1 + 0.12 * np.sin(points @ [4.2, 6.8, 5.3] + phase)
    mesh.vertices = center + points * nudge[:, None] * radii
    foliage_color(mesh, color, phase)
    return mesh


def branching_crown(form, phase, color):
    reach, ring, rise, radius = FORMS[form]
    crown = []
    for i in range(7):
        bearing = phase + i * 2 * np.pi / 7 + 0.13 * np.sin(i * 2)
        land = reach * (0.91 + 0.09 * np.cos(i * 2.12))
        x, z = np.array([np.cos(bearing), np.sin(bearing)]) * land
        h = ring + 0.12 * np.sin(phase + 1.65 * i)
        crown.append(
            leaf_lobe(
                (x, h, z),
                (radius + 0.15, rise, radius + 0.11),
                phase + i,
                color + (i % 3 - 1) * 6,
            )
        )
    crown.append(
        leaf_lobe((0.05, 0.72, -0.07), (0.48, 0.28, 0.42), phase, color + 6, top=True)
    )
    return trimesh.util.concatenate(crown)


def conifer_crown(form, phase, color):
    if form == "spire":
        rings = [
            (0, 0.18),
            (0.05, 0.83),
            (0.13, 0.59),
            (0.21, 0.75),
            (0.32, 0.47),
            (0.39, 0.57),
            (0.55, 0.35),
            (0.63, 0.42),
            (0.76, 0.20),
            (0.83, 0.23),
            (1, 0.015),
        ]
    else:
        rings = [
            (0, 0.24),
            (0.04, 1),
            (0.11, 0.68),
            (0.19, 0.87),
            (0.30, 0.54),
            (0.38, 0.69),
            (0.50, 0.48),
            (0.59, 0.53),
            (0.73, 0.31),
            (0.77, 0.34),
            (1, 0.015),
        ]
    sides = 11
    angles = np.arange(sides) * 2 * np.pi / sides + phase
    vertices = []
    for j, (height, width) in enumerate(rings):
        angle = angles + j * 0.07
        lobes = width * (1 + 0.13 * np.sin(5 * angle + j))
        vertices.extend(
            np.column_stack(
                [
                    lobes * np.cos(angle),
                    height + 0.013 * np.cos(angles * 2 + j),
                    lobes * np.sin(angle),
                ]
            )
        )
    faces = []
    for row in range(len(rings) - 1):
        for i in range(sides):
            a, b = row * sides + i, row * sides + (i + 1) % sides
            faces.extend(((a, a + sides, b), (b, a + sides, b + sides)))
    limit = (len(rings) - 1) * sides
    faces.extend((0, i, i + 1) for i in range(1, sides - 1))
    faces.extend((limit, limit + i + 1, limit + i) for i in range(1, sides - 1))
    canopy = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    foliage_color(canopy, color - [24, 20, 11], phase)
    return canopy


def shape_clearance(points, constraint):
    direction = np.asarray(constraint["direction_xz"], dtype=float)
    direction /= np.linalg.norm(direction)
    distance = points @ direction
    limit = constraint["max_depth_m"]
    if distance.max() <= limit:
        return points
    return points - np.maximum(0, distance)[:, None] * direction * (
        1 - limit / distance.max()
    )


def make_tree(spec):
    e, base, south = spec["origin_gltf_m"]
    width, depth = np.asarray(spec["crown_extents_m"])
    height = spec["standing_height_m"]
    fraction = spec["crown_bottom_fraction"]
    form = spec["crown_form"]
    phase = spec["index"] * 2.399963229728653
    color = GREENS[spec["tone"]]
    evergreen = form in ("spire", "tiered")
    canopy = (
        conifer_crown(form, phase, color)
        if evergreen
        else branching_crown(form, phase, color)
    )
    p = canopy.vertices.copy()
    bounds = canopy.bounds
    p[:, (0, 2)] -= bounds.mean(axis=0)[[0, 2]]
    p[:, (0, 2)] *= [width * 0.96 / canopy.extents[0], depth * 0.96 / canopy.extents[2]]
    p[:, 1] = height * (
        fraction + (1 - fraction) * (p[:, 1] - bounds[0, 1]) / canopy.extents[1]
    )
    cut = spec.get("clearance_cut")
    if cut:
        p[:, (0, 2)] = shape_clearance(p[:, (0, 2)], cut)
    canopy.vertices = p + [e, base, south]

    woody = []
    tone = vertex_palette((117, 100, 84) if form != "birch" else (165, 143, 112))
    radius = min(0.36, width * 0.030, height * 0.035)
    n = -south
    shift = radius * np.array([np.cos(phase), np.sin(phase)])
    kink = (e + shift[0], n + shift[1], base + height * (0.29 if evergreen else 0.36))
    branch(woody, (e, n, base - 0.035), kink, radius, radius * 0.68, tone, sections=7)
    top = (
        e + shift[0] * 0.68,
        n + shift[1] * 0.68,
        base + height * (0.91 if evergreen else 0.68),
    )
    branch(woody, kink, top, radius * 0.70, radius * 0.18, tone, sections=7)
    if not evergreen:
        for k in range(5):
            angle = phase + 2 * np.pi * k / 5
            end = (
                e + width * 0.21 * np.cos(angle),
                n - depth * 0.21 * np.sin(angle),
                base + height * (0.64 + 0.085 * np.sin(angle)),
            )
            branch(woody, kink, end, radius * 0.42, radius * 0.12, tone, sections=6)
    stem = trimesh.util.concatenate(woody)
    if cut:
        vertices = stem.vertices.copy()
        center = np.array([e, south])
        vertices[:, (0, 2)] = (
            shape_clearance(vertices[:, (0, 2)] - center, cut) + center
        )
        stem.vertices = vertices
    return stem, canopy


def write(path, value, compact=False):
    path.write_text(
        json.dumps(
            value,
            indent=None if compact else 2,
            separators=(",", ":") if compact else None,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--triangles", type=Path)
    args = parser.parse_args()
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    assert (
        source.digest(SCENE / manifest["heightfield_url"])
        == spec["source_heightfield_sha256"]
    )
    assert (
        source.digest(SCENE / config["asset_url"])
        == spec["source_art_sha256"]
        == config["asset_sha256"]
    )
    assert all(
        source.digest(SCENE / url) == digest
        for url, digest in spec["source_placement_recipes"].items()
    )
    trees = spec["trees"]
    assert len(trees) == 273
    assert {row["index"] for row in trees} == set(range(300)) - set(
        spec["retired_indices"]
    )
    wood, foliage, samples = [], [], {}
    for row in trees:
        stem, crown = make_tree(row)
        assert stem.area > 0 and crown.area > 0
        assert np.isfinite(stem.vertices).all() and np.isfinite(crown.vertices).all()
        assert (
            abs(crown.bounds[1, 1] - row["origin_gltf_m"][1] - row["standing_height_m"])
            < 1e-5
        )
        assert (crown.extents[[0, 2]] <= np.asarray(row["crown_extents_m"])).all()
        wood.append(stem)
        foliage.append(crown)
        if args.triangles:
            samples[f"tree_{row['index']}"] = np.concatenate(
                [stem.triangles, crown.triangles]
            ).astype(np.float32)
    if args.triangles:
        np.savez_compressed(args.triangles, **samples)
    layers = {
        "pilot-trees-wood": trimesh.util.concatenate(wood),
        "pilot-trees-foliage": trimesh.util.concatenate(foliage),
    }
    model = trimesh.Scene(base_frame=PACKAGE)
    for name, mesh in layers.items():
        model.add_geometry(mesh, node_name=name, geom_name=name)

    def annotate(gltf):
        gltf["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.0, "roughnessFactor": 0.94}}
        ]
        for mesh in gltf["meshes"]:
            mesh["primitives"][0]["material"] = 0
        for node in gltf["nodes"]:
            if node.get("name") in layers:
                node["extras"] = {"asset_kind": "vegetation"}

    output = args.stage or SCENE / PACKAGE
    output.mkdir(parents=True, exist_ok=True)
    glb = output / "trees.glb"
    glb.write_bytes(
        trimesh.exchange.gltf.export_glb(
            model, include_normals=True, tree_postprocessor=annotate
        )
    )
    payload = {
        "source_art_sha256": spec["source_art_sha256"],
        "source_placement_recipes": spec["source_placement_recipes"],
        "source_groups": spec["source_groups"],
        "url": f"{PACKAGE}/trees.glb",
        "sha256": sha256(glb.read_bytes()).hexdigest(),
        "tree_count": len(trees),
        "active_recipes": {"registered": 11, "removed": 25},
    }
    descriptor = output / "trees.json"
    write(descriptor, payload, compact=True)
    if args.stage is None:
        config["pilot_trees_l2"] = {
            "url": f"{PACKAGE}/trees.json",
            "sha256": source.digest(descriptor),
        }
        write(config_path, config)
    result = {
        "trees": len(trees),
        "documented_stems": sum("tree_number" in row for row in trees),
        "forms": dict(Counter(row["crown_form"] for row in trees)),
        "triangles": {name: len(mesh.faces) for name, mesh in layers.items()},
        "bytes": glb.stat().st_size,
        "sha256": payload["sha256"],
        "descriptor_sha256": source.digest(descriptor),
    }
    write(args.audit, result)
    print(result)


if __name__ == "__main__":
    main()
