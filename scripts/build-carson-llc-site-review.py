# SPDX-License-Identifier: Apache-2.0
"""Build registered Carson and Living-Learning Center exteriors."""

import argparse
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import shapely
from shapely.affinity import scale
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-bean-unthank-site-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)
site, tools, geometry = shared.site, shared.tools, shared.geometry
graduate = shared.shared
index_mesh = graduate.shared.shared.shared.index_mesh
roof_layer = tools.load_builder("build-longhouse-site-review.py").roof_layer
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/carson-llc-site-review.json"
DIRECTORY = "carson-llc-review"
GROUND = "carson-llc-grounds"
CARSON = (156, 95, 76)
LLC = (148, 88, 68)
DARK_BRICK = (132, 82, 69)
ROOF_DARK = (124, 129, 123)
METAL = (181, 189, 187)
PALE = (215, 214, 198)
SLATE = (116, 127, 126)
STONE = (200, 182, 150)
BASE = (147, 140, 124)
GLASS = (78, 108, 113)
LIT_GLASS = (104, 137, 141)
SOLAR = (67, 78, 99)
PAVING = (174, 163, 145)
GRASS = (143, 157, 111)


def ring(poly):
    return list(orient(poly).exterior.coords)[:-1]


def compact(region):
    return shared.clean(region)


def flat_top(z):
    return lambda e, n: z


def roof_edges(parts, area, evaluate, depth=0.18):
    border = compact(area.difference(area.buffer(-depth, join_style="mitre")))
    roof_layer(parts, border, evaluate, 0.069, 0.056, SLATE, PALE)


def carson_shell(parts, plan, model, base):
    kitchen = compact(plan.intersection(box(*model["kitchen_bounds"])))
    housing = compact(plan.difference(kitchen))
    for area, z in ((housing, 19.08), (kitchen, 8.27)):
        site.flat(parts, area, base, z, CARSON, ROOF_DARK)
        cornice = compact(
            area.buffer(0.12, join_style="mitre").difference(
                area.buffer(-0.21, join_style="mitre")
            )
        )
        site.flat(parts, cornice, z - 0.18, z + 0.215, STONE, (169, 165, 149))
        parapet = compact(area.difference(area.buffer(-0.25, join_style="mitre")))
        site.flat(parts, parapet, z + 0.01, z + 0.15, DARK_BRICK, STONE)
    for w, s, e, n, z in model["equipment"]:
        area = compact(box(w, s, e, n).intersection(plan.buffer(-0.21)))
        if area.is_empty:
            continue
        bottom = 8.27 if kitchen.covers(area.centroid) else 19.08
        site.flat(
            parts, area, bottom - 0.045, z, DARK_BRICK if z > 22 else SLATE, ROOF_DARK
        )
        body = compact(area.buffer(-0.26, join_style="mitre"))
        site.flat(parts, body, z - 0.025, z + 0.135, SLATE, BASE)
    return [(housing, flat_top(19.08), "housing"), (kitchen, flat_top(8.27), "dining")]


def llc_shell(parts, plan, model, base):
    rest = plan
    priority = []
    surfaces = []
    for bounds, top in model["towers"]:
        area = compact(plan.intersection(box(*bounds)))
        site.flat(parts, area, base, top, LLC, ROOF_DARK)
        cap = compact(area.buffer(0.14, join_style="mitre"))
        site.flat(parts, cap, top - 0.13, top + 0.14, SLATE, METAL)
        priority.append((area, flat_top(top), "tower"))
        rest = compact(rest.difference(area))
    for name, bounds, axis, ridge, top, positive, negative in model["roofs"]:
        area = compact(plan.intersection(box(*bounds)))
        assert area.area > 85, name
        planes = np.zeros((2, 3))
        planes[:, axis] = [-positive, negative]
        planes[:, 2] = [top + positive * ridge, top - negative * ridge]

        def peak(e, n, axis=axis, ridge=ridge, top=top, s=(positive, negative)):
            coordinate = (e, n)[axis] - ridge
            return top + np.minimum(-s[0] * coordinate, s[1] * coordinate)

        for piece, height in graduate.roof_cells(area, planes):
            site.surface(
                parts,
                compact(piece),
                base,
                lambda e, n: height(e, n) - 0.145,
                LLC,
                METAL,
            )
        eaves = compact(
            area.buffer(0.55, join_style="mitre").difference(plan.difference(area))
        )
        for piece, height in graduate.roof_cells(eaves, planes):
            piece = compact(piece)
            roof_layer(parts, piece, height, 0.163, 0, SLATE, METAL)
            roof_edges(parts, piece, height)
        priority.append((compact(rest.intersection(area)), peak, "housing"))
        surfaces.append((area, peak))
        rest = compact(rest.difference(area))
    low = model["lower_z"]
    site.flat(parts, rest, base, low, LLC, ROOF_DARK)
    site.flat(
        parts,
        compact(rest.difference(rest.buffer(-0.17, join_style="mitre"))),
        low - 0.07,
        low + 0.21,
        SLATE,
        METAL,
    )
    priority.append((rest, flat_top(low), "community"))
    w, s, e, n, z = model["clerestory"]
    pane = compact(box(w, s, e, n).intersection(plan.buffer(-0.20)))
    site.flat(parts, pane, 17.31, z, SLATE, METAL)
    for y in (s, n):
        a, b = ((e, y), (w, y)) if y == n else ((w, y), (e, y))
        length, add = tools.face(parts, a, b)
        shared.glazing(
            add,
            0.07,
            length - 0.07,
            z - 0.86,
            z - 0.26,
            max(1, round(length / 1.62)),
            glass=GLASS,
        )
        add(0.02, length - 0.02, 0.006, 0.23, z - 0.19, z + 0.03, METAL)
    for w, s, e, n, z in model["roof_equipment"]:
        body = compact(box(w, s, e, n).intersection(plan.buffer(-0.16)))
        if body.is_empty:
            continue
        anchor = body.centroid
        bottom = max(
            [low] + [h(anchor.x, anchor.y) for a, h in surfaces if a.covers(anchor)]
        )
        if z > bottom + 0.13:
            site.flat(parts, body, bottom - 0.5, z, SLATE, METAL)
            inset = compact(body.buffer(-0.175, join_style="mitre"))
            site.flat(parts, inset, z - 0.035, z + 0.092, SLATE, PALE)
    if "solar" in model:
        panels(parts, model["solar"], surfaces[-1][1], plan)
    return priority


def panels(parts, bounds, height, plan):
    w, s, e, n = bounds

    def panel_height(east, north):
        return height(east, north) + 0.20

    for y in np.linspace(s, n - 1.45, 2):
        for x in np.arange(w, e - 1.85, 2.2):
            cell = box(x, y, x + 1.98, y + 1.43)
            if not plan.covers(cell):
                continue
            roof_layer(parts, cell, panel_height, 0.13, 0, SLATE, SOLAR)
            for ratio in (0.333, 0.666):
                rule = box(
                    x + ratio * 1.98, y + 0.02, x + ratio * 1.98 + 0.022, y + 1.41
                )
                roof_layer(
                    parts, rule, panel_height, 0.019, 0.026, SLATE, (122, 137, 151)
                )


def casements(add, center, width, z, high, top_storey):
    half = width / 2
    trim = (165, 166, 151)
    add(
        center - half - 0.05,
        center + half + 0.05,
        0.012,
        0.10,
        z - 0.054,
        high + 0.05,
        trim,
    )
    span = width / 4
    for i in range(4):
        a = center - half + i * span
        add(
            a + 0.041,
            a + span - 0.035,
            0.101,
            0.131,
            z + 0.043,
            high - 0.038,
            LIT_GLASS if i in (0, 2) else GLASS,
        )
    if top_storey:
        y = z + (high - z) * 0.39
        add(
            center - half + 0.035,
            center + half - 0.035,
            0.130,
            0.151,
            y - 0.025,
            y + 0.025,
            trim,
        )
    add(
        center - half - 0.084,
        center + half + 0.084,
        0.074,
        0.193,
        z - 0.125,
        z - 0.043,
        STONE,
    )


def lawn_side_shade(add, center, width, z):
    extent = width * 0.56
    for offset in np.arange(-extent, extent, 0.25):
        add(
            center + offset,
            center + offset + 0.063,
            0.117,
            0.604,
            z - 0.017,
            z + 0.039,
            SLATE,
        )
    add(center - extent, center + extent, 0.519, 0.651, z - 0.029, z + 0.048, SLATE)
    for x in (center - extent + 0.10, center + extent - 0.10):
        add(x - 0.032, x + 0.032, 0.066, 0.55, z - 0.14, z - 0.013, SLATE)


def carson_face(add, edge, top, kind, base, grade, gate, a, b):
    length = edge.length
    if length < 0.93:
        return
    add(0.018, length - 0.018, 0.008, 0.066, grade - 0.24, grade + 0.26, BASE)
    if gate:
        x = edge.project(Point(gate["position_enu_m"]))
        threshold = gate["threshold_z_m"]
        width = gate["width_m"]
        tools.frame(
            add, x - width / 2, width, threshold + 0.035, threshold + 2.45, mullions=4
        )
        shared.glazing(
            add,
            x - width / 2 - 0.16,
            x + width / 2 + 0.16,
            threshold + 2.49,
            threshold + 2.71,
            4,
        )
        width = min(7.64, length - 0.26)
        add(
            x - width / 2,
            x + width / 2,
            0.02,
            2.68,
            gate["threshold_z_m"] + 2.76,
            gate["threshold_z_m"] + 3.04,
            STONE,
        )
        for offset in (-width / 2, width / 2):
            add(
                x + offset - 0.13,
                x + offset + 0.13,
                0.018,
                0.092,
                grade - 0.08,
                gate["threshold_z_m"] + 2.77,
                STONE,
            )
    if kind == "dining":
        shared.floor_glass(add, length, grade, min(top - 0.60, base + 3.1), gate, edge)
        add(0.026, length - 0.026, 0.012, 0.108, top - 0.45, top - 0.28, STONE)
        return

    e, n = edge.interpolate(0.5, normalized=True).coords[0]
    stripe = 2.6 < length < 6 and (
        (e < -83 and n < -43) or (-78 < e < -72 and n < -51) or (e > -48 and n > -57)
    )
    if stripe:
        left, right = length * 0.20, length * 0.81
        add(left - 0.08, right + 0.08, 0.008, 0.095, base + 0.58, top - 0.88, STONE)
        add(left, right, 0.096, 0.136, base + 0.72, top - 1.02, GLASS)
        for x in np.arange(left + 0.13, right, 0.139):
            add(x, x + 0.025, 0.134, 0.157, base + 0.75, top - 1.065, LIT_GLASS)
        for z in np.arange(base + 2.78, top - 1.08, 2.92):
            add(left, right, 0.121, 0.163, z, z + 0.108, STONE)
        return
    bays = max(1, round(length / 4.0))
    step = length / bays
    if step < 1.56:
        return
    for i in range(bays):
        center = (i + 0.5) * step
        for floor in range(5):
            z = base + (1.19 if floor == 0 else 1.45) + 2.93 * floor
            if z < grade + 0.48 or z + 1.45 > top - 0.55:
                continue
            if floor == 0 and gate and abs(center - x) < 3.6:
                continue
            casements(
                add,
                center,
                min(step * 0.81, 3.47),
                z,
                z + (1.36 if floor == 0 else 1.60),
                floor > 0,
            )


def llc_face(add, edge, top, kind, base, grade, gate, a, b, lower_roof=None):
    length = edge.length
    if length < 0.91:
        return
    middle = edge.interpolate(0.5, normalized=True)
    way = (np.asarray(b) - a) / length
    out = (way[1], -way[0])
    low = base + 3.51
    if kind == "community":
        shared.floor_glass(
            add, length, grade, top(*middle.coords[0]) - 0.27, gate, edge
        )
        return
    min_roof = min(top(*a), top(*b))
    if kind == "tower":
        if length > 2.1:
            x = length * 0.56
            for z in np.arange(base + 0.52, min_roof - 2.06, 3.10):
                shared.glazing(add, x - 0.69, x + 0.69, z, z + 2.72, 2, glass=LIT_GLASS)
                add(x - 0.77, x + 0.77, 0.016, 0.138, z - 0.06, z + 0.016, PALE)
        return
    storefront = gate is not None or (
        out[1] < -0.7
        and -166.2 < middle.y < -161.2
        or out[1] > 0.7
        and (-153.0 < middle.y < -150.9 or -202.5 < middle.y < -200.8)
    )
    if lower_roof is None:
        add(0.01, length - 0.01, 0.008, 0.081, grade - 0.19, grade + 0.35, BASE)
        if length > 2.3 and storefront:
            shared.floor_glass(add, length, grade, low - 0.17, gate, edge)
    if gate:
        x = edge.project(Point(gate["position_enu_m"]))
        width = min(length - 0.13, gate["width_m"] + 0.89)
        z = gate["threshold_z_m"] + 2.69
        add(x - width / 2, x + width / 2, 0.053, 1.07, z, z + 0.164, SLATE)

    light_band = base + 9.25
    if min_roof > light_band + 0.32:
        add(0.006, length - 0.006, 0.009, 0.052, light_band, min_roof - 0.19, PALE)
        add(
            0.009,
            length - 0.009,
            0.111,
            0.197,
            light_band - 0.112,
            light_band + 0.035,
            SLATE,
        )
    bays = max(1, round(length / 3.02))
    step = length / bays
    if step < 1.31:
        return
    for i in range(bays):
        center = (i + 0.5) * step
        width = min(step * 0.68, 2.08)
        h = top(*(np.asarray(a) + center * way))
        if lower_roof is None and not storefront and grade + 2.5 < low:
            shared.glazing(
                add,
                center - width * 0.38,
                center + width * 0.38,
                grade + 0.83,
                grade + 2.41,
                2,
            )
        for layer, z in enumerate((base + 4.13, base + 7.12, base + 10.18)):
            if lower_roof is not None and z < lower_roof + 0.23:
                continue
            high = min(h - 0.39, z + 1.63)
            if high < z + 0.72:
                continue
            shared.glazing(
                add, center - width / 2, center + width / 2, z, high, 2, glass=GLASS
            )
            add(
                center - width * 0.56,
                center + width * 0.56,
                0.102,
                0.23,
                z - 0.078,
                z - 0.023,
                STONE,
            )
            if out[1] < -0.52 and layer < 2:
                lawn_side_shade(add, center, width, high + 0.14)


def wall_details(parts, plan, zones, gates, datum, field, carson):
    spans = [
        (area.buffer(0.008), h, kind) for area, h, kind in zones if area.area > 0.03
    ]
    outline = list(plan.exterior.coords)
    for a, b in zip(outline, outline[1:]):
        for u, v, roof, kind in site.science.face_spans(a, b, spans):
            line = LineString((u, v))
            middle = line.interpolate(0.5, normalized=True)
            grade = geometry.sample_ground(field, middle.x, middle.y)
            gate = next(
                (g for g in gates if line.distance(Point(g["position_enu_m"])) < 0.011),
                None,
            )
            _, add = tools.face(parts, u, v)
            if carson:
                carson_face(
                    add, line, roof(middle.x, middle.y), kind, datum, grade, gate, u, v
                )
            else:
                llc_face(add, line, roof, kind, datum, grade, gate, u, v)

    if carson:
        return
    lower, flat, _ = next(z for z in zones if z[2] == "community")
    for area, roof, kind in zones:
        if kind != "housing":
            continue
        for section in geometry.sections(area):
            edge = list(orient(section).exterior.coords)
            for a, b in zip(edge, edge[1:]):
                wall = LineString((a, b))
                for p in shapely.get_parts(wall.intersection(lower.buffer(0.012))):
                    if p.geom_type != "LineString" or p.length < 2:
                        continue
                    a0, b0 = sorted(
                        (p.coords[0], p.coords[-1]),
                        key=lambda xy: wall.project(Point(xy)),
                    )
                    mid = p.interpolate(0.5, normalized=True)
                    if plan.boundary.distance(mid) < 0.035:
                        continue
                    grade = geometry.sample_ground(field, mid.x, mid.y)
                    _, add = tools.face(parts, a0, b0)
                    llc_face(
                        add,
                        p,
                        roof,
                        kind,
                        datum,
                        grade,
                        None,
                        a0,
                        b0,
                        lower_roof=flat(mid.x, mid.y),
                    )


def carson_porch(parts, gate, field):
    e, n = gate["position_enu_m"]
    if gate["gate"] != "carson-east":
        return []
    supports = []
    for offset in (-3.21, -1.57, 1.57, 3.21):
        point = (e + 2.49, n + offset)
        block = box(point[0] - 0.14, point[1] - 0.23, point[0] + 0.14, point[1] + 0.23)
        base = geometry.sample_ground(field, *point)
        site.flat(parts, block, base - 0.16, gate["threshold_z_m"] + 2.79, STONE)
        supports.append(block)
    return supports


def add_ground(parts, quad, patches, field, blocked):
    def entries(x, color):
        return [{"outline": ring(p), "rgb": color} for p in geometry.sections(x)]

    lawn = scale(Point(*quad["center"]).buffer(1, quad_segs=29), *quad["lawn_radii"])
    rim = lawn.buffer(quad["walk_width"], quad_segs=7).difference(lawn)
    walks = [
        LineString(path).buffer(width / 2, quad_segs=5) for width, path in quad["paths"]
    ]
    pavement = compact(shapely.union_all([rim, *walks, *patches]))
    # Clip pavement against its holes so the central green and open courts remain visible.
    safe = compact(blocked.union(lawn.difference(shapely.union_all(walks))))
    parts.append(tools.approaches(entries(pavement, PAVING), field, safe))
    north = Polygon(quad["north_lawn"])
    parts.append(
        tools.approaches(
            entries(lawn.union(north), GRASS), field, blocked.union(pavement)
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    plans, records, ground, path_patches, columns, gates, meshes, zone_stats = (
        [],
        [],
        [],
        [],
        [],
        [],
        {},
        {},
    )
    for model in spec["models"]:
        id = model["id"]
        carson = model["campus_id"] == "076"
        plan = orient(Polygon(model["footprint_enu_m"]))
        assert plan.is_valid
        sample = [
            geometry.sample_ground(field, *plan.exterior.interpolate(d).coords[0])
            for d in np.arange(0, plan.exterior.length, 0.51)
        ]
        floor = min(sample) - 0.40
        datum = float(np.median(sample))
        parts, entries, supports = [], [], []
        zones = (
            carson_shell(parts, plan, model, floor)
            if carson
            else llc_shell(parts, plan, model, floor)
        )
        for entry in model["entries"]:
            assert plan.boundary.distance(Point(entry["position_enu_m"])) < 0.003
            gate, patch = site.approach(ground, field, entry)
            entries.append(gate)
            path_patches.append(patch)
            if carson:
                supports.extend(carson_porch(parts, gate, field))
        wall_details(parts, plan, zones, entries, datum, field, carson)
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        meshes[id] = index_mesh(mesh)
        records.append(
            {k: model[k] for k in ("id", "name", "campus_id")}
            | dict(
                footprint_enu_m=ring(plan),
                base_z_m=round(floor, 4),
                roof_z_m=round(float(mesh.bounds[1, 1]), 4),
                area_m2=round(plan.area, 3),
                support_collision_enu_m=[ring(p) for p in supports],
                entrances=entries,
            )
        )
        plans.append(plan)
        gates.extend(entries)
        columns.extend(supports)
        zone_stats[id] = [round(a.area, 2) for a, _, _ in zones]
    old = shapely.union_all(
        [
            Polygon(b["footprint_enu_m"]).buffer(0)
            for b in manifest["buildings"]
            if b["id"] in meshes
        ]
    )
    count, clearance = graduate.shared.check_routes(
        plans, columns, gates, old, manifest, graph, config, set(meshes)
    )
    add_ground(
        ground, spec["quad"], path_patches, field, shapely.union_all([*plans, *columns])
    )
    out = SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    site.memorial.gerlinger.export(
        glb, meshes, trimesh.util.concatenate(ground), GROUND, "carson-llc-paving"
    )
    descriptor = out / "site.json"
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        ground_node=GROUND,
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        buildings=records,
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    config["carson_llc_site"] = dict(
        url=f"{DIRECTORY}/site.json", sha256=tools.digest(descriptor)
    )
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit = dict(
        areas={x["id"]: x["area_m2"] for x in records},
        roof_zones_m2=zone_stats,
        triangles={id: len(m.faces) for id, m in meshes.items()},
        route_edges=count,
        nearest_route_m=round(clearance, 3),
        entrances={x["id"]: x["entrances"] for x in records},
        sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
