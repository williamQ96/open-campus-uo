# SPDX-License-Identifier: Apache-2.0
"""Rebuild three Marlatt Apartment exteriors and the riverfront utility building."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import nearest_points
import trimesh

path = Path(__file__).with_name("build-east-station-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
station = module_from_spec(loader)
loader.loader.exec_module(station)
ROOT, SCENE, base, garden, geometry, prior = (
    station.ROOT,
    station.SCENE,
    station.base,
    station.garden,
    station.geometry,
    station.prior,
)
PACKAGE = "western-exterior-review"
GROUND = "western-exterior-approaches"
BRICK = (153, 99, 81)
SIDING = (168, 162, 139)
ROOF = (121, 126, 120)
TAN = (170, 153, 130)
BLOCK = (157, 149, 134)
CEMENT = (173, 165, 149)
BROWN = (101, 84, 68)
STEEL = (96, 104, 105)
METAL_ROOF = (148, 160, 160)
GALVANIZED = (143, 149, 148)


def facade_courses(add, length, bottom, top, spacing, color):
    for z in np.arange(bottom + spacing, top - 0.075, spacing):
        add(0.022, length - 0.022, 0.008, 0.027, z, z + 0.012, color)


def marlatt_window(add, u, grade, width=1.65, tall=1.26):
    station.previous.WINDOW(
        add, u, width, grade, grade + tall, BROWN, station.GLASS, ribs=3
    )


def suite_entry(add, u, z):
    add(u - 0.48, u + 0.48, 0.04, 0.156, z, z + 2.13, BROWN)
    add(u - 0.33, u + 0.33, 0.156, 0.181, z + 0.57, z + 2.00, (89, 100, 99))
    for h in (0.56, 1.28, 2.01):
        add(u - 0.35, u + 0.35, 0.176, 0.207, z + h, z + h + 0.032, BROWN)
    add(u + 0.309, u + 0.419, 0.189, 0.22, z + 1.04, z + 1.096, STEEL)


def terrace(ground, field, plan):
    def ground_z(east, north):
        return geometry.sample_ground(field, east, north) + 0.028

    floor = min(ground_z(*p) for p in plan.exterior.coords) - 0.14
    ground.append(geometry.shell(plan, floor, ground_z, CEMENT, CEMENT))


def open_stair(parts, x, lower_n, grade):
    width, run, rise = 0.93, 4.2, 2.65
    start = x - width / 2
    level = grade + rise
    flight = 14
    for i in range(flight):
        at = lower_n + (i / flight) * run
        z = grade + (i + 1) * rise / flight
        base.flat(
            parts, box(start, at, start + width, at + run / flight), z - 0.10, z, BROWN
        )
    for e in (start, start + width):
        garden.tools.beam(
            parts,
            (e, lower_n, grade + 0.87),
            (e, lower_n + run, level + 0.87),
            0.05,
            BROWN,
        )
        garden.tools.beam(
            parts,
            (e, lower_n, grade + 0.02),
            (e, lower_n + run, level - 0.11),
            0.108,
            BROWN,
        )
        for f in np.linspace(0, 1, 5):
            n = lower_n + f * run
            z = grade + f * rise
            garden.tools.beam(parts, (e, n, z), (e, n, z + 0.85), 0.049, BROWN)
    landing = box(start, lower_n + run, start + width, lower_n + run + 1.06)
    base.flat(parts, landing, level - 0.13, level, BROWN)
    for e in (start, start + width):
        garden.tools.beam(
            parts,
            (e, lower_n + run, level + 0.87),
            (e, lower_n + run + 1.06, level + 0.87),
            0.05,
            BROWN,
        )
    return box(start, lower_n, start + width, lower_n + run + 1.06)


def marlatt(parts, ground, outline, wall, floor, top, row, entry, field):
    side, door = entry
    e, n = door.coords[0]
    grade = geometry.sample_ground(field, e, n)
    courtyard = row["role"] == "courtyard"
    supports = []
    for edge, (length, add, normal, plan, _, _) in prior.building_faces(parts, wall):
        bottom = geometry.sample_ground(field, *plan(length * 0.5, 0))
        cap = min(top(plan(u, 0)) for u in (0.02, length - 0.02)) - 0.22
        brick_top = bottom + (2.64 if courtyard else 0.94)
        add(0.02, length - 0.02, 0.009, 0.061, floor, brick_top, BRICK)
        facade_courses(add, length, floor, brick_top, 0.137, (168, 119, 99))
        facade_courses(add, length, brick_top, cap, 0.204, (150, 151, 132))
        add(0.02, length - 0.02, 0.063, 0.097, brick_top, brick_top + 0.055, BROWN)
        has_entry = edge.equals(side)
        at = edge.project(door) if has_entry else None
        if courtyard:
            for u in (length * 0.18, length * 0.83):
                marlatt_window(add, u, bottom + 0.77, 1.71, 1.13)
                marlatt_window(add, u, bottom + 3.51, 1.85, 0.83)
            if has_entry:
                suite_entry(add, at, grade + 0.11)
                add(
                    at - 1.20,
                    at + 1.20,
                    0.023,
                    0.156,
                    grade + 3.0,
                    grade + 3.52,
                    (80, 111, 88),
                )
            elif normal[0] > 0.93 or normal[0] < -0.93:
                suite_entry(add, min(length - 1, 6.5), bottom + 2.65)
            continue

        inward = (row["role"] == "west" and normal[0] > 0.90) or (
            row["role"] == "east" and normal[0] < -0.90
        )
        if inward:
            divisions = 5 if row["role"] == "west" else 7
            span = length / divisions
            for index in range(divisions):
                u = (index + 0.5) * span
                door_u = at if has_entry and abs(u - at) < span * 0.44 else u + 0.38
                current_grade = geometry.sample_ground(field, *plan(door_u, 0))
                suite_entry(add, door_u, current_grade + 0.10)
                marlatt_window(add, u - span * 0.22, current_grade + 0.91, 1.69, 1.18)
                marlatt_window(add, u + span * 0.26, current_grade + 1.48, 1.12, 0.46)
                add(
                    u - span * 0.37,
                    u - span * 0.06,
                    0.079,
                    0.51,
                    current_grade + 0.08,
                    current_grade + 0.48,
                    BRICK,
                )
        elif length < 12:
            marlatt_window(add, length * 0.61, bottom + 0.94, 1.82, 1.34)
        else:
            for u in np.arange(3.72, length - 1.8, 6.5):
                marlatt_window(add, float(u), bottom + 1.46, 1.26, 0.57)
    if courtyard:
        q = outline.bounds
        for x in (q[0] - 0.44, q[2] + 0.49):
            y = -439.7
            supports.append(
                open_stair(parts, x, y, geometry.sample_ground(field, x, y))
            )
        terrace(ground, field, box(e - 1.16, n - 2.09, e + 1.16, n - 0.017))
    else:
        normal = 1 if row["role"] == "west" else -1
        start_x = e + normal * 0.22
        end_x = e + normal * 1.60
        for lo in np.arange(-472.25, -431.34, 3.2):
            hi = min(-431.34, lo + 3.2)
            terrace(
                ground, field, box(min(start_x, end_x), lo, max(start_x, end_x), hi)
            )
    return grade + 0.10, supports


def riverfront(parts, ground, outline, wall, floor, top, row, field):
    for edge, (length, add, normal, plan, _, _) in prior.building_faces(parts, wall):
        if length < 1.10:
            continue
        grade = geometry.sample_ground(field, *plan(length * 0.5, 0))
        cap = min(top(plan(u, 0)) for u in (0.10, length - 0.10)) - 0.19
        facade_courses(add, length, floor, cap, 0.208, (185, 171, 148))
        add(0.012, length - 0.012, 0.017, 0.048, floor, grade + 0.51, BLOCK)
        if normal[0] < -0.48 and normal[1] < -0.55 and length > 8:
            u = length * 0.52
            door_bottom = geometry.sample_ground(field, *plan(u, 0)) + 0.035
            add(u - 1.28, u + 1.28, 0.021, 0.19, door_bottom, door_bottom + 2.61, STEEL)
            add(
                u - 1.19,
                u + 1.19,
                0.191,
                0.221,
                door_bottom + 0.04,
                door_bottom + 2.52,
                GALVANIZED,
            )
            for height in np.arange(door_bottom + 0.13, door_bottom + 2.52, 0.09):
                add(u - 1.17, u + 1.17, 0.220, 0.243, height, height + 0.018, STEEL)
            add(
                u - 1.32, u - 1.20, 0.087, 0.251, door_bottom, door_bottom + 2.65, STEEL
            )
            add(
                u + 1.20, u + 1.32, 0.087, 0.251, door_bottom, door_bottom + 2.65, STEEL
            )
            for start, end in ((0.06, 2.15), (2.15, 4.23), (4.23, 6.19)):
                near_half = 1.35 + 0.20 * start
                far_half = 1.35 + 0.20 * end
                terrace(
                    ground,
                    field,
                    Polygon(
                        (
                            plan(u - near_half, start),
                            plan(u - far_half, end),
                            plan(u + far_half, end),
                            plan(u + near_half, start),
                        )
                    ),
                )
    # Stand the visible sheet-metal ribs on the measured roof slopes.
    frame = row["roof_frame"]
    axis = np.asarray(frame["axis"])
    across = np.array([-axis[1], axis[0]])
    origin = np.asarray(frame["origin_enu_m"])
    for along in np.arange(-7.7, 8.57, 0.45):
        center = origin + along * axis
        for a, b in ((0, -8), (0, 8)):
            chord = LineString((center + a * across, center + b * across)).intersection(
                outline.buffer(-0.045)
            )
            if chord.geom_type != "LineString" or chord.length < 0.08:
                continue
            endpoints = list(chord.coords)
            garden.tools.beam(
                parts,
                (*endpoints[0], top(endpoints[0]) + 0.026),
                (*endpoints[-1], top(endpoints[-1]) + 0.026),
                0.032,
                STEEL,
            )


def build(row, field, ground):
    outline = orient(Polygon(row["outline_enu_m"]))
    wall = orient(outline.buffer(-0.41, join_style="mitre"))
    floor, _ = garden.science.earlier.fit_base(field, outline)
    parts = []
    entrance = row["entrance"]
    gates, supports = [], []
    if entrance is None:
        top = prior.shell(parts, row, outline, wall, floor, TAN, STEEL, METAL_ROOF)
        riverfront(parts, ground, outline, wall, floor, top, row, field)
    else:
        top = prior.shell(parts, row, outline, wall, floor, SIDING, BROWN, ROOF)
        edges = list(zip(wall.exterior.coords, list(wall.exterior.coords)[1:]))
        side = LineString(
            garden.locate_face(edges, entrance["near"], entrance["bearing"])
        )
        door = nearest_points(Point(entrance["near"]), side)[1]
        assert door.distance(Point(entrance["near"])) < 0.69
        threshold, supports = marlatt(
            parts, ground, outline, wall, floor, top, row, (side, door), field
        )
        east, north = door.coords[0]
        gates = [
            dict(
                gate=entrance["gate"],
                position_enu_m=[round(east, 5), round(north, 5)],
                outward_degrees=entrance["bearing"],
                threshold_z_m=round(threshold, 4),
                width_m=1.05,
                approach_distance_m=2.12,
                estimated=True,
                snap_to_facade=False,
            )
        ]
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000018))
    record = dict(
        id=row["id"],
        name=row["name"],
        street_address=row["street_address"],
        footprint_enu_m=base.ring(outline),
        ground_footprints_enu_m=[base.ring(wall)],
        support_collision_enu_m=[base.ring(s) for s in supports],
        area_m2=round(outline.area, 3),
        base_z_m=round(floor, 4),
        roof_z_m=round(float(mesh.bounds[1, 1]), 4),
        entrances=gates,
    )
    return garden.science.ordered_mesh(mesh), record, wall, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = ROOT / "data/metadata"
    spec = json.loads((metadata / f"{PACKAGE}.json").read_bytes())
    config_path, source_path = (
        SCENE / name for name in ("presentation.json", "manifest.json")
    )
    config, manifest = (
        json.loads(path.read_bytes()) for path in (config_path, source_path)
    )
    height_path = SCENE / manifest["heightfield_url"]
    digest = garden.tools.digest
    assert digest(source_path) == spec["source_manifest_sha256"]
    assert digest(height_path) == spec["source_heightfield_sha256"]
    field = json.loads(height_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, footprints, supports = {}, [], [], [], []
    for row in spec["models"]:
        mesh, record, wall, feet = build(row, field, ground)
        meshes[row["id"]] = mesh
        records.append(record)
        footprints.append(wall)
        supports.extend(feet)
    approach = [entry for row in records for entry in row["entrances"]]
    original = union_all(
        [
            Polygon(row["footprint_enu_m"])
            for row in manifest["buildings"]
            if row["id"] in meshes
        ]
    )
    check_routes = prior.chapter.prior.nearby.shared.graduate.shared.check_routes
    count, clearance = check_routes(
        footprints, supports, approach, original, manifest, graph, config, set(meshes)
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
        model, meshes, pavement, GROUND, "western-exterior-paving"
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
        config["western_exterior_site"] = {
            "url": f"{PACKAGE}/site.json",
            "sha256": digest(descriptor),
        }
        prior.prior.write_json(config_path, config)
    audit = {
        "buildings": records,
        "batch_removals": removals,
        "route_edges": count,
        "nearest_route_m": round(clearance, 4),
        "triangles": {id: len(mesh.faces) for id, mesh in meshes.items()},
        "glb_sha256": digest(model),
        "descriptor_sha256": digest(descriptor),
    }
    prior.prior.write_json(args.audit, audit)
    print(audit["triangles"], audit["nearest_route_m"])


if __name__ == "__main__":
    main()
