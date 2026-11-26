# SPDX-License-Identifier: Apache-2.0
"""Export layered shrubs and fern fronds in the original planting group order."""

import argparse
from collections import Counter
from importlib import import_module
import json
from pathlib import Path

import numpy as np
from shapely.geometry import box
import trimesh

pilot = import_module("build-pilot-trees-l2")
terrain = import_module("build-cascade-exterior-review")
SCENE = pilot.SCENE
SPEC = pilot.source.ROOT / "data/metadata/understory-l2.json"
PACKAGE = "understory-l2"
NODE = "understory-rebuilt"
SOIL = "understory-planting-beds"
PALETTE = np.array([(76, 112, 65), (96, 126, 65), (87, 120, 77), (111, 138, 81)])
SHRUB_FORMS = {
    "low-rounded": (0.45, 0.41, 0.31, 0.43),
    "upright": (0.34, 0.50, 0.39, 0.37),
    "branched": (0.51, 0.53, 0.26, 0.36),
    "mounded": (0.46, 0.48, 0.34, 0.40),
}


def shrub(form, angle, color):
    reach, level, rise, radius = SHRUB_FORMS[form]
    lobes = []
    for i in range(4):
        azimuth = angle + i * np.pi / 2
        scale = 1 + 0.13 * np.sin(i * 2.9 + angle)
        lobes.append(
            pilot.leaf_lobe(
                [
                    reach * np.cos(azimuth),
                    level + 0.11 * np.sin(i + angle),
                    reach * np.sin(azimuth),
                ],
                np.array([radius, rise, radius]) * scale,
                angle + i,
                color + (i - 2) * 4,
            )
        )
    lobes.append(pilot.leaf_lobe([0, 0.7, 0], [0.43, 0.26, 0.4], angle, color + 7))
    wood = []
    bark = pilot.vertex_palette((103, 87, 62))
    for side in (-1, 1):
        pilot.branch(
            wood,
            (0, 0, 0),
            (side * 0.34, 0.14 * side, 0.55),
            0.038,
            0.021,
            bark,
            sections=5,
        )
    return trimesh.util.concatenate([*lobes, *wood])


def fern(angle, color):
    vertices, faces, palette = [], [], []

    def add(a, b, c, tint):
        first = len(vertices)
        vertices.extend([a, b, c])
        faces.append((first, first + 1, first + 2))
        palette.extend([tint] * 3)

    for i in range(8):
        phi = angle + 2 * np.pi * i / 8
        outward = np.array([np.cos(phi), 0, np.sin(phi)])
        across = np.array([-outward[2], 0, outward[0]])
        reach = 0.87 + 0.15 * np.sin(phi * 2.4)
        lift = 0.69 + 0.22 * np.cos(i * 1.95)

        def point(t):
            return outward * (t * reach) + [0, lift * np.sin(t * 2.36), 0]

        for j, t in enumerate(np.linspace(0.12, 0.92, 7)):
            a, b = point(t - 0.095), point(t + 0.09)
            width = 0.19 * np.sin(np.pi * t) * reach
            for side in (-1, 1):
                tip = point(t + 0.035) + across * (side * width) + [0, -0.055, 0]
                add(a, b, tip, color + (i % 3 - 1) * 7 + side * 5)
            rib = across * (0.014 * (1 - t) + 0.002)
            add(a - rib, a + rib, b, color + 13)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.visual.vertex_colors = np.column_stack(
        [
            pilot.vertex_palette(np.asarray(palette)),
            np.full(len(palette), 255, np.uint8),
        ]
    )
    return mesh


def make_plant(spec, index, elevation):
    angle = index * 2.399963229728653
    color = PALETTE[spec["tone"]]
    e, _, south = spec["anchor_gltf_m"]
    width, height, depth = np.asarray(spec["size_m"]) * [0.91, 0.99, 0.91]
    form = spec["form"]
    plant = (
        fern(angle, color + [1, 8, -5]) if form == "fern" else shrub(form, angle, color)
    )
    low, high = plant.bounds
    points = plant.vertices.copy()
    points[:, (0, 2)] -= ((low + high) / 2)[[0, 2]]
    points[:, 1] -= low[1]
    points *= [width, height, depth] / plant.extents
    if cut := spec.get("clearance_cut"):
        points[:, (0, 2)] = pilot.shape_clearance(points[:, (0, 2)], cut)
    plant.vertices = points + [e, elevation - 0.025, south]
    return plant


def bed_surface(path, field):
    source = trimesh.load_scene(path, process=False)
    supporting_surfaces = []
    for name in ("landscape-paving", "landscape-lawn"):
        matrix, geometry = source.graph[name]
        mesh = source.geometry[geometry].copy().apply_transform(matrix)
        supporting_surfaces.append(mesh.triangles)
    triangles = np.concatenate(supporting_surfaces)
    origins = triangles[:, 0][:, [0, 2]]
    bases = (triangles[:, 1:, [0, 2]] - origins[:, None]).transpose(0, 2, 1)
    valid = np.abs(np.linalg.det(bases)) > 1e-8
    triangles = triangles[valid]
    origins = origins[valid]
    inverse = np.linalg.inv(bases[valid])
    horizontal = triangles[:, :, [0, 2]]
    lower, upper = horizontal.min(axis=1), horizontal.max(axis=1)
    heights = triangles[:, :, 1]

    def elevation(east, north):
        point = np.array([east, -north])
        near = ((lower <= point) & (point <= upper)).all(axis=1)
        coords = np.einsum("ijk,ik->ij", inverse[near], point - origins[near])
        weights = np.column_stack((1 - coords.sum(axis=1), coords))
        inside = (weights >= -1e-6).all(axis=1)
        support_height = (weights[inside] * heights[near][inside]).sum(axis=1)
        ground = terrain.sample_ground(field, east, north)
        return max(ground, support_height.max(initial=ground)) + 0.075

    return elevation


def make_soil(beds, elevation):
    sections = []
    for bed in beds:
        west, south, east, north = bed["bounds_enu_m"]
        columns = np.linspace(west - 0.08, east + 0.08, 2 + round(east - west))
        rows = np.linspace(south - 0.08, north + 0.08, 2 + round(north - south))
        profile = box(west, south, east, north).buffer(0.07, quad_segs=3)
        bottom = min(elevation(*xy) for xy in profile.exterior.coords) - 0.34
        for left, right in zip(columns, columns[1:]):
            for front, back in zip(rows, rows[1:]):
                area = profile.intersection(box(left, front, right, back))
                for plan in terrain.sections(area):
                    sections.append(
                        terrain.shell(
                            plan, bottom, elevation, (51, 38, 25), (68, 50, 34)
                        )
                    )
    return trimesh.util.concatenate(sections)


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
        digest(SCENE / url) == sha for url, sha in spec["source_recipes"].items()
    )
    entries = spec["plants"]
    assert [(r["layer"], r["index"]) for r in entries] == [
        (name, index)
        for name, (count, _, _) in spec["source_ranges"].items()
        for index in range(count)
    ]
    field = json.loads((SCENE / manifest["heightfield_url"]).read_bytes())
    elevation = bed_surface(SCENE / config["asset_url"], field)
    models, ranges, raw = [], [], {}
    lifts = {}
    nverts = nindices = 0
    for ordinal, entry in enumerate(entries):
        east, ground, south = entry["anchor_gltf_m"]
        height = elevation(east, -south) if entry.get("site") else ground
        if entry.get("site"):
            lifts[entry["index"]] = round(float(height - ground), 4)
        model = make_plant(entry, ordinal, height)
        assert np.isfinite(model.vertices).all() and model.area > 0
        assert (
            model.extents[[0, 2]] <= np.asarray(entry["size_m"])[[0, 2]] + 1e-5
        ).all()
        nverts += len(model.vertices)
        nindices += len(model.faces) * 3
        ranges.append([nverts, nindices, not entry.get("retired", False)])
        models.append(model)
        if args.triangles:
            raw[f"{entry['layer']}:{entry['index']}"] = model.triangles.astype(
                np.float32
            )
    if args.triangles:
        np.savez_compressed(args.triangles, **raw)
    stage = trimesh.Scene(base_frame=PACKAGE)
    stage.add_geometry(trimesh.util.concatenate(models), node_name=NODE, geom_name=NODE)
    stage.add_geometry(
        make_soil(spec["soil_beds"], elevation), node_name=SOIL, geom_name=SOIL
    )

    def annotate(gltf):
        gltf["materials"] = [
            {
                "doubleSided": True,
                "pbrMetallicRoughness": {"metallicFactor": 0, "roughnessFactor": 0.96},
            }
        ]
        for mesh in gltf["meshes"]:
            mesh["primitives"][0]["material"] = 0
        for node in gltf["nodes"]:
            if node.get("name") in (NODE, SOIL):
                node["extras"] = {"asset_kind": "landscape-detail"}

    output = args.stage or SCENE / PACKAGE
    output.mkdir(exist_ok=True, parents=True)
    asset = output / "plants.glb"
    asset.write_bytes(
        trimesh.exchange.gltf.export_glb(
            stage, include_normals=True, tree_postprocessor=annotate
        )
    )
    descriptor = output / "plants.json"
    payload = {
        "source_art_sha256": spec["source_art_sha256"],
        "source_recipes": spec["source_recipes"],
        "source_ranges": spec["source_ranges"],
        "ranges": ranges,
        "url": f"{PACKAGE}/plants.glb",
        "sha256": digest(asset),
    }
    pilot.write(descriptor, payload, compact=True)
    if args.stage is None:
        config["understory_l2"] = {
            "url": f"{PACKAGE}/plants.json",
            "sha256": digest(descriptor),
        }
        pilot.write(config_path, config)
    report = {
        "entries": len(entries),
        "forms": dict(Counter(r["form"] for r in entries)),
        "triangles": nindices // 3,
        "vertices": nverts,
        "planting_base_lifts_m": lifts,
        "bytes": asset.stat().st_size,
        "sha256": payload["sha256"],
        "descriptor_sha256": digest(descriptor),
    }
    pilot.write(args.audit, report)
    print(report)


if __name__ == "__main__":
    main()
