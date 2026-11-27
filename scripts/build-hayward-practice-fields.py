# SPDX-License-Identifier: Apache-2.0
"""Export Turf Field 4, the throwing enclosure and the East 18th flag walk."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import get_parts
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

agate = import_module("build-agate-fifteenth-eighteenth")
east, site, west, central = agate.east, agate.site, agate.west, agate.central

PACKAGE = "hayward-practice-fields-review"
GROUND = "hayward-practice-fields-ground"
LINES = "hayward-practice-fields-markings"
FENCES = "hayward-practice-fields-enclosures"
DETAILS = "hayward-practice-fields-planting-and-flags"
STEEL = (53, 63, 56)
WIRE = (103, 109, 97)
WHITE = (221, 219, 203)


def fit_plane(field, surface):
    x0, y0, x1, y1 = surface.bounds
    points = [
        (x, y)
        for x in np.linspace(x0, x1, 42)
        for y in np.linspace(y0, y1, 25)
        if surface.covers(Point(x, y))
    ]
    inputs = np.asarray([(1, x, y) for x, y in points])
    grade = np.asarray([site.ground_height(field, *point) for point in points])
    fit = np.linalg.lstsq(inputs, grade, rcond=None)[0]
    fit[0] += float(np.max(grade - inputs @ fit)) + 0.055

    def level(e, n):
        return float(fit[0] + fit[1] * e + fit[2] * n)

    return level, fit


def ground_layers(parts, field, spec, buildings):
    turf = Polygon(spec["turf_outline"])
    x0, y0, x1, y1 = turf.bounds
    level, fit = fit_plane(field, turf)
    sidewalk = east.band(spec["south_walk"])
    walks = sidewalk.union(west.surface(spec["paths"])).difference(buildings)
    grass = Polygon(spec["grass_throws"])
    concrete = Polygon(spec["throws_concrete"])
    sector = Polygon(spec["throws_sector"]).difference(concrete)
    parking = west.surface(spec["asphalt"]).difference(buildings)
    border = turf.buffer(1.45).difference(turf.union(walks))
    white, amber = turf_markings(spec)
    markings = white.union(amber)

    def slope(e, n):
        inner = max(0, 1 - turf.distance(Point(e, n)) / 1.45)
        return level(e, n) * inner + (site.ground_height(field, e, n) + 0.035) * (
            1 - inner
        )

    for i, x in enumerate(np.arange(x0, x1, 4.8)):
        strip = turf.intersection(box(x, y0, min(x + 4.8, x1), y1)).difference(markings)
        tint = (103, 130, 75) if i % 2 else (95, 123, 72)
        site.landscape.top_surface(parts, strip, level, tint, cell=1.9)
    for shape, tint in ((white, WHITE), (amber, (185, 163, 101))):
        site.landscape.top_surface(parts, shape, level, tint, cell=1.15)
    site.landscape.top_surface(parts, border, slope, (92, 113, 66), cell=0.82)
    for shape, color, lift, cell in (
        (
            grass.difference(walks.union(concrete).union(sector)),
            (113, 127, 79),
            0.126,
            2.2,
        ),
        (walks, (175, 171, 156), 0.134, 1.12),
        (concrete, (170, 167, 150), 0.124, 0.81),
        (sector, (147, 107, 87), 0.128, 1.05),
        (parking.difference(walks), (126, 126, 117), 0.094, 1.1),
    ):
        site.drape(parts, field, shape, color, lift, cell)
    return turf, walks, sidewalk, level, fit


def turf_markings(spec):
    left, bottom, right, top = spec["soccer_bounds"]
    middle = spec["midline_e"]
    center_y = (bottom + top) / 2
    white = [
        list(box(left, bottom, right, top).exterior.coords),
        [(middle, bottom), (middle, top)],
        list(Point(middle, center_y).buffer(9.13, quad_segs=40).exterior.coords),
    ]
    spots = [Point(middle, center_y)]
    for base, direction in ((left, 1), (right, -1)):
        for gap, half in ((13.70, 14.76), (5.32, 9.18)):
            end = base + gap * direction
            white.append(
                [
                    (base, center_y - half),
                    (end, center_y - half),
                    (end, center_y + half),
                    (base, center_y + half),
                ]
            )
        spot = base + 10.95 * direction
        spots.append(Point(spot, center_y))
        arc = Point(spot, center_y).buffer(9.12, quad_segs=40).boundary
        portion = (
            box(spot + 2.75, bottom, middle, top)
            if direction == 1
            else box(middle, bottom, spot - 2.75, top)
        )
        white.extend(
            list(segment.coords) for segment in get_parts(arc.intersection(portion))
        )
    other = box(*spec["multigame_bounds"])
    x0, y0, x1, y1 = other.bounds
    amber = [list(other.exterior.coords), [(middle, y0), (middle, y1)]]
    for x in spec.get("multigame_ticks_e", (-6.9, 2.35, 39.76, 48.41)):
        for y in (center_y - 4.45, center_y + 4.47):
            amber.append([(x - 1.46, y), (x + 1.46, y)])
    white = central.buffered_lines(white, 0.106).union(
        unary_union([spot.buffer(0.12, quad_segs=8) for spot in spots])
    )
    return white, central.buffered_lines(amber, 0.106).difference(white)


def throwing_lines(parts, field, spec):
    center = Point(*spec["circle"])
    inner = center.buffer(1.05, quad_segs=22)
    site.drape(parts, field, inner, (137, 139, 126), 0.153, 0.58)
    site.drape(parts, field, inner.buffer(0.068).difference(inner), WHITE, 0.159, 0.58)
    rim = (
        Polygon(spec["throws_sector"])
        .boundary.buffer(0.055)
        .difference(Polygon(spec["throws_concrete"]).buffer(0.05))
    )
    site.drape(parts, field, rim, (199, 187, 158), 0.161, 1.0)


def fence_run(parts, field, points, height, gate=False):
    line = LineString(points)
    steps = int(np.ceil(line.length / (0.164 if not gate else 0.195)))
    positions = [
        line.interpolate(d).coords[0] for d in np.linspace(0, line.length, steps + 1)
    ]
    for e, n in positions:
        z = site.ground_height(field, e, n)
        site.flat_box(parts, e, n, 0.024, 0.024, z + 0.13, z + height, STEEL)
    for distance in np.linspace(0, line.length, int(np.ceil(line.length / 2.36)) + 1):
        e, n = line.interpolate(distance).coords[0]
        z = site.ground_height(field, e, n)
        site.flat_box(parts, e, n, 0.075, 0.075, z - 0.08, z + height + 0.025, STEEL)
    for a, b in zip(points, points[1:]):
        za, zb = site.ground_height(field, *a), site.ground_height(field, *b)
        for z in (0.22, height - 0.18):
            site.beam(parts, (*a, za + z), (*b, zb + z), 0.037, STEEL)
    if gate:
        for d in np.linspace(0, line.length, 5)[:-1]:
            a = line.interpolate(d).coords[0]
            b = line.interpolate(d + line.length / 4).coords[0]
            za, zb = site.ground_height(field, *a), site.ground_height(field, *b)
            site.beam(parts, (*a, za + height - 0.16), (*b, zb + 0.26), 0.058, STEEL)
    return [
        box(*LineString((a, b)).buffer(0.082).bounds)
        for a, b in zip(points, points[1:])
    ]


def mesh_barrier(parts, a, b, height, width, z_low=0.18):
    p, q = np.asarray(a), np.asarray(b)
    length = float(np.linalg.norm(q[:2] - p[:2]))
    for u in np.linspace(0, 1, int(np.ceil(length / width)) + 1):
        pos = (1 - u) * p + u * q
        site.beam(parts, pos + (0, 0, z_low), pos + (0, 0, height), 0.007, WIRE)
    for v in np.linspace(z_low, height, int(np.ceil((height - z_low) / width)) + 1):
        site.beam(parts, p + (0, 0, v), q + (0, 0, v), 0.007, WIRE)


def net_runs(parts, field, spec):
    count = 0
    for row in spec["net_runs"]:
        z = row["height"]
        coords = [(e, n, site.ground_height(field, e, n)) for e, n in row["points"]]
        for e, n, h in coords:
            site.cylinder_between(
                parts, (e, n, h - 0.1), (e, n, h + z + 0.20), 0.062, STEEL, sides=9
            )
        for a, b in zip(coords, coords[1:]):
            mesh_barrier(parts, a, b, z, 0.65, z_low=0.96)
        count += len(coords)
    e, n = spec["circle"]
    coords = []
    for angle in np.linspace(np.deg2rad(53), np.deg2rad(304), 9):
        x, y = e + 4.55 * np.cos(angle), n + 4.55 * np.sin(angle)
        z = site.ground_height(field, x, y)
        coords.append((x, y, z))
        site.cylinder_between(parts, (x, y, z), (x, y, z + 5.5), 0.058, STEEL)
    for a, b in zip(coords, coords[1:]):
        mesh_barrier(parts, a, b, 5.4, 0.42)
    return count


def goals(parts, spec, level):
    x0, y0, x1, y1 = spec["soccer_bounds"]
    middle = (y0 + y1) / 2
    for x, offset in ((x0, -2.1), (x1, 2.1)):
        lo, hi = middle - 3.66, middle + 3.66
        z0, z1 = level(x, lo), level(x, hi)
        a, b = (x, lo, z0 + 2.35), (x, hi, z1 + 2.35)
        site.beam(parts, (x, lo, z0), a, 0.09, WHITE)
        site.beam(parts, (x, hi, z1), b, 0.09, WHITE)
        site.beam(parts, a, b, 0.09, WHITE)
        back = x + offset
        c, d = (back, lo, level(back, lo)), (back, hi, level(back, hi))
        for p, q in ((a, c), (b, d), (c, d)):
            site.beam(parts, p, q, 0.045, WHITE)
        mesh_barrier(parts, c, d, 0.91, 0.39, z_low=0.05)


def border_planting(parts, ground, field, spec, keep_clear):
    count = 0
    for row in spec["bed_lines"]:
        line = LineString(row["points"])
        bed = line.buffer(row["width"] / 2, cap_style="flat").difference(keep_clear)
        if bed.is_empty:
            continue
        site.drape(ground, field, bed, (126, 115, 86), 0.085, 0.76)
        for d in np.arange(0.46, line.length, 0.96):
            pos = line.interpolate(d)
            if not bed.buffer(-0.13).covers(pos):
                continue
            e, n = pos.coords[0]
            z = site.ground_height(field, e, n)
            h = (0.29, 0.34, 0.26, 0.40)[count % 4]
            site.orb(
                parts,
                (e, n, z + h * 0.71),
                (0.32, 0.36, h * 0.65),
                (96, 113 - count % 4 * 4, 67),
            )
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    spec = site.read(site.root / "data/metadata/hayward-practice-fields.json")
    prior = site.read(site.root / "data/metadata/agate-fifteenth-eighteenth.json")
    manifest, field, graph = east.pinned_site(site.scene, spec)
    buildings, previous = east.build_blockers(
        site.scene, spec, manifest, box(*spec["extent"])
    )
    ground, paint, structures, details = [], [], [], []
    turf, walks, sidewalk, level, fit = ground_layers(ground, field, spec, buildings)
    throwing_lines(paint, field, spec)
    goals(structures, spec, level)
    closed = []
    for row in spec["fences"]:
        closed.extend(fence_run(structures, field, row["line"], row["height"]))
    gate = spec["gate"]
    closed.extend(fence_run(structures, field, gate["line"], gate["height"], gate=True))
    poles = net_runs(structures, field, spec)
    flags = []
    for row in spec["flag_rows"]:
        line = LineString([row["from"], row["to"]])
        flags.extend(
            line.interpolate(d).coords[0]
            for d in np.arange(0, line.length, row["spacing"])
        )
    agate.flagpoles(details, field, flags)
    shrubs = border_planting(
        details, ground, field, spec, walks.union(turf).union(buildings)
    )
    assert len(closed) <= 16
    # The northern step begins on the painted part of Agate's East 18th crossing.
    seam = box(42.9, -602.0, 89, -596.7)
    old_surface = (
        west.surface(prior["walk_joins"])
        .union(agate.agate.longitudinal_band(prior["road"]))
        .union(central.buffered_lines(prior["ramp_ends"], 1.28))
        .intersection(seam)
    )
    edges, lengths = west.check_routes(
        graph,
        spec["routes"],
        walks.union(old_surface),
        buildings.union(previous).union(unary_union(closed)),
    )

    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        (LINES, paint, "landscape-detail"),
        (FENCES, structures, "landscape-detail"),
        (DETAILS, details, "landscape-vegetation"),
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
            context_trees=spec["procedural_placement_cleared"],
            closed_site_boxes_enu_m=[
                [round(x, 4) for x in shape.bounds] for shape in closed
            ],
            walkable_ground=dict(
                paths=spec["routes"],
                bounds_enu_m=[
                    [-149, -603, -65, -595],
                    [-66, -603, 12, -594],
                    [11, -603, 74, -593],
                    [-34, -596.7, 38, -541],
                    [37, -597, 73, -541],
                    [-65, -543, 14, -464],
                    [13, -543, 74, -464],
                ],
            ),
        ),
        compact=True,
    )
    audit = dict(
        turf_m2=round(turf.area, 2),
        turf_grade_coefficients=fit.round(7).tolist(),
        sidewalk_m2=round(sidewalk.area, 2),
        walk_and_apron_m2=round(walks.area, 2),
        fence_m=round(sum(LineString(row["line"]).length for row in spec["fences"]), 2),
        solid_spans=len(closed),
        net_uprights=poles,
        flagpoles=len(flags),
        shrubs=shrubs,
        removed_context_tree_indices=[
            row["index"] for row in spec["procedural_placement_cleared"]
        ],
        route_edges=edges,
        route_length_m=lengths[0],
        faces=faces,
        asset_sha256=site.pin(glb),
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
