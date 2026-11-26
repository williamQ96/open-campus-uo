# SPDX-License-Identifier: Apache-2.0
"""Build the Gerlinger Hall and Annex exterior package from campus reference geometry."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.affinity import scale
from shapely.geometry import LineString, Point, Polygon, box
import trimesh

source = Path(__file__).with_name("build-museum-exterior-review.py")
builder_spec = spec_from_file_location(source.stem, source)
museum = module_from_spec(builder_spec)
builder_spec.loader.exec_module(museum)
tools = museum.tools
geometry = tools.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/gerlinger-site-review.json"
DIRECTORY = "gerlinger-site-review"
GROUND = "gerlinger-approaches"
SOUTH_STAIRS = (-422.12, -378.37)
BREEZEWAY_SUPPORTS = (-235.9, -225.10)

BRICK = (150, 91, 75)
BRICK_BAND = (136, 78, 67)
SHINGLE = (119, 114, 104)
COPPER = (102, 102, 83)
TRIM = (196, 175, 140)
CREAM = (215, 205, 172)
GLASS = (59, 82, 84)
IRON = (56, 53, 49)
MAROON = (116, 48, 51)
SLAB = (157, 156, 144)
CONCRETE = (147, 149, 139)
PLANTING = (89, 110, 65)


def surface(parts, region, bottom, height, wall=BRICK, roof=SHINGLE):
    for piece in geometry.sections(region):
        parts.append(geometry.shell(piece, bottom, height, wall, roof))


def prism(parts, region, bottom, top, wall=BRICK, roof=None):
    tools.flat(parts, region, bottom, top, wall, roof)


def hip(parts, region, bounds, bottom, eave, ridge, inset, roof=SHINGLE):
    west, south, east, north = bounds
    mid = (west + east) / 2
    y0, y1 = south + inset, north - inset
    sw, se, ne, nw = (west, south), (east, south), (east, north), (west, north)
    a, b = (mid, y0), (mid, y1)
    gradient = ridge - eave
    faces = (
        (Polygon([sw, se, a]), lambda e, n: (n - south) / inset),
        (Polygon([se, ne, b, a]), lambda e, n: (east - e) / (east - mid)),
        (Polygon([ne, nw, b]), lambda e, n: (north - n) / inset),
        (Polygon([nw, sw, a, b]), lambda e, n: (e - west) / (mid - west)),
    )
    for face, rise in faces:
        surface(
            parts,
            region.intersection(face),
            bottom,
            lambda e, n: eave + gradient * rise(e, n),
            BRICK,
            roof,
        )


def tower_roof(parts, base):
    previous = None
    profiles = (
        (1.0, 23.31),
        (0.69, 23.72),
        (0.40, 24.39),
        (0.19, 25.01),
        (0.05, 25.41),
    )
    for factor, elevation in profiles:
        ring = scale(base.envelope, factor, factor, origin="center")
        if previous:
            prior, low = previous
            outer = list(prior.exterior.coords)[:-1]
            inner = list(ring.exterior.coords)[:-1]
            for j in range(4):
                k = (j + 1) % 4
                axis = 0 if outer[j][0] == outer[k][0] else 1
                start, end = outer[j][axis], inner[j][axis]
                face = Polygon([outer[j], outer[k], inner[k], inner[j]])
                surface(
                    parts,
                    face,
                    23.08,
                    lambda e, n: low
                    + (elevation - low) * ((e, n)[axis] - start) / (end - start),
                    CONCRETE,
                    COPPER,
                )
        previous = ring, elevation
    prism(parts, ring, 23.08, elevation, CONCRETE, COPPER)


def hall_roof(parts, plan, spec, bottom):
    west, east = spec["central_roof_east_west_m"]
    profile = spec["central_roof_profile_north_up_m"]
    core = plan.intersection(box(west, -226, east, -196))
    for (n0, z0), (n1, z1) in zip(profile, profile[1:]):
        face = core.intersection(box(west, n0, east, n1))
        surface(
            parts,
            face,
            bottom,
            lambda e, n: z0 + (z1 - z0) * (n - n0) / (n1 - n0),
            BRICK,
            (153, 151, 135) if n0 < -222 else SHINGLE,
        )

    for x0, y0, x1, y1, top in (
        (-442.36, -225.08, west, -196.62, 25.84),
        (east, -225.08, -357.96, -197.02, 26.72),
    ):
        bounds = (x0, y0, x1, y1)
        hip(parts, plan.intersection(box(*bounds)), bounds, bottom, 21.54, top, 9.8)
    front = plan.intersection(box(-357.96, -219, -356, -202))
    center = -210.74
    for lo, hi in ((-218.17, center), (center, -203.31)):
        surface(
            parts,
            front.intersection(box(-358, lo, -356, hi)),
            bottom,
            lambda e, n: 21.76 + 3.18 * (1 - abs(n - center) / 7.43),
            BRICK,
            SHINGLE,
        )

    for x in (-428.04, -373.48):
        for n in (-200.10, -221.23):
            tower = box(x - 2.55, n - 2.42, x + 2.55, n + 2.42)
            tower = tower.intersection(plan)
            prism(parts, tower, 20.65, 23.15, BRICK)
            prism(parts, tower.buffer(0.105, join_style="mitre"), 23.05, 23.37, TRIM)
            tower_roof(parts, tower)

    for side, n in ((-1, -217.6), (1, -204.85)):
        for i, e in enumerate(spec["dormer_centers_east_m"]):
            if side == 1 and i == 1:
                continue
            front_n = n + side * (0.21 if i in {0, 9} else 0)
            back_n = n - side * 3.72
            half = 0.94 if i in {0, 9} else 0.78
            low = min(front_n, back_n)
            high = max(front_n, back_n)
            for begin, end in ((e - half, e), (e, e + half)):
                surface(
                    parts,
                    box(begin, low, end, high),
                    23.84,
                    lambda x, y: 25.64
                    + 0.56 * (1 - abs(x - e) / half)
                    + 0.10 * abs(y - front_n),
                    TRIM,
                    SHINGLE,
                )
            direction = side
            _, face = tools.face(
                parts, (e + direction * half, front_n), (e - direction * half, front_n)
            )
            sash(
                face,
                half,
                1.19,
                24.10,
                25.52,
                columns=3,
                rows=3,
                shade=IRON if i in {0, 9} else GLASS,
            )

    for e, n, width, depth, z in (
        (-433.4, -211, 2.9, 1.6, 26.00),
        (-365.2, -211.4, 2.6, 1.5, 26.64),
        (-432.5, -205.8, 1.7, 1.55, 25.07),
    ):
        prism(
            parts,
            box(e - width / 2, n - depth / 2, e + width / 2, n + depth / 2),
            z - 0.7,
            z + 0.1,
            TRIM,
            GLASS,
        )


def sash(face, center, width, low, high, columns=3, rows=4, shade=GLASS):
    lo, hi = center - width / 2, center + width / 2
    face(lo - 0.09, hi + 0.09, 0.008, 0.068, low - 0.095, high + 0.10, TRIM)
    face(lo, hi, 0.073, 0.094, low, high, shade)
    for x in np.linspace(lo, hi, columns + 1):
        face(x - 0.026, x + 0.026, 0.09, 0.125, low, high, CREAM)
    for z in np.linspace(low, high, rows + 1):
        face(lo, hi, 0.09, 0.131, z - 0.026, z + 0.026, CREAM)
    face(lo - 0.14, hi + 0.14, 0.03, 0.19, low - 0.11, low - 0.019, TRIM)


def surround(face, center, ground, reach):
    sash(
        face, center, 1.93, ground + 0.19, ground + 3.38, columns=2, rows=4, shade=IRON
    )
    for offset in (-1.46, 1.46):
        at = center + offset
        face(at - 0.23, at + 0.23, 0.04, reach, ground + 0.13, ground + 3.36, CREAM)
        face(
            at - 0.34, at + 0.34, 0.04, reach + 0.13, ground + 0.13, ground + 0.36, TRIM
        )
        face(
            at - 0.35, at + 0.35, 0.04, reach + 0.11, ground + 3.18, ground + 3.47, TRIM
        )
    face(
        center - 1.94,
        center + 1.94,
        -0.012,
        reach + 0.20,
        ground + 3.40,
        ground + 3.66,
        CREAM,
    )


def hall_east(parts, gate, field):
    e, n = gate["position_enu_m"]
    grade = float(geometry.sample_ground(field, e + 2.25, n))
    width, front = tools.face(parts, (e, -218.17), (e, -203.31))
    at = n + 218.17
    for x in (-3.9, 0, 3.9):
        c = at + x
        sash(front, c, 1.58, 15.31, 18.31, rows=6)
        sash(front, c, 1.49, 19.14, 20.83, rows=3)
        front(c - 0.94, c + 0.94, 0.012, 0.30, 18.44, 18.63, TRIM)
        awning = box(e + 0.11, n + x - 0.86, e + 0.89, n + x + 0.86)
        surface(
            parts, awning, 17.54, lambda xx, yy: 18.28 - 0.61 * (xx - e), MAROON, MAROON
        )
        if x:
            sash(front, c, 1.32, grade + 0.58, grade + 2.07, rows=3)
            front(c - 0.90, c + 0.90, 0.09, 0.86, 15.02, 15.19, IRON)
            front(c - 0.89, c + 0.89, 0.82, 0.88, 15.97, 16.03, IRON)
            for u in np.linspace(c - 0.87, c + 0.87, 8):
                front(u - 0.019, u + 0.019, 0.824, 0.884, 15.17, 16.0, IRON)
    surround(front, at, grade, 0.61)
    cap = museum.arch(n, 3.69, grade + 3.42, grade + 3.69, 0.77)
    museum.arch_panel(parts, cap, e + 0.115, 0, 1, CREAM)
    front(0, width, -0.015, 0.20, 21.51, 21.81, TRIM)
    gable = Polygon([(n - 7.42, 21.75), (n + 7.42, 21.75), (n, 24.93)])
    museum.arch_panel(parts, gable, e + 0.13, 0, 1, CREAM)
    for edge in (-7.42, 7.42):
        tools.beam(
            parts, (e + 0.185, n + edge, 21.79), (e + 0.185, n, 25.02), 0.18, TRIM
        )
    for q in (0.27, width - 0.27, at - 5.42, at + 5.42):
        for z in np.arange(12, 21.55, 0.46):
            front(q - 0.18, q + 0.18, -0.005, 0.094, z, z + 0.26, BRICK_BAND)
    for start, end in ((-223.76, -218.17), (-203.31, -197.02)):
        side_width, wing = tools.face(parts, (-357.96, start), (-357.96, end))
        for lo, hi, w in (
            (12.23, 13.63, 1.35),
            (15.22, 17.72, 1.5),
            (19.0, 20.71, 1.27),
        ):
            sash(wing, side_width / 2, w, lo, hi, rows=4)
        wing(0, side_width, -0.02, 0.24, 21.38, 21.64, TRIM)
    landing = box(e - 0.018, n - 2.21, e + 2.95, n + 2.21)
    surface(
        parts,
        landing,
        grade - 0.42,
        lambda ee, nn: grade + 0.13 + 0.095 * (e + 2.95 - ee),
        SLAB,
        SLAB,
    )


def hall_long_sides(parts, spec, field):
    west, east = spec["central_roof_east_west_m"]
    north, south = -200.48, -225.08
    nw, front = tools.face(parts, (east, north), (west, north))
    _, rear = tools.face(parts, (west, south), (east, south))
    gate = spec["entrances"][1]
    e, n = gate["position_enu_m"]
    grade = float(geometry.sample_ground(field, e, n + 2.5))
    for z, h in ((12.28, 0.24), (15.32, 0.18), (20.55, 0.45)):
        front(0, nw, -0.02, 0.21, z, z + h, TRIM)
    for z, h in ((12.56, 0.20), (20.55, 0.45)):
        rear(0, nw, -0.02, 0.21, z, z + h, TRIM)
    bays = np.linspace(2.28, nw - 2.28, 10)
    for i, at in enumerate(bays):
        sash(front, at, 2.22, 15.62, 19.34, columns=4, rows=6)
        if abs(east - at - e) > 2.7:
            for delta in (-0.64, 0.64):
                sash(front, at + delta, 0.83, 10.33, 12.03, columns=2, rows=3)
        is_door = i in (0, len(bays) - 1)
        at = SOUTH_STAIRS[i // (len(bays) - 1)] - west if is_door else at
        x = west + at
        arch = museum.arch(x, 3.42, 14.13, 18.89, 1.62)
        museum.arch_panel(parts, arch, south - 0.045, 2, 1, TRIM)
        if is_door:
            sash(rear, at, 2.06, 14.00, 17.45, columns=2, rows=4, shade=IRON)
            sash(rear, at, 2.45, 17.61, 18.97, columns=4, rows=2)
        else:
            sash(rear, at, 2.47, 14.25, 18.97, columns=4, rows=7)
            sash(rear, at, 2.08, 11.06, 12.36, columns=4, rows=2, shade=IRON)
        nose = museum.arch(x, 2.50, 18.87, 18.93, 1.09)
        museum.arch_panel(parts, nose, south - 0.105, 2, 1, GLASS)
        for u in (at - 0.64, at, at + 0.64):
            rear(u - 0.024, u + 0.024, 0.12, 0.157, 18.94, 19.70, CREAM)
    surround(front, east - e, grade, 0.23)
    arch = museum.arch(e, 3.1, grade + 3.39, grade + 3.71, 0.68)
    museum.arch_panel(parts, arch, north + 0.22, 2, -1, CREAM)

    for x in SOUTH_STAIRS:
        low = float(geometry.sample_ground(field, x, south - 4.1))
        for s in range(11):
            z = low + (14.0 - low) * (s + 1) / 11
            prism(
                parts,
                box(x - 1.48, south - 4.45 + s * 0.33, x + 1.48, south + 0.016),
                low - 0.34,
                z,
                SLAB,
            )
        for sign in (-1, 1):
            r = x + sign * 1.39
            tools.beam(
                parts,
                (r, south - 4.25, low + 1.04),
                (r, south - 0.61, 14.89),
                0.051,
                IRON,
            )
            for step in (0.10, 0.40, 0.70, 0.94):
                nn = south - 4.25 + 3.64 * step
                z = low + (13.86 - low) * step
                tools.beam(parts, (r, nn, z), (r, nn, z + 1.03), 0.038, IRON)

    for start, end in (
        ((-442.36, -196.62), (-442.36, -223.7)),
        ((west, -196.62), (-442.36, -196.62)),
        ((-442.36, -223.7), (-430.55, -223.7)),
        ((-357.96, -197.02), (east, -197.02)),
        ((-370.15, -223.76), (-357.96, -223.76)),
    ):
        width, face = tools.face(parts, start, end)
        face(0, width, 0.002, 0.22, 21.10, 21.46, TRIM)
        for u in np.arange(1.95, width - 1, 3.38):
            for lo, hi, w, rows in (
                (10.62, 12.19, 1.06, 3),
                (14.53, 17.31, 1.49, 5),
                (18.39, 20.04, 1.23, 3),
            ):
                sash(face, u, w, lo, hi, rows=rows)


def annex_shell(parts, plan, spec, base):
    break_n = spec["main_roof_break_north_m"]
    main = plan.intersection(box(-500, -271, -430, break_n))
    prism(parts, main, base, spec["main_roof_z_m"], (130, 83, 73), (184, 183, 176))
    high = plan.intersection(box(-498, break_n, -430.6, -238.87))
    prism(parts, high, base, 20.40, (130, 83, 73), SLAB)
    low = plan.difference(main.union(high))
    bridge = low.intersection(box(-440.52, -237.45, -437.37, -222))
    prism(parts, low.difference(bridge), base, 14.90, (131, 85, 76), (179, 175, 157))
    prism(parts, bridge, 13.06, 15.27, CONCRETE, SLAB)
    for n in BREEZEWAY_SUPPORTS:
        prism(parts, box(-440.34, n - 0.24, -437.54, n + 0.24), base, 13.23, CONCRETE)
    return bridge


def annex_front(parts, spec, field):
    side = -233.21
    west, east = -483.52, -452.76
    width, front = tools.face(parts, (east, side), (west, side))
    grade = float(geometry.sample_ground(field, -471.8, side + 1.8))
    front(0, width, -0.03, 0.55, 14.65, 15.25, CONCRETE)
    for u in np.arange(0.35, width - 1.2, 2.51):
        sash(front, u + 1.06, 1.94, grade + 0.52, 14.37, columns=2, rows=1)
        front(u - 0.14, u + 0.18, 0.048, 0.43, grade + 0.10, 14.70, CONCRETE)
    side_hi = -238.87
    _, upper = tools.face(parts, (east, side_hi), (west, side_hi))
    upper(0, width, -0.025, 0.11, 15.09, 20.52, CONCRETE)
    # Narrow recessed seams interrupt the surface without changing the roof envelope.
    for u in np.arange(0.20, width - 1.65, 2.49):
        upper(u, u + 2.445, 0.115, 0.19, 16.11, 20.35, (159, 161, 146))
        upper(u + 0.05, u + 0.18, 0.12, 0.69, 15.09, 15.58, (127, 128, 115))
    planter = box(-482.8, side + 1.59, -455.73, side + 4.0)
    grades = [
        geometry.sample_ground(field, e, side + 2.7)
        for e in np.linspace(-482, -456, 10)
    ]
    bed = planter.buffer(-0.20, join_style="mitre")
    prism(
        parts, planter.difference(bed), min(grades) - 0.55, max(grades) + 0.56, CONCRETE
    )
    prism(parts, bed, min(grades) - 0.52, max(grades) + 0.37, PLANTING)
    gate = spec["entrances"][0]
    e, n = gate["position_enu_m"]
    _, entrance = tools.face(parts, (e + 2, n), (e - 2, n))
    ground = float(geometry.sample_ground(field, e, n + 2.7))
    sash(entrance, 2, 1.86, ground + 0.63, ground + 3.39, columns=2, rows=3, shade=IRON)
    entrance(0.25, 3.65, -0.025, 0.89, ground + 3.28, ground + 3.59, CONCRETE)
    for i in range(4):
        entrance(
            0.51,
            3.49,
            -0.025,
            1.94 - 0.37 * i,
            ground - 0.38,
            ground + (i + 1) * 0.145,
            SLAB,
        )
    for e0, color in ((-495.86, (117, 74, 68)), (-431.55, (143, 91, 79))):
        is_west = e0 < -450
        a, b = (-244.92, -268.9) if is_west else (-268.9, -244.92)
        length, wing = tools.face(parts, (e0, a), (e0, b))
        wing(0, length, -0.07, 0.10, 10.54, 11.42, CONCRETE)
        wing(0, length, -0.03, 0.09, 24.97, 25.48, color)
    return planter


def export(
    output,
    buildings,
    terrain,
    ground_node=GROUND,
    ground_layer="gerlinger-paving",
    vegetation=None,
):
    scene = trimesh.Scene()
    vegetation = vegetation or {}
    for name, mesh in (*buildings.items(), (ground_node, terrain), *vegetation.items()):
        colors = mesh.visual.vertex_colors.copy()
        srgb = colors[:, :3].astype(float) / 255
        linear = np.where(
            srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4
        )
        colors[:, :3] = np.round(linear * 255).astype(np.uint8)
        mesh.visual.vertex_colors = colors
        scene.add_geometry(mesh, node_name=name, geom_name=name)

    def identify(tree):
        tree["asset"][
            "copyright"
        ] = "Open Campus contributors. Original geometry CC BY 4.0."
        tree["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.025, "roughnessFactor": 0.86}}
        ]
        for node in tree["nodes"]:
            name = node.get("name")
            if name in buildings:
                node["extras"] = {"asset_kind": "building", "asset_id": name}
            elif name == ground_node:
                node["extras"] = {
                    "asset_kind": "landscape-surface",
                    "surface_layer": ground_layer,
                }
            elif name in vegetation:
                node["extras"] = {
                    "asset_kind": "landscape-detail",
                    "detail_kind": "vegetation",
                }
        for mesh in tree["meshes"]:
            mesh["primitives"][0]["material"] = 0

    output.write_bytes(
        trimesh.exchange.gltf.export_glb(
            scene, include_normals=True, tree_postprocessor=identify
        )
    )
    reload = trimesh.load(output, force="scene", process=False)
    assert set(reload.graph.nodes_geometry) == {*buildings, ground_node, *vegetation}
    assert np.allclose(scene.bounds, reload.bounds, atol=0.00005)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    prior = {b["id"]: b for b in manifest["buildings"]}
    plans, meshes, records = {}, {}, []
    supports = []
    for name in ("hall", "annex"):
        model = spec[name]
        key = model["id"]
        plan = Polygon(model["footprint_enu_m"])
        assert plan.is_valid and key in config["replaces_building_ids"]
        base = round(
            min(
                geometry.sample_ground(field, *plan.exterior.interpolate(s).coords[0])
                for s in np.arange(0, plan.exterior.length, 0.4)
            )
            - 0.42,
            3,
        )
        pieces = []
        if name == "hall":
            hall_roof(pieces, plan, model, base)
            hall_east(pieces, model["entrances"][0], field)
            hall_long_sides(pieces, model, field)
            collision = plan
            extra = [box(e - 1.48, -229.53, e + 1.48, -225.08) for e in SOUTH_STAIRS]
        else:
            bridge = annex_shell(pieces, plan, model, base)
            planter = annex_front(pieces, model, field)
            collision = plan.difference(bridge)
            extra = [
                planter,
                *[
                    box(-440.34, n - 0.24, -437.54, n + 0.24)
                    for n in BREEZEWAY_SUPPORTS
                ],
            ]
        supports.extend(extra)
        mesh = trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        for gate in model["entrances"]:
            assert collision.boundary.distance(Point(gate["position_enu_m"])) < 0.0005
        plans[key] = collision
        meshes[key] = mesh
        records.append(
            {
                "id": key,
                "footprint_enu_m": list(collision.exterior.coords)[:-1],
                "support_collision_enu_m": [
                    list(p.exterior.coords)[:-1] for p in extra
                ],
                "area_m2": round(plan.area, 2),
                "base_z_m": base,
                "roof_z_m": round(float(mesh.bounds[1, 1]), 3),
                "entrances": model["entrances"],
            }
        )
    block = shapely.union_all([*plans.values(), *supports])
    others = {
        key: Polygon(value["footprint_enu_m"]).buffer(0)
        for key, value in prior.items()
        if key not in plans
    }
    assert not any(block.intersection(other).area > 0.02 for other in others.values())
    navigation = json.loads((SCENE / "navigation.json").read_bytes())
    old = shapely.union_all(
        [Polygon(prior[key]["footprint_enu_m"]).buffer(0) for key in plans]
    )
    conflicts = []
    for i, (a, b, *_) in enumerate(navigation["edges"]):
        edge = LineString([navigation["nodes_enu_m"][a], navigation["nodes_enu_m"][b]])
        if edge.distance(block) < 0.42 <= edge.distance(old):
            conflicts.append(i)
    assert not conflicts, conflicts
    paving = [
        ((-356.68, -215.2, -350.8, -206.5), SLAB),
        ((-403.22, -200.50, -396.8, -194.99), SLAB),
        ((-443.72, -228.43, -355.8, -224.28), SLAB),
        ((-493.33, -237.0, -430.72, -227.0), SLAB),
    ]
    terrain = tools.approaches(
        [
            {"outline": list(box(*bounds).exterior.coords), "rgb": rgb}
            for bounds, rgb in paving
        ],
        field,
        block,
    )
    directory = SCENE / DIRECTORY
    directory.mkdir(exist_ok=True)
    model = directory / "site.glb"
    export(model, meshes, terrain)
    site = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": tools.digest(field_path),
        "url": f"{DIRECTORY}/site.glb",
        "sha256": tools.digest(model),
        "ground_node": GROUND,
        "buildings": records,
    }
    descriptor = directory / "site.json"
    descriptor.write_text(
        json.dumps(site, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n"
    )
    config["gerlinger_site_review"] = {
        "url": f"{DIRECTORY}/site.json",
        "sha256": tools.digest(descriptor),
    }
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    audit = {
        "areas_m2": {r["id"]: r["area_m2"] for r in records},
        "triangles": {key: len(mesh.faces) for key, mesh in meshes.items()}
        | {GROUND: len(terrain.faces)},
        "route_edges": len(navigation["edges"]),
        "new_route_conflicts": conflicts,
        "model_sha256": tools.digest(model),
        "site_sha256": tools.digest(descriptor),
    }
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
