# SPDX-License-Identifier: Apache-2.0
"""Build the registered East Broadway and Orchard exterior batch."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
from shapely.affinity import affine_transform
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient

path = Path(__file__).with_name("build-franklin-boulevard-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
franklin = module_from_spec(loader)
loader.loader.exec_module(franklin)

houses, chapter, design = franklin.houses, franklin.chapter, franklin.design
base, geometry, approaches = franklin.base, franklin.geometry, franklin.approaches
PACKAGE = "broadway-orchard-exterior-review"
SPEC = houses.ROOT / "data/metadata/broadway-orchard-exterior-review.json"
GLASS = (82, 106, 105)
METAL = (105, 109, 104)
CONCRETE = (148, 145, 131)


def accents(parts, field, row, edges):
    for face in row["accents"]:
        edge = design.locate_face(edges, face["near_enu_m"], face["bearing"])
        span, add, _, point, _, slab = chapter.setup_face(parts, *edge)
        line = LineString(edge)
        grade = geometry.sample_ground(field, *point(span / 2, .04))
        trim = row["trim_color"]
        for a, b, bottom, top, depth, tone in face["bands"]:
            left, right = sorted(line.project(Point(p)) for p in (a, b))
            add(left, right, -.002, depth, grade + bottom, grade + top, tone)
        for points, lower, depth, tone in face["profiles"]:
            edge_profile = [(line.project(Point(p)), grade + z) for p, z in points]
            left, right = edge_profile[0][0], edge_profile[-1][0]
            shape = Polygon([(left, grade + lower), *edge_profile, (right, grade + lower)])
            if not shape.is_valid:
                raise ValueError(f"Invalid fascia profile on {row['id']}.")
            slab(shape, .028, depth, tone)
        for at, size, sill, tone in face["vents"]:
            x = line.project(Point(at))
            z = grade + sill
            points = [(x + size * np.sin(a), z + size * np.cos(a))
                      for a in np.arange(8) * np.pi / 4]
            polygon = Polygon(points)
            slab(polygon, .03, .056, tone)
            slab(polygon.buffer(.047).difference(polygon), .05, .076, trim)
            for y in np.linspace(z - .58 * size, z + .58 * size, 5):
                add(x - size * .59, x + size * .59, .052, .076, y - .009, y + .009, trim)


def upper_storeys(parts, row, height):
    if not row["raised_wall_enu_m"]:
        return
    edges = list(houses.shared.face_edges(orient(Polygon(row["raised_wall_enu_m"]))))
    bottom = row["raised_wall_bottom_z_m"]
    trim = row["trim_color"]
    for face in row["raised_facades"]:
        edge = design.locate_face(edges, face["near_enu_m"], face["bearing"])
        span, add, _, point, _, _ = chapter.setup_face(parts, *edge)
        line = LineString(edge)
        if face["seams"]:
            for x in np.arange(.21, span - .10, face["seams"]):
                top = height(point(x, 0)) - .167
                if top > bottom + .17:
                    add(x, x + .024, -.002, .038, bottom + .13, top, trim)
        add(.02, span - .02, -.007, .084, bottom - .055, bottom + .29, row["wall_color"])
        for at, width, sill, rise, ribs in face["windows"]:
            center = line.project(Point(at))
            width = min(width, 2 * min(center - .065, span - center - .065))
            roof = min(height(point(x, 0)) for x in (center - width/2, center + width/2))
            top = min(bottom + sill + rise, roof - .23)
            if width <= .24 or top <= bottom + sill + .38:
                raise ValueError(f"Upper opening does not fit on {row['id']} at {at}.")
            chapter.prior.window(add, center, width, bottom + sill, top, trim, GLASS, ribs=ribs)


def external_stairs(parts, field, row):
    feet = []
    matrix = franklin.frame(row)
    for start, end, lateral, width, upper, steps in row["external_stairs"]:
        mid = lateral + width / 2
        lower = geometry.sample_ground(field, *affine_transform(Point(start, mid), matrix).coords[0])
        for x0, x1, top in zip(
            np.linspace(start, end, steps + 1)[:-1],
            np.linspace(start, end, steps + 1)[1:],
            np.linspace(lower, upper, steps + 1)[1:],
        ):
            left, right = sorted((x0, x1))
            tread = affine_transform(box(left - .014, lateral, right + .014, lateral + width), matrix)
            base.flat(parts, tread, top - .115, top, CONCRETE)
            for v in (lateral + .04, lateral + width - .04):
                rail = affine_transform(box(left - .028, v - .026, right + .028, v + .026), matrix)
                base.flat(parts, rail, top + .79, top + .869, METAL)
                base.flat(parts, affine_transform(box(left, v - .025, left + .048, v + .025), matrix),
                          top - .035, top + .855, METAL)
        for u in (start + (end - start) * .18, end):
            for v in (lateral + .12, lateral + width - .12):
                at = affine_transform(Point(u, v), matrix).coords[0]
                z = geometry.sample_ground(field, *at)
                top = lower + (upper - lower) * ((u - start) / (end - start))
                feet.append(approaches.supported_post(parts, at, z - .12, top, METAL, .060))
    return feet


def ground_surfaces(parts, field, row):
    matrix = franklin.frame(row)
    for bounds, tone in row["ground_surfaces"]:
        outline = affine_transform(box(*bounds), matrix)

        def grade(e, n):
            return geometry.sample_ground(field, e, n) + .026

        floor = min(grade(*at) for at in outline.exterior.coords) - .17
        parts.append(geometry.shell(outline, floor, grade, tone, tone))


def elevations(parts, field, row, edges, entry, door_edge, door_at, height):
    feet = franklin.elevations(parts, field, row, edges, entry, door_edge, door_at, height)
    accents(parts, field, row, edges)
    upper_storeys(parts, row, height)
    feet.extend(external_stairs(parts, field, row))
    ground_surfaces(parts, field, row)
    return feet


def build(spec, manifest, config, field, graph):
    return houses.build(spec, manifest, config, field, graph, decorate=elevations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    houses.export_review(
        spec_path=SPEC,
        package=PACKAGE,
        key="broadway_orchard_exterior_site",
        ground_node="broadway-orchard-approaches",
        paving_node="broadway-orchard-paving",
        builder=build,
        audit_path=args.audit,
        stage=args.stage,
    )


if __name__ == "__main__":
    main()
