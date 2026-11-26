# SPDX-License-Identifier: Apache-2.0
"""Build four existing exteriors and the observed Chapter Alder site."""

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

path = Path(__file__).with_name("build-former-hospital-site-review.py")
loader = spec_from_file_location(path.stem, path)
hospital = module_from_spec(loader)
loader.loader.exec_module(hospital)
ROOT, SCENE, base, geometry = (
    hospital.ROOT,
    hospital.SCENE,
    hospital.base,
    hospital.geometry,
)
district = hospital.district
chapter, design, shared = district.chapter, hospital.design, district.houses.shared
beam = hospital.rod
PACKAGE = "alder-thirteenth-exterior-review"
GROUND = "alder-thirteenth-ground"
CONCRETE = (167, 162, 150)
PAVING = (175, 168, 153)
BRICK = (151, 88, 69)
BED = (136, 126, 101)
STONE = (147, 137, 117)
TRIM = (112, 117, 105)
INK = (60, 66, 67)
METAL = (77, 84, 89)
PANEL = (97, 106, 112)
GLASS = (67, 97, 111)
WOOD = (160, 110, 69)
RED = (163, 54, 51)
GOLD = (231, 187, 57)
ROOF = (159, 160, 149)
FORM = (178, 127, 80)
FORM_EDGE = (146, 90, 58)
FENCE = (182, 90, 56)


def facades(parts, outline):
    for start, end in shared.face_edges(orient(outline)):
        yield LineString((start, end)), chapter.setup_face(parts, start, end)


def glazing(add, left, right, bottom, top, frame=INK, bays=2):
    add(left, right, 0.026, 0.12, bottom, top, frame)
    for i in range(bays):
        a, b = (left + (right - left) * j / bays for j in (i, i + 1))
        add(a + 0.06, b - 0.06, 0.121, 0.144, bottom + 0.075, top - 0.075, GLASS)
    if top - bottom > 2:
        add(left, right, 0.144, 0.164, top - 0.42, top - 0.37, frame)


def gable(parts, bounds, eave, peak, wall, roof):
    west, south, east, north = bounds
    mid = (west + east) / 2
    for x0, x1, edge in ((west, mid, west), (mid, east, east)):
        band = box(x0, south, x1, north)

        def top(e, n):
            return peak - (peak - eave) * abs(e - mid) / (east - mid)

        parts.append(geometry.shell(band, eave - 0.12, top, wall, roof))
        for n in (south, north):
            beam(parts, (mid, n, peak), (edge, n, eave), 0.052, TRIM)


def corner(parts, spec, wall, floor, grade):
    eave = grade + spec["eave_m"]
    base.flat(parts, wall, floor, eave, BRICK, ROOF)
    gable(parts, spec["gable_enu_m"], eave - 0.20, grade + spec["ridge_m"], BRICK, TRIM)
    for _, (length, add, normal, _, _, _) in facades(parts, wall):
        if length < 3:
            continue
        add(0.05, length - 0.05, 0.006, 0.064, eave - 0.32, eave, TRIM)
        for seam in np.arange(grade + 0.24, eave - 0.35, 0.184):
            add(0.02, length - 0.02, 0.003, 0.016, seam, seam + 0.014, (168, 110, 86))
        if normal[1] > -0.92 and normal[0] > -0.92:
            continue
        count = 5 if normal[1] < -0.92 else 3
        for i in range(count):
            width = length / count
            start = i * width + 0.17
            end = (i + 1) * width - 0.21
            if normal[0] < -0.92 and i != count - 1:
                continue
            glazing(add, start, end, grade + 0.20, eave - 1.07, INK)
            add(start - 0.05, end + 0.05, 0.015, 0.33, eave - 0.96, eave - 0.43, RED)
            add(
                start - 0.05,
                start + 0.20,
                0.015,
                0.20,
                grade + 0.10,
                eave - 0.34,
                STONE,
            )
    return wall, []


def gopuran(parts, spec, wall, floor, grade):
    low = grade + spec["low_roof_m"]
    high = grade + spec["high_roof_m"]
    deep = wall.intersection(box(-712, 24.6, -697, 62))
    base.flat(parts, wall, floor, low, STONE, ROOF)
    base.flat(parts, deep, low - 0.02, high - 0.36, STONE, ROOF)
    cap = wall.intersection(box(-712, 11, -698, 31))
    base.flat(parts, cap, low - 0.02, high, STONE, ROOF)
    for edge, (length, add, n, plan, _, _) in facades(parts, wall):
        if n[1] < -0.92:
            glazing(add, 0.39, length - 0.43, grade + 0.06, grade + 3.36, WOOD, 3)
            glazing(add, 0.53, length - 0.64, grade + 4.33, high - 0.60, INK, 2)
            add(0.02, length - 0.02, 0.013, 0.18, grade + 3.58, grade + 4.11, STONE)
            for x in np.arange(0.61, length - 0.35, 0.26):
                add(x, x + 0.019, 0.15, 0.17, grade + 4.24, grade + 5.16, INK)
        elif n[1] > 0.92:
            glazing(add, 0.59, length - 0.56, grade + 4.25, high - 0.68, INK)
        elif edge.length > 18:
            for north in (30.8, 38.5, 46.4, 54.6):
                u = edge.project(Point(plan(0, 0)[0], north))
                glazing(add, u - 0.55, u + 0.55, grade + 4.44, grade + 5.66)
    return wall, []


def flock(parts, spec, wall, floor, grade):
    west, south, east, north = wall.bounds
    podium = grade + spec["podium_cap_m"]
    tower = wall.intersection(
        box(west - 1, spec["south_tower_wall_north_m"], east + 1, north + 1)
    )
    tower = tower.difference(union_all([box(*r) for r in spec["upper_insets_enu_m"]]))
    recess = box(-684.98, south - 0.2, -684.16, spec["south_tower_wall_north_m"] + 1.02)
    tower = tower.difference(recess)
    assert tower.geom_type == "Polygon"
    base.flat(parts, wall, floor, podium, STONE, CONCRETE)
    for _, (length, add, n, _, _, _) in facades(parts, wall):
        if n[1] > -0.92 or length < 10:
            continue
        bay = length / 9
        for i in range(9):
            x = i * bay
            glazing(add, x + 0.15, x + bay - 0.14, grade + 0.21, podium - 0.42, INK)
            add(x + 0.018, x + 0.158, 0.018, 0.19, grade + 0.10, podium, WOOD)
            add(x + 0.16, x + bay - 0.14, 0.15, 0.168, grade + 1.21, grade + 1.25, INK)
        add(0, length, 0.008, 0.28, podium - 0.39, podium, METAL)
    split = 47.0
    caps = [
        (
            tower.intersection(box(west - 1, south, east + 1, split)),
            grade + spec["tower_roof_m"],
        ),
        (
            tower.intersection(box(west - 1, split, east + 1, north + 1)),
            grade + spec["north_roof_m"],
        ),
    ]
    for wing, top in caps:
        base.flat(parts, wing, podium - 0.02, top, METAL, ROOF)
        for x, y in (
            (wing.centroid.x, wing.centroid.y),
            (wing.representative_point().x + 2, wing.representative_point().y + 2.5),
        ):
            unit = box(x - 1.05, y - 0.83, x + 1.05, y + 0.83)
            if wing.covers(unit):
                base.flat(parts, unit, top, top + 0.69, TRIM)
    for edge, (length, add, n, plan, _, _) in facades(parts, tower):
        if length < 1.3:
            east_face, north_face = plan(length / 2, 0)
            if n[1] < -0.94 and -685.0 <= east_face <= -684.16 and north_face < 20:
                add(
                    0.022,
                    length - 0.022,
                    0.02,
                    0.073,
                    podium + 1.2,
                    caps[0][1] - 0.15,
                    GOLD,
                )
            continue
        bays = max(1, round(length / 2.62))
        for i in range(bays):
            u0, u1 = ((i + k) * length / bays for k in (0, 1))
            x, y = plan((u0 + u1) / 2, 0)
            top = caps[0 if y < split else 1][1]
            for row in range(6):
                z = podium + row * 3.01
                if z + 2.62 >= top:
                    continue
                panel = PANEL if (i + 3 * row) % 5 == 1 else METAL
                add(u0 + 0.019, u1 - 0.019, 0.008, 0.032, z + 0.06, z + 2.94, panel)
                if (i + row * 3) % 9 != 4 and u1 - u0 > 1.56:
                    glazing(add, u0 + 0.30, u1 - 0.39, z + 0.76, z + 2.35, INK, 2)
                color = GOLD if (i * 3 + row * 5) % 7 in (0, 1) else INK
                add(u1 - 0.24, u1 - 0.17, 0.032, 0.071, z + 0.12, z + 2.88, color)
            add(u0 + 0.016, u1 - 0.018, 0.021, 0.10, top - 0.28, top + 0.14, INK)
        if edge.bounds[1] < 30 and n[1] < -0.95 and length > 8:
            add(0.09, length - 0.09, 0.016, 0.09, podium + 2.49, podium + 2.58, METAL)
    front = south + 0.31
    e0, e1 = west + 8.75, east - 4.7
    canopy = box(e0, front + 0.30, e1, south + 7.75)
    base.flat(parts, canopy, podium + 2.79, podium + 2.98, WOOD, METAL)
    for e in np.arange(e0 + 0.35, e1, 1.38):
        beam(
            parts,
            (e, front + 0.31, podium + 2.78),
            (e, south + 7.7, podium + 2.78),
            0.098,
            INK,
        )
    for e in (e0 + 0.76, e1 - 0.85):
        beam(
            parts,
            (e, front + 0.78, podium),
            (e, front + 0.78, podium + 2.78),
            0.19,
            WOOD,
        )
    for e in np.arange(west + 0.48, east - 0.3, 0.53):
        beam(parts, (e, front, podium), (e, front, podium + 1.11), 0.02, METAL)
    for z in (podium + 0.10, podium + 1.10):
        beam(parts, (west + 0.36, front, z), (east - 0.31, front, z), 0.047, INK)
    return wall, []


def duck(parts, spec, wall, floor, grade):
    west, south, east, north = wall.bounds
    eave = grade + spec["box_eave_m"]
    porch = wall.intersection(
        box(-667, south - 0.2, -639, south + spec["porch_setback_m"])
    )
    occupied = wall.difference(porch)
    roof = (104, 126, 138)
    base.flat(parts, occupied, floor, eave, METAL, roof)
    base.flat(parts, wall, grade + 3.50, eave, PANEL, roof)
    gw, gs, ge, gn = spec["south_gable_bounds_enu_m"]
    glass_top = grade + spec["clerestory_eave_m"]
    base.flat(parts, box(gw, gs, ge, gn), eave, glass_top, METAL, roof)
    for _, (length, add, n, _, _, _) in facades(parts, box(gw, gs, ge, gn)):
        if n[1] < -0.95:
            for u in np.arange(0.24, length - 0.25, 0.60):
                glazing(
                    add, u, min(u + 0.49, length - 0.06), eave + 0.05, glass_top + 0.04
                )
    for lo, hi in zip(np.linspace(gw, ge, 4)[:-1], np.linspace(gw, ge, 4)[1:]):
        gable(
            parts,
            (lo, gs, hi, gn),
            glass_top,
            grade + spec["clerestory_ridge_m"],
            METAL,
            roof,
        )
        mid = (lo + hi) / 2
        for d in np.arange(0.38, (hi - lo) / 2 - 0.32, 0.39):
            z = (
                grade
                + spec["clerestory_ridge_m"]
                - d
                * 2
                * (spec["clerestory_ridge_m"] - spec["clerestory_eave_m"])
                / (hi - lo)
            )
            for e in (mid + d, mid - d):
                beam(
                    parts,
                    (e, gs - 0.02, glass_top - 0.03),
                    (e, gs - 0.02, z),
                    0.035,
                    GOLD,
                )
    for _, (length, add, n, _, _, _) in facades(parts, wall):
        if length < 2.0:
            continue
        for i, u in enumerate(np.arange(0.14, length - 0.27, 0.45)):
            color = (
                GOLD
                if i % 13 in (3, 9)
                else ((121, 129, 135) if i % 3 else (102, 112, 121))
            )
            add(
                u,
                min(u + 0.37, length - 0.07),
                0.014,
                0.031,
                grade + 3.60,
                eave - 0.11,
                color,
            )
        add(0.02, length - 0.02, 0.024, 0.105, grade + 3.48, grade + 3.57, WOOD)
        if n[0] > 0.93:
            for u in np.arange(2.4, length - 2, 5.4):
                glazing(add, u - 1.36, u + 1.41, grade + 0.62, grade + 3.36)
    for edge, (length, add, n, _, _, _) in facades(parts, occupied):
        if n[1] < -0.92 and edge.bounds[1] < south + 3 and length > 10:
            for u in np.arange(2.3, length - 1.6, 4.65):
                glazing(add, u - 1.98, u + 1.91, grade + 0.12, grade + 3.41, INK, 3)
            u = edge.project(Point(spec["entry"]["east"], south))
            add(u - 2.20, u - 1.90, 0.018, 0.35, grade, grade + 3.47, WOOD)
            add(u + 1.90, u + 2.21, 0.018, 0.35, grade, grade + 3.47, WOOD)
            add(u - 2.2, u + 2.21, 0.018, 0.35, grade + 3.23, grade + 3.47, WOOD)
    supports = []
    for e in (-663.1, -658.2, -653.1, -646.72, -641.05):
        column = box(e - 0.135, south + 0.62, e + 0.135, south + 0.91)
        base.flat(parts, column, floor, grade + 3.52, PANEL)
        supports.append(column)
    return occupied, supports


def building(spec, field):
    outline = orient(Polygon(spec["footprint_enu_m"]))
    west, south, east, north = outline.bounds
    grade = geometry.sample_ground(field, spec["entry"]["east"], south)
    floor = (
        min(geometry.sample_ground(field, *p) for p in outline.exterior.coords) - 0.52
    )
    parts = []
    model = {"corner": corner, "gopuran": gopuran, "flock": flock, "duck": duck}[
        spec["role"]
    ]
    occupied, supports = model(parts, spec, outline, floor, grade)
    target = Point(
        spec["entry"]["east"], south + (1.74 if spec["role"] == "duck" else 0)
    )
    door, _ = nearest_points(occupied.boundary, target)
    e, n = door.coords[0]
    width = 1.7 if spec["role"] != "gopuran" else 1.38
    threshold = geometry.sample_ground(field, e, n) + 0.044
    gate = {
        "gate": spec["entry"]["gate"],
        "position_enu_m": [round(e, 4), round(n, 4)],
        "outward_degrees": 180,
        "threshold_z_m": round(threshold, 4),
        "width_m": width,
        "approach_distance_m": spec["entry"]["distance"],
        "snap_to_facade": False,
        "estimated": True,
    }
    mesh = tidy(parts)
    record = {
        **{k: spec[k] for k in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(occupied)],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [gate],
    }
    return mesh, record, occupied, supports


def tidy(parts):
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    return design.science.ordered_mesh(mesh)


def concrete_frame(parts, slab, field, levels):
    floor = min(geometry.sample_ground(field, *p) for p in slab.exterior.coords) - 0.40
    grade = levels[0]
    for z in levels:
        base.flat(
            parts, slab, z - 0.31, z, CONCRETE, FORM if z == levels[-1] else PAVING
        )
    for e in (-740.83, -734.04, -727.44, -721.24, -714.86, -708.90):
        for n in (15.65, 22.9, 30.0, 38.95, 45.68, 52.52, 59.41):
            pier = box(e - 0.26, n - 0.26, e + 0.26, n + 0.26)
            if slab.covers(pier):
                base.flat(parts, pier, floor, levels[-1] + 0.19, CONCRETE)
    for line, (length, add, _, plan, _, _) in facades(parts, slab):
        for z in levels[1:]:
            add(0.013, length - 0.013, -0.013, 0.09, z - 0.40, z - 0.21, FORM_EDGE)
        for d in np.arange(0.24, length - 0.12, 0.58):
            e, n = plan(d, -0.13)
            beam(parts, (e, n, levels[-1]), (e, n, levels[-1] + 1.07), 0.031, FENCE)
        for z in (levels[-1] + 0.21, levels[-1] + 0.54, levels[-1] + 1.03):
            beam(parts, (*plan(0, -0.13), z), (*plan(length, -0.13), z), 0.032, FENCE)
        if line.length > 16:
            for z, top in zip(levels, levels[1:]):
                for d in np.arange(0.43, length - 0.30, 0.70):
                    e, n = plan(d, -0.35)
                    beam(parts, (e, n, z), (e, n, top - 0.31), 0.035, FORM_EDGE)
                if z > grade:
                    for d in np.arange(0.25, length - 3.1, 6.1):
                        add(
                            d,
                            min(d + 2.6, length - 0.16),
                            -0.46,
                            -0.39,
                            z + 0.08,
                            z + 0.89,
                            METAL,
                        )


def construction(spec, limits, field):
    slab = Polygon(spec["slab_enu_m"])
    boxes = [box(*r) for r in spec["closed_boxes_enu_m"]]
    assert slab.difference(union_all(boxes)).area < 0.003
    assert limits.covers(slab) and all(limits.covers(r) for r in boxes)
    site = orient(limits.buffer(-0.45, join_style="mitre"))
    assert site.covers(slab)
    parts = [hospital.varied_yard(field, site)]
    for start, end in shared.face_edges(site):
        hospital.fence(parts, field, LineString((start, end)))
    grade = geometry.sample_ground(field, -718.25, 38.9)
    levels = [grade + h for h in spec["nominal_slab_rise_m"]]
    concrete_frame(parts, slab, field, levels)
    for e in np.arange(-740.55, -708.42, 0.34):
        lines = slab.buffer(-0.45).intersection(LineString(((e, 13.0), (e, 61.0))))
        for line in getattr(lines, "geoms", (lines,)):
            if line.geom_type == "LineString" and line.length > 0.45:
                a, b = line.coords[0], line.coords[-1]
                beam(
                    parts,
                    (*a, levels[-1] + 0.014),
                    (*b, levels[-1] + 0.014),
                    0.022,
                    FORM_EDGE,
                )
    for n in np.arange(15.3, 60.1, 0.71):
        lines = slab.buffer(-0.44).intersection(LineString(((-742, n), (-707.8, n))))
        for line in getattr(lines, "geoms", (lines,)):
            if line.geom_type == "LineString" and line.length > 0.45:
                a, b = line.coords[0], line.coords[-1]
                beam(
                    parts,
                    (*a, levels[-1] + 0.029),
                    (*b, levels[-1] + 0.029),
                    0.022,
                    FORM_EDGE,
                )
    hospital.tower_crane(parts, field, spec["crane_enu_m"])
    return parts, boxes, slab


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    meta = ROOT / "data/metadata"
    spec = json.loads((meta / f"{PACKAGE}.json").read_bytes())
    config_path, manifest_path = (
        SCENE / name for name in ("presentation.json", "manifest.json")
    )
    config, manifest = [
        json.loads(p.read_bytes()) for p in (config_path, manifest_path)
    ]
    field_path = SCENE / manifest["heightfield_url"]
    digest = design.tools.digest
    assert digest(manifest_path) == spec["source_manifest_sha256"]
    assert digest(field_path) == spec["source_heightfield_sha256"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    lots = {id: Polygon(ring) for id, ring in spec["taxlots_enu_m"].items()}
    limits = union_all([lots[id] for id in spec["site"]["lots"]])
    ground, closed, slab = construction(spec["site"], limits, field)
    meshes, records, plans, supports = {}, [], [], []
    for row in spec["models"]:
        shell, record, plan, piers = building(row, field)
        parcel = union_all([lots[id] for id in row["lots"]])
        footprint = Polygon(record["footprint_enu_m"])
        assert footprint.difference(parcel.buffer(0.12)).area < 1, row["id"]
        assert footprint.intersection(limits).area < 0.02, row["id"]
        meshes[row["id"]] = shell
        records.append(record)
        plans.append(plan)
        supports.extend(piers)
    sidewalk = Polygon(
        [(-706.99, 9.15), (-639.92, 8.82), (-639.96, 12.25), (-707.01, 12.82)]
    )
    ground.append(hospital.draped(field, sidewalk.difference(union_all(plans)), PAVING))
    assert all(
        a.intersection(b).area < 0.01
        for i, a in enumerate(plans)
        for b in plans[i + 1 :]
    )
    old_ids = {p["id"] for p in spec["source_ranges"]}
    original = union_all(
        [
            Polygon(r["footprint_enu_m"])
            for r in manifest["buildings"]
            if r["id"] in old_ids
        ]
    )
    check_routes = chapter.prior.nearby.shared.graduate.shared.check_routes
    count, clearance = check_routes(
        [*plans, *closed],
        supports,
        [r["entrances"][0] for r in records],
        original,
        manifest,
        graph,
        config,
        old_ids,
    )
    appearances = json.loads((meta / "campus-expansion-audit.json").read_bytes())
    patches = shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, appearances
    )
    output = args.stage or SCENE / PACKAGE
    output.mkdir(parents=True, exist_ok=True)
    model, descriptor = output / "site.glb", output / "site.json"
    terrain = tidy(ground)
    design.site.memorial.gerlinger.export(model, meshes, terrain, GROUND, GROUND)
    active_source = next(iter(old_ids - set(spec["retired_ids"])))
    result = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": digest(model),
        "buildings": records,
        "absorbed_ids": spec["retired_ids"],
        "split_buildings": {id: active_source for id in meshes if id != active_source},
        "batch_removals": patches,
        "closed_site_boxes_enu_m": spec["site"]["closed_boxes_enu_m"],
    }
    trees = spec.get("context_tree_removals", [])
    if trees:
        registered = {record["id"]: record for record in records}
        assert all(
            Polygon(
                registered[tree["overlapping_building_id"]]["footprint_enu_m"]
            ).covers(Point(tree["position_enu_m"]))
            for tree in trees
        )
        result["context_trees"] = [
            {k: tree[k] for k in ("index", "position_enu_m")} for tree in trees
        ]
    descriptor.write_text(
        json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf8",
        newline="\n",
    )
    if args.stage is None:
        config["alder_thirteenth_exterior_site"] = {
            "url": f"{PACKAGE}/site.json",
            "sha256": digest(descriptor),
        }
        config_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf8",
            newline="\n",
        )
    audit = {
        "buildings": records,
        "construction_parcels_m2": round(limits.area, 3),
        "construction_slab_m2": round(slab.area, 3),
        "triangles": {
            **{k: len(v.faces) for k, v in meshes.items()},
            GROUND: len(terrain.faces),
        },
        "route_edges": count,
        "nearest_route_m": round(clearance, 4),
        "removed_triangles": sum(b - a for a, b in (p["triangles"] for p in patches)),
        "batch_removals": patches,
        "glb_sha256": digest(model),
        "descriptor_sha256": digest(descriptor),
    }
    args.audit.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )
    print(audit["triangles"], count, clearance)


if __name__ == "__main__":
    main()
