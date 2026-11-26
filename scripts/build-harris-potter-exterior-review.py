# SPDX-License-Identifier: Apache-2.0
"""Export ten individually registered Harris, Potter and East 20th buildings."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient
import trimesh

potter = import_module("build-potter-university-exterior-review")
fairmount, garden = potter.fairmount, potter.garden
base, geometry, millrace = potter.base, potter.geometry, potter.millrace
northwest, chapter = potter.northwest, potter.chapter
frontages = potter.frontages
PACKAGE = "harris-potter-exterior-review"
GROUND = "harris-potter-approaches"
CONCRETE = (160, 150, 128)
FENCE = (123, 94, 70)


def entry_details(parts, row, field, edge, add, plan, center):
    spec = row["entry"]
    level, trim = spec["threshold_z_m"], row["trim_color"]
    if "arched_door" in row:
        a, b = edge.coords
        surround = chapter.arch(center, level, 1.38, 2.47, 0.42)
        inside = chapter.arch(center, level + 0.04, 1.16, 2.29, 0.38)
        frontages.heritage.profile(parts, a, b, inside, 0.080, (112, 85, 67))
        frontages.heritage.profile(
            parts, a, b, surround.difference(inside), 0.119, trim
        )
        add(
            center + 0.33, center + 0.39, 0.083, 0.143, level + 0.96, level + 1.09, trim
        )
    else:
        potter.door(add, center, level, row.get("door_color", trim))
    if "porch" in row:
        return potter.porch(parts, row, field, plan, center, level)
    return []


def paneled_front(add, span, floor, high, trim):
    add(0.026, span - 0.026, 0.017, 0.126, high - 0.24, high - 0.10, trim)
    for fraction in (0.19, 0.49, 0.79):
        u = span * fraction
        panel = span * 0.15
        add(
            u - panel / 2,
            u + panel / 2,
            0.018,
            0.048,
            floor - 0.28,
            high - 0.21,
            (197, 184, 160),
        )
        for low in (floor + 0.43, floor + 3.16):
            northwest.window_grid(
                add, u, panel * 0.84, low, low + 1.45, 2, 1, (215, 207, 182)
            )


def garage_front(add, plan, center, field, garage):
    width, color = garage["width_m"], garage["color"]
    level = geometry.sample_ground(field, *plan(center, 0.12)) + 0.045
    left, right = center - width / 2, center + width / 2
    add(left - 0.10, right + 0.10, 0.015, 0.076, level, level + 2.13, CONCRETE)
    for z in level + 0.05 + np.arange(7) * 0.286:
        add(left, right, 0.077, 0.096, z, z + 0.255, color)


def facades(parts, row, wall, field, height, entrance, entrance_point):
    supports = []
    floor, *upper = row["levels_z_m"]
    garage = row.get("garage")
    garage_face, garage_point = (
        potter.choose_face(wall, garage) if garage else (None, None)
    )
    trim, seam = row["trim_color"], row["seam_color"]
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        center = edge.project(entrance_point) if edge.equals(entrance) else None
        if center is not None:
            supports.extend(entry_details(parts, row, field, edge, add, plan, center))
        if span < 1.33:
            continue
        top = min(height(plan(u, 0)) for u in np.linspace(0.035, span - 0.035, 9))
        if row.get("frontage_fields"):
            if normal[0] < -0.96 and span >= 5:
                paneled_front(add, span, floor, top, trim)
                continue
            add(0.021, span - 0.021, 0.014, 0.081, top - 0.23, top - 0.10, trim)
        else:
            millrace.siding(add, span, top - 0.18, floor - 0.42, seam, 0.183)
        garage_at = (
            edge.project(garage_point) if garage and edge.equals(garage_face) else None
        )
        if garage_at is not None:
            garage_front(add, plan, garage_at, field, garage)
        count = max(1, round(span / row.get("bay_pitch_m", row["bay_m"])))
        for at in (np.arange(count) + 0.5) * span / count:
            width = min(span / count * 0.61, 1.22)
            if center is not None and row.get("front_picture_windows"):
                width = min(span / count * 0.72, 1.94)
            ceiling = (
                min(height(plan(v, 0)) for v in (at - width / 2, at, at + width / 2))
                - 0.24
            )
            for index, low in enumerate((floor, *upper)):
                if not index and (
                    (center is not None and abs(at - center) < 1.31)
                    or (
                        garage_at is not None
                        and abs(at - garage_at) < garage["width_m"] * 0.57
                    )
                ):
                    continue
                sill = low + (0.66 if index else 0.77)
                northwest.window_grid(
                    add,
                    at,
                    width,
                    sill,
                    min(sill + 1.20, ceiling),
                    3 if width > 1.65 else 2,
                    2,
                    trim,
                )
    return supports


def fence(parts, row, field):
    west, east, n = row["fence_enu_m"]
    step = 0.151
    for e in np.arange(west, east - step, step):
        grade = geometry.sample_ground(field, e, n)
        base.flat(
            parts,
            box(e, n - 0.052, e + step - 0.014, n + 0.034),
            grade - 0.07,
            grade + 1.55,
            FENCE,
        )
    for e in np.linspace(west, east, 6):
        grade = geometry.sample_ground(field, e, n)
        base.flat(
            parts,
            box(e - 0.058, n - 0.07, e + 0.058, n + 0.065),
            grade - 0.1,
            grade + 1.64,
            FENCE,
        )
    return orient(box(west - 0.06, n - 0.07, east + 0.06, n + 0.065))


def street_stair(paving, field, edge, point, row):
    spec = row["street_landing"]
    _, _, _, plan = millrace.basis(paving, *edge.coords)
    at = edge.project(point)
    inner, outer, top = spec["inner_m"], spec["outer_m"], spec["level_z_m"]
    foot = geometry.sample_ground(field, *plan(at, outer)) + 0.07
    width = 1.52
    frontages.staircase(paving, plan, at, width, (inner, outer), foot, top, CONCRETE)
    start = row["entry"]["stair_run_m"] - 0.17
    first = plan(at, start)
    pitch = (top - geometry.sample_ground(field, *first) - 0.10) / (inner - start)
    origin, target = np.asarray(plan(at, inner)), np.asarray(first)
    vector = (origin - target) / (inner - start)
    walk = fairmount.rectangle(plan, at - width / 2, at + width / 2, start, inner)
    paving.append(
        geometry.shell(
            orient(walk),
            foot - 0.2,
            lambda e, n: top + pitch * (np.asarray([e, n]) - origin).dot(vector),
            CONCRETE,
            CONCRETE,
        )
    )
    walls = []
    for a, b in ((at - 4.35, at - 0.94), (at + 0.94, at + 4.7)):
        shape = orient(fairmount.rectangle(plan, a, b, outer - 0.34, outer - 0.02))
        z = min(geometry.sample_ground(field, *p) for p in shape.exterior.coords)
        base.flat(paving, shape, z - 0.18, top - 0.025, (111, 105, 91), CONCRETE)
        walls.append(shape)
    return walls


def build(row, field, paving):
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = outline.buffer(-row["eaves_m"], join_style="mitre")
    if "covered_recess_enu_m" in row:
        wall = wall.difference(box(*row["covered_recess_enu_m"]))
    wall = orient(wall)
    parts = []
    height = garden.roof_sections(
        parts, outline, wall, row["base_z_m"], row, grid=0.0002
    )
    spec = row["entry"]
    entrance, point = (
        potter.choose_face(wall, spec, 1.35 if row.get("narrow_front") else 2.1)
        if spec
        else (None, None)
    )
    supports = facades(parts, row, wall, field, height, entrance, point)
    for item in row.get("dormers", []):
        fairmount.dormer(parts, row, item, height, outline)
    if "chimney" in row:
        e, n, width, depth, rise, color = row["chimney"]
        z = height((e, n))
        plan = box(e - width / 2, n - depth / 2, e + width / 2, n + depth / 2)
        base.flat(parts, plan, z - 0.28, z + rise, color, CONCRETE)
    if "fence_enu_m" in row:
        supports.append(fence(parts, row, field))
    for e, n in row.get("canopy_posts_enu_m", []):
        pier = orient(box(e - 0.095, n - 0.095, e + 0.095, n + 0.095))
        z = geometry.sample_ground(field, e, n)
        base.flat(parts, pier, z - 0.09, height((e, n)) - 0.09, CONCRETE)
        supports.append(pier)
    gates = (
        [
            frontages.estimated_entry(
                paving, {**row, "entry_finish": "stone"}, field, entrance, point
            )
        ]
        if spec
        else []
    )
    if "street_landing" in row:
        supports.extend(street_stair(paving, field, entrance, point, row))
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{key: row[key] for key in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(wall)],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": row["base_z_m"],
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": gates,
    }
    return mesh, record, wall, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "harris_potter_exterior_site", build
    )


if __name__ == "__main__":
    main()
