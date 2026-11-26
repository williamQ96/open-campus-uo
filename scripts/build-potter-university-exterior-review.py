# SPDX-License-Identifier: Apache-2.0
"""Export the Central Lutheran complex and seven registered nearby exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import nearest_points, split
import trimesh

frontages = import_module("build-south-campus-frontages-review")
fairmount, garden = frontages.fairmount, frontages.garden
base, geometry, millrace = frontages.base, frontages.geometry, frontages.millrace
northwest, chapter = frontages.northwest, frontages.chapter
PACKAGE = "potter-university-exterior-review"
GROUND = "potter-university-approaches"
STONE = (162, 152, 131)
WOOD = (104, 87, 72)
BRICK = (145, 99, 79)
GLASS = (68, 88, 99)
MULLION = (82, 75, 66)


def choose_face(wall, spec, minimum=2.1):
    hint = Point(spec["near"])
    direction = fairmount.bearing_vector(spec["bearing"])
    choices = (
        LineString((a, b))
        for a, b in garden.shared.face_edges(wall)
        if np.linalg.norm(np.subtract(b, a)) >= minimum
        and garden.neighbor.bearing(a, b) @ direction > 0.96
    )
    face = min(choices, key=hint.distance)
    point = nearest_points(face, hint)[0]
    if point.distance(hint) > 0.78:
        raise ValueError(f"{spec['gate']} is outside the registered frontage.")
    return face, point


def door(add, at, floor, color):
    millrace.door(add, at, floor, color)
    add(at - 0.38, at + 0.38, 0.104, 0.118, floor + 0.085, floor + 0.86, color)
    add(at - 0.36, at + 0.36, 0.104, 0.118, floor + 1.72, floor + 1.98, color)


def porch(parts, row, field, plan, at, level):
    width, depth, rise = row["porch"]
    width /= 2
    color = row["trim_color"]
    base.flat(
        parts,
        fairmount.rectangle(plan, at - width, at + width, -0.03, depth),
        level - 0.46,
        level,
        STONE,
    )
    chapter.gabled_canopy(
        parts,
        plan,
        at,
        width + 0.07,
        -0.10,
        depth + 0.12,
        level + 2.23,
        rise,
        row["roof_color"],
        color,
    )
    supports = []
    for u in (at - width + 0.12, at + width - 0.12):
        pad = fairmount.rectangle(plan, u - 0.08, u + 0.08, depth - 0.14, depth + 0.02)
        grade = geometry.sample_ground(field, *plan(u, depth))
        base.flat(parts, pad, grade - 0.07, level + 2.34, color)
        supports.append(pad)
    return supports


def house_facades(parts, row, wall, field, height, front, point):
    trim, seam = row["trim_color"], row["seam_color"]
    level = row["entry"]["threshold_z_m"]
    floor = row["levels_z_m"][0]
    supports = []
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 0.65:
            continue
        door_centers = []
        primary_at = edge.project(point) if edge.equals(front) else None
        if primary_at is not None:
            door_centers.append(primary_at)
            if "porch" in row:
                supports.extend(porch(parts, row, field, plan, primary_at, level))
        if normal[0] > 0.98:
            for n in row.get("secondary_doors_n_m", []):
                e = plan(span / 2, 0)[0]
                target = Point(e, n)
                at = edge.project(target)
                if edge.distance(target) < 0.1 and 0.59 < at < span - 0.59:
                    door_centers.append(at)
        for center in door_centers:
            door(add, center, level, row.get("door_color", trim))
        if span < 1.5:
            continue
        top = min(height(plan(u, 0)) for u in np.linspace(0.045, span - 0.045, 9))
        millrace.siding(add, span, top - 0.20, floor - 0.52, seam, 0.185)
        if "band_z_m" in row:
            z = row["band_z_m"]
            add(0.018, span - 0.018, 0.019, 0.071, z - 0.05, z + 0.09, trim)
        count = max(1, round(span / row["bay_m"]))
        width = min(span / count * 0.60, 1.23)
        enclosed_porch = primary_at is not None and row.get("enclosed_porch")
        for u in (np.arange(count) + 0.5) * span / count:
            limit = (
                min(height(plan(x, 0)) for x in (u - width / 2, u, u + width / 2))
                - 0.23
            )
            for index, low in enumerate(row["levels_z_m"]):
                if not index and enclosed_porch:
                    continue
                if not index and any(abs(u - d) < 1.20 for d in door_centers):
                    continue
                sill = low + (0.68 if index else 0.77)
                northwest.window_grid(
                    add, u, width, sill, min(sill + 1.2, limit), 2, 2, trim
                )
        if enclosed_porch:
            for first, last in (
                (0.73, primary_at - 1.64),
                (primary_at + 1.64, span - 0.73),
            ):
                if last - first > 0.7:
                    northwest.window_grid(
                        add,
                        (first + last) / 2,
                        last - first,
                        level + 0.49,
                        level + 2.17,
                        max(2, round((last - first) / 0.72)),
                        2,
                        trim,
                    )
    return supports


def retaining_wall(parts, row, field):
    spec = row.get("retaining_enu_m")
    if not spec:
        return []
    west, east, north, gate, gap, rise = spec
    supports = []
    for first, last in ((west, gate - gap), (gate + gap, east)):
        stations = np.linspace(first, last, 7)
        for left, right in zip(stations[:-1], stations[1:]):
            section = orient(box(left, north - 0.17, right, north + 0.19))
            low = geometry.sample_ground(field, (left + right) / 2, north) - 0.12
            base.flat(parts, section, low, low + rise, STONE, (175, 168, 145))
            supports.append(section)
    return supports


def house(row, field, paving, outline):
    wall = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
    front, point = choose_face(
        wall, row["entry"], 1.3 if row.get("narrow_door_wall") else 2.1
    )
    parts = []
    height = garden.roof_sections(
        parts, outline, wall, row["base_z_m"], row, grid=0.0002
    )
    supports = house_facades(parts, row, wall, field, height, front, point)
    supports.extend(retaining_wall(parts, row, field))
    for item in row.get("dormers", []):
        fairmount.dormer(parts, row, item, height, outline)
    if "chimney" in row:
        e, n, w, d, rise, color = row["chimney"]
        z = height((e, n))
        base.flat(
            parts,
            box(e - w / 2, n - d / 2, e + w / 2, n + d / 2),
            z - 0.34,
            z + rise,
            color,
        )
    gates = [
        frontages.estimated_entry(
            paving, {**row, "entry_finish": "stone"}, field, front, point
        )
    ]
    return parts, wall, supports, gates


def sanctuary_screen(add, plan, span, lower, height, show_cross, door_at):
    for u in np.arange(0.11, span - 0.08, 0.19):
        top = height(plan(u, 0)) - 0.22
        add(u, u + 0.039, 0.014, 0.057, lower, top, (83, 70, 59))
    if not show_cross:
        return
    for index, u in enumerate(np.arange(span * 0.53, span * 0.92, 0.32)):
        low = 22.0 + (index % 4) * 0.28
        north = plan(u, 0)[1]
        z = min(26.4, low + 2.05 + max(north + 631, -1.0) * 0.12)
        color = ((78, 93, 133), (103, 120, 139), (109, 87, 99))[index % 3]
        add(u - 0.056, u + 0.056, 0.06, 0.086, low, z, color)
        add(u - 0.04, u + 0.04, 0.052, 0.071, 19.5, 20.72, color)
    cross = span * 0.36
    if door_at is not None:
        cross = min(span * 0.42, max(span * 0.24, door_at - 1.95))
    add(cross - 0.074, cross + 0.074, 0.079, 0.132, 20.95, 25.94, STONE)
    add(cross - 0.74, cross + 0.74, 0.081, 0.135, 24.18, 24.32, STONE)


def church_facades(parts, wall, height, doorways):
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 0.5:
            continue
        at = [edge.project(point) for face, point, _ in doorways if edge.equals(face)]
        n = plan(span / 2, 0)[1]
        upper = n > -636.85
        high = min(height(plan(u, 0)) for u in np.linspace(0.03, span - 0.03, 10))
        millrace.siding(add, span, 19.34, 16.15, (160, 115, 89), 0.148)
        if upper:
            sanctuary_screen(
                add, plan, span, 19.45, height, normal[0] < -0.95, at[0] if at else None
            )
        elif span >= 2.4:
            count = max(1, round(span / 2.25))
            for i in range(count):
                pos = (i + 0.5) * span / count
                if any(abs(pos - entrance) < 1.44 for entrance in at):
                    continue
                low = 18.30 if normal[0] > 0.9 else max(19.08, high - 1.57)
                northwest.window_grid(
                    add,
                    pos,
                    min(1.42, span / count * 0.60),
                    low,
                    min(low + 0.78, high - 0.23),
                    2,
                    1,
                    MULLION,
                )
    for edge, point, spec in doorways:
        _, add, _, _ = millrace.basis(parts, *edge.coords)
        center = edge.project(point)
        z = spec["threshold_z_m"]
        width = spec["width_m"]
        add(
            center - width / 2 - 0.08,
            center + width / 2 + 0.08,
            0.022,
            0.11,
            z,
            z + 2.4,
            MULLION,
        )
        for offset in (-0.25 * width, 0.25 * width):
            u = center + offset
            add(
                u - width * 0.21,
                u + width * 0.21,
                0.11,
                0.137,
                z + 0.15,
                z + 2.23,
                GLASS,
            )
            add(
                u - width * 0.21,
                u + width * 0.21,
                0.137,
                0.155,
                z + 1.01,
                z + 1.085,
                STONE,
            )


def church(row, field, paving, outline):
    parts, supports, gates = [], [], []
    canopy = box(*row["east_canopy_enu_m"])
    wall = orient(
        outline.buffer(-row["eaves_m"], join_style="mitre").difference(canopy)
    )
    band = 19.41
    base.flat(parts, wall, row["base_z_m"], band, BRICK)
    height = garden.roof_sections(
        parts, outline, wall, band, {**row, "wall_color": WOOD}, grid=0.0002
    )
    west, east = row["entry"], row["east_entry"]
    front = [choose_face(wall, spec) for spec in (west, east)]
    church_facades(
        parts, wall, height, [(*face, spec) for face, spec in zip(front, (west, east))]
    )
    e0, n0, e1, n1 = canopy.bounds
    for n in np.linspace(n0 + 0.44, n1 - 1.09, 4):
        if abs(n - east["near"][1]) < 1.13:
            continue
        post = orient(box(e1 - 0.45, n - 0.07, e1 - 0.30, n + 0.07))
        grade = geometry.sample_ground(field, e1 - 0.375, n)
        base.flat(parts, post, grade - 0.07, height((e1 - 0.375, n)) - 0.13, MULLION)
        supports.append(post)
    for spec, (face, point) in zip((west, east), front):
        gates.append(
            frontages.estimated_entry(
                paving, {"entry": spec, "entry_finish": "stone"}, field, face, point
            )
        )
    courtyard = Polygon(outline.interiors[0])
    open_walk = courtyard.buffer(-0.3, join_style="mitre")
    if open_walk.area < 50:
        raise ValueError("The municipal courtyard opening was lost.")
    millrace.western.terrace(paving, field, orient(open_walk))
    lawn = orient(box(*row["courtyard_planting_enu_m"]))
    assert open_walk.covers(lawn)
    ground = min(geometry.sample_ground(field, *p) for p in lawn.exterior.coords)
    paving.append(
        geometry.shell(
            lawn,
            ground - 0.07,
            lambda e, n: geometry.sample_ground(field, e, n) + 0.12,
            (139, 133, 114),
            (99, 119, 76),
        )
    )
    return parts, wall, supports, gates


def build(row, field, paving):
    outline = orient(
        set_precision(Polygon(row["outline_enu_m"], row["holes_enu_m"]), 0.002)
    )
    model = church if row["holes_enu_m"] else house
    parts, wall, supports, gates = model(row, field, paving, outline)
    collision = [wall]
    if wall.interiors:
        n = Polygon(wall.interiors[0]).centroid.y
        cut = LineString([(wall.bounds[0] - 1, n), (wall.bounds[2] + 1, n)])
        collision = list(split(wall, cut).geoms)
        assert all(not part.interiors for part in collision)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{key: row[key] for key in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(orient(p)) for p in collision],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "base_z_m": row["base_z_m"],
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "area_m2": round(outline.area, 3),
        "entrances": gates,
    }
    if outline.interiors:
        record["footprint_holes_enu_m"] = [
            list(ring.coords)[:-1] for ring in outline.interiors
        ]
    return mesh, record, wall, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "potter_university_exterior_site", build
    )


if __name__ == "__main__":
    main()
