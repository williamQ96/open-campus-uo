# SPDX-License-Identifier: Apache-2.0
"""Export the Agate and Emerald block exteriors and their public approaches."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import split
import trimesh


emerald = import_module("build-emerald-onyx-frontages-review")
fairmount, garden, geometry = emerald.fairmount, emerald.garden, emerald.geometry
base, potter, frontages = emerald.base, emerald.potter, emerald.frontages
northwest, millrace = emerald.northwest, emerald.millrace
PACKAGE = "agate-emerald-frontages-review"
GROUND = "agate-emerald-approaches"
CEMENT = (156, 154, 143)
METAL = (79, 85, 78)
PARKING_WALL = (146, 151, 133)


def prune_rings(shape):
    if not shape.interiors:
        return [shape]
    south = max(Polygon(r).bounds[1] for r in shape.interiors)
    north = min(Polygon(r).bounds[3] for r in shape.interiors)
    if south >= north:
        raise ValueError("The courtyard rings require distinct ground section cuts.")
    midpoint = (south + north) / 2
    west, _, east, _ = shape.bounds
    cut = LineString([(west - 1, midpoint), (east + 1, midpoint)])
    sections = list(geometry.sections(split(shape, cut)))
    if any(piece.interiors for piece in sections):
        raise ValueError("Ground collision sections must have simple rings.")
    if not np.isclose(sum(piece.area for piece in sections), shape.area):
        raise ValueError("The collision subdivision changed the ground area.")
    return sections


def output(parts, row, roof, occupied, supports, gates):
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{key: row[key] for key in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(roof),
        "ground_footprints_enu_m": [
            base.ring(orient(p)) for p in prune_rings(occupied)
        ],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(roof.area, 3),
        "base_z_m": row["base_z_m"],
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": gates,
    }
    if roof.interiors:
        record["footprint_holes_enu_m"] = [list(h.coords)[:-1] for h in roof.interiors]
    return mesh, record, occupied, supports


def doorway(paving, row, field, face, point, entry):
    return frontages.estimated_entry(
        paving,
        {
            **row,
            "entry": {**entry["route"], "bearing": entry["bearing"]},
            "entry_finish": "stone",
        },
        field,
        face,
        point,
    )


def parking_supports(parts, paving, row, field):
    ceiling = row["parking_ceiling_z_m"]
    piers = []
    for e, n in row["parking_posts"]:
        pad = orient(box(e - 0.145, n - 0.167, e + 0.145, n + 0.167))
        low = emerald.grade(field, (e, n))
        if ceiling - low < 2.15:
            raise ValueError(
                "The observed parking frontage must stay open below the deck."
            )
        base.flat(parts, pad, low - 0.12, ceiling + 0.12, (146, 141, 127), CEMENT)
        base.flat(
            parts,
            box(e - 0.188, n - 0.209, e + 0.188, n + 0.209),
            low - 0.082,
            low + 0.31,
            CEMENT,
        )
        piers.append(pad)
    w, s, e, n = row["parking_paving"]
    for y0, y1 in zip(np.linspace(s, n, 11)[:-1], np.linspace(s, n, 11)[1:]):
        millrace.western.terrace(paving, field, orient(box(w, y0, e, y1)))
    for north in np.linspace(s + 1.9, n - 1.7, 9):
        y = emerald.grade(field, (e - 0.35, north))
        wheel_stop = box(e - 0.43, north - 0.82, e - 0.23, north + 0.80)
        base.flat(paving, wheel_stop, y - 0.035, y + 0.093, (75, 77, 65))
    return piers


def courtyard_floors(paving, roof, field):
    for ring in roof.interiors:
        court = orient(Polygon(ring))
        center = np.array(court.centroid.coords[0])
        level = 10.42
        base.flat(
            paving,
            court,
            emerald.grade(field, center) - 0.12,
            level,
            (141, 145, 116),
            (159, 159, 135),
        )
        x, y = center
        bounds = court.bounds
        walk = orient(
            court.intersection(
                box(x - 0.63, bounds[1] - 0.1, x + 0.63, bounds[3] + 0.1)
            )
        )
        base.flat(paving, walk, level - 0.025, level + 0.052, CEMENT)


def studies_facades(parts, row, upper, field, height, entree, door):
    levels = row["levels_z_m"]
    trim = row["trim_color"]
    slots = [(Point(e, n), w, tone) for e, n, w, tone in row["north_panels"]]
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, upper):
        if span < 1.29:
            continue
        stations = []
        if normal[1] > 0.97:
            for point, width, tone in slots:
                if edge.distance(point) > 0.47:
                    continue
                at = edge.project(point)
                left = max(0.04, at - width / 2)
                right = min(span - 0.04, at + width / 2)
                if right - left < 1.23:
                    continue
                for a, b in zip(
                    np.linspace(left, right, 11)[:-1], np.linspace(left, right, 11)[1:]
                ):
                    cap = min(height(plan(x, 0)) for x in (a, b)) - 0.19
                    add(a, b, 0.009, 0.038, levels[0] - 0.38, cap, tone)
                    add(
                        a + 0.018,
                        a + 0.028,
                        0.039,
                        0.045,
                        levels[0] - 0.39,
                        cap,
                        (128, 128, 109),
                    )
                stations.append(at)
        u = span / 2
        lowest = emerald.grade(field, plan(u, 0))
        if normal[0] < -0.98 and span > 25:
            fascia = row["parking_ceiling_z_m"]
            add(0.032, span - 0.032, 0.02, 0.14, fascia - 0.065, fascia + 0.35, trim)
        if not stations:
            count = max(1, round(span / 3.1))
            stations = (np.arange(count) + 0.5) * span / count
            pitch_top = min(
                height(plan(x, 0)) for x in np.linspace(0.03, span - 0.03, 6)
            )
            millrace.siding(
                add,
                span,
                pitch_top - 0.18,
                max(lowest, levels[0] - 0.23),
                row["seam_color"],
                0.193,
            )
        entry_at = edge.project(door) if edge.equals(entree) else None
        if entry_at is not None:
            low = row["north_entry"]["route"]["threshold_z_m"]
            potter.door(add, entry_at, low, trim)
            add(
                entry_at - 1.17,
                entry_at + 1.17,
                -0.04,
                0.89,
                low + 2.21,
                low + 2.39,
                trim,
            )
        for center in stations:
            width = min(
                1.66, max(0.84, span / 5), 2 * (span - center) - 0.07, 2 * center - 0.07
            )
            if width < 0.59:
                continue
            upper_edge = (
                min(
                    height(plan(t, 0))
                    for t in (center - width / 2, center, center + width / 2)
                )
                - 0.26
            )
            for i, z in enumerate(levels):
                if not i and entry_at is not None and abs(center - entry_at) < 1.26:
                    continue
                sill = z + 0.49
                head = min(upper_edge, sill + 1.30)
                if head - sill > 0.44:
                    northwest.window_grid(add, center, width, sill, head, 2, 1, trim)


def studies(row, field, paving):
    roof = orient(
        set_precision(Polygon(row["outline_enu_m"], row["holes_enu_m"]), 0.002)
    )
    upper = orient(roof.buffer(-row["eaves_m"], join_style="mitre"))
    floor = upper.difference(box(*row["parking_open"]))
    parts = []
    high = row["parking_ceiling_z_m"]
    roof_at = garden.roof_sections(parts, roof, upper, high, row, grid=0.0002)
    for section in geometry.sections(floor):
        base.flat(
            parts, orient(section), row["base_z_m"], high + 0.02, PARKING_WALL, CEMENT
        )
    supports = parking_supports(parts, paving, row, field)
    courtyard_floors(paving, roof, field)
    approach = row["north_entry"]
    face, point = potter.choose_face(
        upper, {**approach, "gate": approach["route"]["gate"]}
    )
    studies_facades(parts, row, upper, field, roof_at, face, point)
    gate = doorway(paving, row, field, face, point, approach)
    return output(parts, row, roof, floor, supports, [gate])


def market(row, field, paving):
    roof = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = orient(
        roof.buffer(-row["eaves_m"], join_style="mitre").difference(box(*row["recess"]))
    )
    parts = []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    entry = row["storefront"]
    face, point = potter.choose_face(wall, {**entry, "gate": entry["route"]["gate"]})
    panel, north, width = row["arcade_east"]
    supports = []
    for n in (north - width / 2, north + width / 2):
        post = orient(box(panel - 0.148, n - 0.145, panel + 0.148, n + 0.145))
        foot = emerald.grade(field, (panel, n))
        head = height((panel, n)) - 0.13
        base.flat(parts, post, foot - 0.18, head, row["trim_color"])
        base.flat(
            parts,
            box(panel - 0.24, n - 0.24, panel + 0.24, n + 0.24),
            foot - 0.08,
            foot + 0.59,
            CEMENT,
        )
        supports.append(post)
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.78:
            continue
        if edge.equals(face):
            station = edge.project(point)
            threshold = entry["route"]["threshold_z_m"]
            potter.door(add, station, threshold, (117, 118, 99))
            for u in (station - 1.27, station + 1.28):
                northwest.window_grid(
                    add,
                    u,
                    1.15,
                    threshold + 0.43,
                    threshold + 2.37,
                    2,
                    2,
                    row["trim_color"],
                )
            add(
                0.04,
                span - 0.04,
                0.01,
                0.12,
                threshold + 2.44,
                threshold + 2.76,
                (81, 111, 127),
            )
        elif normal[0] > 0.97 and edge.distance(Point(row["wall_blue"])) < 0.52:
            top = min(height(plan(u, 0)) for u in (0.04, span - 0.04)) - 0.28
            add(0.04, span - 0.04, 0.01, 0.029, 7.32, top, (96, 142, 175))
        elif normal[1] > 0.97 and span > 9.5:
            add(0.09, span - 0.09, 0.012, 0.046, 7.35, 10.16, (96, 142, 175))
            for u in (1.15, 2.66):
                northwest.window_grid(add, u, 1.22, 7.81, 9.62, 2, 2, row["trim_color"])
    millrace.western.terrace(paving, field, orient(box(*row["apron"])))
    return output(
        parts,
        row,
        roof,
        wall,
        supports,
        [doorway(paving, row, field, face, point, entry)],
    )


def raised_bay(parts, row, wall):
    spec = row["projecting_bay"]
    edge, point = potter.choose_face(wall, {**spec, "gate": row["id"]})
    _, add, _, plan = millrace.basis(parts, *edge.coords)
    at = edge.project(point)
    w, depth = spec["width_m"], spec["projection_m"]
    bottom, high = spec["heights_m"]
    bay = orient(
        Polygon(
            [
                plan(at - w / 2, -0.06),
                plan(at + w / 2, -0.06),
                plan(at + w / 2, depth * 0.5),
                plan(at + w * 0.32, depth),
                plan(at - w * 0.32, depth),
                plan(at - w / 2, depth * 0.5),
            ]
        )
    )
    base.flat(parts, bay, bottom, high, row["wall_color"])
    for _, (span, frame, _, _, _, _) in fairmount.views(parts, bay):
        if 0.48 < span < w - 0.1:
            northwest.window_grid(
                frame,
                span / 2,
                span * 0.77,
                bottom + 0.46,
                high - 0.32,
                2 if span > 1.4 else 1,
                1,
                row["trim_color"],
            )
    add(
        at - w / 2 - 0.11,
        at + w / 2 + 0.11,
        -0.05,
        depth + 0.10,
        high - 0.08,
        high + 0.13,
        row["trim_color"],
    )


def build(row, field, paving):
    if "parking_open" in row:
        return studies(row, field, paving)
    if "storefront" in row:
        return market(row, field, paving)
    mesh, record, wall, supports = emerald.build(row, field, paving)
    if "projecting_bay" in row:
        parts = [mesh]
        raised_bay(parts, row, wall)
        mesh = garden.science.ordered_mesh(trimesh.util.concatenate(parts))
    return mesh, record, wall, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "agate_emerald_frontages_site", build
    )


if __name__ == "__main__":
    main()
