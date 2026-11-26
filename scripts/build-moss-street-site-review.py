# SPDX-License-Identifier: Apache-2.0
"""Export the five Moss Street volumes, public-facing exterior and courtyard oak."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-global-scholars-site-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)
site, tools, geometry = shared.site, shared.tools, shared.geometry
roof_layer = shared.shared.roof_layer
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/moss-street-site-review.json"
DIRECTORY = "moss-street-review"
GROUND = "moss-street-approach"
OAK = "moss-street-water-oak"
SAGE = (161, 161, 134)
CREAM = (216, 210, 185)
BRICK = (162, 96, 69)
BRICK_LIGHT = (176, 109, 79)
TIMBER = (159, 122, 81)
END_GRAIN = (177, 144, 104)
ROOF = (190, 193, 185)
ROOF_EDGE = (161, 173, 167)
GLASS = (93, 119, 116)
GLASS_LIGHT = (117, 139, 130)
PAVING = (177, 168, 152)
MULCH = (139, 127, 108)


def plane(values):
    origin_e, origin_n, base, east_slope, north_slope = values
    return (
        lambda e, n: base + (e - origin_e) * east_slope + (n - origin_n) * north_slope
    )


def lower_walls(parts, plan, floor):
    boundary = box(350, -459.4, 425, -411)
    north = plan.intersection(boundary)
    south = plan.difference(boundary)
    site.flat(parts, north, floor, 10.97, SAGE, ROOF_EDGE)
    site.flat(parts, south, floor, 10.46, SAGE, ROOF_EDGE)


def upper_volume(parts, plan, zone):
    area = orient(Polygon(zone["outline_enu_m"]))
    assert area.is_valid
    z_at = plane(zone["plane"])
    base = zone["upper_wall_base_z_m"]
    clerestory = area.buffer(-0.68, join_style="mitre").intersection(plan)
    assert clerestory.area > 45
    site.surface(
        parts, clerestory, base - 0.24, lambda x, y: z_at(x, y) - 0.12, CREAM, CREAM
    )
    roof_layer(parts, area, z_at, 0.165, 0, ROOF_EDGE, ROOF)
    for region in geometry.sections(clerestory):
        outline = orient(region).exterior
        for a, b in zip(outline.coords, list(outline.coords)[1:]):
            segment = LineString((a, b))
            length = segment.length
            if length < 2.20:
                continue
            top = min(z_at(*a), z_at(*b)) - 0.34
            if top < base + 0.70:
                continue
            _, add = tools.face(parts, a, b)
            count = max(1, round(length / 3.61))
            width = length / count
            for j in range(count):
                center = (j + 0.5) * width
                add(
                    center - width * 0.19,
                    center + width * 0.19,
                    0.005,
                    0.055,
                    top - 0.53,
                    top,
                    ROOF_EDGE,
                )
                add(
                    center - width * 0.17,
                    center + width * 0.17,
                    0.055,
                    0.084,
                    top - 0.48,
                    top - 0.05,
                    GLASS,
                )
    return area, z_at


def skylights(parts, roof, z_at, name):
    placements = {
        "north main": [
            (e, -425.55)
            for e in (368.8, 373.3, 376.9, 379.3, 383.7, 386.5, 391.8, 395.3)
        ],
        "south main": [(e, -467.0) for e in (380.5, 384.1, 388.7, 393.1, 396.6, 399.9)],
        "east upper": [(403.4, -427.0), (405.0, -431.8)],
    }
    for e, n in placements.get(name, []):
        panel = box(e - 0.36, n - 0.43, e + 0.36, n + 0.43)
        if roof.contains(panel):
            roof_layer(parts, panel, z_at, 0.125, 0.151, ROOF_EDGE, GLASS_LIGHT)


def window_row(add, left, right, bottom, top, timber, divs, offset=0):
    trim = TIMBER if timber else ROOF_EDGE
    add(
        left - 0.06,
        right + 0.06,
        offset + 0.012,
        offset + 0.06,
        bottom - 0.048,
        top + 0.048,
        trim,
    )
    for b, a in zip(
        np.linspace(left, right, divs + 1)[:-1], np.linspace(left, right, divs + 1)[1:]
    ):
        add(
            b + 0.022,
            a - 0.022,
            offset + 0.060,
            offset + 0.090,
            bottom,
            top,
            GLASS if timber else GLASS_LIGHT,
        )
    for x in np.linspace(left, right, divs + 1):
        add(x - 0.022, x + 0.022, offset + 0.088, offset + 0.117, bottom, top, trim)
    add(
        left,
        right,
        offset + 0.088,
        offset + 0.124,
        bottom + (top - bottom) * 0.4,
        bottom + (top - bottom) * 0.4 + 0.052,
        trim,
    )


def elevations(parts, plan, field, gate, oak):
    ring = plan.exterior
    for a, b in zip(ring.coords, list(ring.coords)[1:]):
        edge = LineString((a, b))
        length = edge.length
        if length < 0.96:
            continue
        _, add = tools.face(parts, a, b)
        mid = (np.asarray(a) + b) * 0.5
        along = (np.asarray(b) - a) / length
        normal = np.array([along[1], -along[0]])
        toward_court = np.asarray(oak) - mid
        court = np.linalg.norm(toward_court) < 24 and normal @ toward_court > 3.0
        ground = geometry.sample_ground(field, *mid)
        top = 10.45 if mid[1] < -459.4 else 10.96
        count = max(1, round(length / (1.62 if court else 2.89)))
        step = length / count
        at_gate = edge.distance(Point(gate["position_enu_m"])) < 0.005
        door = edge.project(Point(gate["position_enu_m"])) if at_gate else None
        if court:
            add(0.013, length - 0.013, 0.013, 0.132, top - 0.24, top + 0.008, TIMBER)
        elif length > 1.08:
            add(
                0.025, length - 0.025, 0.008, 0.078, ground + 0.29, ground + 0.37, CREAM
            )
        if door is not None:
            base = gate["threshold_z_m"]
            site.allen.doors(add, door, gate["width_m"], base)
            half = min(1.50, door - 0.02, length - door - 0.02)
            if half > 1.06 and top > base + 2.72:
                window_row(
                    add, door - half, door + half, base + 2.37, top - 0.11, True, 3
                )
        for i in range(count):
            u, v = i * step, (i + 1) * step
            center = (u + v) * 0.5
            if (
                door is not None
                and abs(center - door) < gate["width_m"] / 2 + step * 0.43
            ):
                continue
            lo = ground + (0.29 if court else 0.66)
            hi = min(top - 0.20, ground + (2.65 if court else 2.48))
            if hi - lo < 0.75:
                continue
            brick = not court and (i + int(mid[0])) % 4 in (0, 1) and step > 1.42
            if brick:
                add(
                    u + 0.018,
                    v - 0.018,
                    0.018,
                    0.106,
                    ground + 0.07,
                    top - 0.043,
                    BRICK,
                )
                add(
                    u + 0.023,
                    v - 0.023,
                    0.108,
                    0.129,
                    ground + 0.10,
                    ground + 0.29,
                    BRICK_LIGHT,
                )
                add(
                    u + 0.023,
                    v - 0.023,
                    0.108,
                    0.129,
                    hi + 0.08,
                    hi + 0.22,
                    BRICK_LIGHT,
                )
            inset = min(0.36, step * 0.21)
            window_row(
                add,
                u + inset,
                v - inset,
                lo,
                hi,
                court,
                2 if step < 2.1 else 3,
                0.103 if brick else 0,
            )
            if court and step > 1.13:
                add(
                    u + 0.046,
                    u + 0.127,
                    0.031,
                    0.24,
                    ground + 0.07,
                    top - 0.065,
                    TIMBER,
                )
            if not court:
                add(
                    u + inset - 0.09,
                    v - inset + 0.09,
                    0.120,
                    0.272,
                    lo - 0.072,
                    lo - 0.016,
                    CREAM,
                )


def covers(parts, specs, field):
    supports = []
    for item in specs:
        roof = orient(Polygon(item["corners"]))
        _, s, _, n = roof.bounds
        base = item["height_m"]
        height = lambda e, y: base + (y - (n + s) / 2) * item["north_slope"]
        roof_layer(parts, roof, height, 0.18, 0, ROOF_EDGE, ROOF)
        inside = roof.buffer(-0.09)
        w, s, e, n = inside.bounds
        for x in np.arange(w + 0.35, e - 0.25, 1.05):
            rafter = inside.intersection(box(x - 0.065, s - 0.2, x + 0.065, n + 0.2))
            roof_layer(parts, rafter, height, 0.158, -0.178, TIMBER, END_GRAIN)
        shares = []
        for x, y in item["columns"]:
            assert roof.buffer(0.02).covers(Point(x, y)), (x, y)
            support = box(x - 0.142, y - 0.142, x + 0.142, y + 0.142)
            low = geometry.sample_ground(field, x, y)
            high = height(x, y) - 0.23
            site.flat(parts, support, low - 0.11, high, TIMBER)
            site.flat(
                parts,
                box(x - 0.164, y - 0.164, x + 0.164, y + 0.164),
                low,
                low + 0.19,
                ROOF_EDGE,
            )
            shares.append((x, y, high - 0.17))
            supports.append(support)
        for a, b in zip(shares, shares[1:]):
            tools.beam(parts, a, b, 0.206, TIMBER)
            p, q = np.asarray(a), np.asarray(b)
            join = p + (q - p) * 0.24
            tools.beam(parts, p - [0, 0, 0.53], join, 0.079, TIMBER)
    return supports


def branch(parts, start, end, lower_radius, upper_radius, color, *, sections=9):
    points = np.array([(e, y, -n) for e, n, y in (start, end)])
    axis = points[1] - points[0]
    section = trimesh.creation.cylinder(
        radius=1, height=np.linalg.norm(axis), sections=sections
    )
    ratio = (section.vertices[:, 2] > 0).astype(float)
    vertices = section.vertices.copy()
    vertices[:, :2] *= (lower_radius + (upper_radius - lower_radius) * ratio)[:, None]
    section.vertices = vertices
    transform = trimesh.geometry.align_vectors([0, 0, 1], axis)
    transform[:3, 3] = points.mean(axis=0)
    section.apply_transform(transform)
    section.visual.vertex_colors = [*color, 255]
    parts.append(section)


def oak_tree(spec, field):
    e, n = spec["position_enu_m"]
    ground = geometry.sample_ground(field, e, n)
    stature = spec["modeled_height_m"]
    ew, ns = np.array(spec["modeled_spread_m"]) * 0.5
    trunk = []
    branch(
        trunk,
        (e, n, ground - 0.13),
        (e + 0.34, n + 0.10, ground + 6.37),
        0.445,
        0.25,
        (104, 88, 71),
    )
    branch(
        trunk,
        (e + 0.34, n + 0.10, ground + 5.85),
        (e + 0.90, n + 0.52, ground + 12.0),
        0.255,
        0.11,
        (110, 92, 72),
    )
    foliage = []
    for i in range(12):
        theta = 2 * np.pi * i / 12 + 0.18 * np.cos(i * 4.1)
        x = np.cos(theta) * ew * (0.49 + 0.09 * np.sin(i * 3.19))
        z = np.sin(theta) * ns * (0.52 + 0.075 * np.cos(i * 2.77))
        level = (0.695 + 0.091 * np.sin(i * 1.87)) * stature
        branch(
            trunk,
            (e + 0.24, n + 0.15, ground + 4.8 + (i % 4) * 1.46),
            (e + x, n - z, ground + level - 1.55),
            0.123 + (i % 3) * 0.025,
            0.035,
            (106, 94, 74),
        )
        foliage.append(
            (
                x,
                z,
                level,
                ew * (0.33 + 0.06 * np.cos(i * 2.04)),
                ns * (0.33 + 0.06 * np.sin(i * 2.57)),
                stature * (0.169 + 0.027 * np.cos(i * 1.91)),
            )
        )
    foliage.extend(
        [
            (-1.6, -1.5, stature * 0.835, ew * 0.44, ns * 0.40, stature * 0.146),
            (2.7, 2.05, stature * 0.79, ew * 0.43, ns * 0.46, stature * 0.172),
        ]
    )
    leaves = []
    shades = [
        (98, 128, 75),
        (110, 138, 80),
        (93, 121, 70),
        (103, 135, 74),
        (120, 145, 87),
    ]
    for i, (x, z, y, w, d, h) in enumerate(foliage):
        part = trimesh.creation.icosphere(subdivisions=2)
        p = part.vertices.copy()
        vary = 1 + 0.11 * np.sin(
            p[:, 0] * 12.94 + p[:, 1] * 17.21 + p[:, 2] * 13.71 + i * 0.83
        )
        p *= vary[:, None] * np.array([w, h, d])
        p += [x, y, z]
        part.vertices = p
        part.visual.vertex_colors = [*shades[i % len(shades)], 255]
        leaves.append(part)
    crown = trimesh.util.concatenate(leaves)
    point = crown.vertices.copy()
    scale = np.array(
        [
            2 * ew / crown.extents[0],
            stature / crown.bounds[1, 1],
            2 * ns / crown.extents[2],
        ]
    )
    point[:, [0, 2]] -= crown.bounds[:, [0, 2]].mean(axis=0)
    crown.vertices = point * scale + [e, ground, -n]
    return trimesh.util.concatenate([*trunk, crown]), Point(e, n).buffer(
        0.46, quad_segs=3
    )


def validate(spec, plan, supports, entry, manifest, graph, config):
    changed = {spec["id"], *spec["absorbed_ids"]}
    collision = shapely.union_all([plan, *supports])
    sources = {
        b["id"]: Polygon(b["footprint_enu_m"]).buffer(0) for b in manifest["buildings"]
    }
    for id, footprint in sources.items():
        if id not in changed:
            assert collision.intersection(footprint).area < 0.02, id
    active = json.loads((SCENE / config["kalapuya_site"]["url"]).read_bytes())[
        "corridor_patch"
    ]
    removed = set(active["removed_edges"])
    nodes = graph["nodes_enu_m"]
    lines = [
        LineString([nodes[a], nodes[b]])
        for i, (a, b, *_) in enumerate(graph["edges"])
        if i not in removed
    ]
    for path in active["paths"]:
        points = [nodes[path["anchor"]], *path["points"]]
        lines.extend(LineString([a, b]) for a, b in zip(points, points[1:]))
    min_dist = min(route.distance(collision) for route in lines)
    assert min_dist > 0.42
    angle = np.deg2rad(entry["outward_degrees"])
    normal = np.array([np.sin(angle), np.cos(angle)])
    door = np.asarray(entry["position_enu_m"])
    approach = LineString(
        [door + normal * 0.65, door + normal * entry["approach_distance_m"]]
    )
    assert approach.distance(collision) > 0.51
    return (
        len(lines),
        round(min_dist, 3),
        [
            round(plan.intersection(sources[i["id"]]).area, 2)
            for i in spec["absorbed_batches"]
        ],
    )


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
    plan = orient(Polygon(spec["footprint_enu_m"]))
    assert plan.is_valid
    lowest = (
        min(
            geometry.sample_ground(field, *plan.exterior.interpolate(d).coords[0])
            for d in np.arange(0, plan.exterior.length, 0.55)
        )
        - 0.42
    )
    parts, ground = [], []
    entry, landing_end = site.approach(ground, field, spec["entrance"])
    lower_walls(parts, plan, lowest)
    for zone in spec["roofs"]:
        roof, z_at = upper_volume(parts, plan, zone)
        skylights(parts, roof, z_at, zone["name"])
    elevations(parts, plan, field, entry, spec["oak"]["position_enu_m"])
    supports = covers(parts, spec["covers"], field)
    tree, trunk = oak_tree(spec["oak"], field)
    supports.append(trunk)
    count, clearance, previous = validate(
        spec, plan, supports, entry, manifest, graph, config
    )

    approaches = shapely.union_all([Polygon(spec["moss_street_approach"]), landing_end])
    roads = shapely.union_all(
        [
            LineString(feature["centerline_enu_m"]).buffer(feature["width_m"] / 2)
            for feature in manifest["corridors"]["features"]
            if feature["kind"] == "road"
            and LineString(feature["centerline_enu_m"]).distance(approaches) < 8.0
        ]
    )
    approaches = approaches.difference(roads)
    court = Polygon(spec["court_surface"])
    beds = [Polygon(p) for p in spec["street_beds"]]
    decks = [Polygon(p) for p in spec["court_decks"]]
    blocked = shapely.union_all([plan, *supports])
    for regions, rgb, mask in (
        (geometry.sections(approaches), PAVING, blocked),
        ([court], MULCH, shapely.union_all([blocked, approaches, *decks])),
        (decks, (155, 139, 111), shapely.union_all([blocked, approaches])),
        (beds, (125, 143, 98), shapely.union_all([blocked, approaches, court])),
    ):
        ground.append(
            tools.approaches(
                [dict(outline=list(p.exterior.coords), rgb=rgb) for p in regions],
                field,
                mask,
            )
        )
    building = trimesh.util.concatenate(parts)
    building.update_faces(building.nondegenerate_faces(height=0.00005))
    building = shared.index_mesh(building)
    land = trimesh.util.concatenate(ground)
    appearances = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = tools.load_builder(
        "build-frohnmayer-exterior-review.py"
    ).source_removals(spec, config, appearances)
    out = SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    site.memorial.gerlinger.export(
        glb,
        {spec["id"]: building},
        land,
        GROUND,
        "moss-street-paving",
        vegetation={OAK: tree},
    )
    descriptor = out / "site.json"
    record = {k: spec[k] for k in ("id", "name", "campus_id", "footprint_enu_m")}
    record.update(
        area_m2=round(plan.area, 2),
        base_z_m=round(lowest, 4),
        roof_z_m=round(float(building.bounds[1, 1]), 4),
        entrances=[entry],
        support_collision_enu_m=[list(p.exterior.coords)[:-1] for p in supports],
    )
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        ground_node=GROUND,
        buildings=[record],
        absorbed_ids=spec["absorbed_ids"],
        batch_removals=removals,
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    config["moss_street_site"] = {
        "url": f"{DIRECTORY}/site.json",
        "sha256": tools.digest(descriptor),
    }
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit = dict(
        footprint_m2=record["area_m2"],
        old_footprint_intersection_m2=previous,
        building_triangles=len(building.faces),
        site_triangles=len(land.faces),
        tree_triangles=len(tree.faces),
        registered_oak=spec["oak"]["tree_number"],
        route_edges=count,
        minimum_route_clearance_m=clearance,
        model_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
