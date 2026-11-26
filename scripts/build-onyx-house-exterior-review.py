# SPDX-License-Identifier: Apache-2.0
"""Export the Onyx House exterior and street approach."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
northwest = import_module("build-northwest-infill-exterior-review")
base, garden, geometry = fairmount.base, fairmount.garden, fairmount.geometry
PACKAGE = "onyx-house-exterior-review"
GROUND = "onyx-house-approaches"
CONCRETE = (157, 155, 146)
STONE = (131, 128, 114)
WALK = (181, 168, 148)
SHADOW = (134, 140, 134)


def patch(parts, bounds, bottom, top, color, cap=None):
    shape = orient(box(*bounds))
    base.flat(parts, shape, bottom, top, color, color if cap is None else cap)
    return shape


def top_at(roof_at, plan, left, right):
    return min(roof_at(plan(u, 0)) for u in (left, (left + right) / 2, right))


def upper_elevations(parts, row, wall, roof_at):
    floor, upper = row["floor_levels_m"]
    trim = row["trim_color"]
    for _, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 2.25:
            continue
        head = top_at(roof_at, plan, 0.07, span - 0.07)
        for z in np.arange(floor + 0.17, head - 0.16, 0.175):
            add(0.03, span - 0.03, 0.012, 0.025, z, z + 0.012, SHADOW)
        e, n = plan(span / 2, 0)
        south_band = normal[1] < -0.95 and e > -225 and n < -652
        west = normal[0] < -0.95 and e < -233
        east = normal[0] > 0.95 and e > -202
        for i, level in enumerate((floor, upper)):
            sill, lintel = level + 0.78, min(level + 2.36, head - 0.28)
            if lintel - sill < 0.64:
                continue
            if south_band:
                sections = round(span / 3.0)
                for center in (span * (j + 0.5) / sections for j in range(sections)):
                    northwest.window_grid(
                        add, center, span / sections - 0.10, sill, lintel, 3, 1, trim
                    )
                continue
            centers = (
                np.linspace(span * 0.14, span * 0.86, 5)
                if west
                else np.linspace(span * 0.24, span * 0.76, max(2, round(span / 4.4)))
            )
            for pos in centers:
                width = min(span * 0.19, 1.5 if west or east else 1.34)
                northwest.window_grid(
                    add, pos, width, sill, lintel, 2, 2 if i == 0 else 1, trim
                )


def lower_south_elevation(parts, row, wall, low_floor, roof_at):
    trim = row["trim_color"]
    for _, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 2.1:
            continue
        head = top_at(roof_at, plan, 0.07, span - 0.07) - 0.29
        if normal[1] < -0.92 and span > 6:
            for z in np.arange(low_floor + 0.15, head, 0.19):
                add(0.04, span - 0.04, 0.02, 0.035, z, z + 0.015, SHADOW)
            for center in (span * 0.23, span * 0.77):
                northwest.window_grid(
                    add,
                    center,
                    min(span * 0.22, 2.28),
                    low_floor + 0.24,
                    min(head, low_floor + 2.55),
                    2,
                    2,
                    trim,
                )
            fairmount.millrace.door(add, span * 0.50, low_floor, trim)
            add(span * 0.10, span * 0.92, 0.035, 0.57, head, head + 0.16, trim)
        else:
            for center in np.linspace(
                span * 0.28, span * 0.72, max(2, round(span / 4.6))
            ):
                northwest.window_grid(
                    add,
                    center,
                    min(span * 0.23, 1.35),
                    low_floor + 1.12,
                    min(head, low_floor + 2.24),
                    2,
                    1,
                    trim,
                )


def west_ground(parts, row, upper_wall, field):
    ground_wall = orient(
        upper_wall.difference(unary_union([box(*b) for b in row["alley_bay_cuts_m"]]))
    )
    floor = row["floor_levels_m"][0]
    base.flat(parts, ground_wall, row["bottom_z_m"], floor + 0.026, CONCRETE)
    for _, (span, add, normal, plan, _, _) in fairmount.views(parts, ground_wall):
        if span < 5 or normal[0] > -0.96 or plan(span / 2, 0)[0] > -233:
            continue
        for center in (span * 0.26, span * 0.70):
            for z in np.linspace(floor - 0.97, floor - 0.56, 8):
                add(center - 0.42, center + 0.42, 0.042, 0.061, z, z + 0.018, SHADOW)
    piers = []
    for x, y in row["alley_columns_m"]:
        z = geometry.sample_ground(field, x, y) - 0.07
        piers.append(
            patch(parts, [x - 0.14, y - 0.14, x + 0.14, y + 0.14], z, floor, CONCRETE)
        )
    return ground_wall, piers


def porch(parts, apron, row, field):
    x, y = row["entry_enu_m"]
    level = row["entry_level_z_m"]
    grades = geometry.sample_ground(field, x + 5.8, y) - 0.018
    trim = row["trim_color"]
    patch(
        apron,
        [x - 0.09, y - 2.45, x + 2.62, y + 2.45],
        grades - 0.40,
        level,
        CONCRETE,
        WALK,
    )
    landing = grades + 0.57
    pieces = np.linspace(x + 5.8, x + 4.45, 5)
    for i, (outer, inner) in enumerate(zip(pieces[:-1], pieces[1:]), 1):
        top = grades + i * (landing - grades) / 4
        patch(
            apron,
            [inner, y - 0.96, outer, y + 0.96],
            grades - 0.15,
            top,
            CONCRETE,
            WALK,
        )
    patch(
        apron,
        [x + 2.63, y - 0.96, x + 4.46, y + 0.57],
        grades - 0.15,
        landing,
        CONCRETE,
        WALK,
    )
    lateral = np.linspace(y + 0.57, y + 3.0, 10)
    for i, (near, far) in enumerate(zip(lateral[:-1], lateral[1:]), 1):
        top = landing + i * (level - landing) / 9
        patch(
            apron, [x + 2.63, near, x + 4.45, far], grades - 0.15, top, CONCRETE, WALK
        )
    patch(
        apron,
        [x + 1.22, y + 2.39, x + 2.63, y + 3.88],
        grades - 0.15,
        level,
        CONCRETE,
        WALK,
    )
    patch(
        apron,
        [x + 2.63, y + 3.0, x + 4.45, y + 3.88],
        grades - 0.15,
        level,
        CONCRETE,
        WALK,
    )
    for e in (x + 4.45, x + 2.65):
        a = np.array([e, lateral[0], landing])
        b = np.array([e, lateral[-1], level])
        fairmount.beam(parts, a + (0, 0, 0.85), b + (0, 0, 0.85), 0.056, trim)
        for at in np.linspace(a, b, 6):
            fairmount.beam(parts, at, at + (0, 0, 0.85), 0.046, trim)
    fairmount.balustrade(parts, (x, y - 2.32), (x + 2.54, y - 2.32), level, trim)
    fairmount.balustrade(parts, (x + 2.56, y - 2.32), (x + 2.56, y + 2.44), level, trim)
    fairmount.balustrade(parts, (x + 1.24, y + 3.86), (x + 4.43, y + 3.86), level, trim)

    eave, rise = level + 3.32, 0.54
    for a, b in ((y - 1.99, y), (y, y + 1.99)):
        roof = orient(box(x - 0.11, a, x + 2.72, b))
        parts.append(
            geometry.shell(
                roof,
                eave - 0.11,
                lambda _, n: eave + rise * (1 - abs(n - y) / 1.99),
                trim,
                row["low_roof_color"],
            )
        )
    supports = []
    for n in (y - 1.77, y + 1.77):
        supports.append(
            patch(
                parts,
                [x + 2.32, n - 0.095, x + 2.53, n + 0.095],
                level,
                eave + 0.08,
                trim,
            )
        )
    for a, b in row["retaining_segments_m"]:
        locals_ = np.linspace(a, b, max(2, int((b - a) / 1.3) + 1))
        for left, right in zip(locals_[:-1], locals_[1:]):
            z = geometry.sample_ground(field, x + 5.8, (left + right) / 2)
            bounds = [x + 5.43, left, x + 5.77, right]
            supports.append(patch(apron, bounds, z - 0.31, z + 0.63, STONE))
    return {
        "gate": "onyx-east-porch",
        "position_enu_m": [x + 5.80, y],
        "outward_degrees": 90,
        "threshold_z_m": grades,
        "width_m": 1.42,
        "approach_distance_m": 1.75,
        "estimated": True,
        "snap_to_facade": False,
    }, supports


def build(row, field, apron):
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    high_area = outline.intersection(
        unary_union([box(*bounds) for bounds in row["high_extent_m"]])
    )
    high = orient(high_area)
    low = orient(outline.difference(high))
    merged = orient(outline.buffer(-0.22, join_style="mitre"))
    upper_wall = orient(merged.intersection(high))
    low_wall = orient(merged.intersection(low))
    parts = []
    high_at = garden.roof_sections(
        parts, high, upper_wall, row["floor_levels_m"][0], row, grid=0.0002
    )
    low_at = garden.roof_sections(
        parts,
        low,
        low_wall,
        row["bottom_z_m"],
        {
            **row,
            "roof_zones": row["low_roof_zones"],
            "roof_color": row["low_roof_color"],
        },
        grid=0.0002,
    )
    upper_elevations(parts, row, upper_wall, high_at)
    lower_south_elevation(parts, row, low_wall, row["south_entry_level_z_m"], low_at)
    ground_wall, piers = west_ground(parts, row, upper_wall, field)
    for _, (span, add, normal, plan, _, _) in fairmount.views(parts, ground_wall):
        if span > 4 and normal[0] > 0.94 and plan(span / 2, 0)[0] > -202:
            entry = row["entry_enu_m"][1]
            at = projection_along_span(plan, span, entry)
            fairmount.millrace.door(add, at, row["entry_level_z_m"], row["trim_color"])
    for bounds in row["roof_fixture_bounds_m"]:
        e, n = box(*bounds).centroid.coords[0]
        top = low_at((e, n))
        patch(parts, bounds, top - 0.24, top + 1.22, (138, 140, 134))
    x0, y0, x1, y1 = row["south_terrace_bounds_m"]
    deck = row["south_entry_level_z_m"]
    patch(apron, [x0, y0, x1, y1], deck - 0.73, deck, CONCRETE, WALK)
    gate, porch_supports = porch(parts, apron, row, field)
    supports = [*piers, *porch_supports]
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    return (
        mesh,
        {
            **{key: row[key] for key in ("id", "name", "street_address")},
            "footprint_enu_m": base.ring(outline),
            "ground_footprints_enu_m": [base.ring(ground_wall), base.ring(low_wall)],
            "support_collision_enu_m": [base.ring(part) for part in supports],
            "area_m2": round(outline.area, 3),
            "base_z_m": row["bottom_z_m"],
            "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
            "entrances": [gate],
        },
        union_all_walls(ground_wall, low_wall),
        supports,
    )


def projection_along_span(plan, span, north):
    start, end = plan(0, 0), plan(span, 0)
    return float(
        np.clip(span * (north - start[1]) / (end[1] - start[1]), 0.62, span - 0.62)
    )


def union_all_walls(high, low):
    combined = high.union(low)
    if combined.geom_type != "Polygon":
        raise ValueError("The Onyx ground wings must share a seam.")
    return combined


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "onyx_house_exterior_site", build
    )


if __name__ == "__main__":
    main()
