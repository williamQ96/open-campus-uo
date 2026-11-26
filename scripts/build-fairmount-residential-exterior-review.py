# SPDX-License-Identifier: Apache-2.0
"""Export seven registered Fairmount Boulevard residential exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon

source = Path(__file__).with_name("build-fairmount-boulevard-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
houses = module_from_spec(loader)
loader.loader.exec_module(houses)

PACKAGE = "fairmount-residential-exterior-review"
WOOD = (123, 94, 69)
SOLAR = (53, 66, 77)


def solar_modules(parts, row, height):
    first, south, last, north, columns, rows = row["solar"]
    origin = np.asarray(row["roof_frame"]["origin_enu_m"])
    u = np.asarray(row["roof_frame"]["axis"])
    v = np.array([-u[1], u[0]])
    dx, dy = (last - first) / columns, (north - south) / rows
    for a in first + (np.arange(columns) + .5) * dx:
        for b in south + (np.arange(rows) + .5) * dy:
            corners = [
                origin + (a + i * dx) * u + (b + j * dy) * v
                for i, j in ((-.45, -.45), (.45, -.45), (.45, .45), (-.45, .45))
            ]
            bottom = min(height(p) for p in corners) - .11
            panel = houses.geometry.shell(
                Polygon(corners), bottom, lambda e, n: height((e, n)) + .107,
                (134, 137, 132), SOLAR,
            )
            lower = np.isclose(panel.vertices[:, 1], bottom, atol=1e-6, rtol=0)
            panel.vertices[lower, 1] = [
                height((e, -z)) + .044 for e, _, z in panel.vertices[lower]
            ]
            parts.append(panel)


def balcony(parts, field, edges, row):
    x, y, bearing, width, depth, rise = row["balcony"]
    edge = houses.design.locate_face(edges, [x, y], bearing)
    length, add, _, point, _, _ = houses.chapter.setup_face(parts, *edge)
    center = LineString(edge).project(Point(x, y))
    left = max(.09, center - width / 2)
    right = min(length - .09, center + width / 2)
    grade = max(houses.geometry.sample_ground(field, *point(center, offset)) for offset in (.02, depth))
    platform = grade + rise
    houses.approaches.gallery(add, left, right, depth, platform, WOOD)
    houses.housing.trim_window(add, center + .45, 1.02, platform + .08,
                               platform + 1.86, row["trim_color"])
    for fraction in (.18, .72):
        u = left + (right - left) * fraction
        houses.housing.trim_window(add, u, 1.37, platform + 2.62, platform + 3.45, row["trim_color"])
    feet = []
    for u in (left + .14, right - .14):
        p = point(u, depth - .09)
        floor = houses.geometry.sample_ground(field, *p) - .13
        feet.append(houses.approaches.supported_post(parts, p, floor, platform - .08, WOOD, .075))
    return feet


def elevations(parts, field, row, edges, entry, edge, door_u, height):
    feet = houses.elevations(parts, field, row, edges, entry, edge, door_u, height)
    if row["solar"]:
        solar_modules(parts, row, height)
        length, add, _, point, _, _ = houses.chapter.setup_face(parts, *edge)
        ground = houses.geometry.sample_ground(field, *point(length / 2, 0))
        for index in range(7):
            u = (index + 1) * length / 8
            beam = LineString([point(u, .03), point(u, 2.21)]).buffer(.035, cap_style="flat")
            bottom = min(height(p) for p in beam.exterior.coords) - .31
            parts.append(houses.geometry.shell(beam, bottom, lambda e, n: height((e, n)) - .137, WOOD, WOOD))
        for fraction in (.22, .78):
            u = length * fraction
            start = point(u, .03)
            end = point(u, 2.20)
            top = height(end) - .16
            brace = trimesh.creation.cylinder(.031, segment=[
                [start[0], top - 2.05, -start[1]], [end[0], top, -end[1]],
            ], sections=8)
            brace.visual.vertex_colors = [66, 63, 55, 255]
            parts.append(brace)
        upper = min(height(point(u, 2.01)) for u in (.24, length - .24)) - 2.72
        houses.approaches.gallery(add, .19, length - .19, 1.97, upper, (72, 61, 50))
        for fraction in (.29, .62, .82):
            u = length * fraction
            houses.housing.trim_window(add, u, length * .164, upper + .16, upper + 1.96,
                                       row["trim_color"], ribs=2)
        for fraction in (.3, .62, .83):
            u = length * fraction
            houses.housing.trim_window(add, u, length * .17, ground + 2.61, ground + 3.67,
                                       row["trim_color"], ribs=2)
    if row["balcony"]:
        feet.extend(balcony(parts, field, edges, row))
        style = row["porch"]
        _, _, _, point, _, _ = houses.chapter.setup_face(parts, *edge)
        span = style["width"] / 2
        roof = Polygon([point(u, depth) for u, depth in (
            (door_u - span - .10, -.08), (door_u + span + .10, -.08),
            (door_u + span + .10, 1.12), (door_u - span - .10, 1.12),
        )])
        z = min(height(point(u, .76)) for u in (door_u - span, door_u + span)) + .01
        houses.base.flat(parts, roof, z - .14, z + .025, row["roof_color"])
    if row["street_address"].startswith("1925 "):
        origin = np.asarray(row["roof_frame"]["origin_enu_m"])
        axis = np.asarray(row["roof_frame"]["axis"])
        across = np.array([-axis[1], axis[0]])
        corners = [origin + axis * -3.42 + across * value for value in (-3.0, 2.8)]
        _, add, _, _, _, _ = houses.chapter.setup_face(parts, *corners[::-1])
        for index in range(5):
            houses.housing.trim_window(add, .63 + index * 1.13, .91, 31.43, 32.34,
                                       row["trim_color"], ribs=1)
    if row["street_address"].startswith("2055 "):
        length, add, _, _, _, _ = houses.chapter.setup_face(parts, *edge)
        elevation = entry["threshold_z_m"]
        for u in (max(.06, door_u - .66), min(length - .06, door_u + .66)):
            add(u - .032, u + .032, .04, .97, elevation + .79, elevation + .87, row["trim_color"])
    return feet


def build(spec, manifest, config, field, graph):
    return houses.build(spec, manifest, config, field, graph, decorate=elevations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    houses.export_review(
        spec_path=houses.ROOT / "data/metadata/fairmount-residential-exterior-review.json",
        package=PACKAGE, key="fairmount_residential_exterior_site",
        ground_node="fairmount-residential-approaches", paving_node="fairmount-residential-paving",
        builder=build, audit_path=args.audit, stage=args.stage,
    )


if __name__ == "__main__":
    main()
