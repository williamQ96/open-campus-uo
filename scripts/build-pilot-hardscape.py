# SPDX-License-Identifier: Apache-2.0
"""Build the pilot stair, amphitheater and raised planter review."""

import argparse
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path
import struct

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

geometry = import_module("build-cascade-exterior-review")
tools = import_module("build-athletic-exterior-review")
decode = import_module("build-pilot-tree-clearance").mesh_arrays
ROOT, SCENE = geometry.ROOT, geometry.SCENE
PACKAGE = "pilot-hardscape-review"
STONE = (176, 170, 151)
COURT = (165, 160, 148)
TRIM = (185, 173, 146)
BRICK = (128, 92, 67)
IRON = (67, 75, 69)
LAWN = (130, 145, 91)


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def write(path, value, compact=False):
    text = json.dumps(
        value,
        ensure_ascii=False,
        indent=None if compact else 2,
        separators=(",", ":") if compact else None,
    )
    path.write_text(text + "\n", encoding="utf-8", newline="\n")


def enu_arc(center, inner, outer, start, stop):
    angles = np.deg2rad(
        np.linspace(start, stop, max(6, round((stop - start) / 2.8)) + 1)
    )
    points = np.column_stack((np.cos(angles), np.sin(angles)))
    return orient(
        Polygon(
            [
                *(np.asarray(center) + outer * points),
                *(np.asarray(center) + inner * points[::-1]),
            ]
        )
    )


def ground_shell(parts, area, field, lift, wall, cap):
    def top(e, n):
        return geometry.sample_ground(field, e, n) + lift

    for plan in geometry.sections(area):
        cutoff = min(top(*xy) for xy in plan.exterior.coords) - lift - 0.32
        parts.append(geometry.shell(plan, cutoff, top, wall, cap))


def add_treads(walkable, detail, flight, field):
    center = flight["center_east"]
    half = flight["width_m"] / 2
    bottom, landing, end = (
        flight[k] for k in ("bottom_north", "landing_north", "threshold_north")
    )
    height, lower = flight["landing_y"], flight["lowest_y"]
    stone = flight["stone"]
    if "apron_north" in flight:
        apron = np.linspace(flight["apron_north"], bottom, 5)
        for front, back in zip(apron, apron[1:]):
            ground_shell(
                walkable,
                box(center - half, back, center + half, front),
                field,
                0.065,
                stone,
                COURT,
            )
    n = np.linspace(bottom, landing, flight["treads"] + 1)
    levels = np.linspace(lower, height, len(n))
    for i, (front, back) in enumerate(zip(n, n[1:])):
        top = levels[i + 1] - 0.009 if i + 1 < len(n) - 1 else height
        span = box(center - half, back - 0.006, center + half, front)
        tools.flat(walkable, span, min(lower - 0.24, top - 0.28), top, stone)
        strip = box(
            center - half + 0.02, front - 0.043, center + half - 0.02, front - 0.001
        )
        tools.flat(detail, strip, top - 0.028, top + 0.002, TRIM)
    tools.flat(
        walkable,
        box(center - half, end, center + half, landing + 0.01),
        min(lower - 0.25, height - 0.3),
        height,
        stone,
    )
    cap = flight["cap_width"]
    for side in (-1, 1):
        e = center + half * side
        edge = box(e - cap / 2, end + 0.12, e + cap / 2, bottom - 0.01)
        for piece, top in zip(
            (
                box(e - cap / 2, back, e + cap / 2, front)
                for front, back in zip(n, n[1:])
            ),
            levels[1:],
        ):
            tools.flat(detail, piece, lower - 0.21, top + 0.19, stone)
        tools.flat(
            detail,
            edge.intersection(box(e - cap, end, e + cap, landing)),
            lower - 0.25,
            height + 0.19,
            stone,
        )
    rail_boxes = []
    for e in flight["rails_east"]:
        for side in np.linspace(0.08, 0.92, 5):
            north = bottom + side * (landing - bottom)
            z = lower + side * (height - lower)
            tools.beam(detail, (e, north, z - 0.09), (e, north, z + 0.92), 0.040, IRON)
            foot = box(e - 0.064, north - 0.062, e + 0.064, north + 0.062)
            tools.flat(detail, foot, z - 0.074, z - 0.045, IRON)
        tools.beam(
            detail,
            (e, bottom + 0.025, lower + 0.90),
            (e, landing - 0.28, height + 0.94),
            0.050,
            IRON,
        )
        tools.beam(
            detail,
            (e, landing - 0.275, height + 0.94),
            (e, landing - 0.70, height + 0.94),
            0.049,
            IRON,
        )
        rail_boxes.append(box(e - 0.045, landing - 0.65, e + 0.045, bottom - 0.23))
    readings = [
        [center, round((front + back) / 2, 4), round(float(z), 4)]
        for front, back, z in zip(n, n[1:], levels[1:])
    ]
    check = {
        "id": flight["name"],
        "treads": len(n) - 1,
        "rise": round(height - lower, 4),
        "bottom_at_center_gap": round(
            lower - geometry.sample_ground(field, center, bottom), 4
        ),
        "check_points": readings,
    }
    return rail_boxes, check


def amphitheater(walkable, detail, data, field):
    center = data["center_enu_m"]
    floor = Point(*center).buffer(data["paving_radius_m"], quad_segs=32)
    # Tessellate the court before sampling so the current curved grade is retained.
    tile_loop = np.arange(-12.0, 12.01, 2.4)
    for x, y in ((x, y) for x in tile_loop[:-1] for y in tile_loop[:-1]):
        cell = box(
            center[0] + x, center[1] + y, center[0] + x + 2.4, center[1] + y + 2.4
        ).intersection(floor)
        ground_shell(walkable, cell, field, 0.135, COURT, COURT)
    lo, hi = data["tier_angles_degrees"]
    ring_points = []
    for index, (inner, outer, rise) in enumerate(data["treads"]):
        ring = enu_arc(center, inner, outer, lo, hi)
        ground_shell(walkable, ring, field, 0.135 + rise, STONE, STONE)
        nose = enu_arc(center, inner + 0.008, inner + 0.046, lo, hi)
        ground_shell(detail, nose, field, 0.14 + rise, STONE, TRIM)
        theta = np.deg2rad(219)
        at = np.asarray(center) + (inner + outer) / 2 * np.array(
            [np.cos(theta), np.sin(theta)]
        )
        ring_points.append(
            [*at.round(4), round(0.135 + rise + geometry.sample_ground(field, *at), 4)]
        )
    stage_center = data["stage_center_enu_m"]
    r = data["stage_radius_m"]
    stage = (
        Point(*stage_center)
        .buffer(r, quad_segs=27)
        .intersection(box(-280, -44, data["stage_clip_east_m"], -13))
    )
    ground_shell(
        walkable, stage, field, 0.135 + data["stage_height_m"], STONE, (186, 174, 150)
    )
    for inner, rise in ((r, 0.145), (r + 0.39, 0.082)):
        strip = enu_arc(stage_center, inner, inner + 0.40, 159, 266)
        ground_shell(walkable, strip, field, 0.135 + rise, STONE, STONE)
    walls = []
    for row in data["walls"]:
        start, stop = row["angles_degrees"]
        r, width = row["radius_m"], row["width_m"]
        # Visible construction joints break the wall into matched concrete bays.
        edges = np.linspace(start, stop, max(3, round((stop - start) / 6)) + 1)
        for low, high in zip(edges, edges[1:]):
            wall = enu_arc(
                center, r - width / 2, r + width / 2, low + 0.055, high - 0.055
            )
            ground_shell(detail, wall, field, row["height_m"], STONE, TRIM)
            walls.append(wall)
    return walls, ring_points


def planter(parts, spec, field):
    area = box(*spec["outline_enu_m"])
    lip, soil = spec["coping_height_m"], spec["soil_height_m"]
    inner = area.buffer(-spec["wall_thickness_m"], join_style="mitre")
    base = min(geometry.sample_ground(field, *xy) for xy in area.exterior.coords) - 0.25
    border = area.difference(inner)
    tools.flat(parts, border, base, lip - 0.115, BRICK)
    tools.flat(
        parts,
        border.buffer(0.045, join_style="mitre"),
        lip - 0.115,
        lip,
        (154, 133, 108),
        TRIM,
    )
    tools.flat(parts, inner, base, soil, BRICK, LAWN)
    for a, b in zip(list(area.exterior.coords), list(area.exterior.coords)[1:]):
        width, add = tools.face(parts, a, b)
        for z in np.arange(base + 0.13, lip - 0.145, 0.13):
            add(0.013, width - 0.013, 0.003, 0.014, z, z + 0.012, (149, 126, 102))
        for u in np.arange(1.2, width - 0.4, 1.5):
            add(u, u + 0.016, 0.043, 0.049, lip - 0.10, lip, (137, 125, 101))


def source_cuts(spec):
    patches = []
    for cut in spec["cuts"]:
        raw = (SCENE / cut["file"]).read_bytes()
        length, label = struct.unpack_from("<I4s", raw, 12)
        assert label == b"JSON"
        model = json.loads(raw[20 : 20 + length])
        node = next(n for n in model["nodes"] if n.get("name") == cut["target"])
        primitive = model["meshes"][node["mesh"]]["primitives"][cut["primitive"]]
        positions, indices = decode(model, memoryview(raw)[28 + length :], primitive)
        material = model["materials"][primitive["material"]].get("name", "")
        anchors = []
        for start, stop in cut["spans"]:
            for tri in (start, (start + stop) // 2, stop - 1):
                vertex = int(indices[tri][0])
                anchors.append(
                    [tri * 3, vertex, positions[vertex].astype(float).tolist()]
                )
        patches.append(
            {
                "target": cut["target"],
                "material": material,
                "vertices": len(positions),
                "triangles": len(indices),
                "spans": cut["spans"],
                "anchors": anchors,
            }
        )
    return patches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    spec = load(ROOT / "data/metadata/pilot-hardscape-l2.json")
    presentation_path = SCENE / "presentation.json"
    config, manifest = load(presentation_path), load(SCENE / "manifest.json")
    field_path = SCENE / manifest["heightfield_url"]
    graph_path = SCENE / "navigation.json"
    assert sha(field_path) == spec["heightfield_sha256"]
    assert sha(graph_path) == spec["navigation_sha256"]
    assert (
        config["asset_sha256"]
        == spec["source_art_sha256"]
        == sha(SCENE / config["asset_url"])
    )
    for key, digest in spec["related_models"].items():
        path = SCENE / config[key]["url"]
        assert sha(path) == config[key]["sha256"] and load(path)["sha256"] == digest
        assert sha(SCENE / load(path)["url"]) == digest
    field, graph = load(field_path), load(graph_path)
    walkable, detail, rail_boxes, readings = [], [], [], []
    for flight in spec["flights"]:
        boxes, check = add_treads(walkable, detail, flight, field)
        rail_boxes.extend(boxes)
        readings.append(check)
    curved, stage_readings = amphitheater(walkable, detail, spec["amphitheater"], field)
    planter(detail, spec["planter"], field)
    nodes = graph["nodes_enu_m"]
    lines = [LineString([nodes[a], nodes[b]]) for a, b, *_ in graph["edges"]]
    # Reject boxes on any current travel line. The low amphitheater walls are
    # rendered continuously, with no collision proxies across crossing paths.
    rail_clearance = [
        min(line.distance(piece) for line in lines) for piece in rail_boxes
    ]
    assert min(rail_clearance) > 0.53, rail_clearance
    walkable_mesh = trimesh.util.concatenate(walkable)
    detail_mesh = trimesh.util.concatenate(detail)
    stage = trimesh.Scene()
    stage.add_geometry(
        walkable_mesh, node_name="hardscape-walkable", geom_name="hardscape-walkable"
    )
    stage.add_geometry(
        detail_mesh, node_name="hardscape-detail", geom_name="hardscape-detail"
    )

    def metadata(tree):
        tree["asset"][
            "copyright"
        ] = "Open Campus contributors. Original geometry CC BY 4.0."
        tree["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.015, "roughnessFactor": 0.9}}
        ]
        for node in tree["nodes"]:
            if node.get("name") == "hardscape-walkable":
                node["extras"] = {"asset_kind": "landscape-surface"}
            if node.get("name") == "hardscape-detail":
                node["extras"] = {"asset_kind": "landscape-detail"}
        for mesh in tree["meshes"]:
            mesh["primitives"][0]["material"] = 0

    output = args.stage or (SCENE / PACKAGE)
    output.mkdir(exist_ok=True, parents=True)
    model, descriptor = output / "site.glb", output / "site.json"
    model.write_bytes(
        trimesh.exchange.gltf.export_glb(
            stage, include_normals=True, tree_postprocessor=metadata
        )
    )
    masks = source_cuts(spec)
    payload = {
        "source_art_sha256": spec["source_art_sha256"],
        "related_models": {
            id: spec["related_models"][key]
            for id, key in (
                ("roof-6684e091", "knight_library_site"),
                ("roof-266f13fd", "emu_green_site"),
                ("roof-11d15952", "oregon_jaqua_site"),
            )
        },
        "url": f"{PACKAGE}/site.glb",
        "sha256": sha(model),
        "cuts": masks,
        "collision_boxes_enu_m": [list(piece.bounds) for piece in rail_boxes],
        "walkable_bounds_enu_m": [
            [
                f["center_east"] - f["width_m"] / 2,
                f["threshold_north"],
                f["center_east"] + f["width_m"] / 2,
                f.get("apron_north", f["bottom_north"]),
            ]
            for f in spec["flights"]
        ]
        + [[-288.5, -43.5, -263.5, -18.5]],
    }
    write(descriptor, payload, True)
    if args.stage is None:
        config["pilot_hardscape_site"] = {
            "url": f"{PACKAGE}/site.json",
            "sha256": sha(descriptor),
        }
        write(presentation_path, config)
    report = {
        "flights": readings,
        "amphitheater_tread_probes": stage_readings,
        "route_edges": len(lines),
        "rail_route_clearance_m": rail_clearance,
        "terrace_wall_segments": len(curved),
        "triangles": [len(walkable_mesh.faces), len(detail_mesh.faces)],
        "removed_triangles": sum(
            end - start for cut in masks for start, end in cut["spans"]
        ),
        "glb_sha256": sha(model),
        "site_sha256": sha(descriptor),
    }
    write(args.audit, report)
    print(
        report["triangles"], report["removed_triangles"], round(min(rail_clearance), 3)
    )


if __name__ == "__main__":
    main()
