# SPDX-License-Identifier: Apache-2.0
"""Build Friendly Hall, Collier House and McKenzie Hall from registered exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-lillis-complex-site-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)
tools, site, geometry = shared.tools, shared.site, shared.geometry
nearby = shared.nearby
roof_cells = nearby.shared.graduate.roof_cells
roof_layer = nearby.shared.roof_layer
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/friendly-collier-mckenzie-site-review.json"
DIRECTORY = "friendly-collier-mckenzie-review"
GROUND = "friendly-collier-mckenzie-grounds"

BRICK = (148, 92, 81)
RED_BRICK = (158, 99, 85)
DARK_BRICK = (123, 80, 68)
ROOF = (112, 118, 115)
ROOF_DARK = (98, 104, 101)
METAL = (151, 150, 133)
LIMESTONE = (176, 163, 143)
SILL = (177, 166, 147)
CREAM = (210, 199, 171)
FILL = (206, 207, 197)
TRIM = (233, 232, 218)
SIDING = (183, 190, 185)
LINE = (156, 168, 161)
FLOOR = (128, 108, 91)
PAVING = (174, 169, 153)
COURT = (163, 160, 147)
GRASS = (142, 153, 108)
IRON = (73, 82, 77)
GLASS = (68, 94, 95)
GLASS_PALE = (102, 130, 130)
CONCRETE = (170, 166, 149)
BRUTALIST_BRICK = (175, 156, 119)
BRUTALIST_LIGHT = (184, 166, 130)

flat, union, ring = shared.flat, shared.union, shared.ring
face_edges = shared.face_edges


def fit_base(field, outline):
    perimeter = outline.exterior
    readings = [
        geometry.sample_ground(field, *perimeter.interpolate(u).coords[0])
        for u in np.arange(0, perimeter.length, 0.54)
    ]
    return float(min(readings) - 0.48), float(np.median(readings))


def hip_planes(bounds, eave, ridge):
    w, s, e, n = bounds
    rise = ridge - eave
    short = min(e - w, n - s) * 0.5
    if e - w > n - s:
        ex, ny = min((e - w) * 0.45, short * 1.30), short
    else:
        ex, ny = short, min((n - s) * 0.45, short * 1.22)
    dx, dy = rise / ex, rise / ny
    return np.array(
        [
            [dx, 0, eave - dx * w],
            [-dx, 0, eave + dx * e],
            [0, dy, eave - dy * s],
            [0, -dy, eave + dy * n],
        ]
    )


def pitched(parts, wall, eaves, planes, floor, wall_color, roof_color=ROOF):
    for area, top in roof_cells(wall, planes):
        site.surface(
            parts, area, floor, lambda e, n: top(e, n) - 0.14, wall_color, roof_color
        )
    for area, top in roof_cells(eaves, planes):
        roof_layer(parts, area, top, 0.175, 0.018, METAL, roof_color)

    return lambda e, n: np.min(planes @ [e, n, 1])


def roof_partition(parts, footprint, sections, floor, wall_color, inset=0.34):
    remaining = footprint
    roof_heights = []
    for label, region, eave, ridge in sections:
        shell = remaining.intersection(box(*region))
        if shell.area <= 0.10:
            continue
        outside = shell.buffer(inset, join_style="mitre").difference(
            footprint.difference(shell)
        )
        if ridge - eave < 0.18:
            flat(parts, shell, floor, eave, wall_color, ROOF)
            flat(parts, outside, eave - 0.12, eave + 0.08, METAL, ROOF)
            top = lambda e, n, z=eave + 0.06: z
        else:
            planes = hip_planes(outside.bounds, eave, ridge)
            if label == "main-house":
                planes[:, :2] *= 1.17
                planes[:, 2] = eave + (planes[:, 2] - eave) * 1.17
                planes = np.vstack([planes, [0, 0, ridge]])
            top = pitched(parts, shell, outside, planes, floor, wall_color)
        roof_heights.append((shell, top, label))
        remaining = remaining.difference(shell)
    return remaining, roof_heights


def height_at(zones, x, n, default):
    point = Point(x, n)
    for area, height, label in zones:
        if area.buffer(0.035).covers(point):
            return float(height(x, n)), label
    return default, "wall"


def close_sash(add, center, width, low, upper, color=CREAM, shade=GLASS, cols=2):
    left, right = center - width * 0.5, center + width * 0.5
    if width < 0.24 or upper - low < 0.31:
        return
    add(left - 0.071, right + 0.071, 0.012, 0.064, low - 0.075, upper + 0.085, color)
    add(left, right, 0.065, 0.087, low, upper, shade)
    for x in np.linspace(left, right, cols + 1):
        add(x - 0.016, x + 0.016, 0.086, 0.115, low, upper, color)
    for t in (0.07, 0.52, 0.94):
        z = low + t * (upper - low)
        add(left, right, 0.086, 0.116, z - 0.023, z + 0.023, color)
    add(left - 0.072, right + 0.072, 0.035, 0.17, low - 0.095, low - 0.024, SILL)


def cylinder(parts, e, n, low, high, radius, color, sides=12):
    mesh = trimesh.creation.cylinder(radius=radius, height=high - low, sections=sides)
    mesh.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], [0, 1, 0]))
    mesh.apply_translation([e, 0.5 * (low + high), -n])
    mesh.visual.vertex_colors = [*color, 255]
    parts.append(mesh)


def friendly_roofs(parts, ground, spec, base):
    p = spec["main_roof"]
    west, south, east, north = p["bounds"]
    ridge = p["ridge_e"]
    main = ground.intersection(
        box(west + 0.57, south - 1.0, spec["main_end_e"], north + 1.0)
    )
    outer = main.buffer(0.36, join_style="mitre").difference(ground.difference(main))
    edge_low, top_z = p["eave"], p["top"]
    inner = 0.145
    side_slope = 1.58
    planes = np.array(
        [
            [inner, 0, top_z - inner * ridge],
            [-inner, 0, top_z + inner * ridge],
            [side_slope, 0, edge_low - side_slope * west],
            [-side_slope, 0, edge_low + side_slope * east],
            [0, 1.39, edge_low - 1.39 * south],
            [0, -1.39, edge_low + 1.39 * north],
        ]
    )
    roofline = pitched(parts, main, outer, planes, base, BRICK, ROOF)
    rest, zones = roof_partition(
        parts, ground.difference(main), spec["east_roof_sections"], base, RED_BRICK
    )
    flat(parts, rest, base, 10.01, RED_BRICK, ROOF_DARK)
    zones.insert(0, (main, roofline, "original"))
    zones.append((rest, lambda e, n: 10.01, "link"))
    for n in spec["dormer_n"]:
        panel = box(west + 0.64, n - 1.06, west + 3.34, n + 1.06).intersection(outer)
        if panel.area < 2.1:
            continue
        _, y0, _, y1 = panel.bounds
        x = panel.bounds[0]
        low = max(15.0, float(roofline(x, n)) - 0.14)
        roof = min(18.43, float(roofline(x + 2.22, n)) + 0.26)
        if roof - low < 1.08:
            continue
        flat(parts, panel, low, roof - 0.18, DARK_BRICK)
        flat(
            parts,
            panel.buffer(0.12, join_style="mitre"),
            roof - 0.23,
            roof,
            METAL,
            ROOF,
        )
        length, add = tools.face(parts, (x, y1), (x, y0))
        close_sash(add, length * 0.5, min(length - 0.23, 1.34), low + 0.12, roof - 0.31)
    return zones


def friendly_portal(parts, gate, field):
    e, n = gate["position_enu_m"]
    threshold = gate["threshold_z_m"]
    low = geometry.sample_ground(field, e - 2.1, n) - 0.38
    supports = []
    slab = box(e - 1.93, n - 2.12, e + 0.035, n + 2.12)
    flat(parts, slab, low, threshold - 0.018, LIMESTONE)
    canopy = box(e - 2.16, n - 2.20, e + 0.15, n + 2.20)
    hi = threshold + 3.28
    flat(parts, canopy, hi - 0.24, hi, CREAM, CONCRETE)
    flat(parts, canopy.buffer(0.088, join_style="mitre"), hi, hi + 0.115, CREAM, METAL)
    for dy in (-1.84, 1.84):
        x, y = e - 1.76, n + dy
        supports.append(box(x - 0.17, y - 0.17, x + 0.17, y + 0.17))
        flat(parts, supports[-1], low, threshold + 0.16, LIMESTONE)
        cylinder(parts, x, y, threshold + 0.16, hi - 0.48, 0.133, CREAM)
        cylinder(parts, x, y, hi - 0.48, hi - 0.22, 0.191, CREAM)
    return supports


def arched_panel(parts, a, b, u, width, low, high, surround, fill):
    outline = shared.heritage.arch(u, width, low, high)
    shared.heritage.profile(parts, a, b, outline, 0.062, fill)
    shared.heritage.profile(
        parts, a, b, outline.buffer(0.10).difference(outline), 0.133, surround
    )


def friendly_gable(parts, a, b, center, width, base, top):
    base = min(base, top - width * 0.55)
    arched_panel(parts, a, b, center, width, base, top, LIMESTONE, BRICK)
    disk = Point(center, top - 0.92).buffer(0.28, quad_segs=7)
    shared.heritage.profile(parts, a, b, disk.buffer(0.085), 0.114, SILL)
    shared.heritage.profile(parts, a, b, disk, 0.132, GLASS)


def friendly(parts, ground, spec, gates, field, base, datum):
    zones = friendly_roofs(parts, ground, spec, base)
    supports = []
    for a, b in face_edges(ground):
        length, add = tools.face(parts, a, b)
        if length < 0.71:
            continue
        mid = (np.asarray(a) + b) * 0.5
        top, label = height_at(zones, *mid, 10.01)
        top = max(top, datum + 4)
        gate = shared.aligned_gate(a, b, gates)
        cut = shared.frontage(parts, a, b, gate["position_enu_m"])[2] if gate else -100
        for z in (datum + 0.69, datum + 3.14, top - 0.24):
            add(
                0,
                length,
                -0.016,
                0.113,
                z,
                z + 0.079,
                LIMESTONE if z != datum + 3.14 else DARK_BRICK,
            )
        for z in np.arange(datum + 1.0, min(datum + 3.0, top - 0.35), 0.39):
            add(0, length, -0.012, 0.045, z, z + 0.068, DARK_BRICK)
        count = max(1, round(length / (2.56 if label == "original" else 2.31)))
        for u in np.linspace(
            length / (2 * count), length - length / (2 * count), count
        ):
            if abs(u - cut) < ((gate["width_m"] * 0.54 + 0.19) if gate else 1.0):
                continue
            dx = (np.asarray(b) - a) / length
            x, n = np.asarray(a) + dx * u
            local_top, _ = height_at(zones, x, n, top)
            for z in (datum + 1.11, datum + 4.27, datum + 7.45):
                close_sash(
                    add,
                    u,
                    min(1.13, length * 0.52),
                    z,
                    min(z + 1.80, local_top - 0.52),
                    METAL,
                )
        if label == "original" and length > 8.1 and abs(a[1] - b[1]) < 0.28:
            for u in (length * 0.30, length * 0.70):
                friendly_gable(parts, a, b, u, 3.47, top - 0.85, top + 0.61)
        if gate:
            threshold = gate["threshold_z_m"]
            site.allen.doors(add, cut, gate["width_m"], threshold)
            add(
                cut - 1.29,
                cut + 1.29,
                0.026,
                0.189,
                threshold + 2.34,
                threshold + 2.54,
                CREAM,
            )
            if "-west-" in gate["gate"]:
                supports.extend(friendly_portal(parts, gate, field))
                friendly_gable(parts, a, b, cut, 3.80, min(top - 1.1, 14.32), 17.92)
    paths = [
        LineString(spec[k]).buffer(0.88, quad_segs=5)
        for k in ("front_path", "secondary_path")
    ]
    return supports, paths


def collier_porch(parts, gate, spec, field, base):
    west, south, east, north = spec["porch_bounds"]
    t = gate["threshold_z_m"]
    slab = box(west, south, east, north)
    flat(parts, slab, base, t, DARK_BRICK, FLOOR)
    flat(parts, slab.buffer(0.19, join_style="mitre"), t - 0.14, t - 0.025, TRIM, FLOOR)
    z = t + 2.78
    flat(parts, slab.buffer(0.28, join_style="mitre"), z, z + 0.19, TRIM, ROOF)
    flat(parts, slab.buffer(0.12, join_style="mitre"), z + 0.19, z + 0.27, TRIM, METAL)
    supports = []
    for y in (south + 0.22, north - 0.22):
        x = east - 0.21
        supports.append(box(x - 0.127, y - 0.127, x + 0.127, y + 0.127))
        flat(parts, supports[-1], t, z, TRIM)
        length, add = tools.face(parts, (west + 0.18, y), (east - 0.14, y))
        for high in (t + 0.11, t + 0.92):
            add(0.10, length - 0.04, -0.043, 0.022, high, high + 0.055, TRIM)
        for offset in np.linspace(0.16, length - 0.10, 14):
            add(offset - 0.022, offset + 0.022, -0.037, 0.015, t + 0.12, t + 0.96, TRIM)
    return supports


def mckenzie_south_steps(parts, field, gate):
    e, n = gate["position_enu_m"]
    landing, toe = n - 3.85, n - 7.36
    low = geometry.sample_ground(field, e, toe)
    high = max(low + 0.71, geometry.sample_ground(field, e, n) + 0.33)
    left, right = e - 5.75, e + 5.75
    for i in range(6):
        start = toe + i * (landing - toe) / 6
        z = low + (i + 1) * (high - low) / 6
        flat(
            parts,
            box(left, start, right, landing + 0.022),
            low - 0.45,
            z,
            CONCRETE,
            PAVING,
        )
    flat(
        parts, box(left, landing, right, n + 0.024), low - 0.42, high, CONCRETE, PAVING
    )
    for x in (e - 3.62, e + 3.62):
        tools.beam(
            parts, (x, toe + 0.24, low + 0.96), (x, landing, high + 0.85), 0.054, IRON
        )
        tools.beam(
            parts, (x, toe + 0.24, low + 0.18), (x, toe + 0.24, low + 0.96), 0.051, IRON
        )
        tools.beam(parts, (x, landing, high), (x, landing, high + 0.85), 0.051, IRON)
    approach = box(left - 0.25, toe - 1.24, right + 0.25, toe + 0.06)
    return gate | {"threshold_z_m": round(high, 3)}, approach, []


def collier(parts, ground, spec, gates, field, base, datum):
    rest, zones = roof_partition(
        parts, ground, spec["roof_sections"], base, FILL, inset=0.39
    )
    flat(parts, rest, base, datum + 4.02, FILL, ROOF)
    zones.append((rest, lambda e, n: datum + 4.02, "rear"))
    for a, b, c, d, z in spec["chimneys"]:
        chimney = box(a, b, c, d)
        flat(parts, chimney, datum + 5.2, z, BRICK)
        flat(parts, chimney.buffer(0.08), z, z + 0.14, DARK_BRICK, BRICK)
    supports = []
    for a, b in face_edges(ground):
        length, add = tools.face(parts, a, b)
        if length < 0.45:
            continue
        mid = (np.asarray(a) + b) * 0.5
        roof, name = height_at(zones, *mid, datum + 4.02)
        higher = min(roof - 0.16, 14.02 if name == "main-house" else roof - 0.1)
        add(0, length, -0.016, 0.085, datum - 0.28, datum + 0.52, DARK_BRICK)
        for z in np.arange(datum + 0.57, higher - 0.12, 0.187):
            add(0, length, 0.003, 0.029, z, z + 0.031, LINE)
        if higher > datum + 2:
            add(0, length, -0.015, 0.162, higher - 0.25, higher - 0.025, TRIM)
            stops = np.linspace(0.05, length - 0.05, max(2, round(length / 0.74) + 1))
            for u in stops:
                add(
                    max(0, u - 0.034),
                    min(length, u + 0.034),
                    0.03,
                    0.187,
                    higher - 0.37,
                    higher - 0.14,
                    TRIM,
                )
        gate = shared.aligned_gate(a, b, gates)
        cut = shared.frontage(parts, a, b, gate["position_enu_m"])[2] if gate else -100
        count = max(1, round(length / 2.38))
        for u in np.linspace(
            length / (2 * count), length - length / (2 * count), count
        ):
            if gate and abs(u - cut) < 1.25:
                continue
            width = min(length * 0.61, 1.12)
            for low in (
                (datum + 1.02, datum + 4.55)
                if name == "main-house"
                else (datum + 1.05,)
            ):
                stop = min(low + 1.92, higher - 0.36)
                close_sash(add, u, width, low, stop, TRIM, GLASS_PALE, 1)
                if stop > low + 0.44:
                    add(
                        u - width * 0.59,
                        u + width * 0.59,
                        0.041,
                        0.181,
                        stop + 0.054,
                        stop + 0.123,
                        TRIM,
                    )
        if gate:
            site.allen.doors(add, cut, gate["width_m"], gate["threshold_z_m"])
            if gate["gate"] == "collier-east":
                supports.extend(collier_porch(parts, gate, spec, field, base))
    paths = [LineString(path).buffer(0.86, quad_segs=5) for path in spec["walks"]]
    return supports, paths


def mckenzie_masses(parts, plan, ground, spec, base, datum):
    rest = plan
    zones = []
    for label, bounds, roof, cap in [
        *spec["roof_divisions"],
        ["central", plan.bounds, *spec["default_roof"]],
    ]:
        area = rest.intersection(box(*bounds))
        if area.area < 0.2:
            continue
        footprint = area.intersection(ground)
        overhang = area.difference(footprint)
        flat(parts, footprint, base, roof, BRUTALIST_BRICK, CONCRETE)
        for shell in geometry.sections(overhang):
            # The south canopy is solid. Courtyard floors overhang the
            # recessed glazing in three deep slabs with exposed supports.
            if shell.centroid.y < 155:
                flat(parts, shell, 3.84, roof, BRUTALIST_LIGHT, CONCRETE)
                for z in np.arange(3.84, roof - 0.23, 3.55):
                    flat(parts, shell, z, z + 0.24, CONCRETE)
            else:
                flat(parts, shell, roof - 0.46, roof, CONCRETE)
                for z in (1.18, 4.71, 8.26):
                    flat(parts, shell, z, z + 0.28, CONCRETE)
        nearby.parapet(parts, area, roof, cap, CONCRETE, CONCRETE, 0.29)
        zones.append((area, lambda e, n, z=roof: z, label))
        rest = rest.difference(area)
    for w, s, e, n, z in spec["equipment"]:
        volume = box(w, s, e, n).intersection(plan.buffer(-0.24))
        if volume.area < 0.09:
            continue
        start, _ = height_at(zones, *volume.centroid.coords[0], 11.0)
        flat(parts, volume, start - 0.025, z - 0.09, BRUTALIST_BRICK, CONCRETE)
        flat(parts, volume.buffer(0.058), z - 0.11, z, CONCRETE)
    return zones


def mckenzie_arcades(parts, plan, ground, spec, field):
    supports = []
    for index, bounds in enumerate(spec["recesses"]):
        pocket = plan.intersection(box(*bounds)).difference(ground)
        if pocket.is_empty:
            continue
        w, s, e, n = pocket.bounds
        if index == 0:
            edge = [(x, s + 0.63) for x in np.linspace(w + 0.73, e - 0.71, 4)]
            underside = 3.91
        else:
            edge = [(e - 0.38, y) for y in np.linspace(s + 0.91, n - 0.91, 9)]
            underside = 1.18
        for x, y in edge:
            p = box(x - 0.215, y - 0.215, x + 0.215, y + 0.215)
            base = geometry.sample_ground(field, x, y) - 0.28
            if pocket.buffer(0.07).covers(p.centroid):
                flat(parts, p, base, underside, CONCRETE)
                supports.append(p)
            if index != 1:
                continue
            for low in (1.3, 4.8, 8.37):
                fins = box(x - 0.19, y - 0.14, x + 0.22, y + 0.14)
                flat(parts, fins, low, min(low + 2.65, 11.01), CONCRETE)
        if index == 1:
            for z in (1.18, 4.71, 8.26):
                band = box(e - 0.17, s, e + 0.17, n)
                flat(parts, band, z, z + 0.30, CONCRETE)
    return supports


def mckenzie(parts, ground, plan, spec, gates, field, base, datum):
    zones = mckenzie_masses(parts, plan, ground, spec, base, datum)
    supports = mckenzie_arcades(parts, plan, ground, spec, field)
    for a, b in face_edges(ground):
        length, add = tools.face(parts, a, b)
        if length < 0.59:
            continue
        v = (np.asarray(b) - a) / length
        outside = np.array([v[1], -v[0]])
        gate = shared.aligned_gate(a, b, gates)
        cut = shared.frontage(parts, a, b, gate["position_enu_m"])[2] if gate else -50
        is_court = (
            a[0] > -584.1
            and b[0] > -584.1
            and min(a[1], b[1]) >= 169.9
            and max(a[1], b[1]) <= 198.1
        )
        count = max(1, round(length / (2.33 if not is_court else 2.83)))
        for u in np.linspace(
            length / (count * 2), length - length / (count * 2), count
        ):
            e, n = np.asarray(a) + v * u
            grade = geometry.sample_ground(
                field, e + 0.27 * outside[0], n + 0.27 * outside[1]
            )
            top, label = height_at(zones, e, n, 10.99)
            width = min(length * 0.57, 1.43 if "west" in label else 2.08)
            for z in (
                (-1.38, 2.09, 5.62, 9.1) if grade < -0.65 else (0.75, 4.08, 7.59, 11.13)
            ):
                if z < grade + 0.14:
                    continue
                if (
                    gate
                    and abs(u - cut) < max(1.30, gate["width_m"] * 0.56)
                    and z < gate["threshold_z_m"] + 2.64
                ):
                    continue
                stop = min(top - 0.48, z + 2.15)
                close_sash(
                    add, u, width, z, stop, IRON, GLASS_PALE if is_court else GLASS
                )
                if stop > z + 0.38:
                    add(
                        u - width * 0.66,
                        u + width * 0.66,
                        0.018,
                        0.153,
                        z - 0.47,
                        z - 0.16,
                        CONCRETE,
                    )
            post = min(0.18, length * 0.065)
            offset = min(length - 0.20, u + width * 0.59)
            if length > 1.58:
                add(
                    offset - post,
                    offset + post,
                    0.018,
                    0.28,
                    max(-1.95, grade - 0.35),
                    top - 0.15,
                    CONCRETE,
                )
        e, n = (np.asarray(a) + b) * 0.5
        top, _ = height_at(zones, e, n, 10.99)
        for z in np.arange(-2.0, top - 0.13, 3.55):
            add(0, length, -0.014, 0.18, z, z + 0.28, CONCRETE)
        add(0, length, -0.015, 0.129, top - 0.33, top + 0.04, CONCRETE)
        if gate:
            threshold = gate["threshold_z_m"]
            width = gate["width_m"]
            site.allen.doors(add, cut, width, threshold)
            add(
                cut - width * 0.58,
                cut + width * 0.58,
                0.016,
                0.145,
                threshold + 2.33,
                threshold + 2.68,
                IRON,
            )
    return supports


def courtyard(parts, spec, field, blocked):
    court = Polygon(spec["court_outline"])
    bed = box(*spec["court_bed"])
    nearby.add_paths(parts, field, court, union([blocked, bed]), COURT)
    nearby.add_paths(parts, field, bed, blocked, GRASS)
    supports = []
    west, south, east, north = spec["court_stairs"]
    center = (south + north) * 0.5
    floor = geometry.sample_ground(field, west, center)
    upper = geometry.sample_ground(field, east, center)
    bottom = min(floor, upper) - 0.52
    heights = []
    for i, (x0, x1) in enumerate(
        zip(np.linspace(west, east, 14)[:-1], np.linspace(west, east, 14)[1:])
    ):
        z = max(
            geometry.sample_ground(field, x1, center) + 0.10,
            floor + (i + 1) * (upper - floor) / 13 + 0.045,
        )
        heights.append(z)
        flat(parts, box(x0, south, x1, north), bottom, z, CONCRETE, PAVING)
    for y in (south, north):
        curb = box(west, y - 0.095, east, y + 0.095)
        site.surface(
            parts,
            curb,
            bottom,
            lambda x, n: geometry.sample_ground(field, x, center) + 0.27,
            CONCRETE,
            CONCRETE,
        )
        supports.append(curb)
        tools.beam(
            parts,
            (west, y, heights[0] + 0.83),
            (east, y, heights[-1] + 0.83),
            0.061,
            IRON,
        )
    for a, b in list(face_edges(court))[1:4]:
        side = LineString([a, b])
        barrier = side.buffer(0.18, cap_style="flat").difference(
            box(west - 0.4, south - 0.17, east + 0.4, north + 0.17)
        )
        if barrier.is_empty:
            continue

        def height(x, n):
            return geometry.sample_ground(field, x, n) + 0.74

        site.surface(parts, barrier, -2.46, height, CONCRETE, CONCRETE)
        supports.extend(geometry.sections(barrier))
    for outline in (spec["south_walk"], spec["north_walk"]):
        nearby.add_paths(parts, field, Polygon(outline), blocked, PAVING)
    return supports


def build(spec, manifest, config, field, graph):
    meshes, records, terrain, solids, site_supports, gates = {}, [], [], [], [], []
    grade_paths = []
    for code, m in spec["models"].items():
        plan = orient(Polygon(m["footprint_enu_m"]))
        ground = orient(Polygon(m["ground_footprint_enu_m"]))
        assert plan.is_valid and ground.is_valid
        base, datum = fit_base(field, plan)
        parts, entries, supports = [], [], []
        for raw in m["entrances"]:
            assert ground.boundary.distance(Point(raw["position_enu_m"])) < 0.004
            enabled = raw
            if raw["gate"] == "collier-east":
                enabled = raw | {
                    "position_enu_m": [
                        m["porch_bounds"][2] - 0.34,
                        raw["position_enu_m"][1],
                    ]
                }
            entry_builder = (
                mckenzie_south_steps
                if raw["gate"] == "mckenzie-south"
                else shared.site_entry
            )
            gate, paving, caps = entry_builder(terrain, field, enabled)
            entries.append(gate | {"position_enu_m": raw["position_enu_m"]})
            grade_paths.append(paving)
            supports.extend(caps)
        if code == "009":
            piers, paths = friendly(parts, ground, m, entries, field, base, datum)
            grade_paths.extend(paths)
        elif code == "081":
            piers, paths = collier(parts, ground, m, entries, field, base, datum)
            grade_paths.extend(paths)
        else:
            piers = mckenzie(parts, ground, plan, m, entries, field, base, datum)
            piers.extend(
                courtyard(terrain, m, field, union([ground, *piers, *supports]))
            )
        supports.extend(piers)
        model = trimesh.util.concatenate(parts)
        model.update_faces(model.nondegenerate_faces(height=0.00005))
        id = m["id"]
        meshes[id] = nearby.shared.index_mesh(model)
        solids.append(ground)
        site_supports.extend(supports)
        gates.extend(entries)
        records.append(
            {k: m[k] for k in ("id", "name", "campus_id")}
            | dict(
                footprint_enu_m=ring(plan),
                ground_footprints_enu_m=[ring(ground)],
                support_collision_enu_m=[ring(piece) for piece in supports],
                base_z_m=round(base, 4),
                roof_z_m=round(float(meshes[id].bounds[1, 1]), 4),
                area_m2=round(plan.area, 3),
                entrances=entries,
            )
        )
    prior = union(
        [
            Polygon(row["footprint_enu_m"]).buffer(0)
            for row in manifest["buildings"]
            if row["id"] in meshes
        ]
    )
    edges, clearance = nearby.shared.graduate.shared.check_routes(
        solids, site_supports, gates, prior, manifest, graph, config, set(meshes)
    )
    nearby.add_paths(
        terrain, field, union(grade_paths), union([*solids, *site_supports]), PAVING
    )
    return meshes, records, trimesh.util.concatenate(terrain), (edges, clearance)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--audit", type=Path, required=True)
    args = cli.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    terrain = SCENE / manifest["heightfield_url"]
    field = json.loads(terrain.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, (count, clearance) = build(
        spec, manifest, config, field, graph
    )
    output = SCENE / DIRECTORY
    output.mkdir(exist_ok=True)
    glb = output / "site.glb"
    site.memorial.gerlinger.export(
        glb, meshes, ground, GROUND, "friendly-collier-mckenzie-paving"
    )
    descriptor = output / "site.json"
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(terrain),
        ground_node=GROUND,
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        buildings=records,
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    config["friendly_collier_mckenzie_site"] = dict(
        url=f"{DIRECTORY}/site.json", sha256=tools.digest(descriptor)
    )
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )
    result = dict(
        buildings={
            b["id"]: {
                "area_m2": b["area_m2"],
                "entrances": b["entrances"],
                "triangles": len(meshes[b["id"]].faces),
            }
            for b in records
        },
        route_edges=count,
        nearest_route_m=round(clearance, 3),
        glb_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
        court_height_samples={
            str((e, n)): round(float(geometry.sample_ground(field, e, n)), 3)
            for e, n in ((-577.0, 184.0), (-573.0, 186.0), (-567.0, 186.0))
        },
    )
    args.audit.write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
