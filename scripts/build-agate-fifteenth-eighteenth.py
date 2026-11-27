# SPDX-License-Identifier: Apache-2.0
"""Export Agate Street's Hayward Field frontage and two southern junctions."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.affinity import rotate, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

agate = import_module("build-agate-thirteenth-fifteenth")
east, site, west, central = agate.east, agate.site, agate.west, agate.central

PACKAGE = "agate-fifteenth-eighteenth-review"
GROUND = "agate-fifteenth-eighteenth-paving"
MARKINGS = "agate-fifteenth-eighteenth-markings"
FURNISHINGS = "agate-fifteenth-eighteenth-furnishings"
PLANTING = "agate-fifteenth-eighteenth-planting"
ASPHALT = (130, 128, 121)
WALK = (176, 172, 160)
CURB = (160, 156, 144)


def pavement(parts, field, spec, buildings, neighbor):
    road = (
        agate.longitudinal_band(spec["road"])
        .union(west.surface(spec["junctions"]))
        .difference(buildings)
    )
    west_walk = agate.longitudinal_band(spec["west_walk"])
    east_walk = agate.longitudinal_band(spec["east_walk"])
    walk = unary_union([west_walk, east_walk, west.surface(spec["walk_joins"])])
    ramps = central.buffered_lines(spec["ramp_ends"], 1.28)
    walk = walk.union(ramps).difference(road.union(buildings))
    covered = road.union(walk)
    curbs = (
        road.buffer(0.13)
        .difference(road)
        .difference(unary_union([box(*bounds) for bounds in spec["curb_gaps"]]))
        .difference(buildings)
        .intersection(box(44, -624.8, 125.8, -262.75))
    )
    for shape, color, lift, resolution in (
        (road, ASPHALT, 0.101, 1.6),
        (walk, WALK, 0.137, 1.21),
        (curbs, CURB, 0.177, 0.96),
    ):
        site.drape(parts, field, shape, color, lift, resolution)
    seam = unary_union(
        [
            agate.longitudinal_band(neighbor["west_walk"]),
            agate.longitudinal_band(neighbor["east_walk"]),
            agate.longitudinal_band(neighbor["road"]).intersection(
                box(76, -252.35, 100, -249.65)
            ),
        ]
    ).intersection(box(70, -262.55, 108, -249.65))
    return road, walk, curbs, covered.union(seam)


def bicycle():
    wheels = [
        Point(e, n)
        .buffer(0.26, quad_segs=10)
        .difference(Point(e, n).buffer(0.205, quad_segs=10))
        for e, n in ((0, -0.42), (0, 0.44))
    ]
    lines = [
        [(0, -0.40), (-0.24, -0.08), (0, 0.44), (0.18, -0.04), (0, -0.40)],
        [(-0.24, -0.08), (0.18, -0.04)],
        [(0, 0.44), (-0.11, 0.57), (0.13, 0.57)],
        [(-0.32, -0.08), (-0.21, -0.08)],
        [(0, 0.94), (0, 1.54)],
    ]
    arrow = Polygon([(0, 1.78), (0.28, 1.35), (-0.28, 1.35)])
    return unary_union([*wheels, central.buffered_lines(lines, 0.058), arrow])


def markings(parts, field, spec, road):
    stripes = unary_union(
        [
            box(
                e - 0.185,
                row["north"] - row["length"] / 2,
                e + 0.185,
                row["north"] + row["length"] / 2,
            )
            for row in spec["crossings"]
            for e in row["e"]
        ]
    )
    symbol = bicycle()
    symbols = unary_union(
        [
            translate(rotate(symbol, angle, origin=(0, 0)), e, n)
            for e, n, angle in spec["symbols"]
        ]
    )
    ticks = [[(e - 0.32, n), (e + 0.34, n)] for n, e in spec["parking_ticks"]]
    white = central.buffered_lines(spec["white_lines"], 0.118).union(
        central.buffered_lines(ticks, 0.081)
    )
    hatches = [[(86.65, n - 0.64), (87.98, n + 0.30)] for n in spec["hatch_norths"]]
    yellow = central.buffered_lines(spec["yellow_lines"], 0.103).union(
        central.buffered_lines(hatches, 0.081)
    )
    for shape, tint in (
        (stripes, (222, 218, 201)),
        (white.union(symbols), (204, 202, 187)),
        (yellow, (192, 164, 83)),
    ):
        site.drape(parts, field, shape.intersection(road), tint, 0.162, 0.89)


def fixture(parts, field, row):
    e, n = row["position"]
    base = site.ground_height(field, e, n)
    angle = np.deg2rad(row["heading"])
    outward = np.array((np.sin(angle), np.cos(angle)))
    across = np.array((-np.cos(angle), np.sin(angle)))
    point = np.array((e, n))

    def position(u, height, offset=0):
        x, y = point + u * across + offset * outward
        return (x, y, base + height)

    kind = row["kind"]
    if kind in ("meter", "call"):
        call = kind == "call"
        high = 1.76 if call else 1.23
        steel = (77, 119, 159) if call else (82, 91, 94)
        site.cylinder_between(
            parts, position(0, -0.05), position(0, high), 0.115, steel
        )
        site.flat_box(
            parts, e, n, 0.23, 0.23, base + high - 0.28, base + high, (50, 61, 65)
        )
        if call:
            site.cylinder_between(
                parts,
                position(0, high),
                position(0, high + 0.13),
                0.11,
                (224, 220, 188),
            )
        return box(e - 0.14, n - 0.14, e + 0.14, n + 0.14)

    height = 2.26
    site.cylinder_between(
        parts, position(0, -0.05), position(0, height), 0.034, (116, 119, 111), sides=8
    )
    profiles = {
        "crossing": ([(0, -0.41), (0.41, 0), (0, 0.41), (-0.41, 0)], (178, 184, 58)),
        "stop": (
            [
                (0.14, -0.35),
                (0.35, -0.14),
                (0.35, 0.14),
                (0.14, 0.35),
                (-0.14, 0.35),
                (-0.35, 0.14),
                (-0.35, -0.14),
                (-0.14, -0.35),
            ],
            (170, 53, 50),
        ),
        "parking": (
            [(-0.24, -0.31), (0.24, -0.31), (0.24, 0.31), (-0.24, 0.31)],
            (211, 215, 193),
        ),
    }
    outline, tint = profiles[kind]
    # The narrow horizontal bands give the pole-mounted signs their observed silhouettes.
    panel = Polygon(outline)
    for z in np.linspace(panel.bounds[1] + 0.012, panel.bounds[3] - 0.012, 26):
        band = panel.intersection(LineString([(-0.5, z), (0.5, z)]))
        lo, _, hi, _ = band.bounds
        width, depth = (
            (hi - lo, 0.039) if row["heading"] in (0, 180) else (0.039, hi - lo)
        )
        site.flat_box(
            parts,
            e,
            n,
            width,
            depth,
            base + height + z - 0.016,
            base + height + z + 0.016,
            tint,
        )
    if kind == "crossing":
        ink = (43, 52, 44)
        site.cylinder_between(
            parts,
            position(-0.035, height + 0.127, 0.028),
            position(-0.035, height + 0.185, 0.028),
            0.033,
            ink,
            sides=8,
        )
        for a, b in (
            ((-0.03, 0.125), (0.016, -0.011)),
            ((0.016, -0.011), (-0.105, -0.132)),
            ((0.016, -0.011), (0.134, -0.132)),
            ((-0.041, 0.095), (-0.142, 0.02)),
            ((-0.041, 0.095), (0.102, 0.016)),
        ):
            site.beam(
                parts,
                position(a[0], height + a[1], 0.026),
                position(b[0], height + b[1], 0.026),
                0.031,
                ink,
            )
    else:
        label = "STOP" if kind == "stop" else "P"
        site.text_strokes(
            parts,
            label,
            lambda u, z: position(u, height - 0.074 + z, 0.029),
            0.096,
            0.13,
            (235, 232, 217) if kind == "stop" else (59, 93, 66),
        )
    return box(e - 0.09, n - 0.09, e + 0.09, n + 0.09)


def flags(parts, field, spec):
    line = LineString([*spec["flag_run"], *spec["flag_corner"][1:]])
    positions = [line.interpolate(d).coords[0] for d in np.arange(0, line.length, 3.92)]
    return flagpoles(parts, field, positions)


def flagpoles(parts, field, positions):
    colors = (
        (145, 62, 60),
        (229, 224, 203),
        (71, 105, 143),
        (208, 163, 70),
        (76, 123, 89),
    )
    for index, (e, n) in enumerate(positions):
        z = site.ground_height(field, e, n)
        top = z + 6.9
        site.cylinder_between(
            parts, (e, n, z - 0.05), (e, n, top), 0.045, (173, 175, 165), sides=8
        )
        for j in range(7):
            step = j / 7
            u = step * 0.96
            sway = np.sin(step * 4 + index * 0.57) * 0.12
            site.flat_box(
                parts,
                e - u - 0.073,
                n + sway,
                0.15,
                0.052,
                top - 0.64 - step * 0.12,
                top - 0.05 - step * 0.12,
                colors[index % len(colors)],
            )
    return len(positions)


def plants(parts, field, spec, roads, walks, buildings):
    obstacles, used = [], []
    restricted = roads.union(walks).union(buildings)
    for row in spec["tree_inventory"]:
        e, n = row["position_enu_m"]
        center = Point(e, n)
        if restricted.distance(center) < 0.20:
            continue
        site.canopy(parts, field, row, len(used))
        used.append(row["tree_id"])
        obstacles.append(box(e - 0.22, n - 0.22, e + 0.22, n + 0.22))
    beds = unary_union(
        [
            box(71.52, -456, 72.73, -432),
            box(71.72, -420, 72.91, -316),
            box(70.84, -590, 72.07, -506),
        ]
    ).difference(restricted.buffer(0.16))
    rng = np.random.default_rng(182)
    count = 0
    for bed in site.geometry.sections(beds):
        x0, y0, x1, y1 = bed.bounds
        for y in np.arange(y0 + 0.39, y1, 0.89):
            x = (x0 + x1) / 2 + rng.uniform(-0.18, 0.18)
            if not bed.covers(Point(x, y)):
                continue
            z = site.ground_height(field, x, y)
            site.orb(parts, (x, y, z + 0.23), (0.27, 0.41, 0.25), (92, 109, 68))
            count += 1
    return obstacles, used, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(site.root / "data/metadata/agate-fifteenth-eighteenth.json")
    manifest, field, graph = east.pinned_site(site.scene, spec)
    prior = site.read(site.root / "data/metadata/agate-thirteenth-fifteenth.json")
    buildings, prior_boxes = east.build_blockers(
        site.scene, spec, manifest, box(*spec["limits"])
    )
    ground, paint, objects, vegetation = [], [], [], []
    road, walk, curbs, walkable = pavement(ground, field, spec, buildings, prior)
    markings(paint, field, spec, road)
    solids = [fixture(objects, field, row) for row in spec["fixtures"]]
    pole_count = flags(objects, field, spec)
    stems, trees, shrubs = plants(vegetation, field, spec, road, walk, buildings)
    assert len(solids) <= 16
    paths = spec["routes"]
    edges, lengths = west.check_routes(
        graph, paths, walkable, unary_union([buildings, prior_boxes, *solids, *stems])
    )
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        (MARKINGS, paint, "landscape-detail"),
        (FURNISHINGS, objects, "landscape-detail"),
        (PLANTING, vegetation, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    descriptor = args.stage / "site.json"
    pins = spec["pins"]
    site.fairmount.write_json(
        descriptor,
        dict(
            source_presentation_sha256=pins["presentation"],
            source_base_model_sha256=pins["model"],
            source_heightfield_sha256=pins["heightfield"],
            source_navigation_sha256=pins["navigation"],
            ground_node=GROUND,
            url=f"{PACKAGE}/site.glb",
            sha256=site.pin(glb),
            buildings=[],
            walkable_ground=dict(
                paths=paths,
                bounds_enu_m=[
                    [65, -342, 117, -262.4],
                    [65, -422, 117, -341],
                    [55, -502, 127, -421],
                    [66, -582, 112, -501],
                    [42, -626, 112, -581],
                ],
            ),
            closed_site_boxes_enu_m=[
                [round(v, 4) for v in solid.bounds] for solid in solids
            ],
        ),
        compact=True,
    )
    audit = dict(
        road_m2=round(road.area, 2),
        walks_m2=round(walk.area, 2),
        curb_m2=round(curbs.area, 2),
        crossing_stripes=[len(row["e"]) for row in spec["crossings"]],
        fixtures=len(solids),
        flagpoles=pole_count,
        tree_ids=trees,
        rejected_tree_ids=sorted(
            {row["tree_id"] for row in spec["tree_inventory"]} - set(trees)
        ),
        shrubs=shrubs,
        route_edges=edges,
        route_lengths_m=lengths,
        faces=faces,
        asset_sha256=site.pin(glb),
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
