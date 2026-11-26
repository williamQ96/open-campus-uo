# SPDX-License-Identifier: Apache-2.0
"""Build the registered Allen Hall exterior and its modeled entrances."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-memorial-quad-site-review.py")
loader = spec_from_file_location(source.stem, source)
memorial = module_from_spec(loader)
loader.loader.exec_module(memorial)
tools, geometry = memorial.tools, memorial.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/allen-site-review.json"
DIRECTORY = "allen-site-review"
GROUND = "allen-approaches"

BRICK = (153, 89, 72)
HISTORIC = (141, 86, 68)
BRICK_TRIM = (176, 106, 85)
BRICK_DARK = (117, 76, 66)
LIMESTONE = (208, 197, 174)
PRECAST = (177, 172, 158)
METAL = (156, 161, 154)
GLASS = (67, 94, 96)
DARK = (77, 96, 92)
PALE_GLASS = (107, 135, 130)
ROOF = (167, 167, 151)
ROOF_LOW = (150, 149, 138)
SOIL = (112, 94, 75)
flat, surface = memorial.flat, memorial.roof


def membrane(zone, n):
    _, south, _, north = zone["bounds"]
    z0, z1 = zone["south_z_m"], zone["north_z_m"]
    return z0 + (n - south) / (north - south) * (z1 - z0)


def register_roofs(parts, spec, plan, bottom):
    remaining = plan
    for zone in spec["roof_sections"]:
        section = remaining.intersection(box(*zone["bounds"]))
        assert section.area > 5, zone["name"]
        remaining = remaining.difference(section)
        high = zone["south_z_m"] > 18
        surface(
            parts,
            section,
            bottom,
            lambda e, n: membrane(zone, n),
            (117, 117, 107) if high else BRICK,
            ROOF if high else ROOF_LOW,
        )
        edge = section.difference(section.buffer(-0.16, join_style="mitre"))
        surface(
            parts,
            edge,
            min(membrane(zone, n) for n in section.bounds[1::2]) - 0.095,
            lambda e, n: membrane(zone, n) + 0.15,
            BRICK_DARK,
            PRECAST,
        )
    low = spec["west_roof_z_m"]
    flat(parts, remaining, bottom, low, BRICK, ROOF)
    rim = remaining.difference(remaining.buffer(-0.18, join_style="mitre"))
    flat(parts, rim, low - 0.12, low + 0.18, BRICK_DARK, LIMESTONE)

    for ox, oy, ex, ey, z in (
        (-361.08, 102.12, -357.78, 110.22, 17.42),
        (-364.07, 116.22, -355.61, 116.91, 14.91),
        (-344.95, 88.25, -341.03, 91.64, 19.91),
        (-346.67, 82.44, -342.43, 84.89, 20.35),
        (-335.45, 93.87, -332.75, 96.88, 18.33),
        (-323.56, 88.04, -323.18, 92.92, 18.15),
    ):
        flat(parts, box(ox, oy, ex, ey), low - 0.15, z, (137, 137, 124), PRECAST)
    for e in (-343.52, -338.97, -333.98, -328.89):
        flat(parts, box(e - 0.46, 78.70, e + 0.46, 79.68), 14.60, 15.37, METAL, PRECAST)


def windows(add, left, right, low, high, bays, warm=False):
    boundaries = np.linspace(left, right, bays + 1)
    for i, (a, b) in enumerate(zip(boundaries, boundaries[1:])):
        color = (
            (119, 112, 87)
            if warm and i % 4 == 2
            else (PALE_GLASS if i % 3 == 1 else GLASS)
        )
        add(a + 0.032, b - 0.032, 0.107, 0.129, low, high, color)
    for x in boundaries:
        add(x - 0.038, x + 0.038, 0.130, 0.186, low, high, METAL)
    for z in (low, high - (high - low) * 0.28, high):
        add(left, right, 0.130, 0.185, z - 0.041, z + 0.041, METAL)


def doors(add, center, width, base):
    left = center - width / 2
    add(left - 0.07, left + width + 0.07, 0.161, 0.226, base, base + 2.35, METAL)
    for x in (left + 0.105, center + 0.043):
        end = x + width / 2 - 0.15
        add(x, end, 0.226, 0.244, base + 0.126, base + 2.25, (59, 81, 82))
        add(x, end, 0.245, 0.268, base + 1.06, base + 1.14, PRECAST)


def glazing_bay(parts, a, b, base, high, gate, canopy=True):
    length, add = tools.face(parts, a, b)
    width = gate["width_m"]
    add(0.00, 0.13, -0.022, 0.255, base - 0.11, high, BRICK_DARK)
    add(length - 0.14, length, -0.022, 0.255, base - 0.11, high, BRICK_DARK)
    header = base + 2.43
    windows(add, 0.23, length - 0.23, header, high - 0.22, 5, True)
    for z in (base + 4.34, base + 7.04, high - 0.20):
        add(0.23, length - 0.23, 0.09, 0.199, z - 0.071, z + 0.071, METAL)
    windows(add, 0.23, length - 0.23, base + 0.14, header, 5)
    doors(add, length / 2, width, base)
    if canopy:
        add(0.09, length - 0.08, -0.021, 0.94, header + 0.03, header + 0.22, PRECAST)
    for l in (0.18, length - 0.24):
        add(l, l + 0.06, 0.15, 0.23, base, high, DARK)


def west_wing(parts, a, b):
    length, add = tools.face(parts, a, b)
    add(0.40, length - 0.35, 0.007, 0.18, 5.92, 13.72, LIMESTONE)
    add(0.31, length - 0.31, 0.011, 0.46, 13.82, 14.10, LIMESTONE)
    add(0.39, length - 0.36, 0.010, 0.32, 5.88, 6.07, LIMESTONE)
    for low, high in ((6.48, 8.77), (10.61, 13.04)):
        add(
            0.66,
            length - 0.63,
            0.183,
            0.201,
            low - 0.075,
            high + 0.063,
            (162, 168, 155),
        )
        windows(
            lambda l, r, i, o, lo, hi, rgb: add(
                l, r, i + 0.103, o + 0.103, lo, hi, rgb
            ),
            0.79,
            length - 0.78,
            low,
            high,
            24,
        )
    for u in np.linspace(2.24, length - 2.24, 9):
        add(u - 0.47, u + 0.47, 0.179, 0.257, 9.1, 10.16, (197, 184, 157))
        for delta, z in ((-0.23, 9.44), (-0.07, 9.62), (0.15, 9.23)):
            add(u + delta, u + delta + 0.11, 0.257, 0.285, z, z + 0.40, (178, 168, 143))
        add(u - 0.34, u + 0.34, 0.075, 0.10, 3.42, 5.42, BRICK_DARK)
        windows(add, u - 0.33, u + 0.33, 3.64, 5.24, 2)
    _, at = memorial.coordinate(a, b)
    for u in np.linspace(0.51, length - 0.50, 22):
        e, n = at(u, 0.13)
        tools.beam(parts, (e, n, 14.12), (e, n, 14.72), 0.033, DARK)
    e, n = at(0.48, 0.13)
    end_e, end_n = at(length - 0.47, 0.13)
    for z in (14.48, 14.71):
        tools.beam(parts, (e, n, z), (end_e, end_n, z), 0.04, DARK)


def elevations(parts, spec, plan, base, thresholds):
    coords = list(orient(plan).exterior.coords)
    gates = {g["gate"]: g for g in spec["entrances"]}
    for a, b in zip(coords, coords[1:]):
        length, add = tools.face(parts, a, b)
        e, n = (np.asarray(a) + b) / 2
        if e == -364.07 and length > 35:
            west_wing(parts, a, b)
        elif e == -364.98:
            gate = gates["allen-west"]
            glazing_bay(parts, a, b, thresholds[gate["gate"]], 13.97, gate)
        elif e == -320.53:
            gate = gates["allen-east"]
            glazing_bay(parts, a, b, thresholds[gate["gate"]], 14.69, gate)
        elif n == 74.42 and length > 20:
            south_front(parts, a, b, gates["allen-south"], thresholds["allen-south"])
        else:
            historic = n > 96.0 and e > -345.82
            roof = 14.9 if e > -349.0 else 14.21
            add(
                0,
                length,
                -0.01,
                0.047,
                base,
                roof - 0.10,
                HISTORIC if historic else BRICK,
            )
            add(0, length, 0.008, 0.21, roof - 0.093, roof + 0.123, PRECAST)
            if length < 2.3:
                continue
            for z in (5.86, 10.24):
                add(0, length, 0.015, 0.109, z - 0.065, z + 0.075, BRICK_TRIM)
            count = max(1, round(length / (3.16 if historic else 3.63)))
            for u in (np.arange(count) + 0.5) * length / count:
                half = 0.72 if historic else 1.04
                for lo, hi in ((4.51, 6.58), (7.48, 9.72), (11.08, 13.47)):
                    add(
                        u - half - 0.10,
                        u + half + 0.10,
                        0.057,
                        0.11,
                        lo - 0.095,
                        hi + 0.10,
                        BRICK_DARK,
                    )
                    windows(add, u - half, u + half, lo, hi, 2 if historic else 3)
                    add(
                        u - half - 0.10,
                        u + half + 0.10,
                        0.057,
                        0.211,
                        lo - 0.14,
                        lo - 0.06,
                        LIMESTONE,
                    )


def south_front(parts, a, b, gate, threshold):
    length, add = tools.face(parts, a, b)
    u = gate["position_enu_m"][0] - a[0]
    for low, high in ((3.76, 6.27), (7.43, 9.96), (11.29, 13.60)):
        for left, right, bays in ((u + 2.38, length - 1.04, 16), (0.37, u - 2.09, 2)):
            if right - left > 0.83:
                add(left, right, 0.03, 0.110, low - 0.045, high + 0.11, BRICK_DARK)
                windows(add, left, right, low, high, bays, True)
                add(left, right, 0.04, 0.307, low - 0.11, low - 0.038, LIMESTONE)
        if low > 4:
            add(u + 2.05, length - 0.79, 0.029, 0.48, high + 0.24, high + 0.45, PRECAST)
    doors(add, u, gate["width_m"], threshold)
    windows(add, u - 1.76, u + 1.76, threshold + 2.40, 13.95, 3, True)
    add(u - 2.00, u + 2.00, -0.020, 1.03, threshold + 2.47, threshold + 2.67, PRECAST)
    for z in (threshold + 4.27, 10.47):
        add(u - 1.81, u + 1.81, 0.013, 0.218, z - 0.09, z + 0.11, METAL)


def grounds_and_entries(parts, field, spec):
    paving, blockers, thresholds = [], [], {}
    for gate, run, half, count, rise in zip(
        spec["entrances"],
        (1.82, 0.91, 1.24),
        (1.45, 2.04, 1.45),
        (3, 1, 1),
        (0.46, 0.12, 0.14),
    ):
        e, n = gate["position_enu_m"]
        angle = np.deg2rad(gate["outward_degrees"])
        direction = np.array([np.sin(angle), np.cos(angle)])
        cross = np.array([direction[1], -direction[0]])
        anchor = np.array([e, n])

        def span(lo, hi, side):
            return Polygon(
                [
                    anchor + direction * reach + cross * spread
                    for reach, spread in (
                        (lo, -side),
                        (hi, -side),
                        (hi, side),
                        (lo, side),
                    )
                ]
            )

        toe = geometry.sample_ground(field, *(anchor + direction * run))
        threshold = round(float(toe + rise), 3)
        thresholds[gate["gate"]] = threshold
        for i in range(count):
            depth = run - i * (run - 0.53) / max(1, count - 1)
            shape = span(-0.024, depth, half)
            z = toe + (i + 1) / count * rise
            flat(parts, shape, toe - 0.64, z, PRECAST)
            if i == 0 and count > 1:
                blockers.append(shape)
        paving.append(span(run - 0.085, run + 2.56, half + 0.27))
    for e0, n0, e1, n1 in (
        (-367.13, 81.58, -366.70, 97.68),
        (-367.13, 98.01, -366.70, 113.24),
        (-341.40, 70.87, -332.65, 72.31),
        (-331.83, 70.90, -322.55, 72.35),
    ):
        plan = box(e0, n0, e1, n1)
        sample = lambda e, n: geometry.sample_ground(field, e, n)
        z = min(sample(e, n) for e in (e0, e1) for n in (n0, n1)) - 0.31
        surface(parts, plan, z, lambda e, n: sample(e, n) + 0.34, PRECAST, LIMESTONE)
        blockers.append(plan)
        if e0 > -360:
            area = plan.buffer(-0.14, join_style="mitre")
            surface(parts, area, z, lambda e, n: sample(e, n) + 0.365, PRECAST, SOIL)
            for e in np.arange(e0 + 0.7, e1 - 0.42, 1.3):
                shrub = trimesh.creation.icosphere(subdivisions=1)
                n = (n0 + n1) / 2
                shrub.apply_scale([0.46, 0.36, 0.41])
                shrub.apply_translation([e, sample(e, n) + 0.48, -n])
                shrub.visual.vertex_colors = [88, 112, 71, 255]
                parts.append(shrub)
    return paving, blockers, thresholds


def build(spec, manifest, field, graph):
    building_id = spec["id"]
    plan = Polygon(spec["footprint_enu_m"])
    assert plan.is_valid
    base = round(
        min(
            geometry.sample_ground(field, *plan.exterior.interpolate(u).coords[0])
            for u in np.arange(0, plan.exterior.length, 0.40)
        )
        - 0.55,
        3,
    )
    grounds = []
    paving, blockers, thresholds = grounds_and_entries(grounds, field, spec)
    occupied = shapely.union_all([plan, *blockers])
    old = Polygon(
        next(
            b["footprint_enu_m"]
            for b in manifest["buildings"]
            if b["id"] == building_id
        )
    )
    for gate in spec["entrances"]:
        e, n = gate["position_enu_m"]
        angle = np.deg2rad(gate["outward_degrees"])
        distance = gate["approach_distance_m"]
        assert plan.exterior.distance(Point(e, n)) < 0.001
        assert 0 < distance < 5
        assert (
            occupied.distance(
                Point(e + distance * np.sin(angle), n + distance * np.cos(angle))
            )
            >= 0.5
        )
    for item in manifest["buildings"]:
        if item["id"] != building_id:
            assert (
                occupied.intersection(Polygon(item["footprint_enu_m"]).buffer(0)).area
                < 0.02
            ), item["id"]
    conflicts = []
    for index, (i, j, *_) in enumerate(graph["edges"]):
        line = LineString([graph["nodes_enu_m"][i], graph["nodes_enu_m"][j]])
        if line.distance(occupied) < 0.42 <= line.distance(old):
            conflicts.append(index)
    assert not conflicts, conflicts
    grounds.append(
        tools.approaches(
            [{"outline": list(p.exterior.coords), "rgb": PRECAST} for p in paving],
            field,
            occupied,
        )
    )
    parts = []
    register_roofs(parts, spec, plan, base)
    elevations(parts, spec, plan, base, thresholds)
    model = trimesh.util.concatenate(parts)
    model.update_faces(model.nondegenerate_faces(height=0.00005))
    record = {
        "id": building_id,
        "footprint_enu_m": spec["footprint_enu_m"],
        "area_m2": round(plan.area, 2),
        "base_z_m": base,
        "roof_z_m": round(float(model.bounds[1, 1]), 4),
        "support_collision_enu_m": [list(p.exterior.coords)[:-1] for p in blockers],
        "entrances": [
            g | {"threshold_z_m": thresholds[g["gate"]]} for g in spec["entrances"]
        ],
    }
    return (
        record,
        model,
        trimesh.util.concatenate(grounds),
        {"route_edges": len(graph["edges"]), "new_conflicts": conflicts},
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    record, model, ground, audit = build(
        spec, manifest, json.loads(field_path.read_bytes()), graph
    )
    assert record["id"] in config["replaces_building_ids"]
    output = SCENE / DIRECTORY
    output.mkdir(exist_ok=True)
    glb = output / "site.glb"
    memorial.gerlinger.export(
        glb, {record["id"]: model}, ground, GROUND, "allen-paving"
    )
    descriptor = output / "site.json"
    descriptor.write_text(
        json.dumps(
            {
                "source_presentation_sha256": config["asset_sha256"],
                "source_base_model_sha256": manifest["model"]["sha256"],
                "source_heightfield_sha256": tools.digest(field_path),
                "url": f"{DIRECTORY}/site.glb",
                "sha256": tools.digest(glb),
                "ground_node": GROUND,
                "buildings": [record],
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf8",
        newline="\n",
    )
    config["allen_site_review"] = {
        "url": f"{DIRECTORY}/site.json",
        "sha256": tools.digest(descriptor),
    }
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit.update(
        footprint_m2=record["area_m2"],
        model_sha256=tools.digest(glb),
        descriptor_sha256=tools.digest(descriptor),
        triangles=[len(model.faces), len(ground.faces)],
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
