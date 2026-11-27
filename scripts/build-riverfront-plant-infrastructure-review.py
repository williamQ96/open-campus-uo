# SPDX-License-Identifier: Apache-2.0
"""Build the Riverfront Parkway crossing and thermal tank from registered evidence."""

import argparse
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import trimesh

previous = import_module("build-villard-orchard-walnut-review")
fairmount, garden, hilyard = previous.fairmount, previous.garden, previous.hilyard
geometry = fairmount.geometry
PACKAGE = "riverfront-plant-infrastructure-review"
GROUND = "riverfront-plant-landscape"

CONCRETE = (157, 150, 132)
RIB = (143, 136, 119)
RAIL = (99, 92, 77)
BALLAST = (125, 119, 104)
TANK = (123, 148, 140)
TRIM = (93, 121, 116)
METAL = (151, 163, 155)


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def ring(plan):
    return [list(map(float, p)) for p in list(orient(plan).exterior.coords)[:-1]]


def cap(plan, low, high, side, top=None):
    return geometry.shell(orient(plan), low, lambda *_: high, side, top or side)


def bridge(field, spec):
    center = np.asarray(spec["center_enu_m"])
    axis = np.asarray(spec["axis_enu"])
    cross = np.array([-axis[1], axis[0]])
    spans = np.asarray(spec["span_lengths_m"])
    half = spans.sum() / 2
    stations = np.concatenate(([0], np.cumsum(spans))) - half
    width = spec["finished_width_m"] / 2
    soffit = spec["girder_top_z_m"] - spec["girder_depth_m"]
    girder_top = spec["girder_top_z_m"]
    parts = []
    colliders = []

    def world(s, t):
        return center + s * axis + t * cross

    def quad(lo, hi, left, right):
        return Polygon(
            [world(lo, left), world(hi, left), world(hi, right), world(lo, right)]
        )

    def deck_piece(lo, hi, left, right, bottom, top, color, upper=None):
        parts.append(cap(quad(lo, hi, left, right), bottom, top, color, upper))

    for a, b in zip(stations[:-1], stations[1:]):
        for left, right in ((-2.057, -0.009), (0.009, 2.057)):
            deck_piece(a + 0.012, b - 0.012, left, right, soffit, girder_top, CONCRETE)
        for sign in (-1, 1):
            left, right = sorted((sign * 1.86, sign * width))
            deck_piece(
                a,
                b,
                left,
                right,
                girder_top - 0.22,
                girder_top + 0.068,
                CONCRETE,
                (173, 166, 148),
            )
            face_a, face_b = sorted((sign * 2.05, sign * 2.095))
            for s in np.arange(a + 0.13, b - 0.10, 0.16):
                deck_piece(
                    s, s + 0.039, face_a, face_b, soffit + 0.035, girder_top - 0.19, RIB
                )

    for s in stations:
        abutment = abs(s) > half - 0.1
        half_along = 0.73 if abutment else spec["pier_width_m"] / 2
        half_depth = 2.14 if abutment else spec["pier_depth_m"] / 2
        pier = quad(s - half_along, s + half_along, -half_depth, half_depth)
        ground = min(hilyard.grade(field, p) for p in pier.exterior.coords) - 0.16
        parts.append(cap(pier, ground, soffit + 0.065, CONCRETE))
        colliders.append(pier)
        if not abutment:
            for sign in (-1, 1):
                alt = sorted((sign * half_depth, sign * (half_depth + 0.035)))
                for x in np.linspace(s - half_along + 0.08, s + half_along - 0.09, 13):
                    deck_piece(x, x + 0.031, *alt, ground, soffit + 0.015, RIB)
                for z in np.arange(ground + 1.07, soffit - 0.3, 1.12):
                    deck_piece(
                        s - half_along, s + half_along, *alt, z, z + 0.038, CONCRETE
                    )

    for sign in (-1, 1):
        edge = sign * (width - 0.078)
        for z in (0.37, 0.71, 1.052):
            deck_piece(
                -half,
                half,
                edge - 0.026,
                edge + 0.026,
                girder_top + z - 0.027,
                girder_top + z + 0.023,
                RAIL,
            )
        for s in np.linspace(-half + 0.14, half - 0.14, 24):
            deck_piece(
                s - 0.034,
                s + 0.034,
                edge - 0.038,
                edge + 0.038,
                girder_top + 0.046,
                girder_top + 1.07,
                RAIL,
            )

    end = half + spec["approach_run_m"]
    bank_heights = [float(hilyard.grade(field, world(s, 0))) for s in (-end, end)]
    body = spec["ballast_top_z_m"]

    def rail_bed(s):
        return float(
            np.interp(
                s,
                [-end, -half, half, end],
                [bank_heights[0] + 0.24, body, body, bank_heights[1] + 0.24],
            )
        )

    def sloped(lo, hi, left, right, height, depth, color, upper=None):
        plan = quad(lo, hi, left, right)
        start, stop = rail_bed(lo) + height, rail_bed(hi) + height
        mesh = cap(plan, min(start, stop) - depth, min(start, stop), color, upper)
        bottom_count = np.sum(mesh.vertices[:, 1] < min(start, stop) - 0.001)
        assert bottom_count > 0
        vertices = mesh.vertices
        surface = vertices[:, 1] >= min(start, stop) - 0.001
        distance = (vertices[:, [0, 2]] * [1, -1] - center) @ axis
        levels = np.interp(distance, [lo, hi], [start, stop])
        vertices[:, 1] = np.where(surface, levels, levels - depth)
        parts.append(mesh)

    for lo, hi in ((-end, -half), (-half, half), (half, end)):
        sloped(lo, hi, -1.94, 1.94, 0, 0.45, BALLAST, (132, 128, 113))
        for t in (-0.7175, 0.7175):
            sloped(
                lo,
                hi,
                t - 0.045,
                t + 0.045,
                0.168,
                0.12,
                (118, 119, 114),
                (168, 167, 153),
            )
    for s in np.arange(-end + 0.2, end - 0.2, 0.62):
        sloped(s - 0.102, s + 0.102, -1.29, 1.29, 0.046, 0.06, (110, 99, 83))

    west_edge, east_edge = spec["road_edges_enu_m"]
    roadway = Polygon([*west_edge, *reversed(east_edge)])
    assert roadway.is_valid
    previous.drape(parts, field, roadway, (126, 127, 113), 0.088, cell=1.5)
    for edge in (west_edge, east_edge):
        walk = LineString(edge).buffer(1.36, cap_style="flat", join_style="mitre")
        previous.drape(
            parts, field, walk.difference(roadway), (172, 170, 152), 0.11, cell=1.5
        )
    median = LineString([world(0, -6.5), world(0, 6.35)]).buffer(0.96, quad_segs=8)
    assert roadway.covers(median)
    previous.drape(parts, field, median, (175, 167, 147), 0.155)
    previous.drape(parts, field, median.buffer(-0.135), (148, 129, 106), 0.175)
    for sign in (-1, 1):
        ends = sorted((sign * (half - 6.5), sign * (half + 0.12)))
        previous.drape(
            parts, field, quad(*ends, -width + 0.70, width - 0.70), CONCRETE, 0.061
        )
    return parts, colliders, soffit


def tank(field, spec):
    center = np.asarray(spec["center_enu_m"])
    radius = spec["radius_m"]
    base = spec["rim_base_z_m"]
    lip = base + spec["height_m"]
    body = Point(center).buffer(radius - 0.10, quad_segs=24)
    shell = Point(center).buffer(radius, quad_segs=24)
    footing = Point(center).buffer(radius + 0.38, quad_segs=24)
    ground = min(hilyard.grade(field, p) for p in shell.exterior.coords) - 0.22
    parts = [cap(footing, ground, base + 0.08, (154, 149, 132))]
    wall = cap(body, ground + 0.08, lip - 0.31, TANK)
    wall.update_faces(np.abs(wall.face_normals[:, 1]) < 0.1)
    wall.remove_unreferenced_vertices()
    parts.append(wall)
    parts.append(cap(shell, lip - 0.38, lip, TRIM, (133, 151, 133)))
    for height in spec["course_heights_m"]:
        z = base + height
        stroke = Point(center).buffer(radius - 0.074, quad_segs=24)
        parts.append(cap(stroke, z - 0.033, z + 0.021, (101, 125, 112)))
    crown = Point(center).buffer(radius - 0.49, quad_segs=24)
    rim = [(e, lip + 0.014, -n) for e, n in ring(crown)]
    roof = trimesh.Trimesh(
        vertices=[(center[0], lip + 0.14, -center[1]), *rim],
        faces=[(0, i + 1, (i + 1) % len(rim) + 1) for i in range(len(rim))],
        process=False,
    )
    assert np.all(roof.face_normals[:, 1] > 0.99)
    roof.visual.vertex_colors = np.repeat([[139, 155, 136, 255]], len(rim) + 1, axis=0)
    parts.append(roof)
    parts.append(
        cap(
            Point(center + [8.9, -0.52]).buffer(0.54, quad_segs=8),
            lip + 0.065,
            lip + 0.48,
            (149, 157, 148),
            (177, 179, 166),
        )
    )
    parts.append(
        cap(
            box(*(list(center + [11.7, -1.3]) + list(center + [13.8, 1.15]))),
            lip + 0.07,
            lip + 0.64,
            (151, 154, 143),
        )
    )

    def radial(deg, distance=radius + 0.21):
        angle = np.deg2rad(deg)
        return center + distance * np.array([np.cos(angle), np.sin(angle)])

    def segment(a, b, width):
        return LineString([a, b]).buffer(width / 2, cap_style="square")

    rail_degrees = np.linspace(-35, 16, 13)
    for a, b in zip(rail_degrees[:-1], rail_degrees[1:]):
        plan = segment(radial(a, radius - 0.43), radial(b, radius - 0.43), 0.059)
        for z in (lip + 0.52, lip + 1.04):
            parts.append(cap(plan, z - 0.024, z + 0.018, METAL))
    for angle in rail_degrees:
        post = Point(radial(angle, radius - 0.43)).buffer(0.049, quad_segs=2)
        parts.append(cap(post, lip, lip + 1.065, METAL))

    side_a, side_b = radial(-31.2), radial(-29.2)
    for xy in (side_a, side_b):
        parts.append(
            cap(Point(xy).buffer(0.046, quad_segs=2), base + 0.10, lip + 1.0, METAL)
        )
    for z in np.arange(base + 0.35, lip + 0.97, 0.31):
        parts.append(cap(segment(side_a, side_b, 0.040), z, z + 0.041, METAL))
    platform = box(
        *(list(center + [radius - 0.28, -0.75]) + list(center + [radius + 1.45, 0.75]))
    )
    platform_z = hilyard.grade(field, center + [radius + 1, 0]) + 0.95
    parts.append(cap(platform, platform_z - 0.17, platform_z, METAL))
    treads = []
    for step in range(6):
        d = 0.26 * step
        pad = box(
            *(
                list(center + [radius + 0.20, -0.77 - d - 0.28])
                + list(center + [radius + 1.28, -0.77 - d])
            )
        )
        top = platform_z - step * 0.16
        parts.append(cap(pad, top - 0.09, top, METAL))
        treads.append(pad)
    service = unary_union([platform, *treads])
    rail_plan = segment(
        center + [radius + 1.43, -0.72], center + [radius + 1.43, 0.72], 0.055
    )
    parts.append(cap(rail_plan, platform_z + 0.98, platform_z + 1.04, METAL))
    for n in (-0.69, 0.69):
        post = Point(center + [radius + 1.43, n]).buffer(0.042, quad_segs=2)
        parts.append(cap(post, platform_z - 0.15, platform_z + 1.045, METAL))

    ident = spec["id"]
    mesh = garden.science.ordered_mesh(trimesh.util.concatenate(parts))
    record = dict(
        id=ident,
        name=spec["name"],
        street_address=spec["street_address"],
        footprint_enu_m=ring(shell),
        support_collision_enu_m=[
            ring(component) for component in geometry.sections(service)
        ],
        area_m2=round(shell.area, 3),
        base_z_m=round(float(ground), 3),
        roof_z_m=round(float(lip + 0.14), 3),
        entrances=[],
    )
    return mesh, record, shell, footing, service


def export(stage, audit):
    scene_root = fairmount.SCENE
    spec = read(fairmount.ROOT / f"data/metadata/{PACKAGE}.json")
    manifest_path, config_path, graph_path = (
        scene_root / name
        for name in ("manifest.json", "presentation.json", "navigation.json")
    )
    manifest, config, graph = [
        read(path) for path in (manifest_path, config_path, graph_path)
    ]
    field_path = scene_root / manifest["heightfield_url"]
    field = read(field_path)
    for key, path in (
        ("manifest", manifest_path),
        ("heightfield", field_path),
        ("navigation", graph_path),
    ):
        assert digest(path) == spec[f"source_{key}_sha256"]
    parts, piers, soffit = bridge(field, spec["bridge"])
    tank_mesh, record, shell, footing, platform = tank(field, spec["tank"])
    retired = [row["id"] for row in spec["source_ranges"]]
    original = unary_union(
        [
            Polygon(row["footprint_enu_m"])
            for row in manifest["buildings"]
            if row["id"] in retired
        ]
    )
    assert len(retired) == 3 and record["id"] not in {
        row["id"] for row in manifest["buildings"]
    }
    boxes = [box(*pier.bounds) for pier in piers]
    review_routes = fairmount.chapter.prior.nearby.shared.graduate.shared.check_routes
    routes, distance = review_routes(
        [footing], [*boxes, platform], [], original, manifest, graph, config, retired
    )
    assert distance > 0.53, distance
    road_clearance = [
        soffit - hilyard.grade(field, p) for p in spec["bridge"]["road_points_enu_m"]
    ]
    assert min(road_clearance) > 4.4
    assert all(
        unary_union(boxes).distance(Point(p)) > 0.48
        for p in spec["bridge"]["road_points_enu_m"]
    )
    source_audit = read(fairmount.ROOT / "data/metadata/campus-expansion-audit.json")
    removals = garden.shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, source_audit
    )
    assert set(retired) == {r["id"] for r in removals}
    stage.mkdir(parents=True, exist_ok=True)
    model, descriptor = stage / "site.glb", stage / "site.json"
    bridge_mesh = garden.science.ordered_mesh(trimesh.util.concatenate(parts))
    garden.site.memorial.gerlinger.export(
        model, {record["id"]: tank_mesh}, bridge_mesh, GROUND, GROUND
    )
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=spec["source_heightfield_sha256"],
        ground_node=GROUND,
        url=f"{PACKAGE}/site.glb",
        sha256=digest(model),
        buildings=[record],
        batch_removals=removals,
        absorbed_ids=retired,
        new_building_ids=[record["id"]],
        closed_site_boxes_enu_m=[list(b.bounds) for b in boxes],
    )
    fairmount.write_json(descriptor, payload, compact=True)
    receipt = dict(
        asset_sha256=digest(model),
        descriptor_sha256=digest(descriptor),
        route_edges=routes,
        minimum_route_clearance_m=round(distance, 4),
        underside_enu_m=round(soffit, 4),
        road_probe_clearances_m=[round(z, 4) for z in road_clearance],
        bridge_triangles=len(bridge_mesh.faces),
        tank_triangles=len(tank_mesh.faces),
        removed_triangles=sum(b - a for a, b in (r["triangles"] for r in removals)),
        tank_plan_m2=round(shell.area, 3),
        supports=len(boxes),
    )
    fairmount.write_json(audit, receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    export(args.stage, args.audit)
