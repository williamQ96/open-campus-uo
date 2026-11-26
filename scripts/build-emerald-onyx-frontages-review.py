# SPDX-License-Identifier: Apache-2.0
"""Export the registered Emerald, Onyx and East 21st building exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient
import trimesh


onyx = import_module("build-onyx-university-frontages-review")
fairmount, garden, geometry = onyx.fairmount, onyx.garden, onyx.geometry
harris, potter, frontages = onyx.harris, onyx.potter, onyx.frontages
base, millrace, northwest, chapter = (
    onyx.base,
    onyx.millrace,
    onyx.northwest,
    onyx.chapter,
)
PACKAGE = "emerald-onyx-frontages-review"
GROUND = "emerald-onyx-approaches"
CONCRETE = (160, 154, 135)
DECK = (170, 165, 147)


def grade(field, point):
    # The south edge of 1314 East 21st extends beyond the terrain and height grids.
    e, n = point
    return geometry.sample_ground(field, e, max(n, field["min_north_m"]))


def exterior_stair(parts, field, plan, at, level, run, width, trim):
    low = grade(field, plan(at, run)) + 0.065
    frontages.staircase(parts, plan, at, width, (0.04, run), low, level, DECK)
    for x in (at - width / 2, at + width / 2):
        fairmount.beam(
            parts,
            (*plan(x, 0.1), level + 0.86),
            (*plan(x, run), low + 0.86),
            0.052,
            trim,
        )
        for t in np.linspace(0.02, 0.98, 5):
            d, z = run * t, (1 - t) * level + t * low
            fairmount.beam(
                parts, (*plan(x, d), z - 0.05), (*plan(x, d), z + 0.88), 0.039, trim
            )
    return orient(fairmount.rectangle(plan, at - width / 2, at + width / 2, 0.02, run))


def balcony(parts, add, plan, at, width, depth, level, trim):
    left, right = at - width / 2, at + width / 2
    add(left, right, -0.07, depth, level - 0.18, level, DECK)
    for start, end in (
        (plan(left, 0.03), plan(left, depth)),
        (plan(left, depth), plan(right, depth)),
        (plan(right, 0.03), plan(right, depth)),
    ):
        onyx.parking.railing(parts, start, end, level)
    for x in (left + 0.095, right - 0.095):
        add(
            x - 0.047,
            x + 0.047,
            depth - 0.116,
            depth - 0.02,
            level - 0.03,
            level + 0.91,
            trim,
        )


def dormer(parts, add, row, plan, at, width, bottom, wall_height, rise):
    half = width / 2
    add(
        at - half,
        at + half,
        -0.72,
        0.14,
        bottom - 0.38,
        bottom + wall_height,
        row["wall_color"],
    )
    chapter.gabled_canopy(
        parts,
        plan,
        at,
        half + 0.14,
        -0.72,
        0.24,
        bottom + wall_height,
        rise,
        row["roof_color"],
        row["trim_color"],
    )

    def dormer_trim(left, right, start, end, low, high, color):
        add(left, right, start + 0.14, end + 0.14, low, high, color)

    northwest.window_grid(
        dormer_trim,
        at,
        width - 0.28,
        bottom + 0.13,
        bottom + wall_height - 0.10,
        2,
        1,
        row["trim_color"],
    )


def windows(add, spans, at, span, trim, height, plan):
    for offset, width, lo, hi in spans:
        u = at + offset
        left, right = u - width / 2, u + width / 2
        if left < 0.03 or right > span - 0.02:
            raise ValueError(
                f"Window does not fit facade station {u:.2f}/{span:.2f} m."
            )
        ceiling = min(height(plan(x, 0)) for x in (left, u, right)) - 0.27
        head = min(hi, ceiling)
        sill = min(lo, head - 0.62)
        northwest.window_grid(
            add, u, width, sill, head, 2, 1 if width < 1.3 else 2, trim
        )


def explicit_front(parts, paving, row, field, edge, view, point, detail, height):
    span, add, _, plan, _, _ = view
    trim, at = row["trim_color"], edge.project(point)
    hold = []
    windows(add, detail.get("windows", ()), at, span, trim, height, plan)
    for offset, width in detail.get("garages", ()):
        u = at + offset
        if not 0.22 < u - width / 2 < u + width / 2 < span - 0.19:
            raise ValueError(f"Garage exceeds the registered frontage on {row['id']}.")
        harris.garage_front(
            add,
            plan,
            u,
            field,
            {"width_m": width, "color": detail.get("garage_color", (117, 114, 98))},
        )
    if "garage_band" in detail:
        left, right, z = detail["garage_band"]
        add(at + left, at + right, 0.018, 0.56, z, z + 0.24, trim)
    if "dormer" in detail:
        offset, w, z, wall_h, rise = detail["dormer"]
        dormer(parts, add, row, plan, at + offset, w, z, wall_h, rise)
    if "canopy" in detail:
        w, depth, z = detail["canopy"]
        add(at - w / 2, at + w / 2, -0.06, depth, z, z + 0.16, trim)
    if "stair" in detail:
        offset, top, length, width = detail["stair"]
        hold.append(
            exterior_stair(parts, field, plan, at + offset, top, length, width, trim)
        )
        potter.door(add, at + offset, top, trim)
    if "balcony" in detail:
        offset, w, depth, top = detail["balcony"]
        balcony(parts, add, plan, at + offset, w, depth, top, trim)
    if detail.get("address_plate"):
        add(at + 0.93, at + 1.43, 0.012, 0.049, 13.42, 13.56, trim)
    route = None
    if "door" in detail:
        offset, level = detail["door"]
        u = at + offset
        potter.door(add, u, level, detail.get("door_color", trim))
        if "porch" in detail:
            hold.extend(
                potter.porch(
                    parts, {**row, "porch": detail["porch"]}, field, plan, u, level
                )
            )
        if detail.get("porch_rail"):
            width, depth, _ = detail["porch"]
            onyx.parking.railing(
                parts,
                plan(u - width * 0.46, depth),
                plan(u + width * 0.46, depth),
                level,
            )
        if detail.get("porch_side_stair"):
            width, depth, _ = detail["porch"]
            # The lower treads are on the east side of the south-facing porch.
            near = plan(u + width / 2 - 0.06, depth / 2)
            far = plan(u + width / 2 + 1.12, depth / 2)
            northwest.stair(
                parts, far, near, grade(field, far) + 0.05, level, 0.90, steps=5
            )
        if "route" in detail:
            route = frontages.estimated_entry(
                paving,
                {
                    **row,
                    "entry": {**detail["route"], "bearing": detail["bearing"]},
                    "entry_finish": "stone",
                },
                field,
                edge,
                edge.interpolate(u),
            )
    return hold, route


def facades(parts, paving, row, wall, field, height):
    designated = []
    for spec in row["frontages"]:
        min_span = spec.get("minimum", 2.1)
        ref = {**spec, "gate": row["id"]}
        edge, point = potter.choose_face(wall, ref, min_span)
        designated.append((edge, point, spec))
    supports, gates = [], []
    trim = row["trim_color"]
    for edge, view in fairmount.views(parts, wall):
        span, add, _, plan, _, _ = view
        if span < 0.70:
            continue
        active = [
            (point, detail) for face, point, detail in designated if edge.equals(face)
        ]
        top = min(height(plan(u, 0)) for u in np.linspace(0.04, span - 0.04, 7))
        millrace.siding(
            add,
            span,
            top - 0.21,
            max(row["levels_z_m"][0] - 0.48, grade(field, plan(span / 2, 0)) - 0.11),
            row["seam_color"],
            0.18,
        )
        for point, detail in active:
            piers, gate = explicit_front(
                parts, paving, row, field, edge, view, point, detail, height
            )
            supports.extend(piers)
            if gate:
                gates.append(gate)
        # Observed elevations use their itemized openings. Side and rear spacing is inferred.
        if active or span < 1.55:
            continue
        count = max(1, round(span / row["bay_m"]))
        width = min(1.39, 0.61 * span / count)
        for u in (np.arange(count) + 0.5) * span / count:
            ceiling = (
                min(height(plan(x, 0)) for x in (u - width / 2, u, u + width / 2))
                - 0.25
            )
            ground = grade(field, plan(u, 0))
            for floor in row["levels_z_m"]:
                lo = floor + 0.69
                hi = min(lo + 1.13, ceiling)
                if hi - lo > 0.48 and lo > ground + 0.28:
                    northwest.window_grid(add, u, width, lo, hi, 2, 1, trim)
    return supports, gates


def terrain_apron(paving, field, west, east, south):
    north = field["min_north_m"]
    spacing = field["spacing_m"]
    grid = np.arange(field["min_east_m"], east, spacing)
    stations = [west, *grid[grid > west], east]
    grass = (135, 143, 107)

    def surface(e, n):
        return grade(field, (e, north)) + 0.012

    for a, b in zip(stations, stations[1:]):
        strip = orient(box(a, south, b, north + 0.018))
        bottom = min(surface(*p) for p in strip.exterior.coords) - 0.18
        paving.append(geometry.shell(strip, bottom, surface, grass, grass))


def build(row, field, paving):
    roof = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = roof.buffer(-row["eaves_m"], join_style="mitre")
    if "recess" in row:
        wall = wall.difference(box(*row["recess"]))
    wall = orient(wall)
    parts = []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    supports, gates = facades(parts, paving, row, wall, field, height)
    if "driveway" in row:
        millrace.western.terrace(paving, field, orient(box(*row["driveway"])))
    if "terrain_apron" in row:
        terrain_apron(paving, field, *row["terrain_apron"])
    if "chimney" in row:
        e, n, w, d, rise, color = row["chimney"]
        level = height((e, n))
        base.flat(
            parts,
            box(e - w / 2, n - d / 2, e + w / 2, n + d / 2),
            level - 0.48,
            level + rise,
            color,
            CONCRETE,
        )
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{key: row[key] for key in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(roof),
        "ground_footprints_enu_m": [base.ring(wall)],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(roof.area, 3),
        "base_z_m": row["base_z_m"],
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": gates,
    }
    return mesh, record, wall, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "emerald_onyx_frontages_site", build
    )


if __name__ == "__main__":
    main()
