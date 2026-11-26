# SPDX-License-Identifier: Apache-2.0
"""Export the Steam Plant, Phi Kappa Psi, 642 E 8th and 1414 Alder exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
garden, base, geometry = fairmount.garden, fairmount.base, fairmount.geometry
chapter, millrace, beam = fairmount.chapter, fairmount.millrace, fairmount.beam
PACKAGE = "northwest-infill-exterior-review"
GROUND = "northwest-infill-approaches"
STEEL = (57, 69, 71)
GLASS = (63, 91, 98)
WOOD = (151, 105, 74)
LIGHT = (220, 216, 193)


def edges(wall, heading=None, minimum=2.0):
    for a, b in garden.shared.face_edges(wall):
        direction = garden.neighbor.bearing(a, b)
        if LineString([a, b]).length >= minimum and (
            heading is None or np.dot(direction, heading) > 0.96
        ):
            yield a, b


def window_grid(add, center, width, bottom, top, columns, rows, trim=LIGHT):
    if top - bottom < 0.36:
        return
    left, right = center - width / 2, center + width / 2
    add(left - 0.055, right + 0.055, 0.012, 0.080, bottom - 0.06, top + 0.06, trim)
    add(left, right, 0.081, 0.096, bottom, top, GLASS)
    for x in np.linspace(left, right, columns + 1)[1:-1]:
        add(x - 0.019, x + 0.019, 0.096, 0.12, bottom, top, trim)
    for y in np.linspace(bottom, top, rows + 1)[1:-1]:
        add(left, right, 0.096, 0.12, y - 0.018, y + 0.018, trim)


def chapter_house(parts, row, wall, outline, floor, highest):
    white = row["trim_color"]
    south = list(edges(wall, [0, -1]))
    for edge in edges(wall, minimum=3):
        span, add, _, plan, _, _ = chapter.setup_face(parts, *edge)
        h = min(highest(edge[0]), highest(edge[1]))
        add(0.045, span - 0.045, 0.013, 0.126, 3.20, 3.37, white)
        add(0.045, span - 0.045, 0.018, 0.143, h - 0.25, h - 0.13, white)
        indent = 1.15
        for at in np.linspace(indent, span - indent, max(1, round(span / 2.55))):
            position = plan(at, 0)
            recessed = (
                edge in south
                and -857.6 <= position[0] <= -850.55
                and position[1] < 275.5
            )
            for sill in (0.03, 4.19):
                if recessed and sill < 4:
                    continue
                if floor + 0.4 < sill and highest(position) > sill + 1.65:
                    window_grid(add, at, 1.02, sill, sill + 1.48, 2, 3, white)
                    for sign in (-1, 1):
                        x = at + sign * 0.71
                        add(
                            x - 0.134,
                            x + 0.134,
                            0.029,
                            0.096,
                            sill,
                            sill + 1.50,
                            (77, 105, 93),
                        )
    a, b = row["porch_front_enu_m"]
    span, add, _, plan, _, slab = chapter.setup_face(parts, a, b)
    arcade_bottom = -1.64
    arch_top = 2.80
    arcade = box(0, arcade_bottom, span, 3.31)
    centers = [span * fraction for fraction in (0.19, 0.5, 0.81)]
    width = 1.62
    cutouts = [
        chapter.arch(u, arcade_bottom - 0.03, width, arch_top - arcade_bottom, 0.64)
        for u in centers
    ]
    slab(arcade.difference(unary_union(cutouts)), -0.12, 0.23, white)
    for u in centers:
        inner = chapter.arch(
            u, arcade_bottom - 0.06, width, arch_top - arcade_bottom, 0.64
        )
        outer = chapter.arch(
            u, arcade_bottom - 0.06, width + 0.21, arch_top - arcade_bottom + 0.16, 0.76
        )
        trim = outer.difference(inner).intersection(box(0, arcade_bottom, span, 3.20))
        slab(trim, 0.228, 0.272, white)
    add(0, span, -0.13, 0.34, 3.22, 3.44, white)
    fairmount.balustrade(
        parts, plan(0.07, 0.23), plan(span - 0.07, 0.23), 3.42, (115, 126, 107)
    )
    supports = [
        fairmount.rectangle(plan, left, right, 0.01, 0.22)
        for left, right in zip(
            (0, centers[0] + width / 2, centers[1] + width / 2, centers[2] + width / 2),
            (
                centers[0] - width / 2,
                centers[1] - width / 2,
                centers[2] - width / 2,
                span,
            ),
        )
    ]
    for e in (-859.9, -857.2, -854.5):
        fairmount.dormer(
            parts,
            row,
            {
                "near": [e, 275.1],
                "bearing": 180,
                "width": 1.22,
                "depth": 1.78,
                "sill": 8.81,
                "top": 10.15,
                "style": "gable",
                "windows": 1,
            },
            highest,
            outline,
        )
    for e, n in [(-865.18, 281.8), (-847.32, 283.65), (-861.21, 294.6)]:
        h = highest((e, n))
        base.flat(
            parts,
            box(e - 0.41, n - 0.32, e + 0.41, n + 0.32),
            h - 0.34,
            h + 1.04,
            white,
            (119, 118, 102),
        )
    return supports


def retail(parts, row, wall, field, highest):
    rail, steel, upper = (168, 181, 170), (124, 141, 138), (89, 98, 93)
    for a, b in edges(wall):
        span, add, normal, plan, _, _ = chapter.setup_face(parts, a, b)
        y = geometry.sample_ground(field, *plan(span / 2, 0)) + 0.07
        top = min(highest(a), highest(b)) - 0.19
        if top - y < 2.0:
            continue
        split = y + 1.72
        add(0.025, span - 0.025, 0.011, 0.054, y, split, steel)
        add(0.025, span - 0.025, 0.011, 0.041, split, top, upper)
        add(0.03, span - 0.03, 0.053, 0.074, split, split + 0.063, rail)
        for i in np.arange(0.14, span - 0.08, 0.31):
            add(i, i + 0.018, 0.055, 0.070, y + 0.07, split, rail)
        millrace.siding(add, span, top, split, (68, 76, 72), 0.24)
        if normal[0] > 0.95 and span > 16:
            for u in [span * 0.21, span * 0.50, span * 0.81]:
                add(u - 0.046, u + 0.046, 0.067, 0.154, y + 0.1, top - 0.31, STEEL)
                add(u - 0.15, u + 0.15, 0.065, 0.22, top - 0.48, top - 0.27, STEEL)
        if span < 6 and normal[0] > 0.95 and plan(span / 2, 0)[1] > 589:
            millrace.door(add, span * 0.55, y, rail)
    a, b = row["porch_front_enu_m"]
    span, add, _, plan, _, _ = chapter.setup_face(parts, a, b)
    y = geometry.sample_ground(field, *plan(span / 2, 0)) + 0.05
    h = min(highest(a), highest(b)) + 0.13
    add(0, span, -0.07, 0.11, y + 2.42, h, WOOD)
    add(span - 0.29, span, -0.14, 0.14, y, y + 2.42, WOOD)
    for z in np.arange(y + 2.49, h - 0.035, 0.205):
        add(0.023, span - 0.017, 0.111, 0.125, z, z + 0.014, (109, 75, 53))
    add(0, span, -0.075, 0.14, h - 0.035, h + 0.04, rail)
    north_span, north_add, *_ = chapter.setup_face(
        parts, (-967.84, 594.84), (-970.4, 594.84)
    )
    north_add(0, north_span, -0.047, 0.11, y + 2.42, h, WOOD)
    for z in np.arange(y + 2.49, h - 0.035, 0.205):
        north_add(0.015, north_span - 0.014, 0.111, 0.125, z, z + 0.014, (109, 75, 53))
    return [fairmount.rectangle(plan, span - 0.29, span, -0.11, 0.12)]


def stair(parts, low, high, bottom, top, width, *, steps=16):
    a, b = np.asarray(low), np.asarray(high)
    forward = (b - a) / np.linalg.norm(b - a)
    side = np.array([-forward[1], forward[0]]) * width / 2
    stations = np.linspace(0, 1, steps + 1)
    for start, end in zip(stations, stations[1:]):
        first, last = a + (b - a) * start, a + (b - a) * end
        level = bottom + (top - bottom) * end
        tread = orient(Polygon([first - side, last - side, last + side, first + side]))
        base.flat(parts, tread, level - 0.092, level, (98, 113, 120), (145, 157, 157))
    for offset in (-side, side):
        beam(
            parts,
            (*(a + offset), bottom - 0.12),
            (*(b + offset), top - 0.12),
            0.133,
            STEEL,
        )
        beam(
            parts,
            (*(a + offset), bottom + 0.82),
            (*(b + offset), top + 0.82),
            0.046,
            STEEL,
        )
        for t in (0, 0.25, 0.5, 0.75, 1):
            p = a + (b - a) * t + offset
            z = bottom + (top - bottom) * t
            beam(parts, (*p, z), (*p, z + 0.82), 0.036, STEEL)


def mixed_use(parts, wall, shell, level, field, highest):
    gray, green, deck_color = (136, 154, 157), (113, 133, 73), (89, 117, 129)
    for a, b in edges(shell, minimum=2.6):
        span, add, normal, plan, _, _ = chapter.setup_face(parts, a, b)
        middle = plan(span / 2, 0)
        h = min(highest(a), highest(b))
        if h < level + 1.4:
            continue
        north = normal[1] > 0.95
        east = normal[0] > 0.95
        if north or east:
            add(
                0.035,
                span - 0.035,
                0.018,
                0.102,
                level - 0.12,
                level + 0.105,
                deck_color,
            )
            for t in np.linspace(0.12, 0.88, max(2, round(span / 2.85))):
                at = t * span
                high = min(highest(plan(at, 0)) - 0.32, level + 2.14)
                window_grid(
                    add, at, min(1.10, span * 0.35), level + 0.66, high, 2, 1, LIGHT
                )
        if north:
            y = geometry.sample_ground(field, *middle) + 0.13
            add(0.04, span - 0.04, 0.011, 0.062, y, level - 0.13, green)
            for t in (0.2, 0.5, 0.78):
                window_grid(
                    add,
                    t * span,
                    min(0.94, 0.16 * span),
                    y + 0.59,
                    min(level - 0.22, y + 1.77),
                    2,
                    2,
                    gray,
                )
        elif not east:
            for t in (0.24, 0.62, 0.86):
                window_grid(
                    add,
                    t * span,
                    0.94,
                    level + 0.51,
                    min(h - 0.36, level + 2.12),
                    2,
                    2,
                    LIGHT,
                )

    for a, b in edges(wall, [1, 0], minimum=4):
        span, add, _, plan, _, _ = chapter.setup_face(parts, a, b)
        mid = plan(span / 2, 0)
        if abs(mid[0] + 773) < 0.24:
            ground = geometry.sample_ground(field, *mid) + 0.07
            millrace.door(add, span * 0.50, ground, gray)
            for fraction in (0.24, 0.75):
                window_grid(
                    add, span * fraction, 1.18, ground + 0.81, ground + 1.93, 2, 2, gray
                )
    bay = box(-768.14, -146.00, -765.66, -137.42)
    base.flat(parts, bay, level - 0.28, level, deck_color, (134, 147, 148))
    fairmount.balustrade(parts, (-765.71, -146), (-765.71, -137.42), level, STEEL)
    fairmount.balustrade(parts, (-768.12, -137.42), (-765.71, -137.42), level, STEEL)
    stair(
        parts,
        [-765.92, -150.82],
        [-766.11, -145.65],
        geometry.sample_ground(field, -765.92, -150.82) + 0.045,
        level,
        1.16,
    )
    supports = []
    for e, n in [(-767.88, -145.90), (-767.83, -137.54), (-771.67, -137.72)]:
        footing = box(e - 0.098, n - 0.098, e + 0.098, n + 0.098)
        base.flat(
            parts,
            footing,
            geometry.sample_ground(field, e, n) - 0.07,
            level - 0.12,
            gray,
        )
        supports.append(footing)
    # The north street terrace and unbranded canopy preserve the observed form.
    patio = box(-805.33, -134.48, -798.75, -132.55)
    base.flat(parts, patio, level - 1.68, level - 1.44, (108, 101, 85), (146, 127, 97))
    base.flat(parts, patio, level + 0.49, level + 0.86, (139, 55, 48), (149, 62, 54))
    for e in [-805.14, -798.91]:
        beam(
            parts,
            (e, -132.73, level - 1.52),
            (e, -132.73, level + 0.49),
            0.084,
            (93, 73, 57),
        )
    return supports


def steam_plant(parts, row, wall, field, highest):
    trim, glass_trim = row["trim_color"], (167, 173, 164)
    for a, b in edges(wall, minimum=4):
        span, add, normal, plan, _, slab = chapter.setup_face(parts, a, b)
        step_count = max(1, round(span / 6.8))
        divisions = np.linspace(0.27, span - 0.27, step_count + 1)
        for u in divisions:
            peak = highest(plan(u, 0))
            add(u - 0.185, u + 0.185, 0.017, 0.193, -1.32, peak + 0.19, trim)
            add(u - 0.23, u + 0.23, 0.02, 0.232, peak + 0.12, peak + 0.32, trim)
        for i, (left, right) in enumerate(zip(divisions, divisions[1:])):
            mid = (left + right) / 2
            top = min(highest(plan(left + 0.04, 0)), highest(plan(right - 0.04, 0)))
            y = geometry.sample_ground(field, *plan(mid, 0))
            add(left, right, 0.014, 0.047, y + 0.51, 2.34, (154, 149, 132))
            add(left + 0.09, right - 0.09, 0.027, 0.147, top - 0.52, top - 0.29, trim)
            if span > 9 and (normal[0] > -0.78 or i % 2 == 0):
                panel_width = min(3.85, (right - left) * 0.68)
                window_grid(add, mid, panel_width, 4.14, top - 1.15, 7, 11, glass_trim)
                level = max(y + 0.6, 0.02)
                window_grid(add, mid, panel_width * 0.84, level, 2.03, 6, 3, glass_trim)
                if i % 3 == 0:
                    width = panel_width * 0.42
                    add(
                        mid - width,
                        mid + width,
                        0.122,
                        0.143,
                        level,
                        2.025,
                        (166, 162, 141),
                    )
                    add(
                        mid - 0.015,
                        mid + 0.015,
                        0.143,
                        0.153,
                        level,
                        2.025,
                        (139, 135, 119),
                    )
                add(
                    mid - panel_width * 0.62,
                    mid + panel_width * 0.62,
                    0.081,
                    0.18,
                    3.86,
                    4.16,
                    trim,
                )
                diamond = Polygon(
                    [
                        (mid - 0.16, top - 0.72),
                        (mid, top - 0.54),
                        (mid + 0.16, top - 0.72),
                        (mid, top - 0.90),
                    ]
                )
                slab(diamond, 0.019, 0.086, (106, 113, 105))
        if span > 45 and normal[0] > 0.35 and normal[1] > 0.35:
            u = span * 0.47
            ledge = fairmount.rectangle(plan, u - 2.15, u + 2.15, -0.03, 1.03)
            base.flat(parts, ledge, 1.93, 5.37, trim)
            add(u - 1.73, u + 1.73, 1.034, 1.071, 3.12, 4.44, GLASS)
            for x in np.linspace(u - 1.73, u + 1.73, 10):
                add(x - 0.018, x + 0.018, 1.074, 1.096, 3.12, 4.44, glass_trim)
            add(u - 1.73, u + 1.73, 1.074, 1.096, 3.76, 3.795, glass_trim)
    frame = row["roof_frame"]
    start = np.asarray(frame["origin_enu_m"])
    along = np.asarray(frame["axis"])
    along /= np.linalg.norm(along)
    across = np.array([-along[1], along[0]])
    for u, v, w, h in [
        (1, -1, 0.85, 0.51),
        (8, -7, 0.6, 0.47),
        (23, -4, 1.1, 0.76),
        (36, -10, 0.7, 0.62),
        (43, -11, 0.91, 0.49),
    ]:
        e, n = start + along * u + across * v
        fixture = box(e - w / 2, n - w / 2, e + w / 2, n + w / 2)
        if wall.covers(fixture):
            z = highest((e, n))
            base.flat(parts, fixture, z - 0.10, z + h, (139, 145, 141), (172, 173, 162))
    return []


def build(row, field, paving):
    outline = orient(Polygon(row["outline_enu_m"]))
    assert outline.is_valid
    shell = orient(outline.buffer(-0.135, join_style="mitre"))
    wall = shell
    if "open_bay_enu_m" in row:
        wall = orient(shell.difference(box(*row["open_bay_enu_m"])))
    floor, _ = garden.science.earlier.fit_base(field, wall)
    parts = []
    if row["architecture"] == "mixed":
        level = 3.83
        row = {
            **row,
            "raised_wall_enu_m": base.ring(shell),
            "raised_wall_bottom_z_m": level - 0.22,
        }
    highest = garden.roof_sections(parts, outline, wall, floor, row, grid=0.0002)
    gate, _, _, supports = fairmount.entrance(parts, row, wall, field, paving)
    model = row["architecture"]
    if model == "chapter":
        supports.extend(chapter_house(parts, row, wall, outline, floor, highest))
    elif model == "retail":
        supports.extend(retail(parts, row, wall, field, highest))
    elif model == "mixed":
        supports.extend(mixed_use(parts, wall, shell, level, field, highest))
    elif model == "steam":
        supports.extend(steam_plant(parts, row, wall, field, highest))
    else:
        raise ValueError(f"No exterior builder for {model} ({row['id']}).")
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{field: row[field] for field in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(wall)],
        "support_collision_enu_m": [base.ring(pier) for pier in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [gate] if gate else [],
    }
    return mesh, record, wall, supports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "northwest_infill_exterior_site", build
    )
