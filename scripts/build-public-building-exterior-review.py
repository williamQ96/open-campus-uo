# SPDX-License-Identifier: Apache-2.0
"""Export the Clinical Services, natural history museum, Barn and Agate Hall exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-northsite-millrace-site-review.py")
loader = spec_from_file_location(source.stem, source)
reference = module_from_spec(loader)
loader.loader.exec_module(reference)
science, site, tools, shared, prior = (
    reference.science, reference.site, reference.tools, reference.shared, reference.prior
)
flat, union, ring, geometry = reference.flat, reference.union, reference.ring, reference.geometry
SCENE = reference.SCENE
SPEC = geometry.ROOT / "data/metadata/public-building-exterior-review.json"
DIRECTORY = "public-building-exterior-review"
GROUND = "public-building-exterior-approaches"

CLAY = (150, 91, 78)
OCHRE = (165, 133, 103)
CREAM = (214, 207, 179)
CONCRETE = (166, 161, 150)
GRAY = (141, 143, 132)
GLASS = (73, 101, 105)
DARK_GLASS = (65, 91, 96)
GREEN = (79, 124, 116)
TEAL = (54, 103, 95)
WOOD = (113, 78, 58)
TIMBER = (146, 102, 75)
METAL = (164, 165, 152)
DARK = (71, 74, 74)
STRIPE = (191, 187, 164)
WALK = (177, 170, 150)
PANEL = (45, 65, 88)
ROOFS = {
    "oxblood": (150, 103, 89),
    "membrane": (207, 204, 189),
    "sand": (179, 156, 132),
    "shingle": (119, 104, 93),
    "green": (122, 139, 124),
    "zinc": METAL,
    "charcoal": (109, 111, 108),
}
WALLS = {"029": CONCRETE, "049": WOOD, "052": OCHRE, "147": CREAM}


def as_plane(values):
    east, north, elevation = values
    return lambda e, n: east * e + north * n + elevation


def hip_planes(hip):
    z, rise = hip["ridge_z"], hip["ridge_z"] - hip["eave_z"]
    e = hip["ridge_e"]
    south, north = hip["ridge_south_n"], hip["ridge_north_n"]
    slopes = (
        (rise / (e - hip["west_e"]), 0, e, south),
        (-rise / (hip["east_e"] - e), 0, e, south),
        (0, rise / (south - hip["south_n"]), e, south),
        (0, -rise / (hip["north_n"] - north), e, north),
    )
    return np.array([[x, y, z - x * e0 - y * n0] for x, y, e0, n0 in slopes])


def roof_shell(parts, outline, row, floor, wall):
    remaining = outline
    surfaces = []
    for zone in row["roof"]:
        plan = set_precision(remaining.intersection(Polygon(zone["plan"])), 0.001)
        if plan.area <= 0.0001:
            continue
        remaining = set_precision(remaining.difference(plan), 0.001)
        roof = ROOFS[zone["finish"]]
        eaves = set_precision(plan.buffer(0.24, join_style="mitre").difference(outline.difference(plan)), 0.001)
        if zone["name"] == "west deep hipped roof":
            planes = hip_planes(row["hip"])
            top = science.earlier.pitched(parts, plan, eaves, planes, floor, wall, roof)
        else:
            top = as_plane(zone["plane"])
            site.surface(parts, plan, floor, lambda e, n: top(e, n) - 0.15, wall, roof)
            science.earlier.roof_layer(parts, eaves, top, 0.17, 0.013, GRAY, roof)
        surfaces.append((plan, top))
    if remaining.area > 0.025:
        raise ValueError(f"Uncovered roof in {row['name']}: {remaining.area:.3f} m²")
    return surfaces


def roof_at(surfaces, e, n):
    point = Point(e, n)
    for plan, top in surfaces:
        if plan.distance(point) < 0.025:
            return float(top(e, n))
    plan, top = min(surfaces, key=lambda piece: piece[0].distance(point))
    return float(top(e, n))


def entry_width(edge, gates, zone):
    for gate in gates:
        point = Point(gate["position_enu_m"])
        if edge.distance(point) < 0.022 and (
            abs(edge.project(point) - zone[0]) < zone[1] + gate["width_m"] * 0.63
        ):
            return gate
    return None


def eave_height(surfaces, edge, left, right):
    return min(roof_at(surfaces, *edge.interpolate(u).coords[0]) for u in (left, (left + right) / 2, right))


def clinical_facade(parts, outline, surfaces, gates, field):
    for a, b in shared.face_edges(outline):
        length, add = tools.face(parts, a, b)
        edge = LineString((a, b))
        if length < 1.35:
            continue
        width = length / max(1, round(length / 2.17))
        for u in np.arange(width * 0.5, length, width):
            left, right = u - width * 0.42, u + width * 0.42
            eave = eave_height(surfaces, edge, left, right)
            e, n = edge.interpolate(u).coords[0]
            exposed = geometry.sample_ground(field, e, n)
            band = eave - 2.05
            if band > exposed + 0.9:
                add(left, right, 0.006, 0.079, band - 0.39, band - 0.15, OCHRE)
                if e < -681.4 or n < -568.5 or e > -660.1:
                    prior.window(add, u, width * 0.75, band, eave - 0.48, CONCRETE, DARK_GLASS, 2)
            if eave > exposed + 4.9 and (e < -682.7 or n < -575.2) and not entry_width(edge, gates, (u, width * 0.44)):
                prior.window(add, u, width * 0.61, exposed + 0.94, exposed + 2.54, GRAY, GLASS, 2)
            if e > -674 or n < -566:
                rib = min(0.17, width * 0.095)
                add(u - rib, u + rib, -0.06, 0.41, eave - 0.50, eave - 0.16, CONCRETE)


def museum_facade(parts, row, outline, surfaces, gates, datum, field):
    for a, b in shared.face_edges(outline):
        length, add = tools.face(parts, a, b)
        if length < 1.2:
            continue
        edge = LineString((a, b))
        width = length / max(1, round(length / 2.76))
        west = (b[1] - a[1]) / length < -0.50
        add(0.02, length - 0.02, -0.04, 0.07, datum + 0.22, datum + 0.60, CONCRETE)
        for u in np.arange(width * 0.5, length, width):
            left, right = u - width * 0.446, u + width * 0.446
            top = eave_height(surfaces, edge, left, right) - 0.23
            if top > datum + 1.02:
                add(left, left + 0.085, 0.003, 0.080, datum + 0.48, top, TIMBER)
            if west and not entry_width(edge, gates, (u, width * 0.48)):
                prior.window(add, u, width * 0.72, datum + 0.93, min(top - 0.1, datum + 3.14), WOOD, DARK_GLASS, 2)
        if west:
            top = eave_height(surfaces, edge, 0.02, length - 0.02) - 0.38
            if top > datum + 2.2:
                add(0.01, length - 0.01, 0.018, 0.285, top - 0.19, top, TIMBER)
                for u in np.arange(0.37, length - 0.18, 1.47):
                    add(u - 0.052, u + 0.052, -0.055, 0.32, top - 0.31, top - 0.10, WOOD)

    porch = row["porch"]
    roof_plan = Polygon(porch["plan"]).buffer(0.39, join_style="mitre")
    ridge, height = porch["ridge_n"], porch["ridge_z"]
    run = max(ridge - roof_plan.bounds[1], roof_plan.bounds[3] - ridge)
    pitch = (height - porch["eave_z"]) / run
    e0, n0, e1, n1 = roof_plan.bounds
    for a, b in ((n0, ridge), (ridge, n1)):
        top = lambda e, n: height - abs(n - ridge) * pitch
        science.earlier.roof_layer(parts, roof_plan.intersection(box(e0, a, e1, b)), top, 0.19, 0.014, TIMBER, ROOFS["shingle"])
    supports = []
    for e, n in porch["posts"]:
        post = box(e - 0.21, n - 0.21, e + 0.21, n + 0.21)
        base = geometry.sample_ground(field, e, n) - 0.25
        flat(parts, post, base, height - abs(n - ridge) * pitch - 0.12, TIMBER)
        supports.append(post)
    for e in (e0 + 0.4, e1 - 0.27):
        for n in (n0 + 0.4, n1 - 0.4):
            tools.beam(parts, (e, n, height - abs(n - ridge) * pitch - 0.15), (e, ridge, height - 0.12), 0.28, WOOD)
    for w, s, e, n, z in row["equipment"]:
        flat(parts, box(w, s, e, n), roof_at(surfaces, (w + e) * 0.5, (s + n) * 0.5) - 0.07, z, GRAY, METAL)
    return supports


def barn_facade(parts, row, outline, surfaces, gates, datum):
    for a, b in shared.face_edges(outline):
        length, add = tools.face(parts, a, b)
        edge = LineString((a, b))
        if length < 0.82:
            continue
        add(0.02, length - 0.02, 0.013, 0.054, datum + 0.16, datum + 0.54, CONCRETE)
        for u in np.arange(0.28, length - 0.12, 0.46):
            top = eave_height(surfaces, edge, max(0, u - 0.15), min(length, u + 0.15))
            add(u - 0.014, u + 0.014, 0.011, 0.048, datum + 0.54, top - 0.24, TIMBER)
        for gate in gates:
            point = Point(gate["position_enu_m"])
            u = edge.project(point)
            if edge.distance(point) > 0.020:
                continue
            width = gate["width_m"] * 0.5
            sill = gate["threshold_z_m"]
            if gate["gate"] == "barn-east-bay" and width + 0.13 < min(u, length - u):
                add(u - width - 0.13, u + width + 0.13, -0.02, 0.075, sill, sill + 3.03, GRAY)
                for z in np.arange(sill + 0.1, sill + 2.98, 0.244):
                    add(u - width, u + width, 0.077, 0.101, z, z + 0.025, DARK)
            if 0.73 < u < length - 2.6:
                prior.window(add, min(length - 0.86, u + width + 0.95), 1.06, sill + 1.0, sill + 2.32, TIMBER, DARK_GLASS, 2)
    for section in row["raised_roof"]:
        plan = Polygon(section["plan"])
        top = as_plane(section["plane"])
        site.surface(parts, plan, min(roof_at(surfaces, *plan.centroid.coords[0]) - 0.15, top(*plan.centroid.coords[0]) - 0.45), top, GRAY, METAL)
        surfaces.insert(0, (plan, top))
    solar = row["solar"]
    center, axis, normal = (np.array(solar[key]) for key in ("origin", "axis", "normal"))
    u0, v0, u1, v1 = solar["bounds_uv_m"]
    steps_u = np.linspace(u0, u1, solar["panels_per_row"] + 1)
    steps_v = np.linspace(v0, v1, solar["panel_rows"] + 1)
    for a, b in zip(steps_u, steps_u[1:]):
        for c, d in zip(steps_v, steps_v[1:]):
            panel = Polygon([center + axis * u + normal * v for u, v in ((a + 0.035, c + 0.025), (b - 0.035, c + 0.025), (b - 0.035, d - 0.025), (a + 0.035, d - 0.025))])
            panel = panel.intersection(outline.buffer(-0.08))
            if panel.area < 0.14:
                continue
            e, n = panel.centroid.coords[0]
            surface = next((top for plan, top in surfaces if plan.covers(Point(e, n))), None)
            if surface:
                science.earlier.roof_layer(parts, panel, lambda x, y: surface(x, y) + 0.075, 0.06, 0.016, DARK, PANEL)


def agate_facade(parts, row, outline, surfaces, gates, datum):
    for a, b in shared.face_edges(outline):
        length, add = tools.face(parts, a, b)
        edge = LineString((a, b))
        if length < 1.1:
            continue
        west = (b[1] - a[1]) / length < -0.65
        width = length / max(1, round(length / 2.55))
        base = datum + 0.22
        add(0.02, length - 0.02, -0.028, 0.071, base, base + 0.24, CONCRETE)
        for u in np.arange(width * 0.5, length, width):
            if entry_width(edge, gates, (u, width * 0.46)):
                continue
            top = eave_height(surfaces, edge, u - width * 0.36, u + width * 0.36)
            for sill in (base + 1.12, base + 4.23):
                if top < sill + 1.85:
                    continue
                prior.window(add, u, width * 0.67, sill, sill + 1.35, STRIPE, GLASS, 3)
                if west:
                    add(u - width * 0.40, u + width * 0.40, 0.042, 0.82, sill + 1.34, sill + 1.49, TEAL)
            if west and top > base + 6:
                add(u - width * 0.49, u + width * 0.49, -0.009, 0.085, top - 0.68, top - 0.50, STRIPE)

    gate = gates[0]
    portal = Point(gate["position_enu_m"])
    band = gate["threshold_z_m"]
    e, n = portal.coords[0]
    a, b = (e - 0.014, n + 3.45), (e - 0.014, n - 3.45)
    width, add = tools.face(parts, a, b)
    add(0.16, width - 0.16, -0.19, 0.073, band + 5.81, band + 9.52, CREAM)
    add(0.44, width - 0.44, 0.01, 0.24, band + 3.60, band + 3.76, STRIPE)
    for u in (0.33, width - 0.33):
        add(u - 0.21, u + 0.21, -0.03, 0.33, band, band + 9.45, CREAM)
        for z in (band + 0.48, band + 6.40, band + 9.19):
            add(u - 0.26, u + 0.26, 0.004, 0.38, z, z + 0.15, STRIPE)
    for u in (1.51, width * 0.50, width - 1.51):
        prior.window(add, u, 1.53, band + 4.04, band + 5.82, CREAM, DARK_GLASS, 2)
        angles = np.linspace(0, np.pi, 13)
        for first, second in zip(angles, angles[1:]):
            a2 = (e - 0.12, n + width * 0.5 - (u + 0.75 * np.cos(first)), band + 5.82 + 0.68 * np.sin(first))
            b2 = (e - 0.12, n + width * 0.5 - (u + 0.75 * np.cos(second)), band + 5.82 + 0.68 * np.sin(second))
            tools.beam(parts, a2, b2, 0.11, STRIPE)
    add(0.79, width - 0.79, 0.025, 0.91, band + 5.79, band + 6.06, GREEN)
    for u in np.linspace(0.32, width - 0.32, 21):
        rise = 0.85 * np.sin(np.pi * u / width) ** 1.4
        add(u - 0.17, u + 0.17, -0.20, 0.139, band + 9.42, band + 9.53 + rise, CREAM)
    for w, s, east, north in row["skylights"]:
        e, n = (w + east) * 0.5, (s + north) * 0.5
        plan = box(w, s, east, north)
        cap = roof_at(surfaces, e, n) + 0.63
        lowest = min(roof_at(surfaces, *corner) for corner in plan.exterior.coords)
        flat(parts, plan, lowest - 0.03, cap - 0.13, METAL, GRAY)
        flat(parts, plan.buffer(-0.12), cap - 0.13, cap, STRIPE, (185, 188, 171))


def build(spec, manifest, config, field, graph):
    meshes, ground, solids, supports, gates, pads, records = {}, [], [], [], [], [], []
    for code, row in spec["models"].items():
        outline = orient(Polygon(row["footprint_enu_m"]))
        floor, datum = science.earlier.fit_base(field, outline)
        parts, entries, feet = [], [], []
        for entry in row["entrances"]:
            assert outline.boundary.distance(Point(entry["position_enu_m"])) < 0.004
            gate, pad, blocks = shared.site_entry(ground, field, entry)
            entries.append(gate)
            pads.append(pad)
            feet.extend(blocks)
        surfaces = roof_shell(parts, outline, row, floor, WALLS[code])
        if code == "029":
            clinical_facade(parts, outline, surfaces, entries, field)
        elif code == "049":
            feet.extend(museum_facade(parts, row, outline, surfaces, entries, datum, field))
        elif code == "052":
            barn_facade(parts, row, outline, surfaces, entries, datum)
        else:
            agate_facade(parts, row, outline, surfaces, entries, datum)
        door_entries = [gate for gate in entries if gate["gate"] != "barn-east-bay"]
        prior.painted_doors(parts, shared.face_edges(outline), door_entries, CREAM, DARK_GLASS)
        raw = trimesh.util.concatenate(parts)
        raw.update_faces(raw.nondegenerate_faces(height=0.00005))
        mesh = science.ordered_mesh(raw)
        meshes[row["id"]] = mesh
        solids.append(outline)
        supports.extend(feet)
        gates.extend(entries)
        records.append({
            "id": row["id"], "name": row["name"], "campus_id": row["campus_id"],
            "footprint_enu_m": ring(outline), "ground_footprints_enu_m": [ring(outline)],
            "support_collision_enu_m": [ring(post) for post in feet],
            "entrances": entries, "base_z_m": round(floor, 4),
            "roof_z_m": round(float(mesh.bounds[1, 1]), 4), "area_m2": round(outline.area, 3),
        })
    previous = union([Polygon(row["footprint_enu_m"]).buffer(0) for row in manifest["buildings"] if row["id"] in meshes])
    edges, clearance = prior.nearby.shared.graduate.shared.check_routes(solids, supports, gates, previous, manifest, graph, config, set(meshes))
    paths = [LineString(path["line"]).buffer(path["width"] * 0.5, cap_style=2, join_style=2) for path in spec["paved_paths"]]
    prior.nearby.add_paths(ground, field, union([*paths, *pads]), union([*solids, *supports]), WALK)
    return meshes, records, science.ordered_mesh(trimesh.util.concatenate(ground)), edges, clearance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--spec", type=Path, default=SPEC)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_bytes())
    manifest_path = SCENE / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    assert tools.digest(manifest_path) == spec["sources"]["scene_manifest_sha256"]
    assert tools.digest(field_path) == spec["sources"]["heightfield_sha256"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, edges, clearance = build(spec, manifest, config, field, graph)
    appearances = json.loads((geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes())
    removals = shared.frohnmayer.source_removals({"absorbed_batches": spec["source_ranges"]}, config, appearances)
    output = args.stage or SCENE / DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    model = output / "site.glb"
    site.memorial.gerlinger.export(model, meshes, ground, GROUND, "public-building-exterior-paving")
    descriptor = output / "site.json"
    payload = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": tools.digest(field_path),
        "ground_node": GROUND,
        "url": f"{DIRECTORY}/site.glb",
        "sha256": tools.digest(model),
        "buildings": records,
        "absorbed_ids": [],
        "batch_removals": removals,
    }
    descriptor.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n")
    if args.stage is None:
        config["public_building_exterior_site"] = {"url": f"{DIRECTORY}/site.json", "sha256": tools.digest(descriptor)}
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf8", newline="\n")
    audit = {
        "buildings": records, "route_edges": edges, "nearest_route_m": round(clearance, 3),
        "triangles": {asset_id: len(mesh.faces) for asset_id, mesh in meshes.items()},
        "batch_removals": removals, "glb_sha256": payload["sha256"],
        "descriptor_sha256": tools.digest(descriptor),
    }
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n")
    print({key: audit[key] for key in ("route_edges", "nearest_route_m", "triangles", "glb_sha256")})


if __name__ == "__main__":
    main()
