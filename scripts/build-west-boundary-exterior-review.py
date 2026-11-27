# SPDX-License-Identifier: Apache-2.0
"""Rebuild the East 17th and East 19th Avenue boundary exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
northwest = import_module("build-northwest-infill-exterior-review")
neighborhood = import_module("build-neighborhood-exterior-closeout-review")
garden, base, chapter = fairmount.garden, fairmount.base, fairmount.chapter
geometry, millrace = fairmount.geometry, fairmount.millrace
PACKAGE = "west-boundary-exterior-review"
GROUND = "west-boundary-approaches"
BRICK = (157, 99, 76)
RECESS = (129, 79, 64)
CEMENT = (165, 162, 145)
DARK = (66, 81, 78)


def roof_eyebrow(parts, row, easting, north, roof_at):
    z = roof_at((easting, north))
    _, _, _, _, _, slab = chapter.setup_face(
        parts, (easting - 1.1, north), (easting + 1.1, north)
    )
    opening = chapter.arch(1.1, z - 0.075, 1.52, 0.34, 0.28)
    trim = opening.buffer(0.054)
    slab(trim, -0.12, 0.013, row["trim_color"])
    slab(opening, 0.013, 0.027, DARK)
    for offset in (-0.28, 0.0, 0.28):
        x = easting + offset
        fairmount.beam(
            parts,
            (x, north - 0.035, z - 0.064),
            (x, north - 0.035, z + 0.171),
            0.025,
            row["trim_color"],
        )


def duplex(parts, row, wall, field, roof_at, gate_point):
    trim = row["trim_color"]
    for line, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.6 or line.centroid.x < -999.75 and abs(normal[0]) > 0.9:
            continue
        ground = geometry.sample_ground(field, *plan(span / 2, 0))
        top = min(roof_at(plan(u, 0)) for u in np.linspace(0.1, span - 0.1, 5))
        add(0.02, span - 0.02, 0.006, 0.043, ground - 0.12, ground + 0.22, CEMENT)
        pitch = 0.31 if normal[1] < -0.9 else 0.28
        for u in np.arange(pitch, span - 0.1, pitch):
            if normal[1] < -0.9:
                add(
                    u,
                    u + 0.013,
                    0.008,
                    0.021,
                    ground + 0.22,
                    top - 0.13,
                    (129, 129, 105),
                )
        count = max(1, round(span / 2.5))
        for u in np.linspace(span * 0.20, span * 0.81, count):
            p = Point(plan(u, 0))
            if p.distance(gate_point) < 1.08 or top < ground + 2.38:
                continue
            northwest.window_grid(
                add, u, min(1.26, span * 0.54), ground + 1.10, ground + 2.24, 2, 2, trim
            )
    supports = []
    for west, south, east, north in row["porch_recesses_enu_m"]:
        pad = orient(box(west + 0.12, south + 0.22, east - 0.05, north + 0.02))
        level = geometry.sample_ground(field, *pad.centroid.coords[0]) + 0.22
        base.flat(parts, pad, level - 0.29, level, CEMENT)
        for x in (west + 0.19, east - 0.17):
            if x < -999.91:
                continue
            post = orient(box(x - 0.062, south + 0.28, x + 0.062, south + 0.41))
            cap = roof_at(post.centroid.coords[0]) - 0.145
            base.flat(parts, post, level - 0.01, cap, trim)
            supports.append(post)
    for e, n in row["eyebrows_enu_m"]:
        roof_eyebrow(parts, row, e, n, roof_at)
    chimney = orient(box(*row["chimney_enu_m"]))
    z = roof_at(chimney.centroid.coords[0])
    base.flat(parts, chimney, z - 0.1, z + 1.06, BRICK)
    base.flat(
        parts, chimney.buffer(0.075, join_style="mitre"), z + 1.02, z + 1.18, RECESS
    )
    return supports


def alley(parts, row, wall, field, roof_at):
    trim = row["trim_color"]
    for line, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.60 or line.centroid.x < -999.75:
            continue
        z = geometry.sample_ground(field, *plan(span / 2, 0))
        top = min(roof_at(plan(u, 0)) for u in (0.12, span / 2, span - 0.12))
        add(0.015, span - 0.015, 0.008, 0.039, z - 0.16, z + 0.57, CEMENT)
        if row["style"] == "alley-flat":
            add(0.02, span - 0.02, 0.01, 0.05, top - 0.32, top - 0.20, trim)
            if normal[1] > 0.9:
                northwest.window_grid(add, span * 0.71, 1.09, 1.73, 2.80, 2, 2, trim)
            elif normal[0] > 0.9 and span > 3.30:
                for u in (span * 0.23, span * 0.71):
                    northwest.window_grid(add, u, 1.14, 1.62, 2.71, 2, 2, trim)
        elif abs(normal[0]) > 0.9 and span > 3.0:
            for u in np.linspace(span * 0.19, span * 0.81, 4):
                northwest.window_grid(add, u, 0.91, z + 1.19, z + 2.26, 2, 1, trim)


def alley_gallery(parts, row, wall, field, roof_at):
    trim = row["trim_color"]
    metal = (66, 71, 62)
    gallery = row["gallery"]
    supports = []
    for line, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 2 or line.centroid.x < -999.75:
            continue
        grade = geometry.sample_ground(field, *plan(span / 2, 0))
        level = grade + gallery["rise_m"]
        top = min(roof_at(plan(u, 0)) for u in np.linspace(0.12, span - 0.12, 6))
        add(0.026, span - 0.026, 0.007, 0.038, grade - 0.12, grade + 0.18, CEMENT)
        add(0.02, span - 0.02, 0.01, 0.086, level - 0.07, level + 0.045, trim)
        for u in np.arange(0.12, span - 0.08, 0.19):
            add(u, u + 0.018, 0.013, 0.026, level + 0.026, top - 0.17, (163, 158, 132))
        if normal[0] > 0.95 and span > 13:
            start, stop = gallery["start_m"], gallery["stop_m"]
            inner, outer = 0.015, gallery["deck_depth_m"]
            # This wall runs south to north, and the photographed stair descends south.
            first, last = span - stop, span - start
            neighborhood.gallery(
                parts, plan, first, last, inner, outer, level, field, (trim, metal)
            )
            for at in (first + 0.11, last - 0.13):
                supports.append(
                    fairmount.rectangle(
                        plan, at - 0.073, at + 0.073, outer - 0.22, outer - 0.074
                    )
                )
            stair_foot = span - gallery["stair_from_m"]
            stair_top = span - gallery["stair_to_m"]
            neighborhood.exterior_stairs(
                parts,
                plan,
                stair_foot,
                stair_top,
                inner,
                outer,
                grade,
                level,
                (112, 109, 92),
                metal,
            )
            for u in (span - 2.58, span - 6.97):
                millrace.door(add, u, level + 0.035, trim)
            for u in (span - 4.20, span - 9.57):
                neighborhood.window(
                    add, span, u, 1.28, level + 0.78, 1.22, top, trim, 1
                )
            for u in (span - 2.59, span - 6.50, span - 11.10):
                neighborhood.window(
                    add, span, u, 1.04, grade + 0.78, 1.29, top, trim, 1
                )
        elif normal[1] < -0.94:
            for u in (span * 0.24, span * 0.62):
                neighborhood.window(
                    add, span, u, 1.19, level + 0.76, 1.17, top, trim, 1
                )
            neighborhood.window(
                add, span, span * 0.27, 0.75, grade + 0.94, 1.05, top, trim, 1
            )
        else:
            for u in (span * 0.26, span * 0.72):
                neighborhood.window(
                    add, span, u, 0.94, level + 0.74, 1.09, top, trim, 1
                )
    return supports


def church(parts, row, wall, field, roof_at):
    trim = row["trim_color"]
    course = row["cladding_break_z_m"]
    for line, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.8 or line.centroid.x <= -999.7 and abs(normal[0]) > 0.9:
            continue
        grade = geometry.sample_ground(field, *plan(span / 2, 0))
        top = min(roof_at(plan(u, 0)) for u in np.linspace(0.12, span - 0.12, 5))
        for z in np.arange(course + 0.24, top - 0.23, 0.23):
            add(0.027, span - 0.027, 0.012, 0.028, z, z + 0.018, (159, 150, 129))
        add(0.014, span - 0.014, 0.014, 0.052, course - 0.08, course + 0.06, trim)
        if normal[1] < -0.90 and span > 13.0:
            for u in np.linspace(0.45, span - 0.36, 6):
                add(u - 0.22, u + 0.22, 0.012, 0.27, grade - 0.12, course, BRICK)
            for u in np.linspace(span * 0.13, span * 0.85, 5):
                add(
                    u - 1.09,
                    u + 1.09,
                    0.012,
                    0.052,
                    grade + 0.19,
                    course - 0.39,
                    RECESS,
                )
        if normal[0] > 0.90 and span > 13.0:
            at = span * 0.32
            add(
                at - 1.1,
                at + 1.1,
                0.021,
                0.067,
                grade + 0.08,
                course - 0.64,
                (181, 139, 117),
            )
        if normal[1] > 0.90 and span > 9.0 and line.centroid.y > -690:
            for u in (span * 0.17, span * 0.84):
                millrace.door(add, u, grade + 0.09, DARK)
            northwest.window_grid(
                add, span * 0.61, 2.46, grade + 0.07, grade + 2.46, 4, 3, DARK
            )
            add(span * 0.25, span * 0.39, 0.014, 0.091, 3.12, 3.83, DARK)
            for z in np.linspace(3.19, 3.77, 7):
                add(span * 0.25, span * 0.39, 0.090, 0.115, z, z + 0.023, trim)

    east, west, north = row["clerestory_east_west_north_m"]
    span, add, *_ = chapter.setup_face(parts, (east, north), (west, north))
    for u in np.linspace(0.81, span - 0.92, 8):
        northwest.window_grid(add, u, 0.23, 6.58, 7.54, 1, 1, trim)

    shaft = orient(box(*row["tower_enu_m"]))
    roof = row["tower_z_m"]
    base.flat(parts, shaft, 5.65, roof, trim, row["roof_color"])
    base.flat(
        parts, shaft.buffer(0.086, join_style="mitre"), roof - 0.10, roof + 0.05, trim
    )
    for _, (span, add, normal, _, _, _) in fairmount.views(parts, shaft):
        if normal[1] > 0.85 or normal[0] > 0.85:
            mid = span / 2
            add(mid - 0.10, mid + 0.10, 0.009, 0.066, roof - 1.89, roof - 0.62, DARK)
            add(mid - 0.35, mid + 0.35, 0.009, 0.066, roof - 1.05, roof - 0.85, DARK)


def model(row, field, paving):
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
    for recess in row.get("porch_recesses_enu_m", []):
        wall = orient(wall.difference(box(*recess)))
    floor, _ = garden.science.earlier.fit_base(field, wall)
    parts = []
    wall_base = floor
    if "cladding_break_z_m" in row:
        wall_base = row["cladding_break_z_m"]
        base.flat(parts, wall, floor, wall_base, BRICK)
    roof_at = garden.roof_sections(parts, outline, wall, wall_base, row, grid=0.0002)
    gate, _, point, supports = fairmount.entrance(parts, row, wall, field, paving)
    if row["style"] == "duplex":
        supports.extend(duplex(parts, row, wall, field, roof_at, point))
    elif row["style"] == "church":
        church(parts, row, wall, field, roof_at)
    elif row["style"] == "alley-gallery":
        supports.extend(alley_gallery(parts, row, wall, field, roof_at))
    else:
        alley(parts, row, wall, field, roof_at)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    return (
        mesh,
        {
            **{key: row[key] for key in ("id", "name", "street_address")},
            "footprint_enu_m": base.ring(outline),
            "ground_footprints_enu_m": [base.ring(p) for p in geometry.sections(wall)],
            "support_collision_enu_m": [base.ring(p) for p in supports],
            "area_m2": round(outline.area, 3),
            "base_z_m": round(floor, 4),
            "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
            "entrances": [gate] if gate else [],
        },
        wall,
        supports,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "west_boundary_exterior_site", model
    )


if __name__ == "__main__":
    main()
