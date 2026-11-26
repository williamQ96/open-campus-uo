# SPDX-License-Identifier: Apache-2.0
"""Export the museum shell, courtyard and entrance from registered exterior evidence."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

helpers_path = Path(__file__).with_name("build-athletic-exterior-review.py")
helpers_spec = spec_from_file_location(helpers_path.stem, helpers_path)
tools = module_from_spec(helpers_spec)
helpers_spec.loader.exec_module(tools)
geometry = tools.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/museum-exterior-review.json"
DIRECTORY = "museum-exterior-review"
GROUND = "museum-approaches"

BRICK = (147, 87, 66)
REAR_BRICK = (122, 75, 64)
PATTERN = (125, 76, 56)
TRIM = (176, 122, 92)
STONE = (186, 160, 133)
ROOF = (185, 181, 171)
GALLERY_ROOF = (139, 135, 129)
GLASS = (56, 70, 67)
SHADOW = (62, 47, 44)
PLANTING = (90, 112, 65)


def rectangle(parts, bounds, base, top, color, roof=None):
    tools.flat(parts, box(*bounds), base, top, color, roof)


def roofs(parts, plan, zones, base):
    remaining = plan
    resolved = []
    for zone in zones:
        bounds = zone["bounds"]
        region = remaining.intersection(box(*bounds))
        assert region.area > 2, zone["name"]
        low = zone["bottom_roof_z_m"]
        high = zone.get("top_roof_z_m", low)
        material = REAR_BRICK if "east" in zone["name"] else BRICK
        slopes = {
            "east": lambda e, n: (bounds[2] - e) / (bounds[2] - bounds[0]),
            "north": lambda e, n: (bounds[3] - n) / (bounds[3] - bounds[1]),
            "south": lambda e, n: (n - bounds[1]) / (bounds[3] - bounds[1]),
        }
        slope = slopes.get(zone.get("fall"), lambda e, n: 0)

        def height(e, n):
            return low + (high - low) * slope(e, n)

        roofing = GALLERY_ROOF if "courtyard" in zone["name"] else ROOF
        for piece in geometry.sections(region):
            parts.append(geometry.shell(piece, base, height, material, roofing))
        resolved.append((zone["name"], region))
        remaining = remaining.difference(region)
    tools.flat(parts, remaining, base, 16.66, BRICK, ROOF)
    assert abs(sum(region.area for _, region in resolved) + remaining.area - plan.area) < 0.001
    return {name: round(region.area, 2) for name, region in resolved} | {
        "connecting gallery roofs": round(remaining.area, 2)
    }


def arch_panel(parts, outline, fixed, axis, normal, color):
    vertices = []
    for tri in shapely.constrained_delaunay_triangles(outline).geoms:
        for offset, z in list(orient(tri).exterior.coords)[:3]:
            e, n = (fixed, offset) if axis == 0 else (offset, fixed)
            vertices.append((e, z, -n))
    mesh = trimesh.Trimesh(vertices, np.arange(len(vertices)).reshape(-1, 3), process=False)
    if mesh.face_normals[0, axis] * normal < 0:
        mesh.invert()
    mesh.visual.vertex_colors = [*color, 255]
    parts.append(mesh)


def arch(center, width, base, spring, rise, pointed=False):
    if pointed:
        right = [
            (center + width / 2 * (1 - t * t), spring + rise * (t + t * t) / 2)
            for t in np.linspace(0, 1, 11)
        ]
        arc = right + [(2 * center - e, z) for e, z in reversed(right[:-1])]
    else:
        arc = [
            (center + width / 2 * np.cos(a), spring + rise * np.sin(a))
            for a in np.linspace(0, np.pi, 21)
        ]
    return Polygon([(center - width / 2, base), (center + width / 2, base), *arc])


def west_front(parts, entry, west, south, north, field):
    _, n = entry["position_enu_m"]
    grade = float(geometry.sample_ground(field, west - 1.8, n))
    landing = grade + 0.39
    width, front = tools.face(parts, (west, north), (west, south))
    center = north - n
    for z, h, material in ((6.32, 0.25, TRIM), (10.72, 0.2, PATTERN),
                           (12.88, 0.35, TRIM), (19.94, 0.37, TRIM)):
        front(0, width, -0.025, 0.16, z, z + h, material)
    for u in np.arange(1, width - 0.6, 0.48):
        front(u, u + 0.16, 0.025, 0.23, 19.42, 19.91, TRIM)
    for offset in np.arange(1.9, width - 1, 1.45):
        for row in range(3):
            at = offset + (row % 2) * 0.73
            if abs(at - center) < 3.3 and row == 0:
                continue
            nn, z = north - at, 14.45 + row * 1.7
            for side in (-1, 1):
                for level in (-1, 1):
                    tools.beam(parts, (west - 0.036, nn + side * 0.66, z),
                               (west - 0.036, nn, z + level * 0.78), 0.064, PATTERN)
    outside = arch(n, 4.88, landing, landing + 4.2, 2.55, pointed=True)
    inside = arch(n, 2.72, landing + 0.03, landing + 3.55, 1.68, pointed=True)
    peak = landing + 7.55
    portal = Polygon([(n - 2.94, landing), (n + 2.94, landing),
                      (n + 2.94, landing + 4.9), (n, peak),
                      (n - 2.94, landing + 4.9)])
    for profile, at, color in ((portal, -0.45, PATTERN), (outside, -0.49, TRIM),
                                (outside.buffer(-0.24), -0.51, STONE),
                                (inside, -0.53, SHADOW)):
        arch_panel(parts, profile, west + at, 0, -1, color)
    for side in (-1, 1):
        u = center + side * 2.55
        front(u - 0.29, u + 0.29, -0.025, 0.57, landing, landing + 4.87, BRICK)
        front(u - 0.39, u + 0.39, -0.025, 0.65, landing, landing + 0.29, TRIM)
        front(u - 0.39, u + 0.39, 0.04, 0.65, landing + 4.55, landing + 4.78, TRIM)
    for end in (-2.95, 2.95):
        tools.beam(parts, (west - 0.52, n, peak),
                   (west - 0.52, n + end, landing + 4.9), 0.14, TRIM)
    front(center - 1.01, center + 1.01, 0.54, 0.59, landing + 0.04, landing + 3.22, GLASS)
    for u in (center - 1.04, center, center + 1.04):
        front(u - 0.024, u + 0.024, 0.59, 0.65, landing + 0.04, landing + 3.31, TRIM)
    front(center - 1.04, center + 1.04, 0.59, 0.65, landing + 1.18, landing + 1.25, TRIM)
    for step in range(3):
        front(center - 2.94 + 0.09 * step, center + 2.94 - 0.09 * step,
              -0.03, 1.48 - 0.31 * step, grade - 0.42,
              grade + 0.13 * (step + 1), STONE)
    for at in (-150.9, -120.0):
        strip = arch(at, 0.76, grade + 0.6, grade + 3.1, 0.52, pointed=True)
        arch_panel(parts, strip.buffer(0.13), west - 0.089, 0, -1, TRIM)
        arch_panel(parts, strip, west - 0.092, 0, -1, GLASS)
    for start, end in (((west, south), (west + 11.3, south)),
                       ((west + 11.3, north), (west, north))):
        side_width, face = tools.face(parts, start, end)
        for z, h in ((6.32, 0.25), (12.88, 0.35), (19.88, 0.22)):
            face(0, side_width, -0.024, 0.115, z, z + h, TRIM)


def east_front(parts, east, south, north, field):
    width, rear = tools.face(parts, (east, south), (east, north))
    grade = float(geometry.sample_ground(field, east + 1.2, -134))
    for z in (grade + 0.34, grade + 4.15):
        rear(0, width, -0.018, 0.1, z, z + 0.14, PATTERN)
    for offset in (18.5, 21.2, 23.9, 26.6, 29.3, 32):
        rear(offset, offset + 1.24, 0, 0.035, grade + 0.78, grade + 2.76, SHADOW)
        rear(offset + 0.09, offset + 1.17, 0.039, 0.061, grade + 0.86, grade + 2.68, GLASS)
        rear(offset - 0.05, offset + 1.3, -0.01, 0.17, grade + 0.70, grade + 0.83, STONE)
    rear(34.65, 36.27, 0.003, 0.045, grade + 0.18, grade + 3.25, SHADOW)
    rear(36.47, 40.0, 0.003, 0.065, grade + 0.25, grade + 3.5, SHADOW)
    rear(34.41, 36.6, -0.04, 0.86, grade + 3.18, grade + 3.32, (106, 102, 94))
    rear(34.53, 40.2, -0.03, 1.01, grade - 0.46, grade + 0.24, STONE)
    for offset in (36.56, 38.25, 39.98):
        tools.beam(parts, (east + 0.96, south + offset, grade + 0.18),
                   (east + 0.96, south + offset, grade + 0.98), 0.042, (107, 111, 103))
    tools.beam(parts, (east + 0.96, south + 36.54, grade + 0.98),
               (east + 0.96, south + 40, grade + 0.98), 0.052, (107, 111, 103))


def courtyards(parts, plan, bounds, side_courts, forecourt, field):
    e0, n0, e1, n1 = bounds
    nc = (n0 + n1) / 2
    grade = float(geometry.sample_ground(field, (e0 + e1) / 2, nc))
    basin = box(e0 + 3.3, nc - 1.19, e1 - 3.4, nc + 1.19)
    tools.flat(parts, basin.buffer(0.24, join_style="mitre").difference(basin),
               grade - 0.1, grade + 0.42, STONE)
    tools.flat(parts, basin, grade - 0.22, grade + 0.30, (73, 113, 99))
    for n, sign in ((n0, 1), (n1, -1)):
        side = sorted((n, n + sign * 0.52))
        rectangle(parts, (e0, side[0], e1, side[1]), grade - 0.15, grade + 0.84, BRICK, TRIM)
        for e in np.linspace(e0 + 1.2, e1 - 1.2, 9):
            profile = arch(e, 1.37, grade + 0.86, grade + 3.18, 0.56)
            front = n + sign * 0.063
            arch_panel(parts, profile.buffer(0.12), front, 2, -sign, TRIM)
            arch_panel(parts, profile, front + sign * 0.013, 2, -sign, SHADOW)
            tools.beam(parts, (e + 0.95, n + sign * 0.28, grade + 0.84),
                       (e + 0.95, n + sign * 0.28, grade + 3.29), 0.22, STONE)
        inner = sorted((n + sign * 0.66, n + sign * 1.39))
        rectangle(parts, (e0 + 1.52, inner[0], e1 - 1.52, inner[1]),
                  grade - 0.08, grade + 0.2, PLANTING)
    for n in (nc - 1.37, nc, nc + 1.37):
        profile = arch(n, 0.82, grade + 5.4, grade + 8.28, 0.44)
        arch_panel(parts, profile.buffer(0.095), e0 + 0.034, 0, 1, TRIM)
        arch_panel(parts, profile, e0 + 0.048, 0, 1, GLASS)
        tools.beam(parts, (e0 + 0.056, n - 0.4, grade + 6.53),
                   (e0 + 0.056, n + 0.4, grade + 6.53), 0.051, STONE)
    profile = arch(nc, 1.68, grade + 0.23, grade + 2.43, 0.78)
    arch_panel(parts, profile.buffer(0.14), e0 + 0.034, 0, 1, TRIM)
    arch_panel(parts, profile, e0 + 0.048, 0, 1, SHADOW)
    for n in (nc - 1.53, nc + 1.53):
        arch_panel(parts, box(n - 0.31, grade + 0.23, n + 0.31, grade + 2.55),
                   e0 + 0.048, 0, 1, GLASS)
    walls, paving = [], []
    for i, (left, lo, right, hi) in enumerate(side_courts):
        n = lo if i == 0 else hi
        setback = n + (0.45 if i == 0 else -0.45)
        wall = box(left + 0.01, min(n, setback), right - 0.01, max(n, setback))
        walls.append(wall)
        base = min(geometry.sample_ground(field, e, n) for e in np.linspace(left, right, 5))
        tools.flat(parts, wall, base - 0.36, base + 1.32, BRICK, TRIM)
        paving.append((box(left + 0.05, lo + 0.015, right - 0.05, hi - 0.015), (150, 140, 115)))
        for e in (-502, -491.4):
            beds = box(e - 1.04, lo + 1.05, e + 1.04, hi - 1.05)
            paving.append((beds, PLANTING))
    pavement = box(e0 + 0.02, n0 + 0.02, e1 - 0.02, n1 - 0.02)
    paving.append((pavement, (159, 145, 119)))
    paving.append((Polygon(forecourt), (163, 154, 135)))
    # Disjoint paving avoids coplanar planting and avoids covering solid walls.
    blocked = plan.union(shapely.union_all(walls))
    ground = []
    for region, rgb in reversed(paving):
        areas = geometry.sections(region.difference(blocked))
        if areas:
            ground.append(tools.approaches(
                [{"outline": list(region.exterior.coords), "rgb": rgb}], field, blocked
            ))
        blocked = blocked.union(region)
    return trimesh.util.concatenate(ground), walls


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
    target = spec["id"]
    prior = {
        b["id"]: Polygon(b["footprint_enu_m"]).buffer(0) for b in manifest["buildings"]
    }
    court = box(*spec["campbell_courtyard_bounds_enu_m"])
    plan = Polygon(spec["outer_enu_m"], [list(court.exterior.coords)])
    assert plan.is_valid and target in config["replaces_building_ids"]
    grade = [
        geometry.sample_ground(field, *ring.interpolate(distance).coords[0])
        for ring in (plan.exterior, *plan.interiors)
        for distance in np.arange(0, ring.length, 0.35)
    ]
    base = round(min(grade) - 0.39, 3)
    west, south, east, north = plan.bounds
    entry = spec["entrance"]
    assert plan.boundary.distance(Point(entry["position_enu_m"])) < 0.001
    parts = []
    roof_areas = roofs(parts, plan, spec["roof_zones"], base)
    west_front(parts, entry, west, south, north, field)
    east_front(parts, east, south, north, field)
    ground, walls = courtyards(
        parts, plan, court.bounds, spec["side_courts_bounds_enu_m"],
        spec["west_forecourt_enu_m"], field,
    )
    occupied = plan.union(shapely.union_all(walls))
    assert not any(occupied.intersection(p).area > 0.02 for id, p in prior.items() if id != target)

    graph = json.loads((SCENE / "navigation.json").read_bytes())
    edges = [LineString([graph["nodes_enu_m"][a], graph["nodes_enu_m"][b]])
             for a, b, *_ in graph["edges"]]
    conflicts = [i for i, line in enumerate(edges)
                 if line.distance(occupied) < 0.42 <= line.distance(prior[target])]
    assert not conflicts, conflicts

    building = trimesh.util.concatenate(parts)
    stage = trimesh.Scene()
    for name, mesh in ((target, building), (GROUND, ground)):
        colors = mesh.visual.vertex_colors.copy()
        srgb = colors[:, :3].astype(float) / 255
        linear = np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)
        colors[:, :3] = np.round(linear * 255).astype(np.uint8)
        mesh.visual.vertex_colors = colors
        stage.add_geometry(mesh, node_name=name, geom_name=name)

    def metadata(tree):
        tree["asset"]["copyright"] = "Open Campus contributors. Original geometry CC BY 4.0."
        tree["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.02, "roughnessFactor": 0.86}}
        ]
        for node in tree["nodes"]:
            if node.get("name") == target:
                node["extras"] = {"asset_kind": "building", "asset_id": target}
            elif node.get("name") == GROUND:
                node["extras"] = {"asset_kind": "landscape-surface", "surface_layer": "museum-paving"}
        for mesh in tree["meshes"]:
            mesh["primitives"][0]["material"] = 0

    output = SCENE / DIRECTORY
    output.mkdir(exist_ok=True)
    glb = output / "site.glb"
    glb.write_bytes(trimesh.exchange.gltf.export_glb(
        stage, include_normals=True, tree_postprocessor=metadata
    ))
    exported = trimesh.load(glb, force="scene", process=False)
    assert set(exported.graph.nodes_geometry) == {target, GROUND}
    assert np.allclose(stage.bounds, exported.bounds, atol=0.00005)
    descriptor = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": tools.digest(field_path),
        "url": f"{DIRECTORY}/site.glb",
        "sha256": tools.digest(glb),
        "ground_node": GROUND,
        "building": {
            "id": target,
            "footprint_enu_m": spec["outer_enu_m"],
            "footprint_holes_enu_m": [list(court.exterior.coords)[:-1]],
            "support_collision_enu_m": [list(wall.exterior.coords)[:-1] for wall in walls],
            "area_m2": round(plan.area, 2),
            "base_z_m": base,
            "roof_z_m": round(float(building.bounds[1, 1]), 4),
            "entrances": [entry],
        },
    }
    site = output / "site.json"
    site.write_text(json.dumps(descriptor, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    config["museum_site_review"] = {"url": f"{DIRECTORY}/site.json", "sha256": tools.digest(site)}
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8", newline="\n")
    audit = {
        "footprint_m2": round(plan.area, 2),
        "campbell_courtyard_m2": round(court.area, 2),
        "roof_zone_m2": roof_areas,
        "footing_samples": len(grade),
        "minimum_footing_cover_m": round(min(grade) - base, 3),
        "route_edges": len(edges),
        "new_route_conflicts": conflicts,
        "building_triangles": len(building.faces),
        "ground_triangles": len(ground.faces),
        "asset_sha256": tools.digest(glb),
        "site_sha256": tools.digest(site),
    }
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
