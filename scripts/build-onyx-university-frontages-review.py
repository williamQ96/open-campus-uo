# SPDX-License-Identifier: Apache-2.0
"""Export the eight Onyx and University Street exterior reviews."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision, union_all
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh


southern = import_module("build-southern-boundary-exterior-review")
parking = import_module("build-east-nineteenth-exterior-review")
harris, potter, frontages = southern.harris, southern.potter, southern.frontages
fairmount, garden = southern.fairmount, southern.garden
base, geometry, millrace = southern.base, southern.geometry, southern.millrace
northwest, chapter = southern.northwest, southern.chapter
PACKAGE = "onyx-university-frontages-review"
GROUND = "onyx-university-approaches"
CONCRETE = (166, 159, 139)
STONE = (119, 111, 94)
IRON = (64, 69, 62)
GLASS = (73, 100, 111)


def roof_sections(parts, outline, wall, level, row):
    lower_zones = row.get("lower_roof")
    if not lower_zones:
        return garden.roof_sections(parts, outline, wall, level, row, grid=0.0002)
    lower_areas = [box(*zone["bounds_m"]) for zone in lower_zones]
    segments = [outline.difference(union_all(lower_areas))]
    segments.extend(outline.intersection(area) for area in lower_areas)
    roof_sets = [row["roof_zones"], *[[zone] for zone in lower_zones]]
    views = []
    for segment, zones in zip(segments, roof_sets):
        for piece in geometry.sections(segment):
            at = garden.roof_sections(
                parts,
                piece,
                wall.intersection(piece),
                level,
                {**row, "roof_zones": zones},
                grid=0.0002,
            )
            views.append((piece, at))

    def height(point):
        return min(views, key=lambda pair: pair[0].distance(Point(point)))[1](point)

    return height


def stacked_arch(parts, edge, add, plan, at, level, trim):
    add(at - 1.03, at + 1.03, 0.01, 0.092, level - 0.15, level + 6.51, (197, 180, 143))
    for z, w, h, fill in (
        (level + 0.017, 1.11, 2.28, (69, 78, 72)),
        (level + 3.39, 1.05, 1.77, GLASS),
    ):
        outer = chapter.arch(at, z - 0.04, w + 0.2, h + 0.20, 0.44)
        inner = chapter.arch(at, z, w, h, 0.38)
        frontages.heritage.profile(
            parts, *edge.coords, outer.difference(inner), 0.148, trim
        )
        frontages.heritage.profile(parts, *edge.coords, inner, 0.12, fill)
    add(at - 0.73, at + 0.73, 0.037, 0.51, level + 3.29, level + 3.42, STONE)
    parking.railing(parts, plan(at - 0.67, 0.47), plan(at + 0.67, 0.47), level + 3.39)
    for u in (at - 0.67, at + 0.67):
        parking.railing(parts, plan(u, 0.097), plan(u, 0.47), level + 3.39)
    add(at + 0.28, at + 0.33, 0.151, 0.18, level + 0.88, level + 1.02, trim)


GLYPHS = {
    "T": (((0, 1), (1, 1)), ((0.5, 1), (0.5, 0))),
    "R": (
        ((0, 0), (0, 1), (0.84, 1), (1, 0.79), (0.84, 0.55), (0, 0.55)),
        ((0.46, 0.55), (1, 0)),
    ),
    "I": (((0, 1), (1, 1)), ((0.5, 1), (0.5, 0)), ((0, 0), (1, 0))),
    "N": (((0, 0), (0, 1), (1, 0), (1, 1)),),
    "Y": (((0, 1), (0.5, 0.49), (1, 1)), ((0.5, 0.49), (0.5, 0))),
    "H": (((0, 0), (0, 1)), ((1, 0), (1, 1)), ((0, 0.5), (1, 0.5))),
    "O": (
        (
            (0.2, 0),
            (0, 0.18),
            (0, 0.83),
            (0.2, 1),
            (0.8, 1),
            (1, 0.83),
            (1, 0.18),
            (0.8, 0),
            (0.2, 0),
        ),
    ),
    "U": (((0, 1), (0, 0.17), (0.2, 0), (0.8, 0), (1, 0.17), (1, 1)),),
    "S": (
        (
            (1, 1),
            (0.14, 1),
            (0, 0.8),
            (0.13, 0.56),
            (0.86, 0.44),
            (1, 0.2),
            (0.87, 0),
            (0, 0),
        ),
    ),
    "E": (((1, 1), (0, 1), (0, 0), (1, 0)), ((0, 0.5), (0.83, 0.5))),
    "1": (((0.12, 0.79), (0.5, 1), (0.5, 0)), ((0.1, 0), (0.88, 0))),
    "9": (
        (
            (0.2, 0),
            (0.85, 0.2),
            (1, 0.6),
            (0.84, 1),
            (0.18, 1),
            (0, 0.79),
            (0.18, 0.57),
            (1, 0.6),
        ),
    ),
    "3": (
        (
            (0, 1),
            (0.82, 1),
            (1, 0.82),
            (0.79, 0.55),
            (0.32, 0.51),
            (0.83, 0.46),
            (1, 0.19),
            (0.78, 0),
            (0, 0),
        ),
    ),
}


def inscription(parts, plan, text, center, z, depth, color):
    for index, letter in enumerate(text):
        u = center + (index - (len(text) - 1) / 2) * 0.248 - 0.09
        for stroke in GLYPHS[letter]:
            points = [(*plan(u + x * 0.18, depth), z + y * 0.22) for x, y in stroke]
            for a, b in zip(points, points[1:]):
                fairmount.beam(parts, a, b, 0.025, color)


def name_panel(parts, add, plan, center, z):
    add(center - 1.08, center + 1.08, 0.016, 0.10, z - 0.47, z + 0.53, (211, 199, 157))
    add(center - 1.01, center + 1.01, 0.10, 0.119, z - 0.40, z + 0.46, (230, 220, 178))
    for text, height in (("TRINITY", z + 0.095), ("HOUSE", z - 0.23)):
        inscription(parts, plan, text, center, height, 0.127, (55, 81, 78))


def face_details(parts, row, wall, field, height, face, point):
    trim, seam = row["trim_color"], row["seam_color"]
    levels = row["levels_z_m"]
    supports = []
    sign = row.get("sign")
    columns = row.get("column_front")
    cladding = row.get("cladding")
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 0.72:
            continue
        center = edge.project(point) if edge.equals(face) else None
        top = min(height(plan(u, 0)) for u in np.linspace(0.035, span - 0.035, 7))
        ground = geometry.sample_ground(field, *plan(span / 2, 0))
        if cladding in ("brick", "lap"):
            pitch = 0.093 if cladding == "brick" else 0.178
            millrace.siding(
                add, span, top - 0.18, max(ground - 0.1, levels[0] - 0.46), seam, pitch
            )
        if cladding == "board":
            add(
                0.023,
                span - 0.023,
                0.009,
                0.119,
                levels[0] - 0.03,
                levels[0] + 0.29,
                seam,
            )
            if normal[0] < -0.97 and span > 8.0:
                inscription(
                    parts, plan, "1931", span * 0.51, levels[0] + 0.009, 0.134, IRON
                )
            for u in np.arange(0.12, span - 0.09, 0.54):
                z = height(plan(u, 0))
                add(
                    u - 0.018, u + 0.018, 0.013, 0.047, levels[0] + 0.28, z - 0.18, seam
                )
        sign_at = None
        if sign and normal[0] < -0.97 and edge.distance(Point(sign[:2])) < 0.38:
            sign_at = edge.project(Point(sign[:2]))
            name_panel(parts, add, plan, sign_at, sign[2])
        if center is not None:
            if row.get("stacked_arch"):
                stacked_arch(
                    parts, edge, add, plan, center, row["entry"]["threshold_z_m"], trim
                )
            else:
                supports.extend(
                    harris.entry_details(parts, row, field, edge, add, plan, center)
                )
        if columns and normal[0] > 0.97 and edge.distance(Point(columns)) < 0.40:
            u = edge.project(Point(columns))
            add(u - 1.59, u + 1.59, 0.013, 1.25, 25.27, 25.48, trim)
            for x in (u - 1.34, u, u + 1.34):
                xy = plan(x, 1.06)
                z = geometry.sample_ground(field, *xy)
                supports.append(
                    parking.pier(
                        parts, plan, x, 1.06, z - 0.08, 25.32, trim, width=0.29
                    )
                )
        if span < 1.47:
            continue
        count = max(1, round(span / row["bay_m"]))
        width = min(span / count * 0.66, 1.44)
        for u in (np.arange(count) + 0.5) * span / count:
            if sign_at is not None and abs(u - sign_at) < 1.56:
                continue
            e, n = plan(u, 0)
            for i, z in enumerate(levels):
                if (
                    center is not None
                    and abs(u - center) < (1.78 if row.get("stacked_arch") else 1.37)
                    and (not i or row.get("stacked_arch"))
                ):
                    continue
                if (
                    i
                    and normal[1] > 0.96
                    and any(abs(e - x) < 1.28 for x in row.get("north_bays", []))
                ):
                    continue
                sill = z + (0.70 if cladding == "board" else 0.68)
                cap = (
                    min(height(plan(p, 0)) for p in (u - width / 2, u, u + width / 2))
                    - 0.27
                )
                head = min(cap, sill + (1.06 if cladding == "board" else 1.28))
                if (
                    sill > geometry.sample_ground(field, e, n) + 0.23
                    and head - sill > 0.43
                ):
                    northwest.window_grid(
                        add,
                        u,
                        width,
                        sill,
                        head,
                        2,
                        1 if cladding == "board" else 2,
                        trim,
                    )
        if normal[1] > 0.96:
            for x in row.get("north_bays", []):
                pos = Point(x, edge.interpolate(0.5, normalized=True).y)
                u = edge.project(pos)
                if 0.66 < u < span - 0.66 and pos.distance(edge) < 0.32:
                    low = levels[1] + 0.61
                    add(
                        u - 0.72,
                        u + 0.72,
                        0.014,
                        0.205,
                        low - 0.13,
                        low + 1.47,
                        row["wall_color"],
                    )

                    def projecting(a, b, near, far, z0, z1, color):
                        add(a, b, near + 0.205, far + 0.205, z0, z1, color)

                    northwest.window_grid(
                        projecting, u, 1.26, low, low + 1.28, 2, 2, trim
                    )
    return supports


def retaining(paving, field, west, east, n, rise):
    walls = []
    palette = [STONE, (110, 109, 99), (123, 116, 101), (125, 118, 102)]
    stops = np.linspace(west, east, max(2, round((east - west) / 0.70)))
    for index, (a, b) in enumerate(zip(stops, stops[1:])):
        section = orient(box(a, n - 0.13, b, n + 0.20))
        grade = geometry.sample_ground(field, (a + b) / 2, n)
        base.flat(
            paving, section, grade - 0.16, grade + rise, palette[index % 4], STONE
        )
        walls.append(section)
    return walls


def stepped_front_windows(parts, row):
    west, east, north = row["upper_front"]
    _, add, _, _ = millrace.basis(parts, (west, north), (east, north))
    trim = row["trim_color"]
    for at in (2.02, 5.67):
        lo = row["levels_z_m"][1] + 0.69
        northwest.window_grid(add, at, 1.29, lo, lo + 1.21, 2, 2, trim)
        for x in (at - 0.79, at + 0.79):
            add(x - 0.105, x + 0.105, 0.01, 0.067, lo - 0.01, lo + 1.24, IRON)


def parking_bays(parts, row, wall, field):
    ceiling = row["parking_ceiling_m"]
    occupied = wall.difference(box(*row["parking_cut"]))
    for footprint in geometry.sections(occupied):
        base.flat(
            parts, orient(footprint), row["base_z_m"], ceiling + 0.015, (140, 129, 112)
        )
    supports = []
    for e, n in row["parking_posts"]:
        post = orient(box(e - 0.145, n - 0.155, e + 0.145, n + 0.155))
        grade = geometry.sample_ground(field, e, n)
        if ceiling - grade < 2.1:
            raise ValueError("Parking opening is too short for the observed bays.")
        base.flat(parts, post, grade - 0.12, ceiling + 0.06, CONCRETE)
        supports.append(post)
    return occupied, supports


def north_fence(parts, field, west, east, n):
    for e in np.arange(west + 0.07, east - 0.025, 0.166):
        board = box(e - 0.074, n - 0.052, e + 0.074, n + 0.052)
        z = geometry.sample_ground(field, e, n)
        base.flat(parts, board, z - 0.07, z + 1.62, (141, 108, 78))
    return orient(box(west, n - 0.06, east, n + 0.06))


def build(row, field, paving):
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = outline.buffer(-row["eaves_m"], join_style="mitre")
    if "recess" in row:
        wall = wall.difference(box(*row["recess"]))
    wall = orient(wall)
    parts = []
    level = row.get("parking_ceiling_m", row["base_z_m"])
    height = roof_sections(parts, outline, wall, level, row)
    entry = row.get("entry")
    face, point = potter.choose_face(wall, entry) if entry else (None, None)
    supports = face_details(parts, row, wall, field, height, face, point)
    occupied = wall
    if "parking_cut" in row:
        occupied, posts = parking_bays(parts, row, wall, field)
        supports.extend(posts)
    if "driveway" in row:
        driveway = orient(box(*row["driveway"]))
        millrace.western.terrace(paving, field, driveway)
    if "north_fence" in row:
        supports.append(north_fence(parts, field, *row["north_fence"]))
    if "upper_front" in row:
        stepped_front_windows(parts, row)
    if "retaining" in row:
        supports.extend(retaining(paving, field, *row["retaining"]))
    if "chimney" in row:
        e, n, w, d, rise = row["chimney"]
        top = height((e, n))
        base.flat(
            parts,
            box(e - w / 2, n - d / 2, e + w / 2, n + d / 2),
            top - 0.36,
            top + rise,
            row["wall_color"],
            STONE,
        )
    if "attic" in row:
        e, n = row["attic"]
        z = height((e, n))
        shelf = orient(box(e - 1.26, n - 0.42, e + 1.26, n + 0.66))
        base.flat(
            parts, shelf, z - 0.42, z + 0.24, row["wall_color"], row["roof_color"]
        )
        northwest.window_grid(
            millrace.basis(parts, (e + 1.26, n + 0.66), (e - 1.26, n + 0.66))[1],
            1.26,
            1.93,
            z - 0.20,
            z + 0.16,
            3,
            1,
            row["trim_color"],
        )
    if "split_retaining" in row:
        n = point.y + row["split_retaining"]
        supports.extend(
            retaining(paving, field, point.x - 5.58, point.x - 0.82, n, 0.47)
        )
        supports.extend(
            retaining(paving, field, point.x + 0.82, point.x + 4.5, n, 0.47)
        )
    gates = (
        [
            frontages.estimated_entry(
                paving, {**row, "entry_finish": "stone"}, field, face, point
            )
        ]
        if entry and entry["route"]
        else []
    )
    if entry and not entry["route"]:
        _, _, _, plan = millrace.basis(paving, *face.coords)
        frontages.paved_strip(
            paving, field, plan, face.project(point), 1.68, -0.14, 2.22
        )
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{key: row[key] for key in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [
            base.ring(orient(p)) for p in geometry.sections(occupied)
        ],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": row["base_z_m"],
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": gates,
    }
    return mesh, record, occupied, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "onyx_university_frontages_site", build
    )


if __name__ == "__main__":
    main()
