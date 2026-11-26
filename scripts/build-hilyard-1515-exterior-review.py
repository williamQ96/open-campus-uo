# SPDX-License-Identifier: Apache-2.0
"""Build three separate exteriors from the merged E 15th and Hilyard candidate."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-villard-garden-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
garden = module_from_spec(loader)
loader.loader.exec_module(garden)

ROOT, SCENE = garden.ROOT, garden.SCENE
base, geometry, chapter, science = (
    garden.base,
    garden.geometry,
    garden.chapter,
    garden.science,
)
approach_source = Path(__file__).with_name("build-alder-millrace-exterior-review.py")
approach_loader = spec_from_file_location(approach_source.stem, approach_source)
approaches = module_from_spec(approach_loader)
approach_loader.loader.exec_module(approaches)

PACKAGE = "hilyard-fifteenth-exterior-review"
GROUND = "hilyard-1515-approaches"
DARK = (83, 66, 52)
CONCRETE = (164, 156, 138)
PALE = (196, 190, 159)
FRAME = (113, 119, 110)
WOOD = (156, 92, 61)
WOOD_TRIM = (114, 69, 45)
GLASS = (76, 103, 110)
PARKING = (77, 71, 64)


def sash(add, position, width, sill, height, ribs=1):
    chapter.prior.window(
        add, position, width, sill, sill + height, FRAME, GLASS, ribs=ribs
    )


def brace(parts, plan, a, b, thickness, color):
    def world(p):
        e, n = plan(p[0], p[1])
        return [e, p[2], -n]

    ends = np.asarray([world(a), world(b)])
    direction = ends[1] - ends[0]
    transform = trimesh.geometry.align_vectors([0, 0, 1], direction)
    transform[:3, 3] = ends.mean(axis=0)
    piece = trimesh.creation.box(
        (thickness, thickness, np.linalg.norm(direction)), transform
    )
    piece.visual.vertex_colors = [*color, 255]
    parts.append(piece)


def apartment_fascia(add, length, roof, overhang):
    add(0, length, -0.025, overhang, roof - 0.27, roof - 0.153, DARK)
    for station in np.arange(0.23, length - 0.10, 0.40):
        add(station, station + 0.045, 0.005, overhang, roof - 0.315, roof - 0.24, DARK)


def apartments(parts, edges, field, row, gate_frames):
    is_treetop = row["kind"] == "treetop"
    roof = row["roof_zones"][0]["planes"][0][2]
    for edge in edges:
        length, add, outward, plan, _, _ = chapter.setup_face(parts, *edge)
        if length < 2.5:
            continue
        grade = geometry.sample_ground(field, *plan(length / 2, 0))
        apartment_fascia(add, length, roof, row["overhang_m"])
        frame = gate_frames.get(edge)
        north = outward[1] > 0.96
        front_parking = frame is not None and north and is_treetop
        if not front_parking:
            add(0, length, 0.002, 0.065, grade - 0.09, grade + 0.27, CONCRETE)
        near = 1.45 if is_treetop else 1.58
        count = max(2, round(length / (4.3 if is_treetop else 3.55)))
        if frame and north and not is_treetop:
            positions = np.asarray(
                [fraction * length for fraction in (0.17, 0.37, 0.63, 0.83)]
            )
        else:
            positions = np.linspace(near, length - near, count)
        for center in positions:
            width = min(2.13 if is_treetop else 1.54, length / count - 0.12)
            if width < 0.68:
                continue
            if frame and abs(center - frame[1]) < width / 2 + 0.78:
                continue
            for sill in ((2.04, 4.64) if is_treetop else (1.78, 4.27)):
                sash(add, center, width, sill, 0.94 if is_treetop else 1.12, ribs=2)
            if not is_treetop and not north:
                sash(add, center, min(0.94, width), grade + 0.22, 0.58)
        if frame and north:
            gate, center = frame
            if is_treetop:
                add(
                    center - 0.89,
                    center + 0.89,
                    0.017,
                    0.052,
                    3.82,
                    5.78,
                    (177, 169, 134),
                )
                add(center - 0.45, center + 0.45, 0.054, 0.08, 4.57, 4.80, DARK)
                parking_canopies(parts, add, length, center, plan, grade)
            else:
                sash(add, center, 1.58, 3.27, 2.09, ribs=1)
                add(
                    center - 0.91,
                    center + 0.91,
                    0.026,
                    0.058,
                    2.87,
                    3.22,
                    (228, 226, 207),
                )
        if not is_treetop and outward[0] < -0.96 and length > 19:
            center = length * 0.52
            floor = 1.19
            garden.residential.balcony(add, center, 8.23, floor, 1.23, DARK)
            for u in (center - 3.70, center + 3.70):
                add(u - 0.058, u + 0.058, 0.91, 1.04, floor, roof - 0.31, DARK)
        if frame and not north:
            rail_stair(parts, plan, grade, frame[0], frame[1])


def parking_canopies(parts, add, length, center, plan, grade):
    top = grade + 2.59
    for left, right in ((0.10, center - 1.05), (center + 1.05, length - 0.10)):
        add(left, right, -0.018, 1.83, top - 0.112, top, DARK)
        for u in np.linspace(left + 0.63, right - 0.63, 3):
            brace(
                parts, plan, (u, 0.04, top - 0.98), (u, 1.58, top - 0.11), 0.115, DARK
            )


def rail_stair(parts, plan, grade, gate, center):
    if gate["rise_m"] < 0.34:
        return
    run = gate["landing_m"]
    top = gate["threshold_z_m"]
    for offset in (-0.52, 0.52):
        u = center + offset
        brace(
            parts,
            plan,
            (u, run - 0.16, grade + 0.80),
            (u, 0.52, top + 0.85),
            0.041,
            DARK,
        )
        brace(
            parts,
            plan,
            (u, run - 0.16, grade + 0.02),
            (u, run - 0.16, grade + 0.80),
            0.037,
            DARK,
        )
        brace(parts, plan, (u, 0.52, top), (u, 0.52, top + 0.85), 0.037, DARK)


def duplex(parts, edges, field, height, gate_frames):
    posts = []
    for edge in edges:
        length, add, outward, plan, _, _ = chapter.setup_face(parts, *edge)
        if length < 1.3:
            continue
        grade = geometry.sample_ground(field, *plan(length / 2, 0))
        for u in np.arange(0.12, length - 0.03, 0.32):
            top = height(plan(u, 0))
            add(u, u + 0.032, 0.002, 0.033, grade + 0.11, top - 0.17, WOOD_TRIM)
        frame = gate_frames.get(edge)
        if frame:
            gate, center = frame
            left, right = center - 4.53, center + 4.82
            left, right = max(0.22, left), min(length - 0.22, right)
            z = gate["threshold_z_m"]
            add(left, right, 0, 1.22, z - 0.36, z, CONCRETE)
            second_door = max(left + 0.84, center - 3.30)
            garden.neighbor.door(add, second_door, z, WOOD)
            for u in (left + 0.31, right - 0.31):
                point = plan(u, 1.09)
                posts.append(
                    approaches.supported_post(
                        parts, point, z - 0.30, z + 2.60, (211, 206, 183), 0.087
                    )
                )
            floor = z + 2.79
            garden.residential.balcony(
                add, (left + right) / 2, right - left, floor, 1.32, DARK
            )
            add(left, right, 0, 1.25, floor - 0.22, floor - 0.04, WOOD_TRIM)
            for x in np.linspace(left + 0.87, right - 0.87, 3):
                sash(add, x, 1.31, floor + 0.35, 1.34)
            for x in (left + 1.66, right - 1.93):
                if min(abs(x - center), abs(x - second_door)) > 1.24:
                    sash(add, x, 1.08, z + 0.70, 1.04)
            rail_stair(parts, plan, grade, gate, center)
        else:
            for u in np.linspace(1.14, length - 1.14, max(2, round(length / 3.55))):
                top = height(plan(u, 0))
                if grade + 4.32 < top - 0.26:
                    sash(add, u, 1.18, grade + 3.43, 0.89)
                if outward[1] < -0.96 and abs(u - length * 0.30) < 1.12:
                    garden.neighbor.door(add, length * 0.30, grade + 0.10, WOOD)
                else:
                    sash(add, u, 0.79, grade + 0.93, 0.78)
    return posts


def build_building(row, field, ground):
    outline = orient(Polygon(row["outline_enu_m"]))
    roof = orient(outline.buffer(row["overhang_m"], join_style="mitre"))
    wall = orient(outline.buffer(-0.12, join_style="mitre"))
    floor, _ = science.earlier.fit_base(field, wall)
    parts = []
    is_duplex = row["kind"] == "duplex"
    color = WOOD if is_duplex else PALE
    row = row | {
        "wall_color": color,
        "trim_color": DARK,
        "roof_color": (
            (105, 106, 97)
            if is_duplex
            else ((212, 213, 201) if row["kind"] == "hilyard" else (171, 168, 151))
        ),
    }
    occupied = wall
    upper_bottom = floor
    if row["kind"] == "treetop":
        west, _, east, north = wall.bounds
        near = row["entrances"][0]["near_enu_m"]
        grade = geometry.sample_ground(field, *near)
        upper_bottom = grade + 2.48
        wings = box(west - 1, north - 2.95, near[0] - 1.23, north + 1)
        wings = wings.union(box(near[0] + 1.23, north - 2.95, east + 1, north + 1))
        occupied = orient(wall.difference(wings))
        # The ground-level rear wall below the apartments is plastered.
        rear = occupied.intersection(
            box(west - 1, wall.bounds[1] - 1, east + 1, north - 3)
        )
        base.flat(parts, occupied.difference(rear), floor, upper_bottom, PARKING)
        base.flat(parts, rear, floor, upper_bottom, PALE)
    height = garden.roof_sections(parts, roof, wall, upper_bottom, row, grid=0.0001)
    if row["kind"] == "treetop":
        channel = box(-852.4, -280.25, -850.45, -272.05)
        base.flat(parts, channel, height((-851.5, -276.0)), 6.615, (144, 142, 127))
    elif not is_duplex:
        for e, n in ((-875.5, -260.6), (-869.7, -260.4), (-869.2, -281.8)):
            cap = Point(e, n).buffer(0.24, quad_segs=2)
            z = height((e, n))
            base.flat(parts, cap, z, z + 0.17, (159, 158, 146))
    edges = [tuple(map(tuple, edge)) for edge in garden.shared.face_edges(wall)]
    frames, gates = {}, []
    for hint in row["entrances"]:
        plan = row | {"door_color": WOOD if is_duplex else DARK, "entrance": hint}
        gate, edge, u = approaches.entry_stair(parts, ground, edges, field, plan, None)
        gate["estimated"] = True
        frames[edge] = (gate, u)
        gates.append(gate)
    supports = []
    if is_duplex:
        supports = duplex(parts, edges, field, height, frames)
    else:
        apartments(parts, edges, field, row, frames)
        if row["kind"] == "treetop":
            gate, u = next(
                (gate, u)
                for gate, u in frames.values()
                if gate["gate"] == "north-steps"
            )
            edge = next(edge for edge, frame in frames.items() if frame[0] is gate)
            _, _, _, plan, _, _ = chapter.setup_face(parts, *edge)
            rail_stair(parts, plan, geometry.sample_ground(field, *plan(u, 0)), gate, u)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000015))
    record = {
        "id": row["id"],
        "name": row["name"],
        "street_address": row["street_address"],
        "footprint_enu_m": base.ring(wall),
        "area_m2": round(occupied.area, 3),
        "ground_footprints_enu_m": [base.ring(occupied)],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "entrances": gates,
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
    }
    return science.ordered_mesh(mesh), record, occupied, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(
        (ROOT / "data/metadata/hilyard-1515-exterior-review.json").read_bytes()
    )
    manifest_path, config_path = SCENE / "manifest.json", SCENE / "presentation.json"
    manifest, config = (
        json.loads(path.read_bytes()) for path in (manifest_path, config_path)
    )
    field_path = SCENE / manifest["heightfield_url"]
    digest = garden.tools.digest
    assert digest(manifest_path) == spec["source_manifest_sha256"]
    assert digest(field_path) == spec["source_heightfield_sha256"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    models, records, ground, plans, supports, entries = {}, [], [], [], [], []
    for row in spec["models"]:
        mesh, record, plan, feet = build_building(row, field, ground)
        models[row["id"]] = mesh
        records.append(record)
        plans.append(plan)
        supports.extend(feet)
        entries.extend(record["entrances"])
    assert all(
        a.distance(b) > 0.48 for i, a in enumerate(plans) for b in plans[i + 1 :]
    )
    original = next(
        row
        for row in manifest["buildings"]
        if row["id"] == spec["source_ranges"][0]["id"]
    )
    routes, clearance = chapter.prior.nearby.shared.graduate.shared.check_routes(
        plans,
        supports,
        entries,
        Polygon(original["footprint_enu_m"]),
        manifest,
        graph,
        config,
        set(models),
    )
    appearances = json.loads(
        (ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = garden.shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, appearances
    )
    output = args.stage or SCENE / PACKAGE
    output.mkdir(parents=True, exist_ok=True)
    mesh_path, descriptor = output / "site.glb", output / "site.json"
    paving = science.ordered_mesh(trimesh.util.concatenate(ground))
    garden.site.memorial.gerlinger.export(
        mesh_path, models, paving, GROUND, "hilyard-1515-paving"
    )
    package = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": digest(mesh_path),
        "buildings": records,
        "split_buildings": spec["source_split"],
        "batch_removals": removals,
    }
    descriptor.write_text(
        json.dumps(package, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf8",
        newline="\n",
    )
    if args.stage is None:
        config["hilyard_1515_exterior_site"] = {
            "url": f"{PACKAGE}/site.json",
            "sha256": digest(descriptor),
        }
        config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf8",
            newline="\n",
        )
    audit = {
        "buildings": records,
        "batch_removals": removals,
        "route_edges": routes,
        "nearest_route_m": round(clearance, 4),
        "triangles": {k: len(v.faces) for k, v in models.items()},
        "glb_sha256": digest(mesh_path),
        "descriptor_sha256": digest(descriptor),
    }
    args.audit.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )
    print(audit["triangles"], audit["nearest_route_m"])


if __name__ == "__main__":
    main()
