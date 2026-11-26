# SPDX-License-Identifier: Apache-2.0
"""Separate the Chi Omega and Delta Delta Delta exteriors from their merged source."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import set_precision, union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh


path = Path(__file__).with_name("build-campus-neighbor-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
neighbor = module_from_spec(loader)
loader.loader.exec_module(neighbor)
base, tools, site = neighbor.base, neighbor.tools, neighbor.site
geometry, science, shared, prior, residential = (
    neighbor.geometry,
    neighbor.science,
    neighbor.shared,
    neighbor.prior,
    neighbor.residential,
)
ROOT, SCENE = neighbor.ROOT, neighbor.SCENE
SPEC = ROOT / "data/metadata/chapter-house-exterior-review.json"
DIRECTORY = "chapter-house-exterior-review"
GROUND = "chapter-house-approaches"

BRICK = (148, 88, 74)
BRICK_SHADE = (133, 79, 67)
CAST_STONE = (217, 206, 175)
CREAM = (217, 211, 182)
TRIM = (229, 222, 190)
CLAPBOARD = (192, 183, 154)
SIDE_BOARD = (152, 163, 155)
ROOF = (124, 126, 117)
COPPER = (116, 146, 130)
WOOD = (101, 76, 63)
DARK = (53, 69, 66)
GLASS = (91, 116, 118)
FOUNDATION = (145, 140, 122)


def form(values):
    x, y, z, dx, dy = values
    return np.asarray([dx, dy, z - dx * x - dy * y])


def half_plane(bounds, condition):
    w, s, e, n = bounds
    corners = [
        np.array(x)
        for x in ((w - 1, s - 1), (e + 1, s - 1), (e + 1, n + 1), (w - 1, n + 1))
    ]
    scores = [float(condition[:2] @ x + condition[2]) for x in corners]
    polygon = []
    for a, b, za, zb in zip(
        corners, corners[1:] + corners[:1], scores, scores[1:] + scores[:1], strict=True
    ):
        if za <= 0:
            polygon.append(a)
        if (za <= 0) != (zb <= 0):
            polygon.append(a + (b - a) * za / (za - zb))
    return Polygon(polygon) if len(polygon) > 2 else Polygon()


def roof_geometry(parts, outline, floor, row):
    regions = []
    for zone in row["zones"]:
        layer = outline.intersection(box(*zone["bounds_enu_m"]))
        functions = [form(plane) for plane in zone["planes"]]
        for plane in functions:
            area = layer
            for other in functions:
                if plane is not other:
                    area = area.intersection(half_plane(outline.bounds, plane - other))
            for part in geometry.sections(set_precision(area, 0.002)):

                def height(e, n):
                    return plane @ (e, n, 1)

                parts.append(
                    geometry.shell(part, floor, height, row["wall_color"], ROOF)
                )
                regions.append((part, plane))
    missing = outline.difference(union_all([area for area, _ in regions]))
    assert missing.area < 1, (row["id"], round(missing.area, 3), missing.bounds)
    for remainder in geometry.sections(set_precision(missing, 0.002)):
        if remainder.area > 0.012:
            p = remainder.representative_point()
            z = min(regions, key=lambda item: p.distance(item[0]))[1] @ (
                *p.coords[0],
                1,
            )
            base.flat(parts, remainder, floor, z, row["wall_color"], ROOF)

    def height_at(point):
        query = Point(point)
        elevations = [
            plane @ (*point, 1)
            for region, plane in regions
            if region.distance(query) < 0.014
        ]
        if elevations:
            return max(elevations)
        return min(regions, key=lambda item: query.distance(item[0]))[1] @ (*point, 1)

    return height_at


def setup_face(parts, a, b):
    width, add = tools.face(parts, a, b)
    along = (np.asarray(b) - a) / width
    outside = np.array([along[1], -along[0]])

    def plan(u, n):
        return np.asarray(a) + u * along + n * outside

    def point(u, n, z):
        x, y = plan(u, n)
        return x, y, z

    def slab(region, start, end, color):
        mesh = geometry.shell(region, start, lambda u, z: end, color, color)
        mesh.apply_transform(
            np.array(
                [
                    [along[0], outside[0], 0, a[0]],
                    [0, 0, -1, 0],
                    [-along[1], -outside[1], 0, -a[1]],
                    [0, 0, 0, 1],
                ]
            )
        )
        parts.append(mesh)

    return width, add, outside, plan, point, slab


def principal_edge(edges, target, minimum):
    aligned = [
        edge
        for edge in edges
        if LineString(edge).length > minimum
        and neighbor.bearing(*edge) @ np.asarray(target) > 0.95
    ]
    return max(aligned, key=lambda edge: LineString(edge).length)


def raised_portico_edge(edges, hint):
    return min(
        (
            edge
            for edge in edges
            if neighbor.bearing(*edge)[1] < -0.95 and LineString(edge).length > 4
        ),
        key=lambda edge: LineString(edge).distance(Point(hint)),
    )


def gabled_canopy(parts, plan, center, half_width, foot, nose, z, rise, roof, trim):
    for side in (-1, 1):
        area = Polygon(
            [
                plan(u, d)
                for u, d in (
                    (center, foot),
                    (center + half_width * side, foot),
                    (center + half_width * side, nose),
                    (center, nose),
                )
            ]
        )
        step = plan(center + half_width * side, foot) - plan(center, foot)

        def top(e, n):
            ratio = (np.array([e, n]) - plan(center, foot)).dot(step) / step.dot(step)
            return z + 0.13 + (1 - ratio) * rise

        parts.append(geometry.shell(area, z, top, trim, roof))
    return Polygon(
        [
            plan(u, d)
            for u, d in (
                (center - half_width, foot),
                (center + half_width, foot),
                (center + half_width, nose),
                (center - half_width, nose),
            )
        ]
    )


def sash(add, u, z, width, height, shutters=False, color=TRIM):
    prior.window(add, u, width, z, z + height, color, GLASS, ribs=2)
    add(
        u - width * 0.50,
        u + width * 0.50,
        0.100,
        0.134,
        z + height * 0.35,
        z + height * 0.37,
        color,
    )
    add(u - width * 0.59, u + width * 0.59, 0.010, 0.196, z - 0.082, z - 0.036, color)
    if shutters:
        for side in (-1, 1):
            at = u + side * (width * 0.5 + 0.23)
            add(
                at - 0.184,
                at + 0.184,
                0.019,
                0.092,
                z - 0.033,
                z + height + 0.032,
                DARK,
            )
            for rail in (z + 0.105, z + height * 0.54, z + height - 0.105):
                add(
                    at - 0.175,
                    at + 0.175,
                    0.092,
                    0.105,
                    rail,
                    rail + 0.041,
                    (71, 87, 80),
                )


def stone_window(add, u, z, width, height):
    sash(add, u, z, width, height, color=CAST_STONE)
    outer = width * 0.50 + 0.19
    add(
        u - outer,
        u + outer,
        0.019,
        0.151,
        z + height + 0.048,
        z + height + 0.155,
        CAST_STONE,
    )
    for x in (u - outer, u + outer):
        add(
            x - 0.067,
            x + 0.067,
            0.019,
            0.142,
            z + height - 0.13,
            z + height + 0.153,
            CAST_STONE,
        )


def arch(center, z, width, height, rise):
    radius = width * 0.5
    return Polygon(
        [
            (center - radius, z),
            (center + radius, z),
            *[
                (
                    center + radius * np.cos(t),
                    z + height - rise + rise * (np.sin(t) ** 0.71),
                )
                for t in np.linspace(0, np.pi, 21)
            ],
        ]
    )


def projecting_bay(
    parts, plan, u, half_width, depth, bottom, high, levels, light=False
):
    w = half_width
    outline = orient(
        Polygon(
            [
                plan(v, d)
                for v, d in (
                    (u - w, -0.085),
                    (u + w, -0.085),
                    (u + w, 0.48 * depth),
                    (u + w * 0.66, depth),
                    (u - w * 0.66, depth),
                    (u - w, 0.48 * depth),
                )
            ]
        )
    )
    tone = CAST_STONE if light else BRICK
    base.flat(parts, outline, bottom, high, tone)
    base.flat(
        parts,
        outline.buffer(0.095, join_style="mitre"),
        high - 0.027,
        high + 0.16,
        CAST_STONE,
        COPPER if light else ROOF,
    )
    for a, b in shared.face_edges(outline):
        long, add = tools.face(parts, a, b)
        if (
            long < 0.31
            or LineString([a, b]).distance(LineString([plan(u - w, 0), plan(u + w, 0)]))
            < 0.13
        ):
            continue
        if long > 1.57:
            for c in np.linspace(long * 0.19, long * 0.81, 3):
                stone_window(add, c, levels[0], long * 0.22, 1.51)
                if len(levels) > 1:
                    stone_window(add, c, levels[1], long * 0.22, 1.57)
        else:
            for z in levels:
                stone_window(add, long / 2, z, long * 0.51, 1.46)
    return outline


def west_front(parts, edge, entry, grade):
    length, add, _, plan, point, slab = setup_face(parts, *edge)
    run = LineString(edge).project(Point(entry["position_enu_m"]))
    floor = entry["threshold_z_m"]
    for z in (grade + 0.35, grade + 3.01, grade + 5.65, grade + 8.51):
        add(0.03, length - 0.03, -0.025, 0.094, z - 0.043, z + 0.051, BRICK_SHADE)
    for i, u in enumerate((2.17, 5.82, 11.65, 17.17)):
        if i in (0, 3):
            for z in (grade + 0.92, grade + 3.72, grade + 6.48):
                stone_window(add, u, z, 1.22, 1.54)
        top = 15.12 if i == 2 else 14.32
        foot = grade + 8.14
        half = 2.08 if i == 2 else 1.29
        if i == 2:
            top = 16.73
        shape = Polygon([(u - half, foot - 0.09), (u + half, foot - 0.09), (u, top)])
        slab(shape, -0.012, 0.084, BRICK)
        for start, end in ((u - half, u), (u, u + half)):
            a = point(start, 0.101, top if start == u else foot)
            b = point(end, 0.101, top if end == u else foot)
            tools.beam(parts, a, b, 0.128, CAST_STONE)
        for delta in (-1, 1):
            a = point(u + delta * half, 0.097, foot - 0.065)
            b = (a[0], a[1], a[2] + 0.43)
            tools.beam(parts, a, b, 0.13, CAST_STONE)
        if i == 2:
            # Cast-stone insert and corbel under the larger gable.
            slab(
                Polygon(
                    [(u - 0.35, top - 0.67), (u + 0.35, top - 0.67), (u, top - 0.16)]
                ),
                0.08,
                0.142,
                CAST_STONE,
            )
            stone_window(add, u - 0.50, grade + 7.93, 0.68, 1.18)
            stone_window(add, u + 0.50, grade + 7.93, 0.68, 1.18)
        elif i == 1:
            stone_window(add, u, grade + 7.65, 1.03, 1.39)

    projecting_bay(
        parts,
        plan,
        run + 5.81,
        1.75,
        1.02,
        grade + 0.03,
        grade + 7.09,
        (grade + 0.95, grade + 3.83),
    )
    projecting_bay(
        parts,
        plan,
        run,
        1.13,
        0.93,
        grade + 4.28,
        grade + 6.77,
        (grade + 4.61,),
        light=True,
    )
    for offset in (0.0, 0.15, 0.30):
        profile = box(
            run - 0.48 - offset,
            floor + 3.35 + offset,
            run + 0.48 + offset,
            floor + 3.51 + offset,
        )
        slab(profile, 0.07, 0.23 + offset * 1.2, CAST_STONE)

    outer = arch(run, floor, 2.69, 2.9, 0.54)
    clear = arch(run, floor - 0.02, 1.92, 2.52, 0.45)
    slab(outer.difference(clear), 1.64, 1.93, CAST_STONE)
    slab(arch(run, floor, 1.80, 2.43, 0.38), 0.11, 0.134, WOOD)
    add(run - 1.48, run - 1.29, 0.05, 1.94, floor, floor + 2.54, BRICK)
    add(run + 1.29, run + 1.48, 0.05, 1.94, floor, floor + 2.54, BRICK)
    gabled_canopy(
        parts, plan, run, 1.51, -0.03, 1.99, floor + 2.86, 0.32, COPPER, BRICK
    )
    if run > 2.15:
        shed = Polygon(
            [
                plan(u, n)
                for u, n in (
                    (0.06, 0.012),
                    (run - 1.55, 0.012),
                    (run - 1.55, 1.84),
                    (0.06, 1.84),
                )
            ]
        )
        start = plan(0, 0.02)
        normal = plan(0, 1.02) - start

        def pitch(e, n):
            return floor + 3.132 - (np.array([e, n]) - start).dot(normal) * 0.28

        parts.append(geometry.shell(shed, floor + 2.46, pitch, BRICK, COPPER))
    return [
        Point(plan(run + u, 1.79)).buffer(0.135, quad_segs=2) for u in (-1.38, 1.38)
    ]


def chimneys(parts, outline):
    for e, n in ((-726.67, -185.53), (-726.67, -204.12)):
        shaft = box(e - 0.56, n - 0.41, e + 0.56, n + 0.41)
        assert outline.intersects(shaft)
        base.flat(parts, shaft, 13.45, 16.87, BRICK)
        base.flat(
            parts, shaft.buffer(0.06, join_style="mitre"), 16.84, 17.055, CAST_STONE
        )
        for x in (e - 0.25, e + 0.25):
            parts.append(
                geometry.shell(
                    Point(x, n).buffer(0.146, quad_segs=3),
                    17.05,
                    lambda e, n: 17.62,
                    CREAM,
                    WOOD,
                )
            )
            base.flat(
                parts, Point(x, n).buffer(0.169, quad_segs=3), 17.53, 17.68, CREAM, WOOD
            )


def chi_other_faces(parts, edges, main, audit_height, grade):
    for a, b in edges:
        if (a, b) == main:
            continue
        length, add, out, plan, point, slab = setup_face(parts, a, b)
        if length < 2.1:
            continue
        for u in np.linspace(0.89, length - 0.84, max(1, round(length / 2.66))):
            z = audit_height(plan(u, 0))
            for base_z in (grade + 0.84, grade + 3.56, grade + 6.28):
                if base_z + 1.67 < z - 0.14:
                    stone_window(add, u, base_z, min(1.19, length * 0.31), 1.39)
        center = plan(length * 0.5, 0)
        if center[0] > -722.13 and out[1] < -0.82:
            for z in np.arange(grade + 3.36, grade + 8.18, 0.20):
                add(0.03, length - 0.03, 0.014, 0.046, z, z + 0.028, SIDE_BOARD)
        if center[0] > -715 and out[1] > 0.75 and length > 6:
            # The street view shows board cladding above the brick on the rear addition.
            a, b = (
                (length * 0.62, length - 0.035)
                if plan(0, 0)[0] < plan(length, 0)[0]
                else (0.035, length * 0.36)
            )
            top = min(audit_height(plan(a, 0)), audit_height(plan(b, 0)))
            add(
                a,
                b,
                0.012,
                0.037,
                grade + 3.1,
                max(grade + 3.14, top - 0.18),
                SIDE_BOARD,
            )
            for z in np.arange(grade + 3.14, top - 0.26, 0.21):
                add(a, b, 0.036, 0.057, z, z + 0.024, (136, 149, 143))
        if center[0] > -721 and out[1] > 0.75 and length > 7:
            for u in np.linspace(length * 0.22, length * 0.78, 3):
                foot = 11.75
                height = 13.88
                slab(
                    Polygon([(u - 0.79, foot), (u + 0.79, foot), (u, height)]),
                    -0.04,
                    0.064,
                    BRICK,
                )
                gabled_canopy(
                    parts, plan, u, 0.84, -0.87, 0.12, 12.55, 0.88, ROOF, TRIM
                )


def delta_details(parts, edges, front, entry, grade, audit_height):
    for edge in edges:
        length, add, out, plan, _, _ = setup_face(parts, *edge)
        if length < 2.4:
            continue
        locations = np.linspace(0.04, length - 0.04, max(3, int(length / 0.21)))
        top = np.array([audit_height(plan(u, 0)) for u in locations])
        for z in np.arange(grade + 0.42, max(top), 0.214):
            present = (top[:-1] > z + 0.051) & (top[1:] > z + 0.051)
            intervals = np.flatnonzero(np.diff(np.r_[False, present, False])).reshape(
                -1, 2
            )
            for left, right in intervals:
                add(
                    locations[left],
                    locations[right],
                    0.011,
                    0.041,
                    z,
                    z + 0.024,
                    CLAPBOARD,
                )
        for z in (grade + 0.19, grade + 2.89, grade + 5.52):
            add(0.03, length - 0.03, -0.019, 0.059, z, z + 0.075, CREAM)
        for u in np.linspace(0.93, length - 0.91, max(1, round(length / 2.92))):
            ceiling = audit_height(plan(u, 0))
            for z in (grade + 0.84, grade + 3.63, grade + 6.14):
                if z + 1.44 < ceiling - 0.21 and prior.clear_of_entry(
                    LineString(edge), u, 0.68, [entry]
                ):
                    sash(
                        add,
                        u,
                        z,
                        min(1.22, length * 0.30),
                        1.42,
                        shutters=out[1] < -0.80,
                    )
    length, add, _, plan, point, slab = setup_face(parts, *front)
    center = LineString(front).project(Point(entry["position_enu_m"]))
    z = entry["threshold_z_m"]
    portico_half = min(2.31, length * 0.44)
    gabled_canopy(
        parts, plan, center, portico_half, 0.012, 1.72, z + 2.47, 0.86, ROOF, TRIM
    )
    add(
        center - portico_half,
        center + portico_half,
        0.03,
        1.74,
        z + 2.30,
        z + 2.48,
        CREAM,
    )
    for u in (center - 1.71, center + 1.71):
        add(u - 0.185, u + 0.185, 1.47, 1.87, z, z + 2.36, CREAM)
        add(u - 0.249, u + 0.249, 1.41, 1.91, z, z + 0.17, TRIM)
        add(u - 0.249, u + 0.249, 1.41, 1.91, z + 2.20, z + 2.37, TRIM)
    neighbor.door(add, center, z, DARK)
    for offset in (-0.79, 0.79):
        sash(add, center + offset, z + 0.39, 0.35, 1.43)
    # The facade sign follows the row of three dark triangles visible from 15th Avenue.
    frontage = max(
        (edge for edge in edges if neighbor.bearing(*edge)[1] < -0.94),
        key=lambda edge: LineString(edge).length,
    )
    span, _, _, _, symbol, _ = setup_face(parts, *frontage)
    for u in (span * 0.47 - 0.55, span * 0.47, span * 0.47 + 0.55):
        points = [
            symbol(u - 0.22, 0.09, grade + 3.02),
            symbol(u + 0.22, 0.09, grade + 3.02),
            symbol(u, 0.09, grade + 3.43),
        ]
        for a, b in zip(points, points[1:] + points[:1], strict=True):
            tools.beam(parts, a, b, 0.045, DARK)
    return [
        Point(plan(center + u, 1.68)).buffer(0.16, quad_segs=2) for u in (-1.71, 1.71)
    ]


def build(spec, manifest, config, field, graph):
    models, records, ground, plans, supports, entries = {}, [], [], [], [], []
    for row in spec["models"]:
        id = row["id"]
        outline = orient(set_precision(Polygon(row["outline"]).simplify(0.05), 0.002))
        floor, grade = science.earlier.fit_base(field, outline)
        pieces = []
        roof_at = roof_geometry(pieces, outline, floor, row)
        edges = list(shared.face_edges(outline))
        is_chi = id in spec["source_split"]
        gate = residential.entrance(ground, field, edges, row["entrance"])
        if is_chi:
            front = principal_edge(edges, (-1, 0), 12)
            blocks = west_front(pieces, front, gate, grade)
            chi_other_faces(pieces, edges, front, roof_at, grade)
            chimneys(pieces, outline)
        else:
            front = raised_portico_edge(edges, row["entrance"]["near_enu_m"])
            blocks = delta_details(pieces, edges, front, gate, grade, roof_at)
        mesh = trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.000012))
        models[id] = science.ordered_mesh(mesh)
        plans.append(outline)
        supports.extend(blocks)
        entries.append(gate)
        records.append(
            {
                "id": id,
                "name": row["name"],
                "street_address": row["street_address"],
                "footprint_enu_m": base.ring(outline),
                "area_m2": round(outline.area, 3),
                "support_collision_enu_m": [base.ring(plan) for plan in blocks],
                "entrances": [gate],
                "base_z_m": round(floor, 4),
                "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
            }
        )
    assert plans[0].distance(plans[1]) > 1
    retired = set(spec["source_split"].values())
    former = union_all(
        [
            Polygon(b["footprint_enu_m"]).buffer(0)
            for b in manifest["buildings"]
            if b["id"] in retired
        ]
    )
    count, clearance = prior.nearby.shared.graduate.shared.check_routes(
        plans, supports, entries, former, manifest, graph, config, set(models)
    )
    return (
        models,
        records,
        science.ordered_mesh(trimesh.util.concatenate(ground)),
        count,
        clearance,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--spec", type=Path, default=SPEC)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_bytes())
    manifest_path, config_path = SCENE / "manifest.json", SCENE / "presentation.json"
    manifest, config = [
        json.loads(path.read_bytes()) for path in (manifest_path, config_path)
    ]
    terrain = SCENE / manifest["heightfield_url"]
    if (
        tools.digest(manifest_path) != spec["source_manifest_sha256"]
        or tools.digest(terrain) != spec["source_heightfield_sha256"]
    ):
        raise ValueError(
            "The chapter house split requires the registered base scene and terrain."
        )
    models, records, ground, edges, clearance = build(
        spec,
        manifest,
        config,
        json.loads(terrain.read_bytes()),
        json.loads((SCENE / "navigation.json").read_bytes()),
    )
    appearances = json.loads(
        (ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    patches = shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, appearances
    )
    output = args.stage or SCENE / DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    model, descriptor = output / "site.glb", output / "site.json"
    site.memorial.gerlinger.export(
        model, models, ground, GROUND, "chapter-house-paving"
    )
    package = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{DIRECTORY}/site.glb",
        "sha256": tools.digest(model),
        "buildings": records,
        "absorbed_ids": [],
        "split_buildings": spec["source_split"],
        "batch_removals": patches,
    }
    descriptor.write_text(
        json.dumps(package, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    if args.stage is None:
        config["chapter_house_exterior_site"] = {
            "url": f"{DIRECTORY}/site.json",
            "sha256": tools.digest(descriptor),
        }
        config_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf8",
            newline="\n",
        )
    audit = {
        "buildings": records,
        "route_edges": edges,
        "nearest_route_m": round(clearance, 4),
        "triangles": {key: len(mesh.faces) for key, mesh in models.items()},
        "batch_removals": patches,
        "split_buildings": spec["source_split"],
        "glb_sha256": package["sha256"],
        "descriptor_sha256": tools.digest(descriptor),
    }
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(
        {
            k: audit[k]
            for k in ("route_edges", "nearest_route_m", "triangles", "glb_sha256")
        }
    )


if __name__ == "__main__":
    main()
