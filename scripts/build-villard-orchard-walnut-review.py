# SPDX-License-Identifier: Apache-2.0
"""Build the east neighborhood exteriors and recover two open surfaces."""

import argparse
from importlib import import_module
import json
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient

home = import_module("build-bardell-buckingham-review")
east = import_module("build-east-thirteenth-blocks-review")
agate, fairmount, garden, hilyard, older = (
    home.agate,
    home.fairmount,
    home.garden,
    home.hilyard,
    home.older,
)
geometry = fairmount.geometry
PACKAGE = "villard-orchard-walnut-review"
GROUND = "villard-orchard-walnut-paving"
STEEL = (84, 97, 105)
GLASS = (90, 122, 129)
IVORY = (209, 203, 181)
CONCRETE = (149, 145, 133)
LIGHT = (169, 165, 149)


def drape(parts, field, plan, color, offset, cell=3.0):
    west, south, right, north = plan.bounds

    def top(e, n):
        return hilyard.grade(field, (e, n)) + offset

    # Sample the existing terrain at each small section of the authored surface.
    for x in np.arange(west, right, cell):
        for y in np.arange(south, north, cell):
            area = plan.intersection(box(x, y, x + cell, y + cell))
            for piece in geometry.sections(area):
                if piece.area < 0.002:
                    continue
                low = min(top(*p) for p in piece.exterior.coords) - 0.18
                mesh = geometry.shell(orient(piece), low, top, color, color)
                mesh.update_faces(mesh.face_normals[:, 1] > 0.02)
                mesh.remove_unreferenced_vertices()
                parts.append(mesh)


def open_surfaces(paving, field, specs):
    forecourt = specs["arena_forecourt"]
    drape(paving, field, Polygon(forecourt["polygon_enu_m"]), (169, 163, 144), 0.048)
    for a, b in forecourt["joint_lines_enu_m"]:
        line = LineString([a, b]).buffer(0.025, cap_style="flat")
        drape(paving, field, line, (148, 145, 128), 0.067)
    lots = specs["walnut_parking"]
    drape(paving, field, Polygon(lots["polygon_enu_m"]), (111, 111, 99), 0.049)
    for e, n, w, d in lots["islands_enu_m"]:
        rim = box(e - w / 2, n - d / 2, e + w / 2, n + d / 2).buffer(0.32, quad_segs=3)
        drape(paving, field, rim, (167, 162, 138), 0.099)
        drape(paving, field, rim.buffer(-0.18), (130, 136, 104), 0.121)
    for a, b in lots["striping_enu_m"]:
        strip = LineString([a, b]).buffer(0.055, cap_style="flat")
        drape(paving, field, strip, (180, 164, 109), 0.074)


def supports_for(parts, field, patch, positions, cap, tint):
    supports = []
    for x, y in positions:
        footprint = patch((x - 0.13, y - 0.13, x + 0.13, y + 0.13))
        top = cap((x, y)) if callable(cap) else cap
        hilyard.pier(parts, field, footprint, top, tint)
        supports.append(footprint)
    return supports


def storefront(parts, wall, row, slab, field, world):
    street = slab["street"]
    facing = np.array(hilyard.DIRECTION[street])
    levels, cap = slab["levels"], slab["cap"]
    ground = levels[0]
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 1.15:
            continue
        street_side = normal @ facing > 0.86
        for level in levels[1:]:
            add(
                0.05,
                span - 0.05,
                0.006,
                0.05,
                level - 0.04,
                level + 0.05,
                slab["second_screen"],
            )
        cells = max(1, round(span / 3.25))
        width = min(2.52, span / cells * 0.73)
        for i in range(cells):
            u = (i + 0.5) * span / cells
            for f, level in enumerate(levels[1:]):
                top = min(cap - 0.42, level + 2.19)
                win = width * (0.81 if (i + f) % 3 == 0 else 1.0)
                older.framed(
                    add, u, win, level + 0.64, top, 2 if win < 2.05 else 3, STEEL
                )
                if i % 5 == 1 or (i % 4 == 1 and street_side):
                    nr = min(span - 0.07, u + width / 2 + 0.16)
                    add(
                        nr - 0.22,
                        nr,
                        0.011,
                        0.032,
                        level + 0.14,
                        top + 0.34,
                        slab["accent"],
                    )
        if street_side and span > 7.0:
            sill = max(ground, hilyard.grade(field, plan(span / 2, 0))) + 0.26
            for i in range(max(1, round(span / 2.6))):
                bays = max(1, round(span / 2.6))
                u = (i + 0.5) * span / bays
                w = span / bays * 0.9
                add(u - w / 2, u + w / 2, 0.012, 0.06, sill, levels[1] - 0.43, GLASS)
                add(
                    u - w / 2,
                    u - w / 2 + 0.07,
                    0.062,
                    0.096,
                    sill,
                    levels[1] - 0.42,
                    IVORY,
                )
            add(
                0.08,
                span - 0.08,
                0.026,
                0.71,
                levels[1] - 0.35,
                levels[1] - 0.16,
                STEEL,
            )
        add(0.04, span - 0.04, 0.012, 0.077, cap - 0.26, cap + 0.09, IVORY)


def apartment(row, field, paving, outline, wall, patch, world):
    model = row["block"]
    base_top, roof_top = model["levels"][1], model["cap"]
    parts, supports = [], []
    if "garage" in model:
        parking = wall.intersection(patch(model["garage"]))
        occupied = wall.difference(parking)
        east.flat(parts, occupied, row["base_z_m"], base_top, CONCRETE)
        east.flat(parts, parking, model["beam_height"], base_top, CONCRETE)
        supports.extend(
            supports_for(
                parts, field, patch, model["posts"], model["beam_height"], CONCRETE
            )
        )
    else:
        occupied = wall
        east.flat(parts, wall, row["base_z_m"], base_top, CONCRETE)
    east.flat(parts, wall, base_top, roof_top - 0.19, row["wall_color"])
    east.flat(
        parts, outline, roof_top - 0.18, roof_top, row["trim_color"], row["roof_color"]
    )
    storefront(parts, wall, row, model, field, world)
    older.roof_equipment(parts, row, outline, lambda _: roof_top, patch)
    g = model["gate"]
    position = world(*g)
    gate = dict(
        side=model["street"],
        near=g,
        door=STEEL,
        height=hilyard.grade(field, position) + 0.16,
        gate="street-entry",
        distance=4.04,
    )
    routes = east.entry_gate(
        parts, paving, {**row, "entrance": gate}, wall, field, world
    )
    return agate.output(parts, row, outline, occupied, supports, routes)


def tent(parts, field, patch, world, spec, local):
    left, bottom, right, top, eaves, peak = spec
    x, y = (left + right) / 2, (bottom + top) / 2
    center = world(x, y)
    area = patch((left, bottom, right, top))
    for a, b in zip(area.exterior.coords[:-1], area.exterior.coords[1:]):
        edge = LineString([a, b])
        run = Point(center).distance(edge)

        def crest(e, n):
            return eaves + (peak - eaves) * Point(e, n).distance(edge) / run

        triangle = orient(Polygon([a, b, center]))
        parts.append(
            geometry.shell(triangle, eaves - 0.065, crest, IVORY, (193, 192, 178))
        )
    points = [
        (s, t) for s in (left + 0.20, right - 0.20) for t in (bottom + 0.20, top - 0.20)
    ]
    return supports_for(parts, field, patch, points, eaves, (135, 137, 128))


def build(row, field, paving):
    patch, local, world = older.transforms(row)
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
    if "block" in row:
        return apartment(row, field, paving, outline, wall, patch, world)
    parts, supports = [], []
    cut = row.get("clearance")
    if cut:
        occupied = orient(wall.difference(patch(cut["bounds"])))
    else:
        occupied = wall
    roof = garden.roof_sections(
        parts, outline, occupied, row["base_z_m"], row, grid=0.0002
    )
    views, plan = home.facade(parts, row, occupied, field, world, roof)
    gates = home.registered_approach(parts, paving, row, field, plan, views)
    if cut:
        plan = outline.intersection(patch(cut["bounds"])).buffer(-0.07)
        drape(paving, field, plan, cut["finish"], 0.045)
        supports.extend(
            supports_for(
                parts,
                field,
                patch,
                cut["posts"],
                lambda pos: roof(world(*pos)) - 0.14,
                row["trim_color"],
            )
        )
    if "canopy" in row:
        supports.extend(tent(parts, field, patch, world, row["canopy"], local))
    for s, t in row.get("balconies", []):
        i, u = home.locate(views, row, world, "E", (s, t))
        span, add, _, plan, _, _ = views[i][1]
        lo, hi = max(0.14, u - 1.93), min(span - 0.14, u + 1.93)
        if hi - lo > 1.28:
            z = hilyard.grade(field, plan(u, 0)) + 2.88
            older.balcony(add, lo, hi, z, row["trim_color"])
    older.roof_equipment(parts, row, outline, roof, patch)
    return agate.output(parts, row, outline, occupied, supports, gates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    spec = json.loads((fairmount.ROOT / f"data/metadata/{PACKAGE}.json").read_bytes())

    def recipe(row, field, paving):
        if row["id"] == spec["models"][0]["id"]:
            open_surfaces(paving, field, spec["open_sites"])
        return build(row, field, paving)

    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "villard_orchard_walnut_site", recipe
    )


if __name__ == "__main__":
    main()
