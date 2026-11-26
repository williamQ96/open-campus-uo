# SPDX-License-Identifier: Apache-2.0
"""Build registered exteriors for the two Vivian Olum buildings."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-moss-street-site-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)
site, tools, geometry = shared.site, shared.tools, shared.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/vivian-olum-site-review.json"
DIRECTORY = "vivian-olum-review"
GROUND = "vivian-olum-approaches"
SIDING = (160, 166, 162)
LIGHT_SIDING = (167, 175, 170)
BLUE = (105, 119, 126)
SKIRT = (90, 102, 106)
TRIM = (194, 199, 186)
GLASS = (78, 112, 121)
ROOFS = {"slate": (111, 121, 125), "white": (192, 202, 196)}
FLASHING = (114, 131, 135)
TIMBER = (137, 111, 83)
PAVING = (170, 164, 149)
MULCH = (149, 131, 108)


def profiled_volume(parts, region, zone, floor, roof_color, wall):
    coordinates, elevations = np.asarray(zone["profile"]).T
    axis = zone.get("axis", 1)
    x0, y0, x1, y1 = region.bounds
    start, end = (x0, x1) if axis == 0 else (y0, y1)

    def height(e, n):
        return float(np.interp((e, n)[axis], coordinates, elevations))

    def strip(lo, hi):
        return box(lo, y0 - 1, hi, y1 + 1) if axis == 0 else box(x0 - 1, lo, x1 + 1, hi)

    breaks = [start, *(x for x in coordinates if start < x < end), end]
    for lo, hi in zip(breaks, breaks[1:]):
        section = shapely.remove_repeated_points(
            region.intersection(strip(lo, hi)), tolerance=0.00005
        )
        site.surface(parts, section.buffer(0), floor, height, wall, roof_color)
    return height


def build_shell(parts, plan, model, floor):
    remaining, zones = plan, []
    roof_color = ROOFS[model["roof_tone"]]
    wall = SIDING if model["roof_tone"] == "slate" else LIGHT_SIDING
    for zone in model["zones"]:
        region = remaining.intersection(box(*zone["bounds"]))
        assert region.area > 3, zone["name"]
        remaining = remaining.difference(region)
        height = profiled_volume(parts, region, zone, floor, roof_color, wall)
        zones.append((region, height, zone))
    z = model["low_roof_z_m"]
    site.flat(
        parts,
        shapely.remove_repeated_points(remaining, tolerance=0.00005).buffer(0),
        floor,
        z,
        wall,
        roof_color,
    )
    zones.append((remaining, lambda e, n: z, None))

    for e, n in model["roof_vents"]:
        point = Point(e, n)
        height = next((h for area, h, _ in zones if area.covers(point)), None)
        if height is not None:
            shape = box(e - 0.23, n - 0.23, e + 0.23, n + 0.23)
            top = height(e, n)
            site.flat(parts, shape, top - 0.16, top + 0.25, FLASHING)
            site.flat(
                parts,
                shape.buffer(0.06, join_style="mitre"),
                top + 0.22,
                top + 0.29,
                TRIM,
            )
    return zones


def windows(add, left, right, low, high, glass):
    add(left - 0.07, right + 0.07, 0.012, 0.085, low - 0.07, high + 0.07, TRIM)
    mid = (left + right) / 2
    add(left, mid - 0.026, 0.085, 0.113, low, high, glass)
    add(mid + 0.026, right, 0.085, 0.113, low, high, glass)
    add(
        left,
        right,
        0.105,
        0.15,
        low + (high - low) * 0.52,
        low + (high - low) * 0.52 + 0.038,
        TRIM,
    )


def public_side(add, length, base, height, gate_pos, gate, annex):
    top = height
    add(
        0.009,
        length - 0.009,
        0.011,
        0.048,
        base - 0.13,
        base + (0.47 if annex else 0.61),
        SKIRT,
    )
    if top - base > 2.21:
        line = base + min(top - base - 0.21, 2.75)
        add(0.01, length - 0.01, 0.014, 0.059, line, line + 0.078, BLUE)
        for x in np.arange(0.44, length - 0.18, 0.42):
            add(
                x,
                x + 0.012,
                0.006,
                0.028,
                base + (0.49 if annex else 0.63),
                line - 0.022,
                BLUE,
            )
    if gate_pos is not None:
        site.allen.doors(add, gate_pos, gate["width_m"], gate["threshold_z_m"])
        half = gate["width_m"] * 0.62
        add(
            gate_pos - half,
            gate_pos + half,
            0.042,
            0.435,
            gate["threshold_z_m"] + 2.36,
            gate["threshold_z_m"] + 2.51,
            FLASHING,
        )
    count = max(1, round(length / (2.84 if annex else 2.52)))
    bay = length / count
    for index in range(count):
        middle = (index + 0.5) * bay
        if gate_pos is not None and abs(middle - gate_pos) < gate["width_m"] / 2 + 0.85:
            continue
        width = min(bay * 0.64, 1.72 if annex else 1.67)
        low = base + (0.92 if annex else 0.84)
        high = min(low + 1.23, top - 0.39)
        if high - low > 0.63 and width > 0.65:
            glass = GLASS if index % 3 else (89, 119, 122)
            windows(add, middle - width / 2, middle + width / 2, low, high, glass)
            add(
                middle - width * 0.58,
                middle + width * 0.58,
                0.077,
                0.215,
                low - 0.082,
                low - 0.016,
                TRIM,
            )


def fascia(parts, edge, roof, zone, add, eave):
    a, b = np.array(edge.coords)
    axis = zone.get("axis", 1)
    delta = b[axis] - a[axis]
    corners = [a, b]
    if abs(delta) > 0.01:
        cuts = [
            (position - a[axis]) / delta
            for position, _ in zone["profile"]
            if min(a[axis], b[axis]) + 0.01 < position < max(a[axis], b[axis]) - 0.01
        ]
        corners = [a, *(a + (b - a) * t for t in sorted(cuts)), b]
    for x, y in zip(corners, corners[1:]):
        tools.beam(
            parts, (*x, roof(*x) - 0.077), (*y, roof(*y) - 0.077), 0.116, FLASHING
        )
    for u in np.arange(0.42, edge.length - 0.13, 0.42):
        point = edge.interpolate(u)
        high = roof(point.x, point.y) - 0.18
        if high - eave > 0.37:
            add(u, u + 0.012, 0.009, 0.028, eave + 0.012, high, BLUE)


def elevation(parts, zones, model, plan, gate, field):
    annex = model["roof_tone"] == "white"
    ring = plan.exterior
    for a, b in zip(ring.coords, list(ring.coords)[1:]):
        if np.linalg.norm(np.subtract(a, b)) < 0.58:
            continue
        for x, y, roof, upper in site.science.face_spans(a, b, zones):
            length, add = tools.face(parts, x, y)
            midpoint = (np.asarray(x) + y) * 0.5
            ground = geometry.sample_ground(field, *midpoint)
            height = min(roof(*x), roof(*y))
            edge = LineString((x, y))
            point = Point(gate["position_enu_m"])
            door = edge.project(point) if edge.distance(point) < 0.0025 else None
            if height - ground > 1.52 and length > 0.58:
                public_side(add, length, ground, height, door, gate, annex)
            if upper is not None and length > 0.82:
                fascia(parts, edge, roof, upper, add, height)


def roof_cover(parts, covers, field, light):
    supports = []
    for item in covers:
        outline = orient(Polygon(item["outline"]))
        west, south, east, north = outline.bounds
        z_mid = (north + south) / 2
        height = lambda e, n: item["roof"] + (n - z_mid) * item["slope"]
        shared.roof_layer(
            parts,
            outline,
            height,
            0.149,
            0,
            FLASHING,
            ROOFS["white" if light else "slate"],
        )
        for x in np.arange(west + 0.46, east - 0.17, 1.63):
            rafter = outline.intersection(box(x - 0.055, south, x + 0.055, north))
            shared.roof_layer(parts, rafter, height, 0.105, -0.147, TIMBER, TIMBER)
        tips = []
        for e, n in item["columns"]:
            footprint = box(e - 0.106, n - 0.106, e + 0.106, n + 0.106)
            assert outline.covers(Point(e, n)), (e, n)
            ground = geometry.sample_ground(field, e, n)
            top = height(e, n) - 0.16
            site.flat(parts, footprint, ground - 0.11, top, SKIRT if light else TIMBER)
            tips.append((e, n, top - 0.089))
            supports.append(footprint)
        for a, b in zip(tips, tips[1:]):
            tools.beam(parts, a, b, 0.172, TIMBER)
    return supports


def check_routes(
    plans,
    supports,
    entries,
    baselines,
    manifest,
    graph,
    config,
    ids,
    *,
    excluded_edges=(),
):
    combined = shapely.union_all([*plans, *supports])
    for building in manifest["buildings"]:
        if building["id"] not in ids:
            footprint = Polygon(building["footprint_enu_m"]).buffer(0)
            assert combined.intersection(footprint).area < 0.02, building["id"]
    scheme = json.loads((SCENE / config["kalapuya_site"]["url"]).read_bytes())[
        "corridor_patch"
    ]
    remove = set(scheme["removed_edges"]).union(excluded_edges)
    nodes = graph["nodes_enu_m"]
    edges = [
        LineString([nodes[a], nodes[b]])
        for i, (a, b, *_) in enumerate(graph["edges"])
        if i not in remove
    ]
    for path in scheme["paths"]:
        points = [nodes[path["anchor"]], *path["points"]]
        edges.extend(LineString((a, b)) for a, b in zip(points, points[1:]))
    new_conflicts = [
        i
        for i, line in enumerate(edges)
        if line.distance(combined) < 0.42 <= line.distance(baselines)
    ]
    assert not new_conflicts, new_conflicts
    for gate in entries:
        x = np.asarray(gate["position_enu_m"])
        angle = np.deg2rad(gate["outward_degrees"])
        bearing = np.array([np.sin(angle), np.cos(angle)])
        approach = LineString(
            [x + 0.66 * bearing, x + gate["approach_distance_m"] * bearing]
        )
        assert combined.distance(approach) > 0.53, gate["gate"]
    return len(edges), min(line.distance(combined) for line in edges)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    plans, supports, paving, entries, ground, records = [], [], [], [], [], []
    meshes = {}
    for model in spec["models"]:
        id = model["id"]
        plan = orient(Polygon(model["footprint_enu_m"]))
        assert plan.is_valid
        ring = plan.exterior
        floor = (
            min(
                geometry.sample_ground(field, *ring.interpolate(d).coords[0])
                for d in np.arange(0, ring.length, 0.45)
            )
            - 0.38
        )
        parts = []
        gate, slab = site.approach(ground, field, model["entrance"])
        assert ring.distance(Point(gate["position_enu_m"])) < 0.001
        zones = build_shell(parts, plan, model, floor)
        elevation(parts, zones, model, plan, gate, field)
        piers = roof_cover(parts, model["covers"], field, model["roof_tone"] == "white")
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00006))
        meshes[id] = shared.shared.index_mesh(mesh)
        plans.append(plan)
        supports.extend(piers)
        entries.append(gate)
        paving.append(slab)
        row = {k: model[k] for k in ("id", "name", "campus_id", "footprint_enu_m")}
        row.update(
            area_m2=round(plan.area, 2),
            base_z_m=round(floor, 4),
            roof_z_m=round(float(mesh.bounds[1, 1]), 4),
            entrances=[gate],
            support_collision_enu_m=[list(p.exterior.coords)[:-1] for p in piers],
        )
        records.append(row)
    assert plans[0].intersection(plans[1]).area < 0.001
    old = shapely.union_all(
        [
            Polygon(b["footprint_enu_m"]).buffer(0)
            for b in manifest["buildings"]
            if b["id"] in meshes
        ]
    )
    routes, clearance = check_routes(
        plans, supports, entries, old, manifest, graph, config, set(meshes)
    )
    blocked = shapely.union_all([*plans, *supports])
    paths = shapely.union_all([*paving, *(Polygon(p) for p in spec["paving"])])
    roads = shapely.union_all(
        [
            LineString(f["centerline_enu_m"]).buffer(f["width_m"] / 2)
            for f in manifest["corridors"]["features"]
            if f["kind"] == "road"
            and LineString(f["centerline_enu_m"]).distance(paths) < 7.0
        ]
    )
    # The aerial shows a narrow paved margin along the west side of the main building.
    paths = paths.difference(roads).union(Polygon(spec["west_walk"]))
    court = Polygon(spec["play_surface"])
    ground.append(
        tools.approaches(
            [
                dict(outline=list(p.exterior.coords), rgb=PAVING)
                for p in geometry.sections(paths)
                if p.difference(blocked).area > 0.001
            ],
            field,
            blocked,
        )
    )
    ground.append(
        tools.approaches(
            [dict(outline=list(court.exterior.coords), rgb=MULCH)],
            field,
            shapely.union_all([blocked, paths]),
        )
    )
    land = trimesh.util.concatenate(ground)
    appearance = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = tools.load_builder(
        "build-frohnmayer-exterior-review.py"
    ).source_removals(spec, config, appearance)
    out = SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    site.memorial.gerlinger.export(glb, meshes, land, GROUND, "vivian-olum-paving")
    descriptor = out / "site.json"
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        ground_node=GROUND,
        buildings=records,
        batch_removals=removals,
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    config["vivian_olum_site"] = dict(
        url=f"{DIRECTORY}/site.json", sha256=tools.digest(descriptor)
    )
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit = dict(
        footprint_m2={r["id"]: r["area_m2"] for r in records},
        triangles={id: len(mesh.faces) for id, mesh in meshes.items()},
        ground_triangles=len(land.faces),
        route_edges=routes,
        closest_route_m=round(clearance, 3),
        model_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
