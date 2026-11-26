# SPDX-License-Identifier: Apache-2.0
"""Restore the three separately addressed buildings behind Hilyard Street."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import union_all
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-hilyard-1515-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)

ROOT, SCENE = shared.ROOT, shared.SCENE
base, geometry, chapter, science = (
    shared.base,
    shared.geometry,
    shared.chapter,
    shared.science,
)
garden, approaches = shared.garden, shared.approaches
PACKAGE = "hilyard-central-exterior-review"
GROUND = "hilyard-central-approaches"
STUCCO = (171, 161, 143)
GRAY = (157, 153, 140)
BRICK = (136, 81, 67)
MORTAR = (162, 125, 103)
CONCRETE = (161, 156, 141)
FRAME = (73, 77, 71)
GLASS = (75, 97, 98)
ROOF = (93, 102, 103)
EAVE = (75, 82, 78)
GREEN = (88, 115, 110)
GREEN_TRIM = (102, 131, 124)

COLORS = {
    "three-storey": GRAY,
    "brick": BRICK,
    "stucco": STUCCO,
}


def panel(add, u, z, width=1.10, rise=1.08):
    chapter.prior.window(add, u, width, z, z + rise, FRAME, GLASS, ribs=1)


def pitched_stair(
    parts,
    plan,
    start,
    end,
    clearance,
    width,
    lower,
    upper,
    *,
    tread=GREEN,
    trim=GREEN_TRIM,
):
    count = max(1, round((upper - lower) / 0.184))
    sloping = np.linspace((start, lower), (end, upper), count + 1)
    for (u0, _), (u1, z1) in zip(sloping[:-1], sloping[1:], strict=True):
        corners = [
            plan(u, d)
            for u, d in (
                (u0, clearance),
                (u1, clearance),
                (u1, clearance + width),
                (u0, clearance + width),
            )
        ]
        p = orient(Polygon(corners))
        base.flat(parts, p, z1 - 0.075, z1, tread)
    for distance in (clearance + 0.035, clearance + width - 0.035):
        shared.brace(
            parts,
            plan,
            (start, distance, lower + 0.91),
            (end, distance, upper + 0.91),
            0.051,
            trim,
        )
        for station, z in sloping[::3]:
            shared.brace(
                parts,
                plan,
                (station, distance, z),
                (station, distance, z + 0.9),
                0.036,
                tread,
            )
        shared.brace(
            parts,
            plan,
            (start, distance, lower - 0.035),
            (end, distance, upper - 0.035),
            0.13,
            tread,
        )


def gallery(parts, add, plan, length, field, level_count):
    ground = geometry.sample_ground(field, *plan(length * 0.60, 0.7))
    deck_width = 1.32 if level_count == 2 else 1.11
    left, right = 0.36, length - 0.35
    start, stop = (length - 8.18, length - 0.84) if level_count == 2 else (1.15, 7.58)
    feet = []
    for level in range(level_count):
        deck = ground + 2.63 * (level + 1)
        approaches.gallery(add, left, right, deck_width, deck, GREEN)
        for u in np.arange(left + 0.38, right - 0.35, 0.65):
            add(
                u - 0.026,
                u + 0.026,
                deck_width - 0.04,
                deck_width,
                deck + 0.12,
                deck + 0.89,
                GREEN_TRIM,
            )
        add(
            left,
            right,
            deck_width - 0.043,
            deck_width + 0.015,
            deck + 0.44,
            deck + 0.487,
            GREEN_TRIM,
        )
        run_start, run_stop = (start, stop) if level == 0 else (stop, start)
        pitched_stair(
            parts,
            plan,
            run_start,
            run_stop,
            deck_width + 0.06,
            0.92,
            ground + 2.63 * level,
            deck,
        )
        landing_left, landing_right = sorted(
            (run_stop - 0.02, run_stop + (0.80 if level == 0 else -0.78))
        )
        add(
            landing_left,
            landing_right,
            deck_width - 0.03,
            deck_width + 0.99,
            deck - 0.15,
            deck,
            GREEN,
        )
    for u in (1.7, length * 0.46, length * 0.74, length - 2.0):
        q = plan(u, deck_width - 0.12)
        bearing = geometry.sample_ground(field, *q)
        feet.append(
            approaches.supported_post(
                parts, q, bearing - 0.045, ground + 2.63 * level_count, GREEN, 0.077
            )
        )
    return feet


def walls(parts, edges, row, field, height, door_edge, door_u, threshold):
    supports = []
    style = row["style"]
    gallery_spec = row["gallery"]
    for edge in edges:
        length, add, outward, plan, _, _ = chapter.setup_face(parts, *edge)
        if length < 1.15:
            continue
        grade = geometry.sample_ground(field, *plan(length / 2, 0))
        top = min(height(plan(u, 0)) for u in (0.06, length / 2, length - 0.06))
        add(0.02, length - 0.02, 0.002, 0.036, grade - 0.09, grade + 0.64, CONCRETE)
        if style == "brick":
            for sill in np.arange(grade + 0.66, top - 0.075, 0.102):
                add(0.009, length - 0.009, 0.01, 0.027, sill, sill + 0.011, MORTAR)
        if style == "three-storey" and abs(outward[0]) > 0.96:
            add(0, length, 0.005, 0.027, grade + 2.65, grade + 4.86, (140, 138, 130))
            add(0, length, 0.002, 0.039, grade + 4.86, grade + 4.93, CONCRETE)
        if style != "brick" and abs(outward[0]) > 0.96:
            # The observed alley end walls read as plain end elevations.
            continue
        end_inset = 1.68 if length > 7 else 1.03
        positions = np.linspace(
            end_inset, length - end_inset, max(2, round(length / 3.4))
        )
        has_gallery = gallery_spec and outward @ gallery_spec["outward"] > 0.97
        for i, u in enumerate(positions):
            levels = (0.90, 3.35, 5.98) if style == "three-storey" else (0.98, 3.39)
            for idx, z in enumerate(levels):
                if idx and has_gallery and i % 2 == 0:
                    continue
                if not idx and edge == door_edge and abs(u - door_u) < 1.18:
                    continue
                sill = grade + z
                if sill + 1.05 <= top - 0.10:
                    panel(add, u, sill)
        if has_gallery:
            supports.extend(
                gallery(parts, add, plan, length, field, gallery_spec["level_count"])
            )
            for z in range(gallery_spec["level_count"]):
                deck = grade + 2.63 * (z + 1)
                for u in positions[::2]:
                    if deck + 2.20 < top:
                        garden.neighbor.door(add, u, deck, GREEN)
        if edge == door_edge and style == "three-storey":
            add(
                door_u - 0.38,
                door_u + 0.38,
                0.032,
                0.082,
                threshold + 2.29,
                threshold + 2.45,
                GREEN_TRIM,
            )
    return supports


def build(row, field, paving):
    outline = orient(Polygon(row["outline_enu_m"]))
    wall = orient(outline.buffer(-0.17, join_style="mitre"))
    eaves = orient(outline.buffer(0.22, join_style="mitre"))
    floor, _ = science.earlier.fit_base(field, wall)
    palette = row | {
        "wall_color": COLORS[row["style"]],
        "trim_color": EAVE,
        "roof_color": ROOF,
        "door_color": GREEN,
    }
    parts = []
    height = garden.roof_sections(parts, eaves, wall, floor, palette, grid=0.0001)
    edges = [tuple(map(tuple, edge)) for edge in garden.shared.face_edges(wall)]
    gate, face, u = approaches.entry_stair(parts, paving, edges, field, palette, None)
    gate["estimated"] = True
    supports = walls(parts, edges, row, field, height, face, u, gate["threshold_z_m"])
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000015))
    record = {
        "id": row["id"],
        "name": row["name"],
        "street_address": row["street_address"],
        "footprint_enu_m": base.ring(wall),
        "area_m2": round(wall.area, 3),
        "support_collision_enu_m": [base.ring(p) for p in supports],
        "entrances": [gate],
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
    }
    return science.ordered_mesh(mesh), record, wall, supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(
        (ROOT / "data/metadata/hilyard-central-exterior-review.json").read_bytes()
    )
    manifest_path = SCENE / "manifest.json"
    config_path = SCENE / "presentation.json"
    manifest, config = (
        json.loads(path.read_bytes()) for path in (manifest_path, config_path)
    )
    heightfield = SCENE / manifest["heightfield_url"]
    digest = garden.tools.digest
    assert digest(manifest_path) == spec["source_manifest_sha256"]
    assert digest(heightfield) == spec["source_heightfield_sha256"]
    field = json.loads(heightfield.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, plans, supports, gates, paving = {}, [], [], [], [], []
    for row in spec["models"]:
        mesh, record, wall, feet = build(row, field, paving)
        meshes[row["id"]] = mesh
        records.append(record)
        plans.append(wall)
        supports.extend(feet)
        gates.extend(record["entrances"])
    neighbor = json.loads(
        (SCENE / config["hilyard_apartments_exterior_site"]["url"]).read_bytes()
    )
    existing = Polygon(neighbor["buildings"][0]["footprint_enu_m"])
    assert min(p.distance(existing) for p in plans + supports) > 0.62
    assert (
        min(a.distance(b) for i, a in enumerate(plans) for b in plans[i + 1 :]) > 0.62
    )
    prior = union_all(
        [
            Polygon(row["footprint_enu_m"]).buffer(0)
            for row in manifest["buildings"]
            if row["id"] in meshes
        ]
    )
    count, clearance = chapter.prior.nearby.shared.graduate.shared.check_routes(
        plans, supports, gates, prior, manifest, graph, config, set(meshes)
    )
    appearances = json.loads(
        (ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = garden.shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, appearances
    )
    stage = args.stage or SCENE / PACKAGE
    stage.mkdir(exist_ok=True, parents=True)
    model, descriptor = stage / "site.glb", stage / "site.json"
    paving = science.ordered_mesh(trimesh.util.concatenate(paving))
    garden.site.memorial.gerlinger.export(
        model, meshes, paving, GROUND, "hilyard-central-paving"
    )
    package = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": digest(model),
        "buildings": records,
        "split_buildings": spec["source_split"],
        "batch_removals": removals,
    }
    descriptor.write_text(
        json.dumps(package, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if args.stage is None:
        config["hilyard_central_exterior_site"] = {
            "url": f"{PACKAGE}/site.json",
            "sha256": digest(descriptor),
        }
        config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    audit = {
        "buildings": records,
        "batch_removals": removals,
        "route_edges": count,
        "nearest_route_m": round(clearance, 4),
        "triangles": {key: len(v.faces) for key, v in meshes.items()},
        "glb_sha256": digest(model),
        "descriptor_sha256": digest(descriptor),
    }
    args.audit.write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(audit["triangles"], audit["nearest_route_m"])


if __name__ == "__main__":
    main()
