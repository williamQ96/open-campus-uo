# SPDX-License-Identifier: Apache-2.0
"""Build the registered Cedar and Yasui exteriors and shared courtyards."""

import argparse
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-bean-unthank-site-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)
site, tools, geometry = shared.site, shared.tools, shared.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/cedar-yasui-site-review.json"
DIRECTORY = "cedar-yasui-review"
GROUND = "cedar-yasui-courtyards"
ROOF = (191, 194, 186)
COPING = (148, 155, 153)
BRICK = (144, 99, 83)
BRICK_LIGHT = (155, 112, 92)
BASE = (128, 93, 76)
GLASS = (74, 112, 126)
GLASS_LIGHT = (99, 137, 153)
STEEL = (72, 82, 82)
FINISH = (174, 181, 178)
TIMBER = (161, 126, 79)
GOLD = (221, 187, 49)
GREEN = (128, 152, 80)
GRASS = (144, 161, 108)
PAVING = (174, 166, 151)
METAL = ((184, 191, 190), (152, 164, 166), (201, 207, 199), (121, 138, 142))


def ring(polygon):
    return list(orient(polygon).exterior.coords)[:-1]


def roof(parts, area, ground, top, wall):
    site.flat(parts, area, ground, top, wall, ROOF)
    cap = shared.clean(area.difference(area.buffer(-0.22, join_style="mitre")))
    site.flat(parts, cap, top - 0.019, top + 0.27, wall, COPING)


def shell(parts, model, plan, portal, floor):
    zones, rest = [], plan
    for i, data in enumerate(model["wings"]):
        area = (
            rest
            if i == len(model["wings"]) - 1
            else rest.intersection(box(*data["bounds"]))
        )
        area = shared.clean(area)
        assert area.area > 55, data["name"]
        rest = shared.clean(rest.difference(area))
        solid = shared.clean(area.difference(portal))
        roof(parts, solid, floor, data["top"], BRICK)
        zones.append((area, data))
    for bounds in model["service_roof_blocks"]:
        block = box(*bounds).intersection(plan)
        point = block.centroid
        zone = next(data for area, data in zones if area.distance(point) < 0.004)
        z = zone["top"]
        site.flat(parts, block, z + 0.018, z + 0.20, COPING, (183, 188, 182))
        w, s, e, n = block.bounds
        along_east = e - w > n - s
        length = e - w if along_east else n - s
        for offset in np.arange(1.72, length - 1.25, 6.73):
            shape = (
                box(w + offset, s + 0.52, w + offset + 1.17, min(n - 0.25, s + 2.11))
                if along_east
                else box(
                    w + 0.52, s + offset, min(e - 0.25, w + 2.11), s + offset + 1.17
                )
            ).intersection(block)
            site.flat(parts, shape, z + 0.18, z + 0.72, COPING, FINISH)
    return zones


def facade(parts, a, b, section, base, grade, gate, cedar, court=False, above=None):
    edge = LineString((a, b))
    length, add = tools.face(parts, a, b)
    if length < 0.36:
        return
    top, levels = section["top"], section["levels"]
    massing = section["style"]
    backing = grade + 0.28
    ground_head = min(top - 0.4, base + 3.82)
    room = (top - ground_head) / (levels - 1)
    metal = (
        massing in ("metal", "south")
        or (massing == "court" and b[0] > a[0])
        or (massing == "brick" and court)
    )
    if above is None:
        add(0.018, length - 0.018, 0.009, 0.086, backing - 0.32, backing + 0.25, BASE)
        if length > 0.92 and ((cedar and metal) or gate is not None):
            shared.floor_glass(add, length, grade, ground_head - 0.22, gate, edge)
    center = edge.project(Point(gate["position_enu_m"])) if gate else None
    focus = gate is not None and gate["gate"] in (
        "cedar-agate",
        "cedar-north-court",
        "cedar-south-court",
        "yasui-north-court",
    )
    if focus:
        low = gate["threshold_z_m"]
        w = min(5.10, length - 0.18)
        add(center - w / 2, center + w / 2, 0.074, 0.235, low + 2.62, low + 2.83, GOLD)
        for x in (center - w / 2, center + w / 2):
            add(x - 0.083, x + 0.083, 0.083, 0.242, low + 0.035, low + 2.83, GOLD)
        add(
            center - w * 0.56,
            center + w * 0.56,
            0.032,
            0.74,
            low + 2.86,
            low + 3.09,
            STEEL,
        )

    count = max(1, round(length / (2.41 if metal else 2.71)))
    step = length / count
    if step < 1.19:
        return
    # Repeated vertical metal panels are grouped into bays, with an occasional brick break.
    for i in range(count):
        x = (i + 0.5) * step
        atrium = focus and abs(x - center) < 2.9
        clad = metal and (i // 7) % 4 != 3 and not atrium
        left, right = x - step * 0.47, x + step * 0.47
        panel_bottom = ground_head if above is None else max(ground_head, above + 0.18)
        if clad and panel_bottom < top - 0.34:
            for j in range(4):
                p = left + (right - left) * j / 4
                add(
                    p,
                    p + (right - left) * 0.239,
                    0.009,
                    0.095 + (j % 2) * 0.026,
                    panel_bottom,
                    top - 0.13,
                    METAL[(i + j * 2) % 4],
                )
        elif not atrium and panel_bottom < top * 0.70:
            add(left, right, 0.006, 0.059, panel_bottom, top - 0.16, BRICK_LIGHT)
        for level in range(levels - 1):
            z = ground_head + level * room
            if above is not None and z + 0.44 < above + 0.15:
                continue
            width = step * (0.93 if atrium else 0.56 if clad else 0.66)
            low = z + (0.14 if atrium else 0.64)
            high = min(z + room - 0.20, low + (2.62 if atrium else 1.78))
            x0, x1 = x - width / 2, x + width / 2
            offset = 0.115 if clad else 0.074
            reveal = (
                GOLD
                if massing == "south" and i % 5 == 1
                else GREEN if massing == "south" and i % 5 == 3 else STEEL
            )
            add(
                x0 - 0.037,
                x1 + 0.037,
                offset,
                offset + 0.066,
                low - 0.052,
                high + 0.056,
                reveal,
            )
            add(
                x0 + 0.026,
                x1 - 0.024,
                offset + 0.068,
                offset + 0.098,
                low + 0.035,
                high - 0.035,
                GLASS_LIGHT if (i + level) % 4 == 0 else GLASS,
            )
            if atrium or width > 1.5:
                add(
                    x - 0.024,
                    x + 0.024,
                    offset + 0.097,
                    offset + 0.135,
                    low,
                    high,
                    STEEL,
                )
            add(
                x0 - 0.045,
                x1 + 0.047,
                offset + 0.014,
                offset + 0.16,
                low - 0.109,
                low - 0.055,
                FINISH,
            )
        if (
            not (cedar and metal)
            and above is None
            and gate is None
            and i % 3 != 1
            and length > 1.45
        ):
            inset = 0.15 if cedar else step * 0.23
            shared.glazing(
                add, left + inset, right - inset, backing + 0.57, ground_head - 0.45, 1
            )
    add(0.009, length - 0.009, 0.016, 0.096, top - 0.22, top - 0.078, COPING)


def building_elevations(parts, ground, zones, gates, base, field, cedar):
    for area in geometry.sections(ground):
        for coords in (orient(area).exterior,):
            for a, b in zip(list(coords.coords), list(coords.coords)[1:]):
                line = LineString((a, b))
                if line.length < 0.35:
                    continue
                for zone, section in zones:
                    for run in shapely.get_parts(line.intersection(zone.buffer(0.008))):
                        if run.geom_type != "LineString" or run.length < 0.35:
                            continue
                        a0, b0 = sorted(
                            [run.coords[0], run.coords[-1]],
                            key=lambda pt: line.project(Point(pt)),
                        )
                        p = run.interpolate(0.5, normalized=True)
                        grade = geometry.sample_ground(field, p.x, p.y)
                        gate = next(
                            (
                                g
                                for g in gates
                                if run.distance(Point(g["position_enu_m"])) < 0.012
                            ),
                            None,
                        )
                        is_court = (cedar and p.x < 48 and p.y > -194) or (
                            not cedar and p.x > -19
                        )
                        facade(
                            parts,
                            a0,
                            b0,
                            section,
                            base,
                            grade,
                            gate,
                            cedar,
                            court=is_court,
                        )
    for area, section in zones:
        for body in geometry.sections(area):
            outline = orient(body).exterior
            for a, b in zip(list(outline.coords), list(outline.coords)[1:]):
                edge = LineString((a, b))
                center = np.asarray(edge.interpolate(0.5, normalized=True).coords[0])
                if edge.length < 1.8:
                    continue
                u = (np.asarray(b) - a) / edge.length
                point = Point(center + 0.024 * np.array((u[1], -u[0])))
                neighbor = next(
                    (data["top"] for region, data in zones if region.covers(point)),
                    None,
                )
                if neighbor is not None and neighbor < section["top"] - 0.6:
                    z = geometry.sample_ground(field, *center)
                    facade(parts, a, b, section, base, z, None, cedar, above=neighbor)


def bridge(parts, region, base, top):
    assert region.geom_type == "Polygon"
    site.flat(parts, region, base, top, STEEL, ROOF)
    site.flat(parts, region, base - 0.19, base, TIMBER)
    w, s, e, n = region.bounds
    assert e - w > 6.7 and n - s > 5.8
    for a, b in zip(
        list(orient(region).exterior.coords), list(orient(region).exterior.coords)[1:]
    ):
        if abs(a[1] - b[1]) < 4.9:
            continue
        length, add = tools.face(parts, a, b)
        head = base - 0.08
        add(0.03, length - 0.03, 0.04, 0.31, head - 0.22, head + 0.05, GOLD)
        for x in (0.085, length - 0.085):
            add(x - 0.074, x + 0.074, 0.012, 0.29, head + 0.015, top - 0.15, FINISH)
            add(x - 0.062, x + 0.062, 0.041, 0.235, head - 4.20, head - 0.22, GOLD)
        for z in np.linspace(base + 0.41, top - 2.71, 4):
            shared.glazing(add, 0.18, length - 0.18, z, z + 2.36, 5, glass=GLASS_LIGHT)
            add(0.025, length - 0.025, 0.073, 0.234, z - 0.18, z - 0.012, FINISH)
    site.flat(
        parts, region.difference(region.buffer(-0.16)), top - 0.04, top + 0.18, COPING
    )


def pavilion(parts, model, field):
    shade = Polygon(model["pavilion_roof"])
    body = orient(Polygon(model["pavilion_body"]))
    assert body.difference(shade.buffer(0.10)).area < 0.15
    base = geometry.sample_ground(field, *body.centroid.coords[0])
    top = base + 3.34
    site.flat(parts, body, base - 0.28, top, STEEL)
    site.flat(parts, shade, top - 0.023, top + 0.15, TIMBER)
    site.flat(parts, shade, top + 0.15, top + 0.36, STEEL, ROOF)
    for a, b in zip(list(body.exterior.coords), list(body.exterior.coords)[1:]):
        length, add = tools.face(parts, a, b)
        if length > 1.55:
            shared.glazing(
                add,
                0.22,
                length - 0.22,
                base + 0.18,
                top - 0.27,
                max(2, round(length / 1.39)),
            )
            add(0.13, length - 0.13, 0.086, 0.188, base + 0.02, base + 0.18, COPING)
    return body


def ground_site(parts, spec, plans, field, sites):
    collision = shapely.union_all(sites)
    walk = shapely.union_all(
        [
            LineString(points).buffer(width / 2, quad_segs=5)
            for width, points in spec["paths"]
        ]
        + plans
    )
    entries = lambda area, color: [
        dict(outline=ring(p), rgb=color) for p in geometry.sections(area)
    ]
    for i, area in enumerate(spec["lawns"]):
        field_area = Polygon(area)
        if not field_area.is_valid:
            field_area = field_area.buffer(0)
        turf = shared.clean(field_area.difference(walk))
        if turf.area > 0.01:
            parts.append(
                tools.approaches(
                    entries(turf, GRASS if i < 2 else (133, 151, 98)), field, collision
                )
            )
    parts.append(tools.approaches(entries(walk, PAVING), field, collision))
    return walk, collision


def registered_trees(spec, walk, collision, field):
    trees, records = [], []
    twig = (116, 97, 71)
    for plant in spec["trees"]:
        e, n = plant["point"]
        stem = Point(e, n)
        if walk.distance(stem) < 0.56 or collision.distance(stem) < 0.63:
            continue
        height, spread = plant["height"], plant["spread"]
        low = geometry.sample_ground(field, e, n)
        trunk = trimesh.creation.cylinder(
            radius=0.065 + height * 0.006, height=height * 0.71, sections=7
        )
        trunk.apply_translation((e, low + height * 0.354, -n))
        trunk.visual.vertex_colors = [*twig, 255]
        trees.append(trunk)
        deciduous = "Hemlock" not in (plant["species"] or "")
        for i in range(5):
            angle = 2 * np.pi * i / 5 + plant["number"] * 0.09
            crown = trimesh.creation.icosphere(subdivisions=1)
            pos = crown.vertices.copy()
            taper = 1 if deciduous else 0.78
            radius = spread * (0.257 + i % 2 * 0.037)
            pos *= np.array([radius, radius * 1.57 * taper, radius])
            pos += [
                e + np.cos(angle) * spread * 0.18,
                low + height * (0.69 + 0.051 * i),
                -n + np.sin(angle) * spread * 0.18,
            ]
            crown.vertices = pos
            crown.visual.vertex_colors = [
                *(
                    (116, 144, 84),
                    (124, 151, 92),
                    (105, 135, 79),
                    (119, 143, 82),
                    (111, 137, 79),
                )[i],
                255,
            ]
            trees.append(crown)
        records.append(plant["number"])
    assert trees
    return trimesh.util.concatenate(trees), records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    path = SCENE / "presentation.json"
    cfg = json.loads(path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    staged, records, paths, lands, solids, entries, zone_report = (
        {},
        [],
        [],
        [],
        [],
        [],
        {},
    )
    for model in spec["models"]:
        key = model["id"]
        walls = orient(Polygon(model["footprint_enu_m"]))
        passage = (
            walls.intersection(
                box(-36, model["portal_band"][0], -16, model["portal_band"][1])
            )
            if "portal_band" in model
            else Polygon()
        )
        ground = shared.clean(walls.difference(passage))
        fixed, parts, gates = [], [], []
        terrace = [
            geometry.sample_ground(field, *walls.exterior.interpolate(d).coords[0])
            for d in np.arange(0, walls.exterior.length, 0.73)
        ]
        floor = min(terrace) - 0.37
        base = float(np.median(terrace))
        zones = shell(parts, model, walls, passage, floor)
        for entry in model["entries"]:
            assert ground.boundary.distance(Point(entry["position_enu_m"])) < 0.002
            gate, paving = site.approach(lands, field, entry)
            gates.append(gate)
            paths.append(paving)
        building_elevations(
            parts, ground, zones, gates, base, field, "pavilion_body" in model
        )
        if not passage.is_empty:
            y = geometry.sample_ground(field, *passage.centroid.coords[0])
            bridge(parts, orient(passage), y + 4.38, 17.67)
        if "pavilion_body" in model:
            fixed.append(pavilion(parts, model, field))
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        staged[key] = shared.shared.shared.shared.shared.index_mesh(mesh)
        zone_report[key] = [
            (data["name"], round(s.area, 3), data["top"], data["levels"])
            for s, data in zones
        ]
        record = {k: model[k] for k in ("id", "name", "campus_id")} | dict(
            footprint_enu_m=ring(walls),
            base_z_m=round(floor, 4),
            roof_z_m=round(float(mesh.bounds[1, 1]), 4),
            area_m2=round(walls.area, 3),
            entrances=gates,
            support_collision_enu_m=[ring(p) for p in fixed],
        )
        if not passage.is_empty:
            assert len(geometry.sections(ground)) == 2
            record["ground_footprints_enu_m"] = [
                ring(p) for p in geometry.sections(ground)
            ]
        records.append(record)
        solids.extend([ground, *fixed])
        entries.extend(gates)

    ids = set(staged)
    aliases = [item["id"] for item in spec["absorbed_batches"]]
    ids.update(aliases)
    old = shapely.union_all(
        [
            Polygon(b["footprint_enu_m"]).buffer(0)
            for b in manifest["buildings"]
            if b["id"] in ids
        ]
    )
    routes, clearance = shared.shared.shared.check_routes(
        solids, [], entries, old, manifest, graph, cfg, ids
    )
    walk, collision = ground_site(lands, spec, paths, field, solids)
    orchard, tree_ids = registered_trees(spec, walk, collision, field)
    appearance = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    remove = tools.load_builder("build-frohnmayer-exterior-review.py").source_removals(
        spec, cfg, appearance
    )
    out = SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    site.memorial.gerlinger.export(
        glb,
        staged,
        trimesh.util.concatenate(lands),
        GROUND,
        "cedar-yasui-paving",
        vegetation={"cedar-yasui-trees": orchard},
    )
    package = out / "site.json"
    descriptor = dict(
        source_presentation_sha256=cfg["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        ground_node=GROUND,
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        buildings=records,
        absorbed_ids=aliases,
        batch_removals=remove,
    )
    package.write_text(
        json.dumps(descriptor, separators=(",", ":")) + "\n",
        encoding="utf8",
        newline="\n",
    )
    cfg["cedar_yasui_site"] = dict(
        url=f"{DIRECTORY}/site.json", sha256=tools.digest(package)
    )
    path.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit = dict(
        areas={rec["id"]: rec["area_m2"] for rec in records},
        zones=zone_report,
        triangles={key: len(mesh.faces) for key, mesh in staged.items()},
        former_roofs=remove,
        route_edges=routes,
        closest_route_m=round(float(clearance), 3),
        walk_area_m2=round(float(walk.area), 2),
        campus_trees=tree_ids,
        entries=[g["gate"] for g in entries],
        model_sha256=descriptor["sha256"],
        descriptor_sha256=tools.digest(package),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
