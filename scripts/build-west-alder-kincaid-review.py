# SPDX-License-Identifier: Apache-2.0
"""Export the registered Grace, Alder, Kincaid, and west neighborhood exteriors."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import intersects_xy, set_precision
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import trimesh

neighbor = import_module("build-villard-orchard-walnut-review")
agate, fairmount, garden, hilyard, older, east = (
    neighbor.agate,
    neighbor.fairmount,
    neighbor.garden,
    neighbor.hilyard,
    neighbor.older,
    neighbor.east,
)
PACKAGE = "west-alder-kincaid-review"
GROUND = "west-alder-kincaid-approaches"
GLASS = (93, 118, 123)
DARK = (81, 83, 72)
GRILLE = (114, 108, 90)
TRIM = (206, 197, 174)
PALE = (190, 183, 163)
CEMENT = (155, 147, 127)
BLUE = (76, 104, 122)


def xy(e, n):
    return np.array([e, n])


def roof_zones(row, outline):
    origin = np.asarray(row["roof_frame"]["origin_enu_m"])

    def local(bounds):
        return (np.asarray(bounds) - np.tile(origin, 2)).tolist()

    result = [
        dict(
            bounds_m=local(outline.buffer(0.3).bounds),
            planes=[[0, 0, row["cap_z_m"], 0, 0]],
        )
    ]
    for bounds, z in row["elevation_patches"]:
        result.append(dict(bounds_m=local(bounds), planes=[[0, 0, z, 0, 0]]))
    for bounds, axis, crest, top, pitch in row["ridges"]:
        start = crest - origin[axis]
        forms = [[0, 0, top - sign * pitch * start, 0, 0] for sign in (-1, 1)]
        for form, sign in zip(forms, (-1, 1)):
            form[axis + 3] = sign * pitch
        result.append(dict(bounds_m=local(bounds), planes=forms))
    return result


def open_plans(row, wall):
    f = row["features"]
    openings = []
    if "garage" in f:
        openings.append((wall.intersection(box(*f["garage"])), f["garage_ceiling"]))
    if "court_opening" in f:
        openings.append(
            (wall.intersection(box(*f["court_opening"])), f["bridge_bottom"])
        )
    for bounds in f.get("parking", []):
        openings.append((wall.intersection(box(*bounds)), f["parking_ceiling"]))
    for bounds in f.get("recesses", []):
        openings.append((wall.intersection(box(*bounds)), None))
    occupied = orient(wall.difference(unary_union([zone for zone, _ in openings])))
    return occupied, openings


def facade(parts, row, outline, wall, openings, field, roof):
    style, options = row["style"], row["features"]
    levels = row["levels"]
    trim = BLUE if style == "church" else TRIM
    street = options.get("gallery_side") or options.get("balcony")
    direction = np.asarray(hilyard.DIRECTION[street]) if street else None
    gate = options.get("gate")
    gate_position = Point(gate[1:3]) if gate else None
    for edge, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
        if span < 0.82:
            continue
        street_face = direction is not None and normal @ direction > 0.84
        e_mid, n_mid = plan(span / 2, 0)
        if row["city_objectid"] == 171248 and e_mid < -999.65:
            continue
        arcade_front = style == "arcade" and normal[0] > 0.84 and e_mid > -772
        gate_station = (
            edge.project(gate_position)
            if gate_position is not None
            and normal @ hilyard.DIRECTION[gate[0]] > 0.84
            and edge.distance(gate_position) < 0.8
            else None
        )
        outer_face = outline.exterior.distance(Point(plan(span / 2, 0))) < 0.65
        pieces = max(1, round(span / (3.4 if style != "church" else 3.0)))
        if style == "church":
            # Narrow clerestories under the sanctuary eaves and low wings.
            for i in range(pieces):
                u = span * (i + 0.5) / pieces
                top = min(3.25, roof(plan(u, 0)) - 0.26)
                if top > 1.36:
                    older.framed(
                        add,
                        u,
                        min(2.28, span / pieces * 0.76),
                        top - 0.37,
                        top,
                        2,
                        BLUE,
                    )
            add(0.04, span - 0.04, 0.008, 0.105, 1.73, 1.81, BLUE)
            continue
        for floor, z in enumerate(levels):
            for i in range(pieces):
                u = span * (i + 0.5) / pieces
                e, n = plan(u, -0.13)
                if any(
                    ceiling is not None
                    and z + 0.7 < ceiling
                    and shape.covers(Point(e, n))
                    for shape, ceiling in openings
                ):
                    continue
                if arcade_front and abs(n + 653.25) < 3.75:
                    continue
                if (
                    floor == 0
                    and gate_station is not None
                    and abs(u - gate_station) < 1.42
                ):
                    continue
                if (
                    options.get("screened")
                    and street_face
                    and floor == 0
                    and abs(u - span / 2) < min(3.85, span * 0.36) + 0.6
                ):
                    continue
                grade = hilyard.grade(field, (e, n))
                y = max(z + 0.63, grade + 0.72)
                top = min(y + 1.20, roof((e, n)) - 0.27)
                if top - y > 0.49:
                    width = min(span / pieces * 0.56, 1.58)
                    older.framed(add, u, width, y, top, 2, TRIM)
            if floor and outer_face:
                add(0.06, span - 0.06, 0.008, 0.048, z - 0.064, z + 0.031, trim)
            if floor and street_face and span > 6.0:
                if options.get("gallery_side"):
                    deck = fairmount.rectangle(plan, 0.17, span - 0.17, 0.01, 0.97)
                    east.flat(parts, deck, z - 0.14, z - 0.014, CEMENT, PALE)
                    rail = fairmount.rectangle(plan, 0.24, span - 0.24, 0.86, 0.91)
                    east.railing(parts, rail, z - 0.03, 0.90, trim)
                elif style == "housing":
                    older.balcony(add, span * 0.29, span * 0.71, z, trim)
        if style in ("arcade", "talisman", "camelot") and outer_face:
            for u in np.linspace(0.14, span - 0.14, max(2, round(span / 3.85))):
                z = hilyard.grade(field, plan(u, 0)) + (
                    0.21 if style == "arcade" else 1.92
                )
                cap = roof(plan(u, 0)) - 0.33
                if cap > z + 1.3:
                    add(u - 0.08, u + 0.08, 0.009, 0.041, z, cap, (166, 160, 147))
        if options.get("screened") and street_face and span > 7:
            low = hilyard.grade(field, plan(span / 2, 0))
            cap = levels[1] - 0.21
            if cap > low + 1.28:
                half = min(3.85, span * 0.36)
                middle = span / 2
                add(middle - half, middle + half, 0.013, 0.027, low + 0.10, cap, DARK)
                for u in np.arange(middle - half + 0.09, middle + half - 0.04, 0.29):
                    add(u - 0.016, u + 0.016, 0.028, 0.056, low + 0.14, cap, GRILLE)
                start = plan(span * 0.82, 1.45)
                finish = plan(span * 0.47, 0.55)
                if levels[1] - hilyard.grade(field, start) > 0.45:
                    hilyard.northwest.stair(
                        parts,
                        start,
                        finish,
                        hilyard.grade(field, start) + 0.055,
                        levels[1],
                        1.05,
                        steps=11,
                    )
        elif (
            street_face and span > 8 and options.get("gallery_side") and len(levels) > 1
        ):
            start = plan(span * 0.82, 1.44)
            finish = plan(span * 0.52, 0.59)
            if levels[1] - hilyard.grade(field, start) > 0.55:
                hilyard.northwest.stair(
                    parts,
                    start,
                    finish,
                    hilyard.grade(field, start) + 0.05,
                    levels[1],
                    1.0,
                    steps=12,
                )


def arcade_frontage(parts, wall, field):
    edge, (span, add, _, plan, _, _) = hilyard.face_on(
        parts, wall, xy, "E", [-767.61, -653.25]
    )
    center = edge.project(Point(-767.61, -653.25))
    left, right = max(0.1, center - 3.72), min(span - 0.1, center + 3.72)
    ground = hilyard.grade(field, plan(center, 0))
    sill = ground + 0.08
    head = 16.82
    add(left, right, 0.015, 0.061, sill, head, (182, 180, 173))
    add(
        left + 0.16,
        right - 0.16,
        0.064,
        0.093,
        sill + 0.11,
        head - 0.23,
        (101, 137, 143),
    )
    for u in np.linspace(left + 0.13, right - 0.13, 7):
        add(
            u - 0.042,
            u + 0.042,
            0.094,
            0.135,
            sill + 0.09,
            head - 0.12,
            (216, 211, 191),
        )
    for z in [sill + 2.11, 8.20, 9.56, 11.08, 12.49, 14.03, 15.39, 16.72]:
        if z < head:
            add(left, right, 0.097, 0.138, z - 0.043, z + 0.047, (214, 210, 192))
    add(left, right, 0.08, 1.40, sill + 2.46, sill + 2.60, (190, 185, 168))
    add(center - 0.76, center + 0.76, 0.140, 0.162, sill, sill + 2.15, (116, 133, 134))
    for u in (center - 0.76, center, center + 0.76):
        add(u - 0.048, u + 0.048, 0.162, 0.201, sill, sill + 2.16, TRIM)


def west_screen(parts, wall):
    _, (span, add, _, _, _, _) = hilyard.face_on(
        parts, wall, xy, "N", [-986.0, -376.19]
    )
    for u in np.linspace(0.7, span - 0.7, 5):
        add(u - 0.10, u + 0.10, 0.043, 0.16, -2.03, 0.57, (173, 168, 145))
    if span > 8:
        add(0.11, span - 0.11, 0.065, 0.23, 0.512, 0.676, (150, 149, 130))


def church_front(parts, wall, roof):
    _, (span, add, _, plan, _, panel) = hilyard.face_on(
        parts, wall, xy, "N", [-882.1, -498.55]
    )
    corners = []
    for x in np.linspace(0.1, span - 0.1, 60):
        e, n = plan(x, 0)
        z = roof((e, n)) - 0.21
        if -889.3 < e < -870.1 and z > 2.2:
            corners.append((x, z))
    if len(corners) > 1:
        a, b = corners[0][0], corners[-1][0]
        shape = Polygon([(a, 2.02), (b, 2.02), *reversed(corners)])
        panel(orient(shape), 0.03, 0.07, (204, 198, 176))
        for x in np.linspace(a + 0.15, b - 0.15, 5):
            z = min(5.07, roof(plan(x, 0)) - 0.23)
            if z > 2.42:
                add(x - 0.038, x + 0.038, 0.074, 0.105, 2.12, z, PALE)
    for u in np.linspace(max(0.45, span * 0.15), min(span - 0.45, span * 0.85), 6):
        add(u - 0.095, u + 0.095, 0.02, 0.069, 1.91, 2.23, BLUE)


def decorated_entry(parts, paving, row, occupied, field):
    gate = row["features"].get("gate")
    if gate is None:
        return []
    side, e, n, distance = gate
    edge, (_, _, _, _, _, _) = hilyard.face_on(parts, occupied, xy, side, [e, n])
    position = edge.interpolate(edge.project(Point(e, n)))
    height = hilyard.grade(field, (position.x, position.y)) + 0.105
    return east.entry_gate(
        parts,
        paving,
        {
            **row,
            "entrance": dict(
                side=side,
                near=[e, n],
                height=height,
                door=(102, 104, 94),
                gate="street-entry",
                distance=distance,
            ),
        },
        occupied,
        field,
        xy,
    )


def build(row, field, paving):
    outline = orient(
        set_precision(Polygon(row["outline_enu_m"], row["holes_enu_m"]), 0.002)
    )
    wall = orient(
        outline.buffer(-row["features"].get("eaves", 0.18), join_style="mitre")
    )
    occupied, openings = open_plans(row, wall)
    parts, supports = [], []
    roof = garden.roof_sections(
        parts,
        outline,
        occupied,
        row["base_z_m"],
        {
            **row,
            "roof_zones": roof_zones(row, outline),
        },
        grid=0.0002,
    )
    for opening, ceiling in openings:
        neighbor.drape(paving, field, opening, (163, 156, 138), 0.051)
        if ceiling is not None:
            for polygon in fairmount.geometry.sections(opening):
                if polygon.area < 0.03:
                    continue
                parts.append(
                    fairmount.geometry.shell(
                        orient(polygon),
                        ceiling,
                        lambda e, n: roof((e, n)) - 0.151,
                        row["wall_color"],
                        row["wall_color"],
                    )
                )

    for e, n in row["features"].get("posts", []):
        footprint = box(e - 0.112, n - 0.112, e + 0.112, n + 0.112)
        ceiling = min(
            roof((e, n)) - 0.145, row["features"].get("garage_ceiling", float("inf"))
        )
        hilyard.pier(parts, field, footprint, ceiling, TRIM)
        supports.append(footprint)
    if row["style"] == "arcade":
        # The wells are open through the upper roof and terminate at modeled terraces.
        lower = []
        for hole in outline.interiors:
            plan = Polygon(hole).buffer(0.19)
            east.flat(
                parts,
                plan,
                row["base_z_m"],
                row["features"]["upper_court_bottom"],
                CEMENT,
                PALE,
            )
            lower.append(plan)
        occupied = orient(unary_union([occupied, *lower]))
    is_church = row["style"] == "church"
    visible_wall = occupied if is_church else wall
    facade(parts, row, outline, visible_wall, openings, field, roof)
    if is_church:
        church_front(parts, wall, roof)
    if row["style"] == "arcade":
        arcade_frontage(parts, wall, field)
    if row["features"].get("window_screen"):
        west_screen(parts, wall)
    if row["style"] == "camelot":
        source = row["features"]["court_opening"]
        end = np.array([(source[0] + source[2]) / 2, source[1] + 0.44])
        start = end + np.array([0, 4.5])
        grade = hilyard.grade(field, start)
        hilyard.northwest.stair(
            parts, start, end, grade + 0.035, grade + 1.23, 2.10, steps=7
        )
    extra = []
    for ring in row["secondary_outline_enu_m"]:
        outline_piece = orient(Polygon(ring))
        solid = orient(outline_piece.buffer(-0.14, join_style="mitre"))
        east.flat(
            parts, solid, row["base_z_m"], row["cap_z_m"] - 0.15, row["wall_color"]
        )
        east.flat(
            parts,
            outline_piece,
            row["cap_z_m"] - 0.15,
            row["cap_z_m"],
            TRIM,
            row["roof_color"],
        )
        facade(parts, row, outline_piece, solid, [], field, lambda p: row["cap_z_m"])
        extra.append(solid)
    gates = decorated_entry(parts, paving, row, occupied, field)
    mesh, record, _, supports = agate.output(
        parts, row, outline, set_precision(occupied, 0), supports, gates
    )
    if extra:
        record["ground_footprints_enu_m"].extend(
            agate.base.ring(piece) for piece in extra
        )
        record["area_m2"] = round(
            outline.area
            + sum(Polygon(ring).area for ring in row["secondary_outline_enu_m"]),
            3,
        )
    return mesh, record, unary_union([occupied, *extra]), supports


def source_removals(spec, config, audit):
    special = spec["overlapping_source_range"]
    ident = special["id"]
    ordinary = [row for row in spec["source_ranges"] if row["id"] != ident]
    remove = garden.shared.frohnmayer.source_removals
    patches = remove({"absorbed_batches": ordinary}, config, audit)
    item = next(row for row in spec["source_ranges"] if row["id"] == ident)
    asset = fairmount.SCENE / config["asset_url"]
    assert garden.tools.digest(asset) == special["sha256"] == config["asset_sha256"]
    model = trimesh.load(asset, force="scene", process=False)
    transform, key = model.graph[item["target"]]
    assert np.array_equal(transform, np.eye(4))
    triangles = model.geometry[key].triangles
    plans = {
        row["id"]: Polygon(row["footprint_enu_m"]) for row in audit["appearance_plan"]
    }
    members = audit["context_batches"][item["target"]]
    peer = special["peer_id"]
    a, b = special["triangles"]
    c, d = special["peer_triangles"]
    assert (
        peer in members and ident in members and 0 <= c < d <= a < b <= len(triangles)
    )
    for name, lo, hi in ((ident, a, b), (peer, c, d)):
        hits = intersects_xy(
            plans[name].buffer(0.29), triangles[:, :, 0], -triangles[:, :, 2]
        ).all(axis=1)
        if name == ident:
            hits[c:d] = False
        assert np.array_equal(np.flatnonzero(hits), np.arange(lo, hi)), name
    vertices = triangles[a:b].reshape(-1, 3)
    patches.append(
        {
            **item,
            "triangles": [a, b],
            "source_triangle_count": len(triangles),
            "source_vertices": [
                [i, vertices[i].round(6).tolist()]
                for i in (0, len(vertices) // 2, len(vertices) - 1)
            ],
        }
    )
    return patches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(),
        PACKAGE,
        GROUND,
        "west_alder_kincaid_site",
        build,
        source_removals=source_removals,
    )


if __name__ == "__main__":
    main()
