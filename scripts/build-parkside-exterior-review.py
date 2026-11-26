# SPDX-License-Identifier: Apache-2.0
"""Build the tiered exterior at 2300 Parkside Lane."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
northwest = import_module("build-northwest-infill-exterior-review")
garden, geometry, base = fairmount.garden, fairmount.geometry, fairmount.base
wood = (138, 97, 73)
decking = (149, 124, 100)
railing = (115, 76, 51)
concrete = (149, 142, 127)
palette = {
    "siding": (121, 113, 99),
    "joints": (105, 98, 86),
    "frame": (92, 80, 69),
}
PACKAGE = "parkside-exterior-review"
GROUND = "parkside-driveway"


def sided_tier(parts, shape, bottom, top):
    base.flat(parts, shape, bottom, top, palette["siding"])
    for _, (span, add, normal, _, _, _) in fairmount.views(parts, shape):
        if span < 0.75:
            continue
        for z in np.arange(bottom + 0.25, top - 0.13, 0.19):
            add(0.016, span - 0.016, 0.006, 0.017, z, z + 0.012, palette["joints"])
        if normal[1] > 0.32 or span < 2.4:
            continue
        for at in np.linspace(span * 0.19, span * 0.81, 3 if span > 5 else 2):
            width = min(span * 0.24, 1.95)
            sill = bottom + (0.18 if normal[1] < -0.78 else 0.59)
            northwest.window_grid(
                add, at, width, sill, top - 0.28, 2, 1, palette["frame"]
            )


def deck(parts, footprint, level, railing_edges):
    base.flat(parts, footprint, level - 0.24, level, wood, decking)
    for line in railing_edges:
        fairmount.balustrade(parts, *line, level, railing)
        fairmount.beam(
            parts, (*line[0], level + 0.79), (*line[1], level + 0.79), 0.077, wood
        )


def post(parts, field, position, top, width=0.17):
    e, n = position
    z = geometry.sample_ground(field, e, n)
    pad = orient(box(e - width / 2, n - width / 2, e + width / 2, n + width / 2))
    if top > z + 0.23:
        base.flat(parts, pad, z - 0.12, top, wood)
        base.flat(
            parts, pad.buffer(0.075, join_style="mitre"), z - 0.08, z + 0.19, concrete
        )
    return pad


def slatted_entry(parts, row, level):
    left, right, north = row["gate_face_enu_m"]
    _, add, _, plan, _, _ = fairmount.chapter.setup_face(
        parts, (right, north), (left, north)
    )
    span = right - left
    for start, stop in ((0, 0.12), (span - 0.12, span)):
        add(start, stop, -0.082, 0.095, level, level + 2.66, wood)
    for z in np.arange(level + 0.18, level + 2.39, 0.153):
        add(0.107, span - 0.107, 0.014, 0.071, z, z + 0.106, railing)
    add(0.04, span - 0.04, -0.075, 0.16, level + 2.48, level + 2.64, wood)
    add(0.21, 0.25, 0.080, 0.126, level + 0.93, level + 1.15, palette["frame"])
    _, door, _, _, _, _ = fairmount.chapter.setup_face(
        parts, plan(0.16, -1.48), plan(span - 0.16, -1.48)
    )
    fairmount.millrace.door(door, (span - 0.32) / 2, level, wood)


def clerestory(parts, row):
    x, n, e, y = row["clerestory_enu_m"]
    frame = orient(box(x, n, e, y))
    sill, top = row["clerestory_levels_m"]
    base.flat(parts, frame, sill - 0.18, top, palette["siding"], row["roof_color"])
    base.flat(
        parts,
        frame.buffer(0.11, join_style="mitre"),
        top - 0.19,
        top,
        palette["frame"],
        row["roof_color"],
    )
    for _, (span, add, normal, _, _, _) in fairmount.views(parts, frame):
        if abs(normal[1]) > 0.93:
            northwest.window_grid(
                add,
                span * 0.5,
                span - 0.79,
                sill + 0.18,
                top - 0.26,
                4,
                1,
                palette["frame"],
            )
    x, n, w, d, top = row["chimney_enu_m"]
    flue = orient(box(x - w / 2, n - d / 2, x + w / 2, n + d / 2))
    base.flat(parts, flue, sill, top, (151, 112, 89), palette["frame"])
    for _, (span, add, _, _, _, _) in fairmount.views(parts, flue):
        for z in np.arange(sill + 0.11, top - 0.095, 0.102):
            add(0.01, span - 0.01, 0.003, 0.009, z, z + 0.012, (128, 100, 82))


def driveway(paving, field, row, level):
    shape = orient(Polygon(row["driveway_enu_m"]))
    lip, tie = row["driveway_grade_north_m"]

    def height(e, n):
        blend = np.clip((n - lip) / (tie - lip), 0, 1)
        return (level - 0.035) * (1 - blend) + (
            geometry.sample_ground(field, e, n) + 0.04
        ) * blend

    stations = np.linspace(lip, tie, 7)
    soffit = level - 3.0
    for start, stop in zip(stations, stations[1:]):
        strip = shape.intersection(box(880, start, 930, stop))
        if strip.area > 0.01:
            slab = geometry.shell(orient(strip), soffit, height, concrete, concrete)
            bottom = np.isclose(slab.vertices[:, 1], soffit, rtol=0, atol=1e-6)
            slab.vertices[bottom, 1] = [
                height(e, -n) - 0.23 for e, _, n in slab.vertices[bottom]
            ]
            paving.append(slab)


def build(row, field, paving):
    outline = orient(Polygon(row["outline_enu_m"]))
    shell = orient(outline.buffer(-0.32, join_style="mitre"))
    upper = orient(shell.difference(box(*row["carport_clearance_enu_m"])))
    middle = orient(Polygon(row["middle_wall_enu_m"]))
    lower = orient(Polygon(row["lower_wall_enu_m"]))
    main, mid, low = row["floor_levels_m"]
    foundation, _ = garden.science.earlier.fit_base(field, lower)
    parts = []
    # The open carport sits beneath the same roof as the house.
    roof_e, roof_n, roof_z, slope_e, slope_n = row["main_roof_plane"]
    parts.append(
        geometry.shell(
            outline,
            main + 2.76,
            lambda e, n: roof_z + (e - roof_e) * slope_e + (n - roof_n) * slope_n,
            palette["frame"],
            row["roof_color"],
        )
    )
    sided_tier(parts, upper, main, main + 2.78)
    sided_tier(parts, middle, mid, main)
    sided_tier(parts, lower, low, mid)
    base.flat(parts, lower, foundation, low, concrete)
    clerestory(parts, row)
    for level, spec in zip((main, mid, low), row["decks"]):
        footprint = orient(Polygon(spec["outline_enu_m"]))
        deck(parts, footprint, level, spec["rails_enu_m"])
    base.flat(
        parts, orient(Polygon(row["carport_slab_enu_m"])), main - 0.28, main, concrete
    )
    for a, b in row["carport_rails_enu_m"]:
        fairmount.balustrade(parts, a, b, main, railing)
    slatted_entry(parts, row, main)
    supports = [
        post(parts, field, position, main + 2.68)
        for position in row["carport_posts_enu_m"]
    ]
    for level, spec in zip((main, mid, low), row["decks"]):
        supports.extend(
            post(parts, field, position, level - 0.18)
            for position in spec["posts_enu_m"]
        )
    driveway(paving, field, row, main)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    solid = orient(unary_union((upper, middle, lower)))
    record = {
        **{key: row[key] for key in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(solid)],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(foundation, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [],
    }
    return mesh, record, solid, supports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "parkside_exterior_site", build
    )
