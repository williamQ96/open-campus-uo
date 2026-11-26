# SPDX-License-Identifier: Apache-2.0
"""Build the Parkside Place and three south neighborhood exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
northwest = import_module("build-northwest-infill-exterior-review")
garden, geometry, base = fairmount.garden, fairmount.geometry, fairmount.base
chapter, millrace = fairmount.chapter, fairmount.millrace
PACKAGE = "hilyard-south-exterior-review"
GROUND = "hilyard-south-approaches"
CONCRETE = (143, 143, 133)
IRON = (61, 67, 64)
BRICK = (153, 99, 77)
WOOD = (143, 95, 63)
GARAGE = (67, 83, 87)


def local_top(roof_at, plan, start, end):
    return min(roof_at(plan(at, 0)) for at in (start, (start + end) / 2, end))


def courses(add, start, stop, level, top, spacing, color):
    for z in np.arange(level + spacing, top - 0.06, spacing):
        add(start, stop, 0.015, 0.03, z, z + 0.012, color)


def bay_window(parts, plan, center, width, bottom, head, row):
    depth = 0.57
    positions = [
        plan(center - width / 2, 0),
        plan(center - width * 0.37, depth),
        plan(center + width * 0.37, depth),
        plan(center + width / 2, 0),
    ]
    footprint = orient(Polygon(positions))
    base.flat(parts, footprint, bottom - 0.23, bottom, row["trim_color"])
    for line, (span, add, normal, _, _, _) in fairmount.views(parts, footprint):
        if (abs(normal[0]) < 0.08 and normal[1] > 0) or line.length < 0.35:
            continue
        add(0, span, -0.05, 0.018, bottom, head, row["trim_color"])
        columns = 4 if span > 1.2 else 1
        northwest.window_grid(
            add,
            span / 2,
            span - 0.13,
            bottom + 0.075,
            head - 0.065,
            columns,
            3,
            row["trim_color"],
        )
    chapter.gabled_canopy(
        parts,
        plan,
        center,
        width * 0.54,
        -0.015,
        depth + 0.105,
        head + 0.06,
        row["bay_roof_rise_m"],
        row["roof_color"],
        row["trim_color"],
    )


def bungalow(parts, row, wall, field, roof_at, gate_edge, gate_point):
    bay = Point(row["bay_enu_m"])
    bay_edge = LineString(
        garden.locate_face(list(garden.shared.face_edges(wall)), bay, 180)
    )
    trim = row["trim_color"]
    shade = np.rint(np.array(row["wall_color"]) * 0.91).astype(int)
    for line, (span, add, _, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.5:
            continue
        grade = geometry.sample_ground(field, *plan(span / 2, 0))
        top = local_top(roof_at, plan, 0.12, span - 0.12)
        courses(add, 0.025, span - 0.025, grade + 0.34, top - 0.13, 0.18, shade)
        add(0.01, span - 0.01, 0.007, 0.042, grade - 0.24, grade + 0.31, CONCRETE)
        door_at = line.project(gate_point) if line.equals(gate_edge) else -10
        bay_at = line.project(bay) if line.equals(bay_edge) else -10
        positions = row["bay_and_window_dims_m"]
        if bay_at > 0:
            width, sill, head = positions
            bay_window(parts, plan, bay_at, width, sill, head, row)
            if row.get("porch"):
                vent = roof_at(plan(bay_at, 0)) - 0.89
                add(bay_at - 0.18, bay_at + 0.18, 0.01, 0.055, vent - 0.31, vent, trim)
                for slat in np.linspace(vent - 0.26, vent - 0.048, 5):
                    add(
                        bay_at - 0.129,
                        bay_at + 0.129,
                        0.052,
                        0.074,
                        slat,
                        slat + 0.022,
                        (123, 125, 111),
                    )
        count = max(1, round(span / 2.70))
        for u in ((i + 0.5) * span / count for i in range(count)):
            if abs(u - door_at) < 1.3 or abs(u - bay_at) < positions[0] / 2 + 0.75:
                continue
            if top - grade > 2.38:
                northwest.window_grid(
                    add,
                    u,
                    min(1.18, span * 0.54),
                    grade + 1.08,
                    grade + 2.19,
                    2,
                    2,
                    trim,
                )
    if "chimney_enu_m" in row:
        chimney = orient(box(*row["chimney_enu_m"]))
        z = roof_at(chimney.centroid.coords[0])
        base.flat(parts, chimney, z - 0.28, z + 1.10, row["chimney_color"])
        base.flat(
            parts,
            chimney.buffer(0.09, join_style="mitre"),
            z + 1.10,
            z + 1.23,
            row["chimney_color"],
        )


def contemporary(parts, row, field, outline, wall, roof_at):
    trim = row["trim_color"]
    split = row["cladding_break_z_m"]
    for _, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.75:
            continue
        grade = geometry.sample_ground(field, *plan(span / 2, 0))
        top = local_top(roof_at, plan, 0.12, span - 0.12)
        courses(add, 0.02, span - 0.02, split, top, 0.25, (147, 157, 158))
        add(0.04, span - 0.04, 0.01, 0.08, split - 0.12, split + 0.04, trim)
        for u in (span * 0.33, span * 0.70):
            if top > split + 2.13:
                northwest.window_grid(
                    add, u, 0.58, split + 0.65, top - 0.47, 1, 3, trim
                )
            if normal[1] > -0.8 and span > 3.3:
                northwest.window_grid(
                    add, u, 1.05, grade + 1.03, grade + 2.03, 2, 1, trim
                )
    for entry in row["parapet_equipment_enu_m"]:
        vent = orient(box(*entry))
        assert outline.covers(vent)
        z = roof_at(vent.centroid.coords[0])
        base.flat(parts, vent, z - 0.04, z + 0.21, trim, (155, 158, 155))
    # The dated southeast view shows the dark timber lower elevation below the
    # projecting upper box. The visible glazing stays in this recessed wall.
    a, b = row["recess_face_enu_m"]
    span, add, _, _, _, _ = chapter.setup_face(parts, a, b)
    level = row["recess_threshold_z_m"]
    door_at = span * 0.61
    millrace.door(add, door_at, level, (95, 73, 51))
    northwest.window_grid(
        add, span * 0.23, span * 0.31, level + 0.35, level + 2.02, 2, 2, trim
    )
    a, b = row["upper_front_face_enu_m"]
    span, add, _, plan, _, _ = chapter.setup_face(parts, a, b)
    top = local_top(roof_at, plan, 0.12, span - 0.12)
    courses(add, 0.018, span - 0.018, split, top - 0.18, 0.25, (147, 157, 158))
    for u in (span * 0.31, span * 0.73):
        northwest.window_grid(add, u, 0.52, split + 0.51, top - 0.49, 1, 3, trim)


def parkside_windows(parts, row, wall, field, roof_at):
    trim = row["trim_color"]
    west, _, east, north = row["garage_cut_enu_m"]
    entry = Point(row["entry"]["near"])
    for _, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.35:
            continue
        e, n = plan(span / 2, 0)
        if west - 0.05 <= e <= east + 0.05 and n <= north + 0.05:
            continue
        z = geometry.sample_ground(field, e, n)
        top = local_top(roof_at, plan, 0.12, span - 0.12)
        for top_slab in row["floor_lines_z_m"]:
            if z + 0.4 < top_slab < top - 0.45:
                add(0.018, span - 0.018, 0.017, 0.065, top_slab - 0.11, top_slab, trim)
        courses(add, 0.02, span - 0.02, z + 0.25, top - 0.19, 0.23, (132, 148, 123))
        if span < 2.55:
            continue
        count = max(1, round(span / (3.70 if abs(normal[0]) > 0.85 else 4.85)))
        for index in range(count):
            u = span * (index + 0.5) / count
            center = Point(plan(u, 0))
            band = local_top(roof_at, plan, u - 0.54, u + 0.54)
            for sill in row["window_sills_z_m"]:
                if sill < z + 1.6 and center.distance(entry) < 1.1:
                    continue
                if sill > z + 0.35 and sill + 1.28 < band - 0.26:
                    northwest.window_grid(add, u, 1.05, sill, sill + 1.28, 2, 2, trim)


def balcony(parts, bounds, level):
    area = orient(box(*bounds))
    base.flat(parts, area, level - 0.23, level, CONCRETE)
    front = next(
        (a, b)
        for a, b in garden.shared.face_edges(area)
        if np.isclose(a[1], area.bounds[1]) and np.isclose(b[1], area.bounds[1])
    )
    fairmount.balustrade(parts, *front, level, IRON)
    for e in (area.bounds[0] + 0.09, area.bounds[2] - 0.09):
        fairmount.balustrade(
            parts, (e, area.bounds[1]), (e, area.bounds[3]), level, IRON
        )


def parkside_end_bay(parts, row):
    east, south, north, sill, eave, rise = row["east_gabled_bay"]
    span, add, _, plan, _, _ = chapter.setup_face(parts, (east, south), (east, north))
    pad = fairmount.rectangle(plan, 0, span, -0.36, 0.76)
    base.flat(parts, pad, sill, eave, row["wall_color"])
    chapter.gabled_canopy(
        parts,
        plan,
        span / 2,
        span / 2 + 0.16,
        -0.88,
        0.89,
        eave,
        rise,
        row["roof_color"],
        row["trim_color"],
    )
    _, add_front, _, _, _, _ = chapter.setup_face(
        parts, plan(0, 0.76), plan(span, 0.76)
    )
    northwest.window_grid(
        add_front, span * 0.55, 1.22, sill + 0.47, sill + 1.82, 2, 2, row["trim_color"]
    )
    for u in np.arange(0.16, span - 0.08, 0.19):
        if abs(u - span * 0.55) > 0.66:
            add_front(
                u, u + 0.014, 0.009, 0.027, sill + 0.03, eave - 0.07, (132, 148, 123)
            )


def parkside_access(parts, row, field, paving):
    west, _, east, north = row["garage_cut_enu_m"]
    center = (west + east) / 2
    start = row["garage_ramp_south_m"]
    start_z = geometry.sample_ground(field, center, start) + 0.09
    floor = row["garage_visible_floor_m"]

    def ramp_top(e, n):
        grade = geometry.sample_ground(field, e, n) + 0.031
        return max(grade, np.interp(n, (start, north), (start_z, floor)))

    panels = np.linspace(start, north, 15)
    for a, b in zip(panels[:-1], panels[1:]):
        pad = box(west + 0.11, a, east - 0.11, b)
        z = min(ramp_top(e, n) for e, n in pad.exterior.coords) - 0.09
        paving.append(geometry.shell(pad, z, ramp_top, CONCRETE, (101, 103, 101)))
    for x in (west, east):
        wall = orient(box(x - 0.105, start, x + 0.105, north))
        base.flat(parts, wall, floor - 0.24, floor + 1.03, CONCRETE)
        fairmount.balustrade(parts, (x, start), (x, north), floor + 1.02, IRON)
    threshold = geometry.sample_ground(field, center, north) + 0.06
    shutter = orient(box(west + 0.07, north - 0.05, east - 0.07, north + 0.075))
    base.flat(parts, shutter, threshold - 0.18, threshold + 1.54, GARAGE)
    span, add, _, _, _, _ = chapter.setup_face(
        parts, (west, north - 0.05), (east, north - 0.05)
    )
    courses(
        add, 0.14, span - 0.14, threshold + 0.09, threshold + 1.47, 0.20, (88, 95, 95)
    )
    south = row["garage_fascia_n_m"]
    fascia = orient(box(west - 0.10, south - 0.085, east + 0.10, south + 0.04))
    soffit = row["raised_wall_bottom_z_m"]
    base.flat(parts, fascia, soffit - 0.27, soffit + 0.04, row["trim_color"])
    bulkhead = orient(box(west + 0.05, north - 0.36, east - 0.05, north - 0.08))
    base.flat(parts, bulkhead, threshold + 1.49, soffit, row["wall_color"])
    for bounds, levels in row["balconies"]:
        for level in levels:
            balcony(parts, bounds, level)


def model(row, field, paving):
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    roof = outline
    if "porch_box_enu_m" in row:
        roof = orient(roof.difference(box(*row["porch_box_enu_m"])))
    wall = orient(roof.buffer(-row["eaves_m"], join_style="mitre"))
    cut = row.get("garage_cut_enu_m") or row.get("lower_recess_enu_m")
    top_row = row
    if cut:
        notch = box(*cut)
        raised = orient(set_precision(wall.intersection(notch), 0.002))
        wall = orient(set_precision(wall.difference(notch), 0.002))
        top_row = {**row, "raised_wall_enu_m": list(raised.exterior.coords)}
    floor, _ = garden.science.earlier.fit_base(field, wall)
    parts = []
    shell_base = floor
    if row["style"] == "contemporary":
        shell_base = row["cladding_break_z_m"]
        base.flat(parts, wall, floor, shell_base, WOOD)
    roof_at = garden.roof_sections(parts, roof, wall, shell_base, top_row, grid=0.0002)
    gate, edge, point, supports = fairmount.entrance(parts, row, wall, field, paving)
    if row["style"] == "parkside":
        parkside_windows(parts, row, wall, field, roof_at)
        parkside_end_bay(parts, row)
        parkside_access(parts, row, field, paving)
        west, _, east, north = row["garage_cut_enu_m"]
        south = row["garage_ramp_south_m"]
        supports.extend([box(e - 0.10, south, e + 0.10, north) for e in (west, east)])
    elif row["style"] == "contemporary":
        contemporary(parts, row, field, outline, wall, roof_at)
    else:
        bungalow(parts, row, wall, field, roof_at, edge, point)
        if gate:
            _, _, _, plan = millrace.basis(parts, *edge.coords)
            center = edge.project(point)
            level = gate["threshold_z_m"]
            for stop, top in (
                (1.45, level),
                (1.72, level - 0.15),
                (1.97, level - 0.30),
            ):
                stair = fairmount.rectangle(plan, center - 0.80, center + 0.80, 0, stop)
                base.flat(parts, stair, level - 0.66, top, BRICK)
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
        parser.parse_args(), PACKAGE, GROUND, "hilyard_south_exterior_site", model
    )


if __name__ == "__main__":
    main()
