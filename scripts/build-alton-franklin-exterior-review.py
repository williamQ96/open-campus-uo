# SPDX-License-Identifier: Apache-2.0
"""Export the Alton Baker shelters and the Best Western Franklin wing."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.affinity import affine_transform
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
northwest = import_module("build-northwest-infill-exterior-review")
garden, geometry, base = fairmount.garden, fairmount.geometry, fairmount.base
chapter = fairmount.chapter
PACKAGE = "alton-franklin-exterior-review"
GROUND = "alton-franklin-paving"
TIMBER = (128, 105, 78)
BRACE = (107, 88, 67)
TABLE = (132, 105, 81)
STEEL = (84, 91, 84)
CONCRETE = (162, 158, 140)
TRIM = (76, 81, 77)
GRAY = (153, 148, 132)
YELLOW = (207, 173, 103)


def frame(row):
    origin = np.array(row["roof_frame"]["origin_enu_m"])
    along = np.array(row["roof_frame"]["axis"], dtype=float)
    along /= np.linalg.norm(along)
    across = np.array([-along[1], along[0]])
    transform = [along[0], across[0], along[1], across[1], *origin]

    def world(u, v):
        return origin + u * along + v * across

    def polygon(bounds):
        return orient(affine_transform(box(*bounds), transform))

    return origin, along, across, world, polygon


def table(parts, polygon, u, v, length, floor):
    left, right = u - length / 2, u + length / 2
    desk = polygon([left, v - 0.36, right, v + 0.36])
    base.flat(parts, desk, floor + 0.69, floor + 0.78, TABLE)
    for offset in (-0.65, 0.65):
        bench = polygon([left, v + offset - 0.13, right, v + offset + 0.13])
        base.flat(parts, bench, floor + 0.42, floor + 0.50, TABLE)
    for x in (left + 0.43, right - 0.43):
        crossbar = polygon([x - 0.052, v - 0.76, x + 0.052, v + 0.76])
        base.flat(parts, crossbar, floor + 0.38, floor + 0.43, STEEL)
        for offset in (-0.53, 0.53):
            leg = polygon(
                [x - 0.043, v + offset - 0.043, x + 0.043, v + offset + 0.043]
            )
            base.flat(parts, leg, floor, floor + 0.44, STEEL)
        mid = polygon([x - 0.05, v - 0.06, x + 0.05, v + 0.06])
        base.flat(parts, mid, floor + 0.36, floor + 0.71, STEEL)
    return polygon([left, v - 0.79, right, v + 0.79])


def close_roof_steps(parts, world, outline, roof_at, zones):
    interior = outline.buffer(-0.03)
    for zone in zones:
        corners = list(box(*zone["bounds_m"]).exterior.coords)
        for start, stop in zip(corners[:-1], corners[1:]):
            span, _, _, plan, _, slab = chapter.setup_face(
                parts, world(*start), world(*stop)
            )
            stations = np.linspace(0, span, max(2, int(np.ceil(span / 0.14))))
            for a, b in zip(stations[:-1], stations[1:]):
                points = [plan(u, side) for u in (a, b) for side in (-0.062, 0.062)]
                if not all(interior.covers(Point(p)) for p in points):
                    continue
                profile = np.array([roof_at(p) for p in points]).reshape(2, 2)
                if min(np.ptp(profile, axis=1)) < 0.23:
                    continue
                bottom, top = profile.min(axis=1) - 0.20, profile.max(axis=1) - 0.085
                panel = Polygon(
                    [(a, bottom[0]), (b, bottom[1]), (b, top[1]), (a, top[0])]
                )
                slab(panel, -0.083, 0.083, BRACE)


def pavilion(row, outline, field, paving):
    _, _, _, world, polygon = frame(row)
    pad = polygon(row["slab_bounds_m"])
    floor = max(geometry.sample_ground(field, *p) for p in pad.exterior.coords) + 0.055
    base.flat(paving, pad, floor - 0.38, floor, CONCRETE)
    parts = []
    roof_at = garden.roof_sections(parts, outline, Polygon(), floor, row, grid=0.0002)
    utility = polygon(row["utility_bounds_m"])
    utility_top = min(
        floor + row["utility_height_m"],
        min(roof_at(point) for point in utility.exterior.coords) - 0.16,
    )
    base.flat(parts, utility, floor - 0.04, utility_top, BRACE, row["trim_color"])
    for line, (span, add, _, _, _, _) in fairmount.views(parts, utility):
        if line.length > 1.3:
            add(0.07, span - 0.07, 0.01, 0.059, floor + 0.86, floor + 1.02, CONCRETE)
    if len(row["roof_zones"]) > 1:
        close_roof_steps(parts, world, outline, roof_at, row["roof_zones"])

    supports = []
    front, back = row["post_rows_m"]
    for u in row["post_spacing_m"]:
        for v in (front, back):
            p = world(u, v)
            post = polygon([u - 0.13, v - 0.13, u + 0.13, v + 0.13])
            assert outline.covers(post), row["id"]
            grade = min(floor, geometry.sample_ground(field, *p))
            post_top = roof_at(p) - 0.16
            base.flat(parts, post, grade - 0.16, post_top, TIMBER)
            base.flat(parts, post.buffer(0.044), grade - 0.12, grade + 0.18, CONCRETE)
            supports.append(post)
            step = 0.76 if v == front else -0.76
            fairmount.beam(
                parts,
                (*p, post_top - 0.96),
                (*world(u, v + step), post_top - 0.18),
                0.135,
                BRACE,
            )
        tie_z = min(roof_at(world(u, v)) for v in (front, back)) - 0.23
        fairmount.beam(
            parts, (*world(u, front), tie_z), (*world(u, back), tie_z), 0.21, BRACE
        )

    posts = row["post_spacing_m"]
    for v in (front, back):
        value = min(roof_at(world(u, v)) for u in posts) - 0.25
        fairmount.beam(
            parts,
            (*world(posts[0], v), value),
            (*world(posts[-1], v), value),
            0.196,
            TIMBER,
        )
    for u in (posts[0], posts[-1]):
        level = min(roof_at(world(u, v)) for v in (front, back)) - 0.13
        for v in np.arange(front + 0.27, back - 0.19, 0.29):
            z = roof_at(world(u, v)) - 0.16
            if z - level > 0.18:
                fairmount.beam(
                    parts, (*world(u, v), level), (*world(u, v), z), 0.08, BRACE
                )
    for v in row["table_rows_m"]:
        for u, length in row["table_lengths_m"]:
            supports.append(table(parts, polygon, u, v, length, floor))
    return parts, utility, supports, floor


def hotel_front(parts, row, wall, field, roof_at):
    origin, along, across, _, _ = frame(row)
    for _, (span, add, normal, plan, _, slab) in fairmount.views(parts, wall):
        if span < 2.0:
            continue
        e, n = plan(span / 2, 0)
        u, v = (np.array([e, n]) - origin) @ along, (np.array([e, n]) - origin) @ across
        floor = geometry.sample_ground(field, e, n)
        top = min(roof_at(plan(x, 0)) for x in (0.08, span / 2, span - 0.08))
        street = normal @ across < -0.91
        if -10.01 < u < -1.34 and v < -3.85:
            offsets = np.linspace(0.028, span - 0.028, 17)
            heights = [
                min(
                    roof_at(plan(t, 0)),
                    3.44 + 0.462 * ((plan(t, 0) - origin) @ across + 8.47),
                )
                - 0.17
                for t in offsets
            ]
            panel = [(offsets[0], floor - 0.16), (offsets[-1], floor - 0.16)]
            panel.extend(reversed(list(zip(offsets, heights))))
            slab(Polygon(panel), 0.011, 0.046, YELLOW)
            for z in np.arange(floor + 0.12, top - 0.30, 0.21):
                add(0.027, span - 0.027, 0.046, 0.058, z, z + 0.016, (184, 146, 80))
        elif street and u > 0 and v < -5:
            add(0.02, span - 0.02, 0.024, 0.085, floor + 2.7, floor + 2.83, TRIM)
            northwest.window_grid(
                add, span * 0.49, span * 0.82, floor + 0.62, floor + 2.57, 5, 2, TRIM
            )
        elif (abs(normal @ along) > 0.9 or normal @ across > 0.9) and span > 3.4:
            for at in np.linspace(span * 0.22, span * 0.80, max(2, round(span / 3.7))):
                for sill, head in (
                    (floor + 1.01, floor + 2.51),
                    (floor + 3.11, floor + 3.72),
                ):
                    if top > head + 0.56:
                        northwest.window_grid(
                            add, at, min(1.44, span * 0.28), sill, head, 2, 1, TRIM
                        )
        if u > 0 and top > floor + 3.25:
            for z in np.arange(floor + 2.96, top - 0.16, 0.25):
                add(0.02, span - 0.03, 0.015, 0.028, z, z + 0.015, (131, 125, 113))


def hotel(row, outline, field, paving):
    _, _, _, world, polygon = frame(row)
    roof = orient(
        outline.difference(polygon(row["terrace_cut_m"])).difference(
            polygon(row["east_setback_m"])
        )
    )
    wall = orient(roof.buffer(-0.145, join_style="mitre"))
    floor, _ = garden.science.earlier.fit_base(field, wall)
    parts = []
    roof_at = garden.roof_sections(parts, roof, wall, floor, row, grid=0.0002)
    hotel_front(parts, row, wall, field, roof_at)
    for a, b, c, d in row["roof_units_m"]:
        box_ = polygon([a, b, c, d])
        z = roof_at(box_.centroid.coords[0])
        base.flat(parts, box_, z - 0.08, z + 0.37, GRAY, CONCRETE)
    tip = polygon([9.44, -7.82, 9.76, -5.45])
    tip_top = roof_at(world(9.62, -6.43))
    base.flat(parts, tip, tip_top - 0.34, tip_top + 1.27, row["trim_color"], TRIM)
    deck = polygon(row["terrace_bounds_m"])
    level = geometry.sample_ground(field, *deck.centroid.coords[0]) + 0.12
    base.flat(paving, deck, level - 0.33, level, CONCRETE)
    surrounds = [polygon(bounds) for bounds in row["terrace_walls_m"]]
    for piece in surrounds:
        base.flat(parts, piece, level - 0.12, level + 1.07, TRIM)
    return parts, wall, surrounds, floor, roof


def model(row, field, paving):
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    if row["kind"] == "pavilion":
        parts, solid, supports, floor = pavilion(row, outline, field, paving)
    else:
        parts, solid, supports, floor, outline = hotel(row, outline, field, paving)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{key: row[key] for key in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(p) for p in geometry.sections(solid)],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [],
    }
    return mesh, record, solid, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "alton_franklin_exterior_site", model
    )


if __name__ == "__main__":
    main()
