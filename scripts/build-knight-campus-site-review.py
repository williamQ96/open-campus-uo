# SPDX-License-Identifier: Apache-2.0
"""Build the registered Knight Campus exterior and two exterior bridge spans."""

import argparse
from importlib import import_module
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

loader = spec_from_file_location(
    "science_site", Path(__file__).with_name("build-northeast-science-site-review.py")
)
science = module_from_spec(loader)
loader.loader.exec_module(science)
prior, site, tools = science.prior, science.site, science.tools
flat, union, ring = science.flat, science.union, science.ring
geometry, shared = science.geometry, science.shared
SCENE = science.SCENE
SPEC = geometry.ROOT / "data/metadata/knight-campus-site-review.json"
site_planting = import_module("build-site-planting").site_planting
DIRECTORY = "knight-campus-review"
GROUND = "knight-campus-grounds"

PALE = (211, 217, 215)
ROOF = (172, 181, 176)
GLASS = (65, 103, 109)
COOL_GLASS = (89, 123, 129)
SCREEN = ((131, 169, 170), (166, 192, 190), (113, 150, 153), (152, 181, 181))
SHADE = ((176, 182, 171), (198, 201, 188), (157, 174, 167))
FRAME = (64, 82, 82)
DARK = (66, 75, 74)
EDGE = (158, 169, 166)
METAL = (189, 196, 188)
FRAME_LIGHT = (159, 172, 166)
CONCRETE = (174, 169, 153)
CANOPY = (194, 206, 200)
PAVING = (172, 166, 149)
WATER = (78, 111, 107)


def tower_shell(parts, footprint, bottom, roof, glass=GLASS):
    flat(parts, footprint, bottom, roof, glass, ROOF)
    # A thin pale coping follows the plan, with no inset triangulation seam.
    for a, b in shared.face_edges(footprint):
        length, add = tools.face(parts, a, b)
        if length > 0.18:
            add(0.016, length - 0.016, -0.018, 0.058, roof - 0.07, roof + 0.065, METAL)


def facet(parts, a, b, corners, tones):
    _, coordinate = shared.heritage.memorial.coordinate(a, b)
    vertices = []
    for along, outward, height in corners:
        e, n = coordinate(along, outward)
        vertices.append((e, height, -n))
    for triangle, color in zip(((0, 1, 2), (0, 2, 3)), tones):
        mesh = trimesh.Trimesh(
            [vertices[i] for i in triangle], [[0, 1, 2]], process=False
        )
        mesh.visual.vertex_colors = [*color, 255]
        parts.append(mesh)


def folded_glass(parts, a, b, bottom, roof):
    length, add = tools.face(parts, a, b)
    panels = max(1, round(length / 2.37))
    pitch = length / panels
    z_bins = np.linspace(bottom, roof - 0.14, 6)
    for j, (low, top) in enumerate(zip(z_bins, z_bins[1:])):
        for i in range(panels):
            left, right = i * pitch + 0.025, (i + 1) * pitch - 0.025
            depth = 0.86 if (i + j) % 2 == 0 else 0.61
            corners = [
                (left, 0.15, low),
                (right, depth, low + 0.025),
                (right, 0.16, top),
                (left, depth, top - 0.025),
            ]
            facet(parts, a, b, corners, (SCREEN[(i + j) % 4], SCREEN[(i + j + 1) % 4]))
        add(0.045, length - 0.045, 0.035, 0.22, low - 0.054, low + 0.041, FRAME_LIGHT)
    for u in np.linspace(0.08, length - 0.08, panels + 1):
        add(u - 0.028, u + 0.028, 0.025, 0.107, bottom, roof - 0.14, FRAME)


def curtain(parts, shape, low, high, division=1.62, floors=3, skip=None):
    for a, b in shared.face_edges(shape):
        mid = Point((np.asarray(a) + b) / 2)
        if skip is not None and skip.covers(mid):
            continue
        length, add = tools.face(parts, a, b)
        if length > 1.10:
            prior.curtain(
                add, length, low, high, max(1, round(length / division)), floors
            )


def cylinder(parts, start, end, radius, color, sections=8):
    vertices = [[e, z, -n] for e, n, z in (start, end)]
    mesh = trimesh.creation.cylinder(radius=radius, segment=vertices, sections=sections)
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = [*color, 255]
    parts.append(mesh)


def glazed_bridge(parts, centerline, width, soffit, floor, roof):
    outline = orient(LineString(centerline).buffer(width * 0.5, cap_style=2))
    flat(parts, outline, soffit, floor, EDGE, CONCRETE)
    flat(parts, outline, roof - 0.195, roof, METAL, ROOF)
    a, b = np.asarray(centerline)
    tangent = (b - a) / np.linalg.norm(b - a)
    side = np.array((tangent[1], -tangent[0]))
    for sign in (-1, 1):
        p, q = a + side * sign * width * 0.5, b + side * sign * width * 0.5
        if sign == -1:
            p, q = q, p
        length, add = tools.face(parts, p, q)
        prior.curtain(
            add, length, floor + 0.035, roof - 0.196, max(4, round(length / 1.63)), 2
        )
    return outline


def franklin_bridge(parts, field, span):
    start, end = np.asarray(span["centerline"])
    axis = (end - start) / np.linalg.norm(end - start)
    lateral = np.array((axis[1], -axis[0]))
    width = span["width_m"]
    floor, roof, soffit = (
        span[key] for key in ("floor_z_m", "canopy_z_m", "soffit_z_m")
    )
    glazed_bridge(parts, (start, end + axis * 5.45), width, soffit, floor, roof)
    a, b = start + axis * span["arch_start_m"], start + axis * span["arch_end_m"]
    bearing_ends = [a, b]
    levels = [geometry.sample_ground(field, *p) + 0.65 for p in bearing_ends]
    feet = []
    for point, top in zip(bearing_ends, levels):
        pad = Point(point).buffer(1.13, quad_segs=2)
        flat(parts, pad, top - 1.05, top, CONCRETE, METAL)
        feet.append(pad)
    for side in (-1, 1):
        arc = []
        for t in np.linspace(0, 1, 41):
            crown = np.sin(np.pi * t) ** 0.72
            xy = (
                a
                + (b - a) * t
                + lateral * side * (0.12 + span["arch_max_offset_m"] * crown)
            )
            z_base = levels[0] + (levels[1] - levels[0]) * t
            height = z_base + (span["arch_top_z_m"] - z_base) * crown
            arc.append((*xy, height))
        for index, (p, q) in enumerate(zip(arc, arc[1:])):
            cylinder(parts, p, q, 0.26, METAL, sections=10)
            if index % 3 == 2 and p[2] >= floor + 0.4:
                center = a + (b - a) * (index / 40 + (0.035 if index < 20 else -0.035))
                anchor = center + lateral * side * width * 0.49
                cylinder(parts, p, (*anchor, floor + 0.08), 0.019, FRAME, sections=5)
    return feet


def millrace_bridge(parts, field, span):
    glazed_bridge(
        parts,
        span["centerline"],
        span["width_m"],
        span["soffit_z_m"],
        span["floor_z_m"],
        span["canopy_z_m"],
    )
    e, n = span["pedestal"]
    z = geometry.sample_ground(field, e, n)
    lower, upper = z + 1.45, span["soffit_z_m"]
    pad = box(e - 0.44, n - 0.36, e + 0.44, n + 0.36)
    flat(parts, pad, z - 0.36, lower, CONCRETE)
    for dx in (-1.14, 1.14):
        tools.beam(parts, (e, n, lower - 0.15), (e + dx, n, upper), 0.32, CONCRETE)
    return [pad]


def first_building(parts, field, model, walls, gates, bridge, base, datum):
    upper = {name: orient(Polygon(r)) for name, r in model["upper_regions"].items()}
    levels = model["levels_m"]
    first = levels["western_screen_bottom"]
    for name in ("west", "east"):
        floor = walls[name]
        outline = upper[name]
        roof = levels[name]
        tower_shell(parts, floor, base, first, DARK)
        curtain(parts, floor, datum + 0.37, first - 0.14, floors=2)
        tower_shell(parts, outline, first, roof)
        for a, b in shared.face_edges(outline):
            edge = LineString((a, b))
            if edge.length < 1.25:
                continue
            length, add = tools.face(parts, a, b)
            # The north edge faces the millrace with a simpler curtain wall.
            normal_north = -(b[0] - a[0]) / length
            if normal_north > 0.70:
                prior.curtain(
                    add,
                    length,
                    first + 0.11,
                    roof - 0.14,
                    max(2, round(length / 1.52)),
                    7,
                )
            else:
                folded_glass(parts, a, b, first + 0.41, roof)
            add(0.034, length - 0.034, -0.028, 0.138, first - 0.18, first + 0.34, PALE)
    for name in ("pavilion", "gallery_ground"):
        tower_shell(parts, walls[name], base, levels[name], DARK)
        curtain(parts, walls[name], datum + 0.32, levels[name] - 0.18, floors=2)
    gallery = upper["gallery"]
    tower_shell(parts, gallery, levels["gallery_ground"] + 0.045, levels["gallery"])
    curtain(
        parts,
        gallery,
        levels["gallery_ground"] + 0.20,
        levels["gallery"] - 0.20,
        floors=6,
    )
    x, y, X, Y, z = model["canopy_m"]
    flat(parts, box(x, y, X, Y), z, z + 0.13, EDGE, CANOPY)
    for e in np.linspace(x + 0.21, X - 0.21, 14):
        tools.beam(parts, (e, y, z - 0.105), (e, Y, z - 0.105), 0.10, METAL)
    for a, b, c, d, z in model["equipment_decks"]:
        footprint = box(a, b, c, d)
        flat(
            parts,
            footprint,
            (levels["west"] if c < 0 else levels["east"]) - 0.02,
            z,
            PALE,
            ROOF,
        )
    for shape in walls.values():
        prior.painted_doors(parts, shared.face_edges(shape), gates, METAL, COOL_GLASS)
    return franklin_bridge(parts, field, bridge)


def metal_shades(parts, outline, levels):
    for a, b in shared.face_edges(outline):
        length, add = tools.face(parts, a, b)
        if length < 1.05:
            continue
        bays = max(1, round(length / 1.86))
        width = length / bays
        for floor, top in zip(levels, levels[1:]):
            add(
                0.025, length - 0.025, -0.025, 0.215, floor - 0.095, floor + 0.11, METAL
            )
            for n in range(bays):
                u = width * n
                compression = (0.53, 0.69, 0.91, 0.63)[n % 4]
                add(
                    u + 0.11,
                    u + width - 0.092,
                    0.012,
                    0.051,
                    floor + 0.18,
                    top - 0.12,
                    COOL_GLASS if n % 5 == 1 else GLASS,
                )
                corners = [
                    (u + width * 0.19, 0.14, floor + 0.13),
                    (u + width * 0.53, compression, floor + 0.13),
                    (u + width * 0.31, 0.79, top - 0.10),
                    (u + 0.08, 0.095, top - 0.10),
                ]
                facet(parts, a, b, corners, (SHADE[n % 3], SHADE[(n + 1) % 3]))


def second_building(parts, field, model, walls, gates, bridge, base, datum):
    levels = model["levels_m"]
    lower, roof = levels["transfer"], levels["roof"]
    footprint = walls["base"]
    zones = {name: orient(Polygon(r)) for name, r in model["upper_regions"].items()}
    tower_shell(parts, footprint, base, lower, DARK)
    curtain(
        parts, footprint, levels["l1"] + 0.08, lower - 0.16, division=1.81, floors=2
    )
    upper = orient(union([zones["east"], zones["west"]]))
    tower_shell(parts, upper, lower, roof)
    metal_shades(parts, upper, [lower, 9.43, 14.31, roof - 0.08])
    for region in model["terraces"]:
        deck = orient(Polygon(region))
        z = levels["terrace_deck"]
        flat(parts, deck, z - 0.29, z, EDGE, CONCRETE)
        for a, b in shared.face_edges(deck):
            if upper.boundary.distance(Point((np.asarray(a) + b) / 2)) < 0.06:
                continue
            length, add = tools.face(parts, a, b)
            if length > 1.1:
                prior.nearby.rails(add, 0.06, length - 0.06, -0.075, z)
        canopy = deck.intersection(box(24, 269.4, 49.3, 298))
        if canopy.area > 0.3:
            flat(
                parts,
                canopy,
                levels["terrace_roof"] - 0.14,
                levels["terrace_roof"],
                METAL,
                ROOF,
            )
            e, n = canopy.representative_point().coords[0]
            tools.beam(
                parts, (e, n, z), (e, n, levels["terrace_roof"]), 0.22, FRAME_LIGHT
            )
    penthouse = zones["penthouse"]
    flat(parts, penthouse, roof - 0.01, levels["penthouse"], METAL, ROOF)
    for a, b in shared.face_edges(penthouse):
        length, add = tools.face(parts, a, b)
        for u in np.arange(0.23, length - 0.15, 0.34):
            add(
                u - 0.025,
                u + 0.025,
                0.011,
                0.047,
                roof + 0.10,
                levels["penthouse"] - 0.10,
                EDGE,
            )
    prior.painted_doors(parts, shared.face_edges(footprint), gates, METAL, COOL_GLASS)
    return millrace_bridge(parts, field, bridge)


def build(spec, manifest, config, field, graph):
    meshes, records, grounds, solids, supports, gates, paving = (
        {},
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for campus, model in spec["buildings"].items():
        walls = {
            name: orient(Polygon(coords))
            for name, coords in model["ground_regions"].items()
        }
        outline = orient(Polygon(model["footprint_enu_m"]))
        base, datum = science.earlier.fit_base(field, outline)
        model_gates, feet, parts = [], [], []
        for entry in model["entrances"]:
            point = Point(entry["position_enu_m"])
            assert (
                min(wall.boundary.distance(point) for wall in walls.values()) < 0.006
            ), entry
            gate, path, obstructions = shared.site_entry(grounds, field, entry)
            model_gates.append(gate)
            paving.append(path)
            feet.extend(obstructions)
        bridge = spec["bridges"]["franklin" if campus == "402" else "millrace"]
        make = first_building if campus == "402" else second_building
        feet.extend(make(parts, field, model, walls, model_gates, bridge, base, datum))
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        id = model["id"]
        meshes[id] = science.ordered_mesh(mesh)
        records.append(
            dict(
                id=id,
                name=model["name"],
                campus_id=model["campus_id"],
                footprint_enu_m=ring(outline),
                ground_footprints_enu_m=[ring(p) for p in walls.values()],
                support_collision_enu_m=[ring(p) for p in feet],
                entrances=model_gates,
                base_z_m=round(base, 4),
                roof_z_m=round(float(mesh.bounds[1, 1]), 4),
                area_m2=round(outline.area, 3),
            )
        )
        solids.extend(walls.values())
        supports.extend(feet)
        gates.extend(model_gates)
    known = set(meshes) | set(spec["absorbed_into"])
    prior_solid = union(
        [
            Polygon(item["footprint_enu_m"]).buffer(0)
            for item in manifest["buildings"]
            if item["id"] in known
        ]
    )
    routes, clearance = prior.nearby.shared.graduate.shared.check_routes(
        solids,
        supports,
        gates,
        prior_solid,
        manifest,
        graph,
        config,
        known,
    )
    blocked = union([*solids, *supports])
    millrace = Polygon(spec["millrace_water_enu_m"])
    prior.nearby.add_paths(grounds, field, millrace, blocked, WATER)
    avoid_water = union([blocked, millrace])
    for path in spec["walks"]:
        line = LineString(path["line"]).buffer(
            path["width_m"] * 0.5, join_style=2, cap_style=2
        )
        prior.nearby.add_paths(grounds, field, line, avoid_water, PAVING)
    prior.nearby.add_paths(grounds, field, union(paving), avoid_water, PAVING)
    return (
        meshes,
        records,
        science.ordered_mesh(trimesh.util.concatenate(grounds)),
        routes,
        clearance,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument(
        "--stage", type=Path, help="Write a review package without updating the viewer"
    )
    parser.add_argument("--spec", type=Path, default=SPEC)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_bytes())
    manifest_path = SCENE / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    assert tools.digest(manifest_path) == spec["sources"]["scene_manifest_sha256"]
    assert tools.digest(field_path) == spec["sources"]["scene_heightfield_sha256"]
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, routes, clearance = build(
        spec, manifest, config, field, graph
    )
    appearances = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = shared.frohnmayer.source_removals(spec, config, appearances)
    output = args.stage if args.stage is not None else SCENE / DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    model = output / "site.glb"
    site.memorial.gerlinger.export(
        model, meshes, ground, GROUND, "knight-campus-paving",
        vegetation=site_planting(spec, field, geometry.sample_ground),
    )
    descriptor = output / "site.json"
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        ground_node=GROUND,
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(model),
        buildings=records,
        absorbed_ids=list(spec["absorbed_into"]),
        batch_removals=removals,
        context_trees=spec.get("context_tree_removals", []),
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    if args.stage is None:
        config["knight_campus_site"] = dict(
            url=f"{DIRECTORY}/site.json", sha256=tools.digest(descriptor)
        )
        config_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf8",
            newline="\n",
        )
    audit = dict(
        buildings=records,
        triangles={id: len(mesh.faces) for id, mesh in meshes.items()},
        route_edges=routes,
        nearest_ground_collision_m=round(clearance, 3),
        batch_removals=removals,
        glb_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(
        json.dumps(
            {
                key: audit[key]
                for key in (
                    "triangles",
                    "route_edges",
                    "nearest_ground_collision_m",
                    "glb_sha256",
                )
            }
        )
    )


if __name__ == "__main__":
    main()
