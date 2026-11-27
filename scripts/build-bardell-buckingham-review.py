# SPDX-License-Identifier: Apache-2.0
"""Export registered Bardell, Buckingham and northeast boundary homes."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient

northwest = import_module("build-northwest-blocks-review")
agate, fairmount, garden, hilyard, older = (
    northwest.agate,
    northwest.fairmount,
    northwest.garden,
    northwest.hilyard,
    northwest.older,
)
bardell = import_module("build-bardell-avenue-exterior-review")
PACKAGE = "bardell-buckingham-review"
GROUND = "bardell-buckingham-paving"
CREAM = (186, 183, 162)
IRON = (81, 87, 77)


def direction(row, side):
    e, n = row["roof_frame"]["axis"]
    return {"N": (-n, e), "S": (n, -e), "E": (e, n), "W": (-e, -n)}[side]


def locate(views, row, world, side, near):
    candidate = Point(world(*near))
    v = np.asarray(direction(row, side))
    options = [
        (i, edge.distance(candidate))
        for i, (edge, shape) in enumerate(views)
        if shape[0] > 1.09 and shape[2] @ v > 0.66
    ]
    i, _ = min(options, key=lambda hit: hit[1])
    edge, _ = views[i]
    return i, edge.project(candidate)


def facade_garage(add, panel, style, u, width, level, head, trim):
    count = style["count"]
    colors = style["color"]
    span = width / count
    for i in range(count):
        center = u + (i - (count - 1) / 2) * span
        half = span * 0.47 - 0.08
        a, b = center - half, center + half
        add(a - 0.072, b + 0.072, 0.013, 0.085, level, head + 0.06, trim)
        if style["arches"]:
            shape = Polygon(
                [
                    (a, level),
                    (b, level),
                    *bardell.arch(2 * half, head - 0.14, 0.18, center),
                ]
            )
            panel(orient(shape), 0.086, 0.114, colors)
        else:
            add(a, b, 0.086, 0.112, level + 0.025, head, colors)
        strokes = tuple(max(0, c - 21) for c in colors)
        for y in np.arange(level + 0.19, head - 0.18, 0.27):
            add(a + 0.018, b - 0.018, 0.112, 0.122, y, y + 0.017, strokes)
        if count == 1:
            for x in np.linspace(a + 0.27, b - 0.27, 6):
                add(
                    x - 0.12,
                    x + 0.12,
                    0.121,
                    0.133,
                    head - 0.35,
                    head - 0.19,
                    (103, 119, 116),
                )


def casing(add, panel, level, top, span, u, trim):
    top = min(top, level + 2.74)
    if top < level + 2.03:
        return
    a, b = max(0.05, u - 0.78), min(span - 0.05, u + 0.78)
    if b - a < 0.93:
        return
    p = Polygon(
        [(a, level), (b, level), *bardell.arch(b - a, top - 0.28, 0.28, (a + b) / 2)]
    )
    panel(orient(p), 0.048, 0.079, trim)
    inner = p.buffer(-0.105)
    if not inner.is_empty:
        panel(orient(inner), 0.083, 0.121, (102, 117, 106))
        add(u - 0.026, u + 0.026, 0.118, 0.135, level + 0.20, top - 0.24, trim)


def facade(parts, row, wall, field, world, roof):
    features = row["features"]
    views = list(fairmount.views(parts, wall))
    garage_on = {}
    for style in features.get("garages", []):
        i, u = locate(views, row, world, style["side"], style["near"])
        garage_on[i] = (u, style)
    door = features.get("door")
    gate_plan = locate(views, row, world, door["side"], door["near"]) if door else None
    gables = {
        locate(views, row, world, side, (s, t))[0]
        for side, s, t in features.get("timber", [])
    }
    trim = row["trim_color"]
    for index, (_, (span, add, normal, plan, _, panel)) in enumerate(views):
        if span < 1.18:
            continue
        grade = hilyard.grade(field, plan(span / 2, 0))
        stations = np.linspace(0.09, span - 0.09, max(6, round(span / 0.44)))
        caps = np.array([roof(plan(u, 0)) - 0.18 for u in stations])
        slab = min(caps.min() - 0.1, grade + 0.49)
        add(0.088, span - 0.088, 0.006, 0.039, grade - 0.055, slab, features["brick"])
        tone = tuple(max(0, c - 12) for c in row["wall_color"])
        for y in np.arange(slab + 0.19, caps.max() - 0.10, 0.27):
            active = stations[caps > y + 0.10]
            if len(active) > 1:
                add(active[0], active[-1], 0.005, 0.022, y, y + 0.011, tone)
        slots = []
        if index in garage_on:
            target, style = garage_on[index]
            width = min(style["width"], span - 0.36)
            u = float(np.clip(target, width / 2 + 0.15, span - width / 2 - 0.15))
            floor = hilyard.grade(field, plan(u, 0.12)) + 0.03
            cap = min(
                roof(plan(x, 0)) - 0.20 for x in (u - width * 0.44, u, u + width * 0.44)
            )
            top = min(floor + 2.22, cap)
            if top - floor > 1.66:
                facade_garage(add, panel, style, u, width, floor, top, trim)
                slots.append((u, width / 2 + 0.16))
            if style["gable"] and caps.max() - floor > 2.25:
                bardell.finish_gable(
                    panel, add, floor, stations, caps, row["wall_color"]
                )
        if gate_plan and index == gate_plan[0]:
            u = float(np.clip(gate_plan[1], 0.64, span - 0.64))
            level = hilyard.grade(field, plan(u, 0.03)) + 0.11
            cap = roof(plan(u, 0)) - 0.20
            if door["arch"]:
                casing(add, panel, level, cap, span, u, trim)
            else:
                hilyard.potter.door(add, u, level, (108, 106, 86))
            slots.append((u, 1.20))
            if cap - level > 2.48 and span > 2.52:
                add(
                    max(0.14, u - 0.95),
                    min(span - 0.14, u + 0.95),
                    0.02,
                    0.40,
                    level + 2.26,
                    level + 2.38,
                    trim,
                )
        if index in gables:
            y = grade + 2.21
            for u in np.linspace(0.24, span - 0.24, max(2, round(span / 1.13))):
                top = roof(plan(u, 0)) - 0.22
                if top > y + 0.21:
                    add(u - 0.029, u + 0.029, 0.032, 0.078, y, top, (94, 96, 82))
        num = max(1, round(span / 3.6))
        width = span / num
        for j in range(num):
            u = (j + 0.5) * width
            local = hilyard.grade(field, plan(u, 0))
            top = roof(plan(u, 0)) - 0.25
            window = min(1.57, width * 0.54)
            if not any(abs(u - d) < r + window / 2 for d, r in slots):
                sill = local + 0.78
                head = min(top, sill + 1.29)
                if head - sill > 0.46:
                    bardell.framed_window(add, u, window, sill, head, trim, 2)
            if (upper := features.get("second")) is not None:
                sill = upper + 0.53
                head = min(top, sill + 1.23)
                if head - sill > 0.43 and sill > local + 2.06:
                    bardell.framed_window(add, u, window, sill, head, trim, 2)
    return views, gate_plan


def registered_approach(parts, paving, row, field, gate_plan, views):
    door = row["features"].get("door")
    if not gate_plan or door["distance"] is None:
        return []
    index, at = gate_plan
    edge, (span, _, normal, plan, _, _) = views[index]
    u = float(np.clip(at, 0.64, span - 0.64))
    point = Point(plan(u, 0))
    level = hilyard.grade(field, plan(u, 0.03)) + 0.11
    bearing = float(np.degrees(np.arctan2(normal[0], normal[1])) % 360)
    spec = dict(
        gate="street-entry",
        bearing=bearing,
        threshold_z_m=level,
        width_m=1.13,
        distance_m=door["distance"],
        stair_run_m=1.10,
    )
    return [
        hilyard.frontages.estimated_entry(
            paving, {**row, "entry": spec, "entry_finish": "stone"}, field, edge, point
        )
    ]


def east_apron(paving, field, outline):
    # The low east wing crosses the sampled field boundary.
    boundary = field["min_east_m"] + (field["nx"] - 1) * field["spacing_m"]
    _, south, east, north = outline.bounds
    step = field["spacing_m"]
    start = (
        np.floor((south - 3 - field["min_north_m"]) / step) * step
        + field["min_north_m"]
    )

    def top(_, n):
        return hilyard.grade(field, (boundary, n)) - 0.011

    for n in np.arange(start, north + 3, step):
        piece = orient(box(boundary - 0.014, n, east + 2.0, n + step))
        low = min(top(*p) for p in piece.exterior.coords) - 0.12
        mesh = fairmount.geometry.shell(
            piece, low, top, (145, 149, 111), (145, 149, 111)
        )
        mesh.update_faces(mesh.face_normals[:, 1] > 0.03)
        mesh.remove_unreferenced_vertices()
        paving.append(mesh)


def build(row, field, paving):
    _, _, world = older.transforms(row)
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
    parts = []
    roof = garden.roof_sections(parts, outline, wall, row["base_z_m"], row, grid=0.0002)
    views, gate_plan = facade(parts, row, wall, field, world, roof)
    gates = registered_approach(parts, paving, row, field, gate_plan, views)
    if row["features"].get("east_extension"):
        east_apron(paving, field, outline)
    return agate.output(parts, row, outline, set_precision(wall, 0), [], gates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "bardell_buckingham_site", build
    )


if __name__ == "__main__":
    main()
