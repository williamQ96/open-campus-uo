# SPDX-License-Identifier: Apache-2.0
"""Export registered Villard, Orchard, Garden and East 17th exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union


slope = import_module("build-fairmount-sunset-hillside-review")
hill = slope.hillside
agate, columbia, emerald = slope.agate, slope.columbia, slope.emerald
base, fairmount, garden, geometry = (
    slope.base,
    slope.fairmount,
    slope.garden,
    slope.geometry,
)
PACKAGE = "villard-orchard-garden-review"
PAVING = "villard-orchard-garden-paving"
FRAME = (200, 195, 177)
GLASS = (70, 94, 100)


def support(parts, polygon, field, top, color):
    lower = min(geometry.sample_ground(field, *xy) for xy in polygon.exterior.coords)
    if lower + 0.12 >= top:
        raise ValueError("The support must start below the modeled underside.")
    base.flat(parts, orient(polygon), lower - 0.22, top, color)


def millrace_building(row, field, paving):
    roof, wall = columbia.shell(row)
    parts = []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    occupied = []
    for limit in row["bridge"]["banks"]:
        bank = Polygon(limit)
        footings = wall.intersection(bank)
        for slab in geometry.sections(footings):
            if slab.area < 0.02:
                continue
            support(parts, slab, field, row["base_z_m"] + 0.02, (144, 145, 130))
            occupied.append(slab)

    for edge, view in fairmount.views(parts, wall):
        span, add, _, _, _, _ = view
        if span < 3.0:
            continue
        for z in (3.30, 5.72, 8.31):
            add(0.04, span - 0.04, 0.008, 0.057, z, z + 0.16, FRAME)
        if span > 13:
            for station in np.arange(1.22, span - 0.92, 2.45):
                for z in (3.70, 6.19):
                    hill.northwest.window_grid(
                        add, station, 1.85, z, z + 1.28, 2, 1, FRAME
                    )
        else:
            hill.northwest.window_grid(
                add, span / 2, min(2.0, span * 0.50), 6.08, 7.5, 2, 1, FRAME
            )
    for e, n, width, length, crest in row["bridge"]["units"]:
        unit = box(e - width / 2, n - length / 2, e + width / 2, n + length / 2)
        pad = roof.buffer(-0.21).intersection(unit)
        for piece in geometry.sections(pad):
            if piece.area < 0.14:
                continue
            top = height((e, n))
            base.flat(parts, orient(piece), top + 0.015, crest, (204, 203, 183))
            for i in (-0.49, 0.49):
                grille = piece.intersection(
                    box(e + i - 0.27, n - 0.27, e + i + 0.27, n + 0.27)
                )
                for item in geometry.sections(grille):
                    if item.area > 0.04:
                        base.flat(
                            parts,
                            orient(item),
                            crest - 0.015,
                            crest + 0.034,
                            (113, 121, 116),
                        )

    approach = orient(
        Polygon(((572.1, 193.1), (578.1, 190.7), (577.8, 189.8), (571.9, 191.89)))
    )
    emerald.millrace.western.terrace(paving, field, approach)
    mesh, record, _, _ = agate.output(parts, row, roof, occupied[0], [], [])
    record["ground_footprints_enu_m"] = [base.ring(orient(bank)) for bank in occupied]
    return mesh, record, unary_union(occupied), []


def garden_shelter(row, field, paving):
    roof, _ = columbia.shell(row)
    bounds = roof.bounds
    empty = Polygon()
    parts, supports = [], []
    floor = row["open_shelter"]["floor"]
    height = garden.roof_sections(parts, roof, empty, floor, row, grid=0.0002)
    stone = (173, 167, 149)
    slab = orient(roof.buffer(-0.05))
    bottom = (
        min(geometry.sample_ground(field, *point) for point in slab.exterior.coords)
        - 0.08
    )
    base.flat(paving, slab, bottom, floor, stone)
    for e, n in row["open_shelter"]["posts"]:
        post = orient(box(e - 0.10, n - 0.10, e + 0.10, n + 0.10))
        top = height((e, n))
        support(parts, post, field, top - 0.15, row["trim_color"])
        supports.append(post)
    w, s, e, n = bounds
    beam_z = min(height(tuple(p.centroid.coords)[0]) for p in supports) - 0.21
    points = [
        (w + 0.34, s + 0.38),
        (e - 0.34, s + 0.38),
        (e - 0.34, n - 0.38),
        (w + 0.34, n - 0.38),
    ]
    for start, end in zip(points, points[1:] + points[:1]):
        fairmount.beam(parts, (*start, beam_z), (*end, beam_z), 0.12, row["trim_color"])
    return agate.output(parts, row, roof, supports[0], supports[1:], [])


def park_side_garage(row, field, paving):
    roof, wall = columbia.shell(row)
    parts = []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    front = row["frontages"][0]
    details = {**front, "garages": []}
    supports, gates = emerald.facades(
        parts, paving, {**row, "frontages": [details]}, wall, field, height
    )
    _, _, add, _, plan, at = hill.hill.at_face(parts, wall, row, details)
    for offset, width in front["garages"]:
        left, right = at + offset - width / 2, at + offset + width / 2
        stations = np.linspace(left, right, 7)
        head = min(height(plan(u, 0)) for u in stations) - 0.21
        ground = max(emerald.grade(field, plan(u, 0)) for u in stations)
        floor = min(ground - 0.12, head - 2.0)
        add(left - 0.09, right + 0.09, 0.002, 0.052, floor, head, FRAME)
        add(left, right, 0.054, 0.069, floor, head - 0.10, front["garage_color"])
        for z in np.arange(floor + 0.32, head - 0.16, 0.30):
            add(left, right, 0.07, 0.076, z, z + 0.019, (125, 132, 118))
        for station in np.linspace(left + 0.37, right - 0.37, 6):
            add(
                station - 0.144,
                station + 0.144,
                0.075,
                0.081,
                head - 0.51,
                head - 0.28,
                GLASS,
            )
    return agate.output(parts, row, roof, wall, supports, gates)


def build(row, field, paving):
    if "bridge" in row:
        return millrace_building(row, field, paving)
    if "open_shelter" in row:
        return garden_shelter(row, field, paving)
    if row.get("bounded"):
        return park_side_garage(row, field, paving)
    return slope.build(row, field, paving)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, PAVING, "villard_orchard_garden_site", build
    )


if __name__ == "__main__":
    main()
