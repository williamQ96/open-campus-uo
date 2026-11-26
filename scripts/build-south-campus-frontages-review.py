# SPDX-License-Identifier: Apache-2.0
"""Export six registered South University exteriors and their approaches."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import nearest_points
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
northwest = import_module("build-northwest-infill-exterior-review")
heritage = import_module("build-heritage-core-site-review")
garden, base, geometry = fairmount.garden, fairmount.base, fairmount.geometry
millrace, chapter = fairmount.millrace, fairmount.chapter
PACKAGE = "south-campus-frontages-review"
GROUND = "south-campus-frontage-walks"
STONE = (162, 149, 126)
BRICK = (150, 100, 75)
IRON = (68, 71, 65)
SHADE = (87, 72, 57)


def opening_face(edges, hint, bearing):
    target = Point(hint)
    face = LineString(garden.locate_face(edges, hint, bearing))
    point = nearest_points(face, target)[0]
    if point.distance(target) > 0.62 or face.length < 2.06:
        raise ValueError(f"Opening at {hint} does not meet a registered wall.")
    return face, point


def staircase(parts, plan, at, width, interval, grade, threshold, tread):
    inner, outer = interval
    steps = max(1, round((threshold - grade) / 0.155))
    for index in range(steps):
        stop = inner + (outer - inner) * (steps - index) / steps
        span = fairmount.rectangle(plan, at - width / 2, at + width / 2, inner, stop)
        base.flat(
            parts,
            span,
            grade - 0.22,
            grade + (threshold - grade) * (index + 1) / steps,
            tread,
        )
    if threshold - grade > 0.46:
        for side in (-1, 1):
            u = at + side * width * 0.51
            a, b = plan(u, outer), plan(u, inner + 0.11)
            fairmount.beam(
                parts, (*a, grade + 0.84), (*b, threshold + 0.84), 0.038, IRON
            )
            for t in np.linspace(0, 1, 4):
                p = a * (1 - t) + b * t
                z = grade * (1 - t) + threshold * t
                fairmount.beam(parts, (*p, z), (*p, z + 0.84), 0.031, IRON)


def paved_strip(parts, field, plan, center, width, first, last):
    def top(e, n):
        return geometry.sample_ground(field, e, n) + 0.085

    stations = np.linspace(first, last, max(2, int(np.ceil((last - first) / 0.55)) + 1))
    for near, far in zip(stations[:-1], stations[1:]):
        shape = orient(
            fairmount.rectangle(plan, center - width / 2, center + width / 2, near, far)
        )
        floor = min(top(*p) for p in shape.exterior.coords) - 0.11
        parts.append(geometry.shell(shape, floor, top, STONE, STONE))


def estimated_entry(paving, row, field, face, point):
    spec = row["entry"]
    _, _, _, plan = millrace.basis(paving, *face.coords)
    at, run = face.project(point), spec["stair_run_m"]
    threshold, width = spec["threshold_z_m"], spec["width_m"]
    paved_strip(paving, field, plan, at, width + 0.26, 0, spec["distance_m"])
    along = geometry.sample_ground(field, *plan(at, run)) + 0.12
    grade = min(along, threshold - 0.025)
    tread = BRICK if row["entry_finish"] == "theta-brick" else STONE
    staircase(paving, plan, at, width, (-0.08, run), grade, threshold, tread)
    if "street_steps_m" in row:
        interval = row["street_steps_m"]
        landing, foot = [
            geometry.sample_ground(field, *plan(at, distance)) + 0.075
            for distance in interval
        ]
        staircase(paving, plan, at, width + 0.12, interval, foot, landing, STONE)
    return {
        "gate": spec["gate"],
        "position_enu_m": [round(float(v), 5) for v in point.coords[0]],
        "outward_degrees": spec["bearing"],
        "threshold_z_m": threshold,
        "width_m": width,
        "approach_distance_m": spec["distance_m"],
        "estimated": True,
        "snap_to_facade": False,
    }


def theta_badge(parts, plan, at, lift):
    theta = [
        (at - 0.33 + 0.19 * np.cos(t), lift + 0.22 * np.sin(t))
        for t in np.linspace(0, np.pi * 2, 17)
    ]
    strokes = [
        theta,
        [(at - 0.45, lift), (at - 0.21, lift)],
        [(at + 0.06, lift - 0.22), (at + 0.45, lift + 0.22)],
        [(at + 0.06, lift + 0.22), (at + 0.45, lift - 0.22)],
    ]
    for stroke in strokes:
        for (u, z), (v, h) in zip(stroke, stroke[1:]):
            fairmount.beam(
                parts, (*plan(u, 0.051), z), (*plan(v, 0.051), h), 0.034, STONE
            )


def set_door(add, at, level, color, offset):
    def offset_add(left, right, inner, outer, bottom, top, material):
        add(left, right, inner + offset, outer + offset, bottom, top, material)

    millrace.door(offset_add, at, level, color)


def entry_details(parts, row, edge, span, add, plan, at, roof_at):
    trim, finish = row["trim_color"], row["entry_finish"]
    level = row["entry"]["threshold_z_m"]
    a, b = edge.coords
    if finish == "theta-brick":
        wall = Polygon(
            [
                (0.02, row["base_z_m"]),
                (span - 0.02, row["base_z_m"]),
                *[
                    (u, roof_at(plan(u, 0)) - 0.19)
                    for u in sorted(np.linspace(0.02, span - 0.02, 37), reverse=True)
                ],
            ]
        )
        heritage.profile(parts, a, b, wall, 0.029, BRICK)
        theta_badge(parts, plan, at, level + 7.14)
        northwest.window_grid(add, at, 1.35, level + 5.30, level + 6.53, 3, 2, IRON)
        northwest.window_grid(add, at, 0.71, level + 8.00, level + 9.15, 2, 2, IRON)
        add(at - 0.91, at + 0.91, 0.031, 0.093, level, level + 2.30, SHADE)
        set_door(add, at, level, IRON, 0.09)
    elif finish == "delta-arch":
        outer = chapter.arch(at, level - 0.06, 3.30, 3.43, 0.90)
        opening = chapter.arch(at, level, 2.91, 3.18, 0.75)
        heritage.profile(parts, a, b, opening, 0.045, SHADE)
        heritage.profile(parts, a, b, outer.difference(opening), 0.088, STONE)
        set_door(add, at, level, trim, 0.047)
        northwest.window_grid(add, at, 1.18, level + 4.65, level + 5.92, 3, 2, trim)
    elif finish == "alley-pair":
        for center in (at - 0.64, at + 0.64):
            add(center - 0.49, center + 0.49, 0.019, 0.074, level, level + 2.08, trim)
            for z in np.arange(level + 0.16, level + 1.92, 0.155):
                add(center - 0.38, center + 0.38, 0.074, 0.094, z, z + 0.015, SHADE)
    elif finish == "potter-recess":
        for center in (at - 0.57, at + 0.57):
            add(center - 0.45, center + 0.45, 0.012, 0.068, level, level + 2.13, trim)
            add(
                center - 0.37,
                center + 0.37,
                0.063,
                0.096,
                level + 0.035,
                level + 2.07,
                (161, 153, 84),
            )
            add(
                center - 0.21,
                center + 0.21,
                0.095,
                0.11,
                level + 1.35,
                level + 1.86,
                SHADE,
            )
        add(
            at - 1.14,
            at + 1.14,
            -0.078,
            1.63,
            level + 2.24,
            level + 2.39,
            trim,
        )
    else:
        millrace.door(add, at, level, trim)
        chapter.gabled_canopy(
            parts,
            plan,
            at,
            0.77,
            -0.075,
            0.84,
            level + 2.26,
            0.38,
            row["roof_color"],
            trim,
        )


def garage_front(paving, field, add, plan, center, garage, trim):
    level, width = garage["level_z_m"], garage["width_m"]
    left, right = center - width / 2, center + width / 2
    paved_strip(paving, field, plan, center, width + 0.22, -0.03, 6.0)
    add(left - 0.10, right + 0.10, 0.014, 0.065, level - 0.06, level + 2.46, trim)
    for index in range(6):
        bottom = level + 0.398 * index
        add(left, right, 0.065, 0.096, bottom, bottom + 0.377, SHADE)
        for x in np.linspace(left + 0.30, right - 0.30, 6):
            add(
                x - 0.22,
                x + 0.22,
                0.096,
                0.113,
                bottom + 0.08,
                bottom + 0.29,
                (111, 92, 73),
            )
    for shift in (-1.53, -0.73, 0.07):
        northwest.window_grid(
            add, center + shift, 0.63, level + 3.34, level + 4.58, 1, 3, trim
        )


def facades(parts, row, wall, roof_at, entrance, entry_point, field, paving):
    trim = row["trim_color"]
    garage_face = garage_point = None
    garage = row.get("garage")
    if garage:
        garage_face, garage_point = opening_face(
            list(garden.shared.face_edges(wall)), garage["near"], garage["bearing"]
        )
    for edge, (span, add, _, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.39:
            continue
        entry_at = edge.project(entry_point) if edge.equals(entrance) else None
        garage_at = (
            edge.project(garage_point) if garage and edge.equals(garage_face) else None
        )
        low, *other_levels = row["levels_z_m"]
        band = row.get("brick_band_z_m", low - 0.08)
        seam = row["seam_color"]
        finish = row["entry_finish"]
        is_theta_gable = entry_at is not None and finish == "theta-brick"
        is_delta_gable = entry_at is not None and finish == "delta-arch"
        top = min(roof_at(plan(u, 0)) for u in np.linspace(0.06, span - 0.06, 7)) - 0.19
        if not is_theta_gable and "brick_base" in row:
            add(
                0.02,
                span - 0.02,
                0.009,
                0.027,
                row["base_z_m"],
                band,
                row["brick_base"],
            )
            add(0.02, span - 0.02, 0.025, 0.055, band - 0.04, band + 0.048, trim)
        if not is_theta_gable:
            if row["siding"] == "vertical":
                step = 0.23 if finish == "theta-brick" else 0.27
                for u in np.arange(0.11, span - 0.07, step):
                    add(
                        u,
                        u + 0.015,
                        0.011,
                        0.022,
                        band,
                        roof_at(plan(u, 0)) - 0.18,
                        seam,
                    )
            elif row["siding"] in ("horizontal", "brick"):
                step = 0.18 if row["siding"] == "horizontal" else 0.263
                millrace.siding(add, span, top, low - 0.21, seam, step)
        count = max(1, round(span / row["bay_pitch_m"]))
        centers = (np.arange(count) + 0.5) * span / count
        for index, floor in enumerate((low, *other_levels)):
            for u in centers:
                if is_theta_gable or is_delta_gable or garage_at is not None:
                    continue
                if index == 0 and entry_at is not None and abs(u - entry_at) < 1.85:
                    continue
                width = min(row["window_width_m"], span / count * 0.62)
                if finish == "potter-recess" and index == 0:
                    width *= 1.27
                limit = (
                    min(roof_at(plan(u + d * width / 2, 0)) for d in (-1, 0, 1)) - 0.24
                )
                z = floor + (0.59 if index == 0 else 0.61)
                northwest.window_grid(
                    add, u, width, z, min(z + 1.32, limit), 2, 2, trim
                )
        if entry_at is not None:
            entry_details(parts, row, edge, span, add, plan, entry_at, roof_at)
        if garage_at is not None:
            garage_front(paving, field, add, plan, garage_at, garage, trim)


def build(row, field, paving):
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = outline.buffer(-row["eaves_m"], join_style="mitre")
    if "entry_recess_enu_m" in row:
        wall = wall.difference(box(*row["entry_recess_enu_m"]))
    wall = orient(wall)
    parts = []
    roof_at = garden.roof_sections(
        parts, outline, wall, row["base_z_m"], row, grid=0.0002
    )
    for spec in row.get("dormers", []):
        fairmount.dormer(parts, row, spec, roof_at, outline)
    if "chimney" in row:
        e, n, width, depth, rise = row["chimney"]
        shape = orient(box(e - width / 2, n - depth / 2, e + width / 2, n + depth / 2))
        height = roof_at((e, n))
        base.flat(parts, shape, height - 0.48, height + rise, BRICK, STONE)
    spec = row["entry"]
    face, point = opening_face(
        list(garden.shared.face_edges(wall)), spec["near"], spec["bearing"]
    )
    facades(parts, row, wall, roof_at, face, point, field, paving)
    gate = estimated_entry(paving, row, field, face, point)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    return (
        mesh,
        {
            **{key: row[key] for key in ("id", "name", "street_address")},
            "footprint_enu_m": base.ring(outline),
            "ground_footprints_enu_m": [base.ring(wall)],
            "support_collision_enu_m": [],
            "base_z_m": row["base_z_m"],
            "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
            "area_m2": round(outline.area, 3),
            "entrances": [gate],
        },
        wall,
        [],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "south_campus_frontages_site", build
    )


if __name__ == "__main__":
    main()
