# SPDX-License-Identifier: Apache-2.0
"""Author the Alder Suites, Morse Center and Pomajevich Hall exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-walnut-alder-broadway-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
prior = module_from_spec(loader)
loader.loader.exec_module(prior)
ROOT, SCENE = prior.ROOT, prior.SCENE
chapter, garden, base, geometry = (
    prior.chapter,
    prior.garden,
    prior.base,
    prior.geometry,
)
PACKAGE = "alder-bushnell-exterior-review"
GROUND = "alder-bushnell-approaches"
ALUMINUM = (176, 177, 167)
GLASS = (72, 103, 110)
CONCRETE = (157, 153, 140)
DARK = (75, 73, 66)
SIDING = (171, 165, 141)
STONE = (159, 143, 123)
BRICK = (155, 103, 83)
SAGE = (171, 178, 161)
MORSE = (173, 177, 175)
WINDOW = prior.WINDOW


def shell(parts, row, outline, footprint, floor, body, fascia, top):
    return garden.roof_sections(
        parts,
        outline,
        footprint,
        floor,
        {**row, "wall_color": body, "trim_color": fascia, "roof_color": top},
        grid=0.0002,
    )


def trim_stone(add, low, top, width):
    palette = ((158, 145, 129), (173, 158, 142), (149, 137, 123), (167, 152, 135))
    add(0.012, width - 0.012, 0.004, 0.034, low, top, STONE)
    for column, left in enumerate(np.arange(0.06, width - 0.07, 0.69)):
        for level, bottom in enumerate(np.arange(low + 0.08, top - 0.1, 0.23)):
            offset = (level % 2) * 0.23
            start, end = left + offset, min(left + offset + 0.66, width - 0.03)
            if end - start > 0.028:
                add(
                    start,
                    end,
                    0.031,
                    0.047,
                    bottom,
                    bottom + 0.198,
                    palette[(column + 3 * level + column * level) % len(palette)],
                )


def building_faces(parts, shape):
    for a, b in garden.shared.face_edges(shape):
        yield LineString((a, b)), chapter.setup_face(parts, a, b)


def suites(parts, row, outline, floor, grade, field, ground):
    wall = orient(outline.buffer(-0.26, join_style="mitre"))
    parking_top = grade + 2.72
    west, south, east, north = wall.bounds
    occupied = orient(wall.difference(box(west - 1, south - 1, -776.6, 418.45)))
    base.flat(parts, occupied, floor, parking_top, STONE)
    supports = []
    for x in np.arange(west + 1.15, -778.4, 4.15):
        post = box(x - 0.18, south + 0.67, x + 0.18, south + 1.03)
        base.flat(parts, post, floor, parking_top, CONCRETE)
        supports.append(post)
    height = shell(
        parts, row, outline, wall, parking_top, SIDING, (119, 112, 98), (126, 127, 118)
    )
    front_point = Point(row["entrance"]["point"])
    for edge, (width, add, outward, plan, _, _) in building_faces(parts, wall):
        front = outward[0] > 0.95
        south_side = outward[1] < -0.95
        street_base = grade + 4.1
        if front:
            trim_stone(add, floor, street_base, width)
            at = edge.project(front_point)
            prior.glazed_door(add, at, grade + 0.015, 1.76)
            for center in (width * 0.15, width * 0.39, width * 0.67, width * 0.86):
                if abs(center - at) > 1.8:
                    WINDOW(
                        add,
                        center,
                        1.58,
                        grade + 0.37,
                        street_base - 0.21,
                        ALUMINUM,
                        GLASS,
                        ribs=2,
                    )
            panel = width * 0.44
            add(
                panel - 1.48,
                panel + 1.48,
                0.012,
                0.26,
                street_base + 0.21,
                14.2,
                (199, 196, 178),
            )
            for z in np.arange(street_base + 0.32, 14.1, 0.18):
                add(0.06, width - 0.06, 0.004, 0.022, z, z + 0.014, (144, 138, 118))
                add(
                    panel - 1.46,
                    panel + 1.46,
                    0.258,
                    0.273,
                    z,
                    z + 0.012,
                    (178, 176, 161),
                )
            for z in (2.72, 5.70, 8.68, 11.67):
                WINDOW(add, width * 0.20, 1.02, z, z + 1.43, ALUMINUM, GLASS)
                WINDOW(add, width * 0.72, 1.02, z, z + 1.43, ALUMINUM, GLASS)
                for center in (panel - 0.58, panel + 0.58):
                    add(
                        center - 0.52,
                        center + 0.52,
                        0.269,
                        0.316,
                        z - 0.045,
                        z + 1.48,
                        ALUMINUM,
                    )
                    add(center - 0.46, center + 0.46, 0.316, 0.332, z, z + 1.43, GLASS)
                    add(
                        center - 0.46,
                        center + 0.46,
                        0.331,
                        0.344,
                        z + 0.65,
                        z + 0.69,
                        ALUMINUM,
                    )
            continue
        if south_side:
            add(0.024, width - 0.024, 0.002, 0.036, parking_top, 13.95, (142, 94, 83))
            add(
                0.024,
                width - 0.024,
                0.03,
                0.071,
                parking_top,
                parking_top + 0.34,
                (118, 79, 73),
            )
        for center in np.arange(1.58, width - 1.0, 3.92):
            for z in (2.62, 5.60, 8.60, 11.59):
                if z + 1.42 < height(plan(center, 0)) - 0.25:
                    WINDOW(
                        add, float(center), 1.42, z, z + 1.38, ALUMINUM, GLASS, ribs=1
                    )
        if outward[1] > 0.95:
            # Near the street, balconies project beyond the north elevation.
            near = edge.project(Point((east - 3.7, north)))
            for z in (1.92, 4.90, 7.89, 10.89):
                WINDOW(add, near, 1.26, z + 0.04, z + 2.02, ALUMINUM, GLASS)
                for u in (near - 1.20, near + 1.16):
                    add(u, u + 0.04, 0.05, 0.85, z + 0.93, z + 0.99, ALUMINUM)
                    for d in (0.10, 0.29, 0.48, 0.67):
                        add(u, u + 0.04, d, d + 0.025, z + 0.04, z + 0.95, ALUMINUM)
                for start, end, a, b, lo, hi in [
                    (near - 1.23, near + 1.23, 0, 0.89, z - 0.16, z),
                    (near - 1.23, near + 1.23, 0.81, 0.87, z + 0.93, z + 0.99),
                    (near - 1.23, near + 1.23, 0.81, 0.87, z + 0.13, z + 0.18),
                ]:
                    add(start, end, a, b, lo, hi, ALUMINUM)
                for u in np.arange(near - 1.20, near + 1.22, 0.149):
                    add(u, u + 0.026, 0.818, 0.861, z + 0.12, z + 0.94, ALUMINUM)
    prior.paving(ground, *row["entrance"]["point"], grade, (1, 0), 1.84, 1.2)
    return [occupied], supports, grade


def entrance_step(parts, e, n, grade, height, outward, width, run):
    # The frontage stair sits outside the collision polygon.
    for i in range(5):
        a = outward * run * i / 5
        b = outward * run * (i + 1) / 5
        upper = height - (i / 5) * (height - grade)
        base.flat(
            parts,
            box(e + min(a, b), n - width / 2, e + max(a, b), n + width / 2),
            grade - 0.12,
            upper,
            CONCRETE,
        )
    for side in [-1, 1]:
        y = n + side * (width / 2 - 0.18)
        for t in (0.12, run - 0.13):
            top = height - t * (height - grade) / run
            garden.tools.beam(
                parts,
                (e + outward * t, y, top),
                (e + outward * t, y, top + 0.86),
                0.047,
                ALUMINUM,
            )
        garden.tools.beam(
            parts,
            (e, y, height + 0.86),
            (e + outward * run, y, grade + 0.86),
            0.045,
            ALUMINUM,
        )


def morse(parts, row, outline, floor, grade, field, ground):
    wall = orient(outline.buffer(-0.03, join_style="mitre"))
    height = shell(
        parts, row, outline, wall, floor, MORSE, (128, 137, 138), (183, 187, 184)
    )
    e, n = row["entrance"]["point"]
    entry = Point(e, n)
    threshold = grade + 0.66
    for edge, (width, add, outward, plan, _, _) in building_faces(parts, wall):
        if width < 2.4:
            continue
        west = outward[0] < -0.95
        at = edge.project(entry)
        has_entry = west and edge.distance(entry) < 0.15
        for z in (grade + 1.26, grade + 2.97):
            add(0.03, width - 0.03, 0.008, 0.05, z, z + 0.032, (139, 143, 139))
        add(0.04, width - 0.04, 0.003, 0.031, floor, grade + 1.26, (134, 137, 133))
        for u in np.arange(0.91, width - 0.05, 1.22):
            max_z = height(plan(u, 0)) - 0.19
            add(u, u + 0.017, 0.006, 0.027, grade + 1.28, max_z, (150, 156, 154))
        if has_entry:
            prior.glazed_door(add, at - 0.9, threshold, 1.74)
            prior.glazed_door(add, at + 0.9, threshold, 1.74)
            WINDOW(
                add,
                at,
                4.60,
                threshold + 3.07,
                threshold + 5.16,
                ALUMINUM,
                GLASS,
                ribs=4,
            )
            add(
                at - 2.54,
                at + 2.54,
                0.03,
                1.22,
                threshold + 2.47,
                threshold + 2.59,
                (124, 150, 150),
            )
            for u in np.arange(at - 2.43, at + 2.49, 0.82):
                add(
                    u,
                    u + 0.046,
                    0.02,
                    1.22,
                    threshold + 2.59,
                    threshold + 2.63,
                    ALUMINUM,
                )
        if west and width > 25:
            origin = plan(0, 0)[1]
            along = (plan(width, 0)[1] - origin) / width
            for y in (292, 296.1, 300.2, 304.3, 307.95):
                u = (y - origin) / along
                if 2 < u < width - 2:
                    WINDOW(
                        add,
                        float(u),
                        3.83,
                        grade + 7.15,
                        grade + 8.52,
                        ALUMINUM,
                        GLASS,
                        ribs=2,
                    )
    for y in (278.9, 312.1):
        for x in (-737.05, -707.82):
            pier = box(x - 1.58, y - 2.25, x + 1.58, y + 2.25).intersection(wall)
            base.flat(parts, pier, grade + 9.0, 13.86, MORSE, (178, 179, 175))
    entrance_step(ground, e, n, grade, threshold, -1, 5.35, 1.65)
    prior.paving(ground, e - 1.65, n, grade, (-1, 0), 5.35, 1.15)
    return [wall], [], threshold


def pomajevich(parts, row, outline, floor, grade, field, ground):
    wall = orient(outline.buffer(-0.022, join_style="mitre"))
    top = shell(
        parts, row, outline, wall, floor, BRICK, (190, 182, 151), (126, 113, 104)
    )
    e, n = row["entrance"]["point"]
    threshold = grade + 0.53
    entry = Point(e, n)
    supports = []
    for edge, (width, add, outward, plan, _, _) in building_faces(parts, wall):
        if width < 2.1:
            continue
        front = outward[0] > 0.95 and edge.distance(entry) < 0.18
        low = geometry.sample_ground(field, *plan(width / 2, 0))
        if front:
            at = edge.project(entry)
            add(at - 3.18, at + 3.18, 0.012, 0.09, floor, 6.08, (202, 199, 174))
            prior.glazed_door(add, at, threshold, 1.88)
            WINDOW(add, at, 5.08, threshold + 3.8, 5.62, ALUMINUM, GLASS, ribs=5)
            add(at - 3.66, at + 3.66, 0.013, 2.11, 6.16, 6.34, (193, 188, 165))
            for offset in (-3.27, 3.27):
                u = at + offset
                add(u - 0.10, u + 0.10, 1.83, 2.03, threshold, 6.16, (211, 205, 181))
                x, y = plan(u, 1.93)
                pad = box(x - 0.18, y - 0.18, x + 0.18, y + 0.18)
                base.flat(
                    parts,
                    pad,
                    geometry.sample_ground(field, x, y) - 0.15,
                    threshold + 0.012,
                    CONCRETE,
                )
                supports.append(pad)
            for left, right in ((1.13, at - 3.55), (at + 3.55, width - 0.97)):
                if right - left < 2:
                    continue
                add(left, right, 0.004, 0.073, low + 0.43, 5.71, SAGE)
                for u in np.arange(left + 0.63, right - 0.51, 1.29):
                    for z in (low + 1.08, 4.34):
                        WINDOW(
                            add, float(u), 1.08, z, z + 1.12, ALUMINUM, GLASS, ribs=1
                        )
        else:
            for u in np.arange(1.28, width - 0.86, 2.21):
                for z in (low + 1.23, low + 4.10):
                    if z + 1.16 < top(plan(u, 0)) - 0.23:
                        WINDOW(
                            add, float(u), 1.35, z, z + 1.12, ALUMINUM, GLASS, ribs=1
                        )
    entrance_step(ground, e, n, grade, threshold, 1, 2.35, 2.14)
    prior.paving(ground, e + 2.14, n, grade, (1, 0), 2.35, 0.85)
    # A transverse side ramp and guard follow the visible raised approach.
    west, east = e + 0.18, e + 1.76
    ramp = box(west, n - 6.35, east, n - 1.13)

    def ramp_top(x, y):
        return grade + 0.045 + (threshold - grade - 0.045) * ((y - n + 6.35) / 5.22)

    ground.append(
        geometry.shell(ramp, grade - 0.19, ramp_top, CONCRETE, (169, 167, 155))
    )
    for x in (west + 0.065, east - 0.065):
        y1, y2 = n - 6.25, n - 1.23
        for y in np.linspace(y1, y2, 6):
            z = ramp_top(x, y)
            garden.tools.beam(ground, (x, y, z), (x, y, z + 0.83), 0.042, ALUMINUM)
        garden.tools.beam(
            ground,
            (x, y1, ramp_top(x, y1) + 0.83),
            (x, y2, ramp_top(x, y2) + 0.83),
            0.049,
            ALUMINUM,
        )
    return [wall], supports, threshold


def build(row, field, ground):
    outline = orient(Polygon(row["outline_enu_m"]))
    floor, _ = garden.science.earlier.fit_base(field, outline)
    entry = row["entrance"]
    e, n = entry["point"]
    grade = geometry.sample_ground(field, e, n)
    parts = []
    methods = {"suites": suites, "morse": morse, "pomajevich": pomajevich}
    plans, supports, threshold = methods[row["role"]](
        parts, row, outline, floor, grade, field, ground
    )
    assert all(p.is_valid for p in plans + supports)
    assert min(p.boundary.distance(Point(e, n)) for p in plans) < 0.115
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000018))
    record = {
        "id": row["id"],
        "name": row["name"],
        "street_address": row["street_address"],
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(p) for p in plans],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [
            {
                "gate": entry["gate"],
                "position_enu_m": [e, n],
                "outward_degrees": entry["bearing"],
                "approach_distance_m": entry["distance"],
                "threshold_z_m": round(threshold, 4),
                "width_m": 1.8,
                "estimated": True,
                "snap_to_facade": False,
            }
        ],
    }
    return garden.science.ordered_mesh(mesh), record, plans, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = ROOT / "data/metadata"
    spec = json.loads((metadata / f"{PACKAGE}.json").read_bytes())
    source_path = SCENE / "manifest.json"
    config_path = SCENE / "presentation.json"
    manifest, config = (
        json.loads(path.read_bytes()) for path in (source_path, config_path)
    )
    height_path = SCENE / manifest["heightfield_url"]
    digest = garden.tools.digest
    assert digest(source_path) == spec["source_manifest_sha256"]
    assert digest(height_path) == spec["source_heightfield_sha256"]
    field = json.loads(height_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, plans, supports, gates = {}, [], [], [], [], []
    for row in spec["models"]:
        mesh, record, occupied, feet = build(row, field, ground)
        meshes[row["id"]] = mesh
        records.append(record)
        plans.extend(occupied)
        supports.extend(feet)
        gates.extend(record["entrances"])
    assert len(plans) == 3 and len(supports) > 8
    assert all(not p.covers(Point(-812.2, 415.4)) for p in plans + supports)
    old = union_all(
        [
            Polygon(row["footprint_enu_m"])
            for row in manifest["buildings"]
            if row["id"] in meshes
        ]
    )
    check_routes = chapter.prior.nearby.shared.graduate.shared.check_routes
    count, clearance = check_routes(
        plans, supports, gates, old, manifest, graph, config, set(meshes)
    )
    appearances = json.loads((metadata / "campus-expansion-audit.json").read_bytes())
    removals = garden.shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, appearances
    )
    stage = args.stage or SCENE / PACKAGE
    stage.mkdir(exist_ok=True, parents=True)
    model, descriptor = stage / "site.glb", stage / "site.json"
    pavement = garden.science.ordered_mesh(trimesh.util.concatenate(ground))
    garden.site.memorial.gerlinger.export(
        model, meshes, pavement, GROUND, "alder-bushnell-paving"
    )
    package = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": digest(model),
        "buildings": records,
        "new_building_ids": spec["new_building_ids"],
        "batch_removals": removals,
    }
    prior.write_json(descriptor, package, compact=True)
    if args.stage is None:
        config["alder_bushnell_site"] = {
            "url": f"{PACKAGE}/site.json",
            "sha256": digest(descriptor),
        }
        prior.write_json(config_path, config)
    audit = {
        "buildings": records,
        "batch_removals": removals,
        "route_edges": count,
        "nearest_route_m": round(clearance, 4),
        "triangles": {key: len(mesh.faces) for key, mesh in meshes.items()},
        "glb_sha256": digest(model),
        "descriptor_sha256": digest(descriptor),
    }
    prior.write_json(args.audit, audit)
    print(audit["triangles"], audit["nearest_route_m"])


if __name__ == "__main__":
    main()
