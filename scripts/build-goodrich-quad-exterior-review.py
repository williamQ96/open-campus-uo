# SPDX-License-Identifier: Apache-2.0
"""Model Goodrich Hall after 2025 and the adjoining two Alder Street buildings."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import union_all
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-alder-bushnell-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
prior = module_from_spec(loader)
loader.loader.exec_module(prior)
ROOT, SCENE, base, garden, geometry = (
    prior.ROOT,
    prior.SCENE,
    prior.base,
    prior.garden,
    prior.geometry,
)
PACKAGE = "goodrich-quad-exterior-review"
GROUND = "goodrich-quad-approaches"
SAND = (187, 173, 148)
ASHLAR = (138, 139, 133)
JOINT = (124, 125, 119)
CORNICE = (163, 158, 139)
WHITE = (191, 192, 175)
PANEL = (186, 185, 176)
WOOD = (135, 92, 55)
GLASS = (74, 97, 104)
FRAME = (172, 178, 169)
ROOF = (101, 108, 110)
BOARD = (168, 169, 155)
DARK = (83, 86, 80)
BRICK = (141, 92, 72)
WINDOW = prior.WINDOW


def elevation_stone(parts, point, width, low, high):
    vertices, faces = [], []

    def joint(left, right, base, top, depth):
        vertex = len(vertices)
        for u, z in ((left, base), (right, base), (right, top), (left, top)):
            east, north, up = point(u, depth, z)
            vertices.append((east, up, -north))
        faces.extend(
            ((vertex, vertex + 1, vertex + 2), (vertex, vertex + 2, vertex + 3))
        )

    for course, z in enumerate(np.arange(low + 0.22, high - 0.34, 0.31)):
        joint(0.02, width - 0.02, z, z + 0.011, 0.017)
        for u in np.arange(0.06 + (course % 2) * 0.38, width - 0.08, 0.78):
            joint(u, u + 0.014, z + 0.01, z + 0.306, 0.021)
    stone_joints = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    stone_joints.visual.vertex_colors = (*JOINT, 255)
    parts.append(stone_joints)


def sash_window(add, center, width, low, high, panes=1):
    left, right = center - width / 2, center + width / 2
    add(left - 0.05, right + 0.05, 0.01, 0.065, low - 0.08, high + 0.05, CORNICE)
    add(left, right, 0.065, 0.089, low, high, GLASS)
    for x in np.linspace(left, right, panes + 1):
        add(x - 0.036, x + 0.036, 0.088, 0.12, low, high, WHITE)
    for z in (low, (low + high) / 2, high):
        add(left, right, 0.088, 0.12, z - 0.032, z + 0.032, WHITE)


def main_portal(parts, add, point, slab, u, grade):
    z = grade + 0.48
    add(u - 1.18, u + 1.18, 0.012, 0.34, z - 0.015, z + 2.99, SAND)
    add(u - 0.86, u + 0.86, 0.339, 0.373, z, z + 2.33, WOOD)
    for offset in (-0.432, 0.432):
        at = u + offset
        add(at - 0.31, at + 0.31, 0.367, 0.39, z + 0.51, z + 2.11, GLASS)
    add(u - 0.80, u + 0.80, 0.340, 0.375, z + 2.39, z + 2.86, GLASS)
    for start in np.arange(u - 0.76, u + 0.62, 0.36):
        for a, b in ((z + 2.42, z + 2.84), (z + 2.84, z + 2.42)):
            garden.tools.beam(
                parts,
                point(start, 0.383, a),
                point(start + 0.34, 0.383, b),
                0.022,
                WHITE,
            )

    for offset in (-1.42, 1.42):
        lamp = u + offset
        add(lamp - 0.113, lamp + 0.113, 0.025, 0.232, z + 1.83, z + 2.36, DARK)
        add(lamp - 0.061, lamp + 0.061, 0.230, 0.252, z + 1.95, z + 2.26, SAND)

    mid = grade + 6.42
    arch = Polygon(
        [(u - 0.71, mid - 0.94), (u + 0.71, mid - 0.94)]
        + [
            (u + 0.71 * np.cos(t), mid + 0.67 * np.sin(t))
            for t in np.linspace(0, np.pi, 11)
        ]
    )
    slab(arch.buffer(0.125), 0.123, 0.185, SAND)
    slab(arch, 0.184, 0.202, GLASS)
    add(u - 0.695, u + 0.695, 0.202, 0.224, mid - 0.007, mid + 0.027, FRAME)
    for tilt in np.linspace(0.22, np.pi - 0.22, 5):
        tip = point(u + 0.69 * np.cos(tilt), 0.222, mid + 0.64 * np.sin(tilt))
        garden.tools.beam(parts, point(u, 0.222, mid), tip, 0.023, WHITE)
    for offset in (-5.80, -2.22, 2.22, 5.80):
        at = u + offset
        for d in (-0.20, 0.20):
            q = at + d
            add(q - 0.105, q + 0.105, 0.02, 0.243, grade + 4.10, grade + 7.90, SAND)
            for height in (grade + 4.10, grade + 7.70):
                add(q - 0.16, q + 0.16, 0.02, 0.30, height, height + 0.205, CORNICE)
    for z, dep, h in [
        (grade + 4.04, 0.32, 0.19),
        (grade + 7.80, 0.30, 0.17),
        (grade + 8.02, 0.41, 0.13),
    ]:
        add(u - 6.38, u + 6.38, 0.015, dep, z, z + h, CORNICE)


def build_belfry(parts, data, floor, grade):
    tower = box(*data["stone_and_panel_casing_enu_m"])
    connector = box(*data["joined_link_enu_m"])
    west, south, east, north = tower.bounds
    stone_top = grade + data["stone_base_height_m"]
    base.flat(parts, tower, floor, stone_top, ASHLAR)
    base.flat(
        parts, tower.buffer(0.09, join_style="mitre"), stone_top, stone_top + 0.16, SAND
    )
    base.flat(parts, tower, stone_top + 0.16, 13.42, PANEL)
    base.flat(parts, connector, floor, 12.48, (157, 146, 129), (170, 169, 155))
    lo, _, hi, exterior = connector.bounds
    base.flat(
        parts,
        box(lo, exterior - 0.06, hi - 0.15, exterior + 0.032),
        stone_top,
        12.35,
        WOOD,
    )
    for z in (stone_top + 1.3, 6.78, 10.36):
        base.flat(
            parts,
            box(west - 0.008, south + 0.02, west + 0.03, north - 0.02),
            z,
            z + 0.087,
            (140, 148, 145),
        )
    base.flat(
        parts,
        box(west + 0.18, south - 0.031, west + 2.3, south + 0.05),
        6.21,
        11.7,
        WOOD,
    )
    base.flat(
        parts,
        box(west - 0.031, south + 0.8, west + 0.012, south + 2.62),
        5.58,
        9.94,
        GLASS,
    )
    for z in (6.69, 7.70, 8.76):
        base.flat(
            parts,
            box(west - 0.07, south + 0.78, west + 0.012, south + 2.64),
            z,
            z + 0.059,
            FRAME,
        )
    frame = box(*data["belfry_frame_enu_m"])
    w, s, e, n = frame.bounds
    top = data["beam_top_z_m"]
    base.flat(parts, frame, 13.39, 15.65, PANEL)
    for piece in [box(w, s, e, s + 1.18), box(w, n - 1.18, e, n)]:
        base.flat(parts, piece, 15.62, top, PANEL)
    base.flat(parts, frame, top - 0.9, top, PANEL)
    base.flat(
        parts, box(w + 0.53, s - 0.039, e + 0.11, s + 0.027), 13.45, top - 0.18, WOOD
    )
    cx, cy = (w + e) / 2, (s + n) / 2
    cross_top = data["cross_top_z_m"]
    garden.tools.beam(parts, (cx, cy, top - 0.02), (cx, cy, cross_top), 0.192, WHITE)
    garden.tools.beam(
        parts,
        (cx, cy - 1.02, cross_top - 1.12),
        (cx, cy + 1.02, cross_top - 1.12),
        0.165,
        WHITE,
    )
    for k, (y, dz) in enumerate(
        zip(np.linspace(s + 1.82, n - 1.82, 4), (2.1, 3.1, 1.32, 2.49))
    ):
        hang = top - dz
        garden.tools.beam(parts, (cx, y, hang + 0.32), (cx, y, top - 0.86), 0.071, DARK)
        size = 0.8 + k * 0.09
        profile = (
            np.array(
                [
                    (0, -0.58),
                    (0.28, -0.58),
                    (0.26, -0.44),
                    (0.17, -0.25),
                    (0.099, 0.012),
                    (0, 0.030),
                ]
            )
            * size
        )
        bell = trimesh.creation.revolve(profile, sections=11)
        bell.apply_transform(
            [[1, 0, 0, cx], [0, 0, 1, hang + 0.32], [0, -1, 0, -y], [0, 0, 0, 1]]
        )
        bell.visual.vertex_colors = (112, 86, 57, 255)
        parts.append(bell)
    return tower, connector


def goodrich(parts, row, outline, floor, grade, field, ground):
    wall = orient(outline.buffer(-0.56, join_style="mitre"))
    height = prior.shell(parts, row, outline, wall, floor, ASHLAR, CORNICE, ROOF)
    e, n = row["entrance"]["point"]
    for edge, (width, add, normal, plan, point, slab) in prior.building_faces(
        parts, wall
    ):
        mid = plan(width / 2, 0)
        local_grade = geometry.sample_ground(field, *mid)
        cap = min(height(plan(u, 0)) for u in (0.15, width * 0.5, width - 0.15)) - 0.24
        elevation_stone(parts, point, width, floor, cap)
        add(0.02, width - 0.02, 0.015, 0.10, grade + 3.72, grade + 3.94, CORNICE)
        for u in np.arange(0.14, width - 0.08, 0.48):
            dentil = height(plan(u, 0)) - 0.41
            add(u, u + 0.162, 0.015, 0.165, dentil - 0.11, dentil + 0.105, CORNICE)
        if normal[1] > 0.95:
            center = edge.project(Point(e, n))
            main_portal(parts, add, point, slab, center, grade)
            for offset in (-10.20, -8.47, -3.6, 3.6, 8.47, 10.20):
                u = center + offset
                sash_window(add, u, 1.30, grade + 8.77, min(grade + 11.18, cap - 0.31))
                sash_window(add, u, 1.34, grade + 4.55, grade + 7.11)
                sash_window(add, u, 1.29, grade + 0.63, grade + 2.70)
            sash_window(add, center, 1.61, grade + 8.77, grade + 11.16, panes=3)
        else:
            for u in np.arange(1.88, width - 0.96, 3.39):
                for z in (local_grade + 0.86, grade + 4.58, grade + 8.70):
                    if z + 2.13 < height(plan(u, 0)) - 0.33:
                        sash_window(add, float(u), 1.29, z, z + 2.10)
    cupola = orient(box(-720.48, 219.65, -714.96, 222.15))
    cap = cupola.buffer(0.29, join_style="mitre")
    base.flat(parts, cupola, 13.01, 15.53, (131, 132, 115))
    base.flat(parts, cap, 15.50, 15.68, CORNICE, ROOF)
    for edge, (width, add, outward, *_part) in prior.building_faces(parts, cupola):
        if outward[1] > 0.95:
            for u, w in (
                (width * 0.16, 0.65),
                (width * 0.5, 2.14),
                (width * 0.84, 0.65),
            ):
                sash_window(add, u, w, 14.58, 15.24)
    tower, connector = build_belfry(parts, row["tower"], floor, grade)
    threshold = grade + 0.48
    for i in range(3):
        base.flat(
            ground,
            box(e - 1.46, n + 0.38 * i, e + 1.46, n + 0.38 * (i + 1)),
            grade - 0.17,
            threshold - i * 0.157,
            SAND,
        )
    prior.prior.paving(ground, e, n + 1.14, grade, (0, 1), 2.73, 1.50)
    return [orient(union_all([wall, tower, connector]))], [], threshold


def facilities(parts, row, outline, floor, grade, field, ground):
    wall = orient(
        outline.buffer(-0.34, join_style="mitre").intersection(
            box(-733.82, 190, -718, 204)
        )
    )
    height = prior.shell(parts, row, outline, wall, floor, BOARD, (161, 160, 144), ROOF)
    e, n = row["entrance"]["point"]
    x = outline.bounds[0] + 0.29
    post_plans = []
    threshold = grade + 0.43
    for y in (193.01, 201.16):
        pad = box(x - 0.23, y - 0.23, x + 0.23, y + 0.23)
        base.flat(parts, pad, floor, threshold + 0.68, ASHLAR)
        base.flat(
            parts,
            box(x - 0.13, y - 0.13, x + 0.13, y + 0.13),
            threshold + 0.67,
            height((x, y)) - 0.14,
            BOARD,
        )
        post_plans.append(pad)
    base.flat(ground, box(x - 0.19, 192.74, e + 0.36, 201.39), floor, threshold, SAND)
    prior.entrance_step(ground, x - 0.19, n, grade, threshold, -1, 2.14, 1.21)
    for edge, (width, add, outward, plan, point, _) in prior.building_faces(
        parts, wall
    ):
        west = outward[0] < -0.95
        top = min(height(plan(u, 0)) for u in (0.08, width - 0.08))
        for z in np.arange(grade + 0.51, top - 0.1, 0.185):
            add(0.03, width - 0.03, 0.004, 0.022, z, z + 0.010, (153, 156, 144))
        if west:
            center = edge.project(Point(e, n))
            prior.prior.glazed_door(add, center, threshold, 1.06)
            for u in (center - 2.21, center + 2.21):
                WINDOW(add, u, 1.47, threshold + 0.65, threshold + 2.32, FRAME, GLASS)
            for u in (center - 0.51, center + 0.51):
                WINDOW(add, u, 0.78, grade + 5.23, grade + 6.33, FRAME, GLASS, ribs=1)
            edge_u = width * 0.48
            corners = [
                point(center - edge_u, 2.02, top - 0.13),
                point(center, 2.02, height((x, n)) - 0.23),
                point(center + edge_u, 2.02, top - 0.13),
            ]
            for a, b in (
                (corners[0], corners[1]),
                (corners[1], corners[2]),
                (corners[0], corners[2]),
                (point(center, 2.02, top - 0.13), corners[1]),
            ):
                garden.tools.beam(parts, a, b, 0.092, DARK)
        else:
            for u in np.arange(1.85, width - 0.9, 3.72):
                WINDOW(
                    add,
                    float(u),
                    1.35,
                    grade + 1.33,
                    min(grade + 2.77, top - 0.33),
                    FRAME,
                    GLASS,
                )
    return [wall], post_plans, threshold


def brick(parts, row, outline, floor, grade, field, ground):
    wall = orient(outline.buffer(-0.18, join_style="mitre"))
    height = prior.shell(
        parts, row, outline, wall, floor, BRICK, (111, 113, 108), (148, 151, 145)
    )
    e, n = row["entrance"]["point"]
    door = Point(e, n)
    for edge, (width, add, outward, plan, _, _) in prior.building_faces(parts, wall):
        low_top = min(height(plan(u, 0)) for u in (0.08, width - 0.08))
        for z in np.arange(grade + 0.25, low_top - 0.14, 0.145):
            add(0.03, width - 0.03, 0.003, 0.019, z, z + 0.01, (116, 80, 65))
        if outward[0] < -0.95:
            at = width * 0.58
            add(at - 0.43, at + 0.43, 0.022, 0.066, grade + 0.38, grade + 1.90, DARK)
            for z in np.arange(grade + 0.51, grade + 1.85, 0.10):
                add(at - 0.38, at + 0.38, 0.063, 0.087, z, z + 0.035, FRAME)
        if edge.distance(door) < 0.13:
            at = edge.project(door)
            garden.neighbor.door(add, at, grade + 0.12, DARK)
            for u in (at - 2.65, at + 2.83):
                WINDOW(add, u, 1.04, grade + 1.38, grade + 2.56, FRAME, GLASS)
    chimney = box(-735.09, 180.05, -733.61, 181.56)
    base.flat(parts, chimney, height((-734.3, 180.82)) - 0.23, 9.96, BRICK)
    base.flat(
        parts, chimney.buffer(0.065, join_style="mitre"), 9.94, 10.09, (128, 86, 67)
    )
    prior.prior.paving(ground, e, n, grade, (0, -1), 1.2, 0.91)
    return [wall], [], grade + 0.12


def build(row, field, ground):
    outline = orient(Polygon(row["outline_enu_m"]))
    floor, _ = garden.science.earlier.fit_base(field, outline)
    entry = row["entrance"]
    e, n = entry["point"]
    grade = geometry.sample_ground(field, e, n)
    parts = []
    builders = {"goodrich": goodrich, "facilities": facilities, "brick": brick}
    plans, supports, threshold = builders[row["role"]](
        parts, row, outline, floor, grade, field, ground
    )
    assert all(p.is_valid and p.geom_type == "Polygon" for p in plans + supports)
    assert min(p.boundary.distance(Point(e, n)) for p in plans) < 0.115
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000018))
    outline_full = orient(union_all([outline, *plans]))
    record = {
        "id": row["id"],
        "name": row["name"],
        "street_address": row["street_address"],
        "footprint_enu_m": base.ring(outline_full),
        "ground_footprints_enu_m": [base.ring(p) for p in plans],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(outline_full.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [
            {
                "gate": entry["gate"],
                "position_enu_m": [e, n],
                "outward_degrees": entry["bearing"],
                "approach_distance_m": entry["distance"],
                "threshold_z_m": round(threshold, 4),
                "width_m": 1.14,
                "estimated": True,
                "snap_to_facade": False,
            }
        ],
    }
    return garden.science.ordered_mesh(mesh), record, plans, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = ROOT / "data/metadata"
    spec = json.loads((metadata / f"{PACKAGE}.json").read_bytes())
    source_path, config_path = (
        SCENE / name for name in ("manifest.json", "presentation.json")
    )
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
    assert all(not p.covers(Point(-735.1, 197.26)) for p in plans + supports)
    old = union_all(
        [
            Polygon(row["footprint_enu_m"])
            for row in manifest["buildings"]
            if row["id"] in meshes
        ]
    )
    check_routes = prior.chapter.prior.nearby.shared.graduate.shared.check_routes
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
        model, meshes, pavement, GROUND, "goodrich-quad-paving"
    )
    package = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": digest(model),
        "buildings": records,
        "new_building_ids": spec["new_building_ids"],
        "batch_removals": removals,
    }
    prior.prior.write_json(descriptor, package, compact=True)
    if args.stage is None:
        config["goodrich_quad_site"] = {
            "url": f"{PACKAGE}/site.json",
            "sha256": digest(descriptor),
        }
        prior.prior.write_json(config_path, config)
    audit = {
        "buildings": records,
        "batch_removals": removals,
        "route_edges": count,
        "nearest_route_m": round(clearance, 4),
        "triangles": {key: len(mesh.faces) for key, mesh in meshes.items()},
        "glb_sha256": digest(model),
        "descriptor_sha256": digest(descriptor),
    }
    prior.prior.write_json(args.audit, audit)
    print(audit["triangles"], audit["nearest_route_m"])


if __name__ == "__main__":
    main()
