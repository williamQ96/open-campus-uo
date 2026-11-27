# SPDX-License-Identifier: Apache-2.0
"""Export registered exteriors along Garden Avenue, Franklin Boulevard and Millrace Drive."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.affinity import affine_transform
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

previous = import_module("build-villard-orchard-garden-review")
agate, columbia, emerald = previous.agate, previous.columbia, previous.emerald
base, fairmount, garden, geometry = (
    previous.base,
    previous.fairmount,
    previous.garden,
    previous.geometry,
)
PACKAGE = "garden-franklin-review"
PAVING = "garden-franklin-paving"
FRAME = (203, 199, 177)
GLASS = (76, 102, 110)
CONCRETE = (164, 158, 141)
DARK = (83, 89, 84)
BLUE = (74, 108, 130)
GREEN = (142, 151, 94)
GOLD = (188, 167, 89)
SLATE = (91, 108, 123)


def transforms(row):
    origin = np.asarray(row["roof_frame"]["origin_enu_m"], dtype=float)
    along = np.asarray(row["roof_frame"]["axis"], dtype=float)
    along /= np.linalg.norm(along)
    across = np.array([-along[1], along[0]])
    rotation = np.column_stack([along, across])
    coefficients = [*rotation.ravel(), *origin]

    def patch(bounds):
        return orient(affine_transform(box(*bounds), coefficients))

    def local(point):
        return (np.asarray(point) - origin) @ rotation

    def world(s, t):
        return tuple(origin + rotation @ [s, t])

    return patch, local, world


def slab(parts, field, area, top, color):
    low = min(geometry.sample_ground(field, *p) for p in area.exterior.coords) - 0.20
    if top > low:
        base.flat(parts, orient(area), low, top, color)


def posts(parts, field, positions, patch, world, height, color):
    footprints = []
    for s, t in positions:
        pier = patch((s - 0.12, t - 0.12, s + 0.12, t + 0.12))
        top = height(world(s, t))
        previous.support(parts, pier, field, top, color)
        footprints.append(pier)
    return footprints


def roof_equipment(parts, row, roof, height, patch):
    for x, y, w, d, h in row.get("equipment", []):
        bank = roof.buffer(-0.19).intersection(
            patch((x - w / 2, y - d / 2, x + w / 2, y + d / 2))
        )
        for piece in geometry.sections(bank):
            if piece.area < 0.18:
                continue
            samples = [height(p) for p in piece.exterior.coords]
            if max(samples) - min(samples) > 0.75:
                continue
            low, high = min(samples) - 0.04, max(samples) + h
            base.flat(parts, orient(piece), low, high, (160, 160, 144))
            cap = piece.buffer(-0.09)
            if cap.area > 0.1:
                base.flat(
                    parts, orient(cap), high - 0.02, high + 0.026, (126, 135, 126)
                )


def framed(add, u, width, bottom, top, columns, trim=FRAME):
    emerald.northwest.window_grid(add, u, width, bottom, top, columns, 1, trim)


def floor_windows(add, u, width, levels, floor, cap, trim=FRAME):
    for level in levels:
        bottom = level + 0.63
        top = min(bottom + 1.34, cap - 0.23)
        if bottom >= floor + 0.44 and top > bottom + 0.53:
            framed(add, u, width, bottom, top, 2, trim)


def balcony(add, start, end, z, trim):
    add(start, end, 0.026, 1.00, z - 0.17, z, trim)
    add(start, end, 0.89, 1.0, z + 0.94, z + 1.0, trim)
    add(start, end, 0.89, 1.0, z + 0.14, z + 0.20, trim)
    for u in np.linspace(
        start + 0.032, end - 0.032, max(2, round((end - start) / 0.24) + 1)
    ):
        add(u - 0.018, u + 0.018, 0.90, 0.97, z + 0.17, z + 0.95, trim)


def facade_segments(parts, points):
    for a, b in zip(points, points[1:]):
        if np.linalg.norm(np.asarray(b) - a) > 0.08:
            yield garden.chapter.setup_face(parts, a, b)


def apartment_elevation(add, span, layout, row, local, plan, field, height):
    count = max(1, round(span / 3.82))
    range_width = span / count
    for i in range(count):
        left, right = i * range_width, (i + 1) * range_width
        if right - left < 0.65:
            continue
        u = (left + right) / 2
        p = plan(u, 0)
        s, t = local(p)
        ground = emerald.grade(field, p)
        top = min(height(plan(k, 0)) for k in (left + 0.055, u, right - 0.055)) - 0.15
        if layout == "garage":
            add(left + 0.015, right - 0.015, 0.006, 0.055, ground - 0.08, top, CONCRETE)
            for z in (4.36, 7.27, 10.19, 13.1, 16.02, 18.93):
                lo, hi = max(z + 0.52, ground + 0.30), min(z + 2.32, top - 0.22)
                if hi > lo + 0.38:
                    add(left + 0.17, right - 0.17, 0.059, 0.087, lo, hi, DARK)
                    add(
                        left + 0.19,
                        right - 0.19,
                        0.086,
                        0.109,
                        lo + 0.13,
                        lo + 0.23,
                        FRAME,
                    )
            add(
                left + 0.04,
                left + 0.17,
                0.050,
                0.17,
                ground - 0.06,
                top,
                (183, 179, 159),
            )
            continue
        group = int(
            (s if abs(plan(span, 0)[0] - plan(0, 0)[0]) > span * 0.55 else -t) / 4.0
        )
        panel = (SLATE, (166, 161, 137), (192, 190, 171), (164, 166, 149))[group % 4]
        if top > ground + 0.68:
            add(left + 0.023, right - 0.023, 0.004, 0.042, ground + 0.22, top, panel)
        levels = row["levels_z_m"] if top > 21.5 else [4.12, 7.32, 10.39, 13.47, 16.55]
        frontage = layout == "street"
        if frontage:
            lo, hi = max(ground + 0.30, 5.84), min(8.32, top - 0.34)
            if hi > lo + 0.7:
                framed(add, u, (right - left) * 0.94, lo, hi, 3, (175, 179, 154))
        for z in levels:
            lo, hi = z + 0.48, min(z + 1.97, top - 0.3)
            if hi < lo + 0.62 or lo < ground + 0.38 or frontage and z < 6:
                continue
            width = min(1.72, (right - left) * 0.63)
            framed(add, u, width, lo, hi, 2, (199, 198, 174))
            if (
                group % 5 == 2
                and range_width > 2.48
                and z + 1.25 < top
                and z - ground > 3.5
            ):
                balcony(
                    add,
                    u - 1.09,
                    u + 1.09,
                    z + 0.20,
                    GREEN if frontage else (136, 142, 125),
                )
    if layout == "street":
        add(0.09, span - 0.09, 0.01, 0.94, 8.38, 8.79, GREEN)


def treatment(parts, row, wall, field, height, local):
    kind = row.get("treatment")
    for poly in geometry.sections(wall):
        poly = orient(poly)
        rings = (
            [poly.exterior, *poly.interiors]
            if kind == "apartments"
            else [poly.exterior]
        )
        for ring in rings:
            for span, add, _, plan, _, _ in facade_segments(parts, list(ring.coords)):
                if span < 0.72:
                    continue
                mid = plan(span / 2, 0)
                floor = emerald.grade(field, mid)
                top = min(height(plan(u, 0)) for u in np.linspace(0.06, span - 0.06, 7))
                s, t = local(mid)
                direction = local(plan(span / 2, 1)) - local(mid)
                south = direction[1] < -0.8
                if kind == "apartments":
                    garage = s > 141.9 and -72.6 < t < -20.65
                    street = south and (t < -79 or -67 < t < -64)
                    apartment_elevation(
                        add,
                        span,
                        "garage" if garage else "street" if street else "residential",
                        row,
                        local,
                        plan,
                        field,
                        height,
                    )
                elif kind == "hotel":
                    add(
                        0.015,
                        span - 0.015,
                        0.006,
                        0.060,
                        floor - 0.06,
                        min(top - 0.22, 9.44),
                        (151, 114, 93),
                    )
                    for z in (9.40, 19.47):
                        if top - z > 0.19:
                            add(0.018, span - 0.018, 0.013, 0.11, z, z + 0.16, FRAME)
                    count = max(1, round(span / 3.28))
                    for i in range(count):
                        u = (i + 0.5) * span / count
                        left, right = u - span / count * 0.24, u + span / count * 0.24
                        if right - left > 1.0 and top > 10.5:
                            add(
                                left,
                                right,
                                0.055,
                                0.085,
                                9.25,
                                top - 0.19,
                                (158, 130, 107) if i % 3 != 1 else (153, 150, 132),
                            )
                        floor_windows(
                            add,
                            u,
                            min(1.45, span / count * 0.70),
                            row["levels_z_m"],
                            floor,
                            top,
                        )
                elif kind == "motel":
                    add(0.015, span - 0.015, 0.005, 0.095, top - 0.80, top - 0.14, BLUE)
                    if span > 2.25:
                        count = max(1, round(span / 3.30))
                        for u in (np.arange(count) + 0.5) * span / count:
                            floor_windows(
                                add,
                                u,
                                min(1.67, span / count * 0.62),
                                row["levels_z_m"],
                                floor,
                                top,
                            )
                    if (
                        span > 9
                        and (direction[0] > 0.8 or direction[0] < -0.8)
                        and top > 8.55
                    ):
                        balcony(
                            add,
                            0.11,
                            span - 0.11,
                            5.51 if row["city_objectid"] == 170547 else 6.15,
                            (100, 107, 99),
                        )
                elif kind == "retail" and south and t < 0.6:
                    for u in np.arange(1.76, span - 0.97, 2.77):
                        framed(add, u, 2.47, 6.90, 9.54, 3, (101, 109, 98))
                    add(0.08, span - 0.08, 0.01, 0.50, 9.55, 9.92, FRAME)
                    add(
                        span * 0.27,
                        span * 0.73,
                        0.027,
                        0.09,
                        9.96,
                        10.69,
                        (187, 188, 172),
                    )
                elif kind == "auto" and south and t < 0.7:
                    add(0.01, span - 0.01, 0.015, 0.07, floor - 0.03, top - 0.18, GOLD)
                    add(0.01, span - 0.01, 0.075, 0.13, 9.12, top - 0.18, (69, 87, 92))
                    for u in np.arange(0.18, span - 0.10, 0.24):
                        add(
                            u - 0.012,
                            u + 0.012,
                            0.128,
                            0.149,
                            9.15,
                            top - 0.18,
                            (77, 95, 98),
                        )
                    if span > 2.49:
                        u = span / 2
                        width = min(3.66, span * 0.70)
                        add(
                            u - width / 2,
                            u + width / 2,
                            0.08,
                            0.103,
                            floor - 0.04,
                            9.15,
                            (168, 174, 161),
                        )

                        def forward(a, b, c, d, e, f, color):
                            add(a, b, c + 0.102, d + 0.102, e, f, color)

                        framed(
                            forward,
                            u,
                            width - 0.23,
                            floor + 1.03,
                            min(8.84, top - 0.55),
                            3,
                            (175, 180, 168),
                        )
                elif kind in ("low-rise", "retail", "auto") and span > 2.15:
                    count = max(1, round(span / 4.0))
                    for u in (np.arange(count) + 0.5) * span / count:
                        floor_windows(
                            add,
                            u,
                            min(1.95, span / count * 0.63),
                            row["levels_z_m"],
                            floor,
                            top,
                        )


def gable_elevation(parts, row, world):
    left, crest, right, front, low, high = row["gable_elevation"]
    width, add, _, _, point, panel = garden.chapter.setup_face(
        parts, world(left, front), world(right, front)
    )
    offset = crest - left
    shape = orient(Polygon(((0, low), (width, low), (offset, high))))
    panel(shape, 0.019, 0.116, (192, 192, 172))
    for a, b in (
        (point(0, 0.137, low), point(offset, 0.137, high)),
        (point(offset, 0.137, high), point(width, 0.137, low)),
    ):
        fairmount.beam(parts, a, b, 0.092, row["trim_color"])
    if high - low > 3:

        def forward(a, b, c, d, e, f, color):
            add(a, b, c + 0.118, d + 0.118, e, f, color)

        framed(forward, offset, 1.55, low + 1.10, low + 2.13, 2)
    else:
        add(0.15, width - 0.15, 0.121, 0.152, low + 0.01, low + 0.13, row["trim_color"])


def courtyard(parts, row, roof, field, patch, height):
    hole = orient(Polygon(roof.interiors[0]))
    court = row["court"]
    deck = hole.buffer(-0.034)
    lower = deck.intersection(patch((-10, -58, 80, court["divide"])))
    upper = deck.difference(lower)
    pool = upper.intersection(patch(court["pool"])).buffer(-0.08)
    for sections, level in (
        (lower, court["lower_level"]),
        (upper.difference(pool), court["level"]),
    ):
        for piece in geometry.sections(sections):
            slab(parts, field, piece, level, (159, 158, 139))
    base.flat(
        parts,
        orient(pool),
        court["level"] - 0.38,
        court["level"] - 0.115,
        (74, 129, 138),
    )
    kerb = pool.buffer(0.19).difference(pool)
    base.flat(
        parts,
        orient(kerb),
        court["level"] - 0.08,
        court["level"] + 0.14,
        (196, 190, 165),
    )
    for left in (21.2, 39.54):
        area = upper.intersection(
            patch((left, -34.51, left + 1.69, -26.75))
        ).difference(pool)
        for piece in geometry.sections(area):
            base.flat(
                parts,
                orient(piece),
                court["level"] - 0.02,
                court["level"] + 0.22,
                (121, 139, 92),
            )
    for s in np.arange(145.7, 181.4, 2.61):
        for t in (-22.9, -58.7):
            stripe = roof.buffer(-0.29).intersection(
                patch((s, t - 2.14, s + 0.084, t + 2.14))
            )
            for piece in geometry.sections(stripe):
                if piece.area < 0.06:
                    continue
                align = tuple(piece.representative_point().coords)[0]
                z = height(align)
                if 17.5 < z < 20.05:
                    base.flat(
                        parts, orient(piece), z - 0.009, z + 0.013, (197, 191, 168)
                    )


def patio(parts, row, patch):
    patio = row["patio"]
    _, south, _, _ = patio["bounds"]
    level = patio["z"]
    # The dated street view separates the retaining wall from the open seating.
    for x in (-8.35, -4.92, -1.43, 2.28, 5.51, 8.72):
        for t in (south + 1.76, south + 4.12):
            base.flat(
                parts,
                patch((x - 0.55, t - 0.12, x - 0.39, t + 0.12)),
                level - 0.01,
                level + 0.69,
                (110, 90, 69),
            )
            base.flat(
                parts,
                patch((x + 0.39, t - 0.12, x + 0.55, t + 0.12)),
                level - 0.01,
                level + 0.69,
                (110, 90, 69),
            )
            base.flat(
                parts,
                patch((x - 0.72, t - 0.42, x + 0.72, t + 0.42)),
                level + 0.65,
                level + 0.77,
                (150, 106, 73),
            )
            for offset in (-0.79, 0.79):
                base.flat(
                    parts,
                    patch((x - 0.70, t + offset - 0.12, x + 0.70, t + offset + 0.12)),
                    level + 0.35,
                    level + 0.47,
                    (145, 106, 73),
                )


def residence_details(parts, paving, row, wall, field, height):
    supports, gates = emerald.facades(parts, paving, row, wall, field, height)
    hill = previous.hill.hill
    if "gallery" in row:
        spec = row["gallery"]
        _, span, add, _, plan, _ = hill.at_face(parts, wall, row, spec)
        balcony(add, 0.37, span - 0.36, spec["z"], row["trim_color"])
        for along in (0.54, span - 0.54):
            x, y = plan(along, 0.83)
            post = box(x - 0.053, y - 0.053, x + 0.053, y + 0.053)
            top = spec["z"] - 0.16
            previous.support(parts, post, field, top, row["trim_color"])
            supports.append(post)
    for front in row["frontages"]:
        if not front.get("garages"):
            continue
        _, _, add, _, plan, station = hill.at_face(parts, wall, row, front)
        for offset, width in front["garages"]:
            left, right = station + offset - width / 2, station + offset + width / 2
            z = emerald.grade(field, plan(station + offset, 0))
            head = min(z + 2.36, min(height(plan(s, 0)) for s in (left, right)) - 0.27)
            add(
                left - 0.048,
                right + 0.048,
                0.008,
                0.061,
                z - 0.075,
                head + 0.059,
                FRAME,
            )
            add(left, right, 0.063, 0.088, z - 0.066, head, front["garage_color"])
            for level in np.arange(z + 0.24, head - 0.24, 0.32):
                add(left, right, 0.088, 0.102, level, level + 0.027, (161, 169, 159))
            for at in np.linspace(left + 0.34, right - 0.34, 4):
                add(
                    at - 0.153,
                    at + 0.153,
                    0.089,
                    0.112,
                    head - 0.43,
                    head - 0.19,
                    GLASS,
                )
    return supports, gates


def build(row, field, paving):
    patch, local, world = transforms(row)
    roof = orient(
        set_precision(
            Polygon(row["outline_enu_m"], row["courtyard_rings_enu_m"]), 0.002
        )
    )
    wall = roof.buffer(-row["eaves_m"], join_style="mitre")
    clearance = row.get("clearance", {})
    if clearance:
        wall = wall.difference(
            unary_union([patch(bounds) for bounds in clearance["cuts"]])
        )
    occupied = [orient(p) for p in geometry.sections(wall) if p.area > 0.05]
    wall = unary_union(occupied)
    parts = []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    supports = posts(
        parts,
        field,
        clearance.get("posts", []),
        patch,
        world,
        lambda point: height(point) - 0.14,
        row["trim_color"],
    )
    for limits in clearance.get("screen", []):
        panel = patch(limits)
        slab(parts, field, panel, clearance["screen_top"], row["wall_color"])
        supports.append(panel)
    for limits, z, underside, positions in row.get("exterior_canopies", []):
        base.flat(parts, patch(limits), underside, z, row["trim_color"])
        supports.extend(
            posts(
                parts,
                field,
                positions,
                patch,
                world,
                lambda _: underside,
                (146, 129, 112),
            )
        )
    for west, south, east, north, z, color in row.get("terraces", []):
        slab(paving, field, patch((west, south, east, north)), z, color)
    if "patio" in row:
        patio(parts, row, patch)
    if "gable_elevation" in row:
        gable_elevation(parts, row, world)
    gates = []
    if row.get("treatment"):
        treatment(parts, row, wall, field, height, local)
    else:
        for piece in occupied:
            selected = [
                f for f in row["frontages"] if piece.distance(Point(f["near"])) < 0.75
            ]
            attributes = {**row, "frontages": selected}
            if (
                "gallery" in row
                and piece.distance(Point(row["gallery"]["near"])) > 0.75
            ):
                attributes.pop("gallery")
            piers, exits = residence_details(
                parts, paving, attributes, piece, field, height
            )
            supports.extend(piers)
            gates.extend(exits)
    if "court" in row:
        courtyard(parts, row, roof, field, patch, height)
    roof_equipment(parts, row, roof, height, patch)
    mesh, record, _, _ = agate.output(parts, row, roof, occupied[0], supports, gates)
    record["ground_footprints_enu_m"] = [
        base.ring(orient(section))
        for footprint in occupied
        for section in agate.prune_rings(footprint)
    ]
    return mesh, record, wall, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, PAVING, "garden_franklin_site", build
    )


if __name__ == "__main__":
    main()
