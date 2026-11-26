# SPDX-License-Identifier: Apache-2.0
"""Rebuild the original ZIRC exterior and its visible northwest addition."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-fairmount-boulevard-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
houses = module_from_spec(loader)
loader.loader.exec_module(houses)

ROOT = houses.ROOT
PACKAGE = "zirc-exterior-review"
GROUND = "zirc-exterior-approaches"
MASONRY = (111, 114, 107)
JOINT = (153, 151, 137)
STEEL = (53, 63, 65)
FOLD = (78, 86, 86)
COPPER = (148, 100, 73)
SIDING = (197, 195, 173)
BRICK = (156, 115, 97)
GLASS = (70, 95, 104)
TRIM = (99, 91, 77)


def old_facade(add, span, grade, top, entry_face):
    band = min(grade + 0.89, top - 0.2)
    add(0.01, span - 0.01, 0.002, 0.03, grade - 0.16, band, BRICK)
    if top > band + 0.12:
        add(0.01, span - 0.01, 0.002, 0.026, band, top - 0.055, SIDING)
    for left in np.arange(0.17, span - 0.15, 0.32):
        if top > band + 0.12:
            add(
                left,
                left + 0.012,
                0.028,
                0.042,
                band + 0.015,
                top - 0.065,
                (173, 171, 151),
            )
    if top > grade + 2.42 and not entry_face:
        for center in np.arange(2, span - 1.15, 3.35):
            houses.chapter.prior.window(
                add,
                center,
                1.08,
                grade + 1.07,
                min(grade + 2.43, top - 0.18),
                TRIM,
                GLASS,
                ribs=1,
            )
    if top > grade + 1.5:
        add(0.01, span - 0.01, 0.018, 0.11, top - 0.15, top, COPPER)


def addition_facade(parts, add, span, grade, top, position, height, cladding, windows):
    cap = min(top - 0.10, grade + 2.55) if cladding else top - 0.095
    add(0.01, span - 0.01, 0.002, 0.035, grade - 0.12, cap, MASONRY)
    vertices = []
    faces = []
    for row, z in enumerate(np.arange(grade + 0.22, cap - 0.05, 0.203)):
        add(0.01, span - 0.01, 0.035, 0.044, z, z + 0.011, JOINT)
        for u in np.arange(0.21 if row % 2 else 0.42, span - 0.03, 0.42):
            face = len(vertices)
            for station, y in (
                (u, z - 0.188),
                (u + 0.010, z - 0.188),
                (u + 0.010, z),
                (u, z),
            ):
                e, n = position(station, 0.043)
                vertices.append([e, y, -n])
            faces.extend([[face, face + 1, face + 2], [face, face + 2, face + 3]])
    if vertices:
        joints = trimesh.Trimesh(vertices, faces, process=False)
        joints.visual.vertex_colors = [*JOINT, 255]
        parts.append(joints)
    if cladding:
        add(0.01, span - 0.01, 0.002, 0.053, cap, top - 0.025, STEEL)
        for u in np.arange(0.055, span - 0.04, 0.171):
            local_top = height(position(u, 0))
            if local_top > cap:
                add(u, u + 0.024, 0.053, 0.073, cap, local_top - 0.045, FOLD)
    if windows:
        for center in (0.69, 1.93) if span < 5.6 else (2.15, 3.48):
            if center < span - 0.40 and cap > grade + 1.25:
                houses.chapter.prior.window(
                    add,
                    center,
                    0.48,
                    grade + 0.30,
                    min(cap - 0.10, grade + 2.48),
                    STEEL,
                    GLASS,
                    ribs=1,
                )
    if top > grade + 1.5:
        add(0.01, span - 0.01, 0.035, 0.082, top - 0.11, top + 0.025, FOLD)


def facade_details(parts, plan, field, height, main_face):
    for edge in houses.shared.face_edges(plan):
        span, add, outward, position, _, _ = houses.chapter.setup_face(parts, *edge)
        if span < 0.65:
            continue
        e, n = position(span / 2, 0)
        grade = houses.geometry.sample_ground(field, e, n)
        top = min(height(position(u, 0)) for u in (0.05, span / 2, span - 0.05))
        if e >= -84.65:
            old_facade(add, span, grade, top, edge == main_face)
        else:
            metal = e < -109.6 and 351.9 <= n < 371 and top > grade + 5.2
            exposed = outward[0] < -0.85 or outward[1] > 0.85
            addition_facade(
                parts,
                add,
                span,
                grade,
                top,
                position,
                height,
                metal,
                exposed and not metal,
            )


def porch(parts, field, edge, center, entry):
    _, add, _, point, _, _ = houses.chapter.setup_face(parts, *edge)
    half, depth = 2.9, 1.78
    threshold = entry["threshold_z_m"]
    ridge, beam = threshold + 3.52, threshold + 2.76
    for left, right, outside in (
        (center - half, center, center - half),
        (center, center + half, center + half),
    ):
        footprint = Polygon(
            [
                point(u, d)
                for u, d in (
                    (left, -0.10),
                    (right, -0.10),
                    (right, depth),
                    (left, depth),
                )
            ]
        )
        reference = point(outside, depth)
        slope = (point(center, depth) - reference) * (ridge - beam) / (half * half)

        def plane(e, n):
            return beam + slope @ (np.array([e, n]) - reference)

        cap = houses.geometry.shell(footprint, beam - 0.16, plane, COPPER, COPPER)
        bottom = np.isclose(cap.vertices[:, 1], beam - 0.16, atol=1e-6)
        cap.vertices[bottom, 1] = [
            plane(e, -z) - 0.13 for e, _, z in cap.vertices[bottom]
        ]
        parts.append(cap)
    add(
        center - half,
        center + half,
        depth - 0.085,
        depth + 0.015,
        beam - 0.145,
        beam + 0.025,
        COPPER,
    )
    feet = []
    for u in (center - half + 0.2, center + half - 0.2):
        foot = point(u, depth - 0.12)
        grade = houses.geometry.sample_ground(field, *foot)
        feet.append(
            houses.approaches.supported_post(
                parts, foot, grade - 0.12, beam, COPPER, 0.085
            )
        )
    return feet


def roof_seams(parts, height):
    for e in np.arange(-109.5, -84.8, 0.57):
        area = box(e, 348.05, e + 0.022, 368.39)
        base_z = min(height(p) for p in area.exterior.coords) - 0.13
        seam = houses.geometry.shell(
            area,
            base_z,
            lambda e, n: height((e, n)) + 0.035,
            (153, 164, 161),
            (160, 169, 166),
        )
        lower = np.isclose(seam.vertices[:, 1], base_z, atol=0.00001, rtol=0)
        seam.vertices[lower, 1] = [
            height((e, -z)) + 0.006 for e, _, z in seam.vertices[lower]
        ]
        parts.append(seam)


def west_walk(parts, field):
    strip = (-120.45, -118.42)
    for n in np.arange(352.7, 381.9, 1.1):

        def surface(e, n):
            return houses.geometry.sample_ground(field, e, n) + 0.027

        footprint = box(strip[0], n, strip[1], n + 1.101)
        floor = min(surface(e, n) for e, n in footprint.exterior.coords) - 0.09
        parts.append(
            houses.geometry.shell(
                footprint, floor, surface, (163, 161, 146), (180, 175, 156)
            )
        )


def build(spec, manifest, config, field, graph):
    plan = orient(Polygon(spec["wall_outline_enu_m"]))
    roof = orient(Polygon(spec["roof_outline_enu_m"]))
    assert plan.is_valid and roof.covers(plan)
    floor, _ = houses.design.science.earlier.fit_base(field, plan)
    parts, paving = [], []
    height = houses.design.roof_sections(parts, roof, plan, floor, spec, grid=0.0001)
    entry, edge, center = houses.approaches.entry_stair(
        parts,
        paving,
        list(houses.shared.face_edges(plan)),
        field,
        spec,
        None,
    )
    entry["estimated"] = True
    feet = porch(parts, field, edge, center, entry)
    facade_details(parts, plan, field, height, edge)
    roof_seams(parts, height)
    west_walk(paving, field)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000015))
    ground = houses.design.science.ordered_mesh(trimesh.util.concatenate(paving))
    mesh = houses.design.science.ordered_mesh(mesh)
    name = spec["id"]
    original = next(r for r in manifest["buildings"] if r["id"] == name)
    n, clearance = houses.chapter.prior.nearby.shared.graduate.shared.check_routes(
        [plan],
        [],
        [entry],
        Polygon(original["footprint_enu_m"]),
        manifest,
        graph,
        config,
        {name},
    )
    record = {
        "id": name,
        "name": spec["name"],
        "campus_id": spec["campus_id"],
        "street_address": spec["street_address"],
        "footprint_enu_m": houses.base.ring(plan),
        "area_m2": round(plan.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [entry],
        "support_collision_enu_m": [houses.base.ring(foot) for foot in feet],
    }
    return {name: mesh}, [record], ground, n, clearance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    houses.export_review(
        spec_path=ROOT / "data/metadata/zirc-exterior-review.json",
        package=PACKAGE,
        key="zirc_exterior_site",
        ground_node=GROUND,
        paving_node="zirc-west-walk",
        builder=build,
        audit_path=args.audit,
        stage=args.stage,
    )


if __name__ == "__main__":
    main()
