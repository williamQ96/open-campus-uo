# SPDX-License-Identifier: Apache-2.0
"""Build the registered off-campus residential exterior review."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh


path = Path(__file__).with_name("build-office-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
office = module_from_spec(loader)
loader.loader.exec_module(office)
base, tools, site = office.base, office.tools, office.site
geometry, science, shared, prior = office.geometry, office.science, office.shared, office.prior
ROOT, SCENE = office.ROOT, office.SCENE
SPEC = ROOT / "data/metadata/residential-exterior-review.json"
DIRECTORY = "residential-exterior-review"
GROUND = "residential-approaches"

FRAME = (220, 219, 199)
GLASS = (89, 111, 113)
DARK = (68, 79, 75)
SLATE = (122, 134, 133)
CONCRETE = (174, 170, 155)
STEEL = (164, 166, 156)
BRICK = (143, 102, 84)
CEDAR = (163, 99, 66)
ZINC = (169, 175, 168)
ROYAL_SIDING = (136, 110, 99)
MATERIAL = {
    "lewis": (146, 141, 122),
    "clark": (154, 146, 128),
    "manor": (142, 117, 99),
    "royal": (163, 132, 117),
    "coho": CEDAR,
}


def source_cap(recipe):
    # The recipe is linear RGB. The shared GLB exporter accepts sRGB meshes.
    positions = np.asarray(recipe["position"]).reshape(-1, 3)
    rgb = np.asarray(recipe["color"]).reshape(-1, 3)
    srgb = np.where(rgb <= .0031308, rgb * 12.92, 1.055 * rgb ** (1 / 2.4) - .055)
    mesh = trimesh.Trimesh(positions, np.arange(len(positions)).reshape(-1, 3), process=False)
    mesh.visual.vertex_colors = np.column_stack((np.rint(srgb * 255), np.full(len(rgb), 255)))
    return mesh


def wall_plans(outline, row):
    inset = row["wall_inset_m"]
    if row["kind"] == "royal":
        # Split the main roof across the covered court connection. Both walls
        # stop short of the slot, including at its north end.
        return [
            orient(plan)
            for mask in (box(-1000, -355, -983.1, -300), box(-979.9, -355, -964, -300))
            for plan in geometry.sections(outline.intersection(mask).buffer(-inset, join_style="mitre"))
        ]
    return [orient(outline.buffer(-inset, join_style="mitre"))]


def entrance(ground, field, edges, hint):
    point = Point(hint["near_enu_m"])
    bearing = np.deg2rad(hint["outward_degrees"])
    desired = (np.sin(bearing), np.cos(bearing))
    candidates = []
    for a, b in edges:
        edge = LineString([a, b])
        unit = (np.asarray(b) - a) / edge.length
        outward = np.array([unit[1], -unit[0]])
        if outward.dot(desired) > .97 and edge.length > 2.1:
            candidates.append((edge, outward))
    edge, outward = min(candidates, key=lambda item: item[0].distance(point))
    anchor = edge.interpolate(np.clip(edge.project(point), .95, edge.length - .95))
    run = hint["landing_m"]
    at = np.asarray(anchor.coords[0])
    z_near = geometry.sample_ground(field, *at)
    z_toe = geometry.sample_ground(field, *(at + outward * run))
    gate = {
        "gate": hint["gate"],
        "position_enu_m": [round(x, 5) for x in at],
        "outward_degrees": round(float(np.rad2deg(np.arctan2(*outward))), 5),
        "width_m": 1.3,
        "landing_m": run,
        "rise_m": round(max(.035, z_near - z_toe + .04), 4),
        "approach_distance_m": run + .22,
    }
    return site.approach(ground, field, gate)[0]


def coursing(add, left, right, bottom, top, pitch, color, depth=.027):
    for z in np.arange(bottom, top - .05, pitch):
        add(left, right, 0, depth, z, z + .021, color)


def levels_at(grade, top, count):
    return np.linspace(grade + .57, top - 1.48, count)


def glazed_rows(add, centers, levels, width, frame=FRAME):
    for u in centers:
        for z in levels:
            prior.window(add, u, width, z, z + 1.14, frame, GLASS, ribs=1)


def quoin(add, length, base_z, eave):
    for z in np.arange(base_z + .38, eave - .24, .47):
        step = int(round((z - base_z - .38) / .47))
        width = .24 + .17 * (step % 2)
        add(0, width, -.01, .062, z, z + .442, (183, 166, 143))
        add(length - width, length, -.01, .062, z, z + .442, (183, 166, 143))


def balcony(add, u, width, z, projection, tone, opaque=False):
    left, right = u - width / 2, u + width / 2
    add(left, right, .012, projection, z - .17, z, CONCRETE)
    for end in (left, right):
        add(end - .034, end + .034, .045, projection, z + .07, z + .93, tone)
    add(left, right, projection - .06, projection + .018, z + .89, z + .97, tone)
    for x in np.linspace(left + .09, right - .09, round(width / .20) + 1):
        if opaque:
            add(x - .099, x + .099, projection - .085, projection - .03, z + .06, z + .90, tone)
        else:
            add(x - .013, x + .013, projection - .06, projection - .02, z, z + .90, tone)


def north_portico(parts, a, b, u, eave, grade, kind):
    length, add = tools.face(parts, a, b)
    unit = (np.asarray(b) - a) / length
    outward = np.array([unit[1], -unit[0]])
    anchor = np.asarray(a) + u * unit
    canopy_width = min(4.1, length - .28)
    projection = 2.64
    shade = (126, 115, 94) if kind == "lewis" else (139, 127, 110)
    for z in (grade + 2.38, eave - 2.02):
        for left, right in ((-.5, 0), (0, .5)):
            corners = [
                anchor + t * canopy_width * unit + s * outward
                for t, s in ((left, .035), (right, .035), (right, projection), (left, projection))
            ]
            geometry_piece = Polygon(corners)

            def height(e, n):
                t = (np.array([e, n]) - anchor).dot(unit) / canopy_width
                return z + .13 + .69 * (1 - 2 * abs(t))

            parts.append(geometry.shell(geometry_piece, z, height, FRAME, shade))
    for x in (u - canopy_width * .43, u + canopy_width * .43):
        add(x - .078, x + .078, 2.32, 2.48, grade + .02, grade + 2.42, FRAME)
    balcony(add, u, canopy_width - .22, eave - 4.06, 1.48, SLATE)
    return [Point(anchor + x * unit + 2.4 * outward).buffer(.079, quad_segs=1)
            for x in (-canopy_width * .43, canopy_width * .43)]


def walkup(parts, a, b, grade, eave, kind, entry):
    length, add = tools.face(parts, a, b)
    outside = np.array([b[1] - a[1], a[0] - b[0]]) / length
    north = outside[1] > .96
    supports = []
    if length < 4 and not entry:
        if kind == "manor" and length > 1.25:
            quoin(add, length, grade, eave)
        return supports

    add(.015, length - .015, -.014, .057, grade - .22, grade + .45, SLATE)
    add(.015, length - .015, -.015, .065, eave - .16, eave + .012, FRAME)
    if kind == "manor":
        quoin(add, length, grade, eave)
        if north:
            for u in (.28 * length, .73 * length):
                for z in (grade + 2.83, grade + 5.49):
                    prior.window(add, u, 1.20, z + .15, z + 1.73, FRAME, GLASS)
                    balcony(add, u, 1.65, z, .65, STEEL)
            add(.39 * length, .61 * length, -.03, .17, grade + 2.12, eave - .10, (185, 157, 131))
        else:
            glazed_rows(add, np.linspace(1.18, length - 1.18, max(1, round(length / 3.12))),
                        levels_at(grade, eave, 3), min(1.5, length / 4))
        return supports

    if entry:
        u = LineString([a, b]).project(Point(entry["position_enu_m"]))
        return north_portico(parts, a, b, u, eave, grade, kind)
    rows = levels_at(grade, eave, 3)
    pitch = 3.92 if kind == "lewis" else 3.32
    centers = np.linspace(1.22, length - 1.22, max(2, round(length / pitch)))
    glazed_rows(add, centers, rows, min(1.78, length / 4))
    if length > 9:
        for z in rows[1:]:
            for u in centers[:-1]:
                add(u + .93, u + 1.80, -.009, .038, z - .015, z + 1.17, SLATE)
    if kind == "clark" and length > 18:
        for u in np.linspace(length * .23, length * .77, 3):
            balcony(add, u, 1.68, rows[1] - .42, .70, SLATE)
    return supports


def royal(parts, ground, plans, edges, grade, eave, field):
    for a, b in edges:
        length, add = tools.face(parts, a, b)
        if length < 4.5:
            continue
        normal = (np.asarray(b) - a)[::-1] * [1, -1] / length
        court = (-984 < np.mean([a[0], b[0]]) < -979) and abs(normal[0]) > .91
        add(.015, length - .015, -.021, .052, grade + 2.58, eave - .05, ROYAL_SIDING)
        if length > 11:
            for u in np.arange(.32, length - .2, .38):
                add(u, u + .018, .039, .068, grade + 2.61, eave - .10, BRICK)
        for u in np.linspace(1.22, length - 1.22, max(2, round(length / 3.65))):
            glazed_rows(add, [u], [grade + .81], min(1.53, length / 4))
            if court:
                prior.window(add, u, 1.41, grade + 2.67, grade + 4.63, FRAME, GLASS)
                balcony(add, u, 1.52, grade + 2.62, .79, FRAME, opaque=True)
            else:
                glazed_rows(add, [u], [grade + 3.26], min(1.53, length / 4))

    # Outdoor stairs and perforated block screen alongside the west parking row.
    edge = max((line for line in edges if max(line[0][0], line[1][0]) < -992.8),
               key=lambda item: LineString(item).length)
    length, add = tools.face(parts, *edge)
    u = length * .15
    for step in range(15):
        z = grade + 2.64 * (step + 1) / 15
        t = u + .19 + step * .242
        add(t, t + .242, .056, 1.06, z - .14, z, CONCRETE)
        add(t, t + .028, .99, 1.04, z, z + .84, STEEL)
        add(t, t + .249, .966, 1.033, z + .84, z + .895, STEEL)
    balcony(add, u + 4.40, 1.19, grade + 2.64, 1.055, STEEL)
    screen_start = max(.15, u - 1.67)
    screen_end = u + .10
    for z in np.arange(grade + .03, grade + 4.42, .31):
        add(screen_start, screen_end, .66, .80, z, z + .105, FRAME)
        for t in np.arange(screen_start, screen_end - .12, .26):
            add(t, t + .118, .66, .80, z, z + .31, FRAME)

    center = LineString([(-981.43, -303.3), (-981.43, -332.4)])
    fountain = box(-982.35, -324.1, -980.55, -322.55)
    paving = center.buffer(.67, cap_style="flat").union(fountain.buffer(.89, join_style="mitre"))
    paving = paving.difference(shapely.union_all(plans))
    # Short terrain-following slabs keep the paving surface exposed along the court.
    for n in np.arange(-332.4, -303.3, 1.15):
        for area in geometry.sections(paving.intersection(box(-985, n, -978, n + 1.15))):
            z = min(geometry.sample_ground(field, *p) for p in area.exterior.coords) - .25
            ground.append(geometry.shell(area, z, lambda e, n: geometry.sample_ground(field, e, n) + .047,
                                         CONCRETE, CONCRETE))
    water = geometry.sample_ground(field, -981.45, -323.3)
    base.flat(ground, fountain.difference(fountain.buffer(-.19)), water - .2, water + .48, BRICK)
    base.flat(ground, fountain.buffer(-.19), water - .14, water + .26, SLATE, GLASS)
    # Low planted strips frame the path and leave both door approaches open.
    for x, northings in ((-983.27, (-315.8, -317.4, -324.8, -327.4, -329.4)),
                         (-979.72, (-314.8, -317.4, -320.4, -323.7))):
        for n in northings:
            z = geometry.sample_ground(field, x, n)
            planting = Point(x, n).buffer(.40, quad_segs=3)
            base.flat(ground, planting, z - .16, z + .16, BRICK, (115, 98, 77))
            base.flat(ground, planting.buffer(-.065), z + .07, z + .57,
                      (88, 106, 57), (108, 129, 64))
            base.flat(ground, planting.buffer(-.14), z + .54, z + .68, (108, 129, 64))
    return [fountain]


def coho(parts, a, b, grade, eave):
    length, add = tools.face(parts, a, b)
    if length < 3.6:
        return
    outward = np.array([b[1] - a[1], a[0] - b[0]]) / length
    if outward[1] > -.95 or length < 7:
        coursing(add, .05, length - .05, grade + .29, eave - .12, .19, BRICK)
        glazed_rows(add, np.linspace(1.1, length - 1.1, max(2, round(length / 3.9))),
                    levels_at(grade, eave, 3), min(1.32, length / 3.5))
        return

    for u in np.linspace(2.08, length - 2.08, 3):
        low = grade + 2.53
        left, right = u - 1.03, u + 1.03
        add(left, right, -.035, .73, low, eave - .14, ZINC)
        add(left - .14, right + .14, -.032, .94, eave - .17, eave - .053, DARK)
        add(left, right, .045, .37, grade + .04, low, CEDAR)
        for t in np.linspace(left + .038, right - .038, 22):
            add(t - .012, t + .012, .724, .755, low + .048, eave - .19, STEEL)
        for z in (low + .40, low + 2.82):
            add(left + .19, right - .19, .753, .779, z, z + 1.41, FRAME)
            add(left + .235, right - .235, .779, .81, z + .065, z + 1.345, GLASS)
            add(u - .023, u + .023, .809, .834, z + .04, z + 1.37, FRAME)


def build(spec, manifest, config, field, graph, recipes):
    records, models, ground = [], {}, []
    all_plans, all_supports, all_gates = [], [], []
    originals = {row["id"]: row for row in manifest["buildings"]}
    for row in spec["models"]:
        id, kind = row["id"], row["kind"]
        outline = orient(Polygon(originals[id]["footprint_enu_m"]))
        plans = wall_plans(outline, row)
        assert all(plan.is_valid and outline.covers(plan) for plan in plans)
        eave = recipes[id]["new_eave_z_m"]
        floor, grade = science.earlier.fit_base(field, outline)
        pieces = [source_cap(recipes[id]["cap"])]
        for plan in plans:
            base.flat(pieces, plan, floor, eave - .001, MATERIAL[kind])
        edges = [edge for plan in plans for edge in shared.face_edges(plan)]
        gates = [entrance(ground, field, edges, hint) for hint in row["entrance_hints"]]
        supports = []
        if kind == "royal":
            supports.extend(royal(pieces, ground, plans, edges, grade, eave, field))
        for a, b in edges:
            if kind == "coho":
                coho(pieces, a, b, grade, eave)
            elif kind != "royal":
                entry = shared.aligned_gate(a, b, gates)
                supports.extend(walkup(pieces, a, b, grade, eave, kind, entry))
        prior.painted_doors(pieces, edges, gates, FRAME, DARK)
        mesh = trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=.00006))
        models[id] = science.ordered_mesh(mesh)
        all_plans.extend(plans)
        all_supports.extend(supports)
        all_gates.extend(gates)
        records.append({
            "id": id, "name": row["name"], "street_address": row["street_address"],
            "footprint_enu_m": base.ring(outline),
            "ground_footprints_enu_m": [base.ring(plan) for plan in plans],
            "area_m2": round(sum(plan.area for plan in plans), 3),
            "support_collision_enu_m": [base.ring(plan) for plan in supports],
            "entrances": gates, "base_z_m": round(floor, 4),
            "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        })
    previous = shapely.union_all([Polygon(originals[id]["footprint_enu_m"]) for id in models])
    edges, clearance = prior.nearby.shared.graduate.shared.check_routes(
        all_plans, all_supports, all_gates, previous, manifest, graph, config, set(models)
    )
    return models, records, science.ordered_mesh(trimesh.util.concatenate(ground)), edges, clearance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--spec", type=Path, default=SPEC)
    args = parser.parse_args()
    manifest_path, config_path = SCENE / "manifest.json", SCENE / "presentation.json"
    spec, manifest, config = [json.loads(path.read_bytes()) for path in (args.spec, manifest_path, config_path)]
    terrain = SCENE / manifest["heightfield_url"]
    recipe_path = SCENE / "context-roof-refinements.json"
    for path, key in ((manifest_path, "source_manifest_sha256"),
                      (terrain, "source_heightfield_sha256"),
                      (recipe_path, "source_roof_recipe_sha256")):
        if tools.digest(path) != spec[key]:
            raise ValueError(f"Residential site source changed: {path.name}")
    roof_data = json.loads(recipe_path.read_bytes())
    if roof_data["source_presentation_sha256"] != config["asset_sha256"]:
        raise ValueError("Residential roof source does not match the active presentation.")
    recipes = {item["id"]: item for batch in roof_data["batches"] for item in batch["buildings"]}
    field = json.loads(terrain.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    models, records, ground, edges, clearance = build(spec, manifest, config, field, graph, recipes)
    appearances = json.loads((ROOT / "data/metadata/campus-expansion-audit.json").read_bytes())
    removals = shared.frohnmayer.source_removals({"absorbed_batches": spec["source_ranges"]}, config, appearances)
    assert all(row["triangles"] == recipes[row["id"]]["triangles"] for row in removals)
    output = args.stage or SCENE / DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    model, descriptor = output / "site.glb", output / "site.json"
    site.memorial.gerlinger.export(model, models, ground, GROUND, "residential-paving")
    package = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"], "ground_node": GROUND,
        "url": f"{DIRECTORY}/site.glb", "sha256": tools.digest(model), "buildings": records,
        "absorbed_ids": [], "batch_removals": removals,
    }
    descriptor.write_text(json.dumps(package, separators=(",", ":")) + "\n", encoding="utf8", newline="\n")
    if args.stage is None:
        config["residential_exterior_site"] = {"url": f"{DIRECTORY}/site.json", "sha256": tools.digest(descriptor)}
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf8", newline="\n")

    audit = {
        "buildings": records, "route_edges": edges, "nearest_route_m": round(clearance, 4),
        "triangles": {key: len(mesh.faces) for key, mesh in models.items()}, "batch_removals": removals,
        "glb_sha256": package["sha256"], "descriptor_sha256": tools.digest(descriptor),
    }
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n")
    print({key: audit[key] for key in ("route_edges", "nearest_route_m", "triangles", "glb_sha256")})


if __name__ == "__main__":
    main()
