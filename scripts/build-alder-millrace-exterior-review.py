# SPDX-License-Identifier: Apache-2.0
"""Build the registered Hess, Millrace and 1915 Alder Street exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import set_precision, union_all
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient
import trimesh


def load_builder(name):
    path = Path(__file__).with_name(name)
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


design = load_builder("build-villard-garden-exterior-review.py")
roof_builder = load_builder("build-context-roof-refinements.py")
base, geometry, chapter = design.base, design.geometry, design.chapter
neighbor, residential, shared = design.neighbor, design.residential, design.shared
SCENE, ROOT = design.SCENE, design.ROOT
DIRECTORY = "alder-millrace-exterior-review"
GROUND = "alder-millrace-approaches"
CONFIG_KEY = "alder_millrace_exterior_site"
SPEC = ROOT / "data/metadata/alder-millrace-exterior-review.json"
WHITE = (226, 222, 202)
CONCRETE = (163, 160, 143)
DARK = (53, 57, 53)
GREEN = (62, 89, 72)
PARKING = (102, 104, 94)


def rebuild_roof(parts, outline, fit, style):
    color = tuple(np.rint(roof_builder.roof_color(style["wall_color"])).astype(int))
    if fit["type"] == "flat":
        cap, _ = roof_builder.roof_cap(fit, outline, color)
    else:
        along, across = np.asarray(fit["axis"]), np.asarray(fit["normal_axis"])
        corners = np.asarray(outline.exterior.coords)
        local = corners @ np.vstack((along, across)).T
        lower, upper = local.min(axis=0), local.max(axis=0)
        center = (lower + upper) / 2
        cap, _ = roof_builder.roof_cap(
            fit | {
                "centroid": center[0] * along + center[1] * across,
                "dimensions_m": upper - lower + 0.00002,
            },
            outline,
            color,
        )
    vertices = np.asarray(cap["position"]).reshape(-1, 3)
    mesh = trimesh.Trimesh(
        vertices, np.arange(len(vertices)).reshape(-1, 3), process=False
    )
    # The editable recipe stores linear RGB and the GLB exporter expects sRGB bytes.
    rgb = np.asarray(cap["color"]).reshape(-1, 3)
    srgb = np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * rgb ** (1 / 2.4) - 0.055)
    mesh.visual.vertex_colors = np.column_stack(
        (np.rint(srgb * 255).astype(np.uint8), np.full(len(rgb), 255, dtype=np.uint8))
    )
    parts.append(mesh)


def window(add, u, width, low, high, frame=WHITE):
    chapter.prior.window(add, u, width, low, high, frame, design.GLASS, ribs=2)


def supported_post(parts, point, floor, top, tone, radius):
    foot = Point(point).buffer(radius, quad_segs=1, cap_style="square")
    base.flat(parts, foot, floor, top, tone)
    return foot


def gallery(add, left, right, depth, floor, color):
    add(left, right, -0.036, depth, floor - 0.19, floor, CONCRETE)
    neighbor.railing(add, left, right, depth, floor, color)
    for x in (left, right):
        add(x - 0.027, x + 0.027, 0, depth, floor + 0.88, floor + 0.94, color)


def entry_stair(parts, ground, edges, field, row, target_z, *, top_run=0.72):
    hint = row["entrance"]
    edge = design.locate_face(edges, hint["near_enu_m"], hint["outward_degrees"])
    length, add, outward, position, _, _ = chapter.setup_face(parts, *edge)
    width = hint.get("width_m", 1.3)
    half = width / 2 + 0.02
    margin = max(0.81, half + 0.10)
    if length < 2 * margin:
        raise ValueError(f"Entrance does not fit on {row['id']}.")
    u = np.clip(LineString(edge).project(Point(hint["near_enu_m"])), margin, length - margin)
    run = hint["landing_m"]
    anchor = position(u, 0)
    toe = geometry.sample_ground(field, *position(u, run))
    threshold = target_z if target_z is not None else (
        max(toe, geometry.sample_ground(field, *anchor)) + hint["threshold_above_grade_m"]
    )
    rise = threshold - toe
    count = max(1, round(rise / 0.172))
    assert rise >= 0 and run - top_run >= 0.17 * max(1, count - 1), row["id"]
    left, right = u - half, u + half
    for i in range(count):
        top = toe + (i + 1) * rise / count
        end = run - (run - top_run) * i / max(1, count - 1)
        add(left, right, -0.03, end, toe - 0.24, top, CONCRETE)
        if rise > 0.45:
            for x in (left + 0.055, right - 0.055):
                add(x - 0.018, x + 0.018, end - 0.073, end - 0.025, top, top + 0.88, DARK)
    base.flat(
        ground,
        Polygon([position(a, b) for a, b in (
            (left, run - 0.02), (right, run - 0.02),
            (right, run + 0.50), (left, run + 0.50),
        )]),
        toe - 0.2,
        toe + 0.025,
        CONCRETE,
    )
    if hint.get("glazed_double"):
        frame = tuple(row["door_color"])
        left_leaf, right_leaf = u - width / 4, u + width / 4
        for center in (left_leaf, right_leaf):
            panel = width / 2 - 0.06
            chapter.prior.window(add, center, panel, threshold + 0.06,
                                 threshold + 2.20, frame, design.GLASS, ribs=1)
            add(center - panel / 2, center + panel / 2, 0.075, 0.145,
                threshold + 1.01, threshold + 1.065, frame)
    elif not hint.get("landing_only"):
        neighbor.door(add, u, threshold, tuple(row["door_color"]))
    return {
        "gate": hint.get("gate", "street-entry"),
        "position_enu_m": np.round(anchor, 5).tolist(),
        "outward_degrees": round(float(np.degrees(np.arctan2(*outward))), 5),
        "width_m": width,
        "landing_m": run,
        "rise_m": round(float(rise), 4),
        "approach_distance_m": run + 0.22,
        "threshold_z_m": round(float(threshold), 4),
        **({"snap_to_facade": False} if hint.get("landing_only") else {}),
    }, edge, u


def alder(parts, field, edges, gate, door_edge, u_door, eave):
    trim = (224, 216, 188)
    supports = []
    for edge in edges:
        length, add, _, position, _, _ = chapter.setup_face(parts, *edge)
        ground = geometry.sample_ground(field, *position(length / 2, 0))
        residential.coursing(add, 0.02, length - 0.02, ground + 0.13, eave, 0.095, (119, 71, 59), 0.013)
        add(0, length, 0.008, 0.135, eave - 0.17, eave, trim)
        levels = (eave - 3.66, eave - 1.56)
        if edge == door_edge:
            for u in (length * 0.196, length * 0.795):
                window(add, u, 2.30, levels[0], levels[0] + 1.24, trim)
                window(add, u, 2.30, levels[1], levels[1] + 1.20, trim)
                window(add, u, 0.64, ground + 0.27, ground + 0.73, trim)
                for level in levels:
                    for dx in (-1.28, 1.12):
                        add(u + dx, u + dx + 0.16, 0.021, 0.086, level, level + 1.22, DARK)
            window(add, u_door, 0.96, levels[1], levels[1] + 1.22, trim)
            z = gate["threshold_z_m"] + 2.35
            add(u_door - 1.61, u_door + 1.61, -0.03, 1.26, z, z + 0.16, trim)
            for u in (u_door - 1.36, u_door + 1.36):
                point = position(u, 1.08)
                supports.append(supported_post(
                    parts, point, geometry.sample_ground(field, *point) - 0.05, z, trim, 0.09
                ))
        else:
            for u in np.linspace(1.7, length - 1.7, round(length / 4)):
                for level in levels:
                    window(add, u, 1.17, level, level + 1.21, trim)
    return supports


def hess(parts, field, outline, edges, door_edge, first, eave, base_z, color):
    # The upper residential mass spans an open covered drive at the Alder end.
    west, south, east, _ = outline.bounds
    core = outline.intersection(Polygon([
        (west - 1, south - 1), (east - 4.4, south - 1),
        (east - 4.4, outline.bounds[3] + 1), (west - 1, outline.bounds[3] + 1),
    ]))
    base.flat(parts, core, base_z, first - 0.17, PARKING)
    supports = []
    for e, n in ((east - 0.75, -96.0), (east - 0.74, -104.27), (east - 3.5, -104.22)):
        point = (e, n)
        assert outline.covers(Point(point))
        supports.append(supported_post(parts, point, base_z, first - 0.17, CONCRETE, 0.22))
    base.flat(parts, outline, first - 0.171, eave - 0.001, color)
    for edge in edges:
        length, add, outward, _, _, _ = chapter.setup_face(parts, *edge)
        if length < 2.15:
            continue
        residential.coursing(add, 0, length, first - 0.13, first + 0.10, 0.32, CONCRETE)
        for u in np.arange(0.12, length - 0.08, 0.34):
            add(u, u + 0.020, 0.002, 0.019, first + 0.1, eave - 0.02, (104, 99, 79))
        for level in (first, first + 2.95, first + 5.88):
            span = min(1.55, length * 0.29)
            for u in np.linspace(span + 0.21, length - span - 0.21, max(2, round(length / 4.3))):
                window(add, u, span, level + 0.71, level + 1.93, (192, 189, 170))
            if edge == door_edge:
                gallery(add, 0.12, 1.96, 0.95, level, DARK)
                add(0.13, 1.87, 0.885, 0.959, level + 0.06, level + 0.72, color)
            if outward[1] < -0.96 and length > 2.9:
                gallery(add, 0.12, length - 0.12, 1.12, level, DARK)
            if outward[1] > 0.96:
                gallery(add, 0.14, length - 0.14, 0.95, level, DARK)
        if outward[1] > 0.96 and length > 10:
            neighbor.side_stair(add, length - 5.02, 1.96, first, 2.95)
            neighbor.side_stair(add, length - 5.02, 1.96, first + 2.95, 2.93, reverse=True)
    return [orient(p) for p in geometry.sections(core)], supports


def millrace(parts, field, edges, door_edge, u_door, eave, floor, color):
    first, second = eave - 5.57, eave - 2.77
    supports = []
    for edge in edges:
        length, add, outward, position, _, _ = chapter.setup_face(parts, *edge)
        residential.coursing(add, 0.014, length - 0.014, floor + 0.30, eave - 0.10,
                            0.18, (179, 180, 170))
        add(0.014, length - 0.014, 0.001, 0.085, eave - 0.13, eave, WHITE)
        if abs(outward[0]) > 0.95:
            continue
        count = 5 if outward[1] < 0 else 6
        stride = length / count
        for i in range(count):
            left, right = i * stride + 0.12, (i + 1) * stride - 0.12
            center = (left + right) / 2
            window(add, center, 0.91, second + 0.57, second + 2.10)
            window(add, center - 0.49, 1.28, first + 0.56, first + 1.81)
            if edge != door_edge or abs(center - u_door) > 1.6:
                window(add, center, 1.11, first - 2.12, first - 0.61)
            if edge == door_edge and abs(center - u_door) <= 1.6:
                near = min(u_door - 0.83, right)
                far = max(u_door + 0.83, left)
                ranges = [(left, near), (far, right)]
            else:
                ranges = [(left, right)]
            for start, end in ranges:
                if end - start > 0.48:
                    add(start, end, 1.01, 1.073, first - 2.60, first - 1.43, color)
            gallery(add, left, right, 1.04, first, GREEN)
        for u in np.linspace(0.16, length - 0.16, count + 1):
            point = position(u, 0.995)
            bottom = geometry.sample_ground(field, *point) - 0.03
            supports.append(supported_post(parts, point, bottom, second + 0.22, GREEN, 0.065))
            add(u - 0.028, u + 0.028, 0.027, 0.092, second, eave + 0.04, GREEN)
        if outward[1] > 0.95:
            toe = geometry.sample_ground(field, *position(0.44, 1.9))
            neighbor.side_stair(add, 0.22, 1.92, toe, first - toe)
    return supports


def build(spec, manifest, config, field, graph, fits):
    models, records, ground, plans, supports, gates = {}, [], [], [], [], []
    originals = {row["id"]: row for row in manifest["buildings"]}
    previous = union_all([Polygon(originals[row["id"]]["footprint_enu_m"]) for row in spec["models"]])
    for row in spec["models"]:
        id = row["id"]
        plan = orient(set_precision(Polygon(row["footprint_enu_m"]), 0.002))
        assert plan.is_valid
        outline = orient(plan.buffer(row["eaves_m"], join_style="mitre"))
        edges = list(shared.face_edges(plan))
        fit = fits[id]
        eave = fit["coefficients"][0]
        floor, _ = design.science.earlier.fit_base(field, plan)
        color = tuple(row["wall_color"])
        pieces = []
        rebuild_roof(pieces, outline, fit, row)
        first = eave - 9.73 if row["kind"] == "hess" else None
        gate, door_edge, u = entry_stair(pieces, ground, edges, field, row, first)
        if row["kind"] == "hess":
            occupied, feet = hess(pieces, field, plan, edges, door_edge, first, eave, floor, color)
        else:
            occupied = [plan]
            base.flat(pieces, plan, floor, eave - 0.001, color)
            feet = (
                alder(pieces, field, edges, gate, door_edge, u, eave)
                if row["kind"] == "alder"
                else millrace(pieces, field, edges, door_edge, u, eave, floor, color)
            )
        mesh = trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.000012))
        models[id] = design.science.ordered_mesh(mesh)
        plans.extend(occupied)
        supports.extend(feet)
        gates.append(gate)
        records.append({
            "id": id,
            "name": row["name"],
            "street_address": row["street_address"],
            "footprint_enu_m": base.ring(plan),
            "ground_footprints_enu_m": [base.ring(p) for p in occupied],
            "support_collision_enu_m": [base.ring(p) for p in feet],
            "area_m2": round(plan.area, 3),
            "entrances": [gate],
            "base_z_m": round(floor, 4),
            "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        })
    count, clearance = chapter.prior.nearby.shared.graduate.shared.check_routes(
        plans, supports, gates, previous, manifest, graph, config, set(models)
    )
    return models, records, design.science.ordered_mesh(trimesh.util.concatenate(ground)), count, clearance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest_path, config_path = SCENE / "manifest.json", SCENE / "presentation.json"
    manifest, config = [json.loads(path.read_bytes()) for path in (manifest_path, config_path)]
    terrain = SCENE / manifest["heightfield_url"]
    parameters = ROOT / "data/metadata/context-roof-refinements.json"
    recipes = SCENE / "context-roof-refinements.json"
    for path, key in (
        (manifest_path, "source_manifest_sha256"),
        (terrain, "source_heightfield_sha256"),
        (parameters, "source_roof_parameters_sha256"),
        (recipes, "source_roof_recipe_sha256"),
    ):
        if design.tools.digest(path) != spec[key]:
            raise ValueError(f"Changed source for registered exteriors: {path.name}")
    fits = {fit["id"]: fit for fit in json.loads(parameters.read_bytes())["fits"]}
    models, records, ground, edges, clearance = build(
        spec, manifest, config, json.loads(terrain.read_bytes()),
        json.loads((SCENE / "navigation.json").read_bytes()), fits,
    )
    appearances = json.loads((ROOT / "data/metadata/campus-expansion-audit.json").read_bytes())
    patches = shared.frohnmayer.source_removals(
        {"absorbed_batches": [{"id": id, "target": fits[id]["batch"]} for id in models]},
        config, appearances,
    )
    registered = {
        item["id"]: item
        for batch in json.loads(recipes.read_bytes())["batches"]
        for item in batch["buildings"]
    }
    assert all(patch["triangles"] == registered[patch["id"]]["triangles"] for patch in patches)
    output = args.stage or SCENE / DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    model, descriptor = output / "site.glb", output / "site.json"
    design.site.memorial.gerlinger.export(model, models, ground, GROUND, "alder-millrace-paving")
    bundle = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{DIRECTORY}/site.glb",
        "sha256": design.tools.digest(model),
        "buildings": records,
        "absorbed_ids": [],
        "batch_removals": patches,
    }
    descriptor.write_text(json.dumps(bundle, separators=(",", ":")) + "\n", encoding="utf8")
    digest = design.tools.digest(descriptor)
    if args.stage is None:
        config[CONFIG_KEY] = {"url": f"{DIRECTORY}/site.json", "sha256": digest}
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    audit = {
        "buildings": records, "route_edges": edges, "nearest_route_m": round(clearance, 4),
        "triangles": {key: len(mesh.faces) for key, mesh in models.items()},
        "batch_removals": patches, "glb_sha256": bundle["sha256"], "descriptor_sha256": digest,
    }
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf8")
    print({key: audit[key] for key in ("route_edges", "nearest_route_m", "triangles", "glb_sha256")})


if __name__ == "__main__":
    main()
