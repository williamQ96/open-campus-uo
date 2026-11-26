# SPDX-License-Identifier: Apache-2.0
"""Export five registered buildings around the Lillis Business Complex."""

import argparse
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-oregon-jaqua-site-review.py")
loader = spec_from_file_location(source.stem, source)
nearby = module_from_spec(loader)
loader.loader.exec_module(nearby)
geometry, tools, site = nearby.geometry, nearby.tools, nearby.site
heritage = tools.load_builder("build-heritage-core-site-review.py")
frohnmayer = tools.load_builder("build-frohnmayer-exterior-review.py")
planting = tools.load_builder("build-cedar-yasui-site-review.py")
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/lillis-complex-site-review.json"
DIRECTORY = "lillis-complex-review"
GROUND = "lillis-complex-courtyards"
BRICK = (159, 92, 72)
HISTORIC = (148, 81, 66)
CHILES = (145, 101, 79)
COMPUTING = (148, 82, 65)
DARK_BRICK = (116, 65, 57)
TERRA_COTTA = (192, 169, 139)
STONE = (207, 197, 174)
CONCRETE = (159, 153, 141)
PAVING = (181, 170, 152)
MEMBRANE = (208, 206, 190)
DARK_ROOF = (123, 123, 117)
GLASS = (70, 105, 111)
LIT_GLASS = (105, 140, 146)
PV = (63, 75, 101)
PV_ALT = (75, 87, 110)
STEEL = (144, 154, 149)
SLATE = (118, 127, 123)
IRON = (67, 70, 62)
GRASS = (136, 149, 105)
SOIL = (120, 114, 89)

flat, union, ring = nearby.flat, nearby.union, nearby.ring


def face_edges(plan):
    points = ring(plan)
    return zip(points, points[1:] + points[:1])


def frontage(parts, a, b, point):
    length, add = tools.face(parts, a, b)
    along = (np.asarray(b) - a) / length
    return length, add, np.dot(np.asarray(point) - a, along)


def aligned_gate(a, b, gates):
    edge = LineString([a, b])
    return next(
        (
            gate
            for gate in gates
            if edge.distance(Point(gate["position_enu_m"])) < 0.025
        ),
        None,
    )


def rectangular_window(add, u, width, low, top, sash, historic=False):
    a, b = u - width * 0.5, u + width * 0.5
    if b - a < 0.2 or top - low < 0.2:
        return
    add(a - 0.053, b + 0.053, -0.024, 0.035, low - 0.08, top + 0.048, IRON)
    add(a, b, 0.034, 0.048, low, top, GLASS)
    for x in np.linspace(a, b, 4 if historic else 3):
        add(x - 0.019, x + 0.019, 0.045, 0.086, low, top, sash)
    fractions = (0.18, 0.33, 0.49, 0.66, 0.83) if historic else (0.52,)
    for f in fractions:
        z = low + (top - low) * f
        add(a, b, 0.048, 0.083, z - 0.019, z + 0.019, sash)
    add(a - 0.085, b + 0.085, 0.016, 0.119, low - 0.102, low - 0.045, TERRA_COTTA)


def roof_equipment(parts, spec, plan, cap, wall=STEEL):
    for a, b, c, d, z in spec["equipment"]:
        footprint = box(a, b, c, d).intersection(plan.buffer(-0.3))
        flat(parts, footprint, cap, z - 0.06, wall, MEMBRANE)
        flat(parts, footprint.buffer(0.045), z - 0.06, z, STEEL, MEMBRANE)
        if footprint.area > 12:
            width, face = tools.face(parts, (a, b), (c, b))
            for h in np.linspace(cap + 0.20, z - 0.13, 6):
                face(0.12, width - 0.12, 0.011, 0.049, h, h + 0.042, IRON)


def site_entry(parts, field, entry):
    if entry["rise_m"] < 0.26:
        gate, path = site.approach(parts, field, entry)
        return gate, path, []
    e, n = entry["position_enu_m"]
    angle = np.deg2rad(entry["outward_degrees"])
    outward = np.array([np.sin(angle), np.cos(angle)])
    along = np.array([outward[1], -outward[0]])
    origin = np.array([e, n])
    run = 3.72 if entry["rise_m"] > 1 else 2.34
    width = 3.47 if entry["rise_m"] > 1 else 2.2
    datum = geometry.sample_ground(field, *(origin + outward * run))
    threshold = datum + entry["rise_m"]

    def rectangle(start, end, left, right):
        return Polygon(
            [
                origin + outward * t + along * u
                for t, u in ((start, left), (end, left), (end, right), (start, right))
            ]
        )

    steps = max(3, round(entry["rise_m"] / 0.158))
    for i in range(steps):
        end = run - i * (run - 0.83) / (steps - 1)
        slab = rectangle(-0.025, end, -width * 0.50, width * 0.50)
        flat(
            parts,
            slab,
            datum - 0.63,
            datum + (i + 1) * entry["rise_m"] / steps,
            HISTORIC,
            CONCRETE,
        )
    blocks = []
    for side in (-1, 1):
        cheek = width * 0.5 * side
        wall = rectangle(0.03, run - 0.22, cheek - 0.13, cheek + 0.13)

        def wall_height(x, y):
            distance = np.dot(np.array([x, y]) - origin, outward)
            f = np.clip((distance - 0.75) / (run - 0.8), 0, 1)
            return threshold + 0.34 - f * entry["rise_m"]

        site.surface(parts, wall, datum - 0.58, wall_height, BRICK, STONE)
        blocks.append(wall)
        p = origin + outward * 0.75 + along * (cheek - side * 0.21)
        q = origin + outward * (run - 0.11) + along * (cheek - side * 0.21)
        tools.beam(parts, (*p, threshold + 0.73), (*q, datum + 0.76), 0.048, IRON)
        for f in (0, 0.5, 1):
            pos = (1 - f) * p + f * q
            z = (1 - f) * threshold + f * datum
            tools.beam(parts, (*pos, z + 0.08), (*pos, z + 0.74), 0.044, IRON)
    patch = rectangle(
        run - 0.075, entry["approach_distance_m"] + 1, -width * 0.59, width * 0.59
    )
    return entry | {"threshold_z_m": round(threshold, 3)}, patch, blocks


def historic_portal(parts, a, b, u, add, gate, roof):
    threshold = gate["threshold_z_m"]
    for offset in (-1.83, 1.83):
        x = u + offset
        add(
            x - 0.22,
            x + 0.22,
            -0.045,
            0.28,
            threshold - 0.10,
            threshold + 2.93,
            TERRA_COTTA,
        )
        for height in (0.02, 0.56, 2.68, 2.94):
            add(
                x - 0.29,
                x + 0.29,
                0.034,
                0.39,
                threshold + height,
                threshold + height + 0.13,
                STONE,
            )
    heritage.arched(
        parts, a, b, u, 2.45, threshold, threshold + 4.05, STONE, TERRA_COTTA, True
    )
    for i, offset in enumerate((-1.04, 0, 1.04)):
        highest = min(roof - 0.67, threshold + (7.71 if i == 1 else 7.39))
        heritage.arched(
            parts, a, b, u + offset, 0.66, threshold + 4.48, highest, TERRA_COTTA, BRICK
        )
    add(u - 1.55, u + 1.55, 0.03, 0.20, threshold + 4.31, threshold + 4.44, STONE)
    add(u - 2.13, u + 2.13, 0.018, 0.20, roof - 0.56, roof - 0.35, TERRA_COTTA)
    for x in np.linspace(u - 1.93, u + 1.93, 12):
        add(
            x - 0.045,
            x + 0.045,
            0.026,
            0.115,
            threshold + 7.76,
            roof - 0.56,
            TERRA_COTTA,
        )


def historic(parts, plan, other, model, gates, base, datum):
    roof, cap = model["roof_z_m"], model["parapet_z_m"]
    raised = plan.intersection(box(*model["raised_wing_bounds"]))
    flat(parts, plan, base, roof, HISTORIC, MEMBRANE)
    flat(parts, raised, roof - 0.025, cap - 0.08, HISTORIC, MEMBRANE)
    nearby.parapet(parts, plan, roof, cap, HISTORIC, STONE, 0.38)
    south_rim = plan.intersection(
        box(plan.bounds[0], plan.bounds[1], plan.bounds[2], plan.bounds[1] + 1.25)
    )
    flat(parts, south_rim, roof, cap - 0.035, HISTORIC, MEMBRANE)
    roof_equipment(parts, model, plan, roof)
    for a, b in face_edges(plan):
        length, add = tools.face(parts, a, b)
        if length < 0.6 or other.buffer(0.065).covers(
            LineString([a, b]).interpolate(0.5, normalized=True)
        ):
            continue
        for z in (datum + 1.22, datum + 1.49, roof - 0.06, roof + 0.36):
            add(0, length, -0.019, 0.118, z, z + 0.107, TERRA_COTTA)
        gate = aligned_gate(a, b, gates)
        formal = gate is not None and gate["gate"].endswith("-court")
        u = frontage(parts, a, b, gate["position_enu_m"])[2] if gate else -10
        for offset in np.linspace(0.39, length - 0.39, max(2, round(length / 4) + 1)):
            if formal and abs(offset - u) < 2.18:
                continue
            add(
                offset - 0.106,
                offset + 0.106,
                0,
                0.089,
                datum + 1.25,
                roof + 0.34,
                BRICK,
            )
        if length > 1.9:
            count = max(1, round(length / 2.75))
            for x in np.linspace(
                length / (count * 2), length - length / (count * 2), count
            ):
                if gate and abs(x - u) < (2.32 if formal else 1.45):
                    continue
                width = min(1.02, length / (count + 1))
                rectangular_window(
                    add, x, width, datum + 0.25, datum + 1.08, TERRA_COTTA, True
                )
                for low, high in (
                    (datum + 2.12, datum + 5.10),
                    (datum + 6.1, datum + 9.11),
                ):
                    rectangular_window(
                        add, x, width, low, min(roof - 0.52, high), TERRA_COTTA, True
                    )
                for dx in (-0.27, 0, 0.27):
                    loc = x + dx
                    if 0.12 < loc < length - 0.12:
                        z = roof - 0.45
                        relief = Polygon(
                            [
                                (loc - 0.11, z),
                                (loc, z - 0.08),
                                (loc + 0.11, z),
                                (loc, z + 0.08),
                            ]
                        )
                        heritage.profile(parts, a, b, relief, 0.091, TERRA_COTTA)
        if formal:
            historic_portal(parts, a, b, u, add, gate, roof)
        elif gate:
            site.allen.doors(add, u, gate["width_m"], gate["threshold_z_m"])


def chiles(parts, plan, other, model, gates, base, datum):
    roof, cap = model["roof_z_m"], model["parapet_z_m"]
    flat(parts, plan, base, roof, CHILES, MEMBRANE)
    nearby.parapet(parts, plan, roof, cap, CHILES, STEEL, 0.29)
    roof_equipment(parts, model, plan, roof)
    for a, b in face_edges(plan):
        length, add = tools.face(parts, a, b)
        if length < 0.7 or other.buffer(0.065).covers(
            LineString([a, b]).interpolate(0.5, normalized=True)
        ):
            continue
        gate = aligned_gate(a, b, gates)
        for z in (datum + 3.02, datum + 6.71, datum + 10.51, roof + 0.35):
            add(
                0,
                length,
                -0.011,
                0.075,
                z,
                z + 0.069,
                TERRA_COTTA if gate else DARK_BRICK,
            )
        if gate:
            u = frontage(parts, a, b, gate["position_enu_m"])[2]
            threshold = gate["threshold_z_m"]
            width = min(4.69, length - 0.66)
            heritage.arched(
                parts,
                a,
                b,
                u,
                width,
                threshold + 3.94,
                roof - 0.72,
                TERRA_COTTA,
                DARK_BRICK,
            )
            for x in np.linspace(u - width * 0.42, u + width * 0.42, 5):
                top = roof - 1.3 - abs(x - u) * 0.38
                add(x - 0.034, x + 0.034, 0.087, 0.138, threshold + 3.99, top, STEEL)
            for z in np.linspace(threshold + 5.0, roof - 2.38, 4):
                add(
                    u - width * 0.49, u + width * 0.49, 0.087, 0.14, z, z + 0.055, STEEL
                )
            add(
                u - 2.46,
                u + 2.46,
                -0.02,
                0.34,
                threshold + 2.46,
                threshold + 2.73,
                TERRA_COTTA,
            )
            site.allen.doors(add, u, gate["width_m"], threshold)
        elif length > 2.2:
            count = max(1, round(length / 3.7))
            short = abs(b[1] - a[1]) < 0.18
            for j in range(count):
                x = (j + 0.5) * length / count
                for i in range(3):
                    if short and i != 2 and j not in (0, count - 1):
                        continue
                    bottom = datum + 1.38 + i * 4.06
                    rectangular_window(
                        add,
                        x,
                        min(0.94, length * 0.42),
                        bottom,
                        min(bottom + 1.68, roof - 0.34),
                        IRON,
                    )


def computing(parts, plan, ground, model, gates, base, datum):
    roof, cap = model["roof_z_m"], model["parapet_z_m"]
    flat(parts, ground, base, roof, COMPUTING, DARK_ROOF)
    recess = plan.difference(ground)
    flat(parts, recess, datum + 4.68, roof, COMPUTING, DARK_ROOF)
    nearby.parapet(parts, plan, roof, cap, COMPUTING, CONCRETE, 0.25)
    roof_equipment(parts, model, plan, roof)
    for a, b in face_edges(ground):
        length, add = tools.face(parts, a, b)
        if length < 0.75:
            continue
        gate = aligned_gate(a, b, gates)
        add(0, length, -0.019, 0.088, roof - 1.32, roof + 0.04, CONCRETE)
        for x in np.linspace(
            length * 0.14, length * 0.87, max(1, round(length / 3.55))
        ):
            if gate and length > 2:
                u = frontage(parts, a, b, gate["position_enu_m"])[2]
                if abs(x - u) < gate["width_m"] * 0.64:
                    continue
            width = min(1.24, length * 0.38)
            if width < 0.25:
                continue
            add(
                x - width * 0.54,
                x + width * 0.54,
                0.004,
                0.023,
                datum + 0.83,
                roof - 1.28,
                CONCRETE,
            )
            rectangular_window(add, x, width, datum + 1.0, datum + 3.36, IRON)
            rectangular_window(add, x, width, datum + 4.64, roof - 1.34, IRON)
        if gate:
            u = frontage(parts, a, b, gate["position_enu_m"])[2]
            z = gate["threshold_z_m"]
            add(
                u - gate["width_m"] * 0.62,
                u + gate["width_m"] * 0.62,
                -0.036,
                0.06,
                z + 0.11,
                datum + 4.68,
                IRON,
            )
            rectangular_window(
                add, u, gate["width_m"] * 1.13, z + 2.55, datum + 4.49, STEEL
            )
            site.allen.doors(add, u, gate["width_m"], z)
    for a, b in face_edges(plan):
        if LineString([a, b]).intersects(recess) and max(a[1], b[1]) > 107:
            length, add = tools.face(parts, a, b)
            if length > 2:
                add(0, length, -0.02, 0.11, roof - 1.34, roof + 0.04, CONCRETE)


def solar_nodes(parts, area, bottom, top):
    a, b, c, d = area.bounds
    if c - a < 0.41 or d - b < 0.35:
        return
    flat(parts, area, bottom, top, STEEL, CONCRETE)
    for i in range(12):
        x = a + 0.12 + i * (c - a - 0.24) / 12
        roof = box(x, b + 0.1, x + (c - a - 0.26) / 12 - 0.036, d - 0.1).intersection(
            area
        )
        flat(parts, roof, top, top + 0.045, PV, PV if i % 3 else PV_ALT)


def lillis_roofs(parts, plan, ground, model, base, datum):
    atrium_left, atrium_right = model["atrium_east_range"]
    atrium = plan.intersection(box(atrium_left, 10, atrium_right, 110))
    xmid = (atrium_left + atrium_right) * 0.5

    def vault(x, n):
        return 21.75 - 0.0106 * (x - xmid) ** 2

    residual = plan.difference(atrium)
    zones = []
    for label, bounds, roof, cap in model["zones"]:
        area = residual.intersection(box(*bounds))
        if area.area > 0.10:
            zones.append((area, roof, label))
            flat(parts, area, base, roof, BRICK, MEMBRANE if roof > 13 else DARK_ROOF)
            nearby.parapet(parts, area, roof, cap, TERRA_COTTA, CONCRETE, 0.24)
        residual = residual.difference(area)
    roof, cap = model["default_roof"]
    zones.append((residual, roof, "main"))
    flat(parts, residual, base, roof, BRICK, MEMBRANE)
    nearby.parapet(parts, residual, roof, cap, TERRA_COTTA, CONCRETE, 0.26)
    for a, b, c, d, z in model["raised_roof"]:
        area = box(a, b, c, d).intersection(residual.buffer(-0.15))
        flat(parts, area, roof, z - 0.16, STEEL, DARK_ROOF)
        solar_nodes(parts, area.buffer(-0.11, join_style="mitre"), z - 0.16, z)
    cylinder = Point(xmid - 0.16, 69.6).buffer(10.0, quad_segs=14)
    barrel = atrium.intersection(
        cylinder.union(box(atrium_left, 10, atrium_right, 65.8))
    )
    terrace = atrium.difference(barrel)
    flat(parts, terrace.intersection(ground), base, 17.9, BRICK, DARK_ROOF)
    flat(parts, terrace.difference(ground), datum + 4.15, 17.9, BRICK, DARK_ROOF)
    nearby.parapet(parts, terrace, 17.9, 18.22, TERRA_COTTA, CONCRETE)
    for u, v in zip(
        np.linspace(atrium_left, atrium_right, 19)[:-1],
        np.linspace(atrium_left, atrium_right, 19)[1:],
    ):
        piece = barrel.intersection(box(u, 10, v, 84))
        core = piece.intersection(ground)
        site.surface(
            parts, core, base, lambda x, n: vault(x, n) - 0.22, GLASS, MEMBRANE
        )
        shell = piece.difference(core)
        site.surface(
            parts, shell, datum + 4.15, lambda x, n: vault(x, n) - 0.22, STEEL, MEMBRANE
        )
        nearby.shared.roof_layer(parts, piece, vault, 0.27, 0.028, STEEL, MEMBRANE)
    for a, b, c, d in model["atrium_roof_solar"]:
        area = box(a, b, c, d).intersection(barrel.buffer(-0.35))
        solar_nodes(parts, area, 21.55, 23.18)
    for y in (49.1, 52.77, 56.52, 59.99):
        for x in (xmid - 7.34, xmid + 7.24):
            point = Point(x, y).buffer(0.58, quad_segs=9).intersection(barrel)
            height = vault(x, y)
            flat(parts, point, height - 0.08, height + 0.48, STEEL, (162, 185, 182))
    crown = Point(xmid, 70.5).buffer(1.72, quad_segs=12).intersection(barrel)
    flat(parts, crown, 21.62, 22.16, STEEL, (143, 167, 164))
    return atrium, zones, vault


def solar_wall(parts, a, b, left, right, base, roofline, gate):
    length, add = tools.face(parts, a, b)
    if right - left < 1.15:
        return
    rails = np.linspace(left, right, max(3, round((right - left) / 1.68) + 1))
    for u in rails:
        add(
            max(0, u - 0.048),
            min(length, u + 0.048),
            -0.032,
            0.131,
            base,
            roofline(u),
            STEEL,
        )
    for l, r in zip(rails[:-1], rails[1:]):
        for z in np.arange(base + 2.5, min(roofline(l), roofline(r)) - 0.12, 0.91):
            add(l, r, 0.018, 0.100, z, z + 0.051, STEEL)
    for i, u in enumerate(np.arange(left + 0.37, right - 0.28, 0.77)):
        for group in (3.3, 6.97, 10.63, 14.29, 17.35):
            for j in range(3):
                z = base + group + j * 0.385
                if z + 0.325 < min(roofline(u), roofline(u + 0.59)) - 0.26:
                    add(
                        u,
                        u + 0.59,
                        0.078,
                        0.121,
                        z,
                        z + 0.325,
                        PV if (i + j) % 5 else PV_ALT,
                    )
    if gate:
        u = frontage(parts, a, b, gate["position_enu_m"])[2]
        w = gate["width_m"] * 0.50
        threshold = gate["threshold_z_m"]
        add(
            u - w - 0.32,
            u + w + 0.32,
            -0.025,
            0.52,
            threshold + 2.54,
            threshold + 2.86,
            STONE,
        )
        for sign in (-1, 1):
            o = u + sign * (w + 0.19)
            add(
                o - 0.138,
                o + 0.138,
                0.041,
                0.44,
                threshold - 0.06,
                threshold + 2.73,
                STONE,
            )
        for x in (u - w * 0.51, u + w * 0.51):
            site.allen.doors(add, x, w - 0.10, threshold)


def lillis(parts, plan, ground, other, model, gates, base, datum):
    atrium, zones, vault = lillis_roofs(parts, plan, ground, model, base, datum)
    for a, b in face_edges(ground):
        length, add = tools.face(parts, a, b)
        line = LineString([a, b])
        mid = line.interpolate(0.5, normalized=True)
        if length < 0.48 or other.buffer(0.085).covers(mid):
            continue
        gate = aligned_gate(a, b, gates)
        atrium_area = line.intersection(atrium.buffer(0.042)).length
        if atrium_area > length * 0.72 and mid.y < 67 and abs(b[1] - a[1]) < 0.16:
            dx = (b[0] - a[0]) / length
            solar_wall(
                parts,
                a,
                b,
                0.04,
                length - 0.04,
                datum,
                lambda u: vault(a[0] + u * dx, 0) - 0.18,
                gate,
            )
            continue
        roof, label = next(
            ((z, label) for area, z, label in zones if area.buffer(0.055).covers(mid)),
            (17.9, "rotunda"),
        )
        if label == "rotunda" or (atrium_area > length * 0.68 and mid.y > 68):
            add(0, length, -0.023, 0.055, datum, roof - 0.08, GLASS)
            for low in np.arange(datum + 0.58, roof - 0.42, 1.29):
                add(0, length, 0, 0.110, low, low + 0.039, STEEL)
            for x in np.linspace(0.02, length - 0.02, max(2, round(length / 1.4) + 1)):
                add(
                    max(0, x - 0.037),
                    min(length, x + 0.037),
                    0.027,
                    0.138,
                    datum,
                    roof - 0.04,
                    STEEL,
                )
        else:
            add(0, length, -0.018, 0.117, roof - 0.32, roof + 0.11, TERRA_COTTA)
            for floor in np.arange(datum + 1.32, roof - 1.74, 3.95):
                for x in np.linspace(
                    length * 0.11, length * 0.89, max(1, round(length / 2.96))
                ):
                    rectangular_window(
                        add,
                        x,
                        min(1.59, length * 0.39),
                        floor,
                        min(floor + 2.04, roof - 0.53),
                        STEEL,
                    )
                    add(
                        max(0.027, x - 0.50),
                        min(length - 0.025, x + 0.5),
                        0.015,
                        0.065,
                        floor - 0.56,
                        floor - 0.13,
                        SLATE,
                    )
        if gate:
            u = frontage(parts, a, b, gate["position_enu_m"])[2]
            width = gate["width_m"]
            t = gate["threshold_z_m"]
            add(
                u - width * 0.57,
                u + width * 0.57,
                0.027,
                0.31,
                t + 2.46,
                t + 2.73,
                STONE,
            )
            for x in (u - width * 0.25, u + width * 0.25):
                site.allen.doors(add, x, width * 0.47, t)
    recess = plan.difference(ground)
    for a, b in face_edges(plan):
        line = LineString([a, b])
        if (
            line.length < 0.4
            or line.intersection(recess.buffer(0.017)).length < line.length * 0.9
        ):
            continue
        length, add = tools.face(parts, a, b)
        low = datum + 4.15
        add(0, length, -0.014, 0.051, low, 17.83, GLASS)
        for z in np.arange(low, 17.8, 1.27):
            add(0, length, 0.038, 0.108, z, z + 0.056, STEEL)
        for u in np.linspace(0.025, length - 0.025, max(2, round(length / 1.48) + 1)):
            add(
                max(0, u - 0.042),
                min(length, u + 0.042),
                0.034,
                0.125,
                low,
                17.84,
                STEEL,
            )


def court_parts(parts, field, spec, walks, blocked):
    beds = []
    for bounds in spec["beds"]:
        bed = box(*bounds).difference(blocked.buffer(0.14))
        if bed.area < 0.30:
            continue
        top = geometry.sample_ground(field, *bed.centroid.coords[0]) + 0.29
        flat(parts, bed, top - 0.57, top, HISTORIC, GRASS)
        rim = bed.difference(bed.buffer(-0.145, join_style="mitre"))
        flat(parts, rim, top - 0.04, top + 0.122, HISTORIC, STONE)
        blocked = union([blocked, bed])
        beds.extend(geometry.sections(bed))
    for e, n in spec["court_lamps"]:
        z = geometry.sample_ground(field, e, n)
        tools.beam(parts, (e, n, z - 0.06), (e, n, z + 2.60), 0.11, IRON)
        globe = trimesh.creation.icosphere(subdivisions=2, radius=0.19)
        globe.apply_translation([e, z + 2.73, -n])
        globe.visual.vertex_colors = [225, 213, 181, 255]
        parts.append(globe)
    plaza = union(
        [
            Polygon(spec["main"]),
            *walks,
            *[
                LineString(path).buffer(width * 0.5, quad_segs=5)
                for width, path in spec["paths"]
            ],
        ]
    )
    nearby.add_paths(parts, field, plaza, blocked, PAVING)
    return beds, plaza.difference(blocked)


def build(spec, manifest, config, field, graph):
    plans = {
        key: orient(Polygon(model["wall_footprint_enu_m"]))
        for key, model in spec["models"].items()
    }
    grounds = {
        key: orient(Polygon(model["ground_footprint_enu_m"]))
        for key, model in spec["models"].items()
    }
    output, records, course, supports, walks, all_gates = {}, {}, [], [], [], []
    for number, model in spec["models"].items():
        id = model["id"]
        plan, ground = plans[number], grounds[number]
        other = union([poly for key, poly in plans.items() if key != number])
        assert (
            plan.is_valid and ground.is_valid and plan.intersection(other).area < 0.061
        )
        samples = [
            geometry.sample_ground(field, *plan.exterior.interpolate(d).coords[0])
            for d in np.arange(0, plan.exterior.length, 0.64)
        ]
        base = float(min(samples) - 0.48)
        datum = float(np.median(samples))
        parts, gates, rails = [], [], []
        for raw in model["entrances"]:
            assert ground.boundary.distance(Point(raw["position_enu_m"])) < 0.003
            gate, walk, blocks = site_entry(course, field, raw)
            gates.append(gate)
            walks.append(walk)
            rails.extend(blocks)
        if number == "034":
            lillis(parts, plan, ground, other, model, gates, base, datum)
        elif number == "039":
            computing(parts, plan, ground, model, gates, base, datum)
        elif number == "002":
            chiles(parts, plan, other, model, gates, base, datum)
        else:
            historic(parts, plan, other, model, gates, base, datum)
        soup = trimesh.util.concatenate(parts)
        soup.update_faces(soup.nondegenerate_faces(height=0.00005))
        output[id] = nearby.shared.index_mesh(soup)
        records[id] = {k: model[k] for k in ("id", "name", "campus_id")} | dict(
            footprint_enu_m=ring(plan),
            ground_footprints_enu_m=[ring(ground)],
            support_collision_enu_m=[ring(p) for p in rails],
            base_z_m=round(base, 4),
            roof_z_m=round(float(output[id].bounds[1, 1]), 4),
            area_m2=round(plan.area, 3),
            entrances=gates,
        )
        supports.extend(rails)
        all_gates.extend(gates)
    retired = {item["id"] for item in spec["absorbed_batches"]}
    ids = set(output) | retired
    prior = union(
        [
            Polygon(record["footprint_enu_m"]).buffer(0)
            for record in manifest["buildings"]
            if record["id"] in ids
        ]
    )
    building_collision = union([*grounds.values(), *supports])
    beds, open_plaza = court_parts(
        course, field, spec["court"], walks, building_collision
    )
    records[spec["models"]["034"]["id"]]["support_collision_enu_m"].extend(
        ring(bed) for bed in beds
    )
    supports.extend(beds)
    edges, clearance = nearby.shared.graduate.shared.check_routes(
        list(grounds.values()), supports, all_gates, prior, manifest, graph, config, ids
    )
    trees, tree_ids = planting.registered_trees(
        spec, open_plaza, building_collision, field
    )
    assert set(tree_ids) == {plant["number"] for plant in spec["trees"]}
    return (
        output,
        list(records.values()),
        trimesh.util.concatenate(course),
        trees,
        tree_ids,
        (edges, clearance),
    )


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--audit", type=Path, required=True)
    args = cli.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, trees, tree_ids, (count, clearance) = build(
        spec, manifest, config, field, graph
    )
    appearances = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = frohnmayer.source_removals(spec, config, appearances)
    out = SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    site.memorial.gerlinger.export(
        glb,
        meshes,
        ground,
        GROUND,
        "lillis-complex-paving",
        vegetation={"lillis-registered-courtyard-trees": trees},
    )
    descriptor = out / "site.json"
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        ground_node=GROUND,
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        buildings=records,
        absorbed_ids=[r["id"] for r in removals],
        batch_removals=removals,
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    config["lillis_complex_site"] = dict(
        url=f"{DIRECTORY}/site.json", sha256=tools.digest(descriptor)
    )
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit = dict(
        areas={m["id"]: m["area_m2"] for m in records},
        entrances={m["id"]: m["entrances"] for m in records},
        triangles={id: len(mesh.faces) for id, mesh in meshes.items()},
        route_edges=count,
        trees=tree_ids,
        nearest_route=round(clearance, 3),
        batch_removals=removals,
        glb_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
