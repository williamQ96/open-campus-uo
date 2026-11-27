# SPDX-License-Identifier: Apache-2.0
"""Export the square track, Turf Field 3, outdoor tennis and Southgate."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.affinity import affine_transform, rotate, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import substring, unary_union

practice = import_module("build-hayward-practice-fields")
east, site, west, central = (
    practice.east,
    practice.site,
    practice.west,
    practice.central,
)
PACKAGE = "hayward-square-track-review"
GROUND = "hayward-square-track-ground"
DETAILS = "hayward-square-track-courts-and-southgate"
PLANTS = "hayward-square-track-planting"
WHITE = (219, 215, 194)
STEEL = (56, 65, 63)


def top_with_markings(parts, shape, markings, elevation, color, cell):
    x0, y0, x1, y1 = shape.bounds
    chunk = cell * 10
    for x in np.arange(x0, x1, chunk):
        for y in np.arange(y0, y1, chunk):
            tile = shape.intersection(box(x, y, x + chunk, y + chunk))
            if tile.area == 0:
                continue
            visible = markings.intersection(tile)
            site.landscape.top_surface(
                parts, tile.difference(visible), elevation, color, cell
            )
            if visible.area:
                site.landscape.top_surface(parts, visible, elevation, WHITE, 1.03)


def track_surface(parts, field, spec):
    radius = spec["track_radius"]
    outer = box(*spec["track_outer"]).buffer(-radius).buffer(radius, quad_segs=18)
    width = spec["loop_width"]
    loop = outer.difference(outer.buffer(-width))
    straights = [box(*bounds) for bounds in spec["sprints"]]
    surface = loop.union(unary_union(straights))
    rings = [outer.buffer(-i * width / 4).boundary.buffer(0.048) for i in range(5)]
    colored = unary_union(rings).difference(unary_union(straights))
    strokes = []
    for side, ((x, start), straight) in enumerate(
        zip(spec["sprint_starts"], straights)
    ):
        x0, y0, x1, y1 = straight.bounds
        boundaries = np.linspace(y0 + 0.06, y1 - 0.06, 9)
        for y in boundaries:
            strokes.append([(x0, y), (x1, y)])
        for i, (lo, hi) in enumerate(zip(boundaries, boundaries[1:])):
            digit = str(8 - i if side == 0 else i + 1)
            center = (lo + hi) / 2
            glyphs = (
                (
                    (
                        (0.94, 0.92),
                        (0.56, 1),
                        (0.11, 0.73),
                        (0, 0.28),
                        (0.24, 0),
                        (0.78, 0),
                        (1, 0.22),
                        (0.85, 0.54),
                        (0.48, 0.61),
                        (0.09, 0.45),
                    ),
                )
                if digit == "6"
                else site.GLYPHS[digit]
            )
            strokes.extend(
                [(x + 0.28 + v * 0.52, center + (u - 0.5) * 0.35) for u, v in stroke]
                for stroke in glyphs
            )
        strokes.extend([[(x, y0), (x, y1)], [(x1 - 0.28, y0), (x1 - 0.28, y1)]])
        # Start marks keep the short staggered strokes visible after tessellation.
        strokes.append([(x - 0.52, start + 0.23), (x + 0.72, start + 0.23)])
    colored = colored.union(central.buffered_lines(strokes, 0.094))
    top_with_markings(
        parts,
        surface,
        colored,
        lambda e, n: site.ground_height(field, e, n) + 0.146,
        (148, 101, 81),
        1.18,
    )
    return surface, outer


def turf_field(parts, details, field, spec, track):
    turf = box(*spec["turf"]).difference(track)
    level, fit = practice.fit_plane(field, turf)

    # Playing geometry is authored in its long and short axes, then mapped to ENU.
    def lateral(row):
        a, b, c, d = row
        return b, a, d, c

    soccer = lateral(spec["soccer"])
    pattern = {
        "soccer_bounds": soccer,
        "midline_e": (soccer[0] + soccer[2]) / 2,
        "multigame_bounds": lateral(spec["multigame"]),
        "multigame_ticks_e": [-564.9, -551.2, -526.52, -512.71],
    }
    white, amber = [
        affine_transform(shape, [0, 1, 1, 0, 0, 0])
        for shape in practice.turf_markings(pattern)
    ]
    paint = white.union(amber)
    x0, y0, x1, y1 = turf.bounds
    clipped = turf.difference(paint)
    for i, y in enumerate(np.arange(y0, y1, 4.72)):
        strip = clipped.intersection(box(x0, y, x1, min(y + 4.72, y1)))
        if not strip.is_empty:
            site.landscape.top_surface(
                parts, strip, level, (98, 125, 73) if i % 2 else (108, 134, 77), 1.75
            )
    for marking, tint in ((white, WHITE), (amber, (180, 158, 92))):
        site.landscape.top_surface(parts, marking.intersection(turf), level, tint, 1.12)
    boundary = turf.buffer(0.84).difference(turf.union(track))
    if not boundary.is_empty:

        def skirt(e, n):
            alpha = max(0, 1 - turf.distance(Point(e, n)) / 0.84)
            return alpha * level(e, n) + (1 - alpha) * (
                site.ground_height(field, e, n) + 0.06
            )

        site.landscape.top_surface(parts, boundary, skirt, (110, 128, 76), 0.69)
    mid = (spec["soccer"][0] + spec["soccer"][2]) / 2
    for n, d in ((spec["soccer"][1], -2.02), (spec["soccer"][3], 2.02)):
        a, b = mid - 3.65, mid + 3.65
        left, right = (a, n, level(a, n)), (b, n, level(b, n))
        top_l, top_r = (a, n, left[2] + 2.34), (b, n, right[2] + 2.34)
        back_l, back_r = (a, n + d, level(a, n + d)), (b, n + d, level(b, n + d))
        for p, q in (
            (left, top_l),
            (right, top_r),
            (top_l, top_r),
            (top_l, back_l),
            (top_r, back_r),
        ):
            site.beam(details, p, q, 0.082, WHITE)
        practice.mesh_barrier(details, back_l, back_r, 0.85, 0.39, z_low=0.05)
    return turf, fit


def tennis(parts, details, field, spec):
    decks, paint_count, solid, fits = [], 0, [], []
    for row in spec["courts"]:
        deck = box(*row["bounds"])
        decks.append(deck)
        level, fit = practice.fit_plane(field, deck)
        fits.append(fit.round(7).tolist())
        south, north = row["play_n"]
        mid = (south + north) / 2
        surrounds = []
        blue = []
        paint = []
        for x in spec["court_centers"]:
            outside = box(x - 5.49, south, x + 5.49, north)
            blue.append(outside)
            surrounds.append(outside.buffer(0.20, join_style="mitre"))
            paint.append(list(outside.exterior.coords))
            for e in (x - 4.115, x + 4.115):
                paint.append([(e, south), (e, north)])
            for n in (mid - 6.40, mid + 6.40):
                paint.append([(x - 4.115, n), (x + 4.115, n)])
            paint.append([(x, mid - 6.40), (x, mid + 6.40)])
            for n in (south - 1.45, north + 1.5):
                paint.extend(
                    [(x + (u - 0.5) * 1.52, n + (v - 0.5) * 1.05) for u, v in stroke]
                    for stroke in site.GLYPHS["O"]
                )
            a, b = (x - 5.96, mid), (x + 5.96, mid)
            na, nb = (*a, level(*a)), (*b, level(*b))
            practice.mesh_barrier(details, na, nb, 0.93, 0.22, z_low=0.05)
            for e, n, z in (na, nb):
                site.cylinder_between(
                    details, (e, n, z), (e, n, z + 1.06), 0.046, STEEL, sides=8
                )
            site.beam(
                details,
                (na[0], mid, na[2] + 0.94),
                (nb[0], mid, nb[2] + 0.94),
                0.036,
                WHITE,
            )
            paint_count += 1
        surrounds = unary_union(surrounds)
        blue = unary_union(blue)
        marking = central.buffered_lines(paint, 0.071).intersection(deck)
        site.landscape.top_surface(
            parts,
            deck.difference(surrounds.union(marking)),
            level,
            (104, 120, 89),
            1.45,
        )
        site.landscape.top_surface(
            parts,
            surrounds.difference(blue.union(marking)),
            level,
            (111, 127, 91),
            1.18,
        )
        site.landscape.top_surface(
            parts, blue.difference(marking), level, (85, 111, 124), 1.21
        )
        site.landscape.top_surface(parts, marking, level, WHITE, 1.03)
        x0, y0, x1, y1 = deck.bounds
        for a, b in (
            ((x0, y0), (x0, y1)),
            ((x1, y0), (x1, y1)),
            ((x0, y0), (x1, y0)),
            ((x0, y1), (x1, y1)),
        ):
            practice.mesh_barrier(
                details, (*a, level(*a)), (*b, level(*b)), 2.72, 0.54, z_low=0.1
            )
            line = LineString([a, b])
            for distance in np.linspace(
                0, line.length, int(np.ceil(line.length / 2.74)) + 1
            ):
                x, n = line.interpolate(distance).coords[0]
                z = level(x, n)
                site.cylinder_between(
                    details, (x, n, z - 0.07), (x, n, z + 2.83), 0.038, STEEL, sides=8
                )
        for e in (x0, x1):
            panels = np.linspace(y0 + 0.22, y1 - 0.22, 17)
            for first, last in zip(panels, panels[1:]):
                mid_n = (first + last) / 2
                z = level(e, mid_n)
                site.flat_box(
                    details,
                    e,
                    mid_n,
                    0.025,
                    last - first - 0.018,
                    z + 0.16,
                    z + 1.86,
                    (70, 78, 66),
                )
        solid.extend(
            [box(x0 - 0.09, y0, x0 + 0.09, y1), box(x1 - 0.09, y0, x1 + 0.09, y1)]
        )
    for x in spec["court_centers"]:
        for n in (-538.22, -541.9):
            for step in range(3):
                shown = n + (step - 1) * 0.38
                z = site.ground_height(field, x, shown)
                site.flat_box(
                    details,
                    x,
                    shown,
                    7.12,
                    0.25,
                    z + 0.26 + step * 0.2,
                    z + 0.39 + step * 0.2,
                    (172, 174, 161),
                )
    return unary_union(decks), paint_count, solid, fits


def southgate_walks(spec, junction):
    ramps = [row["outline_enu_m"] for row in junction["ramps"]]
    return unary_union(
        [
            east.band(spec["south_walk"]),
            west.surface([*spec["hardscape"], *ramps]),
            junction_sidewalk_returns(junction),
        ]
    )


def junction_sidewalk_returns(junction):
    return unary_union(
        [
            LineString(row["points_enu_m"]).buffer(
                row["width_m"] / 2, cap_style="square"
            )
            for row in junction["sidewalk_returns"]
        ]
    )


def southgate_road(spec, junction, walks, buildings):
    return (
        east.band(spec["road"])
        .union(Polygon(spec["university_entry"]))
        .union(Polygon(junction["south_throat_enu_m"]))
        .difference(walks.union(buildings))
    )


def crossing_lines(junction):
    return unary_union(
        [
            LineString(edge).buffer(row["width_m"] / 2, cap_style="flat")
            for row in junction["crossings"].values()
            for edge in row["edges_enu_m"]
        ]
    )


def crossing_corridor(row):
    edges = []
    for edge in row["edges_enu_m"]:
        start, end = np.asarray(edge)
        direction = (end - start) / np.linalg.norm(end - start)
        edges.extend([start - 1.80 * direction, end + 2.05 * direction])
    west_top, west_bottom, east_top, east_bottom = edges
    return Polygon([west_top, west_bottom, east_bottom, east_top]).buffer(-0.18)


def junction_lane_icons(junction):
    bicycle = practice.agate.bicycle().intersection(box(-1, -1, 1, 0.65))
    shapes = []
    for row in junction["bike_symbols"]:
        heading = row["rotation_degrees"]
        shapes.extend(
            [
                translate(
                    rotate(bicycle, heading - 90, origin=(0, 0)), *row["center_enu_m"]
                ),
                translate(
                    rotate(central.arrow(), heading, origin=(0, 0)), *row["arrow_enu_m"]
                ),
            ]
        )
    return unary_union(shapes)


def southgate_marks(junction):
    whites = [crossing_lines(junction), junction_lane_icons(junction)]
    whites.append(
        LineString(junction["south_stop_bar_enu_m"]).buffer(0.165, cap_style="flat")
    )
    for row in junction["bike_guides"]:
        line = LineString(row["line_enu_m"])
        whites.extend(
            substring(
                line, start, min(start + row["dash_length_m"], line.length)
            ).buffer(
                row["width_m"] / 2,
                cap_style="flat",
            )
            for start in np.arange(0.38, line.length, row["spacing_m"])
        )
    return unary_union(whites)


def southgate(parts, structures, vegetation, field, spec, junction, road, walks):
    paver = Polygon(spec["brick_cross"])
    e, n = spec["crossing_medallion"]
    ring = Point(e, n).buffer(1.68, quad_segs=24)
    courses = []
    for k, north in enumerate(np.arange(paver.bounds[1], paver.bounds[3], 0.24)):
        courses.append(LineString([(paver.bounds[0], north), (paver.bounds[2], north)]))
        for x in np.arange(paver.bounds[0] + (k % 2) * 0.25, paver.bounds[2], 0.50):
            courses.append(LineString([(x, north), (x, north + 0.24)]))
    joints = unary_union(courses).buffer(0.009).intersection(paver).difference(ring)
    ramp_specs = [
        (Polygon(row["outline_enu_m"]), LineString(row["curb_edge_enu_m"]))
        for row in junction["ramps"]
    ]
    ramp_shapes = unary_union([shape for shape, _ in ramp_specs])
    for shape, tint, lift, resolution in (
        (road.difference(paver), (127, 126, 119), 0.095, 1.5),
        (walks.difference(ramp_shapes), (175, 172, 156), 0.137, 1.15),
        (paver.difference(ring).difference(joints), (155, 142, 123), 0.154, 0.79),
        (joints, (126, 119, 108), 0.154, 0.79),
        (ring, (169, 164, 141), 0.155, 0.61),
        (ring.boundary.buffer(0.045), (112, 125, 96), 0.180, 0.66),
    ):
        site.drape(parts, field, shape, tint, lift, resolution)
    for shape, curb in ramp_specs:
        site.landscape.top_surface(
            parts,
            shape.intersection(walks),
            lambda e, n: site.ground_height(field, e, n)
            + 0.095
            + 0.042 * min(1.0, curb.distance(Point(e, n)) / 1.45),
            (175, 172, 156),
            cell=0.54,
        )
    boxes = []
    for index, (x, north) in enumerate(spec["north_plinths"]):
        planting = box(x - 1.12, north - 2.18, x + 1.12, north + 1.52)
        boxes.append(planting)
        site.drape(parts, field, planting, (150, 141, 110), 0.16, 0.65)
        z = site.ground_height(field, x, north)
        for w, bottom, top, color in (
            (1.38, -0.03, 0.29, (118, 87, 69)),
            (1.19, 0.29, 0.48, (192, 187, 165)),
            (0.98, 0.48, 2.06, (206, 200, 174)),
            (1.18, 2.06, 2.27, (196, 190, 166)),
        ):
            site.flat_box(structures, x, north, w, w * 0.81, z + bottom, z + top, color)
        site.flat_box(
            structures, x, north - 0.401, 0.56, 0.039, z + 0.77, z + 1.88, (58, 74, 59)
        )
        for i, word in enumerate(("UNIVERSITY", "OF OREGON")):
            site.text_strokes(
                structures,
                word,
                lambda u, h: (x + u, north - 0.433, z + 1.37 - i * 0.15 + h),
                0.042,
                0.064,
                (211, 204, 180),
            )
        site.cylinder_between(
            structures,
            (x, north, z + 2.27),
            (x, north, z + 3.37),
            0.108,
            STEEL,
            sides=10,
        )
        site.orb(
            structures, (x, north, z + 3.46), (0.202, 0.202, 0.24), (222, 217, 190)
        )
        for i in range(11):
            dx = (i % 4 - 1.5) * 0.44
            dy = -1.62 + (i // 4) * 0.34
            xx, nn = x + dx, north + dy
            z1 = site.ground_height(field, xx, nn)
            site.orb(
                vegetation,
                (xx, nn, z1 + 0.38),
                (0.3, 0.31, 0.31),
                (104, 121 - index * 7, 65),
            )
    return boxes


def fixtures(structures, vegetation, ground, field, spec, keep_clear):
    for e, n in spec["lighting"]:
        z = site.ground_height(field, e, n)
        site.cylinder_between(
            structures,
            (e, n, z - 0.1),
            (e, n, z + 12.45),
            0.082,
            (132, 135, 127),
            sides=9,
        )
        site.beam(
            structures, (e - 0.96, n, z + 12.27), (e + 0.96, n, z + 12.27), 0.075, STEEL
        )
        for x in np.linspace(e - 0.78, e + 0.78, 4):
            site.flat_box(
                structures, x, n, 0.34, 0.27, z + 12.17, z + 12.42, (190, 185, 157)
            )
    infill = {
        "bed_lines": [
            {"points": o["line"], "width": o["width"]} for o in spec["planting"]
        ]
    }
    return practice.border_planting(vegetation, ground, field, infill, keep_clear)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(site.root / "data/metadata/hayward-square-track.json")
    junction = site.read(site.root / "data/metadata/southgate-junction.json")
    prior = site.read(site.root / "data/metadata/hayward-practice-fields.json")
    agate = site.read(site.root / "data/metadata/agate-fifteenth-eighteenth.json")
    manifest, field, graph = east.pinned_site(site.scene, spec)
    buildings, prior_boxes = east.build_blockers(
        site.scene, spec, manifest, box(*spec["extent"])
    )
    land, objects, green = [], [], []
    track, outer = track_surface(land, field, spec)
    turf, turf_grade = turf_field(land, objects, field, spec, track)
    courts, court_count, boxes, court_grades = tennis(land, objects, field, spec)
    sidewalk = east.band(spec["south_walk"])
    walks = southgate_walks(spec, junction).difference(
        buildings.union(track).union(turf).union(courts)
    )
    road = southgate_road(spec, junction, walks, buildings)
    boxes.extend(southgate(land, objects, green, field, spec, junction, road, walks))
    for runs in spec["exterior_fence"]:
        boxes.extend(practice.fence_run(objects, field, runs["points"], runs["height"]))
    assert len(boxes) <= 16
    for area, color in (
        (
            central.buffered_lines(spec["white_lines"][4:], 0.133).union(
                southgate_marks(junction)
            ),
            WHITE,
        ),
        (central.buffered_lines(spec["yellow_lines"], 0.133), (185, 160, 83)),
    ):
        marking = area.intersection(road)
        site.drape(land, field, marking, color, 0.168, 0.86)
    plants = fixtures(
        objects, green, land, field, spec, walks.union(track).union(turf).union(courts)
    )
    new_crosswalk = Polygon(spec["brick_cross"])
    seam = box(42.9, -602, 89, -596.7)
    east_seam = (
        west.surface(agate["walk_joins"])
        .union(practice.agate.agate.longitudinal_band(agate["road"]))
        .union(central.buffered_lines(agate["ramp_ends"], 1.28))
        .intersection(seam)
    )
    allowed = (
        walks.union(new_crosswalk)
        .union(east.band(prior["south_walk"]))
        .union(east_seam)
    )
    edges, lengths = west.check_routes(
        graph,
        spec["routes"],
        allowed,
        buildings.union(prior_boxes).union(unary_union(boxes)),
    )
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, land, "landscape-surface"),
        (DETAILS, objects, "landscape-detail"),
        (PLANTS, green, "landscape-vegetation"),
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
                paths=spec["routes"],
                bounds_enu_m=[
                    [-329, -628, -244, -583],
                    [-245, -620, -159, -590],
                    [-160, -621, -146, -590],
                    [-160, -551, -74, -470],
                    [-160, -600, -74, -550],
                    [-75, -551, -33, -470],
                    [-75, -600, -33, -550],
                ],
            ),
            context_trees=spec["clear_context_trees"],
            closed_site_boxes_enu_m=[
                [round(value, 4) for value in shape.bounds] for shape in boxes
            ],
        ),
        compact=True,
    )
    audit = dict(
        track_m2=round(track.area, 2),
        track_outer_m2=round(outer.area, 2),
        sprint_lanes=8,
        turf_m2=round(turf.area, 2),
        turf_grade=turf_grade.round(7).tolist(),
        tennis_courts=court_count,
        court_grade_coefficients=court_grades,
        east_18th_walk_m2=round(sidewalk.area, 2),
        road_m2=round(road.area, 2),
        southgate_plinths=len(spec["north_plinths"]),
        landscape_planting=plants,
        cleared_context=[t["index"] for t in spec["clear_context_trees"]],
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
