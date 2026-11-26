# SPDX-License-Identifier: Apache-2.0
"""Build the Bean and Unthank exteriors and their registered common site."""

import argparse
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-graduate-village-site-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)
site, tools, geometry = shared.site, shared.tools, shared.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/bean-unthank-site-review.json"
DIRECTORY = "bean-unthank-review"
GROUND = "bean-unthank-approaches"
BRICK = (158, 92, 68)
BRICK_SHADE = (143, 81, 63)
UNTHANK_BRICK = (125, 82, 60)
DARK = (68, 70, 64)
DARKER = (56, 61, 56)
WARM = (151, 118, 74)
CEMENT = (178, 172, 155)
FRAME = (213, 211, 187)
GLASS = (71, 103, 110)
REFLECTION = (96, 125, 129)
BEAN_ROOF = (195, 196, 185)
UNTHANK_ROOF = (181, 186, 180)
COPING = (153, 156, 149)
PAVING = (171, 165, 151)
METAL = [(131, 143, 142), (168, 177, 174), (186, 191, 182), (106, 122, 123)]


def clean(area):
    return shapely.set_precision(area.buffer(0), 0.001)


def roof_zones(parts, plan, model, floor, bean):
    rest = plan
    regions = []
    dorm_wall = BRICK if bean else UNTHANK_BRICK
    roof_color = BEAN_ROOF if bean else UNTHANK_ROOF
    for wing in model["wings"]:
        area = clean(rest.intersection(box(*wing["bounds"])))
        assert area.area > 50, wing["name"]
        rest = clean(rest.difference(area))
        regions.append((area, wing["top"], wing["kind"]))
    if rest.area > 0.03:
        regions.append((rest, 8.12 if bean else 9.63, "link" if bean else "podium"))
    for area, top, kind in regions:
        wall = DARK if kind in ("admin", "link", "podium") else dorm_wall
        site.flat(parts, area, floor, top, wall, roof_color)
        curb = clean(area.difference(area.buffer(-0.19, join_style="mitre")))
        site.flat(
            parts,
            curb,
            top - 0.01,
            top + (0.25 if kind != "upper" else 0.31),
            wall,
            COPING,
        )
        rim = clean(area.boundary.buffer(0.067, join_style="mitre"))
        site.flat(parts, rim, top + 0.245, top + 0.295, COPING)
    return regions


def glazing(add, left, right, bottom, top, bays, dark=True, glass=GLASS):
    width = right - left
    if width <= 0.11 or top - bottom <= 0.11:
        return
    trim = DARK if dark else FRAME
    add(left - 0.045, right + 0.045, 0.014, 0.074, bottom - 0.048, top + 0.048, trim)
    add(left + 0.019, right - 0.019, 0.075, 0.101, bottom + 0.031, top - 0.031, glass)
    for x in np.linspace(left, right, bays + 1):
        add(x - 0.023, x + 0.023, 0.093, 0.137, bottom, top, trim)
    split = top - (top - bottom) * 0.24
    add(left, right, 0.091, 0.133, split - 0.027, split + 0.027, trim)


def floor_glass(add, length, base, top, gate, edge):
    top = min(top, base + 3.48)
    if length < 0.7 or top < base + 1.58:
        return
    if gate is None:
        glazing(
            add, 0.08, length - 0.08, base + 0.21, top, max(1, round(length / 1.25))
        )
    else:
        center = edge.project(Point(gate["position_enu_m"]))
        width = min(gate["width_m"], 2 * min(center, length - center) - 0.09)
        if width < 1.15:
            # The door may span a short vertex along a recessed entrance.
            width = gate["width_m"]
        left, right = center - width / 2, center + width / 2
        glazing(add, 0.08, left - 0.085, base + 0.21, top, max(1, round(left / 1.4)))
        glazing(
            add,
            right + 0.085,
            length - 0.08,
            base + 0.21,
            top,
            max(1, round((length - right) / 1.4)),
        )
        z = gate["threshold_z_m"]
        tools.frame(
            add, left, width, z + 0.035, z + 2.43, mullions=max(2, round(width / 1.12))
        )
        glazing(add, left, right, z + 2.52, top, max(2, round(width / 1.15)))


def bean_face(add, edge, kind, top, base, gate, court, lower_roof=None):
    length = edge.length
    if kind in ("link", "admin", "stair"):
        floor_glass(add, length, base, top - 0.46, gate, edge)
        if kind == "stair":
            for z in (base + 3.34, base + 6.31):
                if z + 2.5 < top - 0.41:
                    glazing(
                        add,
                        length * 0.19,
                        length * 0.83,
                        z,
                        z + 2.54,
                        max(2, round(length / 2.84)),
                    )
        else:
            add(0.012, length - 0.012, 0.008, 0.184, top - 0.55, top - 0.22, DARKER)
        return

    if lower_roof is None:
        add(0.016, length - 0.016, 0.01, 0.084, base - 0.12, base + 0.38, CEMENT)
    if length > 5 and not court and lower_roof is None:
        floor_glass(add, length, base, base + 2.62, gate, edge)
    count = max(1, round(length / 2.58))
    step = length / count
    if step < 1.14:
        return
    for i in range(count):
        x = (i + 0.5) * step
        left, right = x - step * 0.263, x + step * 0.263
        low = (
            max(base + 2.85, lower_roof + 0.15)
            if lower_roof is not None
            else base + 2.85
        )
        if not court and low < top - 0.16:
            add(
                x - step * 0.487,
                left - 0.046,
                0.009,
                0.119,
                low,
                top - 0.16,
                DARK,
            )
        elif court:
            add(left - 0.063, right + 0.063, 0.01, 0.055, base + 0.33, top - 0.22, DARK)
        for z in (base + 0.78, base + 3.78, base + 6.61):
            if lower_roof is not None and z < lower_roof + 0.22:
                continue
            if z + 1.58 > top - 0.2 or z < base + 1 and not court and length > 5:
                continue
            glazing(
                add,
                left,
                right,
                z,
                z + 1.58,
                2,
                dark=False,
                glass=GLASS if i % 4 else REFLECTION,
            )
        if not court and (lower_roof is None or base + 5.41 > lower_roof):
            add(
                left - 0.06,
                right + 0.06,
                0.022,
                0.119,
                base + 5.41,
                base + 5.46,
                CEMENT,
            )
    add(0.016, length - 0.016, 0.01, 0.101, top - 0.21, top - 0.095, DARK)


def unthank_base(add, edge, top, grade, gate):
    length = edge.length
    floor_glass(add, length, grade, top - 0.15, gate, edge)
    if length > 1.5:
        add(0.008, length - 0.008, 0.026, 0.108, grade + 3.52, grade + 3.74, DARK)
    if top > grade + 5.33 and length > 2.1:
        glazing(
            add,
            0.31,
            length - 0.31,
            grade + 4.13,
            grade + 5.30,
            max(2, round(length / 1.36)),
        )


def unthank_upper(add, edge, top, floor, outer):
    length = edge.length
    if length < 1.25:
        return
    p = edge.interpolate(0.5, normalized=True)
    a, b = edge.coords
    north_face = b[0] < a[0] and p.y > -165
    west_or_east_long = abs(b[1] - a[1]) > 12 and (
        (118 < p.x < 130) or (166 < p.x < 181.5)
    )
    metal = north_face or west_or_east_long
    count = max(1, round(length / (2.46 if metal else 2.88)))
    step = length / count
    if step < 1.31:
        return
    for i in range(count):
        x = (i + 0.5) * step
        left, right = x - step * 0.28, x + step * 0.28
        pier = metal and (i // 6) % 5 != 4
        if pier:
            for j in range(3):
                u = x - step * 0.461 + j * step * 0.305
                panel = METAL[(j + i * 3) % len(METAL)]
                add(u, u + step * 0.286, 0.009, 0.107, floor + 0.035, top - 0.19, panel)
        for level in range(6):
            z = floor + 1.0 + level * 3.12
            if z + 1.80 >= top - 0.17:
                break
            sill = DARK if pier else METAL[1]
            add(left - 0.045, right + 0.045, 0.079, 0.178, z - 0.36, z - 0.042, sill)
            add(left - 0.04, right + 0.04, 0.069, 0.171, z - 0.04, z + 1.79, DARKER)
            add(
                left + 0.04,
                right - 0.037,
                0.174,
                0.198,
                z + 0.016,
                z + 1.70,
                GLASS if (i + level) % 4 else REFLECTION,
            )
            if pier:
                add(x - 0.026, x + 0.026, 0.195, 0.231, z + 0.012, z + 1.714, FRAME)
        if not outer and pier:
            add(
                right + 0.088,
                right + 0.125,
                0.095,
                0.16,
                floor + 0.21,
                top - 0.31,
                DARK,
            )
    add(0.01, length - 0.01, 0.01, 0.105, top - 0.16, top - 0.028, COPING)


def wall_details(parts, plan, regions, field, gates, bean, upper_base):
    # A millimetre-rounded roof cut can separate a shared wall edge from its zone.
    # Buffer the lookup areas so details follow the registered wall centreline.
    spans = [
        (p.buffer(0.008), lambda e, n, top=top: top, kind) for p, top, kind in regions
    ]
    for ring in (plan.exterior, *plan.interiors):
        outer = ring == plan.exterior
        q = list(ring.coords)
        for start, end in zip(q, q[1:]):
            for a, b, height, kind in site.science.face_spans(
                start,
                end,
                spans,
            ):
                edge = LineString((a, b))
                length, add = tools.face(parts, a, b)
                if length < 0.32:
                    continue
                p = edge.interpolate(0.5, normalized=True)
                z = geometry.sample_ground(field, p.x, p.y)
                top = height(p.x, p.y)
                gate = next(
                    (
                        entry
                        for entry in gates
                        if edge.distance(Point(entry["position_enu_m"])) < 0.007
                    ),
                    None,
                )
                if bean:
                    bean_face(add, edge, kind, top, z, gate, not outer)
                else:
                    unthank_base(add, edge, top, z, gate)
                    if kind == "upper":
                        unthank_upper(add, edge, top, upper_base, outer)

    # Detail the exposed walls above adjoining lower roofs.
    for area, top, kind in regions:
        if kind not in ("dorm", "upper"):
            continue
        ring = list(orient(area).exterior.coords)
        for a, b in zip(ring, ring[1:]):
            edge = LineString((a, b))
            if (
                edge.length < 1.3
                or edge.interpolate(0.5, normalized=True).distance(plan.boundary) < 0.14
            ):
                continue
            midpoint = np.asarray(edge.interpolate(0.5, normalized=True).coords[0])
            direction = (np.asarray(b) - a) / edge.length
            across = Point(midpoint + 0.025 * np.array((direction[1], -direction[0])))
            neighbor = next((z for poly, z, _ in regions if poly.covers(across)), None)
            if neighbor is None or neighbor > top - 0.4:
                continue
            _, add = tools.face(parts, a, b)
            if bean:
                ground = geometry.sample_ground(field, *midpoint)
                bean_face(add, edge, kind, top, ground, None, False, neighbor)
            else:
                unthank_upper(add, edge, top, upper_base, False)


def roof_details(parts, model, regions, bean):
    for w, s, e, n in model["roof_plant"]:
        island = box(w, s, e, n)
        point = island.centroid
        z = next((top for a, top, _ in regions if a.covers(point)), None)
        if z is None:
            continue
        site.flat(parts, island, z + 0.02, z + 0.20, COPING)
        for y in np.arange(s + 0.65, n - 0.9, 2.94):
            device = box(w + 0.49, y, e - 0.42, min(n - 0.37, y + 1.47))
            site.flat(
                parts,
                device,
                z + 0.17,
                z + (0.54 if bean else 0.67),
                METAL[0],
                METAL[2],
            )
    if not bean:
        for w, s, e, n in model["atrium_glazing"]:
            outline = box(w, s, e, n)
            site.flat(
                parts, outline.buffer(0.14, join_style="mitre"), 9.66, 9.91, COPING
            )
            site.flat(parts, outline, 9.90, 10.07, FRAME, GLASS)
            for y in np.arange(s + 0.37, n, 0.77):
                site.flat(parts, box(w, y, e, y + 0.064), 10.055, 10.103, FRAME)


def canopy(parts, model, field):
    supports = []
    for x, y in model["entry_posts"]:
        pier = box(x - 0.13, y - 0.13, x + 0.13, y + 0.13)
        z = geometry.sample_ground(field, x, y)
        site.flat(parts, pier, z - 0.13, 6.76, DARK)
        supports.append(pier)
    shape = Polygon(model["north_canopy"])
    holes = shapely.union_all(
        [
            Point(x, y).buffer(0.49, quad_segs=6)
            for x, y in ((160.52, -145.75), (162.49, -146.1), (164.41, -146.5))
        ]
    )
    roof = clean(shape.difference(holes))
    site.flat(parts, roof, 6.69, 6.85, WARM)
    site.flat(parts, roof, 6.85, 7.06, DARKER, COPING)
    terrace = Polygon(model["terrace_canopy"])
    site.flat(parts, terrace, 6.69, 6.83, WARM)
    site.flat(parts, terrace, 6.83, 7.12, DARKER)
    return supports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    lands, paths, records, meshes, plans, supports, gates, zone_stats = (
        [],
        [],
        [],
        {},
        [],
        [],
        [],
        {},
    )
    for model in data["models"]:
        id = model["id"]
        bean = model["campus_id"] == "068"
        holes = model["footprint_holes_enu_m"]
        plan = orient(clean(Polygon(model["footprint_enu_m"], holes)))
        assert plan.is_valid and plan.geom_type == "Polygon"
        floor = (
            min(
                geometry.sample_ground(field, *plan.exterior.interpolate(d).coords[0])
                for d in np.arange(0, plan.exterior.length, 0.73)
            )
            - 0.39
        )
        entries, parts, posts = [], [], []
        for item in model["entries"]:
            assert plan.boundary.distance(Point(item["position_enu_m"])) < 0.002
            entry, paving = site.approach(lands, field, item)
            entries.append(entry)
            paths.append(dict(outline=list(paving.exterior.coords), rgb=PAVING))
        regions = roof_zones(parts, plan, model, floor, bean)
        wall_details(parts, plan, regions, field, entries, bean, 7.17)
        roof_details(parts, model, regions, bean)
        if bean:
            lawn = clean(
                shapely.union_all(
                    [
                        Polygon(r).buffer(-2.8, join_style="mitre")
                        for r in plan.interiors
                    ]
                )
            )
            lawn = lawn.difference(
                shapely.union_all([Polygon(q) for q in model["court_paving"]])
            )
            for piece in geometry.sections(lawn):
                paths.append(
                    dict(outline=list(piece.exterior.coords), rgb=(145, 162, 115))
                )
            for outline in model["court_paving"]:
                paths.append(dict(outline=outline, rgb=PAVING))
        else:
            posts = canopy(parts, model, field)
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        meshes[id] = shared.shared.shared.shared.index_mesh(mesh)
        zone_stats[id] = [
            (kind, round(area.area, 2), top) for area, top, kind in regions
        ]
        records.append(
            {k: model[k] for k in ("id", "name", "campus_id")}
            | dict(
                footprint_enu_m=list(plan.exterior.coords)[:-1],
                footprint_holes_enu_m=[list(r.coords)[:-1] for r in plan.interiors],
                support_collision_enu_m=[
                    list(p.exterior.coords)[:-1] for p in posts if not plan.covers(p)
                ],
                area_m2=round(plan.area, 3),
                base_z_m=round(floor, 4),
                roof_z_m=round(float(mesh.bounds[1, 1]), 4),
                entrances=entries,
            )
        )
        gates.extend(entries)
        plans.append(plan)
        supports.extend(posts)
    assert plans[0].distance(plans[1]) > 9.6
    combined = shapely.union_all(plans)
    old = shapely.union_all(
        [
            Polygon(b["footprint_enu_m"]).buffer(0)
            for b in manifest["buildings"]
            if b["id"] in meshes
        ]
    )
    count, clearance = shared.shared.check_routes(
        plans, supports, gates, old, manifest, graph, config, set(meshes)
    )
    lands.append(tools.approaches(paths, field, combined))
    out = SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    ground = trimesh.util.concatenate(lands)
    site.memorial.gerlinger.export(glb, meshes, ground, GROUND, "bean-unthank-paving")
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
    config["bean_unthank_site"] = dict(
        url=f"{DIRECTORY}/site.json", sha256=tools.digest(descriptor)
    )
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit = dict(
        footprint_m2={r["id"]: r["area_m2"] for r in records},
        court_m2=[round(Polygon(r).area, 3) for r in plans[0].interiors],
        gap_m=round(plans[0].distance(plans[1]), 3),
        route_edges=count,
        closest_route_m=round(clearance, 3),
        zones=zone_stats,
        triangles={id: len(mesh.faces) for id, mesh in meshes.items()},
        entrances={r["id"]: r["entrances"] for r in records},
        glb_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
