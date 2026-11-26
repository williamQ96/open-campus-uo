# SPDX-License-Identifier: Apache-2.0
"""Export the Sigma Chi, 1456/1458 and 1355 East 19th Avenue exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
northwest = import_module("build-northwest-infill-exterior-review")
garden, geometry, base = fairmount.garden, fairmount.geometry, fairmount.base
beam, chapter = fairmount.beam, fairmount.chapter
PACKAGE = "east-nineteenth-exterior-review"
GROUND = "east-nineteenth-approaches"
STEEL = (60, 68, 66)
BRICK = (136, 108, 90)
CONCRETE = (170, 164, 146)
WHITE = (213, 209, 188)
BALCONY = (122, 145, 146)
SASH = (186, 192, 181)


def railing(parts, a, b, floor):
    a, b = np.array(a), np.array(b)
    for p in np.linspace(a, b, max(2, round(np.linalg.norm(b - a) / 1.15))):
        beam(parts, (*p, floor), (*p, floor + 0.88), 0.032, STEEL)
    for height in (0.10, 0.88):
        beam(parts, (*a, floor + height), (*b, floor + height), 0.042, STEEL)


def pier(parts, plan, at, depth, ground, ceiling, color, width=0.12):
    footprint = fairmount.rectangle(
        plan, at - width / 2, at + width / 2, depth - width / 2, depth + width / 2
    )
    base.flat(parts, footprint, ground, ceiling, color)
    return footprint


def chapter_house(parts, row, wall, field, roof_at, paving):
    split = row["upper_floor_m"]
    gate, line, point, supports = fairmount.entrance(parts, row, wall, field, paving)
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 2.20:
            continue
        center = plan(span / 2, 0)
        grade = geometry.sample_ground(field, *center)
        at = edge.project(point) if edge.equals(line) else -10
        middle = -38.0 < center[0] < -21.8 and -782.0 < center[1] < -755.5
        add(0.018, span - 0.018, 0.012, 0.082, split - 0.16, split + 0.03, STEEL)
        count = max(1, round(span / 3.32))
        pitch = span / count
        for i in range(count):
            u = (i + 0.5) * pitch
            reach = pitch * 0.32
            top = min(roof_at(plan(x, 0)) for x in (u - reach, u + reach))
            if abs(u - at) > 1.28 and not middle:
                cladding = (152, 136, 113) if normal[1] > 0.9 else (128, 117, 101)
                add(u - reach, u + reach, 0.009, 0.033, grade, split - 0.22, cladding)
                add(
                    u + reach + 0.10,
                    u + reach + 0.30,
                    0.027,
                    0.045,
                    grade + 0.16,
                    split - 0.28,
                    (64, 82, 82),
                )
            if middle:
                fairmount.millrace.door(add, u, split + 0.036, STEEL)
                northwest.window_grid(
                    add, u, pitch * 0.56, grade + 0.89, split - 0.35, 3, 2, STEEL
                )
            elif top > split + 0.98:
                northwest.window_grid(
                    add, u, pitch * 0.68, top - 1.47, top - 0.32, 2, 2, (133, 142, 135)
                )
            if i + 1 < count:
                x = (i + 1) * pitch
                add(
                    x - 0.084,
                    x + 0.084,
                    0.031,
                    0.139,
                    grade,
                    roof_at(plan(x, 0)) - 0.14,
                    STEEL,
                )
                add(x + 0.12, x + 0.16, 0.078, 0.121, grade + 0.52, split + 1.82, STEEL)
        if middle:
            add(0.028, span - 0.028, -0.07, 1.45, split - 0.24, split, CONCRETE)
            railing(parts, plan(0.075, 1.36), plan(span - 0.075, 1.36), split)
            for x in np.linspace(0.42, span - 0.42, max(2, count // 2)):
                supports.append(
                    pier(parts, plan, x, 1.31, grade - 0.09, split - 0.18, STEEL, 0.16)
                )
    _, add, _, plan = fairmount.millrace.basis(parts, *line.coords)
    at = line.project(point)
    height = gate["threshold_z_m"]
    add(at - 2.40, at + 2.40, -0.05, 4.90, split - 0.48, split - 0.19, STEEL)
    add(at - 2.65, at + 2.65, -0.05, 4.96, split - 0.26, split - 0.14, CONCRETE)
    for u in (at - 2.14, at + 2.14):
        grade = geometry.sample_ground(field, *plan(u, 4.60))
        supports.append(pier(parts, plan, u, 4.60, grade - 0.12, split - 0.27, STEEL))
        northwest.window_grid(
            add, at + (u - at) * 0.63, 0.86, height + 0.24, height + 2.10, 1, 2, STEEL
        )
    for e, n, width, height in row["roof_vents"]:
        shape = orient(box(e - width / 2, n - width / 2, e + width / 2, n + width / 2))
        z = roof_at((e, n))
        base.flat(parts, shape, z - 0.17, z + height, (135, 138, 130))
        base.flat(
            parts,
            shape.buffer(0.08, join_style="mitre"),
            z + height - 0.13,
            z + height + 0.06,
            STEEL,
        )
    return [gate], supports


def duplex(parts, row, wall, field, roof_at):
    land = row["porch_floor_m"]
    ch = row["chimney_enu_m"]
    base.flat(
        parts,
        box(ch[0] - 0.30, ch[1] - 0.36, ch[0] + 0.30, ch[1] + 0.36),
        roof_at(ch) - 0.32,
        roof_at(ch) + 1.07,
        BRICK,
        CONCRETE,
    )
    for _, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.88:
            continue
        grade = geometry.sample_ground(field, *plan(span / 2, 0))
        top = min(roof_at(plan(x, 0)) for x in np.linspace(0.08, span - 0.08, 5))
        add(0.022, span - 0.022, 0.008, 0.028, grade - 0.11, grade + 0.28, BRICK)
        for z in np.arange(grade + 0.34, top - 0.28, 0.166):
            add(0.015, span - 0.015, 0.008, 0.017, z, z + 0.012, (153, 158, 141))
        if normal[1] > 0.9 and plan(span / 2, 0)[0] > 20.3:
            continue
        count = max(1, round(span / (3.5 if normal[1] > 0.9 else 4.2)))
        for i in range(count):
            u = (i + 0.5) * span / count
            width = min(span / count - 0.31, 2.26 if normal[1] > 0.9 else 1.15)
            northwest.window_grid(
                add,
                u,
                width,
                land + 0.76,
                land + 2.03,
                3 if normal[1] > 0.9 else 2,
                2,
                WHITE,
            )
    x, n = row["porch_center_enu_m"]
    edge = garden.locate_face(list(garden.shared.face_edges(wall)), (x, n), 0)
    _, add, _, plan, _, _ = chapter.setup_face(parts, *edge)
    at = LineString(edge).project(Point(x, n))
    fairmount.millrace.door(add, at, land, WHITE)
    top = land + 2.88
    pad = fairmount.rectangle(plan, at - 1.60, at + 1.52, -0.04, 1.83)
    base.flat(parts, pad, land - 0.32, land, CONCRETE)
    stair_base = geometry.sample_ground(field, *plan(at, 3.65))
    fairmount.landing(parts, lambda u, d: plan(u, d + 1.77), at, row, land, stair_base)
    supports = []
    for u in (at - 1.39, at + 1.33):
        grade = geometry.sample_ground(field, *plan(u, 1.68))
        supports.append(
            pier(parts, plan, u, 1.68, grade - 0.13, land + 1.06, BRICK, 0.46)
        )
        pier(parts, plan, u, 1.68, land + 1.03, top, WHITE, 0.24)
    add(at - 1.82, at + 1.77, -0.08, 1.98, top - 0.14, top, WHITE)
    return [], supports


def parking_level(parts, row, wall, field, paving, floor):
    occupied = wall.difference(
        unary_union([box(*coords) for coords in row["parking_open_enu_m"]])
    )
    for section in geometry.sections(occupied):
        base.flat(parts, orient(section), floor, row["parking_ceiling_m"], BRICK)
    east, north = row["driveway_from_enu_m"]
    paving_shape = box(east - 2.60, north - 4.95, east + 2.60, north + 8.0)
    fairmount.millrace.western.terrace(paving, field, orient(paving_shape))
    supports = [
        orient(box(x - 0.15, n - 0.15, x + 0.15, n + 0.15))
        for x, n in row["parking_posts_enu_m"]
    ]
    for post in supports:
        z = geometry.sample_ground(field, *post.centroid.coords[0])
        base.flat(parts, post, z - 0.14, row["parking_ceiling_m"] + 0.04, CONCRETE)
    return occupied, supports


def apartment(parts, row, wall, roof_at):
    band = row["parking_ceiling_m"]
    for _, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if normal[0] < -0.94:
            stations = [span * f for f in (0.0, 0.49, 0.54, 1.0)]
            levels = row["west_balcony_levels_m"]
            for (left, right), level in zip(
                ((stations[0], stations[1]), (stations[2], stations[3])), levels
            ):
                add(left, right, -0.065, 1.58, level - 0.26, level, BALCONY)
                railing(parts, plan(left, 1.52), plan(right, 1.52), level)
                for x in np.linspace(left + 1.19, right - 1.26, 3):
                    fairmount.millrace.door(add, x, level + 0.012, (101, 128, 131))
                    a, b = (
                        (x + 1.12, x + 2.15)
                        if x + 2.3 < right
                        else (x - 2.01, x - 1.11)
                    )
                    northwest.window_grid(
                        add, (a + b) / 2, b - a, level + 0.42, level + 1.85, 2, 1, SASH
                    )
            low, high = [
                (plan(x, 0.77), level) for x, level in zip(stations[1:3], levels)
            ]
            if low[1] > high[1]:
                low, high = high, low
            northwest.stair(parts, low[0], high[0], low[1], high[1], 1.04, steps=3)
        else:
            count = 2 if abs(normal[1]) > 0.9 else max(1, round(span / 4.65))
            stations = (
                np.linspace(span * 0.35, span * 0.65, count)
                if count == 2
                else np.linspace(1.25, span - 1.25, count)
            )
            for u in stations:
                top = roof_at(plan(u, 0))
                for sill, height in ((band + 0.94, 1.46), (band + 3.86, 0.86)):
                    if top - 0.28 > sill + height:
                        northwest.window_grid(
                            add, u, 1.72, sill, sill + height, 2, 1, SASH
                        )
            if normal[1] < -0.9:
                add(0.03, span - 0.03, -0.075, 1.01, band - 0.18, band + 0.13, BALCONY)
                for left, right in ((0.07, 2.04), (span - 2.04, span - 0.07)):
                    top = min(roof_at(plan(u, 0)) for u in (left, right))
                    add(
                        left,
                        right,
                        0.006,
                        0.020,
                        band + 0.15,
                        top - 0.18,
                        (186, 183, 163),
                    )
        for u in np.arange(0.22, span - 0.31, 2.94):
            top = roof_at(plan(u, 0))
            add(
                u - 0.028,
                u + 0.028,
                0.008,
                0.025,
                band + 0.14,
                top - 0.16,
                (148, 150, 140),
            )
        if normal[0] < -0.94:
            for u in np.linspace(1.43, span - 1.43, 7):
                sill = roof_at(plan(u, 0)) - 1.32
                northwest.window_grid(add, u, 1.45, sill, sill + 0.57, 2, 1, SASH)


def build(row, field, paving):
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
    if "open_porch_enu_m" in row:
        wall = orient(wall.difference(box(*row["open_porch_enu_m"])))
    floor, _ = garden.science.earlier.fit_base(field, wall)
    parts = []
    kind = row["kind"]
    roof_at = garden.roof_sections(
        parts, outline, wall, row.get("parking_ceiling_m", floor), row, grid=0.0002
    )
    solid = wall
    if kind == "chapter":
        gates, supports = chapter_house(parts, row, wall, field, roof_at, paving)
    elif kind == "duplex":
        gates, supports = duplex(parts, row, wall, field, roof_at)
    else:
        solid, supports = parking_level(parts, row, wall, field, paving, floor)
        apartment(parts, row, wall, roof_at)
        gates = []
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{key: row[key] for key in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [
            base.ring(orient(p)) for p in geometry.sections(solid)
        ],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": gates,
    }
    return mesh, record, solid, supports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "east_nineteenth_exterior_site", build
    )
