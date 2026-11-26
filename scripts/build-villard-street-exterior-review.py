# SPDX-License-Identifier: Apache-2.0
"""Export six source-registered Villard Street exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box

path = Path(__file__).with_name("build-fairmount-boulevard-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
houses = module_from_spec(loader)
loader.loader.exec_module(houses)

base, geometry, chapter = houses.base, houses.geometry, houses.chapter
design, housing, approaches = houses.design, houses.housing, houses.approaches
PACKAGE = "villard-street-exterior-review"
SPEC = houses.ROOT / "data/metadata/villard-street-exterior-review.json"


def shop(parts, field, row, edges, door_edge, door_u, height):
    cream, bronze = row["wall_color"], row["trim_color"]
    for edge in edges:
        span, add, outward, point, _, _ = chapter.setup_face(parts, *edge)
        floors = [
            geometry.sample_ground(field, *point(u, 0)) for u in (0.04, span - 0.04)
        ]
        grade = max(floors)
        eave = min(height(point(u, 0)) for u in (0.04, span - 0.04)) - 0.15
        add(
            0.02, span - 0.02, 0.004, 0.089, grade + 0.09, grade + 0.55, (145, 141, 114)
        )
        if outward[0] < -0.92:
            add(0.05, span - 0.05, 0.006, 0.124, grade + 0.59, eave, (83, 76, 65))
            for u in np.arange(0.10, span - 0.08, 0.16):
                add(u, u + 0.063, 0.123, 0.19, grade + 0.61, eave - 0.15, bronze)
            add(0.023, span - 0.023, 0.025, 0.216, eave - 0.15, eave + 0.015, bronze)
        if edge == door_edge:
            for shift, width in ((-3.38, 2.01), (2.39, 1.32), (5.62, 1.25)):
                u = door_u + shift
                housing.trim_window(
                    add, u, width, grade + 1.02, grade + 2.57, bronze, ribs=2
                )
            add(
                door_u - 0.91,
                door_u + 0.91,
                -0.005,
                0.54,
                grade + 2.90,
                grade + 3.13,
                cream,
            )
        if outward[0] > 0.92:
            housing.trim_window(
                add, span * 0.49, 1.16, grade + 0.62, grade + 2.37, bronze, ribs=3
            )

    outline = Polygon(row["roof_outline_enu_m"])
    e, n = row["roof_frame"]["origin_enu_m"]
    main = outline.intersection(box(e - 7.31, n - 5.47, e + 13.70, n + 5.55))
    base.flat(parts, main.difference(main.buffer(-0.15)), 8.77, 9.56, cream)
    for x, y, long, wide, top in (
        (-2.8, 2.1, 1.10, 0.86, 10.26),
        (1.8, -0.55, 1.14, 0.81, 9.79),
        (6.7, -2.65, 1.62, 0.84, 9.92),
    ):
        casing = box(
            e + x - long / 2, n + y - wide / 2, e + x + long / 2, n + y + wide / 2
        )
        base.flat(parts, casing, 8.76, top, (155, 153, 138))
        base.flat(
            parts,
            casing.buffer(0.042, join_style="mitre"),
            top - 0.07,
            top + 0.025,
            bronze,
        )
    return []


def porch_front(parts, row, gate, edge, center, height):
    width, add, _, point, _, _ = chapter.setup_face(parts, *edge)
    trim = row["trim_color"]
    depth = row["porch"]["depth"]
    threshold = gate["threshold_z_m"]
    half = min(row["porch"]["width"] / 2, center - 0.08, width - center - 0.08)
    for left, right in (
        (center - half + 0.10, center - 0.72),
        (center + 0.72, center + half - 0.10),
    ):
        design.neighbor.railing(add, left, right, depth - 0.16, threshold, trim)
    posts = []
    if row["profile"] in ("full-porch", "cross-porch"):
        head = threshold + 2.33
        front = depth - 0.038
        add(
            center - half,
            center + half,
            front - 0.08,
            front + 0.09,
            head - 0.16,
            head,
            trim,
        )
        ridge = center if row["profile"] == "full-porch" else center - 1.14
        for left, right in ((center - half, ridge), (ridge, center + half)):
            profile = Polygon(
                [
                    point(x, offset)
                    for x, offset in (
                        (left, front - 0.072),
                        (right, front - 0.072),
                        (right, front + 0.04),
                        (left, front + 0.04),
                    )
                ]
            )
            parts.append(
                geometry.shell(
                    profile,
                    head,
                    lambda e, n: max(head + 0.03, height((e, n)) - 0.15),
                    row["wall_color"],
                    row["wall_color"],
                )
            )
        if row["profile"] == "full-porch":

            def face(left, right, start, end, bottom, top, shade):
                add(
                    left,
                    right,
                    front + start + 0.044,
                    front + end + 0.044,
                    bottom,
                    top,
                    shade,
                )

            housing.trim_window(
                face, center, 1.22, threshold + 3.32, threshold + 4.18, trim, ribs=2
            )
    if row["profile"] == "full-porch":
        for x in (center - 0.77, center + 0.77):
            at = point(x, depth - 0.31)
            head = height(at) - 0.15
            posts.append(
                approaches.supported_post(
                    parts, at, threshold - 0.03, head, trim, 0.074
                )
            )
    return posts


def facade_features(parts, field, row, edges, height):
    trim = row["trim_color"]
    for kind, near, heading, relative_sill, width, tall in row["features"]:
        edge = design.locate_face(edges, near, heading)
        span, add, _, point, _, _ = chapter.setup_face(parts, *edge)
        width = min(width, span - 0.24)
        u = np.clip(
            LineString(edge).project(Point(near)),
            width / 2 + 0.11,
            span - width / 2 - 0.11,
        )
        grade = geometry.sample_ground(field, *point(u, 0.10))
        sill = grade + relative_sill
        cap = min(height(point(x, 0)) for x in (u - width / 2, u + width / 2)) - 0.25
        if kind == "garage":
            for x in np.arange(0.09, span - 0.10, 0.28):
                if x < u - width / 2 or x >= u + width / 2:
                    continue
                top = height(point(x, 0)) - 0.19
                if top > grade + 3.03:
                    add(x, x + 0.013, 0.002, 0.024, grade + 2.98, top, trim)
            if cap - sill < 2.12:
                raise ValueError(f"Garage header above eave for {row['id']}.")
            housing.garage_front(add, u, width, sill + 0.035, (147, 155, 151), trim)
        else:
            if kind == "vent":
                sill = min(sill, cap - tall)
            head = min(sill + tall, cap)
            if head - sill < 0.365:
                raise ValueError(f"Opening does not fit {row['id']} at {near}.")
            housing.trim_window(
                add,
                u,
                width,
                sill,
                head,
                trim,
                ribs=3 if kind == "vent" or width > 1.8 else 1,
            )


def elevations(parts, field, row, edges, gate, edge, center, height):
    if row["profile"] == "shop":
        return shop(parts, field, row, edges, edge, center, height)
    feature_edges = [
        design.locate_face(edges, near, heading)
        for _, near, heading, *_ in row["features"]
    ]
    feet = houses.elevations(
        parts, field, row, edges, gate, edge, center, height, windowless=feature_edges
    )
    facade_features(parts, field, row, edges, height)
    if row["porch"]["kind"] == "eave":
        feet.extend(porch_front(parts, row, gate, edge, center, height))
    return feet


def build(spec, manifest, configuration, heightfield, graph):
    return houses.build(
        spec, manifest, configuration, heightfield, graph, decorate=elevations
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    houses.export_review(
        spec_path=SPEC,
        package=PACKAGE,
        key="villard_street_exterior_site",
        ground_node="villard-street-approaches",
        paving_node="villard-street-paving",
        builder=build,
        audit_path=args.audit,
        stage=args.stage,
    )


if __name__ == "__main__":
    main()
