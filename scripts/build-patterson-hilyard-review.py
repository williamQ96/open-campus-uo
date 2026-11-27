# SPDX-License-Identifier: Apache-2.0
"""Rebuild the Patterson, Hilyard and East 11th exteriors and approaches."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient

hilyard = import_module("build-hilyard-blocks-review")
thirteenth = import_module("build-east-thirteenth-blocks-review")
agate, fairmount, garden = hilyard.agate, hilyard.fairmount, hilyard.garden
older, geometry = hilyard.older, hilyard.geometry
PACKAGE = "patterson-hilyard-review"
GROUND = "patterson-hilyard-paving"
GLASS = (90, 117, 120)
IVORY = (207, 201, 178)
STONE = (163, 155, 140)
STEEL = (75, 85, 85)


def windows(parts, row, wall, field, roof, decorated, gate_edges):
    for edge, (span, add, _, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.48 or any(edge.equals(facade) for facade in decorated):
            continue
        count = max(1, round(span / 3.0))
        for u in (np.arange(count) + 0.5) * span / count:
            bottom = hilyard.grade(field, plan(u, 0))
            width = min(1.34, span / count * 0.64)
            top = min(roof(plan(u - width / 2, 0)), roof(plan(u + width / 2, 0)))
            for i, floor in enumerate(row["levels_z_m"]):
                if i == 0 and any(edge.equals(gate) for gate in gate_edges):
                    continue
                sill = floor + 0.66
                head = min(sill + 1.46, top - 0.19)
                if sill > bottom + 0.42 and head - sill > 0.65:
                    older.framed(add, u, width, sill, head, 2, row["trim_color"])


def front_wall(parts, wall, row, field, world, roof, paving):
    decorated, piers = [], []
    for front in row["fronts"]:
        side, near = front["side"], front["near"]
        edge, view = hilyard.face_on(parts, wall, world, side, near)
        span, add, _, plan, _, panel = view

        north_south = side in ("N", "S")
        rotated = abs(row["roof_frame"]["axis"][1]) > 0.9

        def u(station):
            if north_south != rotated:
                station_point = (station, near[1])
            else:
                station_point = (near[0], station)
            return edge.project(Point(world(*station_point)))

        left, right = sorted(u(station) for station in front["stations"])
        left, right = max(0.045, left), min(span - 0.045, right)
        if right - left < 0.24:
            continue
        decorated.append(edge)
        trim, skin = front["trim"], front["skin"]
        ground = hilyard.grade(field, plan(0.5 * (left + right), 0))
        top = min(roof(plan(x, 0)) for x in np.linspace(left, right, 11)) - 0.04
        if skin:
            add(left, right, 0.006, 0.032, ground - 0.20, top, skin)
        shift = hilyard.elevate(add, 0.034) if skin else add
        if front["siding"]:
            shade = tuple(round(v * 0.90) for v in skin)
            for z in np.arange(ground + 0.25, top - 0.10, 0.21):
                add(left, right, 0.030, 0.047, z, z + 0.012, shade)
        timber = front["timber"]
        if timber:
            bottom, cap = timber["bottom"], min(timber["top"], top)
            if cap > bottom + 0.19:
                add(left, right, 0.034, 0.059, bottom, cap, (189, 181, 155))
                for b in timber["bays"]:
                    p = u(b)
                    if left + 0.07 < p < right - 0.07:
                        add(
                            p - 0.063,
                            p + 0.063,
                            0.057,
                            0.095,
                            bottom,
                            cap,
                            timber["color"],
                        )
                for z in (bottom, (bottom + cap) / 2, cap - 0.074):
                    add(left, right, 0.052, 0.093, z, z + 0.079, timber["color"])
                for a, b in zip(timber["bays"], timber["bays"][1:]):
                    xs = sorted((u(a), u(b)))
                    if xs[1] - xs[0] < 0.44:
                        continue
                    x0, x1 = xs[0] + 0.08, xs[1] - 0.08
                    pts = [
                        (x0, cap - 0.17),
                        (x1, bottom + 0.10),
                        (x1, bottom + 0.26),
                        (x0, cap - 0.01),
                    ]
                    panel(orient(Polygon(pts)), 0.057, 0.089, timber["color"])
                shift = hilyard.elevate(add, 0.094)
        for z in front["bands"]:
            if ground < z < top - 0.12:
                add(left, right, 0.029, 0.11, z - 0.071, z + 0.061, trim)
        for _, stations, width, sill, head, style in front["windows"]:
            for station in stations:
                center = u(station)
                if not width / 2 + 0.09 < center < span - width / 2 - 0.09:
                    continue
                cap = min(roof(plan(center + k * width / 2, 0)) for k in (-1, 0, 1))
                head_here = min(head, cap - 0.12)
                if head_here - sill < 0.52:
                    continue
                if style in ("arch", "tall-arch"):
                    surround = garden.chapter.arch(
                        center,
                        sill,
                        width,
                        head_here - sill,
                        min(0.36, width * 0.43),
                    )
                    panel(orient(surround), 0.10, 0.14, trim)
                    window = surround.buffer(-0.085)
                    panel(orient(window), 0.14, 0.163, GLASS)
                    for z in np.arange(
                        sill + 0.59,
                        head_here - 0.32,
                        1.15 if style == "tall-arch" else 0.53,
                    ):
                        add(
                            center - width * 0.39,
                            center + width * 0.39,
                            0.16,
                            0.176,
                            z,
                            z + 0.045,
                            trim,
                        )
                elif style == "sash":
                    hilyard.northwest.window_grid(
                        shift, center, width, sill, head_here, 3, 2, trim
                    )
                else:
                    older.framed(shift, center, width, sill, head_here, 2, trim)
        canopy = front["canopy"]
        if canopy:
            top = canopy["z"]
            depth = canopy["depth"]
            add(left, right, -0.09, depth + 0.17, top - 0.23, top, trim)
            add(left, right, depth, depth + 0.19, top - 0.28, top - 0.06, trim)
            base = canopy["raised"]
            for station in canopy["columns"]:
                center = u(station)
                if not left + 0.06 < center < right - 0.06:
                    continue
                pad = orient(
                    Point(plan(center, max(0.17, depth - 0.24))).buffer(
                        0.14, quad_segs=4
                    )
                )
                thirteenth.flat(parts, pad, base, top - 0.18, trim)
                piers.append(pad)
            if depth > 1:
                platform = fairmount.rectangle(plan, left, right, 0, depth)
                hilyard.pier(paving, field, platform, base, STONE)
                hilyard.potter.door(
                    hilyard.elevate(add, 0.031),
                    0.5 * (left + right),
                    base,
                    (104, 70, 61),
                )
                low = hilyard.grade(field, plan((left + right) / 2, depth + 1.6))
                for i in range(5):
                    start = depth + 1.53 - i * 0.30
                    step = fairmount.rectangle(
                        plan, left + 1.2, right - 1.2, start, start + 0.37
                    )
                    hilyard.pier(
                        paving, field, step, low + (base - low) * (i + 1) / 5, STONE
                    )
    return decorated, piers


def octagonal_tower(parts, row, field, world):
    s, t, radius, eaves, peak = row["tower"]
    center = world(s, t)
    polygon = orient(Point(center).buffer(radius, quad_segs=2))
    base = hilyard.grade(field, center) - 0.1
    thirteenth.flat(parts, polygon, base, eaves, (183, 173, 147))
    for edge, (span, add, _, _, _, panel) in fairmount.views(parts, polygon):
        add(0.014, span - 0.014, 0.003, 0.044, base, 1.78, row["wall_color"])
        for z in (1.72, 4.24, 6.28, eaves - 0.10):
            add(0.0, span, 0.0, 0.105, z, z + 0.13, (75, 67, 55))
        add(0.05, 0.15, 0.005, 0.075, 1.83, eaves - 0.08, (75, 67, 55))
        add(span - 0.15, span - 0.05, 0.005, 0.075, 1.83, eaves - 0.08, (75, 67, 55))
        for z in (2.42, 5.06):
            older.framed(
                add, span / 2, min(0.91, span * 0.66), z, z + 1.22, 2, (82, 76, 66)
            )
        start, end = edge.coords
        triangle = orient(Polygon([start, end, center]))
        run = Point(center).distance(edge)

        def conical(e, n):
            return eaves + (peak - eaves) * Point(e, n).distance(edge) / run

        parts.append(
            geometry.shell(
                triangle, eaves - 0.06, conical, row["roof_color"], row["roof_color"]
            )
        )


def dormers(parts, row, patch, world, roof):
    for s, t, width, depth, peak in row.get("dormers", []):
        body = patch((s - width / 2, t - depth / 2, s + width / 2, t + depth / 2))
        low = min(roof(p) for p in body.exterior.coords) - 0.26
        roof_eave = peak - 0.55
        thirteenth.flat(parts, body, low, roof_eave, IVORY)
        centerline = np.asarray(world(s, t))
        normal = np.array(row["roof_frame"]["axis"])
        normal /= np.linalg.norm(normal)
        for a, b in ((s - width / 2, s), (s, s + width / 2)):
            piece = patch((a, t - depth / 2 - 0.09, b, t + depth / 2 + 0.07))

            def slope(e, n):
                return peak - 1.1 / width * abs(
                    (np.array([e, n]) - centerline) @ normal
                )

            parts.append(
                geometry.shell(piece, roof_eave - 0.08, slope, IVORY, row["roof_color"])
            )
        _, (span, add, _, _, _, _) = hilyard.face_on(
            parts, body, world, "S", (s, t - depth / 2)
        )
        older.framed(
            add, span / 2, width * 0.67, roof_eave - 0.84, roof_eave - 0.13, 3, IVORY
        )


def sigep_front(parts, row, wall, world, patch, roof):
    warm = (159, 121, 86)
    stone = (147, 150, 140)
    for t in (-5.4, 5.33):
        edge, (span, add, _, plan, _, _) = hilyard.face_on(
            parts, wall, world, "W", (-19.1, t)
        )
        bottom = row["levels_z_m"][0]
        top = min(roof(plan(u, 0)) for u in (span * 0.25, span * 0.75)) - 0.12
        add(0.04, span - 0.04, 0.002, 0.039, bottom, top, stone)
        for floor in row["levels_z_m"]:
            center = span / 2
            add(
                center - 0.95,
                center + 0.95,
                0.031,
                0.055,
                floor + 0.25,
                floor + 2.52,
                warm,
            )
            older.framed(
                hilyard.elevate(add, 0.067),
                center,
                1.74,
                floor + 0.83,
                floor + 2.27,
                3,
                STEEL,
            )
        for z in np.arange(bottom + 0.25, top - 0.17, 0.30):
            add(0.04, 0.72, 0.036, 0.050, z, z + 0.019, (128, 132, 122))
            add(span - 0.73, span - 0.05, 0.036, 0.050, z, z + 0.019, (128, 132, 122))
    edge, (span, add, _, plan, _, _) = hilyard.face_on(
        parts, wall, world, "W", (-18.1, 0)
    )
    z = row["levels_z_m"][0]
    add(0.09, span - 0.09, 0.007, 0.048, z, 7.35, warm)
    for floor in row["levels_z_m"][1:]:
        older.framed(
            hilyard.elevate(add, 0.051),
            span / 2,
            span * 0.71,
            floor + 0.67,
            floor + 2.22,
            4,
            STEEL,
        )
    add(0.19, span - 0.19, 0.013, 0.98, z + 2.52, z + 2.67, STEEL)
    hilyard.potter.door(hilyard.elevate(add, 0.058), span / 2, z, (141, 62, 48))
    thirteenth.railing(parts, patch(row["concept_terrace"]), 7.45, 1.08, STEEL)


def gate(parts, paving, row, field, wall, world):
    spec = row.get("entrance")
    if not spec:
        return [], []
    edge, (_, _, _, plan, _, _) = hilyard.face_on(
        parts, wall, world, spec["side"], spec["near"]
    )
    at = edge.project(Point(world(*spec["near"])))
    height = hilyard.grade(field, plan(at, 0)) + spec["rise"]
    proxy = {**row, "entrance": {**spec, "height": height}}
    return thirteenth.entry_gate(parts, paving, proxy, wall, field, world), [edge]


def build(row, field, paving):
    patch, _, world = older.transforms(row)
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
    parts = []
    roof = garden.roof_sections(parts, outline, wall, row["base_z_m"], row, grid=0.0002)
    decorated, piers = front_wall(parts, wall, row, field, world, roof, paving)
    gates, gate_edges = gate(parts, paving, row, field, wall, world)
    windows(parts, row, wall, field, roof, decorated, gate_edges)
    older.roof_equipment(parts, row, outline, roof, patch)
    dormers(parts, row, patch, world, roof)
    if "tower" in row:
        octagonal_tower(parts, row, field, world)
    if "concept_terrace" in row:
        sigep_front(parts, row, wall, world, patch, roof)
    if bounds := row.get("terrain_extension_enu_m"):
        hilyard.edge_apron(paving, field, box(*bounds))
    return agate.output(parts, row, outline, wall, piers, gates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "patterson_hilyard_site", build
    )


if __name__ == "__main__":
    main()
