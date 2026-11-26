# SPDX-License-Identifier: Apache-2.0
"""Export the 1800–1850 Millrace Drive research building exterior."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
northwest = import_module("build-northwest-infill-exterior-review")
garden, base, chapter = fairmount.garden, fairmount.base, fairmount.chapter
PACKAGE = "millrace-research-exterior-review"
GROUND = "millrace-research-approach"
BASE = (148, 140, 127)
TRIM = (75, 81, 81)
CASE = (146, 147, 135)
VENT = (99, 107, 104)


def ribbon_windows(parts, row, wall, roof_at):
    entry = np.array(row["entry"]["near"])
    for a, b in northwest.edges(wall, minimum=2.12):
        span, add, normal, plan, _, _ = chapter.setup_face(parts, a, b)
        add(0, span, 0.006, 0.035, -2.13, -1.14, BASE)
        add(0, span, 0.035, 0.085, -1.17, -1.09, row["trim_color"])
        # The long elevations have dark ribbon glazing and a solid panel
        # between groups. Short returns retain solid panels.
        count = round(span / 5.55)
        if not count or span < 4.5:
            continue
        pitch = span / count
        for index in range(count):
            u = pitch * (index + 0.5)
            center = plan(u, 0)
            near_entry = normal[1] > 0.9 and np.linalg.norm(center - entry) < 2.85
            if near_entry:
                continue
            width = min(pitch - 0.64, 4.66)
            top = min(roof_at(plan(u - width / 2, 0)), roof_at(plan(u + width / 2, 0)))
            for sill, head in ((-1.06, 0.43), (1.96, 3.38)):
                if top >= head + 0.51:
                    northwest.window_grid(add, u, width, sill, head, 4, 2, TRIM)


def rooftop_equipment(parts, row, roof_at):
    frame = row["roof_frame"]
    origin = np.array(frame["origin_enu_m"])
    axis = np.array(frame["axis"])
    axis /= np.linalg.norm(axis)
    cross = np.array([-axis[1], axis[0]])

    def world(u, v):
        return origin + u * axis + v * cross

    for u, v, width, depth, height in row["equipment"]:
        corners = [
            world(x, y)
            for x, y in box(
                u - width / 2, v - depth / 2, u + width / 2, v + depth / 2
            ).exterior.coords
        ]
        pad = orient(Polygon(corners))
        z = roof_at(world(u, v))
        base.flat(parts, pad, z - 0.12, z + height, CASE, VENT)
        for a, b in list(garden.shared.face_edges(pad))[:2]:
            span, add, *_ = chapter.setup_face(parts, a, b)
            for y in np.linspace(z + height * 0.27, z + height * 0.72, 4):
                add(span * 0.11, span * 0.89, 0.005, 0.027, y, y + 0.027, VENT)


def build(row, field, paving):
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = orient(outline.buffer(-0.095, join_style="mitre"))
    floor, _ = garden.science.earlier.fit_base(field, wall)
    parts = []
    roof_at = garden.roof_sections(parts, outline, wall, floor, row, grid=0.0002)
    gate, edge, position, supports = fairmount.entrance(parts, row, wall, field, paving)
    ribbon_windows(parts, row, wall, roof_at)
    rooftop_equipment(parts, row, roof_at)
    _, add, _, _ = fairmount.millrace.basis(parts, *edge.coords)
    at = edge.project(position)
    level = gate["threshold_z_m"]
    add(at - 2.03, at + 2.03, -0.08, 1.27, level + 2.57, level + 2.84, TRIM)
    add(at - 2.03, at + 2.03, 1.23, 1.34, level + 2.54, level + 2.65, row["trim_color"])
    northwest.window_grid(add, at - 1.14, 0.63, level + 0.13, level + 2.11, 1, 2, TRIM)
    northwest.window_grid(add, at + 1.14, 0.63, level + 0.13, level + 2.11, 1, 2, TRIM)
    northwest.window_grid(add, at, 1.04, level + 2.15, level + 2.45, 1, 1, TRIM)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{key: row[key] for key in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(wall)],
        "support_collision_enu_m": [base.ring(pier) for pier in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [gate],
    }
    return mesh, record, wall, supports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "millrace_research_exterior_site", build
    )
