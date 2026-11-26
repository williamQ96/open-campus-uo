# SPDX-License-Identifier: Apache-2.0
"""Build the registered Kalapuya exterior and the local corridor correction."""

import argparse
from importlib import import_module
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-straub-earl-site-review.py")
loader = spec_from_file_location(source.stem, source)
site = module_from_spec(loader)
loader.loader.exec_module(site)
allen, geometry, tools = site.allen, site.geometry, site.tools
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/kalapuya-site-review.json"
site_planting = import_module("build-site-planting").site_planting
DIRECTORY = "kalapuya-review"
GROUND = "kalapuya-approaches"
REMAINDER = "corridor-remainder"
BRICK = (166, 100, 73)
BRICK_LIGHT = (181, 119, 86)
DARK = (91, 90, 80)
DARK_FRAME = (72, 73, 69)
GLASS = (72, 102, 111)
FRAME = (184, 177, 156)
ROOF = (172, 170, 156)
PAVING = (167, 159, 145)
flat = site.flat


def shell(parts, model, plan, floor):
    regions = []
    remaining = plan
    for zone in model["roof_sections"]:
        area = remaining.intersection(Polygon(zone["polygon"]))
        assert area.area > 4, zone["name"]
        remaining = remaining.difference(area)
        top = zone["height"]
        color = BRICK if zone["skin"] == "brick" else DARK
        flat(parts, area, floor, top, color, ROOF)
        rim = area.difference(area.buffer(-0.17, join_style="mitre"))
        flat(parts, rim, top - 0.09, top + 0.21, color, DARK_FRAME)
        regions.append((area, lambda e, n, z=top: z, zone["skin"]))
    assert remaining.area < 0.001
    for e0, n0, e1, n1, base, top, kind in model["roof_items"]:
        area = box(e0, n0, e1, n1).intersection(plan)
        assert area.area > 1
        flat(parts, area, base, top, BRICK if kind == "brick" else DARK, ROOF)
    return regions


def facade(parts, plan, regions, field, entries):
    for a, b in zip(plan.exterior.coords, list(plan.exterior.coords)[1:]):
        for c, d, height, skin in site.science.face_spans(a, b, regions):
            length, add = tools.face(parts, c, d)
            midpoint = (np.asarray(c) + d) * 0.5
            local_ground = geometry.sample_ground(field, *midpoint)
            roof_z = height(*midpoint)
            segment = LineString((c, d))
            gate = next(
                (
                    g
                    for g in entries
                    if segment.distance(Point(g["position_enu_m"])) < 0.002
                ),
                None,
            )
            door_center = (
                None
                if not gate
                else np.linalg.norm(np.subtract(gate["position_enu_m"], c))
            )
            if length < 1.35:
                continue
            base = 6.58 if roof_z > 18 else local_ground + 0.35
            courses = (
                [base + z for z in (0, 3.08, 6.16, 9.24, 12.32)]
                if roof_z > 18
                else [base]
            )
            count = max(1, round(length / (3.13 if roof_z > 18 else 2.52)))
            step = length / count
            floor_band = 9.17 if roof_z > 18 else local_ground + 0.48
            if floor_band + 0.26 < roof_z:
                add(0, length, 0.008, 0.067, floor_band, floor_band + 0.16, BRICK_LIGHT)
            panels = (skin == "commons" or length < 5.1) and length >= 2.1
            if panels:
                add(
                    0.05,
                    length - 0.05,
                    0.03,
                    0.092,
                    courses[0] - 0.14,
                    roof_z - 0.27,
                    DARK,
                )
            for z in courses:
                if z + 1.48 > roof_z - 0.35:
                    continue
                ground_level = z == courses[0]
                if roof_z > 18 and ground_level:
                    z = max(local_ground + 0.19, base - 0.60)
                for i in range(count):
                    x = (i + 0.5) * step
                    if gate and ground_level and abs(x - door_center) < 2.8:
                        continue
                    width = step * (0.70 if panels or ground_level else 0.46)
                    site.rectangular_window(
                        add, x, width, z, z + (1.83 if ground_level else 1.43), 2
                    )
            if gate:
                floor = gate["threshold_z_m"]
                allen.doors(add, door_center, gate["width_m"], floor)
                width = min(door_center - 0.024, length - door_center - 0.024, 2.3)
                if width > 1.27:
                    allen.windows(
                        add,
                        door_center - width,
                        door_center + width,
                        floor + 2.38,
                        min(roof_z - 0.21, floor + 4.62),
                        4,
                        True,
                    )
            if roof_z > 18 and length > 8:
                for x in (0.18, length - 0.18):
                    add(
                        x - 0.11,
                        x + 0.11,
                        0.04,
                        0.12,
                        max(base, local_ground),
                        roof_z - 0.08,
                        BRICK_LIGHT,
                    )


def roof_step_facades(parts, regions):
    for high, high_at, _ in regions:
        for low, low_at, _ in regions:
            for shape in shapely.get_parts(high):
                ring = orient(shape).exterior
                for a, b in zip(ring.coords, list(ring.coords)[1:]):
                    edge = LineString((a, b))
                    for span in shapely.get_parts(edge.intersection(low.boundary)):
                        if span.geom_type != "LineString" or span.length < 1.65:
                            continue
                        start, end = sorted(
                            (span.coords[0], span.coords[-1]),
                            key=lambda pt: edge.project(Point(pt)),
                        )
                        h = span.interpolate(0.5, normalized=True)
                        lower, upper = low_at(h.x, h.y), high_at(h.x, h.y)
                        if upper - lower < 3.5:
                            continue
                        length, add = tools.face(parts, start, end)
                        count = max(1, round(length / 3.10))
                        step = length / count
                        for i in range(count):
                            center = (i + 0.5) * step
                            glass_joint = length > 10 and i == count // 2
                            if glass_joint:
                                add(
                                    center - step * 0.39,
                                    center + step * 0.39,
                                    0.014,
                                    0.084,
                                    lower + 0.08,
                                    upper - 0.18,
                                    DARK_FRAME,
                                )
                            for z in (10.11, 12.74, 15.82, 18.90):
                                if lower + 0.10 < z and z + 1.50 < upper - 0.18:
                                    site.rectangular_window(
                                        add,
                                        center,
                                        step * (0.61 if glass_joint else 0.46),
                                        z,
                                        z + 1.43,
                                        2,
                                    )


def courtyard_terrace(parts, ground_parts, field):
    # Open court canopy derived from the photographed commons frontage.
    corners = [
        (246.89, -441.41),
        (258.77, -444.66),
        (258.77, -447.09),
        (246.18, -443.72),
    ]
    cover = Polygon(corners)
    flat(parts, cover, 9.13, 9.53, DARK, ROOF)
    piers = [
        box(e - 0.14, n - 0.14, e + 0.14, n + 0.14)
        for e, n in ((246.63, -443.45), (251.91, -444.94), (257.64, -446.49))
    ]
    for post in piers:
        p = post.centroid
        flat(
            parts,
            post,
            geometry.sample_ground(field, p.x, p.y) - 0.14,
            9.16,
            BRICK,
            BRICK,
        )
    for lane in [
        Polygon(
            [(244.36, -443.8), (258.46, -447.52), (257.73, -450.07), (243.77, -446.0)]
        ),
        Polygon(
            [(256.56, -426.93), (266.87, -427.01), (266.93, -421.92), (256.55, -422.02)]
        ),
        Polygon(
            [(278.8, -469.20), (282.17, -469.22), (283.52, -477.45), (280.52, -477.25)]
        ),
    ]:
        ground_parts.append(lane)
    return piers


def unpaved_road(manifest, features, retired):
    original = trimesh.load(
        SCENE / manifest["model"]["url"], force="scene", process=False
    )
    frame, key = original.graph["corridors-road"]
    assert np.array_equal(frame, np.eye(4))
    mesh = original.geometry[key]
    overlap = shapely.union_all([area for area in features if area.intersects(retired)])
    cut = retired.difference(overlap)
    vertices = mesh.triangles
    coords = vertices[:, :, [0, 2]].copy()
    coords[:, :, 1] *= -1
    coords_lo, coords_hi = np.array(cut.bounds).reshape(2, 2)
    possible = np.flatnonzero(
        ((coords.max(1) >= coords_lo) & (coords.min(1) <= coords_hi)).all(1)
    )
    ids, verts = [], []
    recoverable = 0.0
    for index in possible:
        xy = coords[index]
        triangle = Polygon(xy)
        if triangle.intersection(cut).area <= 0.0001:
            continue
        ids.append(int(index))
        kept = triangle.difference(cut)
        if kept.area <= 0.0001:
            continue
        plane = np.linalg.solve(
            np.column_stack([xy, np.ones(3)]), vertices[index, :, 1]
        )
        for piece in shapely.get_parts(shapely.constrained_delaunay_triangles(kept)):
            assert piece.geom_type == "Polygon"
            recoverable += piece.area
            for e, n in list(orient(piece).exterior.coords)[:-1]:
                verts.append((e, e * plane[0] + n * plane[1] + plane[2], -n))
    assert 100 < len(ids) < 135 and 1 < recoverable < 6
    remainder = trimesh.Trimesh(
        verts, np.arange(len(verts)).reshape(-1, 3), process=False
    )
    slots = [ids[0] * 3, ids[len(ids) // 2] * 3 + 1, ids[-1] * 3 + 2]
    anchors = [
        [slot, np.round(vertices[slot // 3, slot % 3], 6).tolist()] for slot in slots
    ]
    return (
        remainder,
        dict(triangle_count=len(vertices), removed_triangles=ids, anchors=anchors),
        round(recoverable, 3),
    )


def route_patch(spec, graph, manifest, blocked):
    id = spec["navigation"]["corridor_id"]
    features = manifest["corridors"]["features"]
    retired = next(f for f in features if f["id"] == id)
    center = LineString(retired["centerline_enu_m"])
    nodes = graph["nodes_enu_m"]
    stale = []
    for i, (a, b, _, kind) in enumerate(graph["edges"]):
        if kind == "road" and all(
            center.distance(Point(nodes[t])) < 0.004 for t in (a, b)
        ):
            stale.append(i)
            continue
        assert LineString((nodes[a], nodes[b])).distance(blocked) >= 0.42, i
    assert len(stale) == 12
    lanes = []
    for route in spec["navigation"]["paths"]:
        path = LineString([nodes[route["anchor"]], *route["points"]])
        assert path.distance(blocked) > 0.55, route
        lanes.append(path.buffer(0.79, join_style="round"))
    return retired, stale, lanes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--spec", type=Path, default=SPEC)
    parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    nav = SCENE / "navigation.json"
    graph = json.loads(nav.read_bytes())
    plan = orient(Polygon(spec["footprint_enu_m"]))
    assert plan.is_valid
    perimeter = plan.exterior
    floor = (
        min(
            geometry.sample_ground(field, *perimeter.interpolate(i).coords[0])
            for i in np.arange(0, perimeter.length, 0.6)
        )
        - 0.46
    )
    parts, land, paving, entries = [], [], [], []
    for gate in spec["entrances"]:
        assert perimeter.distance(Point(gate["position_enu_m"])) < 0.001
        info, path = site.approach(land, field, gate)
        entries.append(info)
        paving.append(path)
    regions = shell(parts, spec, plan, floor)
    facade(parts, plan, regions, field, entries)
    roof_step_facades(parts, regions)
    piers = courtyard_terrace(parts, paving, field)
    blocked = shapely.union_all([plan, *piers])
    for b in manifest["buildings"]:
        if b["id"] != spec["id"]:
            assert (
                blocked.intersection(Polygon(b["footprint_enu_m"]).buffer(0)).area
                < 0.02
            ), b["id"]
    retired, stale, routes = route_patch(spec, graph, manifest, blocked)
    feature_areas = [
        LineString(f["centerline_enu_m"]).buffer(f["width_m"] / 2)
        for f in manifest["corridors"]["features"]
        if f["kind"] == "road" and f["id"] != retired["id"]
    ]
    paved = shapely.union_all([*paving, *routes])
    active_roads = shapely.union_all(
        [area for area in feature_areas if area.intersects(paved)]
    )
    paved = paved.difference(active_roads)
    paths = [p for p in shapely.get_parts(paved) if p.geom_type == "Polygon"]
    land.append(
        tools.approaches(
            [{"outline": list(p.exterior.coords), "rgb": PAVING} for p in paths],
            field,
            blocked,
        )
    )
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
    ground = trimesh.util.concatenate(land)
    retired_area = LineString(retired["centerline_enu_m"]).buffer(
        retired["width_m"] / 2
    )
    remainder, road, retained_area = unpaved_road(manifest, feature_areas, retired_area)
    road.update(
        id=retired["id"],
        source_navigation_sha256=sha256(nav.read_bytes()).hexdigest(),
        removed_edges=stale,
        paths=spec["navigation"]["paths"],
    )
    appearances = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = tools.load_builder(
        "build-frohnmayer-exterior-review.py"
    ).source_removals(spec, config, appearances)
    out = args.stage or SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    site.memorial.gerlinger.export(
        glb, {spec["id"]: mesh, REMAINDER: remainder}, ground, GROUND, "kalapuya-paving",
        vegetation=site_planting(spec, field, geometry.sample_ground),
    )
    descriptor = out / "site.json"
    building = {k: spec[k] for k in ("name", "id", "campus_id", "footprint_enu_m")}
    building.update(
        area_m2=round(plan.area, 2),
        base_z_m=round(floor, 4),
        roof_z_m=round(float(mesh.bounds[1, 1]), 4),
        entrances=entries,
        support_collision_enu_m=[list(p.exterior.coords)[:-1] for p in piers],
    )
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        ground_node=GROUND,
        buildings=[building],
        batch_removals=removals,
        corridor_patch=road,
        context_trees=spec.get("context_tree_removals", []),
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if args.stage is None:
        config["kalapuya_site"] = {
            "url": f"{DIRECTORY}/site.json",
            "sha256": tools.digest(descriptor),
        }
        config_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    audit = dict(
        roof_triangle_count=len(mesh.faces),
        footprint_m2=building["area_m2"],
        original_route_edges=len(graph["edges"]),
        current_route_edges=len(graph["edges"])
        - len(stale)
        + sum(len(p["points"]) for p in road["paths"]),
        retired_route_edges=stale,
        retired_road_triangles=len(road["removed_triangles"]),
        restored_road_area_m2=retained_area,
        remainder_triangles=len(remainder.faces),
        model_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
