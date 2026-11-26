# SPDX-License-Identifier: Apache-2.0
"""Rebuild Straub and Earl around the registered exterior and expansion."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-lawrence-science-site-review.py")
loader = spec_from_file_location(source.stem, source)
science = module_from_spec(loader)
loader.loader.exec_module(science)
allen, tools, geometry, memorial = (
    science.allen,
    science.tools,
    science.geometry,
    science.memorial,
)
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/straub-earl-site-review.json"
DIRECTORY = "straub-earl-review"
GROUND = "straub-earl-approaches"
flat, surface = science.flat, science.surface
BRICK = (150, 84, 67)
DARK_BRICK = (121, 69, 55)
EARL_BRICK = (159, 90, 68)
TRIM = (207, 188, 165)
STUCCO = (190, 174, 147)
ROOF = (126, 128, 121)
MEMBRANE = (168, 165, 151)
PANEL = (112, 130, 138)
RIB = (133, 149, 155)
GLASS = (58, 91, 105)
FRAME = (160, 159, 152)
PAVING = (164, 157, 148)


def earth_profile(parts, region, zone, base, wall):
    axis = 0 if zone["axis"] == "easting" else 1
    p0, p1 = zone["bounds"][axis::2]
    mid, peak, eave = zone["ridge"], zone["ridge_z_m"], zone["eave_z_m"]
    end_eave = zone.get("end_eave_z_m", eave)

    def height(e, n):
        v = (e, n)[axis]
        run = mid - p0 if v < mid else p1 - mid
        edge = eave if v < mid else end_eave
        return peak - (peak - edge) * min(1, abs(v - mid) / run)

    other = region.bounds
    if axis == 0:
        a = box(other[0] - 1, other[1] - 1, mid, other[3] + 1)
        b = box(mid, other[1] - 1, other[2] + 1, other[3] + 1)
    else:
        a = box(other[0] - 1, other[1] - 1, other[2] + 1, mid)
        b = box(other[0] - 1, mid, other[2] + 1, other[3] + 1)
    for flank in (a, b):
        surface(parts, region.intersection(flank), base, height, wall, ROOF)
    return height


def volumes(parts, plan, model, base, brick):
    rest = plan
    regions = []
    for zone in model["roof_sections"]:
        area = rest.intersection(box(*zone["bounds"]))
        assert area.area > 0.6, zone["name"]
        rest = rest.difference(area)
        kind = zone["kind"]
        if "ridge" in zone:
            height = earth_profile(parts, area, zone, base, brick)
        elif "east_height" in zone:
            west, _, east, _ = zone["bounds"]
            west_z, east_z = zone["height"], zone["east_height"]

            def height(e, n, start=west, length=east - west, z0=west_z, z1=east_z):
                return z0 + (z1 - z0) * (e - start) / length

            surface(parts, area, base, height, brick, MEMBRANE)
            rim = area.difference(area.buffer(-0.18, join_style="mitre"))
            surface(
                parts,
                rim,
                min(west_z, east_z) - 0.08,
                lambda e, n: height(e, n) + 0.19,
                brick,
                TRIM,
            )
        else:
            top = zone["height"]
            height = lambda e, n, top=top: top
            flat(parts, area, base, top, brick, MEMBRANE)
            rim = area.difference(area.buffer(-0.18, join_style="mitre"))
            flat(parts, rim, top - 0.09, top + 0.20, brick, TRIM)
        regions.append((area, height, kind))
    assert rest.area < 0.001, rest.area
    return regions


def rectangular_window(add, center, width, low, high, bays):
    left, right = center - width / 2, center + width / 2
    add(left - 0.08, right + 0.08, 0.015, 0.120, low - 0.10, high + 0.12, TRIM)
    allen.windows(add, left, right, low, high, bays)
    add(left - 0.12, right + 0.12, 0.09, 0.238, low - 0.095, low - 0.018, TRIM)


def historic_bays(add, length, base, top, omitted=None):
    for z in (5.27, 8.20, 11.28, 14.09):
        if z + 0.94 >= top - 0.11 or length < 1.52:
            continue
        count = max(1, round(length / 2.38))
        step = length / count
        for i in range(count):
            center = step * (i + 0.5)
            if omitted is not None and abs(center - omitted) < 3.7 and z < 7:
                continue
            full = z < 13.5
            rectangular_window(
                add, center, min(1.32, step * 0.62), z, z + (1.78 if full else 0.92), 2
            )
    for lo, hi, color in [
        (base + 0.6, 4.69, DARK_BRICK),
        (10.99, 11.09, TRIM),
        (13.72, 13.91, TRIM),
        (13.94, 15.23, STUCCO),
    ]:
        if hi < top:
            add(0, length, 0.002, 0.062, lo, hi, color)
    if top > 15.4:
        add(0, length, 0.04, 0.19, 15.20, 15.36, TRIM)


def entry_bay(parts, a, b, add, center, gate, historic):
    floor = gate["threshold_z_m"]
    if historic:
        arch = memorial.museum.arch
        profile = tools.load_builder("build-heritage-core-site-review.py").profile
        for i, x in enumerate((center - 2.07, center, center + 2.07)):
            span = 1.65 if i == 1 else 1.40
            inner = arch(x, span, floor, floor + 2.25, span / 2)
            outer = arch(x, span + 0.32, floor - 0.03, floor + 2.27, span / 2 + 0.18)
            profile(parts, a, b, inner, 0.29, (53, 54, 46))
            profile(parts, a, b, outer.difference(inner), 0.39, TRIM)
            add(
                x - span * 0.36,
                x + span * 0.36,
                0.281,
                0.321,
                floor + 0.1,
                floor + 2.09,
                (80, 69, 50),
            )
            for left, right in (
                (x - span * 0.29, x - 0.044),
                (x + 0.044, x + span * 0.29),
            ):
                add(left, right, 0.323, 0.337, floor + 0.72, floor + 2.06, GLASS)
        add(center - 3.62, center + 3.62, 0.065, 0.55, floor + 3.39, floor + 3.71, TRIM)
        add(center - 3.58, center + 3.58, 0.12, 0.47, floor + 3.80, floor + 4.18, TRIM)
        for x in (center - 3.36, center + 3.36):
            for z in np.arange(floor + 0.35, floor + 3.52, 0.42):
                add(x - 0.22, x + 0.22, 0.058, 0.38, z, z + 0.19, TRIM)
        left, right, spring, peak = center - 5.26, center + 5.26, 15.18, 18.36
        pediment = Polygon([(left, spring), (right, spring), (center, peak)])
        inset = pediment.buffer(-0.17, join_style="mitre")
        profile(parts, a, b, pediment, 0.077, BRICK)
        profile(parts, a, b, pediment.difference(inset), 0.218, TRIM)
        oculus = Point(center, 16.93).buffer(0.43, quad_segs=8)
        profile(parts, a, b, oculus, 0.095, TRIM)
        profile(parts, a, b, oculus.buffer(-0.092), 0.12, (72, 67, 55))
        add(center - 0.38, center + 0.38, 0.089, 0.144, 15.2, 16.18, TRIM)
        return
    allen.doors(add, center, gate["width_m"], floor)
    if gate["gate"] == "straub-north":
        width = min(
            1.87, center - 0.03, np.linalg.norm(np.subtract(a, b)) - center - 0.03
        )
        if width > 1.1:
            allen.windows(
                add, center - width, center + width, floor + 2.47, 11.73, 4, True
            )
            for z in (5.36, 8.67, 11.84):
                add(center - width, center + width, 0.13, 0.33, z, z + 0.16, FRAME)


def earl_bays(add, length, base, roof, skip=None):
    if length < 1.85:
        return
    count = max(1, round(length / 2.68))
    step = length / count
    for row, lower in enumerate((3.68, 6.50, 9.04, 11.56)):
        high = lower + (1.35 if row == 0 else 1.52)
        if high > roof - 0.32:
            continue
        if row:
            add(0.24, length - 0.24, 0.013, 0.082, lower - 0.91, high + 0.047, PANEL)
            for line in np.arange(0.34, length - 0.30, 0.26):
                add(line, line + 0.022, 0.076, 0.114, lower - 0.87, lower - 0.056, RIB)
        for i in range(count):
            center = (i + 0.5) * step
            if skip is not None and row == 0 and abs(skip - center) < 1.52:
                continue
            rectangular_window(
                add,
                center,
                step * (0.55 if row == 0 else 0.74),
                lower,
                high,
                2 if row == 0 else 3,
            )
    add(0.12, length - 0.12, 0.035, 0.18, roof - 0.20, roof - 0.048, TRIM)


def expansion_bays(add, length, base, roof, skip=None):
    for z in (6.39, 8.72, 11.27):
        if z > roof - 1 or length < 2.7:
            continue
        add(0, length, 0.009, 0.086, z, z + 0.09, TRIM)
        count = max(1, round(length / 3.75))
        for i in range(count):
            x = (i + 0.5) * length / count
            if skip is None or abs(skip - x) > 2.75:
                w = min(1.22, length / (count * 2) - 0.14)
                allen.windows(
                    add, x - w, x + w, z + 0.14, min(z + 1.30, roof - 0.15), 3, True
                )


def elevations(parts, plan, regions, gates, base):
    for a, b in zip(plan.exterior.coords, list(plan.exterior.coords)[1:]):
        for c, d, height, kind in science.face_spans(a, b, regions):
            length, add = tools.face(parts, c, d)
            mid = np.add(c, d) * 0.5
            top = height(*mid)
            segment = LineString((c, d))
            gate = next(
                (
                    g
                    for g in gates
                    if segment.distance(Point(g["position_enu_m"])) < 0.002
                ),
                None,
            )
            center = (
                None
                if not gate
                else float(np.linalg.norm(np.subtract(gate["position_enu_m"], c)))
            )
            if kind == "historic":
                historic_bays(add, length, base, top, center)
            elif kind == "earl":
                earl_bays(add, length, base, top, center)
            else:
                expansion_bays(add, length, base, top, center)
            if gate:
                entry_bay(parts, c, d, add, center, gate, gate["gate"] == "straub-west")


def rooftops(parts, name, model):
    for e0, n0, e1, n1, floor, top, kind in model["roof_items"]:
        area = box(e0, n0, e1, n1)
        wall, cap = (DARK_BRICK, TRIM) if kind == "chimney" else (PANEL, FRAME)
        flat(parts, area, floor, top, wall, cap)
    if name != "straub":
        return
    e, n = model["entrances"][0]["position_enu_m"]
    bounds = [e - 0.08, n - 5.26, e + 3.35, n + 5.26]
    earth_profile(
        parts,
        box(*bounds),
        {
            "axis": "northing",
            "bounds": bounds,
            "ridge": n,
            "ridge_z_m": 18.36,
            "eave_z_m": 15.18,
        },
        15.06,
        BRICK,
    )
    for n in model["west_dormers"]:
        foot = box(-191.36, n - 0.63, -189.63, n + 0.63)
        for a, b in ((n - 0.63, n), (n, n + 0.63)):
            surface(
                parts,
                foot.intersection(box(-192, a, -189, b)),
                16.38,
                lambda e, y: 18.16 - abs(y - n) * 0.68,
                STUCCO,
                ROOF,
            )
        _, add = tools.face(parts, (-191.37, n + 0.63), (-191.37, n - 0.63))
        allen.windows(add, 0.24, 1.02, 17.02, 17.67, 2)


def approach(grounds, field, gate):
    e, n = gate["position_enu_m"]
    radians = np.deg2rad(gate["outward_degrees"])
    outward = np.array((np.sin(radians), np.cos(radians)))
    tangent = np.array((outward[1], -outward[0]))
    anchor = np.array([e, n])
    run, rise = gate["landing_m"], gate["rise_m"]
    width = gate["width_m"] * 0.5 + 0.48

    def patch(start, end):
        return Polygon(
            [
                anchor + outward * s + tangent * t
                for s, t in (
                    (start, -width),
                    (end, -width),
                    (end, width),
                    (start, width),
                )
            ]
        )

    toe = geometry.sample_ground(field, *(anchor + outward * run))
    surface(
        grounds,
        patch(-0.017, run),
        toe - 0.42,
        lambda x, y: toe
        + max(0, 1 - np.dot(np.array([x, y]) - anchor, outward) / run) * rise
        + 0.027,
        PAVING,
        PAVING,
    )
    return gate | {"threshold_z_m": round(float(toe + rise + 0.027), 3)}, patch(
        run - 0.05, gate["approach_distance_m"] + 0.9
    )


def build(spec, manifest, field, graph):
    meshes, records, paths, grounds, plans = {}, [], [], [], []
    for name in ("straub", "earl"):
        model = spec[name]
        id = model["id"]
        plan = orient(Polygon(model["footprint_enu_m"]))
        assert plan.is_valid
        perimeter = plan.exterior
        base = (
            min(
                geometry.sample_ground(
                    field, *perimeter.interpolate(distance).coords[0]
                )
                for distance in np.arange(0, perimeter.length, 0.55)
            )
            - 0.48
        )
        parts, entries = [], []
        for gate in model["entrances"]:
            assert perimeter.distance(Point(gate["position_enu_m"])) < 0.002
            entry, paving = approach(grounds, field, gate)
            entries.append(entry)
            paths.append(paving)
        regions = volumes(
            parts, plan, model, base, BRICK if name == "straub" else EARL_BRICK
        )
        elevations(parts, plan, regions, entries, base)
        rooftops(parts, name, model)
        if name == "earl":
            join = box(*spec["classroom_join"]["bounds"])
            assert join.difference(plan.buffer(0.13)).area < 1
            flat(
                parts,
                join,
                spec["classroom_join"]["bottom"],
                spec["classroom_join"]["top"],
                EARL_BRICK,
                MEMBRANE,
            )
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        meshes[id] = mesh
        plans.append(plan)
        records.append(
            dict(
                id=id,
                footprint_enu_m=model["footprint_enu_m"],
                area_m2=round(plan.area, 2),
                base_z_m=round(base, 4),
                roof_z_m=round(float(mesh.bounds[1, 1]), 4),
                entrances=entries,
            )
        )
    assert plans[0].intersection(plans[1]).area < 0.001
    union = shapely.union_all(plans)
    changed = set(meshes) | {a["id"] for a in spec["absorbed_batches"]}
    sources = {
        b["id"]: Polygon(b["footprint_enu_m"]).buffer(0) for b in manifest["buildings"]
    }
    old = shapely.union_all([sources[id] for id in changed])
    conflicts = []
    for i, (a, b, *_) in enumerate(graph["edges"]):
        edge = LineString([graph["nodes_enu_m"][a], graph["nodes_enu_m"][b]])
        if edge.distance(union) < 0.42 <= edge.distance(old):
            conflicts.append(i)
    for entry in (g for row in records for g in row["entrances"]):
        e, n = entry["position_enu_m"]
        radians = np.deg2rad(entry["outward_degrees"])
        reach = entry["approach_distance_m"]
        assert (
            union.distance(
                Point(e + np.sin(radians) * reach, n + np.cos(radians) * reach)
            )
            > 0.53
        ), entry["gate"]
    assert not conflicts, conflicts
    overlap = {
        id: round(union.intersection(p).area, 3)
        for id, p in sources.items()
        if id not in changed and union.intersection(p).area > 0.02
    }
    assert not overlap, overlap
    paving = tools.approaches(
        [{"outline": list(p.exterior.coords), "rgb": PAVING} for p in paths],
        field,
        union,
    )
    ground = trimesh.util.concatenate([*grounds, paving])
    return (
        records,
        meshes,
        ground,
        dict(
            route_edges=len(graph["edges"]),
            new_conflicts=conflicts,
            footprints={row["id"]: row["area_m2"] for row in records},
        ),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    field = SCENE / manifest["heightfield_url"]
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    buildings, models, ground, audit = build(
        spec, manifest, json.loads(field.read_bytes()), graph
    )
    appearances = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    source = tools.load_builder("build-frohnmayer-exterior-review.py")
    removals = source.source_removals(spec, config, appearances)
    out = SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    memorial.gerlinger.export(glb, models, ground, GROUND, "straub-earl-paving")
    descriptor = out / "site.json"
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field),
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        ground_node=GROUND,
        buildings=buildings,
        absorbed_ids=[r["id"] for r in removals],
        batch_removals=removals,
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    config["straub_earl_site"] = {
        "url": f"{DIRECTORY}/site.json",
        "sha256": tools.digest(descriptor),
    }
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    audit.update(
        model_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
        triangles={k: len(v.faces) for k, v in models.items()}
        | {GROUND: len(ground.faces)},
    )
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
