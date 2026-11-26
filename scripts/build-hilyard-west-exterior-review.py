# SPDX-License-Identifier: Apache-2.0
"""Build four street and aerial registered exterior models near Hilyard Street."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
from shapely.affinity import affine_transform
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient


source = Path(__file__).with_name("build-treated-roof-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
treated = module_from_spec(loader)
loader.loader.exec_module(treated)
houses, chapter, design = treated.houses, treated.chapter, treated.design
base, geometry, approaches = treated.base, treated.geometry, treated.approaches
broadway = treated.shared
PACKAGE = "hilyard-west-exterior-review"
WHITE = (222, 216, 193)
GLASS = (81, 101, 101)


def facades(parts, field, row, edges, height):
    matrix = broadway.franklin.frame(row)
    color = row["wall_color"]
    trim = row["trim_color"]
    shade = tuple(max(0, channel - 15) for channel in color)
    upper = (
        list(houses.shared.face_edges(orient(Polygon(row["raised_wall_enu_m"]))))
        if row["raised_wall_enu_m"] else edges
    )
    for face in row["facades"]:
        edge = design.locate_face(upper if face["raised"] else edges,
                                  face["near_enu_m"], face["bearing"])
        span, add, _, point, _, _ = chapter.setup_face(parts, *edge)
        line = LineString(edge)
        grade = row["raised_wall_bottom_z_m"] if face["raised"] else geometry.sample_ground(
            field, *point(span / 2, 0),
        )

        def station(value):
            x, y = face["near"]
            at = Point(value, y) if face["bearing"] in (0, 180) else Point(x, value)
            return line.project(affine_transform(at, matrix))

        treated.finish_wall(add, point, span, grade, height, face["style"], shade)
        for layer, (first, last, bottom, top, tone) in enumerate(face["panels"]):
            left, right = sorted((station(first), station(last)))
            grid = np.linspace(max(.02, left), min(span - .02, right),
                               max(2, int(np.ceil((right - left) / 1.05)) + 1))
            low = grade + bottom
            for a, b in zip(grid[:-1], grid[1:]):
                high = min(grade + top, height(point(a, 0)) - .16, height(point(b, 0)) - .16)
                if b > a + .012 and high > low + .025:
                    add(a, b, .009, .026 + layer * .004, low, high, tone)
        for at, sill, width, rise, ribs in face["windows"]:
            center = station(at)
            if width / 2 + .07 < center < span - width / 2 - .07:
                low = grade + sill
                high = min(low + rise, min(height(point(x, 0))
                           for x in (center - width / 2, center + width / 2)) - .22)
                if high > low + .41:
                    chapter.prior.window(add, center, width, low, high, WHITE, GLASS, ribs=ribs)


def decorate(parts, field, row, edges, entry, door_edge, station, height):
    facades(parts, field, row, edges, height)
    matrix = broadway.franklin.frame(row)
    if row["approach_wall_enu_m"]:
        _, _, _, point, _, _ = chapter.setup_face(parts, *door_edge)
        run = entry["landing_m"]
        top = entry["threshold_z_m"] + .88
        bottom = top - entry["rise_m"] + .12
        for side in (-1, 1):
            u = station + side * (entry["width_m"] / 2 - .035)
            a, b = point(u, .61), point(u, run - .10)
            design.tools.beam(parts, (*a, top), (*b, bottom), .034, (75, 76, 66))
    feet = []
    for point, radius, top in row["supports"]:
        grade = geometry.sample_ground(field, *point)
        if top - grade < 1.8:
            raise ValueError(f"Invalid clearance below the support at {point}.")
        if row["pediment"]:
            foot = Point(point).buffer(radius, quad_segs=6)
            base.flat(parts, foot, grade - .10, top, WHITE)
            base.flat(parts, foot.buffer(.045), grade - .04, grade + .19, WHITE)
            base.flat(parts, foot.buffer(.031), top - .12, top + .05, WHITE)
            feet.append(foot)
        else:
            feet.append(approaches.supported_post(parts, point, grade - .10, top,
                                                  row["trim_color"], radius))

    for kind, bounds, elevation, tone in row["slabs"]:
        region = affine_transform(box(*bounds), matrix)
        if kind == "courtyard":
            region = Polygon(row["roof_holes_enu_m"][0]).buffer(-.10, join_style="mitre")
        if kind == "grade":
            broadway.ground_surfaces(parts, field, row | {
                "ground_surfaces": [[bounds, tone]],
            })
            continue
        if kind == "courtyard":
            grade = geometry.sample_ground(field, *region.centroid.coords[0])
            base.flat(parts, region, grade - .18, grade + elevation, tone)
            continue
        if kind == "gallery":
            x0, y0, x1, y1 = bounds
            front = np.asarray([(x0,y0),(x1,y0)]) @ np.asarray(matrix[:4]).reshape(2,2).T + matrix[4:]
            _, add, _, _, _, _ = chapter.setup_face(parts, *front[::-1])
            # Run the solid balcony skirt along the long façade and leave the western stair open.
            add(.02, x1 - x0 - .06, -.036, .026, elevation - .18, elevation + .79, tone)
        base.flat(parts, region, elevation - .19, elevation, tone)

    if row["pediment"]:
        x0,y0,x1,y1,floor = row["pediment"]
        region = affine_transform(box(x0,y0,x1,y1), matrix)
        parts.append(geometry.shell(region, floor, lambda x,y: height((x,y)) - .11, WHITE, WHITE))
        south = affine_transform(LineString([(x0,y0),(x1,y0)]), matrix)
        _, add, _, _, _, _ = chapter.setup_face(parts, *south.coords)
        center = (x1 - x0) / 2
        add(.025, x1-x0-.025, -.012, .12, floor-.13, floor+.15, WHITE)
        chapter.prior.window(add, center, .60, floor+.41, floor+1.32, WHITE, GLASS, ribs=1)

    for u, v, width, depth, top, tone in row["roof_equipment"]:
        region = affine_transform(box(u - width/2, v - depth/2, u + width/2, v + depth/2), matrix)
        seat = min(height(point) for point in region.exterior.coords) - .12
        if top <= seat + .13:
            raise ValueError(f"Invalid roof equipment on {row['id']} at {(u,v)}.")
        base.flat(parts, region, seat, top, tone)
        base.flat(parts, region.buffer(.048, join_style="mitre"), top - .09, top + .052, WHITE)
        _, add, _, _, _, _ = chapter.setup_face(parts, *list(orient(region).exterior.coords)[:2])
        edge_length = LineString(list(orient(region).exterior.coords)[:2]).length
        for z in np.arange(max(top-.46,seat+.12),top-.10,.093):
            add(.12,edge_length-.12,.007,.029,z,z+.018,(115,120,116))
    return feet


def build(spec, manifest, config, field, graph):
    return houses.build(spec, manifest, config, field, graph, decorate=decorate)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    houses.export_review(
        spec_path=houses.ROOT / "data/metadata/hilyard-west-exterior-review.json",
        package=PACKAGE, key="hilyard_west_exterior_site",
        ground_node="hilyard-west-approaches", paving_node="hilyard-west-paving",
        builder=build, audit_path=args.audit, stage=args.stage,
    )


if __name__ == "__main__":
    main()
