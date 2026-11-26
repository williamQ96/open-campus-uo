# SPDX-License-Identifier: Apache-2.0
"""Export the Columbia, Moss, and East 19th registered building exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient


agate = import_module("build-agate-emerald-frontages-review")
emerald = agate.emerald
fairmount, garden, geometry = emerald.fairmount, emerald.garden, emerald.geometry
base, potter, frontages = emerald.base, emerald.potter, emerald.frontages
millrace, northwest, chapter = emerald.millrace, emerald.northwest, emerald.chapter
PACKAGE = "columbia-moss-frontages-review"
GROUND = "columbia-moss-approaches"
CONCRETE = (171, 164, 145)
WOOD = (131, 95, 71)
GREEN = (73, 104, 91)
GLASS = (75, 105, 108)


def shell(row):
    roof = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = roof.buffer(-row["eaves_m"], join_style="mitre")
    return roof, wall


def reference_face(wall, row, spec):
    return potter.choose_face(wall, {**spec, "gate": row["id"]})


def railing(parts, start, end, level, rail, spacing=0.165, height=0.92):
    a, b = np.asarray(start), np.asarray(end)
    distance = np.linalg.norm(b - a)
    for z in (level + 0.14, level + height):
        fairmount.beam(parts, (*a, z), (*b, z), 0.050, rail)
    for t in np.linspace(0, 1, max(2, round(distance / spacing) + 1)):
        p = a + (b - a) * t
        fairmount.beam(parts, (*p, level + 0.11), (*p, level + height), 0.033, rail)


def deck(parts, row, field):
    west, south, east, north, top, gate = row["deck"]
    floor = (
        min(
            emerald.grade(field, p)
            for p in ((west, south), (east, south), (west, north), (east, north))
        )
        - 0.1
    )
    base.flat(parts, box(west, south, east, north), floor, top, WOOD)
    for e in np.arange(west + 0.13, east - 0.08, 0.255):
        base.flat(
            parts,
            box(e - 0.015, south + 0.032, e + 0.015, north - 0.033),
            top,
            top + 0.006,
            (104, 78, 62),
        )
    fences = [(west, gate - 0.77), (gate + 0.77, east)]
    for a, b in fences:
        railing(
            parts,
            (a, south + 0.07),
            (b, south + 0.07),
            top,
            (105, 77, 59),
            spacing=0.22,
            height=0.79,
        )
    for e in (west, east):
        railing(
            parts,
            (e, south + 0.07),
            (e, north - 0.05),
            top,
            (105, 77, 59),
            spacing=0.22,
            height=0.79,
        )
    edge_boxes = [box(a, south + 0.042, b, south + 0.111) for a, b in fences]
    edge_boxes.extend(
        box(e - 0.035, south + 0.07, e + 0.035, north - 0.05) for e in (west, east)
    )
    return [orient(p) for p in edge_boxes]


def marker(parts, row, wall):
    spec = row["marker"]
    edge, point = reference_face(wall, row, spec)
    _, add, _, _ = millrace.basis(parts, *edge.coords)
    u = edge.project(point)
    width, low, high = spec["width"], spec["z"], spec["height"]
    add(u - width / 2, u + width / 2, 0.014, 0.16, low, low + high, (147, 78, 59))
    add(
        u - width / 2 + 0.12,
        u + width / 2 - 0.12,
        0.164,
        0.178,
        low + 0.106,
        low + high - 0.106,
        (58, 74, 88),
    )


def apartment_bands(parts, row, wall):
    for _, (span, add, _, _, _, _) in fairmount.views(parts, wall):
        if span < 5:
            continue
        for z in row["bands"]:
            # The taller portion ends before the step down to the west stair wing.
            if z > 13.8 and span < 11:
                continue
            add(0.05, span - 0.05, 0.007, 0.06, z - 0.040, z + 0.061, row["seam_color"])


def balcony_arch(parts, row, wall):
    spec = row["craftsman"]
    edge, point = reference_face(wall, row, spec)
    _, add, _, plan = millrace.basis(parts, *edge.coords)
    u = edge.project(point)
    depth, width, z = spec["depth"], spec["width"], spec["z"]
    left, right = u - width / 2, u + width / 2
    add(left, right, -0.06, depth, z - 0.20, z, WOOD)
    for a, b in (
        (plan(left, 0), plan(left, depth)),
        (plan(left, depth), plan(right, depth)),
        (plan(right, depth), plan(right, 0)),
    ):
        railing(parts, a, b, z, GREEN, spacing=0.154, height=0.82)
    arch = chapter.arch(u, z + 0.13, 1.54, 2.02, 0.44)
    inner = chapter.arch(u, z + 0.21, 1.30, 1.88, 0.40)
    frontages.heritage.profile(
        parts, *edge.coords, arch.difference(inner), 0.121, GREEN
    )
    frontages.heritage.profile(parts, *edge.coords, inner, 0.099, GLASS)
    add(u - 0.024, u + 0.024, 0.120, 0.152, z + 0.25, z + 1.81, GREEN)
    for x in (u - 1.16, u + 1.16):
        northwest.window_grid(add, x, 0.49, z + 0.60, z + 1.80, 1, 2, GREEN)
        fairmount.beam(
            parts,
            (*plan(x, 0.10), z - 0.80),
            (*plan(x, depth - 0.05), z - 0.17),
            0.091,
            WOOD,
        )


def garage_dormers(parts, row, wall, field):
    edge, point = reference_face(wall, row, row["garage_dormers"])
    _, add, _, plan = millrace.basis(parts, *edge.coords)
    at = edge.project(point)
    for offset in (-1.44, 1.48):
        u = at + offset
        grade = emerald.grade(field, plan(u, 0.08))
        arch = chapter.arch(u, grade + 1.64, 2.04, 0.46, 0.17)
        frontages.heritage.profile(parts, *edge.coords, arch, 0.106, GLASS)
        for x in (u - 0.52, u, u + 0.52):
            add(x - 0.026, x + 0.026, 0.105, 0.132, grade + 1.64, grade + 2.025, GREEN)
        emerald.dormer(parts, add, row, plan, u, 1.89, 13.89, 1.21, 0.62)


def stores(row, field, paving):
    roof, wall = shell(row)
    wall = orient(wall.difference(box(*row["retail_open"])))
    parts = []
    garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    edge, point = reference_face(wall, row, row["retail_panels"])
    span, add, _, plan = millrace.basis(parts, *edge.coords)
    add(0.03, span - 0.03, 0.012, 0.092, 9.78, 10.53, (211, 203, 171))
    add(0.03, span - 0.03, 0.096, 0.145, 10.44, 10.57, (143, 73, 59))
    add(0.03, span - 0.03, 0.093, 0.141, 9.72, 9.83, (143, 73, 59))
    for x in (2.19, 5.70, 8.92, 12.47, 16.39):
        northwest.window_grid(add, x, 1.53, 8.09, 9.56, 2, 1, row["trim_color"])
    gates = []
    for entry in row["retail_gates"]:
        at = edge.project(Point(entry["at"], point.y))
        potter.door(add, at, entry["threshold"], (144, 96, 71))
        gates.append(
            agate.doorway(
                paving,
                row,
                field,
                edge,
                edge.interpolate(at),
                {"route": entry["gate"], "bearing": 180},
            )
        )
    supports = []
    for e in (106.96, 112.54, 117.1, 123.88):
        n = -717.38
        z = emerald.grade(field, (e, n))
        post = orient(box(e - 0.11, n - 0.14, e + 0.11, n + 0.14))
        base.flat(parts, post, z - 0.18, 11.42, (193, 181, 150))
        supports.append(post)
    return agate.output(parts, row, roof, wall, supports, gates)


def gallery(row, field, paving):
    roof, original = shell(row)
    inner, outer, south, north, upper = row["gallery"]
    cut = box(inner, south, roof.bounds[2] + 0.19, north)
    wall = orient(original.difference(cut))
    parts = []
    cap = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    base.flat(
        parts, box(inner - 0.053, south, outer, north), upper - 0.24, upper, CONCRETE
    )
    railing(
        parts, (outer - 0.048, south), (outer - 0.048, north), upper, (217, 215, 186)
    )
    for n in (south, north):
        railing(parts, (inner, n), (outer, n), upper, (217, 215, 186))
    supports = []
    for n in np.linspace(south + 0.18, north - 0.18, 10):
        x = outer - 0.12
        post = orient(box(x - 0.081, n - 0.08, x + 0.081, n + 0.08))
        z = emerald.grade(field, (x, n))
        base.flat(parts, post, z - 0.105, upper - 0.16, (186, 190, 178))
        supports.append(post)
    millrace.western.terrace(
        paving, field, orient(box(inner + 0.025, south, outer + 0.78, north))
    )
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.53:
            continue
        e, n = plan(span / 2, 0)
        on_gallery = normal[0] > 0.98 and abs(e - inner) < 0.06
        if normal[1] < -0.97 and n < -714.0:
            add(0.024, span - 0.024, 0.006, 0.040, 6.37, 12.11, (139, 103, 85))
        for u in (
            (np.arange(max(1, round(span / 3.45))) + 0.5)
            * span
            / max(1, round(span / 3.45))
        ):
            w = min(1.35, span * 0.64)
            for level in row["levels_z_m"]:
                top = min(cap(plan(u, 0)) - 0.24, level + 1.78)
                if top < level + 1.0:
                    continue
                center = u - 0.23 if on_gallery else u
                northwest.window_grid(
                    add, center, w, level + 0.69, top, 2, 1, row["trim_color"]
                )
                if on_gallery and span - u > 1.08:
                    potter.door(add, u + 0.91, level, (95, 113, 120))
    return agate.output(parts, row, roof, wall, supports, [])


def build(row, field, paving):
    if "retail_open" in row:
        return stores(row, field, paving)
    if "gallery" in row:
        return gallery(row, field, paving)
    mesh, record, wall, supports = emerald.build(row, field, paving)
    parts = [mesh]
    if "deck" in row:
        supports.extend(deck(parts, row, field))
        marker(parts, row, wall)
    if "craftsman" in row:
        balcony_arch(parts, row, wall)
        garage_dormers(parts, row, wall, field)
    if "bands" in row:
        apartment_bands(parts, row, wall)
    return agate.output(parts, row, shell(row)[0], wall, supports, record["entrances"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "columbia_moss_frontages_site", build
    )


if __name__ == "__main__":
    main()
