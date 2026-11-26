# SPDX-License-Identifier: Apache-2.0
"""Export registered Oregon Hall and Jaqua exteriors with their approaches."""

import argparse
from importlib import import_module
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-carson-llc-site-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)
geometry, site, tools = shared.geometry, shared.site, shared.tools
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/oregon-jaqua-site-review.json"
site_planting = import_module("build-site-planting").site_planting
DIRECTORY = "oregon-jaqua-review"
GROUND = "oregon-jaqua-grounds"

BRICK = (162, 105, 79)
BRICK_DARK = (133, 81, 62)
BRICK_LIGHT = (171, 114, 85)
BROWN = (116, 91, 72)
GLASS = (63, 88, 94)
DARK = (65, 75, 72)
METAL = (131, 143, 139)
ALUMINUM = (185, 198, 194)
PALE = (198, 200, 186)
SLATE = (111, 120, 121)
CONCRETE = (157, 150, 136)
PAVING = (173, 165, 148)
LIME = (135, 149, 104)
WATER = (63, 100, 103)


def ring(poly):
    return list(orient(poly).exterior.coords)[:-1]


def union(parts):
    return shapely.union_all(parts).buffer(0)


def flat(parts, shape, bottom, top, wall, roof=None):
    if not shape.is_empty:
        site.flat(parts, shape, bottom, top, wall, roof)


def parapet(out, area, roof, top, face, cap, width=0.28):
    edge = area.difference(area.buffer(-width, join_style="mitre"))
    flat(out, edge, roof - 0.025, top, face)
    flat(out, edge, top - 0.022, top + 0.06, face, cap)


def rails(add, start, end, inset, base):
    for z in (base + 0.10, base + 0.94):
        add(start, end, inset, inset + 0.055, z, z + 0.047, DARK)
    for x in np.linspace(start + 0.035, end - 0.035, max(2, int((end - start) / 0.16))):
        add(
            x - 0.017,
            x + 0.017,
            inset + 0.009,
            inset + 0.044,
            base + 0.10,
            base + 0.97,
            DARK,
        )


def ribbon(add, a, b, z, top, outside=0.038, count=6, glass=GLASS):
    add(a - 0.068, b + 0.068, outside - 0.016, outside, z - 0.073, top + 0.082, DARK)
    for i in range(count):
        l, r = a + i * (b - a) / count, a + (i + 1) * (b - a) / count
        add(l + 0.023, r - 0.023, outside, outside + 0.014, z, top, glass)
    add(
        a - 0.085,
        b + 0.085,
        outside - 0.024,
        outside + 0.105,
        z - 0.11,
        z - 0.057,
        BROWN,
    )


def levels(parts, area, stories, base, top, skip=()):
    for a, b in zip(ring(area), ring(area)[1:] + ring(area)[:1]):
        if any(s(a, b) for s in skip):
            continue
        length, add = tools.face(parts, a, b)
        if length < 1.0:
            continue
        count = max(1, round((length - 0.6) / 5.5))
        spacing = (length - 0.38) / count
        for level in range(stories):
            z = base + 0.67 + level * 3.76
            hi = min(z + 1.45, top - 0.39)
            if hi < z + 0.43:
                break
            for i in range(count):
                low, high = 0.47 + i * spacing, 0.08 + (i + 1) * spacing
                if high > low + 0.32:
                    ribbon(add, low, high, z, hi, count=6 if spacing > 2.2 else 2)
        for z in np.arange(base + 0.52, top - 0.2, 3.76):
            add(0.01, length - 0.01, -0.008, 0.023, z, z + 0.052, BRICK_DARK)


def recessed_front(parts, config, entries, field, floor):
    a = config["arcade"]
    start, end = a["start_e"], a["end_e"]
    south, inner, balcony = a["outer_n"], a["inner_n"], a["balcony_inner_n"]
    datum = entries["oregon-south"]["threshold_z_m"]
    span, length = np.array((start, end)), end - start
    lower_ceiling, balcony_floor, balcony_top = datum + 3.39, datum + 3.92, datum + 6.73
    flat(
        parts,
        box(start, south, end, inner),
        lower_ceiling,
        balcony_floor,
        BRICK,
        CONCRETE,
    )
    flat(parts, box(start, south, end, inner), balcony_top, datum + 7.4, BRICK)
    flat(parts, box(start, south, end, balcony), datum + 7.40, 12.77, BRICK, PALE)
    flat(
        parts,
        box(start, balcony, end, inner),
        balcony_floor - 0.02,
        balcony_top,
        BRICK_DARK,
    )
    stands = []
    for e in a["pier_edges_e"]:
        column = box(e - 0.27, south + 0.11, e + 0.27, south + 0.81)
        flat(parts, column, floor, 9.07, BRICK_LIGHT)
        stands.append(column)
        upper = box(e - 0.28, south + 0.05, e + 0.28, balcony + 0.06)
        flat(parts, upper, balcony_floor, balcony_top, BRICK_LIGHT)
    _, outer = tools.face(parts, (start, south), (end, south))
    _, lower = tools.face(parts, (start, inner), (end, inner))
    _, upper = tools.face(parts, (start, balcony), (end, balcony))
    piers = np.array(a["pier_edges_e"]) - span[0]
    for left, right in zip(piers[:-1] + 0.29, piers[1:] - 0.29):
        ribbon(outer, left + 0.14, right - 0.14, datum + 8.14, datum + 9.84)
        ribbon(
            upper, left + 0.09, right - 0.09, balcony_floor + 0.30, balcony_top - 0.17
        )
        ribbon(lower, left, right, datum + 0.03, lower_ceiling - 0.19, count=7)
        rails(outer, left, right, -0.17, balcony_floor)
    gate = entries["oregon-south"]
    site.allen.doors(lower, gate["position_enu_m"][0] - start, gate["width_m"], datum)
    outer(0, length, -0.014, 0.13, 12.59, 12.82, BRICK_DARK)
    landing = box(start, south - 0.28, end, inner)
    grounds = tools.approaches(
        [{"outline": ring(landing), "rgb": PAVING}], field, union(stands)
    )
    return stands, grounds


def oregon(parts, ground, spec, entries, field, floor):
    zones = [(r, box(*r["bounds"])) for r in spec["roof_regions"]]
    envelope = union([p for _, p in zones])
    front = spec["arcade"]
    arcade = box(front["start_e"], front["outer_n"], front["end_e"], front["inner_n"])
    base = entries["oregon-south"]["threshold_z_m"]
    for region, area in zones:
        name, deck = region["name"], region["deck"]
        main = area.difference(arcade) if name == "west-core" else area
        low = 8.42 if name == "west-stair-head" else floor
        flat(parts, main, low, deck, BRICK, PALE if "west" in name else SLATE)
        parapet(parts, area, deck, region["parapet"], BRICK_LIGHT, CONCRETE)
        skip = ()
        if name == "west-core":
            skip = (lambda a, b: a[1] == b[1] == front["outer_n"],)
        levels(parts, area, region["stories"], base, deck, skip)
        if name in ("west-stair", "entry-tower"):
            west, south, east, north = area.bounds
            _, add = tools.face(parts, (west, south), (east, south))
            for low_z in np.arange(base + 0.02, min(deck - 2.5, 15.0), 3.76):
                if name == "entry-tower":
                    ribbon(
                        add,
                        (east - west) * 0.43,
                        (east - west) * 0.77,
                        low_z + 0.34,
                        low_z + 3.02,
                        count=2,
                        outside=0.13,
                    )
            gate = entries["oregon-west" if name == "west-stair" else "oregon-link"]
            x = gate["position_enu_m"][0] - west
            site.allen.doors(add, x, gate["width_m"], gate["threshold_z_m"])
    piers, apron = recessed_front(parts, spec, entries, field, floor)
    ground.append(apron)
    w, _, e, n = zones[1][1].bounds
    length, terrace = tools.face(parts, (e, n), (w, n))
    rails(terrace, 0.19, length - 0.19, -0.04, 8.67)
    for a, b, c, d, z in spec["equipment"]:
        area = box(a, b, c, d)
        deck = next(region["deck"] for region, p in zones if p.covers(area.centroid))
        flat(parts, area, deck, z - 0.09, SLATE, PALE)
        flat(parts, area.buffer(0.073, join_style="mitre"), z - 0.09, z, METAL, PALE)
        width, intake = tools.face(parts, (a, b), (c, b))
        for y in np.linspace(deck + 0.16, z - 0.17, 5):
            intake(0.16, width - 0.16, 0.016, 0.066, y, y + 0.033, DARK)
    supported = envelope.difference(arcade.buffer(0.021))
    planter = box(*spec["planter"])
    flat(ground, planter, floor, 1.07, CONCRETE)
    flat(ground, planter.buffer(-0.22, join_style="mitre"), 1.05, 1.13, CONCRETE, LIME)
    paths = union(
        [LineString(coords).buffer(1.10, quad_segs=4) for coords in spec["walks"]]
    )
    add_paths(ground, field, paths, union([supported, planter]), PAVING)
    return envelope, supported, [*piers, planter]


def add_paths(parts, field, paths, blocked, color):
    exposed = paths.difference(blocked)
    outlines = [
        {"outline": ring(piece), "rgb": color}
        for piece in geometry.sections(exposed)
        if piece.area > 0.1
    ]
    if outlines:
        parts.append(tools.approaches(outlines, field, blocked))


def jaqua(parts, ground, spec, entries, field, floor):
    west, south, east, north = spec["bounds"]
    deck, halo = spec["deck_z"], spec["top_frame_z"]
    envelope = box(west, south, east, north)
    inner = envelope.buffer(-1.19, join_style="mitre")
    frame_inset = 2.34
    frame_top = envelope.buffer(-frame_inset, join_style="mitre")
    top_ring = envelope.difference(envelope.buffer(-2.49, join_style="mitre"))
    flat(parts, inner, floor, deck, (92, 104, 103), PALE)
    flat(parts, top_ring, deck - 0.18, deck + 0.06, SLATE, PALE)
    frames = [
        (a, b) for a, b in zip(ring(envelope), ring(envelope)[1:] + ring(envelope)[:1])
    ]
    datum = entries["jaqua-south"]["threshold_z_m"]
    bands = [datum, 4.72, 8.59, deck, halo]
    for a, b in frames:
        length, outer = tools.face(parts, a, b)
        unit = (np.array(b) - a) / length
        width = length / 25
        direction = (
            "south" if a[1] == b[1] == south else "west" if a[0] == b[0] == west else ""
        )
        door = entries.get(f"jaqua-{direction}")
        center = np.dot(np.array(door["position_enu_m"]) - a, unit) if door else -10
        half = door["width_m"] / 2 if door else 0
        for row, (low, high) in enumerate(zip(bands, bands[1:])):
            if row == 3:
                continue
            for i in range(25):
                left, right = i * width + 0.025, (i + 1) * width - 0.025
                mixes = (
                    (95, 130, 129),
                    (80, 112, 117),
                    (107, 137, 134),
                    (86, 122, 124),
                    (113, 147, 143),
                )
                color = mixes[(i * 3 + row * 2) % len(mixes)]
                outer(left, right, -0.192, -0.136, low + 0.06, high - 0.074, color)
                z = high - (0.73 if row else 0.65)
                outer(left, right, -0.129, -0.105, z, z + 0.045, (127, 156, 152))
                for louver in np.linspace(high - 0.57, high - 0.16, 6):
                    outer(
                        left + 0.05,
                        right - 0.05,
                        -0.104,
                        -0.08,
                        louver,
                        louver + 0.014,
                        METAL,
                    )
        for i, u in enumerate(np.linspace(0, length, 26)):
            if center - half < u < center + half:
                low = datum + 2.78
            else:
                low = datum - 0.07
            half_width = 0.064 if i % 5 == 0 else 0.039
            outer(
                max(0, u - half_width),
                min(length, u + half_width),
                -0.069,
                0.07,
                low,
                halo,
                ALUMINUM,
            )
            if frame_inset < u < length - frame_inset:
                p = np.array(a) + u * unit
                q = p + np.array((-unit[1], unit[0])) * frame_inset
                tools.beam(
                    parts, (*p, halo - 0.027), (*q, halo - 0.027), 0.073, ALUMINUM
                )
            if i % 5 == 0 and frame_inset < u < length - frame_inset:
                tools.beam(parts, (*p, deck + 0.10), (*q, halo - 0.11), 0.046, METAL)
                tools.beam(parts, (*q, deck), (*q, halo - 0.06), 0.061, METAL)
        for z in [*bands[:-1], 13.88, halo - 0.11]:
            outer(0, length, -0.097, 0.073, z, z + 0.092, ALUMINUM)
        if door:
            threshold = door["threshold_z_m"]
            outer(
                center - half - 0.15,
                center + half + 0.15,
                -0.065,
                0.15,
                threshold + 2.58,
                threshold + 2.80,
                ALUMINUM,
            )
            site.allen.doors(outer, center, door["width_m"], threshold)
    for a, b in zip(frame_top.exterior.coords, list(frame_top.exterior.coords)[1:]):
        tools.beam(parts, (*a, halo - 0.027), (*b, halo - 0.027), 0.081, ALUMINUM)
        corner = min(ring(envelope), key=lambda p: Point(p).distance(Point(a)))
        tools.beam(parts, (*corner, halo - 0.027), (*a, halo - 0.027), 0.073, ALUMINUM)
    parapet(parts, inner, deck, deck + 0.25, PALE, METAL, 0.34)
    for a, b, c, d, z in spec["roof_pieces"]:
        area = box(a, b, c, d)
        flat(parts, area, deck, z, SLATE, PALE if c - a > 4 else (136, 167, 162))
        if c - a < 4 and d - b > 10:
            for y in np.arange(b + 0.3, d, 1.45):
                flat(parts, box(a, y - 0.025, c, y + 0.025), z, z + 0.062, METAL)
    pw, ps, pe, pn = spec["pool_bounds"]
    # Leave both approaches open where paving extends to the glass wall.
    pool_sections = [
        box(pw, spec["pool_west_start_n"], west, pn),
        box(west, north, east, pn),
        box(east, ps, pe, pn),
        box(spec["pool_south_start_e"], ps, east, south),
    ]
    pool = union(pool_sections)
    water = pool.buffer(-0.19, join_style="mitre")
    curb = pool.difference(water).difference(envelope.buffer(0.055))
    add_paths(ground, field, water, Polygon(), WATER)
    site.surface(
        ground,
        curb,
        floor,
        lambda x, y: geometry.sample_ground(field, x, y) + 0.19,
        CONCRETE,
        PALE,
    )
    plaza = union([box(*spec[key]) for key in ("south_plaza", "west_plaza")])
    add_paths(ground, field, plaza, union([envelope, pool]), PAVING)
    return envelope, envelope, pool_sections


def build(spec, manifest, config, field, graph):
    models = ((spec["oregon_hall"], oregon), (spec["jaqua"], jaqua))
    meshes, records, ground, footprints, supports, gates = {}, [], [], [], [], []
    for model, create in models:
        parts, entries = [], {}
        for raw in model["entries"]:
            entry, _ = site.approach(ground, field, raw)
            if entry["gate"] == "oregon-south":
                entry["snap_to_facade"] = False
            entries[entry["gate"]] = entry
        floor = (
            min(
                geometry.sample_ground(field, *gate["position_enu_m"])
                for gate in entries.values()
            )
            - 0.70
        )
        plan, footprint, extra = create(parts, ground, model, entries, field, floor)
        assert plan.is_valid and footprint.is_valid
        for gate in entries.values():
            assert (
                footprint.boundary.distance(Point(gate["position_enu_m"])) < 0.03
            ), gate
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        meshes[model["id"]] = shared.index_mesh(mesh)
        footprints.append(footprint)
        supports.extend(extra)
        gates.extend(entries.values())
        records.append(
            {key: model[key] for key in ("id", "name", "campus_id")}
            | dict(
                footprint_enu_m=ring(plan),
                ground_footprints_enu_m=[ring(p) for p in geometry.sections(footprint)],
                support_collision_enu_m=[ring(p) for p in extra],
                area_m2=round(plan.area, 3),
                base_z_m=round(floor, 4),
                roof_z_m=round(float(mesh.bounds[1, 1]), 4),
                entrances=list(entries.values()),
            )
        )
    previous = union(
        [
            Polygon(b["footprint_enu_m"]).buffer(0)
            for b in manifest["buildings"]
            if b["id"] in meshes
        ]
    )
    routing = shared.graduate.shared.check_routes(
        footprints, supports, gates, previous, manifest, graph, config, set(meshes)
    )
    return meshes, records, trimesh.util.concatenate(ground), routing


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--spec", type=Path, default=SPEC)
    parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    configuration = SCENE / "presentation.json"
    config = json.loads(configuration.read_bytes())
    terrain = SCENE / manifest["heightfield_url"]
    field = json.loads(terrain.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, (edge_count, clearance) = build(
        spec, manifest, config, field, graph
    )
    out = args.stage or SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    site.memorial.gerlinger.export(
        glb, meshes, ground, GROUND, "oregon-jaqua-paving",
        vegetation=site_planting(spec, field, geometry.sample_ground),
    )
    descriptor = out / "site.json"
    data = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(terrain),
        context_trees=[spec["jaqua"]["obsolete_context_tree"], *spec.get("context_tree_removals", [])],
        ground_node=GROUND,
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        buildings=records,
    )
    descriptor.write_text(
        json.dumps(data, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    if args.stage is None:
        config["oregon_jaqua_site"] = dict(
            url=f"{DIRECTORY}/site.json", sha256=tools.digest(descriptor)
        )
        configuration.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf8",
            newline="\n",
        )
    audit = dict(
        models={
            building["id"]: {
                key: building[key]
                for key in ("area_m2", "base_z_m", "roof_z_m", "entrances")
            }
            for building in records
        },
        route_edges=edge_count,
        nearest_route_m=round(clearance, 3),
        glb_sha256=data["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
