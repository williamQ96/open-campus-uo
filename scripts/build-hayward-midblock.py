# SPDX-License-Identifier: Apache-2.0
"""Register the Hayward midblock passage and SRC outdoor recreation grounds."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union


axis = import_module("build-university-south-axis")
east, site, west, practice = axis.east, axis.site, axis.west, axis.practice
PACKAGE = "hayward-midblock-review"
GROUND = "hayward-midblock-paving"
DETAIL = "hayward-midblock-furnishings"
PLANTING = "hayward-midblock-planting"
WALK = (176, 170, 151)
ALLEY = (154, 153, 140)
RAIL = (82, 86, 77)


def adjoining_paths(meta):
    practice_spec = site.read(meta / "hayward-practice-fields.json")
    square_spec = site.read(meta / "hayward-square-track.json")
    howe_spec = site.read(meta / "howe-field-gates-review.json")
    square = west.surface(square_spec["hardscape"]).union(
        axis.agate.agate.longitudinal_band(list(reversed(square_spec["south_walk"])))
    )
    howe = Polygon(howe_spec["pavement_enu_m"])
    existing = square.union(howe).union(west.surface(practice_spec["paths"]))
    west_approach = LineString(
        [howe_spec["route"]["anchor_enu_m"], howe_spec["route"]["points_enu_m"][0]]
    ).buffer(0.8)
    agate_crossing = box(72.5, -480.8, 90.0, -476.95)
    athletic = site.read(meta / "athletic-exterior-review.json")
    east_entry = west.surface([row["outline"] for row in athletic["approaches"]])
    fifteenth = box(-144.0, -246.45, -131.4, -242.0)
    return existing.union(west_approach).union(agate_crossing).union(east_entry).union(
        fifteenth
    ), howe


def paving(ground, field, spec, buildings, howe, adjacent):
    stair = spec["stairs"]
    e0, e1 = stair["west_e"], stair["east_e"]
    n0, n1 = stair["south_n"], stair["north_n"]
    stair_shape = box(e0, n0, e1, n1)
    paving_shapes = [
        Polygon(spec[key]).buffer(0)
        for key in (
            "west_paving",
            "shadow_alley",
            "mcarthur_link",
            "field_walk",
            "field_walk_join",
            "east_join",
            "east_flag_link",
        )
    ]
    coverage = unary_union(
        [*paving_shapes, west.surface(spec["src_walks"]), stair_shape]
    ).difference(buildings)
    landing = paving_shapes[0].intersection(coverage)

    # Fade the estimated stair rise back into the existing Howe plaza.
    def landing_height(e, n):
        alpha = max(0, min(1, (e - (e0 - 10.5)) / 10.5))
        return site.ground_height(field, e, n) + 0.138 + stair["rise_m"] * alpha

    site.landscape.top_surface(
        ground, landing.difference(howe), landing_height, WALK, cell=0.65
    )
    other = coverage.difference(landing.union(stair_shape).union(adjacent))
    alley = other.intersection(paving_shapes[1])
    site.drape(ground, field, alley, ALLEY, 0.135, 0.78)
    site.drape(ground, field, other.difference(alley), WALK, 0.138, 0.92)
    return (
        coverage,
        landing_height,
        round(other.area + landing.difference(howe).area + stair_shape.area, 2),
    )


def stairs(ground, details, field, spec, landing_height):
    e0, e1 = spec["west_e"], spec["east_e"]
    n0, n1 = spec["south_n"], spec["north_n"]
    starts = np.linspace(e0, e1, spec["steps"] + 1)
    mid = (n0 + n1) / 2
    west_top = landing_height(e0, mid)
    east_top = site.ground_height(field, e1, mid) + 0.135
    bottom = (
        min(site.ground_height(field, e, n) for e in (e0, e1) for n in (n0, n1)) - 0.02
    )
    for index, (left, right) in enumerate(zip(starts, starts[1:])):
        top = west_top - (west_top - east_top) * (index + 1) / spec["steps"]
        site.solid(ground, box(left, n0, right, n1), bottom, top, WALK)
    blockers = []
    for n in (n0 + 0.075, n1 - 0.075):
        start = (e0, n, west_top + 0.88)
        end = (e1, n, east_top + 0.88)
        site.beam(details, start, end, 0.044, RAIL)
        for e in (e0, (e0 + e1) / 2, e1):
            height = west_top + (east_top - west_top) * (e - e0) / (e1 - e0)
            site.cylinder_between(
                details,
                (e, n, height - 0.09),
                (e, n, height + 0.87),
                0.026,
                RAIL,
                sides=8,
            )
        blockers.append(box(e0 - 0.046, n - 0.049, e1 + 0.046, n + 0.049))
    return blockers, west_top - east_top


def field_surface(ground, details, field, spec, buildings, paving):
    turf = Polygon(spec["outline"]).difference(buildings)
    level, fit = practice.fit_plane(field, turf)
    x0, y0, x1, y1 = spec["soccer_bounds"]
    e = (x0 + x1) / 2
    c = spec["midfield_n"]
    white_lines = [
        list(box(x0, y0, x1, y1).exterior.coords),
        [(x0, c), (x1, c)],
        list(Point(e, c).buffer(9.13, quad_segs=32).exterior.coords),
    ]
    for end, direction in ((y0, 1), (y1, -1)):
        for depth, half in ((16.4, 20.0), (5.4, 9.15)):
            line = end + depth * direction
            white_lines.append(
                [(e - half, end), (e - half, line), (e + half, line), (e + half, end)]
            )
        penalty = end + 11.02 * direction
        arc = Point(e, penalty).buffer(9.05, quad_segs=28).boundary
        if direction == 1:
            arc = arc.intersection(box(x0, end + 16.39, x1, c))
        else:
            arc = arc.intersection(box(x0, c, x1, end - 16.39))
        if not arc.is_empty:
            white_lines.append(list(arc.coords))
    white = axis.central.buffered_lines(white_lines, 0.108).intersection(turf)
    amber = (
        axis.central.buffered_lines(
            [list(box(*spec["multigame_bounds"]).exterior.coords)], 0.096
        )
        .intersection(turf)
        .difference(white)
    )
    markings = white.union(amber)
    min_x, min_y, max_x, max_y = turf.bounds
    for i, n in enumerate(np.arange(min_y, max_y, 7.5)):
        section = turf.intersection(box(min_x, n, max_x, min(n + 7.5, max_y)))
        tint = (97, 124, 72) if i % 2 else (102, 129, 76)
        site.landscape.top_surface(
            ground, section.difference(markings), level, tint, cell=1.8
        )
    site.landscape.top_surface(ground, white, level, (218, 218, 204), cell=1.0)
    site.landscape.top_surface(ground, amber, level, (166, 152, 98), cell=1.0)

    def slope(x, n):
        weight = max(0, 1 - turf.distance(Point(x, n)) / 1.05)
        base = site.ground_height(field, x, n) + 0.045
        return base + weight * (level(x, n) - base)

    skirt = turf.buffer(1.05).difference(turf.union(buildings).union(paving))
    divider = Polygon(spec.get("north_strip", [])).difference(buildings.union(turf))
    site.landscape.top_surface(
        ground, skirt.difference(divider), slope, (97, 116, 70), cell=0.8
    )
    if not divider.is_empty:
        site.landscape.top_surface(ground, divider, slope, (153, 111, 91), cell=1.1)

    goals = spec.get("goals")
    if goals is None:
        goals = [[*spec["goal_center"], -1.85]]
    for center_e, front_n, depth in goals:
        left_e, right_e = center_e - 3.66, center_e + 3.66
        ends = []
        for goal_e in (left_e, right_e):
            base = level(goal_e, front_n)
            top = (goal_e, front_n, base + 2.35)
            back = (goal_e, front_n + depth, level(goal_e, front_n + depth))
            site.beam(details, (goal_e, front_n, base), top, 0.085, practice.WHITE)
            site.beam(details, top, back, 0.044, practice.WHITE)
            ends.append((top, back))
        site.beam(details, ends[0][0], ends[1][0], 0.085, practice.WHITE)
        practice.mesh_barrier(details, ends[0][1], ends[1][1], 0.88, 0.36, z_low=0.05)
    return turf, fit


def src_edge(details, field, spec):
    blockers = practice.fence_run(details, field, spec["field1_fence"], 1.82)
    for e, n in spec["field1_benches"]:
        base = site.ground_height(field, e, n)
        for side in (-0.71, 0.71):
            site.flat_box(details, e + side, n, 0.11, 0.39, base, base + 0.46, RAIL)
        site.flat_box(
            details, e, n, 1.82, 0.55, base + 0.46, base + 0.54, (147, 126, 98)
        )
        blockers.append(box(e - 0.91, n - 0.275, e + 0.91, n + 0.275))
    for e, n in spec["field_lights"]:
        base = site.ground_height(field, e, n)
        top = base + 10.5
        site.cylinder_between(details, (e, n, base), (e, n, top), 0.076, RAIL, sides=9)
        site.beam(details, (e, n - 0.61, top), (e, n + 0.61, top), 0.084, RAIL)
        for side in (-0.48, 0.48):
            site.flat_box(
                details,
                e + 0.1,
                n + side,
                0.32,
                0.32,
                top - 0.08,
                top + 0.14,
                (197, 191, 167),
            )
        blockers.append(box(e - 0.11, n - 0.11, e + 0.11, n + 0.11))
    return blockers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    spec = site.read(metadata / "hayward-midblock.json")
    manifest, field, original = east.pinned_site(site.scene, spec)
    buildings, old_boxes = east.build_blockers(
        site.scene, spec, manifest, box(*spec["extent"])
    )
    adjacent, howe = adjoining_paths(metadata)
    ground, details, plants = [], [], []
    paved, height, paving_area = paving(ground, field, spec, buildings, howe, adjacent)
    blockers, rise = stairs(ground, details, field, spec["stairs"], height)
    turf, field_fit = field_surface(
        ground, details, field, spec["field2"], buildings, paved
    )
    field1, field1_fit = field_surface(
        ground, details, field, spec["field1"], buildings, paved
    )
    blockers.extend(src_edge(details, field, spec))
    source = metadata / "context-trees-l2.json"
    assert site.pin(source) == spec["evidence"]["source_inferred_trees_sha256"]
    tree_inputs = site.read(source)["trees"]
    assert all(
        [
            tree_inputs[t["index"]]["origin_gltf_m"][0],
            -tree_inputs[t["index"]]["origin_gltf_m"][2],
        ]
        == t["position_enu_m"]
        for t in spec["clear_context_trees"]
    )

    blockers.extend(practice.fence_run(details, field, spec["field_fence"], 1.84))
    flag_line = LineString(spec["flag_pole_line"])
    flag_points = [
        flag_line.interpolate(distance).coords[0]
        for distance in np.arange(0, flag_line.length, 4.34)
    ]
    flag_count = axis.agate.flagpoles(details, field, flag_points)
    planted = practice.border_planting(
        plants,
        ground,
        field,
        spec,
        paved.buffer(0.22).union(buildings).union(turf).union(field1),
    )
    bounds = [
        [-259, -502, -172, -466],
        [-173, -495, -84, -407],
        [-85, -511, 2, -422],
        [1, -513, 76, -472],
        [-164, -554, -150, -482],
        [-163, -603, -150, -553],
        [-162, -422.5, -73, -333.6],
        [-161, -334.3, -72, -245.3],
    ]
    assert len(blockers) <= 16
    edges, lengths = west.check_routes(
        original,
        spec["routes"],
        paved.union(adjacent),
        buildings.union(old_boxes).union(unary_union(blockers)),
    )
    # Match the padded rectangles used by the runtime outdoor route builder.
    padded = unary_union(
        [
            p.buffer(0.501, join_style=2)
            for p in [*blockers, *getattr(old_boxes, "geoms", [old_boxes])]
        ]
    )
    for branch in spec["routes"]:
        points = [branch["anchor_enu_m"], *branch["points_enu_m"]]
        if "end_enu_m" in branch:
            points.append(branch["end_enu_m"])
        route = LineString(points)
        assert not route.intersects(padded), route.intersection(padded).wkt
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        (DETAIL, details, "landscape-detail"),
        (PLANTING, plants, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    pins = spec["pins"]
    descriptor = args.stage / "site.json"
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
            context_trees=spec["clear_context_trees"],
            walkable_ground=dict(paths=spec["routes"], bounds_enu_m=bounds),
            closed_site_boxes_enu_m=[
                [round(coord, 4) for coord in part.bounds] for part in blockers
            ],
        ),
        compact=True,
    )
    audit = dict(
        paving_m2=paving_area,
        field1_m2=round(field1.area, 2),
        field1_grade=list(field1_fit),
        field1_fence_m=round(LineString(spec["field1_fence"]).length, 2),
        src_lights=len(spec["field_lights"]),
        src_benches=len(spec["field1_benches"]),
        field2_m2=round(turf.area, 2),
        field2_grade=list(field_fit),
        removed_context_trees=[t["index"] for t in spec["clear_context_trees"]],
        stairs=spec["stairs"]["steps"],
        stair_rise_m=round(rise, 3),
        fence_m=round(LineString(spec["field_fence"]).length, 2),
        flagpoles=flag_count,
        shrubs=planted,
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
