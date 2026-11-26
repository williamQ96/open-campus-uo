# SPDX-License-Identifier: Apache-2.0
"""Replace three merged source ranges with their six registered exteriors."""

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
garden, base, geometry = fairmount.garden, fairmount.base, fairmount.geometry
millrace = fairmount.millrace
PACKAGE = "onyx-university-split-exterior-review"
GROUND = "onyx-university-walks"
CONCRETE = (162, 156, 141)
WOOD = (147, 111, 84)
IRON = (75, 80, 78)


def rectangle(parts, bounds, low, high, color, cap=None):
    shape = orient(box(*bounds))
    base.flat(parts, shape, low, high, color, cap)
    return shape


def nearest_face(wall, coordinates, bearing):
    target = Point(coordinates)
    edge = LineString(
        garden.locate_face(list(garden.shared.face_edges(wall)), target, bearing)
    )
    point = nearest_points(edge, target)[0]
    if point.distance(target) > 1.10:
        raise ValueError(
            f"Exterior opening at {coordinates} misses the registered wall."
        )
    return edge, point


def approach(paving, field, plan, entry):
    point = Point(plan)
    distance, bearing = entry["distance_m"], entry["bearing"]
    millrace.approach(paving, field, point, distance, bearing)
    return {
        "gate": entry["gate"],
        "position_enu_m": [round(float(v), 5) for v in plan],
        "outward_degrees": bearing,
        "threshold_z_m": entry["approach_z_m"],
        "width_m": entry["width_m"],
        "approach_distance_m": distance,
        "estimated": True,
        "snap_to_facade": False,
    }


def roof_level(roof_at, plan, center, width):
    return min(
        roof_at(plan(t, 0)) for t in (center - width / 2, center, center + width / 2)
    )


def openings(parts, row, wall, roof_at):
    trim = row["trim_color"]
    front = fairmount.bearing_vector(row["front_bearing"])
    item = row.get("door")
    door_face, door_point = (
        nearest_face(wall, item["near_enu_m"], item["bearing"])
        if item
        else (None, None)
    )
    balcony_door = row.get("balcony_door")
    upper_face, upper_point = (
        nearest_face(wall, balcony_door["near_enu_m"], balcony_door["bearing"])
        if balcony_door
        else (None, None)
    )
    for face, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 2.0:
            continue
        door = (
            face.project(door_point)
            if door_face is not None and face.equals(door_face)
            else None
        )
        if door is not None:
            millrace.door(add, door, item["threshold_z_m"], trim)
        upper_door = (
            face.project(upper_point)
            if upper_face is not None and face.equals(upper_face)
            else None
        )
        if upper_door is not None:
            millrace.door(add, upper_door, balcony_door["threshold_z_m"], trim)
        low = row["levels_z_m"][0] - 0.17
        top = roof_level(roof_at, plan, span / 2, span - 0.28) - 0.17
        if row["cladding"] == "vertical":
            for u in np.arange(0.12, span - 0.12, 0.21):
                add(
                    u,
                    u + 0.019,
                    0.019,
                    0.043,
                    low,
                    roof_at(plan(u, 0)) - 0.16,
                    row["cladding_color"],
                )
        else:
            for z in np.arange(low + 0.20, top, 0.20):
                add(
                    0.04, span - 0.04, 0.017, 0.036, z, z + 0.014, row["cladding_color"]
                )
        if row["type"] == "garage":
            if normal @ front > 0.93:
                double_garage(add, span, row["levels_z_m"][0], trim)
            continue
        count = max(1, round(span / row["window_spacing_m"]))
        for i, level in enumerate(row["levels_z_m"]):
            if i > 0 and row["type"] == "flat" and plan(span / 2, 0)[0] < -273.0:
                continue
            if i == 0 and row["type"] == "flat" and plan(span / 2, 0)[0] < -280.8:
                level = row["porch"]["floor_z_m"]
            groups = None
            if normal @ front > 0.92:
                groups = row.get("front_windows", {}).get(str(i))
            if groups is None:
                groups = [
                    [(j + 0.5) / count, row["window_width_m"]] for j in range(count)
                ]
            for fraction, width in groups:
                at = span * fraction
                width = min(width, at * 1.67, (span - at) * 1.67)
                if (
                    door is not None
                    and abs(level - item["threshold_z_m"]) < 0.8
                    and abs(at - door) < (width / 2 + 0.59)
                ):
                    continue
                if (
                    upper_door is not None
                    and i > 0
                    and abs(at - upper_door) < width / 2 + 0.61
                ):
                    continue
                sill = level + 0.80
                head = min(
                    sill + row["window_height_m"],
                    roof_level(roof_at, plan, at, width) - 0.27,
                )
                northwest.window_grid(
                    add, at, width, sill, head, 2 if width >= 1.1 else 1, 2, trim
                )
    return door_face, door_point


def double_garage(add, span, floor, trim):
    for center in (span * 0.25, span * 0.53):
        width = min(2.48, span * 0.265)
        left, right = center - width / 2, center + width / 2
        add(left - 0.09, right + 0.09, 0.017, 0.09, floor, floor + 2.25, trim)
        add(left, right, 0.091, 0.112, floor + 0.04, floor + 2.14, (169, 176, 170))
        for z in np.arange(floor + 0.36, floor + 2.10, 0.37):
            add(
                left + 0.035, right - 0.035, 0.112, 0.122, z, z + 0.022, (151, 158, 150)
            )


def side_stair(parts, row, field):
    left, south, right, north = row["stair_enu_m"]
    top = row["door"]["threshold_z_m"]
    bottom = geometry.sample_ground(field, (left + right) / 2, south)
    stations = np.linspace(south, north - 0.87, 15)
    for i, (a, b) in enumerate(zip(stations[:-1], stations[1:]), 1):
        z = bottom + (top - bottom) * i / 14
        rectangle(parts, [left, a - 0.07, right, b], z - 0.12, z, WOOD)
    rectangle(parts, [left, north - 0.89, right + 0.27, north], top - 0.18, top, WOOD)
    for x in (left + 0.035, right - 0.035):
        a, b = np.array([x, stations[0], bottom]), np.array([x, stations[-1], top])
        fairmount.beam(parts, a - (0, 0, 0.115), b - (0, 0, 0.115), 0.13, IRON)
        fairmount.beam(parts, a + (0, 0, 0.87), b + (0, 0, 0.87), 0.058, IRON)
        for p in np.linspace(a, b, 14):
            fairmount.beam(parts, p, p + (0, 0, 0.87), 0.031, IRON)
    fairmount.balustrade(parts, (left, north - 0.89), (left, north), top, IRON)
    support = rectangle(
        parts, [left, north - 0.16, left + 0.15, north], bottom - 0.13, top, WOOD
    )
    return [orient(box(left, south, right, north)), support]


def covered_entry(parts, row, field, roof_at):
    porch = row["porch"]
    level = porch["floor_z_m"]
    support = []
    bounds = porch["deck_enu_m"]
    ground = min(
        geometry.sample_ground(field, e, n) for e, n in box(*bounds).exterior.coords
    )
    rectangle(parts, bounds, min(level - 0.22, ground - 0.18), level, CONCRETE)
    for e, n in porch["posts_enu_m"]:
        d = porch["post_width_m"] / 2
        z = geometry.sample_ground(field, e, n)
        support.append(
            rectangle(
                parts,
                [e - d, n - d, e + d, n + d],
                min(z, level) - 0.16,
                roof_at((e, n)) - 0.14,
                row["trim_color"],
            )
        )
    for a, b in porch.get("rail_segments_enu_m", []):
        fairmount.balustrade(parts, a, b, level, row["wall_color"])
    return support


def picket_fence(parts, row, field):
    supports = []
    for west, east, n in row["fence_segments_enu_m"]:
        a = geometry.sample_ground(field, west, n)
        b = geometry.sample_ground(field, east, n)
        for z in (0.23, 0.73):
            fairmount.beam(
                parts, (west, n, a + z), (east, n, b + z), 0.055, row["trim_color"]
            )
        for x in np.linspace(west, east, max(2, round((east - west) / 0.18))):
            low = geometry.sample_ground(field, x, n)
            rectangle(
                parts,
                [x - 0.026, n - 0.023, x + 0.026, n + 0.023],
                low - 0.09,
                low + 0.90,
                row["trim_color"],
            )
        supports.append(orient(box(west, n - 0.053, east, n + 0.053)))
    return supports


def balcony(parts, row, field):
    west, south, east, north = row["balcony_enu_m"]
    level = row["levels_z_m"][-1]
    trim = row["trim_color"]
    rectangle(parts, [west, south, east, north], level - 0.17, level, trim)
    fairmount.balustrade(parts, (east, south), (east, north), level, trim)
    supports = []
    for n in (south + 0.13, north - 0.13):
        e = east - 0.14
        ground = geometry.sample_ground(field, e, n) - 0.08
        supports.append(
            rectangle(
                parts, [e - 0.07, n - 0.07, e + 0.07, n + 0.07], ground, level, trim
            )
        )
    return supports


def street_steps(parts, field, position, width, porch):
    e, n = position
    bottom = geometry.sample_ground(field, e, n + 1.35) - 0.05
    top = max(bottom + 0.18, geometry.sample_ground(field, e, n - 0.59)) + 0.03
    stations = np.linspace(n + 1.35, n - 0.59, 6)
    for i, (near, far) in enumerate(zip(stations[:-1], stations[1:]), 1):
        rectangle(
            parts,
            [e - width / 2, far, e + width / 2, near],
            bottom - 0.20,
            bottom + (top - bottom) * i / 5,
            CONCRETE,
        )
    upper = np.linspace(stations[-1], porch["deck_enu_m"][3], 8)
    landing = porch["floor_z_m"]
    for i, (near, far) in enumerate(zip(upper[:-1], upper[1:]), 1):
        rectangle(
            parts,
            [e - width / 2, far, e + width / 2, near],
            top - 0.15,
            top + (landing - top) * i / 7,
            CONCRETE,
        )


def gable_hood(parts, row):
    left, south, right, north = row["hood_enu_m"]
    level = row["porch"]["floor_z_m"]
    z = level + 2.16
    center = (left + right) / 2
    for a, b in ((left, center), (center, right)):
        ring = orient(box(a, south, b, north))
        parts.append(
            geometry.shell(
                ring,
                z - 0.14,
                lambda e, _: z + 0.42 * (1 - abs(e - center) / (right - center)),
                row["trim_color"],
                row["roof_color"],
            )
        )
    return [
        rectangle(
            parts,
            [e - 0.057, north - 0.17, e + 0.057, north - 0.047],
            level - 0.10,
            z - 0.07,
            row["trim_color"],
        )
        for e in (left + 0.10, right - 0.10)
    ]


def build(row, field, paving):
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
    if "porch" in row:
        wall = orient(wall.difference(box(*row["porch"]["recess_enu_m"])))
    parts, supports, gates = [], [], []
    roof_at = garden.roof_sections(
        parts, outline, wall, row["base_z_m"], row, grid=0.0002
    )
    edge, point = openings(parts, row, wall, roof_at)
    if "porch" in row:
        supports.extend(covered_entry(parts, row, field, roof_at))
    if "balcony_enu_m" in row:
        supports.extend(balcony(parts, row, field))
    if "hood_enu_m" in row:
        supports.extend(gable_hood(parts, row))
    if "stair_enu_m" in row:
        supports.extend(side_stair(parts, row, field))
    if "fence_segments_enu_m" in row:
        supports.extend(picket_fence(parts, row, field))
    for bounds in row.get("walks_enu_m", []):
        millrace.western.terrace(paving, field, orient(box(*bounds)))
    if "side_landing_enu_m" in row:
        bounds = row["side_landing_enu_m"]
        threshold = row["door"]["threshold_z_m"]
        rectangle(paving, bounds, threshold - 0.72, threshold, CONCRETE)
        e0, _, e1, n = bounds
        fairmount.balustrade(
            parts, (e0 + 0.16, n - 0.045), (e1 - 0.21, n - 0.045), threshold, IRON
        )
    entry = row.get("entry")
    if entry:
        if "position_enu_m" in entry:
            position = entry["position_enu_m"]
            if "fence_segments_enu_m" in row:
                street_steps(paving, field, position, entry["width_m"], row["porch"])
        else:
            position = point.coords[0]
            _, _, _, plan = millrace.basis(paving, *edge.coords)
            at = edge.project(point)
            threshold = row["door"]["threshold_z_m"]
            local_ground = geometry.sample_ground(field, *plan(at, 0.72))
            fairmount.landing(
                paving, plan, at, row, threshold, min(threshold - 0.05, local_ground)
            )
        gates.append(approach(paving, field, position, entry))
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
            "base_z_m": row["base_z_m"],
            "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
            "area_m2": round(outline.area, 3),
            "entrances": gates,
        },
        wall,
        supports,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "onyx_university_split_site", build
    )


if __name__ == "__main__":
    main()
