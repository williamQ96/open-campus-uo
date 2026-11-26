# SPDX-License-Identifier: Apache-2.0
"""Export three sourced exteriors beside Walnut, Alder and Broadway."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-villard-garden-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
garden = module_from_spec(loader)
loader.loader.exec_module(garden)

ROOT, SCENE = garden.ROOT, garden.SCENE
base, geometry, chapter = garden.base, garden.geometry, garden.chapter
PACKAGE = "walnut-alder-broadway-exterior-review"
GROUND = "walnut-alder-broadway-approaches"
WINDOW = chapter.prior.window
CONCRETE = (159, 157, 145)
PLASTER = (185, 181, 166)
ALUMINUM = (169, 171, 159)
BRICK = (134, 78, 63)
GLASS = (70, 93, 100)
DARK = (62, 63, 60)
WOOD = (93, 75, 64)
FASCIA = (65, 77, 86)
ROOF = (173, 174, 162)


def roof(parts, row, outline, wall, floor, colors):
    wall_color, trim_color, roof_color = colors
    return garden.roof_sections(
        parts,
        outline,
        wall,
        floor,
        {
            "id": row["id"],
            "wall_color": wall_color,
            "trim_color": trim_color,
            "roof_color": roof_color,
            "roof_frame": {"axis": [1, 0], "origin_enu_m": row["roof_origin_enu_m"]},
            "roof_zones": [
                {"bounds_m": [-44, -44, 44, 44], "planes": row["roof_planes"]}
            ],
        },
        grid=0.0001,
    )


def glazed_door(add, u, grade, width=1.65):
    left, right = u - width / 2, u + width / 2
    add(left - 0.075, right + 0.075, 0.008, 0.068, grade, grade + 2.31, ALUMINUM)
    add(left, right, 0.069, 0.095, grade + 0.13, grade + 2.22, GLASS)
    for center in (left + 0.02, u, right - 0.02):
        add(
            center - 0.019,
            center + 0.019,
            0.095,
            0.125,
            grade + 0.05,
            grade + 2.28,
            DARK,
        )
    add(left, right, 0.096, 0.124, grade + 1.92, grade + 1.96, DARK)
    for center in (u - 0.10, u + 0.10):
        add(
            center - 0.024,
            center + 0.024,
            0.123,
            0.164,
            grade + 0.89,
            grade + 1.12,
            ALUMINUM,
        )


def paving(ground, e, n, grade, direction, width, length):
    across = np.array([-direction[1], direction[0]]) * width / 2
    start = np.array([e, n])
    end = start + np.array(direction) * length
    slab = Polygon((start - across, end - across, end + across, start + across))
    base.flat(ground, slab, grade - 0.21, grade + 0.021, CONCRETE)


def walnut(parts, row, outline, floor, grade, field):
    wall = orient(outline.buffer(-0.54, join_style="mitre"))
    height = roof(parts, row, outline, wall, floor, (CONCRETE, WOOD, (118, 98, 78)))
    entrance = Point(row["entrance"]["anchor_enu_m"])
    for a, b in garden.shared.face_edges(wall):
        width, add, outward, plan, _, _ = chapter.setup_face(parts, a, b)
        if width < 3:
            continue
        edge = LineString((a, b))
        at = edge.project(entrance)
        west, south = outward[0] < -0.95, outward[1] < -0.95
        public = south and edge.distance(entrance) < 0.08
        low = geometry.sample_ground(field, *plan(width / 2, 0))
        add(0.04, width - 0.04, 0.003, 0.034, floor, low + 0.27, (127, 128, 119))
        if public:
            glazed_door(add, at, grade)
            add(at - 1.23, at + 1.23, 0.02, 0.12, grade + 2.41, grade + 2.66, WOOD)
        if west:
            centers, bay, ribs = np.linspace(1.95, width - 1.95, 3), 2.22, 3
        else:
            centers = np.arange(2.2, width - 1.35, 3.30)
            bay, ribs = 1.77, 2
        for u in centers:
            if public and abs(u - at) < 2.04:
                continue
            sill, top = low + 0.76, min(low + 2.48, height(plan(u, 0)) - 0.27)
            WINDOW(add, float(u), bay, sill, top, ALUMINUM, GLASS, ribs=ribs)
            if west:
                add(u - 1.11, u + 1.11, 0.104, 0.146, sill + 0.47, sill + 0.51, DARK)
                add(u - 1.11, u + 1.11, 0.104, 0.146, sill + 1.01, sill + 1.05, DARK)
    for n in (-123.7, -122.82, -121.94):
        e = wall.bounds[0] - 1.72
        z = geometry.sample_ground(field, e, n)
        points = [
            (e - 0.37, n, z),
            (e - 0.37, n, z + 0.61),
            (e - 0.28, n, z + 0.72),
            (e + 0.28, n, z + 0.72),
            (e + 0.37, n, z + 0.61),
            (e + 0.37, n, z),
        ]
        for a, b in zip(points, points[1:]):
            garden.tools.beam(parts, a, b, 0.041, DARK)
    return [wall], []


def alder(parts, row, outline, floor, grade, field):
    wall = orient(outline.buffer(-0.11, join_style="mitre"))
    height = roof(parts, row, outline, wall, floor, (PLASTER, ALUMINUM, ROOF))
    e, n = row["entrance"]["anchor_enu_m"]
    projection = box(e, n - 1.31, wall.bounds[0] + 0.28, n + 1.31)
    base.flat(parts, projection, floor, grade + 2.54, PLASTER)
    base.flat(
        parts,
        projection.buffer(0.21, join_style="mitre"),
        grade + 2.54,
        grade + 2.7,
        (95, 90, 78),
        (124, 123, 114),
    )
    _, entry, *_ = chapter.setup_face(parts, (e, n + 1.31), (e, n - 1.31))
    garden.neighbor.door(entry, 1.14, grade, (92, 87, 78))
    add_roof_vents = ((-813, 403.3), (-801.2, 396.3), (-794.2, 402.9))
    for x, y in add_roof_vents:
        z = height((x, y))
        base.flat(
            parts,
            box(x - 0.26, y - 0.22, x + 0.26, y + 0.22),
            z - 0.05,
            z + 0.17,
            ALUMINUM,
        )
    for a, b in garden.shared.face_edges(wall):
        width, add, outward, plan, _, _ = chapter.setup_face(parts, a, b)
        low = geometry.sample_ground(field, *plan(width / 2, 0))
        top = min(height(plan(u, 0)) for u in (0.03, width - 0.03)) - 0.17
        if outward[0] < -0.95:
            split = width * 0.42
            add(0.025, split, 0.001, 0.057, floor, top, BRICK)
            for z in np.arange(low + 0.14, top, 0.16):
                add(0.03, split - 0.02, 0.056, 0.060, z, z + 0.010, (113, 70, 56))
            for u in np.arange(split + 0.10, width - 0.05, 0.255):
                add(u, u + 0.023, 0.004, 0.027, low + 0.19, top, (157, 150, 133))
            WINDOW(add, width * 0.67, 1.02, low + 5.82, low + 7.14, ALUMINUM, GLASS)
            for z in np.arange(low + 4.35, low + 4.73, 0.075):
                add(width * 0.82, width * 0.88, 0.015, 0.056, z, z + 0.032, DARK)
            continue
        add(0.02, width - 0.02, 0.005, 0.043, floor, low + 0.42, CONCRETE)
        for z in (low + 3.06, low + 5.95):
            add(0.02, width - 0.02, 0.002, 0.026, z, z + 0.041, CONCRETE)
        for u in np.arange(2.3, width - 1.3, 3.94):
            for z in (low + 1.15, low + 3.93, low + 6.54):
                WINDOW(add, float(u), 1.50, z, z + 1.12, ALUMINUM, GLASS, ribs=1)
    return [orient(wall.union(projection))], []


def motel(parts, row, outline, floor, grade, field):
    canopy = row["roof_planes"][0][2]
    underside = canopy - 0.67
    base.flat(parts, outline, underside, canopy, FASCIA, (120, 124, 119))
    roof_skin = (84, 94, 99)
    for a, b in garden.shared.face_edges(outline):
        width, add, *_ = chapter.setup_face(parts, a, b)
        for z in np.arange(underside + 0.08, canopy - 0.055, 0.105):
            add(0.012, width - 0.012, 0.001, 0.023, z, z + 0.018, roof_skin)
    office = orient(box(-860.72, 508.1, -850.02, 514.98))
    base.flat(parts, office, floor, underside, CONCRETE)
    entrance = Point(row["entrance"]["anchor_enu_m"])
    for a, b in garden.shared.face_edges(office):
        width, add, outward, plan, *_ = chapter.setup_face(parts, a, b)
        north = outward[1] > 0.95
        edge = LineString((a, b))
        if north:
            WINDOW(add, width * 0.64, 2.18, grade + 1.03, grade + 2.37, ALUMINUM, GLASS)
            continue
        at = edge.project(entrance)
        front = outward[1] < -0.95
        if front:
            glazed_door(add, at, grade)
        for u in np.arange(1.24, width - 0.87, 1.91):
            if not front or abs(u - at) > 1.78:
                WINDOW(
                    add, float(u), 1.70, grade + 0.37, underside - 0.14, ALUMINUM, GLASS
                )
        add(0.04, width - 0.04, 0.003, 0.026, underside - 0.14, underside, FASCIA)
    supports = []
    for e, n in ((-841.25, 511.05), (-841.75, 514.43)):
        post = box(e - 0.16, n - 0.16, e + 0.16, n + 0.16)
        assert outline.covers(post)
        z = geometry.sample_ground(field, e, n)
        base.flat(parts, post, z - 0.15, underside + 0.01, FASCIA)
        supports.append(post)
    base.flat(
        parts,
        box(-846.3, 506.99, -844.62, 507.08),
        underside + 0.14,
        underside + 0.42,
        (216, 212, 202),
    )
    return [office], supports


def build(row, field, ground):
    outline = orient(Polygon(row["outline_enu_m"]))
    assert outline.is_valid
    floor, _ = garden.science.earlier.fit_base(field, outline)
    hint = row["entrance"]
    e, n = hint["anchor_enu_m"]
    grade = geometry.sample_ground(field, e, n)
    build_model = {"walnut-1401": walnut, "alder-968": alder, "broadway-755": motel}
    parts = []
    plans, supports = build_model[row["role"]](parts, row, outline, floor, grade, field)
    assert all(p.is_valid for p in plans + supports)
    assert min(p.boundary.distance(Point(e, n)) for p in plans) < 0.07
    west = hint["bearing"] == 270
    paving(ground, e, n, grade, (-1, 0) if west else (0, -1), 1.28, 0.95)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000018))
    record = {
        "id": row["id"],
        "name": row["name"],
        "street_address": row["street_address"],
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(p) for p in plans],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [
            {
                "gate": hint["gate"],
                "position_enu_m": [e, n],
                "outward_degrees": hint["bearing"],
                "approach_distance_m": hint["distance_m"],
                "threshold_z_m": round(grade + 0.021, 4),
                "width_m": 0.98 if west else 1.64,
                "estimated": True,
                "snap_to_facade": False,
            }
        ],
    }
    return garden.science.ordered_mesh(mesh), record, plans, supports


def write_json(path, value, *, compact=False):
    indent = None if compact else 2
    separators = (",", ":") if compact else None
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=indent, separators=separators)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = ROOT / "data/metadata"
    spec = json.loads((metadata / f"{PACKAGE}.json").read_bytes())
    source_path = SCENE / "manifest.json"
    config_path = SCENE / "presentation.json"
    manifest, config = (
        json.loads(path.read_bytes()) for path in (source_path, config_path)
    )
    height_path = SCENE / manifest["heightfield_url"]
    digest = garden.tools.digest
    assert digest(source_path) == spec["source_manifest_sha256"]
    assert digest(height_path) == spec["source_heightfield_sha256"]
    field = json.loads(height_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, plans, supports, gates = {}, [], [], [], [], []
    for row in spec["models"]:
        mesh, record, occupied, feet = build(row, field, ground)
        meshes[row["id"]] = mesh
        records.append(record)
        plans.extend(occupied)
        supports.extend(feet)
        gates.extend(record["entrances"])
    assert len(plans) == 3 and len(supports) == 2
    assert all(not p.covers(Point(-845.0, 511.15)) for p in plans + supports)
    old = union_all(
        [
            Polygon(row["footprint_enu_m"])
            for row in manifest["buildings"]
            if row["id"] in meshes
        ]
    )
    check_routes = chapter.prior.nearby.shared.graduate.shared.check_routes
    count, clearance = check_routes(
        plans, supports, gates, old, manifest, graph, config, set(meshes)
    )
    appearances = json.loads((metadata / "campus-expansion-audit.json").read_bytes())
    removals = garden.shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, appearances
    )
    stage = args.stage or SCENE / PACKAGE
    stage.mkdir(exist_ok=True, parents=True)
    model, descriptor = stage / "site.glb", stage / "site.json"
    pavement = garden.science.ordered_mesh(trimesh.util.concatenate(ground))
    garden.site.memorial.gerlinger.export(
        model, meshes, pavement, GROUND, "walnut-alder-broadway-paving"
    )
    package = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": digest(model),
        "buildings": records,
        "batch_removals": removals,
    }
    write_json(descriptor, package, compact=True)
    if args.stage is None:
        config["walnut_alder_broadway_site"] = {
            "url": f"{PACKAGE}/site.json",
            "sha256": digest(descriptor),
        }
        write_json(config_path, config)
    audit = {
        "buildings": records,
        "batch_removals": removals,
        "route_edges": count,
        "nearest_route_m": round(clearance, 4),
        "triangles": {key: len(mesh.faces) for key, mesh in meshes.items()},
        "glb_sha256": digest(model),
        "descriptor_sha256": digest(descriptor),
    }
    write_json(args.audit, audit)
    print(audit["triangles"], audit["nearest_route_m"])


if __name__ == "__main__":
    main()
