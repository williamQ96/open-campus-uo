# SPDX-License-Identifier: Apache-2.0
"""Export the lightweight background trees in stable source-index order."""

import argparse
from collections import Counter
from importlib import import_module
import json
from pathlib import Path

import numpy as np
import trimesh

pilot = import_module("build-pilot-trees-l2")
SCENE = pilot.SCENE
SPEC = pilot.source.ROOT / "data/metadata/context-trees-l2.json"
PACKAGE = "context-trees-l2"
NODE = "context-trees-rebuilt"
PALETTE = np.array([(103, 133, 90), (131, 149, 87), (75, 115, 85), (114, 146, 98)])
CROWN_FORMS = {
    "low-spreading": (0.54, 0.40, 0.30),
    "rounded": (0.41, 0.46, 0.34),
    "vase": (0.47, 0.52, 0.23),
    "oval": (0.30, 0.48, 0.35),
}


def make_tree(spec):
    index = spec["index"]
    phase = index * 2.399963229728653
    form = spec["crown_form"]
    reach, level, rise = CROWN_FORMS[form]
    color = PALETTE[spec["tone"]]
    e, base, south = spec["origin_gltf_m"]
    width, depth = spec["crown_extents_m"]
    height = spec["standing_height_m"]
    bottom = spec["crown_bottom_fraction"]
    cut = spec.get("clearance_cut")
    groups = []
    for i in range(3):
        bearing = phase + i * 2 * np.pi / 3
        x, z = (reach * np.cos(bearing), reach * np.sin(bearing))
        variation = 0.08 * np.sin(index + i * 1.7)
        groups.append(
            pilot.leaf_lobe(
                (x, level + variation, z),
                (0.46 + variation, rise, 0.42),
                phase + i,
                color + (i - 1) * 5,
            )
        )
    groups.append(
        pilot.leaf_lobe((-0.06, 0.73, 0.04), (0.43, 0.31, 0.39), phase, color + 5)
    )
    canopy = trimesh.util.concatenate(groups)
    points = canopy.vertices.copy()
    minimum, maximum = canopy.bounds
    points[:, (0, 2)] -= ((minimum + maximum) / 2)[[0, 2]]
    points[:, (0, 2)] *= np.asarray([width, depth]) * 0.97 / canopy.extents[[0, 2]]
    points[:, 1] = height * (
        bottom + (1 - bottom) * (points[:, 1] - minimum[1]) / canopy.extents[1]
    )
    if cut:
        points[:, (0, 2)] = pilot.shape_clearance(points[:, (0, 2)], cut)
    canopy.vertices = points + [e, base, south]

    radius = min(0.29, 0.024 * height)
    shift = radius * 1.08 * np.array([np.cos(phase), np.sin(phase)])
    bend = (e + shift[0], -south + shift[1], base + height * 0.35)
    branch = pilot.branch
    woody = []
    bark = pilot.vertex_palette((112, 92, 71))
    branch(
        woody, (e, -south, base - 0.045), bend, radius, radius * 0.67, bark, sections=6
    )
    for side in (0, 1):
        angle = phase + side * 2.33
        target = (
            e + width * 0.18 * np.cos(angle),
            -south + depth * 0.18 * np.sin(angle),
            base + height * (0.62 + 0.08 * side),
        )
        branch(woody, bend, target, radius * 0.54, radius * 0.11, bark, sections=5)
    stem = trimesh.util.concatenate(woody)
    if cut:
        points = stem.vertices.copy()
        points[:, (0, 2)] = pilot.shape_clearance(
            points[:, (0, 2)] - [e, south], cut
        ) + [e, south]
        stem.vertices = points
    return trimesh.util.concatenate([stem, canopy])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--triangles", type=Path)
    args = parser.parse_args()
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    spec = json.loads(SPEC.read_bytes())
    digest = pilot.source.digest
    assert (
        digest(SCENE / config["asset_url"])
        == spec["source_art_sha256"]
        == config["asset_sha256"]
    )
    assert (
        digest(SCENE / manifest["heightfield_url"]) == spec["source_heightfield_sha256"]
    )
    assert all(
        digest(SCENE / url) == sha for url, sha in spec["source_trunk_recipes"].items()
    )
    entries = spec["trees"]
    assert [entry["index"] for entry in entries] == list(range(300))
    meshes, ranges, raw_triangles = [], [], {}
    indices = vertices = 0
    for entry in entries:
        tree = make_tree(entry)
        assert tree.area > 0 and np.isfinite(tree.vertices).all()
        assert (
            tree.extents[[0, 2]] <= np.asarray(entry["crown_extents_m"]) + 0.00001
        ).all()
        assert (
            abs(
                tree.bounds[1, 1]
                - entry["origin_gltf_m"][1]
                - entry["standing_height_m"]
            )
            < 1e-5
        )
        vertices += len(tree.vertices)
        indices += len(tree.faces) * 3
        ranges.append([vertices, indices, entry["source_base_m"]])
        meshes.append(tree)
        if args.triangles:
            raw_triangles[f"tree_{entry['index']}"] = tree.triangles.astype(np.float32)
    if args.triangles:
        np.savez_compressed(args.triangles, **raw_triangles)
    model = trimesh.Scene(base_frame=PACKAGE)
    model.add_geometry(trimesh.util.concatenate(meshes), node_name=NODE, geom_name=NODE)

    def annotate(gltf):
        gltf["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.0, "roughnessFactor": 0.95}}
        ]
        gltf["meshes"][0]["primitives"][0]["material"] = 0
        for node in gltf["nodes"]:
            if node.get("name") == NODE:
                node["extras"] = {"asset_kind": "landscape-detail"}

    output = args.stage or SCENE / PACKAGE
    output.mkdir(parents=True, exist_ok=True)
    asset = output / "trees.glb"
    asset.write_bytes(
        trimesh.exchange.gltf.export_glb(
            model, include_normals=True, tree_postprocessor=annotate
        )
    )
    descriptor = output / "trees.json"
    payload = {
        "source_art_sha256": spec["source_art_sha256"],
        "source_trunk_recipes": spec["source_trunk_recipes"],
        "url": f"{PACKAGE}/trees.glb",
        "sha256": digest(asset),
        "ranges": ranges,
    }
    pilot.write(descriptor, payload, compact=True)
    if args.stage is None:
        config["context_trees_l2"] = {
            "url": f"{PACKAGE}/trees.json",
            "sha256": digest(descriptor),
        }
        pilot.write(config_path, config)
    report = {
        "trees": len(entries),
        "forms": dict(Counter(row["crown_form"] for row in entries)),
        "triangles": indices // 3,
        "vertices": vertices,
        "bytes": asset.stat().st_size,
        "sha256": payload["sha256"],
        "descriptor_sha256": digest(descriptor),
    }
    pilot.write(args.audit, report)
    print(report)


if __name__ == "__main__":
    main()
