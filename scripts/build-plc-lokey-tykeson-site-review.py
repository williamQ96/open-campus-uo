# SPDX-License-Identifier: Apache-2.0
"""Export the registered PLC, Lokey Education and Tykeson exterior group."""

import argparse
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

from importlib.util import module_from_spec, spec_from_file_location

source = Path(__file__).with_name("build-friendly-collier-mckenzie-site-review.py")
loader = spec_from_file_location(source.stem, source)
earlier = module_from_spec(loader)
loader.loader.exec_module(earlier)
shared = earlier.shared
tools, site, geometry, nearby = (
    earlier.tools,
    earlier.site,
    earlier.geometry,
    earlier.nearby,
)
flat, union, ring = earlier.flat, earlier.union, earlier.ring
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/plc-lokey-tykeson-site-review.json"
DIRECTORY = "plc-lokey-tykeson-review"
GROUND = "plc-lokey-tykeson-grounds"

BRICK = (154, 89, 67)
DEEP_BRICK = (127, 77, 65)
BRICK_LIGHT = (166, 108, 82)
CONCRETE = (170, 167, 149)
LIMESTONE = (204, 193, 166)
SIDING = (191, 181, 163)
TILE_DARK = (115, 88, 73)
ROOF = (170, 170, 159)
TERRA = (193, 180, 163)
GLASS = (68, 99, 107)
GLASS_ALT = (84, 112, 120)
GLASS_SHADOW = (47, 71, 75)
IRON = (65, 77, 75)
PALE = (217, 212, 189)
PATH = (178, 170, 153)
GRASS = (143, 153, 109)
PAVERS = (153, 104, 85)
SHINGLE = (123, 102, 89)


def deck(parts, polygon, base, levels, wall):
    top, cap = levels
    flat(parts, polygon, base, top, wall, ROOF)
    for face in shapely.get_parts(polygon):
        if face.geom_type != "Polygon" or face.area < 0.08:
            continue
        edge = face.difference(face.buffer(-0.27, join_style=2))
        flat(parts, edge, top, cap, CONCRETE, CONCRETE)


def painted_doors(parts, edges, entries, color, glass=GLASS):
    for a, b in edges:
        facade = LineString((a, b))
        for gate in entries:
            point = Point(gate["position_enu_m"])
            if facade.distance(point) > 0.023:
                continue
            u = facade.project(point)
            length, add = tools.face(parts, a, b)
            a0 = max(0.015, u - gate["width_m"] * 0.47)
            b0 = min(length - 0.015, u + gate["width_m"] * 0.47)
            threshold = gate["threshold_z_m"]
            add(a0 - 0.05, b0 + 0.05, 0.025, 0.125, threshold, threshold + 2.53, color)
            add(a0, b0, 0.13, 0.17, threshold + 0.035, threshold + 2.41, glass)
            for frame in (a0, (a0 + b0) * 0.5, b0):
                add(
                    frame - 0.026,
                    frame + 0.026,
                    0.169,
                    0.217,
                    threshold,
                    threshold + 2.44,
                    IRON,
                )
            add(a0, b0, 0.17, 0.21, threshold + 1.03, threshold + 1.08, IRON)


def window(add, x, width, low, top, color=LIMESTONE, shade=GLASS, ribs=2):
    left, right = x - width * 0.5, x + width * 0.5
    add(left - 0.055, right + 0.055, 0.009, 0.066, low - 0.081, top + 0.06, color)
    add(left, right, 0.067, 0.102, low, top, shade)
    for rib in np.linspace(left, right, ribs + 1):
        add(rib - 0.021, rib + 0.021, 0.103, 0.144, low, top, IRON)
    z = low + (top - low) * 0.76
    add(left, right, 0.103, 0.144, z - 0.019, z + 0.019, IRON)


def clear_of_entry(edge, center, half_width, gates):
    return all(
        edge.distance(Point(gate["position_enu_m"])) > 0.023
        or abs(edge.project(Point(gate["position_enu_m"])) - center)
        > gate["width_m"] * 0.5 + half_width + 0.18
        for gate in gates
    )


def plc_frontage(parts, footprint, masks, levels, base, datum, gates):
    for a, b in shared.face_edges(footprint):
        length, add = tools.face(parts, a, b)
        if length < 1.55:
            continue
        edge = LineString((a, b))
        midpoint = edge.interpolate(0.5, normalized=True)
        if midpoint.x <= masks["tower"]:
            role = "tower"
        else:
            role = "wing" if midpoint.y < -140 else "auditorium"
        top = levels[role][0]
        if role == "tower" and abs(a[1] - b[1]) < abs(a[0] - b[0]):
            add(0.07, length - 0.07, 0.01, 0.065, base, top - 0.08, BRICK)
            if length > 4:
                add(
                    length * 0.46,
                    length * 0.52,
                    0.065,
                    0.084,
                    base + 0.34,
                    top - 0.43,
                    DEEP_BRICK,
                )
            continue
        stories = {"tower": 9, "wing": 4, "auditorium": 1}[role]
        floor = min(datum + 0.66, top - 3.0)
        increment = (top - 0.54 - floor) / stories
        bays = max(1, round(length / (3.36 if role == "tower" else 3.1)))
        pitch = length / bays
        for level in range(stories):
            z = floor + level * increment
            add(0.06, length - 0.06, 0.015, 0.112, z - 0.085, z + 0.20, CONCRETE)
            for i in range(bays):
                center = (i + 0.5) * pitch
                width = pitch * 0.74
                if level == 0 and not clear_of_entry(edge, center, width * 0.5, gates):
                    continue
                add(
                    center - width * 0.5,
                    center + width * 0.5,
                    0.019,
                    0.077,
                    z + 0.21,
                    z + 0.69,
                    TILE_DARK,
                )
                window(add, center, width, z + 0.78, z + increment - 0.27, CONCRETE)
                add(
                    center - width * 0.5,
                    center + width * 0.5,
                    0.036,
                    0.089,
                    z + increment - 0.23,
                    z + increment - 0.068,
                    TILE_DARK,
                )
        for i in range(bays + 1):
            u = float(np.clip(i * pitch, 0.08, length - 0.08))
            add(u - 0.065, u + 0.065, 0.036, 0.205, floor + 0.12, top - 0.19, CONCRETE)


def plc(parts, spec, plan, ground, gates, base, datum):
    tower_end = spec["tower_end_e"]
    tower = plan.intersection(box(-630, -190, tower_end, -84))
    auditorium = plan.intersection(box(*spec["auditorium"])).difference(tower)
    wing = plan.difference(union([tower, auditorium]))
    assert all(region.area > 220 for region in (tower, auditorium, wing))
    elevations = spec["roof_levels"]
    for role, footprint in (
        ("tower", tower),
        ("auditorium", auditorium),
        ("wing", wing),
    ):
        deck(
            parts,
            footprint,
            base,
            elevations[role],
            BRICK if role != "auditorium" else BRICK_LIGHT,
        )
    for x0, y0, x1, y1, top in spec["equipment"]:
        target = tower if x1 < tower_end else wing
        low = elevations["tower" if target is tower else "wing"][0]
        shape = target.intersection(box(x0, y0, x1, y1))
        flat(parts, shape, low, top - 0.16, CONCRETE, ROOF)
        flat(parts, shape, top - 0.16, top, IRON, ROOF)
    for n, e, height in (
        (-153.1, -606.91, 44.52),
        (-156.65, -607.97, 43.35),
        (-151.72, -608.55, 43.8),
    ):
        earlier.cylinder(parts, e, n, 41.8, height, 0.054, IRON, 8)
    plc_frontage(
        parts, plan, {"tower": tower_end + 0.065}, elevations, base, datum, gates
    )
    # The east face remains visible above the two wings where their footprints meet.
    for a, b in shared.face_edges(tower):
        if abs(a[0] - tower_end) > 0.002 or abs(b[0] - tower_end) > 0.002:
            continue
        edge = LineString((a, b))
        if edge.distance(plan.boundary) > 0.03 or edge.length < 2.6:
            continue
        length, add = tools.face(parts, a, b)
        count = max(1, round(length / 3.36))
        pitch = length / count
        floor = datum + 0.66
        step = (elevations["tower"][0] - 0.54 - floor) / 9
        for i in range(count):
            center = (i + 0.5) * pitch
            p = edge.interpolate(center)
            if plan.boundary.distance(p) < 0.04:
                continue
            east = Point(p.x + 0.063, p.y)
            above = elevations["auditorium" if auditorium.covers(east) else "wing"][1]
            for story in range(9):
                z = floor + story * step
                if z < above + 0.14:
                    continue
                add(
                    center - pitch * 0.47,
                    center + pitch * 0.47,
                    0.015,
                    0.112,
                    z - 0.085,
                    z + 0.20,
                    CONCRETE,
                )
                add(
                    center - pitch * 0.37,
                    center + pitch * 0.37,
                    0.019,
                    0.077,
                    z + 0.21,
                    z + 0.69,
                    TILE_DARK,
                )
                window(add, center, pitch * 0.74, z + 0.78, z + step - 0.27, CONCRETE)
            add(
                center - pitch * 0.5,
                center - pitch * 0.5 + 0.11,
                0.036,
                0.205,
                above + 0.14,
                elevations["tower"][0] - 0.19,
                CONCRETE,
            )
    painted_doors(parts, shared.face_edges(ground), gates, CONCRETE)
    return []


def roof_pieces(parts, plan, ground, spec, base, wall):
    remaining = plan
    roof_zones = []
    for bounds, eave, ridge in spec["pitched"]:
        region = remaining.intersection(box(*bounds))
        for shape in shapely.get_parts(region):
            if shape.geom_type != "Polygon" or shape.area < 0.06:
                continue
            # Use the local wing rectangle to place the hips.
            planes = earlier.hip_planes(shape.bounds, eave, ridge)
            contact = shape.intersection(ground)
            eaves = shape.buffer(0.31, join_style=2)
            earlier.pitched(parts, contact, eaves, planes, base, wall, SHINGLE)
            voids = shape.difference(ground)
            for missing in shapely.get_parts(voids):
                if missing.geom_type != "Polygon" or missing.area < 0.05:
                    continue
                for zone, z in earlier.roof_cells(missing, planes):
                    site.surface(
                        parts,
                        zone,
                        eave - 0.50,
                        lambda e, n: z(e, n) - 0.14,
                        wall,
                        SHINGLE,
                    )
            roof_zones.append((shape, eave))
        remaining = remaining.difference(region)
    if remaining.area > 0.05:
        low, cap = spec["lower_roof"]
        deck(parts, remaining.intersection(ground), base, (low, cap), wall)
        missing = remaining.difference(ground)
        flat(parts, missing, low - 0.38, cap, wall, ROOF)
        roof_zones.append((remaining, low))
    return roof_zones


def lokey_frontage(parts, ground, roofs, gates, datum, addition):
    for a, b in shared.face_edges(ground):
        edge = LineString((a, b))
        length, add = tools.face(parts, a, b)
        if length < 1.92:
            continue
        midpoint = edge.interpolate(0.5, normalized=True)
        eave = next(
            (z for poly, z in roofs if poly.buffer(0.04).covers(midpoint)), None
        )
        if eave is None:
            continue
        floor = min(datum + 0.59, eave - 2.64)
        levels = 1 if eave - floor < 5.3 else 2
        rows = (eave - 0.62 - floor) / levels
        add(
            0.055,
            length - 0.055,
            0.017,
            0.115,
            eave - 0.34,
            eave - 0.162,
            LIMESTONE if not addition else SIDING,
        )
        add(0.055, length - 0.055, 0.012, 0.074, floor - 0.26, floor + 0.02, DEEP_BRICK)
        bays = max(1, round(length / (3.33 if addition else 3.14)))
        pitch = length / bays
        for level in range(levels):
            z = floor + rows * level
            cap = min(eave - 0.51, z + rows * 0.79 + 0.49)
            for i in range(bays):
                center = (i + 0.5) * pitch
                width = pitch * (0.74 if addition else 0.64)
                if level == 0 and not clear_of_entry(edge, center, width * 0.5, gates):
                    continue
                window(
                    add,
                    center,
                    width,
                    z + 0.58,
                    cap,
                    PALE,
                    GLASS_ALT if i % 3 == 0 else GLASS,
                    3,
                )
        if not addition and length > 7:
            for i in range(1, bays):
                u = pitch * i
                add(
                    u - 0.065,
                    u + 0.065,
                    0.028,
                    0.111,
                    floor + 0.22,
                    eave - 0.59,
                    BRICK_LIGHT,
                )
    painted_doors(parts, shared.face_edges(ground), gates, LIMESTONE)


def lokey(parts, spec, plan, ground, gates, field, base, datum, addition):
    roofs = roof_pieces(
        parts, plan, ground, spec, base, BRICK_LIGHT if addition else BRICK
    )
    lokey_frontage(parts, ground, roofs, gates, datum, addition)
    supports = []
    if addition:
        portal = box(*spec["south_portal"]).intersection(plan)
        flat(parts, portal, 10.20, 10.65, DEEP_BRICK, SHINGLE)
        west, south, east, _ = portal.bounds
        for e in (west + 0.32, east - 0.32):
            n = south + 0.50
            pad = box(e - 0.17, n - 0.20, e + 0.17, n + 0.20)
            flat(
                parts,
                pad,
                geometry.sample_ground(field, e, n) - 0.22,
                10.31,
                BRICK,
                DEEP_BRICK,
            )
            supports.append(pad)
    return supports


def curtain(add, length, low, high, divisions, rows, offset=0.020):
    if high <= low + 0.30:
        return
    for i in range(divisions):
        left = 0.054 + (length - 0.108) * i / divisions
        right = 0.054 + (length - 0.108) * (i + 1) / divisions
        tone = GLASS_ALT if i % 4 == 1 else GLASS
        add(left, right, offset, offset + 0.034, low, high, tone)
    for t in np.linspace(0.05, length - 0.05, divisions + 1):
        add(t - 0.027, t + 0.027, offset + 0.035, offset + 0.088, low, high, IRON)
    for z in np.linspace(low, high, rows + 1):
        add(
            0.026,
            length - 0.026,
            offset + 0.035,
            offset + 0.073,
            z - 0.026,
            z + 0.026,
            IRON,
        )


def tykeson_clay(add, length, start, top, gates, edge, stories=2):
    count = max(1, round(length / 0.33))
    pitch = length / count
    shades = (TERRA, (197, 186, 171), (205, 192, 172), (184, 175, 167), (190, 174, 156))
    for i in range(count):
        shade = shades[(i * 11 + i // 4) % len(shades)]
        add(pitch * i + 0.017, pitch * (i + 1) - 0.014, 0.014, 0.037, start, top, shade)
    cells = max(1, round(length / 3.47))
    pitch = length / cells
    level_height = (top - start) / stories
    for i in range(cells):
        center = (i + 0.5) * pitch
        width = pitch * (0.57 if i % 4 != 2 else 0.31)
        for story in range(stories):
            z = start + story * level_height
            if not clear_of_entry(edge, center, width * 0.5, gates) and story == 0:
                continue
            window(
                add,
                center,
                width,
                z + 0.66,
                z + level_height - 0.39,
                GLASS_SHADOW,
                GLASS_ALT,
            )


def tykeson_brick(add, length, datum, top, gates, edge):
    cells = max(1, round(length / 3.82))
    pitch = length / cells
    for i in range(cells):
        center = (i + 0.5) * pitch
        for story in range(3):
            z = datum + story * (top - datum - 0.56) / 3
            if story == 0 and not clear_of_entry(edge, center, pitch * 0.40, gates):
                continue
            window(add, center, pitch * 0.64, z + 0.64, z + 2.93, DEEP_BRICK, GLASS)


def tykeson(parts, spec, plan, ground, gates, field, base, datum):
    zones = spec["roof_z_m"]
    wide = box(-480, -80, spec["commons_outer_e"], spec["commons_north"])
    commons = plan.intersection(wide)
    brick = plan.intersection(box(spec["brick_edge_e"], -80, -430, -11))
    core = plan.difference(union([brick, commons]))
    upper = plan.intersection(box(-462.15, -67.70, spec["fourth_setback_e"], -18.1))
    upper = upper.difference(commons.buffer(0.45, join_style=2))
    floor4 = zones["brick"] - 0.34
    for p, top, wall in (
        (brick, zones["brick"], BRICK),
        (core, floor4, TERRA),
        (commons, zones["commons"], GLASS_SHADOW),
    ):
        deck(parts, p.intersection(ground), base, (top - 0.20, top), wall)
        porch_roofs = shapely.difference(p, ground, grid_size=0.001)
        for porch in shapely.get_parts(porch_roofs.simplify(0.004)):
            if porch.geom_type == "Polygon" and porch.area > 0.07:
                flat(parts, porch, min(top - 1.0, datum + 3.42), top, wall, ROOF)
    deck(
        parts,
        upper,
        floor4 - 0.06,
        (zones["terra_cotta"] - 0.21, zones["terra_cotta"]),
        TERRA,
    )
    for x0, y0, x1, y1, z in spec["equipment"]:
        flat(
            parts,
            box(x0, y0, x1, y1).intersection(upper),
            zones["terra_cotta"] - 0.2,
            z,
            CONCRETE,
            ROOF,
        )
    for a, b in shared.face_edges(ground):
        edge = LineString((a, b))
        length, add = tools.face(parts, a, b)
        if length < 1.12:
            continue
        point = edge.interpolate(0.5, normalized=True)
        if (
            commons.buffer(0.04).covers(point)
            or edge.distance(Point(-453.5, -63.95)) < 0.04
        ):
            curtain(
                add,
                length,
                datum + 0.19,
                zones["commons"] - 0.27,
                max(2, round(length / 1.46)),
                4,
            )
        elif brick.buffer(0.04).covers(point):
            tykeson_brick(add, length, datum, zones["brick"], gates, edge)
        elif length > 3 and point.x < -460 and -44 < point.y < -34:
            curtain(
                add,
                length,
                datum + 0.23,
                floor4 - 0.38,
                max(2, round(length / 1.38)),
                7,
            )
        else:
            tykeson_clay(add, length, datum + 3.55, floor4 - 0.06, gates, edge)
            if point.x < -455 and length > 2.4:
                curtain(
                    add,
                    length,
                    datum + 0.24,
                    datum + 3.38,
                    max(2, round(length / 1.47)),
                    2,
                )
    # The open Commons roof terrace fronts the recessed terra-cotta floor.
    line = LineString(
        [
            (spec["commons_outer_e"], -67.65),
            (spec["commons_outer_e"], spec["commons_north"] + 0.12),
        ]
    )
    length, add = tools.face(parts, line.coords[-1], line.coords[0])
    tykeson_clay(
        add, length, zones["commons"] + 0.18, floor4 - 0.06, [], line, stories=1
    )
    a, b, c, d = commons.bounds
    for sample in (
        LineString([(a + 0.18, b + 0.68), (a + 0.18, d - 0.28)]),
        LineString([(a + 0.20, b + 0.68), (c - 0.17, b + 0.68)]),
    ):
        length, rail = tools.face(parts, *sample.coords)
        top = zones["commons"]
        rail(0, length, 0.01, 0.042, top + 0.96, top + 1.015, IRON)
        rail(0.03, length - 0.03, 0.013, 0.035, top + 0.22, top + 0.95, GLASS_ALT)
        for pos in np.linspace(0.04, length - 0.04, max(2, round(length / 1.32))):
            rail(pos - 0.022, pos + 0.022, 0.010, 0.07, top + 0.06, top + 1.00, IRON)
    for side in (0, 180):
        target = next(g for g in gates if g["outward_degrees"] == side)
        e, n = target["position_enu_m"]
        outer = n + (5.235 if side == 0 else -3.87)
        endpoints = [(e - 2.75, outer), (e + 2.73, outer)]
        if side == 0:
            endpoints.reverse()
        length, add = tools.face(parts, *endpoints)
        curtain(add, length, datum + 3.59, floor4 - 0.22, 5, 4)
    for a, b in shared.face_edges(upper):
        edge = LineString((a, b))
        length, add = tools.face(parts, a, b)
        if length < 1.95:
            continue
        shade = (TERRA, (204, 193, 179), (180, 172, 165), (190, 180, 163))
        tiles = max(1, round(length / 0.32))
        for i in range(tiles):
            add(
                i * length / tiles + 0.012,
                (i + 1) * length / tiles - 0.016,
                0.008,
                0.038,
                floor4,
                zones["terra_cotta"] - 0.16,
                shade[i % 4],
            )
        count = max(1, round(length / 3.28))
        for u in np.linspace(
            length / count * 0.5, length - length / count * 0.5, count
        ):
            window(
                add,
                u,
                length / count * 0.66,
                floor4 + 0.57,
                zones["terra_cotta"] - 0.61,
                GLASS_SHADOW,
            )
    canopy = box(*spec["canopy"])
    flat(parts, canopy, datum + 3.22, datum + 3.35, IRON, GLASS_ALT)
    x0, y0, x1, y1 = canopy.bounds
    for n in np.linspace(y0 + 0.12, y1 - 0.12, 15):
        flat(
            parts,
            box(x0, n - 0.027, x1, n + 0.027),
            datum + 3.19,
            datum + 3.35,
            IRON,
            IRON,
        )
    supports = []
    for n in (y0 + 0.59, -58.92, -51.35, y1 - 0.98):
        e = x0 + 0.32
        earlier.cylinder(
            parts,
            e,
            n,
            geometry.sample_ground(field, e, n) - 0.18,
            datum + 3.24,
            0.114,
            IRON,
        )
        supports.append(Point(e, n).buffer(0.115, quad_segs=6))
    painted_doors(parts, shared.face_edges(ground), gates, IRON)
    return supports


def place_grounds(parts, spec, field, blocked):
    plc_model = spec["models"]["008"]
    ab = spec["models"]["007"]
    c = spec["models"]["041"]
    ty = spec["models"]["103"]
    for key in ("east_court", "south_court"):
        court = Polygon(plc_model[key]).difference(blocked.buffer(0.12))
        nearby.add_paths(
            parts, field, court, blocked, PATH if key == "east_court" else GRASS
        )
    paths = [
        LineString(values).buffer(width / 2, cap_style=2, join_style=2)
        for model in (plc_model, ab)
        for width, values in model["court_paths"]
    ]
    court_edging = [
        LineString([(-596.6, -141.08), (-589.37, -141.08), (-586.5, -139.14)]),
        LineString([(-592.3, -158.75), (-591.6, -160.38), (-587.88, -160.64)]),
        LineString([(-598.8, -169.61), (-592.0, -169.67), (-590.18, -168.91)]),
    ]
    surrounds = []
    for edging in court_edging:
        strip = edging.buffer(0.22, cap_style=2, join_style=2)
        if strip.distance(blocked) > 0.65:
            p = edging.interpolate(0.5, normalized=True)
            low = geometry.sample_ground(field, *p.coords[0])
            site.surface(
                parts,
                strip,
                low - 0.48,
                lambda e, n: geometry.sample_ground(field, e, n) + 0.37,
                CONCRETE,
                LIMESTONE,
            )
            surrounds.append(strip)
    nearby.add_paths(parts, field, union(paths), blocked, PATH)
    nearby.add_paths(parts, field, Polygon(c["paving"]), blocked, PAVERS)
    plaza = Polygon(ty["plaza"])
    nearby.add_paths(parts, field, plaza, blocked, PATH)
    benches = []
    for x, y in ty["bench_centers"]:
        shape = shapely.affinity.scale(
            Point(x, y).buffer(0.58, quad_segs=8), 1.35, 0.86
        )
        floor = geometry.sample_ground(field, x, y)
        flat(parts, shape, floor - 0.03, floor + 0.39, CONCRETE, PALE)
        benches.append(shape)
    return surrounds, benches


def build(spec, manifest, config, field, graph):
    meshes, records, site_parts, solids, all_supports, gate_rows = (
        {},
        [],
        [],
        [],
        [],
        [],
    )
    walk_surfaces = []
    for campus, model in spec["models"].items():
        plan = orient(Polygon(model["footprint_enu_m"]))
        ground = orient(Polygon(model["ground_footprint_enu_m"]))
        assert plan.is_valid and ground.is_valid and plan.buffer(0.001).covers(ground)
        base, datum = earlier.fit_base(field, plan)
        parts, entries, supports = [], [], []
        for entry in model["entrances"]:
            assert ground.boundary.distance(Point(entry["position_enu_m"])) < 0.004
            gate, paving, rails = shared.site_entry(site_parts, field, entry)
            walk_surfaces.append(paving)
            entries.append(gate)
            supports.extend(rails)
        if campus == "008":
            supports.extend(plc(parts, model, plan, ground, entries, base, datum))
        elif campus == "103":
            supports.extend(
                tykeson(parts, model, plan, ground, entries, field, base, datum)
            )
        else:
            supports.extend(
                lokey(
                    parts,
                    model,
                    plan,
                    ground,
                    entries,
                    field,
                    base,
                    datum,
                    campus == "041",
                )
            )
        id = model["id"]
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        meshes[id] = nearby.shared.index_mesh(mesh)
        gate_rows.extend(entries)
        solids.append(ground)
        all_supports.extend(supports)
        records.append(
            {k: model[k] for k in ("id", "name", "campus_id")}
            | dict(
                footprint_enu_m=ring(plan),
                ground_footprints_enu_m=[ring(ground)],
                support_collision_enu_m=[ring(s) for s in supports],
                entrances=entries,
                area_m2=round(plan.area, 3),
                base_z_m=round(base, 4),
                roof_z_m=round(float(meshes[id].bounds[1, 1]), 4),
            )
        )
    blocked = union([*solids, *all_supports])
    surrounds, benches = place_grounds(site_parts, spec, field, blocked)
    records[0]["support_collision_enu_m"].extend(ring(p) for p in surrounds)
    records[-1]["support_collision_enu_m"].extend(ring(p) for p in benches)
    all_supports.extend([*surrounds, *benches])
    active = set(meshes) | set(spec["absorbed_into"])
    legacy = union(
        [
            Polygon(row["footprint_enu_m"]).buffer(0)
            for row in manifest["buildings"]
            if row["id"] in active
        ]
    )
    edges, separation = nearby.shared.graduate.shared.check_routes(
        solids, all_supports, gate_rows, legacy, manifest, graph, config, active
    )
    nearby.add_paths(
        site_parts,
        field,
        union(walk_surfaces),
        union([blocked, *surrounds, *benches]),
        PATH,
    )
    return meshes, records, trimesh.util.concatenate(site_parts), edges, separation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, count, separation = build(
        spec, manifest, config, field, graph
    )
    appearances = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["batch_sources"]}, config, appearances
    )
    output = SCENE / DIRECTORY
    output.mkdir(exist_ok=True)
    glb = output / "site.glb"
    site.memorial.gerlinger.export(
        glb, meshes, ground, GROUND, "plc-lokey-tykeson-paving"
    )
    descriptor = output / "site.json"
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        ground_node=GROUND,
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        buildings=records,
        absorbed_ids=list(spec["absorbed_into"]),
        batch_removals=removals,
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    config["plc_lokey_tykeson_site"] = dict(
        url=f"{DIRECTORY}/site.json", sha256=tools.digest(descriptor)
    )
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )
    report = dict(
        areas={b["id"]: b["area_m2"] for b in records},
        entrances={b["id"]: b["entrances"] for b in records},
        triangles={id: len(m.faces) for id, m in meshes.items()},
        route_edges=count,
        nearest_route_m=round(separation, 3),
        batch_removals=removals,
        glb_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(
        json.dumps(
            {
                k: report[k]
                for k in ("areas", "triangles", "route_edges", "nearest_route_m")
            }
        )
    )


if __name__ == "__main__":
    main()
