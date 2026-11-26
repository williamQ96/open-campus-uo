# SPDX-License-Identifier: Apache-2.0
"""Rebuild the three registered East Station exteriors."""

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

path = Path(__file__).with_name("build-goodrich-quad-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
previous = module_from_spec(loader)
loader.loader.exec_module(previous)
ROOT, SCENE = previous.ROOT, previous.SCENE
base, garden, geometry, prior = (
    previous.base,
    previous.garden,
    previous.geometry,
    previous.prior,
)
PACKAGE = "east-station-exterior-review"
GROUND = "east-station-frontages"
CONCRETE = (168, 165, 149)
TAN = (165, 161, 139)
BEIGE = (181, 172, 147)
GRAY = (148, 152, 146)
BROWN = (127, 112, 95)
METAL = (73, 83, 99)
SEAM = (100, 107, 113)
FRAME = (191, 188, 167)
DRIP = (96, 101, 96)
GLASS = (72, 93, 103)


def facade_trim(add, width, floor, top, horizontal):
    if horizontal:
        for z in np.arange(floor + 0.43, top - 0.06, 0.19):
            add(0.028, width - 0.028, 0.005, 0.029, z, z + 0.012, GRAY)
    else:
        for u in np.arange(0.05, width - 0.05, 0.5):
            add(u, u + 0.024, 0.008, 0.028, floor, top - 0.06, TAN)


def front_door(add, center, threshold, *, muted=False):
    width = 1.15 if muted else 1.03
    left = center - width / 2
    right = center + width / 2
    add(left - 0.07, right + 0.07, 0.015, 0.115, threshold, threshold + 2.21, FRAME)
    add(
        left,
        right,
        0.115,
        0.143,
        threshold + 0.025,
        threshold + 2.15,
        GRAY if muted else TAN,
    )
    add(
        right - 0.35,
        right - 0.15,
        0.143,
        0.163,
        threshold + 1.28,
        threshold + 1.89,
        GLASS,
    )
    add(
        right - 0.25,
        right - 0.08,
        0.145,
        0.195,
        threshold + 0.95,
        threshold + 0.996,
        DRIP,
    )


def roof_ribs(parts, height):
    # Two orientations follow the four slopes of the standing-seam roof.
    for e in np.arange(786.32, 800.38, 0.37):
        for n0, n1, sign in ((-230.09, -220.18, 1), (-201.98, -207.83, -1)):
            n2 = n0 + sign * min(abs(n1 - n0), min(e - 786.0, 800.5 - e) * 1.125)
            if abs(n2 - n0) > 0.09:
                garden.tools.beam(
                    parts,
                    (e, n0, height((e, n0)) + 0.02),
                    (e, n2, height((e, n2)) + 0.02),
                    0.035,
                    SEAM,
                )
    for n in np.arange(-229.91, -202.1, 0.37):
        for e0, e1, sign in ((786.17, 792.68, 1), (800.32, 792.68, -1)):
            dx = min(abs(e1 - e0), min(n + 230.3, -201.75 - n) * 0.89)
            e2 = e0 + sign * dx
            if abs(e2 - e0) > 0.09:
                garden.tools.beam(
                    parts,
                    (e0, n, height((e0, n)) + 0.023),
                    (e2, n, height((e2, n)) + 0.023),
                    0.035,
                    SEAM,
                )


def lobby_canopy(parts, ground, e, n, grade):
    half = 1.73
    depth = 1.32
    eave = grade + 2.57
    pitch = 0.43
    for left, right, slope in ((e - half, e, 1), (e, e + half, -1)):
        plan = box(left, n - depth, right, n + 0.18)

        def top(east, _north, slope=slope):
            return eave + pitch * (half + slope * (east - e))

        parts.append(geometry.shell(plan, eave - 0.13, top, BROWN, METAL))
    base.flat(
        ground,
        box(e - half - 0.08, n - 1.33, e + half + 0.08, n + 0.03),
        grade - 0.18,
        grade + 0.11,
        CONCRETE,
    )
    prior.prior.paving(ground, e, n - 1.33, grade - 0.01, (0, -1), 1.91, 2.93)
    supports = []
    for x in (e - 1.46, e + 1.46):
        leg = box(x - 0.081, n - 1.09, x + 0.081, n - 0.93)
        supports.append(leg)
        base.flat(parts, leg, grade + 0.08, eave - 0.06, BEIGE)
    return supports


def main_finish(parts, ground, wall, floor, height, door, facing, ground_field):
    e, n = door.coords[0]
    grade = geometry.sample_ground(ground_field, e, n)
    for edge, (width, add, normal, plan, _, _) in prior.building_faces(parts, wall):
        wall_top = min(height(plan(u, 0)) for u in (0.07, width - 0.07)) - 0.18
        facade_trim(add, width, floor, wall_top, horizontal=False)
        add(0.019, width - 0.019, 0.018, 0.072, floor + 0.1, grade + 0.18, CONCRETE)
        if edge.equals(facing):
            u = edge.project(door)
            front_door(add, u, grade + 0.11)
            front_door(add, u + 2.3, grade + 0.10)
            for point in (u - 3.14, u + 4.36, u + 6.17):
                previous.sash_window(add, point, 1.30, grade + 0.66, grade + 2.15)
        else:
            count = max(2, int(width / 4.1)) if normal[1] < 0.9 else 3
            for point in (np.arange(count) + 0.5) * width / count:
                previous.sash_window(
                    add, float(point), 1.32, grade + 0.67, grade + 2.13
                )
    roof_ribs(parts, height)
    for x, y in ((795.0, -214.4), (791.2, -208.4), (796.75, -217.4)):
        z = height((x, y))
        base.flat(
            parts, box(x - 0.14, y - 0.14, x + 0.14, y + 0.14), z - 0.06, z + 0.23, DRIP
        )
    return grade + 0.11, lobby_canopy(parts, ground, e, n, grade)


def annex_finish(parts, ground, wall, floor, height, door, facing, ground_field, role):
    e, n = door.coords[0]
    grade = geometry.sample_ground(ground_field, e, n)
    for edge, (width, add, normal, plan, _, _) in prior.building_faces(parts, wall):
        cap = min(height(plan(u, 0)) for u in (0.06, width - 0.06))
        local_grade = geometry.sample_ground(ground_field, *plan(width / 2, 0))
        facade_trim(add, width, floor, cap - 0.19, horizontal=True)
        add(
            0.03,
            width - 0.03,
            0.016,
            0.065,
            local_grade + 0.38,
            local_grade + 0.63,
            CONCRETE,
        )
        opening = edge.project(door) if edge.equals(facing) else None
        if opening is not None:
            front_door(add, opening, grade + 0.08, muted=True)
        if width > 24:
            visible_band = role == "annex-a" and normal[1] < -0.9
            spacing = 2.93 if visible_band else 5.42
            for u in np.arange(spacing * 0.62, width - 1.0, spacing):
                if opening is not None and abs(u - opening) < 1.16:
                    continue
                sill = local_grade + (1.99 if visible_band else 1.29)
                previous.sash_window(
                    add,
                    float(u),
                    1.04 if visible_band else 1.24,
                    sill,
                    sill + (0.42 if visible_band else 0.65),
                )
        elif normal[0] > 0.9:
            previous.sash_window(
                add, width * 0.49, 1.45, local_grade + 1.13, local_grade + 2.0
            )
    prior.prior.paving(
        ground,
        e,
        n,
        grade,
        (
            float(np.sin(np.deg2rad(180 if role == "annex-a" else 194.42))),
            float(np.cos(np.deg2rad(180 if role == "annex-a" else 194.42))),
        ),
        1.78,
        2.72,
    )
    return grade + 0.08, []


def ridge_vents(parts, row, top):
    frame = row["roof_frame"]
    along = np.asarray(frame["axis"])
    across = np.array([-along[1], along[0]])
    center = np.asarray(frame["origin_enu_m"])
    u_positions = (
        (-16.5, -9.6, 3.25, 12.3, 20.15)
        if row["role"] == "annex-b"
        else (5.6, 11.9, 14.8)
    )
    for u in u_positions:
        e, n = (
            center + u * along + (0.34 if row["role"] == "annex-b" else -0.82) * across
        )
        z = top((e, n))
        base.flat(
            parts, box(e - 0.17, n - 0.17, e + 0.17, n + 0.17), z - 0.17, z + 0.32, DRIP
        )
        base.flat(
            parts, box(e - 0.21, n - 0.21, e + 0.21, n + 0.21), z + 0.22, z + 0.36, GRAY
        )


def build(row, field, ground):
    outline = orient(Polygon(row["outline_enu_m"]))
    wall = orient(outline.buffer(-0.41, join_style="mitre"))
    floor, _ = garden.science.earlier.fit_base(field, outline)
    entrance = row["entrance"]
    door_edge = garden.locate_face(
        list(zip(wall.exterior.coords, list(wall.exterior.coords)[1:])),
        entrance["point"],
        entrance["bearing"],
    )
    facing = LineString(door_edge)
    door = nearest_points(Point(entrance["point"]), facing)[1]
    assert door.distance(Point(entrance["point"])) < 0.6
    parts = []
    is_main = row["role"] == "main"
    wall_color = BEIGE if is_main else GRAY
    roof = METAL if is_main else BROWN
    top = prior.shell(parts, row, outline, wall, floor, wall_color, DRIP, roof)
    if is_main:
        threshold, supports = main_finish(
            parts, ground, wall, floor, top, door, facing, field
        )
    else:
        threshold, supports = annex_finish(
            parts, ground, wall, floor, top, door, facing, field, row["role"]
        )
        ridge_vents(parts, row, top)
    e, n = door.coords[0]
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000018))
    record = {
        "id": row["id"],
        "name": row["name"],
        "campus_id": row["campus_id"],
        "street_address": row["street_address"],
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(wall)],
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [
            {
                "gate": entrance["gate"],
                "position_enu_m": [round(e, 5), round(n, 5)],
                "outward_degrees": entrance["bearing"],
                "threshold_z_m": round(threshold, 4),
                "approach_distance_m": 2.7,
                "width_m": 1.17,
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
        model, meshes, pavement, GROUND, "east-station-paving"
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
        config["east_station_site"] = {
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
