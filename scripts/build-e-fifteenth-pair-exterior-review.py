# SPDX-License-Identifier: Apache-2.0
"""Model the two distinct street and alley buildings off East Fifteenth Avenue."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-hilyard-central-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
prior = module_from_spec(loader)
loader.loader.exec_module(prior)

ROOT, SCENE = prior.ROOT, prior.SCENE
base, geometry, chapter, science = (
    prior.base,
    prior.geometry,
    prior.chapter,
    prior.science,
)
garden = prior.garden
PACKAGE = "e-fifteenth-pair-exterior-review"
GROUND = "e-fifteenth-pair-approaches"
WOOD = (125, 113, 97)
LAP = (157, 139, 115)
WOOD_SHADE = (101, 92, 77)
FRAME = (166, 165, 153)
GLASS = (74, 99, 109)
FASCIA = (80, 76, 65)
CONCRETE = (156, 152, 138)
DARK = (75, 72, 66)
ROOF = (120, 121, 112)
TIMBER = (136, 102, 67)


def board_siding(add, width, grade, height, plan, vertical):
    if vertical:
        for u in np.arange(0.11, width - 0.05, 0.24):
            top = height(plan(u, 0)) - 0.16
            add(u, u + 0.014, 0.003, 0.024, grade + 0.055, top, WOOD_SHADE)
    else:
        top = min(height(plan(u, 0)) for u in (0.04, width / 2, width - 0.04))
        for z in np.arange(grade + 0.29, top - 0.15, 0.168):
            add(0.015, width - 0.015, 0.002, 0.025, z, z + 0.014, WOOD_SHADE)


def wing_facades(parts, wall, field, height, upper, row, entrance_grade):
    street = row["role"] == "street"
    center = row["center_e_m"]
    entrance_n = row["entrance"]["anchor_enu_m"][1]
    for edge in garden.shared.face_edges(wall):
        width, add, outward, plan, _, _ = chapter.setup_face(parts, *edge)
        if width < 1.2:
            continue
        mid = plan(width / 2, 0)
        grade = geometry.sample_ground(field, *mid)
        clad_start = upper if street else grade + 0.29
        board_siding(add, width, clad_start, height, plan, street)

        gap_face = abs(mid[0] - center) < 2.0 and abs(outward[0]) > 0.95
        if gap_face:
            if street:
                doors = [(entrance_n - 1.28, upper), (entrance_n - 1.28, upper + 2.64)]
            else:
                doors = [
                    (entrance_n + 1.72, entrance_grade + 0.035),
                    (entrance_n + 6.78, entrance_grade + 2.70),
                    (entrance_n + 1.02, entrance_grade + 5.30),
                ]
            origin_n = plan(0, 0)[1]
            along_n = (plan(width, 0)[1] - origin_n) / width
            for at, z in doors:
                u = (at - origin_n) / along_n
                if 0.60 <= u <= width - 0.60:
                    garden.neighbor.door(add, u, z, FASCIA)
            continue

        if street:
            rows = (upper + 0.55, upper + 3.22)
            centers = np.linspace(1.62, width - 1.62, max(2, round(width / 3.75)))
            if outward[1] > 0.96:
                centers = np.array([width * 0.29, width * 0.73])
            sash_width = min(0.79, width * 0.24)
            sash_height = 1.54
        else:
            rows = tuple(grade + z for z in (0.84, 3.45, 6.06))
            centers = (
                [width * 0.55]
                if width < 10
                else np.linspace(1.7, width - 1.7, round(width / 3.5))
            )
            sash_width = min(2.06, width * 0.27)
            sash_height = 0.99
        for u in centers:
            if u < sash_width / 2 + 0.14 or u > width - sash_width / 2 - 0.14:
                continue
            for sill in rows:
                if sill + sash_height < height(plan(u, 0)) - 0.26:
                    chapter.prior.window(
                        add,
                        float(u),
                        sash_width,
                        sill,
                        sill + sash_height,
                        FRAME,
                        GLASS,
                        ribs=1,
                    )


def build_wing(parts, row, desc, field, floor, upper, entrance_grade):
    outline = orient(Polygon(desc["outline_enu_m"]))
    street = row["role"] == "street"
    wall = orient(outline.buffer(-0.14, join_style="mitre"))
    eaves = orient(outline.buffer(0.10, join_style="mitre"))
    style = {
        "wall_color": WOOD if street else LAP,
        "trim_color": FASCIA,
        "roof_color": ROOF,
        "roof_frame": {"axis": [1, 0], "origin_enu_m": desc["origin_enu_m"]},
        "roof_zones": [{"bounds_m": [-42, -42, 42, 42], "planes": desc["roof_planes"]}],
    }
    occupied, supports = wall, []
    if street:
        west, south, east, north = wall.bounds
        parking = box(west - 1, north - 4.0, east + 1, north + 0.3)
        occupied = orient(wall.difference(parking))
        base.flat(parts, occupied, floor, upper - 0.005, CONCRETE)
        for e in (west + 0.74, east - 0.74):
            n = north - 0.81
            pier = box(e - 0.13, n - 0.16, e + 0.13, n + 0.16)
            if wall.covers(pier):
                base.flat(parts, pier, floor, upper, CONCRETE)
                supports.append(pier)
    height = garden.roof_sections(
        parts, eaves, wall, upper if street else floor, style, grid=0.0001
    )
    wing_facades(parts, wall, field, height, upper, row, entrance_grade)
    return wall, occupied, supports, height


def world(n, e):
    return e, n


def railing(parts, a, b, at, z, color, *, axes=world):
    for h in (0.11, 0.925):
        prior.shared.brace(parts, axes, (a, at, z + h), (b, at, z + h), 0.045, color)
    for n in np.linspace(a, b, max(2, int(abs(b - a) / 0.17) + 1)):
        prior.shared.brace(parts, axes, (n, at, z), (n, at, z + 0.925), 0.034, color)


def landing(parts, x1, x2, y1, y2, height, material, *, guard=None):
    base.flat(parts, box(x1, y1, x2, y2), height - 0.15, height, material)
    for x in (x1 + 0.036, x2 - 0.036):
        railing(parts, y1 + 0.035, y2 - 0.035, x, height, FASCIA)
    if guard is not None:
        y = y1 + 0.036 if guard == "south" else y2 - 0.036
        railing(
            parts, x1 + 0.035, x2 - 0.035, y, height, FASCIA, axes=lambda e, n: (e, n)
        )


def street_stair(parts, row, floor, upper, height):
    east = row["center_e_m"]
    west, right = east - 1.19, east + 1.23
    north = row["entrance"]["anchor_enu_m"][1]
    upper2 = upper + 2.64
    for level in (upper, upper2):
        landing(
            parts, west, right, north - 2.2, north - 0.24, level, TIMBER, guard="north"
        )
        landing(parts, west, right, north - 10.15, north - 8.8, level, TIMBER)
    # Keep the two flights and the interval visible through the center of the roofs.
    prior.pitched_stair(
        parts,
        world,
        north - 2.12,
        north - 8.82,
        west + 0.16,
        0.94,
        floor,
        upper,
        tread=FASCIA,
        trim=FRAME,
    )
    prior.pitched_stair(
        parts,
        world,
        north - 8.84,
        north - 2.17,
        right - 1.05,
        0.94,
        upper,
        upper2,
        tread=FASCIA,
        trim=FRAME,
    )
    for n in np.arange(north + 0.04, -279.25, -0.55):
        low = (n, west, height[0]((west - 0.1, n)) - 0.07)
        high = (n, right, height[1]((right + 0.1, n)) - 0.07)
        prior.shared.brace(parts, world, low, high, 0.12, TIMBER)
    for e in (west, right):
        prior.shared.brace(
            parts,
            world,
            (north - 0.15, e, upper - 0.12),
            (north - 0.15, e, floor),
            0.10,
            FASCIA,
        )
    gate_s, gate_n = north - 0.21, north - 0.09
    for e in np.arange(west + 0.14, right, 0.14):
        base.flat(
            parts,
            box(e - 0.022, gate_s, e + 0.022, gate_n),
            floor + 0.035,
            min(upper - 0.13, floor + 2.02),
            DARK,
        )
    base.flat(
        parts, box(west, gate_s, right, gate_n), floor + 1.91, floor + 1.985, DARK
    )
    return [box(west, gate_s, right, gate_n)]


def alley_stair(parts, row, grade):
    east = row["center_e_m"]
    west, right = east - 1.13, east + 1.13
    south = row["entrance"]["anchor_enu_m"][1]
    front, back = south + 0.52, south + 6.31
    upper, upper2 = grade + 2.70, grade + 5.30
    prior.pitched_stair(
        parts,
        world,
        front,
        back,
        west + 0.067,
        0.95,
        grade,
        upper,
        tread=TIMBER,
        trim=WOOD_SHADE,
    )
    prior.pitched_stair(
        parts,
        world,
        back,
        front,
        right - 1.011,
        0.95,
        upper,
        upper2,
        tread=TIMBER,
        trim=WOOD_SHADE,
    )
    landing(parts, west, right, back - 0.13, back + 1.16, upper, TIMBER)
    landing(
        parts, west, right, front - 0.16, front + 1.24, upper2, TIMBER, guard="south"
    )
    feet = [box(west + 0.017, front, west + 0.95, front + 1.68)]
    for e in (west + 0.1, right - 0.1):
        for n in (front + 0.12, back + 0.82):
            support = box(e - 0.083, n - 0.083, e + 0.083, n + 0.083)
            base.flat(
                parts,
                support,
                grade - 0.09,
                upper2 - 0.16 if n < back else upper,
                TIMBER,
            )
            feet.append(support)
    return feet


def build(row, field, paving):
    nominal = orient(Polygon(row["outline_enu_m"]))
    floor, _ = science.earlier.fit_base(field, nominal)
    hint = row["entrance"]
    e, n = hint["anchor_enu_m"]
    grade = geometry.sample_ground(field, e, n)
    street = row["role"] == "street"
    upper = grade + 2.55 if street else floor
    parts, walls, blocks, supports, roof_heights = [], [], [], [], []
    for desc in row["wings"]:
        wall, occupied, feet, height = build_wing(
            parts, row, desc, field, floor, upper, grade
        )
        walls.append(wall)
        blocks.append(occupied)
        supports.extend(feet)
        roof_heights.append(height)
    if street:
        supports.extend(street_stair(parts, row, grade, upper, roof_heights))
    else:
        supports.extend(alley_stair(parts, row, grade))
    direction = 1 if hint["bearing"] == 0 else -1
    ground_patch = box(
        e - 0.61, min(n, n + 1.25 * direction), e + 0.61, max(n, n + 1.25 * direction)
    )
    base.flat(paving, ground_patch, grade - 0.19, grade + 0.027, CONCRETE)
    gate = {
        "gate": hint["gate"],
        "position_enu_m": [e, n],
        "outward_degrees": hint["bearing"],
        "approach_distance_m": hint["distance_m"],
        "threshold_z_m": round(grade + 0.027, 4),
        "width_m": 1.22,
        "estimated": True,
        "snap_to_facade": False,
    }
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000018))
    record = {
        "id": row["id"],
        "name": row["name"],
        "street_address": row["street_address"],
        "footprint_enu_m": base.ring(nominal),
        "ground_footprints_enu_m": [base.ring(p) for p in blocks],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(sum(p.area for p in walls), 3),
        "entrances": [gate],
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
    }
    return science.ordered_mesh(mesh), record, blocks, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(
        (ROOT / "data/metadata/e-fifteenth-pair-exterior-review.json").read_bytes()
    )
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
    meshes, records, ground, plans, feet, gates = {}, [], [], [], [], []
    for row in spec["models"]:
        mesh, record, occupied, support = build(row, field, ground)
        meshes[row["id"]] = mesh
        records.append(record)
        plans.extend(occupied)
        feet.extend(support)
        gates.extend(record["entrances"])
    assert len(plans) == 4
    assert all(
        a.distance(b) > 0.67 for i, a in enumerate(plans) for b in plans[i + 1 :]
    )
    adjacent_pack = json.loads(
        (SCENE / config["hilyard_1515_exterior_site"]["url"]).read_bytes()
    )
    adjacent = next(
        row for row in adjacent_pack["buildings"] if row["id"] == "east-15th-740"
    )
    assert all(
        p.distance(Polygon(adjacent["footprint_enu_m"])) > 0.60 for p in plans + feet
    )
    source_id = spec["source_ranges"][0]["id"]
    old = next(row for row in manifest["buildings"] if row["id"] == source_id)
    count, clearance = chapter.prior.nearby.shared.graduate.shared.check_routes(
        plans,
        feet,
        gates,
        Polygon(old["footprint_enu_m"]),
        manifest,
        graph,
        config,
        set(meshes),
    )

    appearances = json.loads(
        (ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = garden.shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, appearances
    )
    stage = args.stage or SCENE / PACKAGE
    stage.mkdir(exist_ok=True, parents=True)
    model, descriptor = stage / "site.glb", stage / "site.json"
    paving = science.ordered_mesh(trimesh.util.concatenate(ground))
    garden.site.memorial.gerlinger.export(
        model, meshes, paving, GROUND, "e-fifteenth-paving"
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
    descriptor.write_text(
        json.dumps(package, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if args.stage is None:
        config["e_fifteenth_pair_site"] = {
            "url": f"{PACKAGE}/site.json",
            "sha256": digest(descriptor),
        }
        config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    audit = {
        "buildings": records,
        "batch_removals": removals,
        "route_edges": count,
        "nearest_route_m": round(clearance, 4),
        "triangles": {key: len(v.faces) for key, v in meshes.items()},
        "glb_sha256": digest(model),
        "descriptor_sha256": digest(descriptor),
    }
    args.audit.write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(audit["triangles"], audit["nearest_route_m"])


if __name__ == "__main__":
    main()
