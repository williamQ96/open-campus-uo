# SPDX-License-Identifier: Apache-2.0
"""Rebuild the Millrace, east Fairmount and Walnut Alley exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import nearest_points
import trimesh

source = Path(__file__).with_name("build-western-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
western = module_from_spec(loader)
loader.loader.exec_module(western)
ROOT, SCENE, base, garden, geometry, prior = (
    western.ROOT,
    western.SCENE,
    western.base,
    western.garden,
    western.geometry,
    western.prior,
)
DIRECTORY = "millrace-fairmount-exterior-review"
GROUND = "millrace-fairmount-approaches"
BRICK = (164, 110, 94)
BROWN = (118, 74, 61)
MORTAR = (148, 104, 91)
PINK = (203, 172, 155)
CREAM = (218, 214, 199)
WHITE = (228, 228, 221)
BLUE = (65, 102, 150)
SAGE = (126, 138, 107)
GREEN = (94, 116, 88)
GRAY = (136, 135, 122)
STEEL = (129, 137, 134)
DARK = (81, 89, 83)
GLASS = (79, 107, 115)

PALETTE = {
    "chapter": (BRICK, STEEL, (163, 169, 162)),
    "orchard": (CREAM, CREAM, (126, 125, 113)),
    "bungalow": (GREEN, CREAM, (134, 130, 109)),
    "garages": (SAGE, CREAM, STEEL),
}


def basis(parts, a, b):
    return prior.chapter.setup_face(parts, a, b)[:4]


def window(add, u, width, z, height, trim=CREAM, *, ribs=1):
    western.station.previous.WINDOW(
        add, u, width, z, z + height, trim, GLASS, ribs=ribs
    )


def door(add, u, z, color):
    add(u - 0.5, u + 0.5, 0.012, 0.081, z, z + 2.06, color)
    add(u - 0.395, u + 0.395, 0.081, 0.102, z + 0.035, z + 1.99, DARK)
    add(u - 0.32, u + 0.32, 0.104, 0.122, z + 0.89, z + 1.91, GLASS)
    add(u + 0.28, u + 0.34, 0.121, 0.155, z + 0.88, z + 1.09, STEEL)


def siding(add, span, high, low, color, pitch):
    for y in np.arange(low + pitch, high, pitch):
        add(0.024, span - 0.024, 0.004, 0.019, y, y + 0.013, color)


def chapter_letters(parts, plan, at, z):
    letters = (
        (((0, 0), (0.15, 0.38), (0.30, 0)), ((0.058, 0.14), (0.242, 0.14))),
        (((0.0, 0.38), (0.32, 0.38)), ((0.16, 0.38), (0.16, 0))),
        (
            (
                (0, 0),
                (0.13, 0),
                (0.04, 0.11),
                (0.025, 0.23),
                (0.1, 0.35),
                (0.23, 0.38),
                (0.34, 0.30),
                (0.36, 0.16),
                (0.26, 0),
                (0.39, 0),
            ),
        ),
    )
    for index, strokes in enumerate(letters):
        start = at - 0.61 + 0.43 * index
        for stroke in strokes:
            points = [(*plan(start + x, 0.071), z + lift) for x, lift in stroke]
            for first, second in zip(points, points[1:]):
                garden.tools.beam(parts, first, second, 0.030, DARK)


def chapter_facades(parts, walls, height, field, entry_edge, gate, threshold):
    for a, b in garden.shared.face_edges(walls):
        size, add, normal, plan = basis(parts, a, b)
        if size < 1.4:
            continue
        line = LineString([a, b])
        mid = plan(size * 0.5, 0)
        y = geometry.sample_ground(field, *mid)
        high = min(height(a), height(b))
        upper = high > 4.5
        if upper:
            is_east = normal[0] > 0.95 and size > 10 and mid[1] < 383
            sign_center = size * 0.53
            if is_east:
                add(size * 0.15, size * 0.88, 0.004, 0.033, y + 0.32, high - 0.16, PINK)
                chapter_letters(parts, plan, sign_center, y + 4.60)
            for u in np.arange(1.38, size - 0.77, 3.45):
                if is_east and abs(u - sign_center) < 1.58:
                    continue
                for h in (0.67, 3.06, 5.54):
                    if y + h + 1.3 < high - 0.25:
                        window(add, u, 1.20, y + h, 1.31, STEEL, ribs=2)
        else:
            siding(add, size, high - 0.21, y + 0.03, MORTAR, 0.21)
            if normal[1] < -0.9 and size > 9:
                for u in np.linspace(1.64, size - 1.81, 5):
                    window(add, u, 1.11, y + 1.8, 0.76, STEEL)
        if line.equals(entry_edge):
            u = line.project(gate)
            door(add, u - 0.37, threshold, STEEL)
            if size > 2.25:
                add(
                    u + 0.19,
                    u + 0.64,
                    0.017,
                    0.078,
                    threshold + 0.28,
                    threshold + 2.1,
                    STEEL,
                )
                add(
                    u + 0.24,
                    u + 0.57,
                    0.078,
                    0.094,
                    threshold + 0.39,
                    threshold + 2.0,
                    GLASS,
                )


def residential_facades(parts, row, wall, height, field, entry_edge, gate, threshold):
    blue = row["role"] == "orchard"
    trim = BLUE if blue else CREAM
    lining = (177, 176, 160) if blue else (81, 102, 76)
    for a, b in garden.shared.face_edges(wall):
        size, add, normal, plan = basis(parts, a, b)
        if size < 1.46:
            continue
        line = LineString([a, b])
        ground = geometry.sample_ground(field, *plan(size / 2, 0))
        top = min(height(plan(u, 0)) for u in (0.02, size * 0.5, size - 0.02))
        base_color = BROWN if not blue and normal[1] < -0.9 else GRAY
        add(0.018, size - 0.018, 0.003, 0.026, ground - 0.12, ground + 0.35, base_color)
        siding(add, size, top - 0.26, ground + 0.28, lining, 0.14 if blue else 0.205)
        entry = line.equals(entry_edge)
        at = line.project(gate) if entry else -10
        if entry:
            door(add, at, threshold, trim)
        centers = (
            np.linspace(size * 0.21, size * 0.79, max(2, round(size / 2.8)))
            if size > 4.2
            else [size * 0.5]
        )
        for u in centers:
            if abs(u - at) < 1.11:
                continue
            sash = min(1.6, size * 0.34)
            if u - sash / 2 > 0.08 and top - ground > 2.48:
                window(add, u, sash, ground + 1.02, 1.20, trim)
        if not blue and top - ground > 5.75:
            for u in centers[::2]:
                if min(u, size - u) > 0.38:
                    window(add, u, min(size * 0.32, 0.92), ground + 4.15, 1.24, trim)


def garages(parts, wall, field, grounds):
    west = wall.bounds[0]
    for n in (-309.55, -315.76, -321.61):
        line = LineString(((west - 1, n), (west + 1, n)))
        face = wall.boundary.intersection(line)
        x = face.x if face.geom_type == "Point" else west + 0.034
        span, add, _, _ = basis(parts, (x, n + 2.43), (x, n - 2.43))
        grade = geometry.sample_ground(field, x, n)
        add(0.25, span - 0.25, 0.025, 0.105, grade + 0.05, grade + 2.35, CREAM)
        add(0.37, span - 0.37, 0.106, 0.129, grade + 0.08, grade + 2.2, WHITE)
        for h in (0.54, 0.96, 1.35, 1.81):
            add(0.379, span - 0.379, 0.129, 0.148, grade + h, grade + h + 0.023, STEEL)
        for u in (1.04, 2.015, 2.99, 3.965):
            add(u - 0.31, u + 0.31, 0.148, 0.174, grade + 1.89, grade + 2.128, GLASS)
        western.terrace(grounds, field, box(x - 3.37, n - 2.18, x + 0.045, n + 2.18))
        window(add, span * 0.41, 1.03, grade + 3.43, 1.14, CREAM)
        window(add, span * 0.73, 0.59, grade + 3.40, 1.22, CREAM)
        siding(add, span, grade + 5.0, grade + 2.38, (113, 128, 104), 0.164)


def approach(grounds, field, gate, distance, bearing):
    east, north = gate.coords[0]
    theta = np.deg2rad(bearing)
    outward = np.array([np.sin(theta), np.cos(theta)])
    tangent = np.array([outward[1], -outward[0]])
    p = np.array([east, north])
    strip = Polygon(
        [
            p - tangent * 0.79,
            p + tangent * 0.79,
            p + outward * distance + tangent * 0.91,
            p + outward * distance - tangent * 0.91,
        ]
    )
    western.terrace(grounds, field, orient(strip))
    return geometry.sample_ground(field, east, north) + 0.08


def build(row, field, grounds):
    outline = orient(Polygon(row["outline_enu_m"]))
    floor, _ = garden.science.earlier.fit_base(field, outline)
    walls = orient(outline.buffer(-0.13, join_style="mitre"))
    role = row["role"]
    if role == "chapter":
        # The low wing roof continues over the east entrance recess.
        walls = orient(walls.difference(box(-775.91, 364.18, -769, 366.92)))
    parts = []
    height = prior.shell(parts, row, outline, walls, floor, *PALETTE[role])
    entries = []
    spec = row["entrance"]
    if spec:
        faces = list(garden.shared.face_edges(walls))
        pair = garden.locate_face(faces, spec["near"], spec["bearing"])
        side = LineString(pair)
        point = nearest_points(side, Point(spec["near"]))[0]
        assert point.distance(Point(spec["near"])) < 1.9, row["id"]
        z = approach(
            grounds, field, point, spec["approach_distance_m"], spec["bearing"]
        )
        e, n = point.coords[0]
        entries.append(
            {
                "gate": spec["gate"],
                "position_enu_m": [round(e, 5), round(n, 5)],
                "outward_degrees": spec["bearing"],
                "threshold_z_m": round(z, 4),
                "width_m": 1.08,
                "approach_distance_m": spec["approach_distance_m"],
                "estimated": True,
                "snap_to_facade": False,
            }
        )
        if role == "chapter":
            chapter_facades(parts, walls, height, field, side, point, z)
        else:
            residential_facades(parts, row, walls, height, field, side, point, z)
    else:
        garages(parts, walls, field, grounds)
    if role == "orchard":
        x, y = 559.05, -263.02
        z = height((x, y))
        base.flat(
            parts,
            box(x - 0.22, y - 0.30, x + 0.22, y + 0.30),
            z - 0.18,
            z + 1.05,
            BROWN,
        )
        base.flat(
            parts, box(x - 0.26, y - 0.34, x + 0.26, y + 0.34), z + 0.99, z + 1.09, GRAY
        )
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000018))
    mesh = garden.science.ordered_mesh(mesh)
    row = {
        **{k: row[k] for k in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(walls)],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": entries,
    }
    return mesh, row, walls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = ROOT / "data/metadata"
    spec = json.loads((metadata / f"{DIRECTORY}.json").read_bytes())
    config_path, source_path = SCENE / "presentation.json", SCENE / "manifest.json"
    config, manifest = [json.loads(p.read_bytes()) for p in (config_path, source_path)]
    height_path = SCENE / manifest["heightfield_url"]
    digest = garden.tools.digest
    assert digest(source_path) == spec["source_manifest_sha256"]
    assert digest(height_path) == spec["source_heightfield_sha256"]
    field = json.loads(height_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, grounds, footprints = {}, [], [], []
    for row in spec["models"]:
        mesh, record, plan = build(row, field, grounds)
        meshes[row["id"]] = mesh
        records.append(record)
        footprints.append(plan)
    entries = [gate for row in records for gate in row["entrances"]]
    original = union_all(
        [
            Polygon(row["footprint_enu_m"])
            for row in manifest["buildings"]
            if row["id"] in meshes
        ]
    )
    # A TIGER terminal spur enters the observed south wing. Register its
    # interior solid bay so the router drops the terminal edge at adoption.
    spur = spec["millrace_terminal_spur"]
    terminal = spur["nodes"][-1]
    edge = graph["edges"][spur["edge_index"]]
    assert edge[:2] == spur["nodes"] and edge[3] == "road"
    assert sum(terminal in values[:2] for values in graph["edges"]) == 1
    chapter = footprints[0]
    solid = box(*spur["collision_box_enu_m"])
    assert chapter.covers(solid) and solid.covers(Point(graph["nodes_enu_m"][terminal]))
    blocked = [
        i
        for i, (a, b, *_) in enumerate(graph["edges"])
        if solid.buffer(0.5, join_style="mitre").intersects(
            LineString([graph["nodes_enu_m"][a], graph["nodes_enu_m"][b]])
        )
    ]
    assert blocked == [spur["edge_index"]]
    check_routes = prior.chapter.prior.nearby.shared.graduate.shared.check_routes
    count, clearance = check_routes(
        footprints,
        [],
        entries,
        original,
        manifest,
        graph,
        config,
        set(meshes),
        excluded_edges=blocked,
    )
    appearances = json.loads((metadata / "campus-expansion-audit.json").read_bytes())
    removals = garden.shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, appearances
    )
    target = args.stage or SCENE / DIRECTORY
    target.mkdir(exist_ok=True, parents=True)
    model, descriptor = target / "site.glb", target / "site.json"
    pavement = garden.science.ordered_mesh(trimesh.util.concatenate(grounds))
    garden.site.memorial.gerlinger.export(
        model, meshes, pavement, GROUND, "millrace-fairmount-paving"
    )
    package = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "closed_site_boxes_enu_m": [spur["collision_box_enu_m"]],
        "url": f"{DIRECTORY}/site.glb",
        "sha256": digest(model),
        "buildings": records,
        "batch_removals": removals,
    }
    prior.prior.write_json(descriptor, package, compact=True)
    if args.stage is None:
        config["millrace_fairmount_exterior_site"] = {
            "url": f"{DIRECTORY}/site.json",
            "sha256": digest(descriptor),
        }
        prior.prior.write_json(config_path, config)
    audit = {
        "buildings": records,
        "batch_removals": removals,
        "route_edges": count,
        "excluded_terminal_edge": spur["edge_index"],
        "nearest_route_m": round(clearance, 4),
        "triangles": {id: len(mesh.faces) for id, mesh in meshes.items()},
        "glb_sha256": digest(model),
        "descriptor_sha256": digest(descriptor),
    }
    prior.prior.write_json(args.audit, audit)
    print(audit["triangles"], audit["nearest_route_m"])


if __name__ == "__main__":
    main()
