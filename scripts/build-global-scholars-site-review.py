# SPDX-License-Identifier: Apache-2.0
"""Build the registered Global Scholars Hall exterior and adjacent courtyard surfaces."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-longhouse-site-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)
site, tools, geometry = shared.site, shared.tools, shared.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/global-scholars-site-review.json"
DIRECTORY = "global-scholars-review"
GROUND = "global-scholars-approaches"
BRICK = (165, 104, 73)
BRICK_SHADE = (148, 83, 66)
CONCRETE = (193, 181, 156)
ROOF = (112, 109, 103)
TRIM = (153, 149, 137)
ROOF_SEAM = (120, 117, 109)
DORMER = (181, 178, 163)
FRAME = (83, 91, 88)
GLASS = (70, 103, 109)
PLANT = (145, 146, 104)
PAVING = (170, 163, 147)
PANEL = (102, 116, 123)
flat, surface = site.flat, site.surface


def roof_profile(parts, area, profile, base):
    coords, elevations = np.asarray(profile).T

    def height(e, n):
        return float(np.interp(n, coords, elevations))

    west, _, east, _ = area.bounds
    for lo, hi in zip(coords, coords[1:]):
        strip = area.intersection(box(west - 1, lo, east + 1, hi))
        surface(parts, strip, base, height, BRICK, ROOF)
    return height


def main_roof_detail(parts, name, area, profile, centers):
    w, _, e, _ = area.bounds
    for north_side in (False, True):
        side, shoulder = (
            (profile[-1], profile[-2]) if north_side else (profile[0], profile[1])
        )
        edge_n, edge_z = side
        sign = -1 if north_side else 1
        for i, x in enumerate(centers):
            if not north_side and i in (0, 4, 6, 13):
                continue
            width = 2.14 if i in (6, 7) else 1.84
            front_n = edge_n + sign * 0.61
            back_n = shoulder[0] + sign * 0.44
            dormer = box(
                x - width / 2, min(front_n, back_n), x + width / 2, max(front_n, back_n)
            )
            if not area.buffer(0.05).covers(dormer):
                continue
            top = shoulder[1] + 0.42
            bottom = edge_z - 0.05
            flat(parts, dormer, bottom, top, ROOF, ROOF)
            outer = [(x - width / 2, front_n), (x + width / 2, front_n)]
            if north_side:
                outer.reverse()
            length, add = tools.face(parts, *outer)
            add(0, length, 0.001, 0.116, bottom, top, DORMER)
            add(0.21, length - 0.21, 0.118, 0.163, top - 1.70, top - 0.22, FRAME)
            add(0.30, length - 0.30, 0.164, 0.180, top - 1.62, top - 0.31, GLASS)
            add(0, length, 0.163, 0.248, top - 0.058, top + 0.065, TRIM)
    for low, high in zip(profile, profile[1:]):
        if high[0] - low[0] < 1.05:
            continue
        strip = area.intersection(box(w - 1, low[0] + 0.02, e + 1, high[0] - 0.02))
        for x in np.arange(w + 0.42, e - 0.38, 1.12):
            seam = strip.intersection(box(x, low[0], x + 0.023, high[0]))
            shared.roof_layer(
                parts, seam, height_vector(low, high), 0.015, 0.017, ROOF, ROOF_SEAM
            )
    if name == "center":
        lo, hi = profile[1:3]
        bottom_n, top_n = lo[0] + 0.65, hi[0] - 0.84
        for start, stop in ((272.3, 287.6), (292.9, 328.2)):
            for x in np.arange(start, stop - 0.70, 1.04):
                panel = box(x, bottom_n, x + 0.88, top_n)
                if area.covers(panel):
                    shared.roof_layer(
                        parts, panel, height_vector(lo, hi), 0.067, 0.114, FRAME, PANEL
                    )


def height_vector(low, high):
    return lambda e, n: low[1] + (n - low[0]) * (high[1] - low[1]) / (high[0] - low[0])


def connectors(parts, remaining, commons, base):
    zones = []
    for zone in commons:
        body = remaining.intersection(box(*zone["bounds_enu_m"]))
        top = zone["roof_z_m"]
        flat(parts, body, base, top, BRICK_SHADE, TRIM)
        edge = body.difference(body.buffer(-0.16, join_style="mitre"))
        flat(parts, edge, top - 0.09, top + 0.23, BRICK_SHADE, CONCRETE)
        garden = body.buffer(-0.26).intersection(box(*zone["living_enu_m"]))
        garden_z = zone["living_z_m"]
        flat(parts, garden, top - 0.05, garden_z, CONCRETE, PLANT)
        w, s, e, n = garden.bounds
        for a, b in (
            ((w + 0.45, s + 0.55), (e - 0.55, n - 0.46)),
            ((w + 0.45, n - 0.55), (e - 0.65, s + 0.47)),
        ):
            path = (
                LineString([a, b])
                .buffer(0.23, cap_style="flat")
                .intersection(garden.buffer(-0.11))
            )
            flat(
                parts, path, garden_z - 0.014, garden_z + 0.024, PLANT, (154, 145, 122)
            )
        zones.append((body, lambda e, n, z=top: z, "commons"))
    return zones


def shell(parts, plan, spec, base):
    remaining = plan
    zones = []
    for name, profile in spec["roof_profiles"].items():
        area = remaining.intersection(box(266, profile[0][0], 334, profile[-1][0]))
        assert area.area > 740, (name, area.area)
        remaining = remaining.difference(area)
        height = roof_profile(parts, area, profile, base)
        main_roof_detail(parts, name, area, profile, spec["dormers_east_m"])
        zones.append((area, height, name))
    for item in spec["roof_west_jogs"]:
        area = remaining.intersection(box(*item["bounds_enu_m"]))
        assert area.area > 3
        remaining = remaining.difference(area)
        z = item["z_m"]
        flat(parts, area, base, z, BRICK, CONCRETE)
        zones.append((area, lambda e, n, z=z: z, "jog"))
    zones.extend(connectors(parts, remaining, spec["commons"], base))
    region_union = shapely.union_all([a for a, _, _ in zones])
    assert plan.symmetric_difference(region_union).area < 0.001
    return zones


def door(add, center, gate, length, top):
    width, base = gate["width_m"], gate["threshold_z_m"]
    safe_width = min(width, max(width * 0.68, 2 * min(center, length - center) - 0.16))
    site.allen.doors(add, center, safe_width, base)
    left, right = max(0.02, center - width * 0.83), min(
        length - 0.02, center + width * 0.83
    )
    if right - left > 2.1:
        site.allen.windows(
            add, left, right, base + 2.38, min(base + 4.55, top - 0.18), 4, True
        )
        add(left - 0.05, right + 0.05, 0.040, 0.97, base + 2.37, base + 2.55, TRIM)


def tall_wall(add, a, b, length, base, roof_at, kind, min_ground, gate, glass_detail):
    vector = (np.asarray(b) - a) / length
    west, east = min(a[0], b[0]), max(a[0], b[0])
    endwall = east - west < (length / 3)
    low = max(base + 0.30, min_ground)
    if endwall:
        center = length / 2
        top = min(roof_at(*a), roof_at(*b), 20.55)
        if length >= 3.18:
            if glass_detail and length >= 9.0:
                pad = length * 0.267
                add(center - pad, center + pad, 0.012, 0.073, low, top - 0.75, CONCRETE)
                for bottom in (8.63, 12.01, 15.46, 18.73):
                    if bottom + 1.08 < top:
                        site.allen.windows(
                            add,
                            center - pad + 0.17,
                            center + pad - 0.17,
                            bottom,
                            bottom + 1.20,
                            4,
                        )
                        add(
                            center - pad - 0.11,
                            center + pad + 0.11,
                            0.057,
                            0.46,
                            bottom - 0.12,
                            bottom,
                            CONCRETE,
                        )
            else:
                for bottom in (9.38, 12.71, 16.06, 19.19):
                    if bottom > low and bottom + 0.94 < top:
                        site.rectangular_window(
                            add, center, 1.07, bottom, bottom + 0.94, 1
                        )
        return
    top = min(roof_at(*a), roof_at(*b))
    if length > 4.1 and top >= 19.7:
        add(0, length, 0.018, 0.20, top - 0.18, top - 0.065, TRIM)
    bay_count = max(1, round(length / 3.67))
    bay_width = length / bay_count
    for index in range(bay_count):
        middle = (index + 0.5) * bay_width
        e, n = np.asarray(a) + vector * middle
        if bay_width < 1.58:
            continue
        ivory = (e < 284.2 and (kind, n > -310) != ("north", True)) or (
            326.3 < e < 329.1 and n < -344
        )
        if ivory and top > 19.6:
            add(
                index * bay_width,
                (index + 1) * bay_width,
                0.004,
                0.047,
                low,
                top - 0.20,
                CONCRETE,
            )
        if index == bay_count // 2 and length > 34 and kind != "jog":
            half = min(1.03, bay_width * 0.32)
            add(middle - half, middle + half, 0.031, 0.08, low + 0.18, 20.23, FRAME)
            for row in (8.66, 12.13, 15.48, 18.63):
                if row > low + 0.04:
                    site.allen.windows(
                        add,
                        middle - half + 0.06,
                        middle + half - 0.06,
                        row,
                        row + 1.36,
                        2,
                    )
            continue
        for row in (7.08, 10.45, 13.79, 17.10):
            if row < low - 0.28 or row + 1.48 > top - 0.42:
                continue
            if (
                gate is not None
                and row < gate[1]["threshold_z_m"] + 4.25
                and abs(middle - gate[0]) < 2.55
            ):
                continue
            width = min(bay_width * 0.62, 2.01)
            site.rectangular_window(add, middle, width, row, row + 1.34, 2)
            add(
                middle - width * 0.64,
                middle + width * 0.64,
                0.06,
                0.28,
                row + 1.36,
                row + 1.48,
                TRIM,
            )


def low_wall(add, length, base, top, gate, west_wall):
    lo = base + 0.17
    hi = min(top - 0.56, lo + (3.88 if west_wall else 3.28))
    if length < 1.30 or hi - lo < 1.70:
        return
    count = max(1, round(length / 1.42))
    if count >= 3:
        site.allen.windows(add, 0.11, length - 0.11, lo, hi, count, west_wall)
        if west_wall:
            add(0.02, length - 0.02, 0.095, 0.43, hi + 0.05, hi + 0.18, CONCRETE)
    else:
        left = max(0.15, (length - 2.03) / 2)
        site.allen.windows(add, left, length - left, lo + 0.25, hi, 2)
    if gate is not None:
        center, info = gate
        door(add, center, info, length, top)


def elevations(parts, plan, zones, field, gates, base):
    for area, roof, kind in zones:
        for piece in geometry.sections(area):
            ring = orient(piece).exterior
            for a, b in zip(ring.coords, list(ring.coords)[1:]):
                if np.linalg.norm(np.subtract(a, b)) < 0.83:
                    continue
                length, add = tools.face(parts, a, b)
                mid = (np.asarray(a) + b) * 0.5
                edge = LineString((a, b))
                direction = (np.asarray(b) - a) / length
                out = np.array([direction[1], -direction[0]])
                probe = mid + out * 0.18
                if plan.boundary.distance(Point(mid)) < 0.003:
                    visible_base = geometry.sample_ground(field, *mid)
                else:
                    visible_base = max(
                        (
                            h(*probe)
                            for other, h, _ in zones
                            if other is not area and other.contains(Point(probe))
                        ),
                        default=999,
                    )
                h = roof(*mid)
                if visible_base >= h - 0.76:
                    continue
                gate = next(
                    (
                        (edge.project(Point(g["position_enu_m"])), g)
                        for g in gates
                        if edge.distance(Point(g["position_enu_m"])) < 0.003
                    ),
                    None,
                )
                if kind == "commons":
                    low_wall(add, length, visible_base, h, gate, out[0] < -0.62)
                else:
                    tall_wall(
                        add,
                        a,
                        b,
                        length,
                        base,
                        roof,
                        kind,
                        visible_base,
                        gate,
                        out[0] < -0.62,
                    )
                    if gate is not None:
                        door(add, gate[0], gate[1], length, h)


def shelter(parts, spec, field):
    w, s, e, n = spec["bounds_enu_m"]
    height = spec["z_m"]

    def top(east, north):
        return height + (east - w) * spec["slope"]

    roof = box(w, s, e, n)
    shared.roof_layer(parts, roof, top, 0.196, 0, TRIM, CONCRETE)
    beam_n = (s + 0.23, n - 0.23)
    for x in (w + 0.14, (w + e) / 2, e - 0.14):
        for y in beam_n:
            p = box(x - 0.101, y - 0.101, x + 0.101, y + 0.101)
            ground = geometry.sample_ground(field, x, y)
            flat(parts, p, ground - 0.13, top(x, y) - 0.17, FRAME, FRAME)
            yield p


def index_mesh(mesh):
    mesh.remove_unreferenced_vertices()
    normals = mesh.vertex_normals
    colors = mesh.visual.vertex_colors
    keys = np.column_stack((mesh.vertices, normals, colors))
    vertices, indices = trimesh.grouping.unique_rows(keys, digits=6, keep_order=True)
    return trimesh.Trimesh(
        vertices=mesh.vertices[vertices],
        faces=indices[mesh.faces],
        vertex_normals=normals[vertices],
        vertex_colors=colors[vertices],
        process=False,
    )


def validations(manifest, graph, config, plan, prior, gate_records, supports):
    active = shapely.union_all([plan, *supports])
    for building in manifest["buildings"]:
        if building["id"] == prior["id"]:
            continue
        existing = Polygon(building["footprint_enu_m"]).buffer(0)
        assert active.intersection(existing).area < 0.02, building["id"]
    kalapuya = json.loads((SCENE / config["kalapuya_site"]["url"]).read_bytes())
    route_edit = kalapuya["corridor_patch"]
    omit = set(route_edit["removed_edges"])
    nodes = graph["nodes_enu_m"]
    routes = [
        LineString([nodes[a], nodes[b]])
        for i, (a, b, *_) in enumerate(graph["edges"])
        if i not in omit
    ]
    for path in route_edit["paths"]:
        points = [nodes[path["anchor"]], *path["points"]]
        routes.extend(LineString([a, b]) for a, b in zip(points, points[1:]))
    prior_outline = Polygon(prior["footprint_enu_m"])
    conflicts = [
        i
        for i, route in enumerate(routes)
        if route.distance(active) < 0.42 <= route.distance(prior_outline)
    ]
    assert not conflicts, conflicts
    for gate in gate_records:
        angle = np.radians(gate["outward_degrees"])
        bearing = np.array([np.sin(angle), np.cos(angle)])
        xy = np.asarray(gate["position_enu_m"])
        reach = gate["approach_distance_m"]
        access = LineString([xy + bearing * 0.63, xy + bearing * reach])
        assert active.distance(access) > 0.52, gate["gate"]
    return len(routes), float(min(route.distance(active) for route in routes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    plan = orient(Polygon(spec["footprint_enu_m"]))
    assert plan.is_valid
    ring = plan.exterior
    base = (
        min(
            geometry.sample_ground(field, *ring.interpolate(d).coords[0])
            for d in np.arange(0, ring.length, 0.6)
        )
        - 0.44
    )
    parts, ground, entries, paved = [], [], [], []
    for gate in spec["entrances"]:
        assert ring.distance(Point(gate["position_enu_m"])) < 0.002
        entry, path = site.approach(ground, field, gate)
        entries.append(entry)
        paved.append(path)
    zones = shell(parts, plan, spec, base)
    elevations(parts, plan, zones, field, entries, base)
    supports = [
        p
        for covered in spec["courtyard_shelters"]
        for p in shelter(parts, covered, field)
    ]
    blocked = shapely.union_all([plan, *supports])
    beds = [orient(Polygon(outline)) for outline in spec["courtyard_planting"]]
    assert all(bed.is_valid and bed.distance(plan) > 0.15 for bed in beds)
    paved.extend(Polygon(path) for path in spec["paving"])
    walkable = [
        [*p.exterior.coords] for p in geometry.sections(shapely.union_all(paved))
    ]
    ground.append(
        tools.approaches(
            [{"outline": r, "rgb": PAVING} for r in walkable],
            field,
            shapely.union_all([blocked, *beds]),
        )
    )
    ground.append(
        tools.approaches(
            [
                {"outline": list(bed.exterior.coords), "rgb": (127, 145, 100)}
                for bed in beds
            ],
            field,
            blocked,
        )
    )
    prior = next(b for b in manifest["buildings"] if b["id"] == spec["id"])
    route_count, min_distance = validations(
        manifest, graph, config, plan, prior, entries, supports
    )
    building = trimesh.util.concatenate(parts)
    building.update_faces(building.nondegenerate_faces(height=0.00005))
    building = index_mesh(building)
    land = trimesh.util.concatenate(ground)
    out = SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    site.memorial.gerlinger.export(
        glb, {spec["id"]: building}, land, GROUND, "global-scholars-paving"
    )
    record = {k: spec[k] for k in ("id", "name", "campus_id", "footprint_enu_m")}
    record.update(
        area_m2=round(plan.area, 2),
        base_z_m=round(base, 4),
        roof_z_m=round(float(building.bounds[1, 1]), 4),
        entrances=entries,
        support_collision_enu_m=[list(p.exterior.coords)[:-1] for p in supports],
    )
    descriptor = out / "site.json"
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        ground_node=GROUND,
        buildings=[record],
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    config["global_scholars_site"] = {
        "url": f"{DIRECTORY}/site.json",
        "sha256": tools.digest(descriptor),
    }
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit = dict(
        triangles=len(building.faces),
        paving_triangles=len(land.faces),
        footprint_m2=record["area_m2"],
        old_footprint_overlap_m2=round(
            plan.intersection(Polygon(prior["footprint_enu_m"])).area, 2
        ),
        roof_z_m=record["roof_z_m"],
        retained_route_edges=route_count,
        closest_active_edge_m=round(min_distance, 3),
        model_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
