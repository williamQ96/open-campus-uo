# SPDX-License-Identifier: Apache-2.0
"""Register the as-built twelve-level Rive Eugene exterior."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-western-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
western = module_from_spec(loader)
loader.loader.exec_module(western)
ROOT, SCENE = western.ROOT, western.SCENE
base, garden, terrain, design = (
    western.base,
    western.garden,
    western.geometry,
    western.prior,
)
DIRECTORY = "rive-eugene-exterior-review"
GROUND = "rive-eugene-approaches"
FOUNDATION = (158, 158, 151)
INK = (72, 80, 92)
SLATE = (96, 106, 120)
LIGHT = (170, 177, 182)
GLOSS = (130, 145, 154)
FRAME = (65, 77, 91)
GLASS = (68, 101, 116)
COPPER = (166, 103, 65)
COPPER_SHADE = (121, 74, 51)
ROOF = (165, 165, 155)
TILE = (180, 172, 147)
POOL = (81, 151, 159)
PLANTS = (116, 133, 102)


def wall_faces(parts, plan):
    for a, b in garden.shared.face_edges(plan):
        width, add, normal, coordinate, *_ = design.chapter.setup_face(parts, a, b)
        yield LineString((a, b)), width, add, normal, coordinate


def plane(parts, outline, floor, top, color, cap=ROOF):
    for piece in terrain.sections(outline):
        parts.append(terrain.shell(piece, floor, lambda e, n: top, color, cap))


def curtain(add, start, end, low, high, step=1.04):
    add(start, end, 0.008, 0.042, low, high, FRAME)
    for left in np.arange(start + 0.075, end - 0.14, step):
        right = min(left + step - 0.105, end - 0.06)
        if right - left > 0.11:
            add(left, right, 0.043, 0.072, low + 0.11, high - 0.11, GLASS)
    add(start, end, 0.075, 0.102, low + 1.04, low + 1.083, FRAME)


def podium_details(parts, occupied, field, door, threshold, height):
    for line, width, add, normal, coordinate in wall_faces(parts, occupied):
        if width < 1.58:
            continue
        x, n = coordinate(width / 2, 0)
        grade = terrain.sample_ground(field, x, n)
        main_door = line.distance(door) < 0.025 and normal[0] < -0.92
        west_shop = normal[0] < -0.92 and x < -887
        north_shop = normal[1] > 0.91 and n > 466
        east = normal[0] > 0.92 and x > -844
        add(0.015, width - 0.015, 0.008, 0.079, height - 0.56, height - 0.035, INK)
        if main_door:
            u = line.project(door)
            curtain(add, 0.12, width - 0.12, threshold + 0.045, threshold + 4.1)
            add(
                u - 1.03,
                u + 1.03,
                0.076,
                0.164,
                threshold + 0.026,
                threshold + 2.74,
                FRAME,
            )
            for offset in (-0.47, 0.47):
                v = u + offset
                add(
                    v - 0.405,
                    v + 0.405,
                    0.165,
                    0.179,
                    threshold + 0.14,
                    threshold + 2.62,
                    GLASS,
                )
                add(
                    v + 0.27,
                    v + 0.32,
                    0.179,
                    0.236,
                    threshold + 0.93,
                    threshold + 1.38,
                    COPPER,
                )
        elif west_shop or north_shop:
            for position in np.arange(0.22, width - 1.8, 6.5):
                end = min(position + (5.4 if west_shop else 4.12), width - 0.14)
                if end - position > 1.07:
                    if west_shop or coordinate(position, 0)[0] < -872.3:
                        curtain(
                            add,
                            position,
                            end,
                            grade + 0.32,
                            min(grade + 3.47, height - 0.61),
                        )
                    else:
                        for u in np.arange(position, end - 0.08, 0.32):
                            add(
                                u,
                                u + 0.045,
                                0.003,
                                0.026,
                                grade + 0.12,
                                height - 0.62,
                                GLOSS,
                            )
        elif east and width > 8.0:
            u = width * 0.47
            add(u - 2.49, u + 2.49, 0.017, 0.173, grade + 0.04, grade + 2.93, FRAME)
            for z in np.arange(grade + 0.23, grade + 2.75, 0.21):
                add(u - 2.37, u + 2.37, 0.173, 0.192, z, z + 0.029, SLATE)


def cloud_color(row, bay, n, e):
    drift = 1.28 * np.sin((e + 897) / 11.7) + 0.87 * np.cos((n - 442) / 4.9)
    if 2.4 + drift < row < 9.2 + drift and (row + bay // 4) % 4 != 0:
        return LIGHT if (bay + row) % 5 else GLOSS
    return SLATE if (bay + row) % 6 != 0 else INK


def facade_panel(parts, plan, left, right, offset, bottom, top, color):
    vertices = []
    for u, h in ((left, bottom), (right, bottom), (right, top), (left, top)):
        e, n = plan(u, offset)
        vertices.append((e, h, -n))
    panel = trimesh.Trimesh(vertices, ((0, 1, 2), (0, 2, 3)), process=False)
    panel.visual.vertex_colors = [*color, 255]
    parts.append(panel)


def metal_facades(parts, outline, low, high, datum):
    for _, width, add, normal, plan in wall_faces(parts, outline):
        if width < 1.26:
            continue
        bays = max(1, round(width / 2.22))
        for row, level in enumerate(np.arange(datum, high - 1.58, 3.44)):
            top = min(level + 3.39, high - 0.10)
            bottom = max(level + 0.06, low + 0.02)
            if top - bottom < 0.4:
                continue
            for bay in range(bays):
                left, right = (v * width / bays for v in (bay, bay + 1))
                center = (left + right) / 2
                e, n = plan(center, 0)
                color = cloud_color(row, bay, n, e)
                copper_band = (normal[1] > 0.9 and -890.3 < e < -887.9) or (
                    normal[0] < -0.91 and 464.0 < n < 466.9
                )
                if copper_band:
                    color = COPPER
                facade_panel(
                    parts, plan, left + 0.021, right - 0.021, 0.037, bottom, top, color
                )
                for seam in np.arange(left + 0.24, right - 0.12, 0.41):
                    facade_panel(
                        parts,
                        plan,
                        seam,
                        seam + 0.025,
                        0.055,
                        bottom,
                        top,
                        COPPER_SHADE if copper_band else SLATE,
                    )
                if top - bottom > 2.0 and right - left > 0.83:
                    sill = bottom + 0.86
                    sash = min(1.31, (right - left) * 0.65)
                    half = sash / 2
                    facade_panel(
                        parts,
                        plan,
                        center - half,
                        center + half,
                        0.114,
                        sill,
                        sill + 1.49,
                        FRAME,
                    )
                    facade_panel(
                        parts,
                        plan,
                        center - half + 0.067,
                        center + half - 0.067,
                        0.133,
                        sill + 0.074,
                        sill + 1.416,
                        GLASS,
                    )
                    facade_panel(
                        parts,
                        plan,
                        center - half + 0.053,
                        center + half - 0.053,
                        0.152,
                        sill + 0.52,
                        sill + 0.57,
                        FRAME,
                    )
        add(0.018, width - 0.018, 0.018, 0.145, high - 0.42, high + 0.29, INK)


def terrace_edges(parts, outline, z, roof_color, planted=False):
    for _, width, add, _, plan in wall_faces(parts, outline):
        if width < 1.38:
            continue
        add(0.02, width - 0.02, 0.014, 0.088, z, z + 0.96, roof_color)
        add(0.02, width - 0.02, 0.088, 0.147, z + 0.90, z + 1.02, FRAME)
        if planted and width > 11:
            for u in np.arange(2.0, width - 2.0, 3.6):
                e, n = plan(u, -0.5)
                base.flat(
                    parts,
                    box(e - 0.48, n - 0.45, e + 0.48, n + 0.45),
                    z,
                    z + 0.38,
                    PLANTS,
                )


def decks(parts, spec, caps):
    upper = spec["roof_frame_y_m"]["main_roof"]
    low = spec["roof_frame_y_m"]["ninth_terrace"]
    pool = box(*spec["roof_pool_enu_m"])
    assert caps["main"].buffer(-0.55).contains(pool)
    edge = pool.buffer(1.1, join_style="mitre").difference(pool)
    plane(parts, edge, upper, upper + 0.47, TILE, TILE)
    plane(parts, pool, upper + 0.04, upper + 0.22, POOL, POOL)
    for row in np.arange(457.62, 462.15, 0.72):
        plane(
            parts,
            box(-851.80, row, -849.52, row + 0.36),
            upper + 0.012,
            upper + 0.27,
            TILE,
            TILE,
        )
    planted = caps["ninth"].buffer(-0.56)
    terrace_edges(parts, planted, low, GLASS, planted=True)
    for west, south in ((-891.0, 425.8), (-884.3, 431.4), (-872.3, 429.6)):
        block = box(west, south, west + 1.7, south + 0.73)
        if planted.covers(block):
            plane(parts, block, low, low + 0.48, FOUNDATION, TILE)
    for x, n in ((-892.6, 459.21), (-863.65, 465.95), (-845.78, 466.18)):
        footprint = box(x, n, x + 2.17, n + 1.12)
        if caps["main"].contains(footprint):
            plane(parts, footprint, upper, upper + 0.58, ROOF, SLATE)


def build(spec, field):
    outline = orient(Polygon(spec["registered_footprint_enu_m"]))
    podium = orient(outline.buffer(-0.11, join_style="mitre"))
    occupied = orient(podium.difference(box(*spec["north_west_recess_enu_m"])))
    floor, _ = garden.science.earlier.fit_base(field, outline)
    rows = spec["roof_frame_y_m"]
    ninth = podium.intersection(box(*spec["nine_terrace_enu_m"]))
    south = podium.difference(ninth).intersection(box(*spec["south_roof_enu_m"]))
    main = podium.difference(union_all((ninth, south, box(*spec["upper_court_enu_m"]))))
    assert all(p.is_valid and p.area > 55 for p in (main, south, ninth))
    assert all(p.geom_type == "Polygon" for p in (main, south, ninth))
    parts, paving = [], []
    plane(parts, occupied, floor, rows["podium_top"], FOUNDATION)
    plane(parts, podium, rows["podium_top"] - 0.48, rows["podium_top"], SLATE)
    for shape, key in (
        (main, "main_roof"),
        (south, "south_roof"),
        (ninth, "ninth_terrace"),
    ):
        height = rows[key]
        plane(parts, shape, rows["podium_top"], height, SLATE)
        # Match the facade clothing to the separate roof plates.
        metal_facades(parts, orient(shape), rows["podium_top"], height, 2.54)
    decks(parts, spec, {"main": main, "ninth": ninth})
    e, n = spec["door_enu_m"]
    door = Point(e, n)
    assert occupied.boundary.distance(door) < 0.005
    threshold = terrain.sample_ground(field, e, n) + 0.06
    podium_details(parts, occupied, field, door, threshold, rows["podium_top"])
    western.terrace(paving, field, box(e - 4.32, n - 1.73, e + 0.01, n + 1.73))
    western.terrace(paving, field, box(-840.25, 446.0, -835.95, 452.2))
    entry = dict(
        gate="rive-hilyard-entry",
        position_enu_m=[e, n],
        outward_degrees=270,
        threshold_z_m=round(threshold, 4),
        width_m=2.0,
        approach_distance_m=3.8,
        estimated=True,
        snap_to_facade=False,
    )
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.000022))
    mesh = garden.science.ordered_mesh(mesh)
    record = {
        **{k: spec[k] for k in ("id", "name", "street_address")},
        "footprint_enu_m": base.ring(outline),
        "ground_footprints_enu_m": [base.ring(occupied)],
        "area_m2": round(outline.area, 3),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "entrances": [entry],
    }
    return mesh, paving, record, occupied


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    meta = ROOT / "data/metadata"
    spec = json.loads((meta / f"{DIRECTORY}.json").read_bytes())
    config_path, manifest_path = (
        SCENE / path for path in ("presentation.json", "manifest.json")
    )
    config, manifest = (
        json.loads(p.read_bytes()) for p in (config_path, manifest_path)
    )
    field_path = SCENE / manifest["heightfield_url"]
    digest = garden.tools.digest
    assert digest(manifest_path) == spec["source_manifest_sha256"]
    assert digest(field_path) == spec["source_heightfield_sha256"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    mesh, paving, record, walls = build(spec, field)
    id = spec["id"]
    original = Polygon(
        next(r["footprint_enu_m"] for r in manifest["buildings"] if r["id"] == id)
    )
    check_routes = design.chapter.prior.nearby.shared.graduate.shared.check_routes
    count, clearance = check_routes(
        [walls], [], record["entrances"], original, manifest, graph, config, {id}
    )
    source_audit = json.loads((meta / "campus-expansion-audit.json").read_bytes())
    removals = garden.shared.frohnmayer.source_removals(
        {"absorbed_batches": [{"id": id, "target": spec["source_batch"]}]},
        config,
        source_audit,
    )
    output = args.stage or SCENE / DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    model, descriptor = output / "site.glb", output / "site.json"
    ground = garden.science.ordered_mesh(trimesh.util.concatenate(paving))
    garden.site.memorial.gerlinger.export(
        model, {id: mesh}, ground, GROUND, "rive-eugene-entry-paving"
    )
    result = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{DIRECTORY}/site.glb",
        "sha256": digest(model),
        "buildings": [record],
        "batch_removals": removals,
    }
    design.prior.write_json(descriptor, result, compact=True)
    if args.stage is None:
        config["rive_eugene_exterior_site"] = {
            "url": f"{DIRECTORY}/site.json",
            "sha256": digest(descriptor),
        }
        design.prior.write_json(config_path, config)
    facts = {
        "record": record,
        "triangles": len(mesh.faces),
        "route_edges": count,
        "nearest_clearance_m": round(clearance, 4),
        "batch_removals": removals,
        "glb_sha256": digest(model),
        "site_sha256": digest(descriptor),
    }
    design.prior.write_json(args.audit, facts)
    print(facts["triangles"], count, clearance, facts["glb_sha256"])


if __name__ == "__main__":
    main()
