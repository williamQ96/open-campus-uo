# SPDX-License-Identifier: Apache-2.0
"""Rebuild six registered exteriors around Alder Street and Harris Street."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import intersects_xy, set_precision
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import trimesh

fairmount = import_module("build-fairmount-kincaid-exterior-review")
northwest = import_module("build-northwest-infill-exterior-review")
east = import_module("build-east-nineteenth-exterior-review")
garden, geometry, base = fairmount.garden, fairmount.geometry, fairmount.base
beam, chapter = fairmount.beam, fairmount.chapter
PACKAGE = "alder-harris-exterior-review"
GROUND = "alder-harris-approaches"
BRICK = (126, 84, 61)
CREAM = (210, 204, 180)
GREEN = (103, 140, 101)
STEEL = (72, 82, 80)
CONCRETE = (155, 153, 136)
WOOD = (120, 82, 61)


def window_bays(parts, row, wall, field, roof_at, gate_edge, gate_point):
    trim = row["trim_color"]
    visible_door = row.get("facade_door_enu_m")
    if visible_door is not None:
        edge = garden.locate_face(
            list(garden.shared.face_edges(wall)), visible_door, 180
        )
        gate_edge, gate_point = LineString(edge), Point(visible_door)
    for line, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 2.25:
            continue
        grade = geometry.sample_ground(field, *plan(span / 2, 0))
        top = min(roof_at(plan(u, 0)) for u in (0.10, span - 0.10, span / 2))
        threshold = line.project(gate_point) if line.equals(gate_edge) else -20
        if row["band_m"] and row["band_m"] + 0.25 < top:
            band = row["band_m"]
            add(0.018, span - 0.018, 0.012, 0.084, band - 0.09, band + 0.02, trim)
        count = max(1, round(span / row["bay_spacing_m"]))
        for i in range(count):
            at = (i + 0.5) * span / count
            width = min(row["window_width_m"], span / count - 0.41)
            for sill, height in row["windows_m"]:
                if (
                    row["style"] == "stucco-apartments"
                    and normal[1] > 0.9
                    and sill > 3.0
                ):
                    continue
                if (
                    grade - 0.12 <= sill
                    and sill + height < top - 0.23
                    and (sill > grade + 2.4 or abs(at - threshold) > 1.15)
                ):
                    northwest.window_grid(
                        add, at, width, sill, sill + height, 2, 2, trim
                    )
        if visible_door is not None and threshold >= 0:
            fairmount.millrace.door(add, threshold, grade + 0.11, (188, 158, 76))
        add(
            0.02,
            span - 0.02,
            0.008,
            0.038,
            grade - 0.22,
            min(grade + 0.33, top - 0.15),
            CONCRETE,
        )


def lorax_tower(parts, row, floor):
    e, n, radius, band, eave, peak = row["tower"]
    outline = orient(Point(e, n).buffer(radius, quad_segs=12))
    base.flat(parts, outline, floor, band, BRICK)
    base.flat(parts, outline, band, eave, CREAM)
    rim = orient(outline.buffer(0.105))
    base.flat(parts, rim, eave - 0.21, eave, STEEL)
    points = list(rim.exterior.coords)[:-1]
    tip = len(points)
    roof = trimesh.Trimesh(
        vertices=[(x, eave, -y) for x, y in points] + [(e, peak, -n)],
        faces=[(i, (i + 1) % tip, tip) for i in range(tip)],
        process=False,
    )
    roof.visual.vertex_colors = (*row["roof_color"], 255)
    parts.append(roof)
    for angle in np.deg2rad((-72, -36, 0, 36, 72)):
        outward = np.array([np.cos(angle), np.sin(angle)])
        tangent = np.array([-outward[1], outward[0]])
        center = np.array((e, n)) + outward * (radius - 0.025)
        a, b = center - 0.34 * tangent, center + 0.34 * tangent
        length, add, _, _, _, slab = chapter.setup_face(parts, a, b)
        for z in (5.36, 8.38, 10.82):
            arch = chapter.arch(length / 2, z, 0.49, 1.26, 0.25)
            trim = arch.buffer(0.054)
            slab(trim.difference(arch), 0.016, 0.064, CREAM)
            slab(arch, 0.015, 0.040, (76, 102, 101))
            add(
                length / 2 - 0.016,
                length / 2 + 0.016,
                0.041,
                0.060,
                z + 0.05,
                z + 1.21,
                STEEL,
            )
    return outline


def covered_porch(parts, line, point, field, width, depth, level, color):
    _, add, _, plan = fairmount.millrace.basis(parts, *line.coords)
    at = line.project(point)
    cap = level + 2.85
    add(at - width, at + width, -0.06, depth, cap - 0.18, cap, color)
    base.flat(
        parts,
        fairmount.rectangle(plan, at - width, at + width, -0.03, depth - 0.16),
        level - 0.24,
        level,
        CONCRETE,
    )
    supports = []
    for offset in np.linspace(-width + 0.17, width - 0.17, 5):
        if abs(offset) < 0.73:
            continue
        x = at + offset
        grade = geometry.sample_ground(field, *plan(x, depth - 0.30))
        supports.append(
            east.pier(parts, plan, x, depth - 0.30, grade - 0.08, cap, color, 0.13)
        )
    return supports


def dormers(parts, row, roof_at, outline):
    for spec in row.get("dormers", []):
        fairmount.dormer(parts, row, spec, roof_at, outline)


def woodside(parts, row, wall, field, roof_at, door_edge, door_point):
    supports = []
    for line, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 2.8:
            continue
        grade = geometry.sample_ground(field, *plan(span / 2, 0))
        at = line.project(door_point) if line.equals(door_edge) else -20
        top = min(roof_at(plan(u, 0)) for u in (0.1, span / 2, span - 0.1))
        face_windows = max(1, round(span / 3.18))
        blue_base = (80, 118, 145)
        deck_levels = row["balcony_levels_m"]
        if normal[0] > 0.9 and span > 8:
            first = deck_levels[0]
            if grade + 0.38 < first - 0.24:
                end = min(span - 0.06, at - 1.57) if at >= 0 else span - 0.06
                for a, b in ((0.06, end), (at + 1.57, span - 0.06)):
                    if a < 0 or b - a < 1.0:
                        continue
                    add(a, b, 0.005, 0.033, grade, first - 0.15, blue_base)
                    count = max(1, round((b - a) / 0.25))
                    for x in np.linspace(a, b, count + 1)[1:-1]:
                        add(
                            x,
                            x + 0.012,
                            0.033,
                            0.047,
                            grade + 0.10,
                            first - 0.18,
                            (134, 151, 154),
                        )
                    for z in np.arange(grade + 0.19, first - 0.20, 0.24):
                        add(a, b, 0.033, 0.047, z, z + 0.012, (134, 151, 154))
        for index, z in enumerate(deck_levels):
            if z + 1.25 > top - 0.14:
                continue
            windows = (
                np.linspace(1.22, span - 1.22, face_windows)
                if face_windows > 1
                else (span / 2,)
            )
            for x in windows:
                if index > 0 or abs(x - at) > 1.07:
                    northwest.window_grid(add, x, 1.56, z + 0.73, z + 1.89, 2, 2, CREAM)
            if not (span > 7.0 and normal[0] > 0.9):
                continue
            segments = ((0.13, span - 0.13),)
            if index == 0 and at >= 0:
                segments = ((0.13, at - 1.12), (at + 1.12, span - 0.13))
            for lower, upper in segments:
                if upper - lower < 1.0:
                    continue
                add(lower, upper, -0.03, 1.49, z - 0.24, z, CREAM)
                fairmount.balustrade(
                    parts, plan(lower, 1.44), plan(upper, 1.44), z, CREAM
                )
                if index == 0:
                    for x in (lower + 0.11, upper - 0.11):
                        y = geometry.sample_ground(field, *plan(x, 1.40))
                        supports.append(
                            east.pier(parts, plan, x, 1.40, y - 0.12, z, CREAM)
                        )
    for interior in wall.interiors:
        if Polygon(interior).area < 10:
            continue
        for a, b in zip(interior.coords, interior.coords[1:]):
            if np.linalg.norm(np.subtract(a, b)) < 2.6:
                continue
            span, add, _, plan, _, _ = chapter.setup_face(parts, a, b)
            for x in np.linspace(1.08, span - 1.08, max(1, round(span / 3.1))):
                for z in row["balcony_levels_m"]:
                    if z + 2.07 < roof_at(plan(x, 0)):
                        northwest.window_grid(
                            add, x, 1.38, z + 0.69, z + 1.82, 2, 1, CREAM
                        )
    return supports


def brick_parapet(parts, row, wall, field, roof_at):
    for _, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 3.4:
            continue
        grade = geometry.sample_ground(field, *plan(span / 2, 0))
        cap = roof_at(plan(span / 2, 0))
        add(
            0.015, span - 0.015, 0.014, 0.065, grade - 0.17, grade + 0.90, (126, 72, 66)
        )
        if normal[1] > 0.9:
            for fraction in (0.14, 0.31, 0.61):
                x = span * fraction
                add(
                    x - 0.51,
                    x + 0.51,
                    0.009,
                    0.037,
                    cap - 2.95,
                    cap + 0.025,
                    (125, 69, 66),
                )
                for offset in np.arange(-0.43, 0.48, 0.11):
                    add(
                        x + offset,
                        x + offset + 0.014,
                        0.037,
                        0.045,
                        cap - 2.95,
                        cap,
                        (103, 62, 59),
                    )
                northwest.window_grid(add, x, 0.83, cap - 2.57, cap - 0.97, 1, 2, CREAM)
                northwest.window_grid(
                    add, x, 1.30, grade + 1.24, grade + 2.58, 2, 1, CREAM
                )
        else:
            count = max(1, round(span / 3.53))
            for x in np.linspace(1.3, span - 1.3, count):
                for sill, height in row["windows_m"]:
                    northwest.window_grid(
                        add, x, 1.17, sill, sill + height, 2, 1, CREAM
                    )


def alley_stair(parts, row, field):
    start, end = row["alley_steps_enu_m"]
    bottom = geometry.sample_ground(field, *start)
    level = row["alley_threshold_m"]
    northwest.stair(parts, start, end, bottom, level, 1.04, steps=11)
    pad = box(end[0] - 0.09, end[1] - 0.56, end[0] + 1.38, end[1] + 0.56)
    base.flat(parts, orient(pad), level - 0.23, level, WOOD)
    fairmount.millrace.door(
        chapter.setup_face(
            parts, (end[0] + 0.015, end[1] - 0.69), (end[0] + 0.015, end[1] + 0.69)
        )[1],
        0.69,
        level,
        WOOD,
    )


def build(row, field, paving):
    outline = orient(
        set_precision(Polygon(row["outline_enu_m"], row.get("holes_enu_m", [])), 0.002)
    )
    roof = outline
    if "tower" in row:
        roof = orient(outline.intersection(box(-801, -424, -774.23, -399)))
    wall = orient(roof.buffer(-row["eaves_m"], join_style="mitre"))
    if "porch_recess_enu_m" in row:
        wall = orient(wall.difference(box(*row["porch_recess_enu_m"])))
    floor, _ = garden.science.earlier.fit_base(field, wall)
    parts = []
    wall_top = row["band_m"]
    roof_floor, roof_row = floor, row
    if wall_top:
        base.flat(parts, wall, floor, wall_top, row["wall_color"])
        roof_floor, roof_row = wall_top, {**row, "wall_color": CREAM}
    roof_at = garden.roof_sections(parts, roof, wall, roof_floor, roof_row, grid=0.0002)
    kind = row["style"]
    gate, line, point, supports = fairmount.entrance(parts, row, wall, field, paving)
    if kind == "woodside":
        supports.extend(woodside(parts, row, wall, field, roof_at, line, point))
    elif kind == "parapet":
        brick_parapet(parts, row, wall, field, roof_at)
    else:
        window_bays(parts, row, wall, field, roof_at, line, point)
        dormers(parts, row, roof_at, roof)
    if kind == "campbell":
        supports.extend(
            covered_porch(
                parts, line, point, field, 5.85, 2.38, gate["threshold_z_m"], GREEN
            )
        )
    if "alley_steps_enu_m" in row:
        alley_stair(parts, row, field)
    if kind == "lorax":
        wall = unary_union([wall, lorax_tower(parts, row, floor)])
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{key: row[key] for key in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [gate] if gate else [],
    }
    if outline.interiors:
        record["footprint_holes_enu_m"] = [
            list(ring.coords)[:-1] for ring in outline.interiors
        ]
    else:
        record["ground_footprints_enu_m"] = [
            base.ring(orient(p)) for p in geometry.sections(wall)
        ]
    return mesh, record, wall, supports


def source_removals(spec, config, audit):
    # Campbell and the next house meet on their old footprint edges. The
    # pinned source gives them separate contiguous triangle ranges.
    special = spec["campbell_source_range"]
    id, target = special["id"], special["target"]
    ordinary = [item for item in spec["source_ranges"] if item["id"] != id]
    patches = garden.shared.frohnmayer.source_removals(
        {"absorbed_batches": ordinary}, config, audit
    )
    scene_path = fairmount.SCENE / config["asset_url"]
    assert (
        garden.tools.digest(scene_path) == config["asset_sha256"] == special["sha256"]
    )
    scene = trimesh.load(scene_path, force="scene", process=False)
    transform, key = scene.graph[target]
    assert np.array_equal(transform, np.eye(4))
    triangles = scene.geometry[key].triangles
    members = audit["context_batches"][target]
    records = {item["id"]: item for item in audit["appearance_plan"]}
    start, end = special["campbell_triangles"]
    peer_start, peer_end = special["peer_triangles"]
    assert id in members and special["peer_id"] in members
    assert 0 <= start < end <= peer_start < peer_end <= len(triangles)
    for building, expected in (
        (id, np.arange(start, end)),
        (special["peer_id"], np.arange(peer_start, peer_end)),
    ):
        outline = Polygon(records[building]["footprint_enu_m"]).buffer(0.29)
        hits = intersects_xy(outline, triangles[:, :, 0], -triangles[:, :, 2]).all(
            axis=1
        )
        if building != id:
            hits[start:end] = False
        assert np.array_equal(np.flatnonzero(hits), expected), building
    corners = triangles[start:end].reshape(-1, 3)
    patches.append(
        {
            "id": id,
            "target": target,
            "triangles": [start, end],
            "source_triangle_count": len(triangles),
            "source_vertices": [
                [i, corners[i].round(6).tolist()]
                for i in (0, len(corners) // 2, len(corners) - 1)
            ],
        }
    )
    return patches


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(),
        PACKAGE,
        GROUND,
        "alder_harris_exterior_site",
        build,
        source_removals=source_removals,
    )
