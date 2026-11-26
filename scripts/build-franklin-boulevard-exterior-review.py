# SPDX-License-Identifier: Apache-2.0
"""Export the address-registered Franklin Boulevard commercial exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
from shapely.affinity import affine_transform
from shapely.geometry import LineString, Point, Polygon, box

path = Path(__file__).with_name("build-fairmount-boulevard-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
houses = module_from_spec(loader)
loader.loader.exec_module(houses)

base, chapter, design = houses.base, houses.chapter, houses.design
geometry, approaches = houses.geometry, houses.approaches
PACKAGE = "franklin-boulevard-exterior-review"
SPEC = houses.ROOT / "data/metadata/franklin-boulevard-exterior-review.json"
CONCRETE = (146, 145, 135)
GLASS = (75, 100, 104)
SERVICE_GLASS = (59, 76, 76)


def frame(row):
    east, north = row["roof_frame"]["axis"]
    return [east, -north, north, east, *row["roof_frame"]["origin_enu_m"]]


def finish_roof(parts, field, row, height):
    matrix = frame(row)
    for bounds, top, tone in row["landings"]:
        slab = affine_transform(box(*bounds), matrix)
        bottom = min(geometry.sample_ground(field, *at) for at in slab.exterior.coords) - 0.15
        base.flat(parts, slab, bottom, top, tone)

    for u, v, width, length, top, tone in row["roof_equipment"]:
        plan = affine_transform(
            box(u - width / 2, v - length / 2, u + width / 2, v + length / 2), matrix
        )
        seat = min(height(p) for p in plan.exterior.coords) - 0.10
        if top <= seat + 0.06:
            raise ValueError(f"Roof accessory has no clearance on {row['id']}.")
        base.flat(parts, plan, seat, top, tone)
        base.flat(parts, plan.buffer(0.025, join_style="mitre"), top - 0.05, top + 0.019, tone)

    for bounds, z, slope, columns, rows in row["solar_array"]:
        left, front, right, back = bounds
        across = np.linspace(left, right, columns + 1)
        depth = np.linspace(front, back, rows + 1)
        origin = np.asarray(row["roof_frame"]["origin_enu_m"])
        u, v = np.asarray(matrix[:4]).reshape(2, 2).T

        def top(e, n):
            return z + slope * ((np.asarray([e, n]) - origin) @ v - front)

        under = min(top(*(origin + x * u + y * v)) for x in (left, right) for y in (front, back))
        for l, r in zip(across[:-1], across[1:]):
            for f, b in zip(depth[:-1], depth[1:]):
                p = affine_transform(box(l + 0.025, f + 0.02, r - 0.025, b - 0.02), matrix)
                support = min(height(x) for x in p.exterior.coords) - 0.02
                panel = geometry.shell(p, min(under - 0.06, support), top, (111, 110, 91), (71, 88, 91))
                lower = np.isclose(panel.vertices[:, 1], min(under - 0.06, support), atol=0.00001)
                panel.vertices[lower, 1] = [
                    top(e, -n) - 0.075 for e, _, n in panel.vertices[lower]
                ]
                parts.append(panel)
        for v_support in (front + 0.25, back - 0.20):
            for u_support in across[::2]:
                p = affine_transform(
                    box(u_support - 0.044, v_support - 0.046,
                        u_support + 0.044, v_support + 0.046), matrix
                )
                e, n = p.centroid.coords[0]
                base.flat(parts, p, height((e, n)) - 0.09, top(e, n) - 0.065, (119, 118, 104))


def finish_wall(parts, field, row, edge, face, gate, door_edge, door_at, height):
    span, add, outward, point, _, _ = chapter.setup_face(parts, *edge)
    trim = row["trim_color"]
    line = LineString(edge)
    grade = geometry.sample_ground(field, *point(span / 2, 0.04))
    eave = min(height(point(x, 0)) - 0.15 for x in np.linspace(0.1, span - 0.1, 15))
    lower_band, wall_band, seams = face["wall"]
    add(0.04, span - 0.04, -0.006, 0.039, grade - 0.11, grade + lower_band, CONCRETE)
    for bottom, top, tone in wall_band:
        add(0.035, span - 0.035, 0.001, 0.049, grade + bottom, min(grade + top, eave), tone)
    if seams:
        for x in np.arange(0.17, span - 0.12, seams):
            cap = height(point(x, 0)) - 0.19
            add(x, x + 0.013, 0.038, 0.057, grade + lower_band + 0.02, cap, trim)

    for at, width, sill, rise, ribs in face["windows"]:
        x = float(line.project(Point(at)))
        width = min(width, 2 * min(x - 0.06, span - x - 0.06))
        if width <= 0.28:
            raise ValueError(f"Window falls outside its wall on {row['id']} at {at}.")
        floor = geometry.sample_ground(field, *point(x, 0.07))
        cap = min(height(point(t, 0)) for t in (x - width / 2, x + width / 2)) - 0.26
        chapter.prior.window(
            add, x, width, floor + sill, min(cap, floor + sill + rise), trim, GLASS, ribs=ribs
        )

    for at, width, rise in face["service_bays"]:
        x = float(line.project(Point(at)))
        floor = geometry.sample_ground(field, *point(x, 0.08)) + 0.015
        lo, hi = x - width / 2, x + width / 2
        add(lo - 0.083, hi + 0.083, -0.014, 0.081, floor, floor + rise + 0.09, trim)
        add(lo, hi, 0.077, 0.105, floor + 0.045, floor + rise, SERVICE_GLASS)
        for z in np.linspace(floor + 0.40, floor + rise - 0.14, 5):
            add(lo + 0.03, hi - 0.03, 0.102, 0.126, z, z + 0.039, trim)
        for u in np.linspace(lo + 0.07, hi - 0.07, 5):
            add(u - 0.02, u + 0.02, 0.102, 0.126, floor + 0.35, floor + rise, trim)

    if edge == door_edge and face["glazed_door"]:
        sill = gate["threshold_z_m"]
        chapter.prior.window(add, door_at, 0.985, sill + 0.12, sill + 2.03, trim, GLASS, ribs=1)
        add(door_at - 0.39, door_at + 0.39, 0.09, 0.156, sill + 1.01, sill + 1.06, trim)

    feet = []
    for start, end, depth, height_at_edge, color in face["sloped_fascias"]:
        left, right = sorted(line.project(Point(at)) for at in (start, end))
        sill = grade + height_at_edge
        eave_top = height(point((left + right) / 2, 0)) - 0.025
        start_point = point(left, 0)
        slope = (eave_top - sill - 0.13) / depth
        plan = Polygon([point(x, d) for x, d in (
            (left, -0.035), (right, -0.035), (right, depth), (left, depth)
        )])

        def top(e, n):
            return eave_top - ((e, n) - start_point) @ outward * slope

        parts.append(geometry.shell(plan, sill, top, color, color))
        add(left, right, depth - 0.085, depth + 0.024, sill - 0.06, sill + 0.09, trim)

    for bounds, head, rise, color, band in face["awnings"]:
        left, right = sorted(line.project(Point(at)) for at in bounds[:2])
        depth = bounds[2]
        z = grade + head
        if rise:
            outline = Polygon([point(x, d) for x, d in (
                (left, -0.04), (right, -0.04), (right, depth), (left, depth),
            )])

            def top(e, n):
                return z + max(0.0, depth - outward @ (np.array([e, n]) - point(left, 0))) * rise / depth

            parts.append(geometry.shell(outline, z - 0.11, top, color, color))
        else:
            add(left, right, -0.035, depth, z - 0.11, z, color)
        if band:
            for x in np.linspace(left + 0.3, right - 0.3, band):
                add(x - 0.045, x + 0.045, depth - 0.022, depth + 0.015,
                    z - 0.095, z - 0.012, trim)

    for at, depth, radius, tone, top in face["piers"]:
        e, n = point(line.project(Point(at)), depth)
        z = geometry.sample_ground(field, e, n)
        head = height((e, n)) - 0.15 if top is None else top
        feet.append(approaches.supported_post(parts, (e, n), z - 0.14, head, tone, radius))
    return feet


def elevations(parts, field, row, edges, gate, door_edge, door_at, height):
    feet = []
    for face in row["facades"]:
        edge = design.locate_face(edges, face["near_enu_m"], face["bearing"])
        feet.extend(finish_wall(parts, field, row, edge, face, gate, door_edge, door_at, height))

    matrix = frame(row)
    for local, half, head, tone in row["canopy_columns"]:
        p = affine_transform(Point(local), matrix).coords[0]
        z = geometry.sample_ground(field, *p)
        feet.append(approaches.supported_post(parts, p, z - 0.16, head, tone, half))

    outline = Polygon(row["roof_outline_enu_m"])
    for bounds, width, bottom, top, tone in row["perimeter_fascias"]:
        section = outline.difference(outline.buffer(-width, join_style="mitre"))
        section = section.intersection(affine_transform(box(*bounds), matrix))
        base.flat(parts, section, bottom, top, tone)

    finish_roof(parts, field, row, height)
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
        key="franklin_boulevard_exterior_site",
        ground_node="franklin-boulevard-approaches",
        paving_node="franklin-boulevard-paving",
        builder=build,
        audit_path=args.audit,
        stage=args.stage,
    )


if __name__ == "__main__":
    main()
