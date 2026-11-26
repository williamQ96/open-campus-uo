# SPDX-License-Identifier: Apache-2.0
"""Build original site vegetation from recorded stems and reviewed crown widths."""

from importlib import import_module

import numpy as np
import trimesh

branch = import_module("build-moss-street-site-review").branch
BARK = (107, 91, 74)
LEAVES = {
    "maple": ((111, 137, 73), (105, 128, 66), (123, 146, 81)),
    "unknown-deciduous": ((105, 131, 81), (92, 120, 72), (115, 141, 86)),
}


def tree_mesh(record, field, sample_ground):
    east, north = record["position_enu_m"]
    z = sample_ground(field, east, north)
    height = record["modeled_height_m"]
    width, depth = record["modeled_spread_m"]
    colors = LEAVES[record["crown_form"]]
    seed = record["tree_number"]
    radius = min(0.23, height * 0.023)
    shape = np.array([width / 2, depth / 2])
    pieces = []
    crown_base = 0.31 if record["crown_form"] == "maple" else 0.40
    junction = z + height * crown_base
    branch(
        pieces,
        (east, north, z - 0.095),
        (east, north, junction),
        radius,
        radius * 0.65,
        BARK,
    )

    crowns = []
    spokes = 7
    for i in range(spokes):
        heading = 2 * np.pi * i / spokes + (seed % 17) * 0.31
        offset = np.array([np.cos(heading), np.sin(heading)]) * shape * 0.49
        level = height * (0.67 + 0.045 * np.sin(1.86 * i + seed))
        endpoint = (east + offset[0], north + offset[1], z + level - height * 0.10)
        branch(
            pieces,
            (east, north, junction),
            endpoint,
            radius * 0.44,
            radius * 0.14,
            BARK,
        )
        crowns.append((offset, level, 0.42, 0.24))
    crowns.append((np.zeros(2), height * 0.82, 0.51, 0.18))

    meshes = []
    for i, (offset, level, horizontal, vertical) in enumerate(crowns):
        leaf = trimesh.creation.icosphere(subdivisions=1)
        p = leaf.vertices.copy()
        texture = 1 + 0.085 * np.sin(p @ [13.6, 16.3, 11.5] + seed + i * 0.82)
        p *= texture[:, None] * [
            shape[0] * horizontal,
            height * vertical,
            shape[1] * horizontal,
        ]
        p += [offset[0], level, -offset[1]]
        leaf.vertices = p
        leaf.visual.vertex_colors = [*colors[i % len(colors)], 255]
        meshes.append(leaf)
    foliage = trimesh.util.concatenate(meshes)
    p = foliage.vertices.copy()
    p[:, (0, 2)] -= foliage.bounds[:, (0, 2)].mean(axis=0)
    p *= [
        width / foliage.extents[0],
        height / foliage.bounds[1, 1],
        depth / foliage.extents[2],
    ]
    foliage.vertices = p + [east, z, -north]
    return trimesh.util.concatenate([*pieces, foliage])


def site_planting(spec, field, sample_ground):
    trees = spec.get("registered_planting", [])
    meshes = {
        f"campus-tree-{tree['tree_number']}": tree_mesh(tree, field, sample_ground)
        for tree in trees
    }
    if len(meshes) != len(trees):
        raise ValueError("Duplicate registered tree number at one site.")
    return meshes
