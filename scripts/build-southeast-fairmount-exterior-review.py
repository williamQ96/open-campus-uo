# SPDX-License-Identifier: Apache-2.0
"""Build the Sunset, Rose and Birch hillside residential exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.affinity import affine_transform
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
base, garden, geometry = fairmount.base, fairmount.garden, fairmount.geometry
chapter, millrace = fairmount.chapter, fairmount.millrace
beam = fairmount.beam
PACKAGE = "southeast-fairmount-exterior-review"
GROUND = "southeast-fairmount-approaches"
GLASS = (65, 91, 95)
WOOD = (128, 100, 76)


def world_frame(row):
    origin = np.asarray(row["roof_frame"]["origin_enu_m"])
    along = np.asarray(row["roof_frame"]["axis"], dtype=float)
    along /= np.linalg.norm(along)
    across = np.array([-along[1], along[0]])
    return [along[0], across[0], along[1], across[1], *origin]


def face(parts, wall, spec):
    edges = list(garden.shared.face_edges(wall))
    edge = garden.locate_face(edges, spec["near"], spec["bearing"])
    width, add, normal, plan, _, _ = chapter.setup_face(parts, *edge)
    u = LineString(edge).project(Point(spec["near"]))
    return width, add, normal, plan, u


def garage(parts, wall, spec, trim, field, roof_at):
    width, add, _, plan, u = face(parts, wall, spec)
    half = min(spec["width"] / 2, width / 2 - 0.16)
    u = float(np.clip(u, half + 0.12, width - half - 0.12))
    sill = geometry.sample_ground(field, *plan(u, 0))
    eave = min(roof_at(plan(at, 0)) for at in (u - half, u + half))
    header = min(sill + 2.35, eave - 0.20)
    assert header - sill > 1.50, spec["near"]
    add(u - half - 0.09, u + half + 0.09, 0.012, 0.069, sill, header, trim)
    add(u - half, u + half, 0.073, 0.100, sill + 0.08, header - 0.12, spec["color"])
    for top in np.linspace(sill + 0.41, header - 0.28, 5):
        add(u - half, u + half, 0.100, 0.108, top, top + 0.022, trim)


def glazing(parts, wall, spec, trim, roof_at):
    width, add, _, plan, u = face(parts, wall, spec)
    half = min(spec["width"] / 2, u - 0.15, width - u - 0.15)
    bottom = spec["sill"]
    transom = bottom + 2.05
    dividers = np.linspace(u - half, u + half, spec["panels"] + 1)
    add(u - half, u + half, 0.042, 0.13, bottom, bottom + 0.10, trim)
    add(u - half, u + half, 0.042, 0.13, transom - 0.08, transom + 0.04, trim)
    for left, right in zip(dividers, dividers[1:]):
        cap = min(roof_at(plan(left, 0)), roof_at(plan(right, 0))) - 0.25
        add(left + 0.04, right - 0.04, 0.055, 0.077, bottom + 0.09, cap, GLASS)
        add(left, right, 0.065, 0.126, cap - 0.08, cap + 0.035, trim)
    for divider in dividers:
        cap = roof_at(plan(divider, 0)) - 0.23
        add(divider - 0.045, divider + 0.045, 0.073, 0.135, bottom, cap, trim)
    door = u + spec["door_offset"]
    millrace.door(add, door, bottom, trim)
    return plan, door


def sloped_walk(parts, plan, u, detail, field):
    upper = detail["sill"]
    reach = detail["walk_length"]
    lower = geometry.sample_ground(field, *plan(u, reach)) + 0.05
    area = fairmount.rectangle(plan, u - 0.58, u + 0.58, 0.001, reach)
    inner, outer = plan(u, 0), plan(u, reach)
    slope = (outer - inner) * ((lower - upper) / reach**2)
    ramp = geometry.shell(
        area,
        min(lower, upper) - 0.15,
        lambda e, n: upper + ([e, n] - inner) @ slope,
        WOOD,
        (116, 98, 79),
    )
    parts.append(ramp)
    for side in (-1, 1):
        anchors = []
        for distance in np.linspace(0.08, reach - 0.10, 6):
            x, n = plan(u + side * 0.55, distance)
            h = upper + distance / reach * (lower - upper)
            beam(parts, (x, n, h - 0.10), (x, n, h + 0.83), 0.053, WOOD)
            anchors.append((x, n, h + 0.81))
        for a, b in zip(anchors, anchors[1:]):
            beam(parts, a, b, 0.058, WOOD)


def balcony(parts, wall, spec, field, roof_at, trim):
    width, add, _, plan, u = face(parts, wall, spec)
    a, b = max(0.15, u - spec["width"] / 2), min(width - 0.16, u + spec["width"] / 2)
    level, depth = spec["floor"], spec["depth"]
    deck = fairmount.rectangle(plan, a, b, 0.006, depth)
    base.flat(parts, deck, level - 0.22, level, WOOD, (137, 112, 87))
    fairmount.balustrade(
        parts, plan(a, depth - 0.05), plan(b, depth - 0.05), level, WOOD
    )
    for edge in (a, b):
        fairmount.balustrade(
            parts, plan(edge, 0.035), plan(edge, depth - 0.05), level, WOOD
        )
    piers = []
    for pos in np.linspace(a + 0.16, b - 0.16, 4):
        e, n = plan(pos, depth - 0.13)
        bottom = geometry.sample_ground(field, e, n)
        pier = box(e - 0.052, n - 0.052, e + 0.052, n + 0.052)
        base.flat(parts, pier, bottom - 0.075, roof_at((e, n)) - 0.16, trim)
        piers.append(pier)
    for pos in np.linspace(a + 0.73, b - 0.73, 7):
        millrace.window(
            add, pos, min((b - a) / 7 - 0.09, 0.96), level + 0.86, 1.12, trim
        )
    return piers


def solar_array(parts, row, roof_at, bounds):
    left, bottom, right, top = bounds
    transform = world_frame(row)
    for a, b in zip(np.linspace(left, right, 4), np.linspace(left, right, 4)[1:]):
        for c, d in zip(np.linspace(bottom, top, 9), np.linspace(bottom, top, 9)[1:]):
            area = affine_transform(
                box(a + 0.034, c + 0.04, b - 0.034, d - 0.04), transform
            )
            lower = min(roof_at(p) for p in area.exterior.coords) - 0.02
            parts.append(
                geometry.shell(
                    area,
                    lower,
                    lambda e, n: roof_at((e, n)) + 0.07,
                    (86, 91, 86),
                    (54, 68, 82),
                )
            )


def build(row, field, paving):
    outline = orient(Polygon(row["outline_enu_m"]))
    assert outline.is_valid, row["id"]
    wall = outline.buffer(-0.135, join_style="mitre")
    if "open_bay" in row:
        wall = wall.difference(
            affine_transform(box(*row["open_bay"]), world_frame(row))
        )
    wall = orient(wall)
    assert wall.geom_type == "Polygon", row["id"]
    floor, _ = garden.science.earlier.fit_base(field, wall)
    parts = []
    roof_at = garden.roof_sections(parts, outline, wall, floor, row, grid=0.0002)
    gate, edge, point, piers = fairmount.entrance(parts, row, wall, field, paving)
    fairmount.facade(parts, row, wall, field, roof_at, edge, point)
    trim = row["trim_color"]
    for detail in row["facade_details"]:
        kind = detail["kind"]
        if kind == "garage":
            garage(parts, wall, detail, trim, field, roof_at)
        elif kind == "glazing":
            plan, door = glazing(parts, wall, detail, trim, roof_at)
            sloped_walk(parts, plan, door, detail, field)
        elif kind == "balcony":
            piers.extend(balcony(parts, wall, detail, field, roof_at, trim))
        else:
            width, add, _, plan, _ = face(parts, wall, detail)
            for fraction, z, breadth, height, ribs in detail["windows"]:
                u = width * fraction
                assert roof_at(plan(u, 0)) > z + height + 0.12, (row["id"], detail)
                millrace.window(add, u, breadth, z, height, trim, ribs=ribs)
            for fraction in detail.get("brackets", []):
                u = width * fraction
                e, n = plan(u, 0.078)
                tip = roof_at((e, n)) - 0.18
                beam(parts, (e, n, tip - 0.72), (*plan(u, 0.37), tip), 0.083, WOOD)
    for detail in row["dormers"]:
        fairmount.dormer(parts, row, detail, roof_at, outline)
    piers.extend(fairmount.supplements(parts, row, field, wall, roof_at))
    if row.get("solar_array"):
        solar_array(parts, row, roof_at, row["solar_array"])
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    return (
        mesh,
        {
            **{k: row[k] for k in ("id", "name", "street_address")},
            "footprint_enu_m": base.ring(outline),
            "ground_footprints_enu_m": [base.ring(wall)],
            "support_collision_enu_m": [base.ring(pier) for pier in piers],
            "area_m2": round(outline.area, 3),
            "base_z_m": round(floor, 4),
            "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
            "entrances": [gate] if gate else [],
        },
        wall,
        piers,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(), PACKAGE, GROUND, "southeast_fairmount_exterior_site", build
    )
