# SPDX-License-Identifier: Apache-2.0
"""Rebuild six exteriors previously represented by context roof treatments."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
from shapely.affinity import affine_transform
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient

path = Path(__file__).with_name("build-broadway-orchard-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)
houses, chapter, design = shared.houses, shared.chapter, shared.design
base, geometry, approaches = shared.base, shared.geometry, shared.approaches
PACKAGE = "treated-roof-exterior-review"
GLASS = (86, 109, 106)
SHAKE = (116, 79, 54)
CONCRETE = (157, 153, 135)


def finish_wall(add, position, span, grade, roof, style, tone):
    if style == "vertical":
        for u in np.arange(.18, span - .10, .43):
            top = roof(position(u, 0)) - .18
            if top > grade + .26:
                add(u, u + .022, -.001, .018, grade + .18, top, tone)
        return
    if style == "plain":
        return
    # Trim masonry and siding courses at the sloping eave.
    course = .145 if style == "brick" else .193
    start = grade + 2.44 if style == "shake" else grade + .20
    u = np.linspace(.025, span - .025, max(8, round(span / .32)))
    tops = np.array([roof(position(x, 0)) - .17 for x in u])
    for z in np.arange(start, max(tops), course):
        width = .015
        if style == "shake":
            width = course - .011
        full = np.flatnonzero(tops > z + width)
        for run in np.split(full, np.flatnonzero(np.diff(full) > 1) + 1):
            if len(run) > 1:
                add(u[run[0]], u[run[-1]], .001, .018, z, z + width,
                    SHAKE if style == "shake" else tone)


def facade_details(parts, field, row, edges, height):
    matrix = shared.franklin.frame(row)
    trim, wall = row["trim_color"], row["wall_color"]
    tone = tuple(max(0, component - 15) for component in wall)
    upper = (
        list(houses.shared.face_edges(orient(Polygon(row["raised_wall_enu_m"]))))
        if row["raised_wall_enu_m"] else edges
    )
    for facade in row["facades"]:
        edge = design.locate_face(upper if facade["raised"] else edges, facade["near_enu_m"], facade["bearing"])
        span, add, _, position, _, _ = chapter.setup_face(parts, *edge)
        line = LineString(edge)
        ground = geometry.sample_ground(field, *position(span / 2, 0))
        grade = row["raised_wall_bottom_z_m"] if facade["raised"] else ground
        along_u = facade["bearing"] in (0, 180)

        def station(value):
            x, y = facade["near"]
            target = affine_transform(Point(value, y) if along_u else Point(x, value), matrix)
            return line.project(target)

        finish_wall(add, position, span, grade, height, facade["style"], tone)
        if facade["raised"]:
            add(.03, span - .03, .002, .066, grade - .035, grade + .245, trim)
        for left, right, bottom, top in facade["bands"]:
            a, b = sorted((station(left), station(right)))
            if b - a > .18:
                add(max(.045, a), min(span - .04, b), -.003, .061,
                    grade + bottom, grade + top, trim)
        for at, sill, width, rise, ribs in facade["windows"]:
            center = station(at)
            if not width / 2 + .08 < center < span - width / 2 - .08:
                continue
            low = grade + sill
            high = min(low + rise, min(height(position(x, 0))
                       for x in (center - width / 2, center + width / 2)) - .205)
            if high > low + .35:
                chapter.prior.window(add, center, width, low, high, trim, GLASS, ribs=ribs)


def entrances_and_supports(parts, field, row, edges, entry, door_edge, door_at, height):
    facade_details(parts, field, row, edges, height)
    if row["garage"]:
        point, bearing, width = row["garage"]
        edge = design.locate_face(edges, point, bearing)
        span, add, _, position, _, _ = chapter.setup_face(parts, *edge)
        center = np.clip(LineString(edge).project(Point(point)), width / 2 + .11, span - width / 2 - .11)
        grade = geometry.sample_ground(field, *position(center, .1))
        houses.housing.garage_front(add, center, width, grade + .03, (193, 187, 169), row["trim_color"])

    feet = []
    for point, radius, top in row["supports"]:
        grade = geometry.sample_ground(field, *point)
        ceiling = top if top is not None else height(point) - .12
        if ceiling <= grade + 1.65:
            raise ValueError(f"Insufficient covered clearance on {row['id']} at {point}.")
        feet.append(approaches.supported_post(parts, point, grade - .15, ceiling, row["trim_color"], radius))

    matrix = shared.franklin.frame(row)
    for kind, a, b, c, d, rise in row["canopies"]:
        floor = affine_transform(box(a, b, c, d), matrix)
        z = geometry.sample_ground(field, *floor.centroid.coords[0]) + rise
        base.flat(parts, floor, z - .19, z, row["trim_color"])
        for x in (a + .14, c - .14):
            p = affine_transform(Point(x, b + .14 if kind == "landing" else d - .14), matrix)
            grade = geometry.sample_ground(field, *p.coords[0])
            feet.append(approaches.supported_post(parts, p.coords[0], grade - .11, z - .13, row["trim_color"], .075))
        if kind == "landing":
            # The outer guard spans the alley-facing edge of the upper gallery.
            _, add, _, _, _, _ = chapter.setup_face(parts, *[
                affine_transform(Point(x, b + .04), matrix).coords[0] for x in (a, c)
            ])
            approaches.gallery(add, .02, c - a - .02, .08, z, row["trim_color"])

    shared.ground_surfaces(parts, field, row | {
        "ground_surfaces":[[area, CONCRETE] for area in row["ground_surfaces"]]
    })
    return feet


def build(spec, manifest, config, field, graph):
    return houses.build(spec, manifest, config, field, graph, decorate=entrances_and_supports)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    houses.export_review(
        spec_path=houses.ROOT / "data/metadata/treated-roof-exterior-review.json",
        package=PACKAGE, key="treated_roof_exterior_site",
        ground_node="treated-roof-approaches", paving_node="treated-roof-paving",
        builder=build, audit_path=args.audit, stage=args.stage,
    )


if __name__ == "__main__":
    main()
