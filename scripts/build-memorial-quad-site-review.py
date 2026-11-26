# SPDX-License-Identifier: Apache-2.0
"""Build the Chapman and Condon exterior models and their documented approaches."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-gerlinger-site-review.py")
loader = spec_from_file_location(source.stem, source)
gerlinger = module_from_spec(loader)
loader.loader.exec_module(gerlinger)
tools = gerlinger.tools
museum = gerlinger.museum
geometry = gerlinger.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/memorial-quad-site-review.json"
DIRECTORY = "memorial-quad-review"
GROUND = "memorial-quad-approaches"
GROUND_LAYER = "memorial-quad-paving"

BRICK = (148, 82, 63)
ADDITION = (133, 87, 73)
DARK_BRICK = (125, 67, 52)
TRIM = (195, 176, 153)
CREAM = (211, 191, 170)
ROOF = (181, 179, 169)
LOW_ROOF = (145, 143, 132)
GLASS = (60, 82, 86)
SHADE = (77, 62, 53)
OAK = (117, 79, 48)
CONCRETE = (159, 156, 145)
STEEL = (67, 66, 58)
flat = gerlinger.prism
roof = gerlinger.surface


def roof_height(zone, e):
    lo, _, hi, _ = zone["bounds"]
    west, east = zone["membrane_z_west_m"], zone["membrane_z_east_m"]
    return west + (east - west) * (e - lo) / (hi - lo)


def rooftop(parts, plan, model, base):
    rest = plan
    for zone in model["roof_segments"]:
        area = rest.intersection(box(*zone["bounds"]))
        assert area.area > 10
        historic = zone["name"] == "main roof"
        brick = BRICK if historic else ADDITION
        membrane = ROOF if historic else LOW_ROOF
        rise = zone["parapet_rise_m"]
        roof(parts, area, base, lambda e, n: roof_height(zone, e), brick, membrane)
        ring = area.difference(area.buffer(-0.29, join_style="mitre"))
        roof(
            parts,
            ring,
            min(roof_height(zone, e) for e in area.bounds[::2]) - 0.14,
            lambda e, n: roof_height(zone, e) + rise,
            brick,
            TRIM,
        )
        rest = rest.difference(area)
    assert rest.is_empty, rest.wkt

    if model["id"] == "roof-7ffcf31b":
        for e in (-606.0, -599.75, -593.40, -587.54):
            flat(
                parts,
                box(e - 0.72, -26.95, e + 0.72, -25.94),
                15.72,
                16.88,
                (136, 130, 113),
                (169, 164, 151),
            )
        for south, north in ((-59.9, -48.1), (-43.8, -37.2)):
            flat(parts, box(-591.0, south, -590.67, north), 14.52, 14.91, LOW_ROOF)


def coordinate(a, b):
    p = np.asarray(a)
    unit = np.asarray(b) - p
    length = np.linalg.norm(unit)
    unit /= length
    return length, lambda u, d: p + unit * u + np.array((unit[1], -unit[0])) * d


def panel(parts, profile, at, axis, normal, material):
    museum.arch_panel(parts, profile, at, axis, normal, material)


def quoin_arch(
    parts,
    start,
    end,
    center,
    width,
    low,
    spring,
    rise,
    material,
    outset=0.107,
    border=0.185,
):
    if start[0] == end[0]:
        axis = 0
        sign = 1 if end[1] > start[1] else -1
        cross = start[1] + sign * center
        fixed = start[0] + outset * sign
        normal = sign
    else:
        axis = 2
        north = end[0] < start[0]
        cross = start[0] + (-1 if north else 1) * center
        fixed = start[1] + (outset if north else -outset)
        normal = -1 if north else 1
    outer = museum.arch(cross, width + 2 * border, low, spring, rise + border)
    opening = museum.arch(cross, width, low + 0.035, spring, rise)
    offset = normal * (1 if axis == 0 else -1)
    panel(parts, outer, fixed, axis, normal, TRIM)
    panel(parts, opening, fixed + 0.022 * offset, axis, normal, material)


def cornice(parts, a, b, ledge, crown):
    width, face = tools.face(parts, a, b)
    face(0, width, -0.025, 0.22, ledge - 0.37, ledge, TRIM)
    face(0, width, -0.02, 0.28, ledge, ledge + 0.12, CREAM)
    if crown:
        count = max(1, int(width / 0.64))
        for u in (np.arange(count) + 0.5) * width / count:
            quoin_arch(
                parts,
                a,
                b,
                u,
                0.26,
                ledge - 0.36,
                ledge - 0.23,
                0.116,
                (163, 143, 125),
                outset=0.225,
                border=0.063,
            )
    face(0, width, -0.02, 0.11, ledge - 0.51, ledge - 0.43, DARK_BRICK)


def framed_sash(face, at, width, low, high, cols=4, rows=5):
    left, right = at - width / 2, at + width / 2
    face(left - 0.085, right + 0.085, 0.012, 0.066, low - 0.09, high + 0.10, DARK_BRICK)
    face(left, right, 0.069, 0.087, low, high, GLASS)
    for u in np.linspace(left, right, cols + 1):
        face(u - 0.023, u + 0.023, 0.084, 0.117, low, high, SHADE)
    for z in np.linspace(low, high, rows + 1):
        face(left, right, 0.091, 0.12, z - 0.022, z + 0.022, SHADE)
    face(left - 0.15, right + 0.15, 0.025, 0.183, low - 0.09, low, TRIM)


def ordinary_parts(parts, a, b, detail, skip):
    width, face = tools.face(parts, a, b)
    _, at_face = coordinate(a, b)
    kind, ledge, floor = detail
    if kind == "addition":
        bay_count = max(1, round(width / 2.73))
        for x in np.linspace(0, width, bay_count + 1):
            face(
                max(0, x - 0.105),
                min(width, x + 0.105),
                -0.04,
                0.136,
                floor,
                14.54,
                CONCRETE,
            )
        for bottom, top in (
            (floor + 0.03, floor + 0.21),
            (5.15, 5.40),
            (9.33, 9.57),
            (14.24, 14.54),
        ):
            face(0, width, -0.02, 0.16, bottom, top, CONCRETE)
        for at in (np.arange(bay_count) + 0.5) * width / bay_count:
            for lo, hi in ((2.48, 4.48), (6.15, 8.44), (10.42, 12.71)):
                framed_sash(face, at, min(1.43, width / 2), lo, hi, 3, 3)
        return

    cornice(parts, a, b, ledge, width > 6.5 and kind == "historic")
    breaks = (
        [(0, width)] if not skip else [(0, skip[0] - 1.18), (skip[0] + 1.18, width)]
    )
    for left, right in breaks:
        if right > left:
            face(left, right, -0.015, 0.17, 4.35, 4.53, TRIM)
    count = max(1, round(width / 3.06))
    for u in np.linspace(0, width, count + 1)[1:-1]:
        face(u - 0.08, u + 0.08, 0.0, 0.14, 4.58, ledge - 0.57, DARK_BRICK)
    for at in (np.arange(count) + 0.5) * width / count:
        glazed = min(width * 0.55, 1.65)
        if not any(abs(at - u) < 1.97 for u in skip):
            framed_sash(face, at, min(glazed, 1.55), 2.47, 3.79, 3, 3)
            framed_sash(face, at, glazed, 5.52, 8.26, 4, 5)
        if kind != "tower":
            framed_sash(face, at, glazed, 9.54, 13.39, 4, 6)
            face(at - glazed / 2, at + glazed / 2, 0.017, 0.053, 8.47, 9.27, DARK_BRICK)
            for i, u in enumerate(
                np.linspace(at - glazed * 0.33, at + glazed * 0.33, 5)
            ):
                side = 1 if i % 2 else -1
                for z in (8.61, 8.94):
                    left = at_face(u - 0.10, 0.058)
                    right = at_face(u + 0.10, 0.058)
                    tools.beam(
                        parts,
                        (*left, z - 0.072 * side),
                        (*right, z + 0.072 * side),
                        0.037,
                        (154, 89, 69),
                    )


def primary_front(parts, a, b, portal, floor):
    width, _ = coordinate(a, b)
    _, face = tools.face(parts, a, b)
    p = portal["position_enu_m"]
    center = np.linalg.norm(np.asarray(p) - a)
    door = portal["width_m"]
    cornice(parts, a, b, 15.57, True)
    face(0, width, -0.01, 0.10, floor - 0.08, floor + 0.14, TRIM)
    for offset in (-door - 1.49, door + 1.49):
        framed_sash(face, center + offset, 1.32, 5.66, 8.37, 3, 5)
        framed_sash(face, center + offset, 1.36, 9.82, 12.75, 3, 5)
    for off in (-1.38, 0, 1.38):
        u = center + off
        quoin_arch(parts, a, b, u, 1.03, 10.96, 13.79, 0.48, GLASS)
        for delta in (-0.28, 0, 0.28):
            face(
                u + delta - 0.022, u + delta + 0.022, 0.134, 0.172, 11.03, 13.92, SHADE
            )
        for z in np.linspace(11.21, 13.59, 6):
            face(u - 0.49, u + 0.49, 0.139, 0.178, z - 0.025, z + 0.025, SHADE)
    quoin_arch(parts, a, b, center, door + 0.44, floor, floor + 3.2, 1.15, SHADE)
    for offset in (-door / 2, 0, door / 2):
        face(
            center + offset - 0.047,
            center + offset + 0.047,
            0.134,
            0.198,
            floor + 0.02,
            floor + 2.93,
            OAK,
        )
    face(
        center - door / 2,
        center + door / 2,
        0.138,
        0.178,
        floor + 0.03,
        floor + 0.61,
        OAK,
    )
    for delta in (-0.69, 0.69):
        face(
            center - door / 2,
            center + door / 2,
            0.142,
            0.18,
            floor + 1.55 + delta,
            floor + 1.61 + delta,
            OAK,
        )
    face(
        center - door / 2 - 0.05,
        center + door / 2 + 0.05,
        0.146,
        0.22,
        floor + 2.81,
        floor + 3.07,
        TRIM,
    )
    for u in (0.11, width - 0.11):
        face(
            max(0, u - 0.11),
            min(width, u + 0.11),
            0.005,
            0.18,
            floor,
            15.07,
            DARK_BRICK,
        )


def apron(parts, a, b, gate, field, grand):
    _, at = coordinate(a, b)
    u = np.linalg.norm(np.asarray(gate["position_enu_m"]) - a)
    length = 4.18 if grand else 1.57
    width = 3.2 if grand else 1.48
    low = float(geometry.sample_ground(field, *at(u, length)))
    high = low + (1.58 if grand else 0.13)
    blocks = []
    for i in range(10 if grand else 1):
        frac = (i + 1) / 10 if grand else 1
        side = width - i * 0.092
        near = length - i * 0.355
        shape = Polygon(
            [
                at(u - side, -0.019),
                at(u + side, -0.019),
                at(u + side, near),
                at(u - side, near),
            ]
        )
        flat(parts, shape, low - 0.47, low + frac * (high - low), CONCRETE)
        if grand and i == 0:
            blocks.append(shape)
    paving = Polygon(
        [
            at(u - width, length - 0.06),
            at(u + width, length - 0.06),
            at(u + width - 0.42, length + 3.0),
            at(u - width + 0.42, length + 3.0),
        ]
    )
    if grand:
        for sign in (-1, 1):
            for start, stop, diff in (
                (0.16, 1.8, 0.15),
                (1.8, 3.52, 0.33),
                (3.52, 4.15, 0.59),
            ):
                ee, nn = at(u + sign * (width - 0.75 + diff), start)
                ee2, nn2 = at(u + sign * (width - 0.75 + diff + 0.18), stop)
                cap0, cap1 = high + 0.41 - 0.37 * start, high + 0.41 - 0.37 * stop
                tools.beam(parts, (ee, nn, cap0), (ee2, nn2, cap1), 0.19, TRIM)
                p = LineString([(ee, nn), (ee2, nn2)]).buffer(0.073, cap_style="flat")
                roof(
                    parts,
                    p,
                    low - 0.33,
                    lambda e, n: min(cap0, cap1),
                    BRICK,
                    DARK_BRICK,
                )
    return paving, high, blocks


def facades(parts, plan, model, field):
    ring = list(orient(plan).exterior.coords)
    gates = model["entrances"]
    paving, supports, thresholds = [], [], {}
    is_condon = model["id"] == "roof-7ffcf31b"
    for a, b in zip(ring, ring[1:]):
        if np.linalg.norm(np.asarray(b) - a) < 1.9:
            continue
        mid = (np.asarray(a) + b) / 2
        segment = LineString([a, b])
        on_wall = [
            g for g in gates if segment.distance(Point(g["position_enu_m"])) < 0.001
        ]
        kind = (
            "tower"
            if mid[0] <= -611.95 and -31.1 <= mid[1] <= -23.5
            else "addition" if mid[1] < -34.0 and is_condon else "historic"
        )
        ledge = 13.8 if kind == "tower" else 15.62 if is_condon else 16.03
        floor = min(2.13, geometry.sample_ground(field, *mid))
        large = next(
            (g for g in on_wall if g["gate"] in ("chapman-west", "condon-east")), None
        )
        if large:
            landing, landing_z, stairs = apron(parts, a, b, large, field, True)
            paving.append(landing)
            supports.extend(stairs)
            thresholds[large["gate"]] = round(landing_z, 4)
            primary_front(parts, a, b, large, landing_z)
        else:
            skip = [
                np.linalg.norm(np.asarray(g["position_enu_m"]) - a) for g in on_wall
            ]
            ordinary_parts(parts, a, b, (kind, ledge, floor), skip)
            for gate, u in zip(on_wall, skip):
                landing, landing_z, _ = apron(parts, a, b, gate, field, False)
                paving.append(landing)
                _, face = tools.face(parts, a, b)
                quoin_arch(
                    parts,
                    a,
                    b,
                    u,
                    gate["width_m"],
                    landing_z,
                    landing_z + 2.29,
                    0.48,
                    SHADE,
                )
                for x in (-0.83, 0, 0.83):
                    face(
                        u + x - 0.045,
                        u + x + 0.045,
                        0.13,
                        0.19,
                        landing_z,
                        landing_z + 2.29,
                        OAK,
                    )
                face(
                    u - 1.17,
                    u + 1.17,
                    -0.021,
                    0.42,
                    landing_z + 2.77,
                    landing_z + 3.09,
                    TRIM,
                )
                for d in (-0.82, 0.82):
                    face(
                        u + d - 0.17,
                        u + d + 0.17,
                        0.032,
                        0.21,
                        landing_z + 3.12,
                        landing_z + 3.55,
                        CREAM,
                    )
    return paving, supports, thresholds


def build(spec, manifest, field):
    buildings, meshes, plans, paving = [], {}, {}, []
    for name in ("chapman", "condon"):
        data = spec[name]
        plan = Polygon(data["footprint_enu_m"])
        key = data["id"]
        assert plan.is_valid
        sample = [
            geometry.sample_ground(field, *plan.exterior.interpolate(s).coords[0])
            for s in np.arange(0, plan.exterior.length, 0.36)
        ]
        base = round(min(sample) - 0.40, 3)
        parts = []
        rooftop(parts, plan, data, base)
        approaches, supports, thresholds = facades(parts, plan, data, field)
        paving.extend(approaches)
        for gate in data["entrances"]:
            assert plan.exterior.distance(Point(gate["position_enu_m"])) < 0.001
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        meshes[key] = mesh
        plans[key] = shapely.union_all([plan, *supports])
        buildings.append(
            {
                "id": key,
                "footprint_enu_m": data["footprint_enu_m"],
                "area_m2": round(plan.area, 2),
                "base_z_m": base,
                "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
                "support_collision_enu_m": [
                    list(outline.exterior.coords)[:-1] for outline in supports
                ],
                "entrances": [
                    gate
                    | (
                        {"threshold_z_m": thresholds[gate["gate"]]}
                        if gate["gate"] in thresholds
                        else {}
                    )
                    for gate in data["entrances"]
                ],
            }
        )
    block = shapely.union_all(list(plans.values()))
    old = []
    for data in manifest["buildings"]:
        shape = Polygon(data["footprint_enu_m"]).buffer(0)
        if data["id"] in plans:
            old.append(shape)
        else:
            assert block.intersection(shape).area < 0.02, data["id"]
    pavement = tools.approaches(
        [{"outline": list(p.exterior.coords), "rgb": CONCRETE} for p in paving],
        field,
        block,
    )
    return buildings, meshes, pavement, shapely.union_all(old), block


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field = json.loads(field_path.read_bytes())
    buildings, meshes, terrain, prior, occupied = build(spec, manifest, field)
    assert set(meshes) <= set(config["replaces_building_ids"])
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    conflicts = []
    for index, (a, b, *_) in enumerate(graph["edges"]):
        edge = LineString([graph["nodes_enu_m"][a], graph["nodes_enu_m"][b]])
        if edge.distance(occupied) < 0.42 <= edge.distance(prior):
            conflicts.append(index)
    assert not conflicts, conflicts
    site_dir = SCENE / DIRECTORY
    site_dir.mkdir(exist_ok=True)
    model = site_dir / "site.glb"
    gerlinger.export(model, meshes, terrain, GROUND, GROUND_LAYER)
    site = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": tools.digest(field_path),
        "url": f"{DIRECTORY}/site.glb",
        "sha256": tools.digest(model),
        "ground_node": GROUND,
        "buildings": buildings,
    }
    site_path = site_dir / "site.json"
    site_path.write_text(
        json.dumps(site, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n"
    )
    config["memorial_quad_site"] = {
        "url": f"{DIRECTORY}/site.json",
        "sha256": tools.digest(site_path),
    }
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    audit = {
        "footprint_m2": {b["id"]: b["area_m2"] for b in buildings},
        "triangles": {key: len(mesh.faces) for key, mesh in meshes.items()}
        | {GROUND: len(terrain.faces)},
        "route_edges": len(graph["edges"]),
        "new_conflicts": conflicts,
        "model_sha256": site["sha256"],
        "site_sha256": tools.digest(site_path),
    }
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
