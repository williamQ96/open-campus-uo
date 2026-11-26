# SPDX-License-Identifier: Apache-2.0
"""Export registered Fairmount, Moss and McMorran hillside exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.affinity import rotate, scale
from shapely.geometry import Point, box
from shapely.geometry.polygon import orient


columbia = import_module("build-columbia-moss-frontages-review")
agate, emerald = columbia.agate, columbia.emerald
fairmount, garden, geometry = emerald.fairmount, emerald.garden, emerald.geometry
base, potter, chapter = emerald.base, emerald.potter, emerald.chapter
millrace, northwest = emerald.millrace, emerald.northwest
PACKAGE = "fairmount-moss-slope-review"
GROUND = "fairmount-moss-slope-approaches"
WOOD = (122, 94, 72)
RAIL = (71, 82, 76)
GLASS = (70, 104, 113)


def at_face(parts, wall, row, spec):
    face, point = potter.choose_face(
        wall, {**spec, "gate": row["id"]}, spec.get("minimum", 2.1)
    )
    span, add, normal, plan, _, _ = next(
        view for edge, view in fairmount.views(parts, wall) if face.equals(edge)
    )
    return face, span, add, normal, plan, face.project(point)


def covered_connector(row, field, paving):
    roof, original = columbia.shell(row)
    west, south, east, north = row["connector"]
    clear = box(west, south, east, north)
    wall = original.difference(clear)
    shells = [orient(p) for p in geometry.sections(wall) if p.area > 0.1]
    parts, supports = [], []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    for shell in shells:
        fronts = [
            entry
            for entry in row["frontages"]
            if shell.distance(Point(entry["near"])) < 0.8
        ]
        piers, _ = emerald.facades(
            parts, paving, {**row, "frontages": fronts}, shell, field, height
        )
        supports.extend(piers)
        for entry in fronts:
            if entry.get("upper_gable"):
                _, _, add, _, plan, at = at_face(parts, shell, row, entry)
                northwest.window_grid(
                    add, at, 3.51, 29.43, 31.38, 3, 2, row["trim_color"]
                )
                chapter.gabled_canopy(
                    parts,
                    plan,
                    at,
                    2.29,
                    -0.08,
                    1.12,
                    28.76,
                    0.46,
                    row["roof_color"],
                    row["trim_color"],
                )
    for e, n in row["connector_posts"]:
        post = orient(box(e - 0.085, n - 0.10, e + 0.085, n + 0.10))
        floor = emerald.grade(field, (e, n))
        base.flat(parts, post, floor - 0.10, height((e, n)) - 0.04, row["trim_color"])
        supports.append(post)
    millrace.western.terrace(
        paving, field, orient(box(west - 0.42, south - 0.72, east + 0.10, north + 0.24))
    )
    mesh, record, _, _ = agate.output(parts, row, roof, shells[0], supports, [])
    record["ground_footprints_enu_m"] = [base.ring(shell) for shell in shells]
    return mesh, record, wall, supports


def moss_recess(row, field, paving):
    roof, original = columbia.shell(row)
    west, south, east, north = row["moss_porch"]
    wall = orient(original.difference(box(west - 1.0, south, east, north)))
    parts = []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    # The listing's red door is on the timber side wall, with glazing behind the porch.
    side = {"near": [367.76, north], "bearing": 180, "minimum": 1.12}
    rear = {"near": [east, (south + north) / 2], "bearing": 270}
    trim = row["trim_color"]
    floor = row["levels_z_m"][0]
    faces = [
        {**side, "door": [0.0, floor], "door_color": [142, 53, 44]},
        {**rear, "windows": [[0.68, 1.47, floor + 0.77, floor + 1.94]]},
    ]
    emerald.facades(parts, paving, {**row, "frontages": faces}, wall, field, height)
    _, span, add, _, _, _ = at_face(parts, wall, row, side)
    for at in np.arange(0.08, span - 0.06, 0.15):
        if not span / 2 - 0.51 < at < span / 2 + 0.51:
            add(at - 0.023, at + 0.023, 0.013, 0.041, floor, floor + 2.15, trim)
    base.flat(
        parts,
        orient(box(west - 0.18, south + 0.05, east, north - 0.04)),
        floor - 0.24,
        floor,
        WOOD,
    )
    northwest.stair(
        parts,
        (west - 0.78, (south + north) / 2),
        (west - 0.17, (south + north) / 2),
        emerald.grade(field, (west - 0.78, (south + north) / 2)) + 0.03,
        floor,
        1.52,
        steps=3,
    )
    pier = orient(box(west + 0.16, south + 0.12, west + 0.30, south + 0.27))
    floor_pier = emerald.grade(field, (west + 0.23, south + 0.195))
    base.flat(
        parts,
        pier,
        floor_pier - 0.08,
        height((west + 0.23, south + 0.195)) - 0.18,
        trim,
    )
    return agate.output(parts, row, roof, wall, [pier], [])


def pool_terrace(parts):
    # The oval's long axis is registered to the 2021 county orthophoto.
    center = Point(209.6, -969.5)
    water = rotate(scale(center.buffer(1, quad_segs=25), 5.94, 3.71), 30.0)
    outer = orient(water.buffer(0.94))
    deck_z = 28.72
    base.flat(parts, outer, 26.79, deck_z - 0.24, (130, 123, 102))
    rim = orient(outer.difference(water))
    parts.append(
        geometry.shell(
            rim, deck_z - 0.23, lambda *_: deck_z, (136, 103, 82), (156, 120, 96)
        )
    )
    base.flat(parts, orient(water), deck_z - 0.32, deck_z - 0.13, (77, 141, 160))
    return outer


def lower_and_upper_decks(parts, row, wall, field):
    _, span, add, _, plan, _ = at_face(parts, wall, row, row["pool_side"])
    upper, lower = 34.0, 31.0
    left, right = 0.42, span - 0.44
    add(left, right, -0.03, 1.74, upper - 0.23, upper, WOOD)
    add(left, 6.56, -0.04, 1.97, lower - 0.22, lower, WOOD)
    for x in np.linspace(1.18, span - 1.16, 8):
        northwest.window_grid(add, x, 1.55, upper + 0.16, upper + 1.92, 1, 1, RAIL)
    for x in (1.53, 4.54, 7.59, 10.82, 14.1):
        northwest.window_grid(add, x, 1.54, lower + 0.58, lower + 1.87, 2, 1, RAIL)
    for u, v, depth, level in (
        (left, right, 1.74, upper),
        (left, 2.85, 1.97, lower),
        (4.39, 6.56, 1.97, lower),
    ):
        columbia.railing(parts, plan(u, depth), plan(v, depth), level, RAIL, 0.78)
    for x in (left, right):
        columbia.railing(parts, plan(x, 0.06), plan(x, 1.74), upper, RAIL, 0.32)
    for x in (left, 6.56):
        columbia.railing(parts, plan(x, 0.04), plan(x, 1.97), lower, RAIL, 0.38)
    at = 3.62
    emerald.exterior_stair(parts, field, plan, at, lower, 5.12, 1.42, RAIL)
    supports = []
    for x in (1.12, 5.79, 10.5, 15.4):
        e, n = plan(x, 1.42)
        pier = orient(fairmount.rectangle(plan, x - 0.102, x + 0.102, 1.32, 1.52))
        base.flat(parts, pier, emerald.grade(field, (e, n)) - 0.1, upper - 0.19, RAIL)
        supports.append(pier)
    return supports


def add_arch(parts, row, wall):
    spec = row["arched_window"]
    face, _, _, _, _, at = at_face(parts, wall, row, spec)
    z = spec["z"]
    outer = chapter.arch(at, z, 2.65, 1.79, 0.43)
    pane = chapter.arch(at, z + 0.10, 2.42, 1.62, 0.39)
    relief = columbia.frontages.heritage.profile
    relief(parts, *face.coords, outer.difference(pane), 0.13, row["trim_color"])
    relief(parts, *face.coords, pane, 0.108, GLASS)
    _, add, _, _ = millrace.basis(parts, *face.coords)
    for u in (at - 0.45, at + 0.45):
        add(u - 0.026, u + 0.026, 0.11, 0.148, z + 0.11, z + 1.49, row["trim_color"])


def build(row, field, paving):
    if "connector" in row:
        return covered_connector(row, field, paving)
    if "moss_porch" in row:
        return moss_recess(row, field, paving)
    if "pool_side" in row:
        # The custom north wall carries continuous glazing instead of repeated bay windows.
        row = {
            **row,
            "frontages": [row["pool_side"]],
            "terrain_apron": [row["apron_west"], row["apron_east"], row["apron_south"]],
        }
    mesh, record, wall, supports = emerald.build(row, field, paving)
    parts = [mesh]
    if "arched_window" in row:
        add_arch(parts, row, wall)
    if "pool_side" in row:
        supports.extend(lower_and_upper_decks(parts, row, wall, field))
        supports.append(pool_terrace(parts))
    if "garden_apron" in row:
        millrace.western.terrace(paving, field, orient(box(*row["garden_apron"])))
    if "shutters" in row:
        e, n, low, high = row["shutters"][0]
        _, _, add, _, _, at = at_face(
            parts, wall, row, {"near": [e, n], "bearing": 180}
        )
        for x in (at - 1.36, at + 1.34):
            add(x - 0.16, x + 0.16, 0.072, 0.133, low, high, (82, 95, 95))
    return agate.output(
        parts, row, columbia.shell(row)[0], wall, supports, record["entrances"]
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "fairmount_moss_slope_site", build
    )


if __name__ == "__main__":
    main()
