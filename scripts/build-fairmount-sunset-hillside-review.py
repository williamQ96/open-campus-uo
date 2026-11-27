# SPDX-License-Identifier: Apache-2.0
"""Export thirteen hillside exteriors registered around Fairmount and Sunset."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient


hillside = import_module("build-fairmount-summit-hamble-review")
agate, columbia, emerald = hillside.agate, hillside.columbia, hillside.emerald
base, fairmount, garden = hillside.base, hillside.fairmount, hillside.garden
geometry = hillside.geometry
PACKAGE = "fairmount-sunset-hillside-review"
GROUND = "fairmount-sunset-hillside-paving"
FRAME = (220, 215, 196)
GLASS = (66, 93, 98)


def court_paving(paving, spec, field):
    court = Point(spec["center"])
    stone = (165, 161, 142)
    grass = (129, 145, 97)

    def ground(e, n):
        return geometry.sample_ground(field, e, n) + 0.068

    outer = court.buffer(spec["radius"], quad_segs=22)
    lawn = court.buffer(spec["radius"] - 0.94, quad_segs=22)
    west, south, east, north = outer.bounds
    step = field["spacing_m"]
    first_east = (
        field["min_east_m"] + np.floor((west - field["min_east_m"]) / step) * step
    )
    first_north = (
        field["min_north_m"] + np.floor((south - field["min_north_m"]) / step) * step
    )
    ring = outer.difference(lawn)
    # The campus grid uses the corner-to-corner diagonal. Clipping along it
    # keeps the paving above every terrain triangle, including the court center.
    for x in np.arange(first_east, east, step):
        for y in np.arange(first_north, north, step):
            corners = ((x, y), (x + step, y), (x + step, y + step), (x, y + step))
            for chosen in ((0, 1, 2), (0, 2, 3)):
                cell = Polygon([corners[i] for i in chosen])
                for layer, color in ((ring, stone), (lawn, grass)):
                    for patch in geometry.sections(layer.intersection(cell)):
                        if patch.area < 0.0001:
                            continue
                        low = min(ground(*p) for p in patch.exterior.coords) - 0.12
                        surface = geometry.shell(
                            orient(patch), low, ground, color, color
                        )
                        surface.update_faces(surface.face_normals[:, 1] > 0.02)
                        surface.remove_unreferenced_vertices()
                        paving.append(surface)
    feature = court.buffer(1.28, quad_segs=16)
    top = ground(*spec["center"])
    base.flat(paving, orient(feature), top - 0.2, top + 0.34, stone)
    base.flat(
        paving, orient(court.buffer(1.02, quad_segs=16)), top + 0.33, top + 0.37, grass
    )


def collector_banks(parts, roof, height, spec):
    for west, south, east, north in spec["collectors"]:
        for x in np.arange(west, east - 0.86, 1.23):
            for n in np.arange(south, north - 0.65, 1.05):
                footprint = box(x, n, x + 1.13, n + 0.93)
                if not roof.covers(footprint):
                    continue
                z = height((x + 0.57, n + 0.47))
                base.flat(parts, orient(footprint), z + 0.045, z + 0.126, (64, 69, 67))
                base.flat(
                    parts,
                    orient(footprint.buffer(-0.047)),
                    z + 0.126,
                    z + 0.15,
                    (51, 61, 65),
                )


def curved_glazing(parts, row, wall, height):
    spec = row["court"]
    center = np.array(spec["center"])
    floor, ceiling = spec["glass_z"]
    for edge, view in fairmount.views(parts, wall):
        span, add, _, plan, _, _ = view
        if span < 0.28:
            continue
        point = np.array(plan(span / 2, 0))
        facing = np.array(plan(span / 2, 1)) - point
        radial = center - point
        toward_court = np.linalg.norm(radial) < 12 and facing @ radial > 0.46
        toward_veranda = point[0] < 888.2 and facing[0] < -0.32
        if not (toward_court or toward_veranda):
            continue
        top = min(ceiling, height(tuple(point)) - 0.28)
        count = max(1, round(span / 1.45))
        for i in range(count):
            left, right = (
                (i + 0.5) * span / count - 0.45 * span / count,
                (i + 0.5) * span / count + 0.45 * span / count,
            )
            add(left, right, 0.004, 0.047, floor - 0.07, top + 0.06, FRAME)
            add(left + 0.043, right - 0.043, 0.049, 0.054, floor, top, GLASS)
            add(
                left + 0.027,
                right - 0.027,
                0.051,
                0.071,
                floor + 1.10,
                floor + 1.15,
                FRAME,
            )


def carport(row, field, paving):
    roof, main = columbia.shell(row)
    removed = Polygon(row["carport"]["cut"])
    remaining = main.difference(removed)
    wall = orient(max(geometry.sections(remaining), key=lambda polygon: polygon.area))
    parts = []
    height = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    supports, gates = emerald.facades(parts, paving, row, wall, field, height)
    for e, n in row["carport"]["posts"]:
        pad = orient(box(e - 0.11, n - 0.13, e + 0.11, n + 0.13))
        if not roof.covers(pad):
            raise ValueError(f"Carport support outside roof at {e}, {n}.")
        z = emerald.grade(field, (e, n))
        top = height((e, n))
        if top - z < 1.8:
            raise ValueError(f"Insufficient clear height at carport support {e}, {n}.")
        base.flat(parts, pad, z - 0.08, top - 0.12, FRAME)
        supports.append(pad)
    pad = roof.intersection(removed).buffer(-0.13)
    for surface in geometry.sections(pad):
        emerald.millrace.western.terrace(paving, field, orient(surface))
    return agate.output(parts, row, roof, wall, supports, gates)


def build(row, field, paving):
    if "carport" in row:
        return carport(row, field, paving)
    if "court" in row:
        roof, wall = columbia.shell(row)
        parts = []
        height = garden.roof_sections(
            parts, roof, wall, row["base_z_m"], row, grid=0.0002
        )
        curved_glazing(parts, row, wall, height)
        collector_banks(parts, roof, height, row["court"])
        court_paving(paving, row["court"], field)
        return agate.output(parts, row, roof, wall, [], [])
    if row["frontages"] and "bounded_garage" in row["frontages"][0]:
        roof, wall = columbia.shell(row)
        parts = []
        height = garden.roof_sections(
            parts, roof, wall, row["base_z_m"], row, grid=0.0002
        )
        supports, gates = emerald.facades(parts, paving, row, wall, field, height)
        spec = row["frontages"][0]
        _, _, add, _, plan, at = hillside.hill.at_face(parts, wall, row, spec)
        offset, width = spec["bounded_garage"]
        left, right = at + offset - width / 2, at + offset + width / 2
        stations = np.linspace(left, right, 8)
        head = min(height(plan(u, 0)) for u in stations) - 0.22
        ground = max(emerald.grade(field, plan(u, 0)) for u in stations)
        sill = min(ground - 0.12, head - 1.75)
        add(left - 0.065, right + 0.065, 0.004, 0.047, sill, head, (96, 92, 81))
        add(left, right, 0.048, 0.065, sill, head - 0.06, (112, 111, 105))
        for z in np.arange(sill + 0.25, head - 0.08, 0.27):
            add(left, right, 0.066, 0.076, z, z + 0.018, (91, 90, 83))
        return agate.output(parts, row, roof, wall, supports, gates)
    if row.get("vertical_cladding"):
        roof, wall = columbia.shell(row)
        parts = []
        height = garden.roof_sections(
            parts, roof, wall, row["base_z_m"], row, grid=0.0002
        )
        piers, gates = emerald.facades(
            parts, paving, {**row, "seam_color": row["wall_color"]}, wall, field, height
        )
        for edge, view in fairmount.views(parts, wall):
            span, add, _, plan, _, _ = view
            for at in np.arange(0.17, span - 0.11, 0.34):
                p = plan(at, 0)
                z = max(row["base_z_m"] + 0.32, emerald.grade(field, p) + 0.09)
                top = height(p) - 0.25
                if top - z > 0.42:
                    add(at - 0.013, at + 0.013, 0.002, 0.020, z, top, row["seam_color"])
        return agate.output(parts, row, roof, wall, piers, gates)
    return emerald.build(row, field, paving)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "fairmount_sunset_hillside_site", build
    )


if __name__ == "__main__":
    main()
