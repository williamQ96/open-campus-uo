# SPDX-License-Identifier: Apache-2.0
"""Rebuild the registered Fairmount houses and two Kincaid-area chapter houses."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import nearest_points
import trimesh

path = Path(__file__).with_name("build-millrace-fairmount-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
millrace = module_from_spec(loader)
loader.loader.exec_module(millrace)
ROOT, SCENE = millrace.ROOT, millrace.SCENE
base, garden, geometry, prior = (
    millrace.base,
    millrace.garden,
    millrace.geometry,
    millrace.prior,
)
chapter = prior.chapter
beam = garden.tools.beam
PACKAGE = "fairmount-kincaid-exterior-review"
GROUND = "fairmount-kincaid-approaches"
MASONRY = (151, 139, 119)
WOOD = (123, 87, 62)
CONCRETE = (168, 163, 148)
BRICK = (153, 102, 83)
IRON = (70, 76, 72)


def bearing_vector(degrees):
    angle = np.deg2rad(degrees)
    return np.array([np.sin(angle), np.cos(angle)])


def rectangle(plan, a, b, start, stop):
    return orient(
        Polygon([plan(a, start), plan(b, start), plan(b, stop), plan(a, stop)])
    )


def views(parts, outline):
    for a, b in garden.shared.face_edges(orient(outline)):
        yield LineString((a, b)), chapter.setup_face(parts, a, b)


def trim_courses(row, add, width, grade, top):
    is_brick = row["front"].get("brick", False)
    pitch = 0.203 if is_brick else row["front"]["siding_pitch_m"]
    shade = np.asarray(row["wall_color"]) * (0.90 if is_brick else 0.92)
    add(
        0.014,
        width - 0.014,
        0.004,
        0.028,
        grade - 0.13,
        min(grade + 0.35, top),
        MASONRY,
    )
    shade = np.round(shade).astype(int)
    for y in np.arange(grade + 0.30 + pitch, top - 0.18, pitch):
        add(0.024, width - 0.024, 0.022, 0.038, y, y + 0.011, shade)


def facade(parts, row, wall, field, roof_at, door_edge, door_point):
    forward = bearing_vector(row["front"]["bearing"])
    trim = row["trim_color"]
    for line, (span, add, normal, plan, _, _) in views(parts, wall):
        if span < 1.30:
            continue
        z = geometry.sample_ground(field, *plan(span / 2, 0))
        top = min(roof_at(plan(u, 0)) for u in np.linspace(0.11, span - 0.11, 6))
        trim_courses(row, add, span, z, top)
        at = (
            line.project(door_point)
            if door_edge is not None and line.equals(door_edge)
            else -10
        )
        if normal @ forward > 0.94 and span > 4.1:
            primary_windows(row, add, span, at, z, top)
        elif span > 2.06:
            for u in np.linspace(
                span * 0.19, span * 0.81, min(7, max(2, round(span / 3.1)))
            ):
                if min(u, span - u) < 0.49 or abs(u - at) < 1.03:
                    continue
                for sill in row["front"]["secondary_levels"]:
                    if z + sill + 1.06 < top - 0.28:
                        millrace.window(
                            add, u, min(span * 0.24, 1.13), z + sill, 1.06, trim
                        )


def primary_windows(row, add, span, door_at, grade, top):
    trim = row["trim_color"]
    for band in row["window_rows"]:
        width = min(band["width_m"], span / len(band["positions"]) * 0.75)
        y = grade + band["sill"]
        if y + band["height_m"] >= top - 0.19:
            continue
        for center in band["positions"]:
            u = span * center
            margin = width / 2 + (0.48 if band["shutters"] else 0.07)
            beside_door = band["sill"] < 2.15 and abs(u - door_at) < margin + 0.71
            if min(u, span - u) < margin or beside_door:
                continue
            if band["shutters"]:
                chapter.sash(
                    add, u, y, width, band["height_m"], shutters=True, color=trim
                )
            else:
                millrace.window(
                    add, u, width, y, band["height_m"], trim, ribs=band["ribs"]
                )


def landing(parts, plan, at, spec, threshold, ground):
    rise = threshold - ground
    steps = max(1, round(rise / 0.16))
    for step in range(steps):
        reach = 0.29 * (steps - step)
        base.flat(
            parts,
            rectangle(plan, at - 0.65, at + 0.65, -0.025, reach),
            ground - 0.12,
            ground + rise * (step + 1) / steps,
            CONCRETE,
        )
    if rise >= 0.36:
        for side in (-1, 1):
            u = at + side * 0.69
            lower, upper = plan(u, 0.29 * steps), plan(u, 0.10)
            beam(
                parts,
                (*lower, ground + 0.82),
                (*upper, threshold + 0.84),
                0.037,
                spec["trim_color"],
            )
            beam(
                parts,
                (*lower, ground + 0.03),
                (*lower, ground + 0.85),
                0.032,
                spec["trim_color"],
            )
            beam(
                parts,
                (*upper, threshold),
                (*upper, threshold + 0.84),
                0.032,
                spec["trim_color"],
            )


def pediment(parts, add, plan, at, level, style, post_color, roof):
    width, depth, rise = (style[name] for name in ("half_width", "depth", "rise"))
    cap = level + 2.68
    for side in (-1, 1):
        x = at + side * (width - 0.2)
        add(x - 0.13, x + 0.13, 0.02, depth * 0.66, level, cap, post_color)
        add(x - 0.20, x + 0.20, 0.017, depth * 0.72, cap - 0.13, cap + 0.04, post_color)
    add(at - width, at + width, 0.011, depth, cap - 0.19, cap, post_color)
    chapter.gabled_canopy(
        parts, plan, at, width, 0.015, depth, cap, rise, roof, post_color
    )
    arc = [
        (*plan(at + 0.49 * np.cos(t), 0.15), level + 1.79 + 0.43 * np.sin(t))
        for t in np.linspace(0, np.pi, 12)
    ]
    for a, b in zip(arc, arc[1:]):
        beam(parts, a, b, 0.045, post_color)


def porch(parts, add, plan, at, level, style, trim, roof, field):
    width, depth, rise = (style[k] for k in ("half_width", "depth", "rise"))
    cap = level + 2.32
    chapter.gabled_canopy(parts, plan, at, width, 0.005, depth, cap, rise, roof, trim)
    support = []
    for u in (at - width + 0.16, at + width - 0.16):
        pad = rectangle(plan, u - 0.083, u + 0.083, depth - 0.23, depth - 0.065)
        foot = geometry.sample_ground(field, *pad.centroid.coords[0])
        base.flat(parts, pad, foot - 0.03, cap, trim)
        support.append(pad)
        base.flat(
            parts,
            pad.buffer(0.043, join_style="mitre"),
            foot - 0.04,
            foot + 0.28,
            CONCRETE,
        )
        add(
            u - 0.14,
            u + 0.14,
            depth - 0.27,
            depth - 0.025,
            cap - 0.10,
            cap + 0.03,
            trim,
        )
    return support


def entrance(parts, row, wall, field, paving):
    spec = row["entry"]
    if spec is None:
        return None, None, None, []
    bearing = row["front"]["bearing"]
    edge = garden.locate_face(
        list(garden.shared.face_edges(wall)), spec["near"], bearing
    )
    line = LineString(edge)
    point = nearest_points(line, Point(spec["near"]))[0]
    assert point.distance(Point(spec["near"])) < 0.85, row["id"]
    _, add, _, plan = millrace.basis(parts, *edge)
    z = millrace.approach(paving, field, point, spec["approach_m"], bearing) - 0.08
    at = line.project(point)
    level = z + spec["rise_m"]
    landing(parts, plan, at, row, level, z)
    millrace.door(add, at, level, row["trim_color"])
    supports = []
    style = row["porch"]
    if style:
        if style["style"] == "pediment":
            pediment(
                parts, add, plan, at, level, style, row["trim_color"], row["roof_color"]
            )
        else:
            supports = porch(
                parts,
                add,
                plan,
                at,
                level,
                style,
                row["trim_color"],
                row["roof_color"],
                field,
            )
    gate = {
        "gate": spec["gate"],
        "position_enu_m": [round(v, 5) for v in point.coords[0]],
        "outward_degrees": bearing,
        "threshold_z_m": round(level, 4),
        "width_m": 1.03,
        "approach_distance_m": spec["approach_m"],
        "estimated": True,
        "snap_to_facade": False,
    }
    return gate, line, point, supports


def dormer(parts, row, spec, roof_at, outline):
    direction = bearing_vector(spec["bearing"])
    along = np.array([-direction[1], direction[0]])
    center = np.asarray(spec["near"])
    width = spec["width"]
    a, b = (center + sign * width * along / 2 for sign in (-1, 1))
    span, add, _, plan, _, _ = chapter.setup_face(parts, a, b)
    footprint = rectangle(plan, 0, span, -spec["depth"], 0)
    assert outline.buffer(0.09).covers(footprint), row["id"]
    z, top = spec["sill"], spec["top"]
    base.flat(
        parts,
        footprint,
        min(roof_at(p) for p in footprint.exterior.coords) - 0.15,
        top,
        row["wall_color"],
        row["roof_color"],
    )
    trim = row["trim_color"]
    bank = span / spec["windows"]
    for index in range(spec["windows"]):
        u = (index + 0.5) * bank
        y = max(z + 0.15, roof_at(plan(u, 0)) + 0.065)
        if top - y > 0.46:
            millrace.window(add, u, bank * 0.81, y, top - y - 0.18, trim, ribs=2)
    if spec["style"] == "gable":
        chapter.gabled_canopy(
            parts,
            plan,
            span / 2,
            span / 2 + 0.09,
            -spec["depth"],
            0.13,
            top,
            0.29,
            row["roof_color"],
            trim,
        )
    else:
        add(0, span, 0.004, 0.15, top - 0.17, top + 0.038, trim)


def balustrade(parts, a, b, z, color):
    a, b = np.asarray(a), np.asarray(b)
    count = max(2, round(np.linalg.norm(b - a) / 0.32))
    for at in np.linspace(a, b, count):
        beam(parts, (*at, z), (*at, z + 0.77), 0.038, color)
    for h in (0.12, 0.77):
        beam(parts, (*a, z + h), (*b, z + h), 0.056, color)


def gallery(parts, spec, field, trim):
    b, a = (np.asarray(spec[k]) for k in ("a", "b"))
    length, add, _, plan, _, _ = chapter.setup_face(parts, a, b)
    cap, upper, reach = (spec[k] for k in ("column_top", "architrave_top", "depth"))
    canopy = rectangle(plan, 0, length, -0.095, reach)
    base.flat(parts, canopy, cap, upper, trim, (170, 169, 154))
    piers = []
    for u in np.linspace(0.28, length - 0.28, 5):
        extent = rectangle(plan, u - 0.13, u + 0.13, reach - 0.36, reach - 0.09)
        bottom = geometry.sample_ground(field, *extent.centroid.coords[0])
        base.flat(parts, extent, bottom - 0.085, cap + 0.03, trim)
        base.flat(
            parts,
            extent.buffer(0.052, join_style="mitre"),
            bottom - 0.095,
            bottom + 0.16,
            trim,
        )
        base.flat(
            parts,
            extent.buffer(0.037, join_style="mitre"),
            cap - 0.17,
            cap + 0.04,
            trim,
        )
        piers.append(extent)
    balustrade(
        parts, plan(0.11, reach - 0.08), plan(length - 0.11, reach - 0.08), upper, trim
    )
    for u in np.arange(0.28, length - 1.0, 1.15):
        end = min(u + 0.86, length - 0.15)
        for low, high in ((upper + 0.18, upper + 0.66), (upper + 0.66, upper + 0.18)):
            beam(
                parts,
                (*plan(u, reach - 0.047), low),
                (*plan(end, reach - 0.047), high),
                0.034,
                trim,
            )
    return piers


def supplements(parts, row, field, wall, roof_at):
    trim = row["trim_color"]
    supports = []
    for spec in row["details"]:
        kind = spec["kind"]
        if kind == "gallery":
            supports.extend(gallery(parts, spec, field, trim))
        elif kind == "rail":
            balustrade(parts, spec["a"], spec["b"], spec["z"], trim)
        elif kind == "attic":
            pair = garden.locate_face(
                list(garden.shared.face_edges(wall)), spec["near"], spec["bearing"]
            )
            _, add, _, plan = millrace.basis(parts, *pair)
            at = LineString(pair).project(Point(spec["near"]))
            if spec.get("round"):
                points = [
                    (
                        *plan(at + 0.24 * np.cos(theta), 0.073),
                        spec["z"] + 0.24 * np.sin(theta),
                    )
                    for theta in np.linspace(0, 2 * np.pi, 17)
                ]
                for first, last in zip(points, points[1:]):
                    beam(parts, first, last, 0.050, trim)
            else:
                millrace.window(add, at, 0.90, spec["z"], 0.79, trim, ribs=2)
        elif kind == "garage":
            pair = garden.locate_face(
                list(garden.shared.face_edges(wall)), spec["near"], spec["bearing"]
            )
            length, add, _, plan = millrace.basis(parts, *pair)
            at = LineString(pair).project(Point(spec["near"]))
            center = np.clip(at, 1.54, length - 1.54)
            z = geometry.sample_ground(field, *plan(center, 0))
            low, high = (center + sign * spec["width"] / 2 for sign in (-1, 1))
            add(low - 0.105, high + 0.105, 0.02, 0.09, z, z + 2.32, trim)
            add(low, high, 0.09, 0.11, z + 0.035, z + 2.14, WOOD)
            for x in np.arange(low + 0.11, high - 0.052, 0.24):
                add(x, x + 0.028, 0.111, 0.129, z + 0.055, z + 2.11, BRICK)
        elif kind == "wing":
            span, add, _, plan, _, _ = chapter.setup_face(parts, spec["b"], spec["a"])
            grade = geometry.sample_ground(field, *plan(span / 2, 0))
            add(
                0.025,
                span - 0.025,
                0.051,
                0.067,
                grade + 0.13,
                grade + spec["height"],
                trim,
            )
            for u in np.arange(1.12, span - 0.7, 2.62):
                millrace.window(add, u, 1.88, grade + 0.94, 1.41, trim, ribs=3)
            add(
                0.02,
                span - 0.02,
                0.011,
                0.101,
                grade + 3.08,
                grade + spec["height"] + 0.06,
                trim,
            )
        elif kind == "timber":
            forward = bearing_vector(row["front"]["bearing"])
            for _, (length, add, normal, plan, _, _) in views(parts, wall):
                if normal @ forward < 0.93 or length < 7:
                    continue
                grade = geometry.sample_ground(field, *plan(length / 2, 0))
                span = length * spec["fraction"]
                add(0.09, span, 0.023, 0.045, grade + 0.48, grade + 3.15, trim)
                for h in spec["levels"]:
                    add(0.04, span, 0.046, 0.063, grade + h, grade + h + 0.09, WOOD)
                for k in np.linspace(0.12, span, 7):
                    add(
                        k - 0.045,
                        k + 0.045,
                        0.046,
                        0.064,
                        grade + 0.48,
                        grade + 3.15,
                        WOOD,
                    )
    for x, n, half, length in row["chimneys"]:
        z = roof_at((x, n))
        volume = box(x - half, n - half * 0.75, x + half, n + half * 0.75)
        base.flat(parts, volume, z - 0.61, z + length, BRICK)
        base.flat(
            parts,
            volume.buffer(0.085, join_style="mitre"),
            z + length - 0.11,
            z + length,
            CONCRETE,
        )
    return supports


def build(row, field, paving):
    outline = orient(Polygon(row["outline_enu_m"]))
    assert outline.is_valid, row["id"]
    wall = orient(outline.buffer(-0.135, join_style="mitre"))
    floor, _ = garden.science.earlier.fit_base(field, wall)
    parts = []
    roof_at = garden.roof_sections(parts, outline, wall, floor, row, grid=0.0002)
    gate, edge, point, supports = entrance(parts, row, wall, field, paving)
    facade(parts, row, wall, field, roof_at, edge, point)
    for dormer_spec in row["dormers"]:
        dormer(parts, row, dormer_spec, roof_at, outline)
    supports.extend(supplements(parts, row, field, wall, roof_at))
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000025))
    mesh = garden.science.ordered_mesh(mesh)
    return (
        mesh,
        {
            **{k: row[k] for k in ("id", "name", "street_address")},
            "footprint_enu_m": base.ring(outline),
            "ground_footprints_enu_m": [base.ring(wall)],
            "support_collision_enu_m": [base.ring(pier) for pier in supports],
            "area_m2": round(outline.area, 3),
            "base_z_m": round(floor, 4),
            "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
            "entrances": [gate] if gate else [],
        },
        wall,
        supports,
    )


def write_json(path, data, *, compact=False):
    content = (
        json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        if compact
        else json.dumps(data, ensure_ascii=False, indent=2)
    )
    path.write_text(content + "\n", encoding="utf-8", newline="\n")


def export_review(
    args, package, ground_name, descriptor_key, build_model, *, source_removals=None,
    collision_reference=None
):
    meta = ROOT / "data/metadata"
    spec = json.loads((meta / f"{package}.json").read_bytes())
    manifest_path, config_path = (
        SCENE / p for p in ("manifest.json", "presentation.json")
    )
    manifest, config = [
        json.loads(p.read_bytes()) for p in (manifest_path, config_path)
    ]
    digest = garden.tools.digest
    field_path = SCENE / manifest["heightfield_url"]
    assert digest(manifest_path) == spec["source_manifest_sha256"]
    assert digest(field_path) == spec["source_heightfield_sha256"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, paving, walls, supports = {}, [], [], [], []
    for model in spec["models"]:
        mesh, record, wall, piers = build_model(model, field, paving)
        meshes[model["id"]] = mesh
        records.append(record)
        walls.append(wall)
        supports.extend(piers)
    replaced = set(meshes)
    prior_ids = {record["id"] for record in manifest["buildings"]}
    splits = spec.get("source_split", {})
    added = spec.get("new_building_ids", [])
    retired = spec.get("absorbed_ids", [])
    assert len(added) == len(set(added)) and set(added).isdisjoint(splits)
    assert set(added) | set(splits) == replaced - prior_ids
    assert len(retired) == len(set(retired)) and set(retired) <= prior_ids - replaced
    original_ids = replaced | set(retired)
    original = union_all(
        [
            Polygon(b["footprint_enu_m"])
            for b in manifest["buildings"]
            if b["id"] in original_ids
        ]
    )
    assert all(
        a.intersection(b).area < 0.01
        for i, a in enumerate(walls)
        for b in walls[i + 1 :]
    )
    checks = chapter.prior.nearby.shared.graduate.shared.check_routes
    count, clearance = checks(
        walls,
        supports,
        [e for r in records for e in r["entrances"]],
        original,
        collision_reference(manifest, config) if collision_reference else manifest,
        graph,
        config,
        original_ids,
    )
    source_audit = json.loads((meta / "campus-expansion-audit.json").read_bytes())
    if source_removals is None:
        removals = garden.shared.frohnmayer.source_removals(
            {"absorbed_batches": spec["source_ranges"]}, config, source_audit
        )
    else:
        removals = source_removals(spec, config, source_audit)
    output = args.stage or SCENE / package
    output.mkdir(parents=True, exist_ok=True)
    model, descriptor = output / "site.glb", output / "site.json"
    ground = garden.science.ordered_mesh(trimesh.util.concatenate(paving))
    garden.site.memorial.gerlinger.export(
        model, meshes, ground, ground_name, ground_name
    )
    payload = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": ground_name,
        "url": f"{package}/site.glb",
        "sha256": digest(model),
        "buildings": records,
        "batch_removals": removals,
    }
    if splits:
        assert set(splits.values()) <= {item["id"] for item in removals}
        payload["split_buildings"] = splits
    if added:
        payload["new_building_ids"] = added
    if retired:
        assert set(retired) <= {item["id"] for item in removals}
        payload["absorbed_ids"] = retired
    write_json(descriptor, payload, compact=True)
    if args.stage is None:
        config[descriptor_key] = {
            "url": f"{package}/site.json",
            "sha256": digest(descriptor),
        }
        write_json(config_path, config)
    report = {
        "records": records,
        "routes_checked": count,
        "route_clearance_m": round(clearance, 4),
        "removed_triangles": sum(
            stop - start for start, stop in (p["triangles"] for p in removals)
        ),
        "batch_removals": removals,
        "building_triangles": {id: len(mesh.faces) for id, mesh in meshes.items()},
        "site_glb_sha256": payload["sha256"],
        "descriptor_sha256": digest(descriptor),
    }
    if splits:
        report["split_buildings"] = splits
    if added:
        report["new_building_ids"] = added
    if retired:
        report["absorbed_ids"] = retired
    write_json(args.audit, report)
    print(report["building_triangles"], count, clearance)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    export_review(
        parser.parse_args(), PACKAGE, GROUND, "fairmount_kincaid_exterior_site", build
    )


if __name__ == "__main__":
    main()
