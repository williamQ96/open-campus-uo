# SPDX-License-Identifier: Apache-2.0
"""Export exact pilot tree and understory triangle spans for reviewed locations."""

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import struct

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "apps/web-preview/public/scene"
PARAMETERS = ROOT / "data/metadata/pilot-tree-clearance.json"
OUTPUT = SCENE / "pilot-green-tree-clearance.json"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def mesh_arrays(model, bin_chunk, primitive):
    def accessor(i, dtype, width):
        a = model["accessors"][i]
        view = model["bufferViews"][a["bufferView"]]
        assert not a.get("sparse") and not view.get("byteStride")
        offset = view.get("byteOffset", 0) + a.get("byteOffset", 0)
        return np.frombuffer(
            bin_chunk, dtype=dtype, count=a["count"] * width, offset=offset
        )

    pos = primitive["attributes"]["POSITION"]
    assert model["accessors"][pos]["componentType"] == 5126
    index = primitive["indices"]
    id_type = {5123: "<u2", 5125: "<u4"}[model["accessors"][index]["componentType"]]
    return accessor(pos, "<f4", 3).reshape(-1, 3), accessor(index, id_type, 1).reshape(
        -1, 3
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree-input", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--spec", type=Path, default=PARAMETERS)
    parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    parameters = json.loads(args.spec.read_bytes())
    assert digest(args.tree_input) == parameters["source_tree_input_sha256"]
    trees = json.loads(args.tree_input.read_bytes())["trees"]
    assert len(trees) == 300
    config_path = SCENE / "presentation.json"
    settings = json.loads(config_path.read_bytes())
    source = SCENE / settings["asset_url"]
    assert (
        digest(source)
        == settings["asset_sha256"]
        == parameters["source_presentation_sha256"]
    )

    raw = source.read_bytes()
    length, typ = struct.unpack_from("<I4s", raw, 12)
    assert typ == b"JSON"
    model = json.loads(raw[20 : 20 + length])
    assert raw[24 + length : 28 + length] == b"BIN\0"
    binary = memoryview(raw)[28 + length :]
    selected = {item["index"]: item for item in parameters["adjustments"]}
    assert len(selected) == len(parameters["adjustments"]) and selected.keys() <= set(
        range(300)
    )
    assert not {60, 216, 273} & selected.keys()
    parts = {}
    for group in ("vegetation", "understory"):
        obj = next(node for node in model["nodes"] if node.get("name") == group)
        primitives = model["meshes"][obj["mesh"]]["primitives"]
        for i, primitive in enumerate(primitives, 1):
            material = model["materials"][primitive["material"]]["name"]
            if group == "understory" and material != "shrub":
                continue
            name = f"{group}_{i}"
            pos, tri = mesh_arrays(model, binary, primitive)
            parts[material] = (group, name, pos, tri)

    offsets = defaultdict(int)
    ranges = defaultdict(list)

    def add(material, offset, count, item, radius, paired=False):
        group, name, pos, tri = parts[material]
        region = tri[offset : offset + count].ravel()
        e, n = item["east_north_m"]
        if paired:
            e, n = e + 1.1, n - 0.5
        assert len(region) == count * 3
        assert np.max(abs(pos[region, 0] - e)) <= radius
        assert np.max(abs(pos[region, 2] + n)) <= radius
        signatures = [int(region[i]) for i in (0, count * 3 // 2, count * 3 - 1)]
        ranges[material].append([offset, offset + count, *signatures])

    for i, (e, n, height, is_conifer, tone) in enumerate(trees):
        leaf, count = (
            ("evergreen", 96)
            if is_conifer
            else (
                ("leaf", "leaf-light", "evergreen")[tone],
                432,
            )
        )
        patches = (("trunk", 24 if is_conifer else 48), (leaf, count))
        item = selected.get(i)
        if item:
            assert item["east_north_m"] == [e, n]
        for material, size in patches:
            start = offsets[material]
            if item:
                add(material, start, size, item, height * 0.60)
            offsets[material] += size
        if item and item["paired_understory"]:
            assert i % 5 == 0
            add("shrub", (i // 5) * 108, 108, item, 1.71, paired=True)
    assert all(
        offsets[k] == len(parts[k][3])
        for k in ("trunk", "leaf", "evergreen", "leaf-light")
    )
    description = []
    removed = {}
    for material, spans in ranges.items():
        group, name, pos, tri = parts[material]
        assert all(left[1] <= right[0] for left, right in zip(spans, spans[1:]))
        removed[name] = sum(span[1] - span[0] for span in spans)
        description.append(
            dict(
                group=group,
                name=name,
                vertices=len(pos),
                triangles=len(tri),
                spans=spans,
            )
        )
    result = {
        "version": 1,
        "operation": "pilot-tree-triangle-suppression-v1",
        "base_asset_sha256": settings["asset_sha256"],
        "suppressed_trees": len(selected),
        "suppressed_understory": sum(
            item["paired_understory"] for item in selected.values()
        ),
        "meshes": description,
    }
    output = args.stage or OUTPUT
    output.write_text(
        json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n"
    )
    sha = digest(output)
    entry = next(
        (
            entry
            for entry in settings["additional_tree_suppressions"]
            if entry["url"] == OUTPUT.name
        ),
        None,
    )
    if args.stage is None and entry and entry["sha256"] != sha:
        stats = settings["stats"]
        stats["trees"] += entry["suppressed_trees"] - len(selected)
        entry.update(sha256=sha, suppressed_trees=len(selected))
        config_path.write_text(
            json.dumps(settings, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    audit = {
        "recipe_sha256": sha,
        "trees_removed": len(selected),
        "understory_removed": result["suppressed_understory"],
        "removed_triangles": removed,
    }
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
