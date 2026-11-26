# SPDX-License-Identifier: Apache-2.0
"""Fit reviewed pilot tree vertices to surveyed stems and recorded crown dimensions."""

import argparse
from collections import defaultdict
from importlib import import_module
import json
from pathlib import Path
import struct

import numpy as np

from_source = import_module("build-pilot-tree-clearance")
sample_ground = import_module("build-cascade-exterior-review").sample_ground
SCENE = from_source.SCENE
PARAMETERS = from_source.ROOT / "data/metadata/registered-pilot-trees.json"
OUTPUT = SCENE / "registered-pilot-trees.json"


def vertex_runs(ids):
    return [
        [int(run[0]), int(run[-1]) + 1]
        for run in np.split(ids, np.flatnonzero(np.diff(ids) != 1) + 1)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree-input", required=True, type=Path)
    parser.add_argument("--spec", type=Path, default=PARAMETERS)
    parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_bytes())
    config = json.loads((SCENE / "presentation.json").read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    asset = SCENE / config["asset_url"]
    assert from_source.digest(args.tree_input) == spec["source_tree_input_sha256"]
    assert from_source.digest(field_path) == spec["source_heightfield_sha256"]
    assert (
        from_source.digest(asset)
        == config["asset_sha256"]
        == spec["source_presentation_sha256"]
    )
    field = json.loads(field_path.read_bytes())
    trees = json.loads(args.tree_input.read_bytes())["trees"]
    assert len(trees) == 300

    raw = asset.read_bytes()
    length, kind = struct.unpack_from("<I4s", raw, 12)
    assert kind == b"JSON" and raw[24 + length : 28 + length] == b"BIN\0"
    model = json.loads(raw[20 : 20 + length])
    binary = memoryview(raw)[28 + length :]
    node = next(node for node in model["nodes"] if node.get("name") == "vegetation")
    assert not {"matrix", "translation", "rotation", "scale"} & node.keys()
    meshes = {}
    for i, primitive in enumerate(model["meshes"][node["mesh"]]["primitives"], 1):
        material = model["materials"][primitive["material"]]["name"]
        meshes[material] = (
            f"vegetation_{i}",
            *from_source.mesh_arrays(model, binary, primitive),
        )

    selected = {item["index"]: item for item in spec["trees"]}
    suppressed = json.loads(from_source.PARAMETERS.read_bytes())["adjustments"]
    assert len(selected) == len(spec["trees"])
    excluded = {60, 216, 273, *(item["index"] for item in suppressed)}
    assert not (excluded & selected.keys())
    offsets = defaultdict(int)
    edits = []
    for i, (e, n, height, conifer, tone) in enumerate(trees):
        leaf = "evergreen" if conifer else ("leaf", "leaf-light", "evergreen")[tone]
        spans = (("trunk", 24 if conifer else 48), (leaf, 96 if conifer else 432))
        item = selected.get(i)
        parts, points = [], []
        for material, size in spans:
            a = offsets[material]
            b = offsets[material] = a + size
            if not item:
                continue
            name, pos, tri = meshes[material]
            assert len(tri[a:b]) == size
            ids = np.unique(tri[a:b])
            assert not np.isin(ids, tri[:a]).any() and not np.isin(ids, tri[b:]).any()
            vertices = pos[ids].astype(float)
            assert np.max(abs(vertices[:, [0, 2]] - [e, -n])) <= height * 0.60
            points.append(vertices)
            samples = (0, len(ids) // 2, len(ids) - 1)
            parts.append(
                dict(
                    name=name,
                    vertices=len(pos),
                    runs=vertex_runs(ids),
                    anchors=[[int(ids[j]), *vertices[j].tolist()] for j in samples],
                )
            )
        if not item:
            continue
        assert not conifer and item["old_enu_m"] == [e, n]
        trunk, crown = points
        base = float(trunk[:, 1].min())
        crown_radius = float(np.max(abs(crown[:, [0, 2]] - [e, -n])))
        stature = float(np.concatenate(points)[:, 1].max()) - base
        east, north = item["new_enu_m"]
        width_scale = item["canopy_width_m"] / (2 * crown_radius)
        height_scale = item["standing_height_m"] / stature
        edits.append(
            dict(
                index=i,
                origin=[e, base, -n],
                target=[east, sample_ground(field, east, north), -north],
                scale=[width_scale, height_scale, width_scale],
                parts=parts,
            )
        )
    assert len(edits) == len(selected)
    assert all(offsets[k] == len(meshes[k][2]) for k in offsets)
    recipe = dict(
        version=1,
        operation="registered-pilot-tree-fit-v1",
        base_asset_sha256=config["asset_sha256"],
        trees=edits,
    )
    output = args.stage or OUTPUT
    output.write_text(
        json.dumps(recipe, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"{len(edits)} fits, {from_source.digest(output)}")


if __name__ == "__main__":
    main()
