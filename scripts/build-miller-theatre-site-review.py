# SPDX-License-Identifier: Apache-2.0
"""Build the registered Miller Theatre Complex and its joint with Villard."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-heritage-core-site-review.py")
loader = spec_from_file_location(source.stem, source)
heritage = module_from_spec(loader)
loader.loader.exec_module(heritage)
memorial, tools, geometry = heritage.memorial, heritage.tools, heritage.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/miller-theatre-site-review.json"
DIRECTORY = "heritage-miller-review"
GROUND = "heritage-miller-approaches"

CONCRETE = (184, 179, 165)
PANEL = (194, 189, 174)
REVEAL = (133, 132, 121)
CAP = (185, 180, 164)
SLATE = (126, 131, 128)
GRAVEL = (164, 167, 160)
GLASS = (52, 73, 76)
ALUMINUM = (172, 174, 159)
IRON = (69, 79, 76)
PAVING = (162, 156, 141)
SOIL = (116, 100, 77)
flat, surface = memorial.flat, memorial.roof


def top(zone, y):
    _, south, _, north = zone["bounds"]
    lo, hi = zone["south_z_m"], zone["north_z_m"]
    return lo + (y - south) * (hi - lo) / (north - south)


def roofs(parts, spec, plan, bottom):
    remaining = plan
    for zone in spec["roof_sections"]:
        area = remaining.intersection(box(*zone["bounds"]))
        assert area.area > 24, zone["name"]
        membrane = SLATE if zone["name"].startswith("Robinson") else GRAVEL
        surface(parts, area, bottom, lambda e, n: top(zone, n), CONCRETE, membrane)
        rim = area.difference(area.buffer(-0.17, join_style="mitre"))
        outrise = 0.24 if zone["name"] == "Robinson fly tower" else 0.14
        surface(
            parts,
            rim,
            min(top(zone, y) for y in area.bounds[1::2]) - 0.10,
            lambda e, n: top(zone, n) + outrise,
            CONCRETE,
            CAP,
        )
        remaining = remaining.difference(area)
    z = spec["remaining_roof_z_m"]
    flat(parts, remaining, bottom, z, CONCRETE, GRAVEL)
    rim = remaining.difference(remaining.buffer(-0.16, join_style="mitre"))
    flat(parts, rim, z - 0.09, z + 0.16, CONCRETE, CAP)
    auditorium = spec["roof_sections"][3]
    for x in (-498.69, -492.87, -486.56):
        for y in (177.95, 183.26, 188.50):
            pos = top(auditorium, y)
            flat(
                parts,
                box(x - 0.30, y - 0.42, x + 0.32, y + 0.41),
                pos - 0.10,
                pos + 0.43,
                CONCRETE,
                CAP,
            )
    for x, n, z in (
        (-487.35, 166.34, 12.67),
        (-472.98, 168.14, 12.79),
        (-466.25, 173.12, 12.88),
        (-475.8, 189.30, 24.37),
    ):
        flat(
            parts,
            box(x - 0.28, n - 0.43, x + 0.28, n + 0.43),
            z - 0.28,
            z + 0.39,
            REVEAL,
            CAP,
        )


def double_door(add, center, threshold):
    left, right = center - 1.12, center + 1.12
    head = threshold + 2.13
    add(left - 0.036, right + 0.036, 0.116, 0.165, threshold, head, ALUMINUM)
    for x in (left + 0.10, center + 0.052):
        add(x, x + 0.91, 0.167, 0.181, threshold + 0.16, head - 0.09, (60, 90, 91))
        add(x, x + 0.91, 0.182, 0.207, threshold + 1.00, threshold + 1.070, IRON)


def lobby(parts, spec, threshold, bottom):
    e = spec["entrance"]["position_enu_m"][0]
    a, b = (e, 190.85), (e, 173.60)
    width, add = tools.face(parts, a, b)
    center = a[1] - spec["entrance"]["position_enu_m"][1]
    low, mullion_head, canopy = threshold - 0.06, 7.27, 8.94
    l, r = 0.65, width - 0.62
    add(0, width, -0.02, 0.092, bottom + 0.05, low, PANEL)
    bay = np.linspace(l, r, 15)
    tint = [GLASS, (66, 87, 89), (60, 81, 83), (79, 88, 79), (59, 80, 84)]
    for i, (start, end) in enumerate(zip(bay, bay[1:])):
        warm = i in (3, 5, 8, 11, 12)
        add(start, end, 0.087, 0.113, low, mullion_head, tint[i % len(tint)])
        add(
            start + 0.11,
            end - 0.066,
            0.112,
            0.129,
            low + 0.31,
            low + 0.42,
            (156, 132, 91) if warm else (89, 107, 104),
        )
        if warm:
            add(start + 0.11, end - 0.065, 0.112, 0.132, 6.86, 6.95, (185, 156, 103))
    for x in bay:
        add(x - 0.031, x + 0.031, 0.111, 0.151, low, canopy, ALUMINUM)
    for z in (low, threshold + 2.18, 6.98, mullion_head):
        add(l, r, 0.114, 0.158, z - 0.029, z + 0.028, ALUMINUM)
    for x in (center - 4.39, center, center + 4.51):
        double_door(add, x, threshold)
    for u in (0.09, width - 0.25):
        add(u, u + 0.15, -0.03, 0.29, low - 0.98, canopy, PANEL)
    add(l, r, 0.077, 0.143, mullion_head, canopy - 0.19, (166, 167, 153))
    for x in np.arange(l + 0.05, r - 0.036, 0.13):
        add(x - 0.012, x + 0.012, 0.14, 0.203, mullion_head, canopy - 0.16, ALUMINUM)
    add(0, width, -0.045, 0.92, canopy - 0.19, canopy + 0.092, PANEL)
    add(l, r, 0.027, 0.79, mullion_head - 0.095, mullion_head + 0.053, ALUMINUM)
    for u in (0.60, width - 0.60):
        add(u - 0.10, u + 0.10, 0.65, 0.82, low - 0.1, canopy - 0.11, PANEL)


def panel_grid(add, length, low, high, spacing):
    add(0, length, 0.012, 0.080, low, high, PANEL)
    for z in np.arange(low + 2.65, high - 0.2, 2.65):
        add(0.017, length - 0.018, 0.079, 0.101, z - 0.019, z + 0.019, REVEAL)
    for u in np.arange(spacing, length - 0.18, spacing):
        add(u - 0.025, u + 0.025, 0.079, 0.101, low, high, REVEAL)


def elevations(parts, spec, plan, threshold, bottom):
    id_x, _ = spec["entrance"]["position_enu_m"]
    coords = list(orient(plan).exterior.coords)
    for a, b in zip(coords, coords[1:]):
        width, add = tools.face(parts, a, b)
        e, n = (np.asarray(a) + b) / 2
        if e == id_x:
            continue
        height = 12.40
        if e < -498.54 and n >= 190.85:
            height = 7.61
        elif e > -464.13 and 171.38 <= n < 192.67:
            height = 10.59
        if width < 1.6:
            continue
        panel_grid(add, width, bottom, height, 3.05)
        if width > 5.15 and n > 193.14 and e < -480.46:
            for u in np.arange(1.66, width - 1.03, 2.77):
                heritage.rectangular(
                    add, u, 1.39, 4.53, min(height - 0.48, 7.42), REVEAL
                )
        if width > 5.11 and n < 173.64 and e > -514:
            u = width / 2
            add(u - 0.55, u + 0.55, 0.083, 0.128, bottom + 0.97, 7.49, IRON)
            add(u - 0.42, u + 0.42, 0.131, 0.157, 4.69, 7.32, (71, 91, 93))
            add(u - 0.43, u + 0.43, 0.157, 0.19, 6.02, 6.076, ALUMINUM)
            if width > 12:
                for ux in (u - 3.14, u + 3.21):
                    heritage.rectangular(add, ux, 1.18, 7.80, 10.17, REVEAL)
    lobby(parts, spec, threshold, bottom)

    tower = spec["roof_sections"][0]
    quad = heritage.corners(tower["bounds"])
    for a, b in zip(quad, quad[1:] + quad[:1]):
        width, add = tools.face(parts, a, b)
        panel_grid(
            add, width, 13.43, min(top(tower, a[1]), top(tower, b[1])) - 0.10, 4.88
        )
        for u in (0.20, width * 0.36, width * 0.71, width - 0.20):
            add(u - 0.083, u + 0.083, 0.075, 0.242, 13.22, 24.30, CONCRETE)
    bay = ((-464.91, 171.38), (-458.67, 171.38))
    width, add = tools.face(parts, *bay)
    for u in np.linspace(1.08, width - 0.94, 4):
        heritage.rectangular(add, u, 1.22, 6.34, 9.32, (142, 144, 133))


def stairs(parts, x, n, run, halfwidth, low, top, count):
    for i in range(count):
        length = run - i * (run - 0.58) / max(1, count - 1)
        z = low + (top - low) * (i + 1) / count
        flat(
            parts,
            box(x - length, n - halfwidth, x + 0.025, n + halfwidth),
            low - 0.78,
            z,
            PAVING,
        )
        flat(
            parts,
            box(x - length - 0.012, n - halfwidth, x - length + 0.059, n + halfwidth),
            z - 0.041,
            z + 0.012,
            REVEAL,
        )
    for side in (-1, 1):
        line = n + side * (halfwidth - 0.12)
        e0, e1 = x - run + 0.19, x - 0.60
        h0, h1 = low + 0.90, top + 0.89
        tools.beam(parts, (e0, line, h0), (e1, line, h1), 0.044, IRON)
        for frac in (0, 0.5, 1):
            px, topz = e0 + (e1 - e0) * frac, h0 + (h1 - h0) * frac
            tools.beam(parts, (px, line, topz - 0.89), (px, line, topz), 0.037, IRON)
    return box(x - run, n - halfwidth, x + 0.025, n + halfwidth)


def exterior_site(parts, field, gate):
    e, n = gate["position_enu_m"]
    toe = geometry.sample_ground(field, e - 3.83, n)
    threshold = round(float(toe + 0.94), 3)
    blockers = [stairs(parts, e, n, 3.83, 3.28, toe, threshold, 7)]
    for x, length, half, rise, count in (
        (-523.90, 1.57, 3.72, 0.44, 3),
        (-530.25, 1.75, 4.32, 0.50, 4),
    ):
        start = geometry.sample_ground(field, x - length, n)
        blockers.append(stairs(parts, x, n, length, half, start, start + rise, count))
    paving = [
        box(e - 7.70, n - 3.28, e - 3.76, n + 3.28),
        box(-530.33, n - 4.30, -525.48, n + 4.30),
        box(-533.30, n - 4.27, -531.95, n + 4.27),
    ]
    for start, stop, en, ew in (
        (175.35, 179.76, -522.20, -516.68),
        (187.04, 191.02, -523.34, -516.69),
        (177.10, 179.45, -529.61, -525.67),
        (187.64, 191.12, -529.56, -525.76),
    ):
        planter = box(en, start, ew, stop)
        z = geometry.sample_ground(field, (en + ew) / 2, (start + stop) / 2)
        flat(parts, planter, z - 0.66, z + 0.30, CONCRETE, SOIL)
        flat(parts, planter.difference(planter.buffer(-0.16)), z + 0.25, z + 0.39, CAP)
        blockers.append(planter)
        for x in np.arange(en + 0.72, ew - 0.34, 1.02):
            for y in np.arange(start + 0.64, stop - 0.35, 1.11):
                shrub = trimesh.creation.icosphere(subdivisions=1)
                shrub.apply_scale([0.46, 0.40, 0.50])
                shrub.apply_translation([x, z + 0.31, -y])
                shrub.visual.vertex_colors = [93, 114, 67, 255]
                parts.append(shrub)
    return blockers, paving, threshold


def build(spec, old_spec, manifest, config, field, graph):
    records, buildings, old_ground, audit = heritage.build(
        old_spec, manifest, config, graph, field, include_temporary_joint=False
    )
    building_id = spec["id"]
    model = Polygon(spec["footprint_enu_m"])
    gate = spec["entrance"]
    assert (
        model.is_valid
        and model.exterior.distance(Point(gate["position_enu_m"])) < 0.001
    )
    villard = Polygon(old_spec["villard"]["footprint_enu_m"])
    assert (
        model.intersection(villard).length > 23
        and model.intersection(villard).area < 0.01
    )
    base = round(
        min(
            geometry.sample_ground(field, *model.exterior.interpolate(u).coords[0])
            for u in np.arange(0, model.exterior.length, 0.38)
        )
        - 0.38,
        3,
    )
    grounds = []
    collision, paving, threshold = exterior_site(grounds, field, gate)
    theatre = shapely.union_all([model, *collision])
    e, n = gate["position_enu_m"]
    assert 0 < gate["approach_distance_m"] < 5
    assert theatre.distance(Point(e - gate["approach_distance_m"], n)) >= 0.5
    prior = next(s for s in manifest["buildings"] if s["id"] == building_id)
    old_shape = shapely.union_all(
        [
            Polygon(prior["footprint_enu_m"]),
            box(*old_spec["villard"]["west_join_bounds"]),
        ]
    )
    overlaps = [
        item["id"]
        for item in manifest["buildings"]
        if item["id"] not in {*buildings, building_id}
        and theatre.intersection(Polygon(item["footprint_enu_m"]).buffer(0)).area > 0.02
    ]
    assert not overlaps, overlaps
    conflicts = []
    for index, (a, b, *_) in enumerate(graph["edges"]):
        edge = LineString([graph["nodes_enu_m"][a], graph["nodes_enu_m"][b]])
        if edge.distance(theatre) < 0.42 <= edge.distance(old_shape):
            conflicts.append(index)
    assert not conflicts, conflicts
    audit["miller_route_edges"] = len(graph["edges"])
    audit["miller_new_conflicts"] = conflicts
    grounds.append(
        tools.approaches(
            [{"outline": list(p.exterior.coords), "rgb": PAVING} for p in paving],
            field,
            theatre,
        )
    )
    parts = []
    roofs(parts, spec, model, base)
    elevations(parts, spec, model, threshold, base)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
    buildings[building_id] = mesh
    records.append(
        {
            "id": building_id,
            "footprint_enu_m": spec["footprint_enu_m"],
            "area_m2": round(model.area, 2),
            "base_z_m": base,
            "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
            "support_collision_enu_m": [
                list(p.exterior.coords)[:-1] for p in collision
            ],
            "entrances": [gate | {"threshold_z_m": threshold}],
        }
    )
    return records, buildings, trimesh.util.concatenate([old_ground, *grounds]), audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    old_spec = json.loads(heritage.SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    records, buildings, ground, audit = build(
        spec, old_spec, manifest, config, json.loads(field_path.read_bytes()), graph
    )
    assert set(buildings) <= set(config["replaces_building_ids"])
    directory = SCENE / DIRECTORY
    directory.mkdir(exist_ok=True)
    glb = directory / "site.glb"
    memorial.gerlinger.export(glb, buildings, ground, GROUND, "heritage-core-paving")
    site_path = directory / "site.json"
    site_path.write_text(
        json.dumps(
            {
                "source_presentation_sha256": config["asset_sha256"],
                "source_base_model_sha256": manifest["model"]["sha256"],
                "source_heightfield_sha256": tools.digest(field_path),
                "url": f"{DIRECTORY}/site.glb",
                "sha256": tools.digest(glb),
                "ground_node": GROUND,
                "buildings": records,
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf8",
        newline="\n",
    )
    config["heritage_miller_site"] = {
        "url": f"{DIRECTORY}/site.json",
        "sha256": tools.digest(site_path),
    }
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit.update(
        footprint_m2=records[-1]["area_m2"],
        model_sha256=tools.digest(glb),
        descriptor_sha256=tools.digest(site_path),
        triangles={name: len(mesh.faces) for name, mesh in buildings.items()}
        | {GROUND: len(ground.faces)},
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
