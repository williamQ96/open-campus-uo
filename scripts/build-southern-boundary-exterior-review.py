# SPDX-License-Identifier: Apache-2.0
"""Export eight surveyed southern boundary exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import split
import trimesh

harris = import_module("build-harris-potter-exterior-review")
potter, frontages = harris.potter, harris.frontages
fairmount, garden = harris.fairmount, harris.garden
base, geometry, millrace = harris.base, harris.geometry, harris.millrace
northwest, chapter = harris.northwest, harris.chapter
PACKAGE = "southern-boundary-exterior-review"
GROUND = "southern-boundary-approaches"
STONE = (155, 144, 121)
IRON = (64, 67, 59)


def garage_panel(add, paving, plan, at, field, spec):
    width, color = spec["width"], spec["color"]
    low = geometry.sample_ground(field, *plan(at, 0.08)) + 0.07
    left, right = at - width / 2, at + width / 2
    add(left - 0.07, right + 0.07, 0.013, 0.082, low - 0.03, low + 2.11, STONE)
    for z in low + 0.02 + np.arange(7) * 0.284:
        add(left, right, 0.083, 0.101, z, z + 0.266, color)
    if spec["bays"] == 2:
        add(at - 0.047, at + 0.047, 0.10, 0.135, low, low + 2.07, STONE)
    if spec.get("windows"):
        for u in np.linspace(left + 0.36, right - 0.36, 8):
            add(u - 0.24, u + 0.24, 0.106, 0.13, low + 1.58, low + 1.96, (73, 95, 104))
    frontages.paved_strip(paving, field, plan, at, width + 0.18, 0, 8.65)


def face_details(parts, row, wall, field, height, entrance, point, paving):
    floor, *upper = row["levels_z_m"]
    trim, seam = row["trim_color"], row["seam_color"]
    garage_faces = [
        (*potter.choose_face(wall, spec), spec) for spec in row.get("garages", [])
    ]
    vent = row.get("vent")
    vent_edge, vent_point = potter.choose_face(wall, vent) if vent else (None, None)
    supports = []
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 0.68:
            continue
        center = edge.project(point) if edge.equals(entrance) else None
        if center is not None:
            supports.extend(
                harris.entry_details(parts, row, field, edge, add, plan, center)
            )
        garage = next((item for item in garage_faces if item[0].equals(edge)), None)
        garage_at = edge.project(garage[1]) if garage else None
        if garage:
            garage_panel(add, paving, plan, garage_at, field, garage[2])
        top = min(height(plan(u, 0)) for u in np.linspace(0.026, span - 0.026, 9))
        millrace.siding(add, span, top - 0.16, floor - 0.6, seam, 0.176)
        if edge.equals(vent_edge):
            pos = edge.project(vent_point)
            ring = Point(pos, vent["z"]).buffer(0.24, quad_segs=8)
            frontages.heritage.profile(parts, *edge.coords, ring, 0.053, trim)
            frontages.heritage.profile(
                parts, *edge.coords, ring.buffer(-0.045), 0.071, IRON
            )
        if span < 1.45 or row.get("rear_volume"):
            continue
        front_windows = center is not None and row.get("front_picture_windows")
        shuttered = row.get("shutters") and normal[0] < -0.92
        count = max(1, round(span / (3.8 if shuttered else row["bay_m"])))
        for at in (np.arange(count) + 0.5) * span / count:
            width = min(
                span / count * 0.68, 1.98 if shuttered or front_windows else 1.37
            )
            ceiling = (
                min(height(plan(u, 0)) for u in (at - width / 2, at, at + width / 2))
                - 0.24
            )
            for index, level in enumerate((floor, *upper)):
                if not index and (
                    (center is not None and abs(at - center) < 1.37)
                    or (garage and abs(at - garage_at) < garage[2]["width"] / 2 + 0.65)
                ):
                    continue
                lo = level + (0.54 if index else 0.68)
                hi = min(lo + 1.29, ceiling)
                grade = geometry.sample_ground(field, *plan(at, 0))
                if hi - lo < 0.38 or lo < grade + 0.10:
                    continue
                northwest.window_grid(
                    add, at, width, lo, hi, 3 if width > 1.65 else 2, 2, trim
                )
                if shuttered:
                    for sign in (-1, 1):
                        u = at + sign * (width / 2 + 0.19)
                        add(
                            u - 0.12,
                            u + 0.12,
                            0.016,
                            0.064,
                            lo - 0.035,
                            hi + 0.036,
                            IRON,
                        )
    return supports


def closed_gate(parts, field, spec):
    e, north, south = spec["e_m"], spec["north_n_m"], spec["south_n_m"]
    mid, width, height = spec["center_n_m"], spec["span_m"], spec["height_m"]
    left, right = mid - width / 2, mid + width / 2
    pale = (176, 162, 131)
    for start, stop in ((south, left), (right, north)):
        for n in np.linspace(start, stop, max(2, round((stop - start) / 0.17))):
            bottom = geometry.sample_ground(field, e, n)
            board = box(e - 0.048, n - 0.071, e + 0.048, n + 0.071)
            base.flat(parts, board, bottom - 0.075, bottom + height, pale)
    bottom = geometry.sample_ground(field, e, mid)
    for n in np.linspace(left + 0.06, right - 0.06, 12):
        base.flat(
            parts,
            box(e - 0.027, n - 0.015, e + 0.03, n + 0.016),
            bottom - 0.05,
            bottom + 1.86,
            IRON,
        )
    for z in (bottom + 0.22, bottom + 1.74):
        fairmount.beam(parts, (e, left, z), (e, right, z), 0.058, IRON)
    for n in (left - 0.10, right + 0.10):
        base.flat(
            parts,
            box(e - 0.14, n - 0.095, e + 0.20, n + 0.095),
            bottom - 0.2,
            bottom + 2.11,
            pale,
        )
    chapter.gabled_canopy(
        parts,
        lambda u, d: np.array([e + d, mid + u]),
        0,
        width / 2 + 0.29,
        -0.54,
        0.57,
        bottom + 1.99,
        0.65,
        (113, 107, 86),
        pale,
    )
    return orient(box(e - 0.13, south, e + 0.13, north))


def harris_retaining(parts, field, point, config):
    e = point.x - config["out_m"]
    endpoints = [config["south_m"]]
    for start, stop in config["breaks_n_m"]:
        endpoints.extend([max(start, config["south_m"]), stop])
    endpoints.append(config["north_m"])
    walls = []
    for start, end in zip(endpoints[::2], endpoints[1::2]):
        if end - start < 0.13:
            continue
        for a, b in zip(
            np.linspace(start, end, 5)[:-1], np.linspace(start, end, 5)[1:]
        ):
            face = orient(box(e - 0.14, a, e + 0.16, b))
            z = min(geometry.sample_ground(field, *p) for p in face.exterior.coords)
            base.flat(
                parts, face, z - 0.09, z + config["rise_m"], (122, 114, 99), STONE
            )
            walls.append(face)
    return walls


def build(row, field, paving):
    outline = orient(
        set_precision(Polygon(row["outline_enu_m"], row["holes_enu_m"]), 0.002)
    )
    wall = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
    parts = []
    height = garden.roof_sections(
        parts, outline, wall, row["base_z_m"], row, grid=0.0002
    )
    entry = row["entry"]
    face, point = potter.choose_face(wall, entry) if entry else (None, None)
    supports = face_details(parts, row, wall, field, height, face, point, paving)
    if "chimney" in row:
        e, n, width, depth, rise, color = row["chimney"]
        z = height((e, n))
        plan = box(e - width / 2, n - depth / 2, e + width / 2, n + depth / 2)
        base.flat(parts, plan, z - 0.24, z + rise, color, STONE)
    if "street_gate" in row:
        supports.append(closed_gate(parts, field, row["street_gate"]))
    if "retaining" in row:
        supports.extend(harris_retaining(paving, field, point, row["retaining"]))
    if "street_landing" in row:
        supports.extend(harris.street_stair(paving, field, face, point, row))
    gates = (
        [
            frontages.estimated_entry(
                paving, {**row, "entry_finish": "stone"}, field, face, point
            )
        ]
        if entry
        else []
    )
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    collision = [wall]
    if wall.interiors:
        north = Polygon(wall.interiors[0]).centroid.y
        cut = LineString([(wall.bounds[0] - 1, north), (wall.bounds[2] + 1, north)])
        collision = list(split(wall, cut).geoms)
        assert all(not segment.interiors for segment in collision)
    record = {
        **{key: row[key] for key in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [
            base.ring(orient(segment)) for segment in collision
        ],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": row["base_z_m"],
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": gates,
    }
    if outline.interiors:
        record["footprint_holes_enu_m"] = [
            list(ring.coords)[:-1] for ring in outline.interiors
        ]
    return mesh, record, wall, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "southern_boundary_exterior_site", build
    )


if __name__ == "__main__":
    main()
