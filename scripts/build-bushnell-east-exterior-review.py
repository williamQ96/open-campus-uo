# SPDX-License-Identifier: Apache-2.0
"""Build the connected East Quad academic exterior and Burke-Griffeth Hall."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import nearest_points
import trimesh

module_path = Path(__file__).with_name("build-goodrich-quad-exterior-review.py")
loader = spec_from_file_location(module_path.stem, module_path)
goodrich = module_from_spec(loader)
loader.loader.exec_module(goodrich)
ROOT, SCENE = goodrich.ROOT, goodrich.SCENE
base, garden, geometry, prior = (
    goodrich.base,
    goodrich.garden,
    goodrich.geometry,
    goodrich.prior,
)
PACKAGE = "bushnell-east-exterior-review"
GROUND = "bushnell-east-approaches"

BRICK = (151, 102, 78)
BISTRO_BRICK = (148, 99, 77)
STUCCO = (185, 181, 163)
CONCRETE = (177, 171, 152)
SOFFIT = (115, 97, 77)
TIN = (93, 96, 91)
PALE = (193, 193, 181)
LIGHT = (212, 211, 195)
GLASS = (82, 106, 118)
GLASS_BLOCK = (121, 147, 150)
METAL = (89, 92, 90)
MORTAR = (162, 129, 104)
BRICK_STREAKS = ((142, 93, 72), (121, 84, 69), (178, 115, 82), (168, 115, 90))


def brickwork(parts, point, length, bottom, top):
    vertices, faces, colors = [], [], []

    def patch(left, right, low, high, color, depth):
        start = len(vertices)
        for u, z in ((left, low), (right, low), (right, high), (left, high)):
            e, n, z = point(u, depth, z)
            vertices.append((e, z, -n))
        faces.extend(((start, start + 1, start + 2), (start, start + 2, start + 3)))
        colors.extend([(*color, 255)] * 4)

    for course, z in enumerate(np.arange(bottom, top - 0.15, 0.14)):
        patch(0.018, length - 0.018, z, z + 0.009, MORTAR, 0.010)
        for mark in range((3 * course) % 7, int((length - 0.1) / 0.39), 7):
            u = mark * 0.39 + 0.04 + (course % 2) * 0.17
            if u + 0.34 < length - 0.03:
                patch(
                    u,
                    u + 0.34,
                    z + 0.012,
                    z + 0.105,
                    BRICK_STREAKS[(course * 7 + mark // 7) % 4],
                    0.013,
                )

    if faces:
        decoration = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        decoration.visual.vertex_colors = colors
        parts.append(decoration)


def glazed_bay(add, center, width, low, high, divisions, tall=False):
    left, right = center - width / 2, center + width / 2
    add(left - 0.036, right + 0.036, 0.025, 0.075, low - 0.065, high + 0.050, METAL)
    add(left, right, 0.073, 0.103, low, high, GLASS)
    for x in np.linspace(left, right, divisions + 1):
        add(x - 0.024, x + 0.024, 0.102, 0.132, low, high, PALE)
    rails = (low, high) if not tall else (low, low + (high - low) * 0.27, high)
    for z in rails:
        add(left, right, 0.102, 0.132, z - 0.025, z + 0.025, PALE)
    add(left - 0.082, right + 0.082, 0.02, 0.185, low - 0.105, low - 0.054, BRICK)


def glass_blocks(add, center, bottom, height, width):
    columns, rows = 5, round(height / 0.17)
    x_edges = np.linspace(center - width / 2, center + width / 2, columns + 1)
    z_edges = np.linspace(bottom, bottom + height, rows + 1)
    add(
        x_edges[0] - 0.042,
        x_edges[-1] + 0.042,
        0.024,
        0.09,
        bottom - 0.042,
        bottom + height + 0.04,
        PALE,
    )
    for i, (left, right) in enumerate(zip(x_edges, x_edges[1:])):
        for j, (b, h) in enumerate(zip(z_edges, z_edges[1:])):
            tone = 6 * ((i * 3 + j * 5) % 3 - 1)
            add(
                left + 0.009,
                right - 0.009,
                0.089,
                0.127,
                b + 0.008,
                h - 0.008,
                tuple(x + tone for x in GLASS_BLOCK),
            )


def clock_portal(parts, supports, add, point, slab, u, grade):
    door_z = grade + 0.15
    for shoulder in (-2.33, -1.30, 1.30, 2.33):
        at = u + shoulder
        add(at - 0.13, at + 0.13, 0.018, 0.116, grade + 0.08, grade + 7.1, CONCRETE)
    for shoulder in (-1.83, 1.83):
        glass_blocks(add, u + shoulder, grade + 3.85, 2.70, 0.68)
        glass_blocks(add, u + shoulder, grade + 0.42, 2.44, 0.68)
    prior.prior.glazed_door(add, u, door_z, 2.12)
    add(u - 1.16, u + 1.16, 0.071, 0.145, door_z + 2.16, door_z + 2.52, GLASS)
    add(u - 1.19, u + 1.19, 0.159, 0.202, door_z + 2.48, door_z + 2.55, PALE)
    arc = [(u - 1.12, grade + 3.92), (u + 1.12, grade + 3.92)]
    arc.extend(
        (u + 1.12 * np.cos(t), grade + 6.15 + 0.28 * np.sin(t))
        for t in np.linspace(0, np.pi, 15)
    )
    pane = Polygon(arc)
    slab(pane.buffer(0.097), 0.040, 0.108, CONCRETE)
    slab(pane, 0.108, 0.137, GLASS)
    for at in (u - 0.62, u + 0.62):
        add(at - 0.024, at + 0.024, 0.136, 0.176, grade + 3.94, grade + 6.38, PALE)
    for z, depth in ((grade + 6.86, 0.22), (grade + 7.03, 0.29)):
        add(u - 2.67, u + 2.67, 0.028, depth, z, z + 0.12, CONCRETE)
    z = grade + 8.46
    parapet = Polygon(
        [
            (u - 1.38, grade + 7.12),
            (u + 1.38, grade + 7.12),
            (u + 1.38, z + 0.37),
            (u + 0.72, z + 0.53),
            (u, z + 0.59),
            (u - 0.72, z + 0.53),
            (u - 1.38, z + 0.37),
        ]
    )
    slab(parapet, -0.15, 0.115, STUCCO)
    slate = Point(u, z).buffer(0.41, quad_segs=10)
    slab(slate, 0.110, 0.152, METAL)
    slab(Point(u, z).buffer(0.377, quad_segs=10), 0.151, 0.192, LIGHT)
    for angle in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        a, b = np.cos(angle), np.sin(angle)
        garden.tools.beam(
            parts,
            point(u + 0.31 * a, 0.203, z + 0.31 * b),
            point(u + 0.355 * a, 0.203, z + 0.355 * b),
            0.016,
            METAL,
        )
    for dx, dy in ((0.064, 0.302), (0.183, 0.096)):
        garden.tools.beam(
            parts, point(u, 0.213, z), point(u + dx, 0.213, z + dy), 0.027, METAL
        )

    add(u - 1.48, u + 1.48, 0.01, 1.37, grade + 2.85, grade + 3.03, CONCRETE)
    for du in (-1.37, 1.37):
        post = point(u + du, 1.13, door_z)
        east, north, _ = post
        supports.append(box(east - 0.075, north - 0.075, east + 0.075, north + 0.075))
        garden.tools.beam(
            parts,
            post,
            point(u + du, 1.13, grade + 2.86),
            0.15,
            CONCRETE,
        )
    return door_z


def covering(parts, outline, wall, floor, row):
    surfaces = {
        **row,
        "wall_color": BRICK,
        "trim_color": SOFFIT,
        "roof_color": (166, 167, 158),
    }
    return garden.roof_sections(parts, outline, wall, floor, surfaces, grid=0.0002)


def entry_edge(wall, entry):
    edges = list(zip(wall.exterior.coords, list(wall.exterior.coords)[1:]))
    start, end = garden.locate_face(edges, entry["near"], entry["bearing"])
    door = nearest_points(Point(entry["near"]), LineString((start, end)))[1]
    return (start, end), door


def library_walk(ground, field, e, n):
    def elevation(east, north):
        return geometry.sample_ground(field, east, north) + 0.034

    def edges(distance):
        center = n + 1.32 * distance / 16
        half = 1.66 - 0.12 * distance / 16
        return (e - distance, center - half), (e - distance, center + half)

    for start in np.arange(0.035, 16, 1.6):
        bottom, top = edges(start)
        next_bottom, next_top = edges(min(start + 1.6, 16))
        path = Polygon((bottom, next_bottom, next_top, top))
        base_z = min(elevation(*pt) for pt in path.exterior.coords) - 0.12
        ground.append(geometry.shell(path, base_z, elevation, CONCRETE, CONCRETE))


def library(parts, ground, supports, outline, wall, floor, row, field, door_line, door):
    top = covering(parts, outline, wall, floor, row)
    threshold = None
    for edge, (width, add, normal, plan, point, slab) in prior.building_faces(
        parts, wall
    ):
        if width < 1.02:
            continue
        e, n = plan(width * 0.5, 0)
        grade = geometry.sample_ground(field, e, n)
        if edge.equals(LineString(door_line)):
            u = edge.project(door)
            e, n = door.coords[0]
            grade = geometry.sample_ground(field, e, n)
            add(
                0.04,
                width - 0.04,
                0.006,
                0.049,
                floor,
                min(top(plan(t, 0)) for t in (0.3, width - 0.3)) - 0.13,
                STUCCO,
            )
            threshold = clock_portal(parts, supports, add, point, slab, u, grade)
            library_walk(ground, field, e, n)
            for side in (-1.47, 1.47):
                garden.tools.beam(
                    parts,
                    point(u + side, 1.21, grade + 0.89),
                    point(u + side, 2.39, grade + 0.71),
                    0.039,
                    METAL,
                )
                for d in (1.21, 2.39):
                    garden.tools.beam(
                        parts,
                        point(u + side, d, grade + 0.04),
                        point(u + side, d, grade + (0.89 if d < 2 else 0.71)),
                        0.038,
                        METAL,
                    )
        elif n >= 202.50:
            left, right = 0.023, width - 0.023
            high = min(top(plan(t, 0)) for t in (left, width * 0.5, right))
            add(left, right, 0.008, 0.044, floor, high - 0.15, STUCCO)
            for z in (grade + 1.04, grade + 4.11, grade + 7.26):
                add(0.023, width - 0.023, 0.046, 0.103, z - 0.092, z, CONCRETE)
                for u in np.arange(1.38, width - 0.92, 2.37):
                    cap = top(plan(u, 0))
                    if cap - z > 1.45:
                        glazed_bay(add, u, 1.04, z + 0.13, min(z + 1.71, cap - 0.29), 2)
        else:
            low_cap = min(top(plan(t, 0)) for t in (0.21, width - 0.21))
            brickwork(parts, point, width, floor + 0.12, low_cap - 0.22)
            spaces = max(1, round(width / (4.48 if normal[1] > 0.95 else 4.08)))
            bay = width / spaces
            for u in (np.arange(spaces) + 0.5) * bay:
                cap = top(plan(u, 0))
                if bay > 1.5:
                    glazed_bay(
                        add,
                        float(u),
                        bay * 0.79,
                        grade + 0.86,
                        grade + 3.22,
                        3,
                        tall=True,
                    )
                    if cap - grade > 5.35:
                        glazed_bay(
                            add,
                            float(u),
                            bay * 0.79,
                            grade + 4.36,
                            min(cap - 0.44, grade + 7.27),
                            3,
                            tall=True,
                        )
    for e, n in ((-650.5, 179.0), (-650.5, 171.1)):
        z = top((e, n))
        base.flat(
            parts,
            box(e - 0.57, n - 0.82, e + 0.57, n + 0.82),
            z - 0.06,
            z + 0.34,
            (137, 139, 135),
        )
    assert threshold is not None
    return threshold


def burke(parts, ground, supports, outline, wall, floor, row, field, door_line, door):
    roof_height = covering(parts, outline, wall, floor, row)
    threshold = None
    for edge, (length, add, normal, plan, point, _) in prior.building_faces(
        parts, wall
    ):
        if length < 1.0:
            continue
        midpoint = plan(length / 2, 0)
        grade = geometry.sample_ground(field, *midpoint)
        spot = edge.project(door) if edge.equals(LineString(door_line)) else None
        if spot is not None:
            e, n = door.coords[0]
            threshold = geometry.sample_ground(field, e, n) + 0.18
            prior.prior.glazed_door(add, spot, threshold, 1.67)
            add(
                spot - 1.16,
                spot + 1.16,
                0.01,
                1.05,
                threshold + 2.44,
                threshold + 2.62,
                TIN,
            )
            prior.prior.paving(ground, e, n, threshold - 0.18, (0, 1), 2.52, 2.35)
        nslots = max(1, int(round(length / 3.56)))
        module = length / nslots
        # Terraced wall edges can cross a roof step. Sample their bands locally.
        for left, right in zip(
            np.linspace(0.024, length - 0.024, nslots + 1),
            np.linspace(0.024, length - 0.024, nslots + 1)[1:],
        ):
            span = right - left
            mid = (left + right) / 2
            e, n = plan(mid, 0)
            roof_z = min(
                roof_height(plan(t, 0)) for t in (left + 0.034, mid, right - 0.034)
            )
            for course_z in (grade + 2.85, grade + 5.80):
                if course_z < roof_z - 0.30:
                    add(
                        left,
                        right,
                        0.018,
                        0.066,
                        course_z,
                        course_z + 0.075,
                        BISTRO_BRICK,
                    )
            if span < 1.4:
                continue
            is_entry = spot is not None and abs(mid - spot) < max(1.78, module * 0.52)
            if not is_entry:
                if n > 155 and e < -716:
                    glazed_bay(
                        add,
                        mid,
                        span * 0.74,
                        grade + 0.67,
                        min(grade + 2.38, roof_z - 0.45),
                        3,
                        tall=True,
                    )
                else:
                    glazed_bay(
                        add,
                        mid,
                        min(2.18, span * 0.69),
                        grade + 0.80,
                        min(grade + 2.49, roof_z - 0.37),
                        2,
                        tall=True,
                    )
            for z in (grade + 3.42, grade + 6.24):
                if roof_z > z + 1.49:
                    glazed_bay(
                        add,
                        mid,
                        min(1.94, span * 0.65),
                        z,
                        min(z + 1.33, roof_z - 0.41),
                        3,
                    )
            if len(edge.coords) and normal[1] > 0.90 and abs(left - 0.024) < 0.01:
                add(
                    left + 0.076,
                    left + 0.158,
                    0.029,
                    0.102,
                    grade + 0.35,
                    roof_z - 0.19,
                    TIN,
                )
        # Shallow projecting mortar and accented individual bricks on the quadrangle sides.
        if normal[1] > 0.80 or normal[0] > 0.85:
            for left in np.arange(0.01, length, 5.5):
                right = min(length - 0.01, left + 5.5)
                low_cap = min(
                    roof_height(plan(u, 0))
                    for u in (left + 0.004, (left + right) / 2, right - 0.004)
                )
                if right - left > 0.28:
                    brickwork(
                        parts,
                        lambda u, d, z, left=left: point(left + u, d, z),
                        right - left,
                        floor + 0.08,
                        low_cap - 0.18,
                    )
    for e, n, width, depth, up in (
        (-709.14, 146.3, 1.42, 0.92, 0.68),
        (-674.2, 150.75, 1.09, 1.12, 1.25),
        (-724.8, 160.0, 1.55, 1.38, 0.64),
    ):
        z = roof_height((e, n))
        base.flat(
            parts,
            box(e - width / 2, n - depth / 2, e + width / 2, n + depth / 2),
            z - 0.36,
            z + up,
            BRICK,
            TIN,
        )
    assert threshold is not None
    return threshold


def build(row, field, ground):
    outline = orient(Polygon(row["outline_enu_m"]))
    wall = orient(outline.buffer(-0.39, join_style="mitre"))
    floor, _ = garden.science.earlier.fit_base(field, outline)
    entry = row["entrance"]
    door_line, door = entry_edge(wall, entry)
    assert door.distance(Point(entry["near"])) < 0.73
    parts, supports = [], []
    author = library if row["role"] == "library" else burke
    threshold = author(
        parts, ground, supports, outline, wall, floor, row, field, door_line, door
    )
    e, n = door.coords[0]
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000018))
    record = {
        "id": row["id"],
        "name": row["name"],
        "street_address": row["street_address"],
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(wall)],
        "support_collision_enu_m": [base.ring(post) for post in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [
            {
                "gate": entry["gate"],
                "position_enu_m": [round(e, 5), round(n, 5)],
                "outward_degrees": entry["bearing"],
                "approach_distance_m": entry["distance"],
                "threshold_z_m": round(threshold, 4),
                "width_m": entry["width_m"],
                "estimated": True,
                "snap_to_facade": False,
            }
        ],
    }
    return garden.science.ordered_mesh(mesh), record, wall, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = ROOT / "data/metadata"
    spec = json.loads((metadata / f"{PACKAGE}.json").read_bytes())
    config_path, source_path = SCENE / "presentation.json", SCENE / "manifest.json"
    config, manifest = (
        json.loads(path.read_bytes()) for path in (config_path, source_path)
    )
    height_path = SCENE / manifest["heightfield_url"]
    digest = garden.tools.digest
    assert digest(source_path) == spec["source_manifest_sha256"]
    assert digest(height_path) == spec["source_heightfield_sha256"]
    field = json.loads(height_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, plans, supports = {}, [], [], [], []
    for row in spec["models"]:
        mesh, record, wall, posts = build(row, field, ground)
        meshes[row["id"]] = mesh
        records.append(record)
        plans.append(wall)
        supports.extend(posts)
    gates = [entry for row in records for entry in row["entrances"]]
    old = goodrich.union_all(
        [
            Polygon(row["footprint_enu_m"])
            for row in manifest["buildings"]
            if row["id"] in meshes
        ]
    )
    check_routes = prior.chapter.prior.nearby.shared.graduate.shared.check_routes
    count, clearance = check_routes(
        plans, [], gates, old, manifest, graph, config, set(meshes)
    )
    appearances = json.loads((metadata / "campus-expansion-audit.json").read_bytes())
    removals = garden.shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, appearances
    )
    target = args.stage or SCENE / PACKAGE
    target.mkdir(exist_ok=True, parents=True)
    model, descriptor = target / "site.glb", target / "site.json"
    pavement = garden.science.ordered_mesh(trimesh.util.concatenate(ground))
    garden.site.memorial.gerlinger.export(
        model, meshes, pavement, GROUND, "bushnell-east-paving"
    )
    package = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": digest(model),
        "buildings": records,
        "batch_removals": removals,
    }
    prior.prior.write_json(descriptor, package, compact=True)
    if args.stage is None:
        config["bushnell_east_site"] = {
            "url": f"{PACKAGE}/site.json",
            "sha256": digest(descriptor),
        }
        prior.prior.write_json(config_path, config)
    audit = {
        "buildings": records,
        "batch_removals": removals,
        "route_edges": count,
        "nearest_route_m": round(clearance, 4),
        "triangles": {key: len(mesh.faces) for key, mesh in meshes.items()},
        "glb_sha256": digest(model),
        "descriptor_sha256": digest(descriptor),
    }
    prior.prior.write_json(args.audit, audit)
    print(audit["triangles"], audit["nearest_route_m"])


if __name__ == "__main__":
    main()
