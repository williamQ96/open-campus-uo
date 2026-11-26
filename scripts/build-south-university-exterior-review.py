# SPDX-License-Identifier: Apache-2.0
"""Export Sigma Nu, 1306 East 18th and 1874 Emerald."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision, union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import nearest_points
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
northwest = import_module("build-northwest-infill-exterior-review")
garden, base, geometry = fairmount.garden, fairmount.base, fairmount.geometry
millrace = fairmount.millrace
PACKAGE = "south-university-exterior-review"
GROUND = "south-university-entry-walks"
CONCRETE = (156, 151, 136)
WOOD = (146, 99, 74)


def solid_box(parts, bounds, bottom, top, color):
    outline = orient(box(*bounds))
    base.flat(parts, outline, bottom, top, color)
    return outline


def height_at(roof_at, plan, center, half_width):
    return min(
        roof_at(plan(i, 0)) for i in (center - half_width, center, center + half_width)
    )


def select_entry(wall, entry):
    near = Point(entry["near_enu_m"])
    face = garden.locate_face(
        list(garden.shared.face_edges(wall)), near, entry["bearing"]
    )
    edge = LineString(face)
    point = nearest_points(edge, near)[0]
    if point.distance(near) > 1.05:
        raise ValueError(f"Approach {entry['gate']} misses its facade.")
    return edge, point


def pedestrian_approach(paving, row, field, face, point):
    entry = row["entry"]
    _, _, _, plan = millrace.basis(paving, *face.coords)
    at = face.project(point)
    z = (
        millrace.approach(paving, field, point, entry["distance_m"], entry["bearing"])
        - 0.08
    )
    local = geometry.sample_ground(field, *plan(at, 0.65))
    threshold = entry["level_z_m"]
    fairmount.landing(
        paving, plan, at, row, threshold, min(threshold - 0.035, local, z)
    )
    return {
        "gate": entry["gate"],
        "position_enu_m": [round(value, 5) for value in point.coords[0]],
        "outward_degrees": entry["bearing"],
        "threshold_z_m": threshold,
        "width_m": entry["width_m"],
        "approach_distance_m": entry["distance_m"],
        "estimated": True,
        "snap_to_facade": False,
    }


def facade(
    parts, row, wall, roof_at, entry_face=None, entry_point=None, upper_only=False
):
    trim, seam = row["trim_color"], row["siding_color"]
    for face, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 2.15:
            continue
        chosen = face.equals(entry_face) if entry_face is not None else False
        door = face.project(entry_point) if chosen else None
        if chosen:
            level = row["entry"]["level_z_m"]
            if row["kind"] == "sigma":
                add(door - 1.30, door + 1.30, 0.011, 0.066, level, level + 2.55, trim)
                for offset in (-0.38, 0.38):
                    u = door + offset
                    add(
                        u - 0.35,
                        u + 0.35,
                        0.066,
                        0.091,
                        level + 0.04,
                        level + 2.08,
                        (106, 94, 78),
                    )
                    inner = u - np.sign(offset) * 0.14
                    add(
                        inner - 0.04,
                        inner + 0.04,
                        0.092,
                        0.112,
                        level + 0.99,
                        level + 1.11,
                        trim,
                    )
                for offset in (-1.02, 1.02):
                    northwest.window_grid(
                        add, door + offset, 0.33, level + 0.34, level + 2.28, 1, 2, trim
                    )
                add(
                    door - 1.42,
                    door + 1.42,
                    0.07,
                    0.33,
                    level + 2.38,
                    level + 2.54,
                    trim,
                )
                add(
                    door - 0.73,
                    door + 0.73,
                    0.069,
                    0.087,
                    level + 2.15,
                    level + 2.32,
                    (100, 119, 118),
                )
            else:
                millrace.door(add, door, level, trim)
        levels = row["levels_z_m"][1:] if upper_only else row["levels_z_m"]
        low = min(levels) - 0.12
        high = height_at(roof_at, plan, span / 2, span * 0.46) - 0.19
        if row["siding"] == "vertical":
            for u in np.arange(0.11, span - 0.09, 0.21):
                top = roof_at(plan(u, 0)) - 0.16
                add(u, u + 0.016, 0.013, 0.024, low, top, seam)
        elif row["kind"] != "sigma":
            for z in np.arange(low + 0.18, high, 0.18):
                add(0.04, span - 0.04, 0.010, 0.022, z, z + 0.012, seam)
        mean = plan(span / 2, 0)
        count = max(2, round(span / row["bay_pitch_m"]))
        if row["kind"] == "eighteenth" and normal[1] > 0.94:
            count = max(2, round(span / 5.0))
        if row["kind"] == "emerald" and not chosen:
            count = min(count, 3)
        centers = np.linspace(span * 0.22, span * 0.78, count)
        for level_index, level in enumerate(levels):
            positions = centers
            if row["kind"] == "emerald" and chosen:
                positions = (
                    [span * 0.17, span * 0.84]
                    if level_index == 0
                    else [span * 0.17, span * 0.5, span * 0.84]
                )
            for center in positions:
                edge_gap = 2.10 if row["kind"] == "sigma" else 1.16
                if (
                    door is not None
                    and level_index == 0
                    and abs(center - door) < edge_gap
                ):
                    continue
                width = min(span * 0.28, row["window_width_m"])
                if row["kind"] == "emerald" and not chosen:
                    width = min(width, 1.43)
                if (
                    row["kind"] == "emerald"
                    and chosen
                    and level_index == 1
                    and abs(center - span / 2) < 0.1
                ):
                    width *= 0.64
                z = level + (0.72 if level_index == 0 else 0.86)
                top = min(
                    z + row["window_height_m"],
                    height_at(roof_at, plan, center, width / 2) - 0.26,
                )
                northwest.window_grid(
                    add,
                    center,
                    width,
                    z,
                    top,
                    2,
                    2 if row["kind"] == "emerald" else 1,
                    trim,
                )
        if row["kind"] == "sigma" and normal[0] < -0.90 and mean[0] < -164:
            for z in levels[1:]:
                add(0.025, span - 0.025, 0.015, 0.060, z - 0.16, z - 0.07, trim)


def sigma(parts, paving, row, outline, field):
    wall = orient(
        outline.buffer(-0.31, join_style="mitre").difference(
            box(*row["portico_recess_m"])
        )
    )
    roof_at = garden.roof_sections(
        parts, outline, wall, row["bottom_z_m"], row, grid=0.0002
    )
    face, point = select_entry(wall, row["entry"])
    facade(parts, row, wall, roof_at, face, point)
    gate = pedestrian_approach(paving, row, field, face, point)
    trim = row["trim_color"]
    level = row["entry"]["level_z_m"]
    solid_box(paving, row["portico_platform_m"], level - 1.04, level, CONCRETE)
    supports = []
    x = row["portico_columns_e_m"]
    for y in row["portico_columns_n_m"]:
        top = roof_at((x, y)) - 0.14
        supports.append(
            solid_box(parts, [x - 0.17, y - 0.17, x + 0.17, y + 0.17], level, top, trim)
        )
        solid_box(
            parts,
            [x - 0.20, y - 0.20, x + 0.20, y + 0.20],
            top - 0.21,
            top + 0.015,
            trim,
        )
    solid_box(
        parts,
        row["portico_header_m"],
        row["portico_header_z_m"] - 0.19,
        row["portico_header_z_m"],
        trim,
    )
    for bounds in row["chimney_bounds_m"]:
        top = roof_at(box(*bounds).centroid.coords[0])
        solid_box(parts, bounds, top - 0.25, top + 0.73, (127, 105, 92))
    deck = row["rear_deck_z_m"]
    left, south, right, north = row["rear_deck_m"]
    solid_box(parts, [left, south, right, north], deck - 0.27, deck, trim)
    for a, b in (
        ((left, north), (left, south)),
        ((left, south), (right, south)),
        ((right, south), (right, north)),
    ):
        fairmount.balustrade(parts, a, b, deck, WOOD)
    for e in (left + 0.17, right - 0.17):
        ground = geometry.sample_ground(field, e, south + 0.17) - 0.05
        supports.append(
            solid_box(
                parts,
                [e - 0.12, south + 0.05, e + 0.12, south + 0.29],
                ground,
                deck,
                trim,
            )
        )
    low = geometry.sample_ground(field, (left + right) / 2, south)
    supports.append(
        solid_box(
            parts,
            [left + 0.29, south + 0.08, right - 0.29, south + 0.21],
            low - 0.29,
            low + 1.68,
            WOOD,
        )
    )
    return wall, supports, gate


def rear_stair(parts, row, field):
    left, south, right, north = row["rear_stair_m"]
    mid_e = (left + right) / 2
    base_z = geometry.sample_ground(field, right, north)
    target = row["levels_z_m"][1]
    middle_z = (base_z + target) / 2
    for x0, x1, start_y, end_y, low, high in (
        (mid_e, right, north, south + 0.65, base_z, middle_z),
        (left, mid_e, south + 0.65, north, middle_z, target),
    ):
        levels = np.linspace(start_y, end_y, 14)
        for i, (a, b) in enumerate(zip(levels[:-1], levels[1:]), 1):
            z = low + i * (high - low) / 13
            solid_box(
                parts, [x0, min(a, b) - 0.047, x1, max(a, b) + 0.047], z - 0.09, z, WOOD
            )
        for x in (x0 + 0.04, x1 - 0.04):
            a = np.array([x, start_y, low])
            b = np.array([x, end_y, high])
            fairmount.beam(parts, a - (0, 0, 0.12), b - (0, 0, 0.12), 0.15, WOOD)
            fairmount.beam(parts, a + (0, 0, 0.84), b + (0, 0, 0.84), 0.075, WOOD)
            for point in np.linspace(a, b, 7):
                fairmount.beam(parts, point, point + (0, 0, 0.84), 0.04, WOOD)
    solid_box(
        parts, [left, south, right, south + 0.71], middle_z - 0.16, middle_z, WOOD
    )
    solid_box(
        parts, [left, north - 0.06, mid_e, north + 0.81], target - 0.17, target, WOOD
    )
    fairmount.balustrade(parts, (left, south), (right, south), middle_z, WOOD)
    return orient(box(left, south, right, north))


def former_chapter(parts, paving, row, outline, field):
    caps = union_all([box(*bounds) for bounds in row["upper_extent_m"]])
    upper = orient(outline.intersection(caps))
    low = orient(outline.difference(upper))
    wall = orient(
        outline.buffer(-0.28, join_style="mitre").difference(
            box(*row["canopy_recess_m"])
        )
    )
    upper_wall = orient(upper.buffer(-0.19, join_style="mitre"))
    upper_at = garden.roof_sections(
        parts, upper, upper_wall, row["levels_z_m"][1] - 0.19, row, grid=0.0002
    )
    low_at = garden.roof_sections(
        parts,
        low,
        Polygon(),
        row["bottom_z_m"],
        {
            **row,
            "roof_zones": row["low_roof_zones"],
            "roof_color": row["low_roof_color"],
        },
        grid=0.0002,
    )
    base.flat(
        parts, wall, row["bottom_z_m"], row["levels_z_m"][1] - 0.18, row["wall_color"]
    )
    facade(parts, row, upper_wall, upper_at, upper_only=True)
    face, point = select_entry(wall, row["entry"])
    threshold = row["entry"]["level_z_m"]
    facade(
        parts,
        {**row, "levels_z_m": [row["levels_z_m"][0]]},
        wall,
        lambda _: row["levels_z_m"][1] - 0.12,
        face,
        point,
    )
    gate = pedestrian_approach(paving, row, field, face, point)
    supports = [rear_stair(parts, row, field)]
    for e, n in row["canopy_columns_m"]:
        bottom = geometry.sample_ground(field, e, n) - 0.08
        supports.append(
            solid_box(
                parts,
                [e - 0.087, n - 0.087, e + 0.087, n + 0.087],
                bottom,
                low_at((e, n)) - 0.13,
                row["trim_color"],
            )
        )
    solid_box(
        paving, row["canopy_platform_m"], threshold - 0.94, threshold - 0.045, CONCRETE
    )
    for bounds in row["roof_fixtures_m"]:
        top = upper_at(box(*bounds).centroid.coords[0])
        solid_box(parts, bounds, top - 0.13, top + 0.54, CONCRETE)
    return wall, supports, gate


def emerald(parts, paving, row, outline, field):
    wall = orient(outline.buffer(-0.30, join_style="mitre"))
    roof_at = garden.roof_sections(
        parts, outline, wall, row["bottom_z_m"], row, grid=0.0002
    )
    face, point = select_entry(wall, row["entry"])
    facade(parts, row, wall, roof_at, face, point)
    gate = pedestrian_approach(paving, row, field, face, point)
    e, n = point.coords[0]
    level = row["entry"]["level_z_m"]
    trim = row["trim_color"]
    cover = orient(box(e - 0.11, n - 1.44, e + 0.96, n + 1.44))
    parts.append(
        geometry.shell(
            cover,
            level + 2.37,
            lambda x, _: level + 2.67 - 0.21 * (x - e),
            trim,
            row["roof_color"],
        )
    )
    piers = [
        solid_box(
            parts, [e + 0.74, y - 0.05, e + 0.83, y + 0.05], level, level + 2.42, trim
        )
        for y in (n - 1.24, n + 1.24)
    ]
    return wall, piers, gate


def build(row, field, paving):
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    parts = []
    model = {"sigma": sigma, "eighteenth": former_chapter, "emerald": emerald}[
        row["kind"]
    ]
    wall, supports, gate = model(parts, paving, row, outline, field)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{key: row[key] for key in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(wall)],
        "support_collision_enu_m": [base.ring(shape) for shape in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": row["bottom_z_m"],
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [gate],
    }
    return mesh, record, wall, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "south_university_exterior_site", build
    )


if __name__ == "__main__":
    main()
