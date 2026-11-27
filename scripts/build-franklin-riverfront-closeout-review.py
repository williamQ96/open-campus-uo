# SPDX-License-Identifier: Apache-2.0
"""Export three registered Franklin properties and the recovered riverfront parking."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.affinity import affine_transform
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import trimesh

precedent = import_module("build-hamilton-dunes-review")
hotel = import_module("build-garden-franklin-review")
terrain = precedent.terrain
fairmount, geometry, grade = precedent.fairmount, precedent.geometry, precedent.grade
cap, ring, read, digest = (
    precedent.cap,
    precedent.ring,
    precedent.read,
    precedent.digest,
)
chapter = fairmount.chapter
top_surface = precedent.top_surface

PACKAGE = "franklin-riverfront-closeout-review"
GROUND = "franklin-riverfront-paving"
FRAME = (187, 187, 174)
GLASS = (82, 111, 125)
CHARCOAL = (67, 74, 76)
SLATE = (93, 103, 103)
WHITE = (214, 212, 194)
TAN = (170, 159, 137)
DARK = (76, 77, 69)
CONCRETE = (153, 152, 136)
ASPHALT = (116, 116, 106)
WATER = (103, 166, 170)
ORANGE = (158, 119, 77)


def shapes(region):
    return sorted(
        (
            orient(p)
            for p in geometry.sections(set_precision(region, 0.001))
            if p.area >= 0.008
        ),
        key=lambda p: (-p.area, *p.bounds),
    )


def mass(parts, shape, base, top, wall, roof=None):
    for piece in shapes(shape):
        parts.append(cap(piece, base, top, wall, roof))


def outside_faces(parts, plan):
    for region in shapes(plan):
        yield from fairmount.views(parts, region)


def grade_surface(parts, field, area, color, cap_offset=0.088):
    if area.area > 0.05:
        top_surface(
            parts, area, lambda e, n: grade(field, (e, n)) + cap_offset, color, cell=1.8
        )


def base_level(field, plan):
    return min(grade(field, p) for p in plan.exterior.coords) - 0.26


def portal(parts, paving, field, wall, hint, width=2.0, distance=3.3):
    edge, (span, add, normal, plan, _, _) = min(
        ((e, info) for e, info in outside_faces(parts, wall) if info[0] >= width + 0.6),
        key=lambda row: row[0].distance(Point(hint)),
    )
    u = np.clip(edge.project(Point(hint)), width / 2 + 0.18, span - width / 2 - 0.18)
    point = plan(u, 0)
    z = grade(field, point) + 0.06
    hotel.framed(add, u - width / 2, width, z + 0.02, z + 2.38, 2, FRAME)
    apron = fairmount.rectangle(
        plan, u - width * 0.74, u + width * 0.74, 0.02, distance
    )
    grade_surface(paving, field, apron, (172, 167, 149))
    return dict(
        gate="street-entry",
        position_enu_m=np.round(point, 4).tolist(),
        outward_degrees=round(float(np.degrees(np.arctan2(*normal)) % 360), 4),
        approach_distance_m=distance,
    )


def mitered_roof(parts, plan, align, eave, ridge, color):
    along = np.array(align, dtype=float)
    along /= np.linalg.norm(along)
    across = np.array([-along[1], along[0]])
    origin = np.array(plan.centroid.coords[0])
    local = affine_transform(plan, [*along, *across, -along @ origin, -across @ origin])
    a, b, c, d = local.bounds
    pitch = 2 * (ridge - eave) / min(c - a, d - b)
    controls = [
        np.array([pitch, 0, eave - pitch * a]),
        np.array([-pitch, 0, eave + pitch * c]),
        np.array([0, pitch, eave - pitch * b]),
        np.array([0, -pitch, eave + pitch * d]),
    ]
    world = [along[0], across[0], along[1], across[1], *origin]
    for control in controls:
        layer = local
        for other in controls:
            if other is not control and not layer.is_empty:
                layer = layer.intersection(
                    chapter.half_plane(local.bounds, control - other)
                )
        dx = control[0] * along + control[1] * across
        intercept = control[2] - dx @ origin
        for region in shapes(affine_transform(layer, world)):

            def z(e, n):
                return float(dx @ [e, n] + intercept)

            parts.append(geometry.shell(region, eave - 0.19, z, color, color))


def balcony_front(parts, wall, court, field, trim, levels):
    for edge, (span, add, normal, plan, _, _) in outside_faces(parts, wall):
        if span < 2.1:
            continue
        target = np.array(court) - plan(span / 2, 0)
        inside = normal @ target > 0.35 * np.linalg.norm(target)
        for z in levels:
            if inside:
                hotel.balcony(add, 0.17, span - 0.17, z, trim)
                for pos in np.arange(0.28, span - 0.25, 4.65):
                    add(pos - 0.05, pos + 0.05, 0.84, 1.01, z - 0.14, z + 2.16, trim)
            for u in np.arange(1.25, span - 1.18, 3.8):
                top = z + 1.8
                if top - grade(field, plan(u, 0)) > 0.5:
                    hotel.framed(add, u - 0.73, 1.46, z + 0.32, top, 2, trim)
        if inside and levels:
            add(
                0.09,
                span - 0.09,
                0.04,
                0.77,
                levels[-1] + 2.21,
                levels[-1] + 2.34,
                trim,
            )


def tower_elevation(parts, shape, base, height, base_bands, street_axis):
    section_span = (height - base) / len(base_bands)
    across = np.array([-street_axis[1], street_axis[0]])
    for _, (span, add, normal, plan, _, _) in outside_faces(parts, shape):
        if span < 1.75:
            continue
        frontage = abs(normal @ across) > 0.82
        count = max(1, round(span / (2.38 if frontage else 2.80)))
        pitch = span / count
        for i in range(count):
            u = i * pitch
            panel = (
                SLATE if i % 5 in (1, 4) else FRAME if i % 5 == 2 else (168, 174, 170)
            )
            add(
                u + 0.028,
                u + pitch - 0.028,
                0.010,
                0.049,
                base + 0.031,
                height - 0.16,
                panel,
            )
            if frontage and i % 7 == 0 and pitch > 1.2:
                add(
                    u + 0.19, u + 0.259, 0.05, 0.082, base + 0.05, height - 0.17, ORANGE
                )
            if pitch > 1.6:
                for j in base_bands:
                    z = base + j * section_span
                    low = z + 0.51
                    high = min(height - 0.24, z + section_span - 0.23)
                    if high - low > 0.65:
                        hotel.framed(
                            add, u + 0.30, pitch * 0.56, low, high, 1, (131, 145, 145)
                        )
        for j in base_bands:
            z = base + j * section_span
            add(0.075, span - 0.075, 0.051, 0.136, z + 0.09, z + 0.20, (112, 122, 118))
        add(0.038, span - 0.038, 0.026, 0.18, height - 0.27, height + 0.09, CHARCOAL)


def dock_elevation(parts, body, field, bottom, upper, axis):
    forward = np.array([axis[1], -axis[0]])
    for _, (span, add, normal, plan, _, _) in outside_faces(parts, body):
        if span < 2.05:
            continue
        frontage = normal @ forward > 0.64
        height = upper - bottom
        count = max(1, round(span / 2.82))
        for band in range(3):
            z = bottom + height * (0.25 + band * 0.237)
            add(0.10, span - 0.10, 0.023, 0.114, z - 0.065, z + 0.134, FRAME)
            for col in range(count):
                u = (col + 0.5) * span / count
                if span / count < 1.12:
                    continue
                add(
                    u - 0.52,
                    u + 0.51,
                    0.018,
                    0.071,
                    z + 0.19,
                    z + 1.80,
                    (147, 157, 151),
                )
                for slit in np.arange(0.31, 1.65, 0.18):
                    add(
                        u - 0.49,
                        u + 0.48,
                        0.071,
                        0.085,
                        z + slit,
                        z + slit + 0.02,
                        (112, 124, 119),
                    )
                if col % 3 == 0:
                    hotel.framed(add, u - 0.35, 0.66, z + 0.24, z + 1.66, 1)
        if frontage:
            for u in np.arange(1.23, span - 1.05, 2.65):
                low = grade(field, plan(u, 0))
                if low < bottom + height * 0.24 - 0.65:
                    hotel.framed(
                        add,
                        u - 0.84,
                        1.68,
                        low + 0.16,
                        bottom + height * 0.24 - 0.035,
                        2,
                        CHARCOAL,
                    )


def tower(parts, field, paving, model, outline):
    grade0 = base_level(field, outline)
    podium = outline.buffer(-0.45, join_style="mitre")
    axis = np.asarray(model["street_axis"], dtype=float)
    axis /= np.linalg.norm(axis)
    access = np.asarray(model["parking_entry_enu_m"])
    perpendicular = np.array([-axis[1], axis[0]])
    patch, _, _ = hotel.transforms(
        {"roof_frame": {"origin_enu_m": access, "axis": axis}}
    )
    cut = patch((-3.75, -5.7, 3.75, 5.45)).intersection(podium)
    mass(
        parts,
        podium.difference(cut),
        grade0,
        model["podium_z_m"],
        (152, 160, 157),
        (160, 167, 156),
    )
    garage_soffit = max(grade(field, p) for p in cut.exterior.coords) + 2.70
    mass(parts, cut, garage_soffit, model["podium_z_m"], (144, 153, 154))
    grade_surface(paving, field, patch((-3.58, -6.4, 3.58, 5.20)), ASPHALT)
    dock_elevation(
        parts, podium.difference(cut), field, grade0, model["podium_z_m"], axis
    )

    upper = Polygon(model["tower_enu_m"]).intersection(podium).buffer(0)
    split = model["roof_split_east_m"]
    top_area = upper.intersection(box(-650, 290, split, 415))
    east_area = upper.difference(top_area)
    pool = Polygon(model["pool_enu_m"])
    spa = Polygon(model["spa_enu_m"])
    amenity = (
        Polygon(model["pool_deck_enu_m"])
        .union(pool.buffer(0.50))
        .union(spa.buffer(0.45))
        .intersection(podium)
    )
    amenity = amenity.difference(upper)
    assert amenity.buffer(0.004).covers(pool) and amenity.buffer(0.004).covers(spa)
    spec = [(top_area, model["main_roof_z_m"]), (east_area, model["east_roof_z_m"])]
    for shape, z in spec:
        mass(parts, shape, model["podium_z_m"] - 0.02, z, (172, 179, 172), WHITE)
        tower_elevation(parts, shape, model["podium_z_m"], z, range(8), axis)
    deck = model["deck_z_m"]
    mass(
        parts,
        amenity.difference(pool.union(spa)),
        model["podium_z_m"] - 0.05,
        deck,
        (152, 164, 151),
        (157, 148, 127),
    )
    terrace_walls = amenity
    for _, (span, add, normal, plan, _, _) in outside_faces(parts, terrace_walls):
        if span < 2.1 or upper.buffer(0.09).covers(Point(plan(span / 2, 0.08))):
            continue
        add(0.025, span - 0.025, 0.025, 0.145, deck - 0.29, deck + 0.025, SLATE)
        for floor in range(7):
            z = model["podium_z_m"] + 3.26 * floor + 0.09
            if z + 2.45 >= deck - 0.22:
                continue
            add(0.03, span - 0.03, 0.011, 0.088, z + 0.015, z + 0.21, WHITE)
            add(0.03, span - 0.03, 0.081, 0.153, z + 2.64, z + 2.83, SLATE)
            for u in np.arange(1.05, span - 0.86, 2.22):
                hotel.framed(
                    add, u - 0.61, 1.22, z + 0.40, z + 2.29, 1, (156, 172, 166)
                )
    for basin in (pool, spa):
        mass(parts, basin, deck - 0.65, deck - 0.16, (98, 147, 151), WATER)
        mass(
            parts,
            basin.buffer(0.17).difference(basin),
            deck - 0.13,
            deck + 0.11,
            (218, 211, 180),
            WHITE,
        )
    terrain.east.railing(parts, amenity, deck, 1.06, (124, 146, 145))
    for e, n, w, d in (
        (-567, 382, 4.3, 3.2),
        (-553, 370, 2.0, 4.9),
        (-544, 357, 3.4, 2.1),
        (-524, 353, 5.1, 3.1),
        (-513, 344, 2.5, 3.6),
        (-497, 344.6, 3.0, 2.6),
    ):
        piece = box(e - w / 2, n - d / 2, e + w / 2, n + d / 2)
        for shape, z in spec:
            mass(
                parts,
                shape.buffer(-0.26).intersection(piece),
                z - 0.09,
                z + 1.15,
                (142, 155, 147),
                WHITE,
            )
    gates = [
        portal(
            parts,
            paving,
            field,
            podium.difference(cut),
            model["street_entry_enu_m"],
            2.1,
            3.65,
        )
    ]
    assert not podium.difference(cut).covers(Point(*(access + perpendicular * 3.0)))
    return podium.difference(cut), [], gates


def raised_hotel(parts, field, paving, model, outline):
    axis = np.asarray(model["long_axis"], dtype=float)
    axis /= np.linalg.norm(axis)
    across = np.array([axis[1], -axis[0]])
    origin = np.array(outline.centroid.coords[0])
    _, local, _ = hotel.transforms(
        {"roof_frame": {"origin_enu_m": origin, "axis": axis}}
    )
    # The back is on the left of the building axis. The balconies face the east parking aisle.
    east_boundary = min(local(p)[1] for p in outline.exterior.coords)
    west_edges = max(local(p)[1] for p in outline.exterior.coords)
    threshold = (
        east_boundary + (west_edges - east_boundary) * model["depth_fraction_covered"]
    )
    ird = [*axis, -across[0], -across[1], -axis @ origin, across @ origin]
    loc = affine_transform(outline, ird)
    aft = loc.intersection(box(-100, threshold, 100, 100))
    world = [axis[0], -across[0], axis[1], -across[1], *origin]
    wall = (
        affine_transform(aft, world)
        .intersection(outline)
        .buffer(-0.11, join_style="mitre")
    )
    assert 0.20 < wall.area / outline.area < 0.66
    foot = base_level(field, outline)
    overhead = model["carport_soffit_z_m"]
    z = model["shell_z_m"]
    mass(parts, wall, foot, overhead + 0.18, (109, 109, 100))
    mass(parts, outline, overhead, z, (148, 138, 119), WHITE)
    supports = []
    for edge, (span, add, normal, plan, _, _) in outside_faces(parts, outline):
        if span < 2.0:
            continue
        facing = normal @ across > 0.73
        if facing:
            for j in (overhead + 0.26, overhead + 3.20):
                if span > 3.70:
                    hotel.balcony(add, 0.06, span - 0.06, j, (99, 88, 72))
                for u in np.arange(1.30, span - 1.12, 3.05):
                    hotel.framed(
                        add, u - 0.75, 1.49, j + 0.39, j + 2.17, 2, (199, 190, 166)
                    )
            for u in np.arange(0.45, span - 0.28, 4.41):
                column = Point(plan(u, -0.11)).buffer(0.143, quad_segs=1)
                mass(
                    parts,
                    column,
                    base_level(field, column),
                    overhead + 0.2,
                    (116, 105, 88),
                )
                supports.append(column)
            for u in np.arange(0.48, span - 0.3, 3.05):
                add(
                    u - 0.066,
                    u + 0.066,
                    0.008,
                    0.80,
                    overhead + 0.15,
                    z - 0.26,
                    (123, 102, 81),
                )
            add(0.03, span - 0.03, 0.028, 1.02, z - 0.25, z - 0.01, (99, 95, 83))
        else:
            base = overhead if not wall.buffer(0.50).intersects(edge) else foot
            for zz in np.arange(base + 0.16, z - 0.13, 0.226):
                add(0.02, span - 0.02, 0.009, 0.038, zz, zz + 0.023, (109, 114, 111))
    occupied = outline.difference(wall.union(unary_union(supports)))
    grade_surface(paving, field, occupied, ASPHALT)
    return wall, supports, []


def lodge(parts, field, paving, model, outline):
    west = model["kind"] == "west"
    base = base_level(field, outline)
    if west:
        walls = outline.buffer(-0.52, join_style="mitre")
        eave = model["eaves_z_m"]
        mass(parts, walls, base, eave, TAN)
        first = outline.intersection(box(85, 125, 104.2, 192.5))
        second = outline.difference(first)
        for shape, az in ((first, (0, 1)), (second, (0.927, 0.375))):
            for piece in shapes(shape):
                mitered_roof(
                    parts, piece, az, eave, model["ridge_z_m"], (116, 118, 103)
                )
        balcony_front(
            parts, walls, model["court_reference"], field, DARK, (eave - 2.58,)
        )
        court = Polygon(model["court_enu_m"]).difference(walls)
        parking(paving, field, court, (0.08, 0.997), np.arange(-18, 21, 2.7))
        return walls, [], []

    canopy = Polygon(model["drive_cover_enu_m"]).intersection(outline)
    lobby = outline.intersection(Polygon(model["lobby_cut_enu_m"])).difference(canopy)
    wing = outline.difference(lobby.union(canopy))
    wing_ground = wing.buffer(-0.56, join_style="mitre")
    vestibule = lobby.buffer(-0.38, join_style="mitre")
    walls = unary_union((wing_ground, vestibule))
    z = model["lodge_roof_z_m"]
    mass(parts, wing_ground, base, z - 0.20, TAN)
    mass(parts, wing, z - 0.21, z, (189, 182, 162), WHITE)
    balcony_front(
        parts, wing_ground, model["court_reference"], field, (126, 107, 88), (z - 2.47,)
    )
    top = model["lobby_eaves_z_m"]
    mass(parts, vestibule, base, top, (131, 120, 107))
    for area in shapes(lobby):
        mitered_roof(
            parts, area, (0.963, -0.270), top, model["lobby_roof_z_m"], (112, 113, 98)
        )
    for side, (span, add, normal, plan, _, _) in outside_faces(parts, vestibule):
        if span < 2.2:
            continue
        low = grade(field, plan(span / 2, 0)) + 0.29
        for u in np.arange(0.27, span - 1.46, 2.22):
            hotel.framed(
                add, u, 1.57, low, min(top - 0.18, low + 3.52), 2, (94, 84, 73)
            )
        add(0.03, span - 0.03, 0.02, 0.13, top - 0.21, top + 0.02, DARK)
    mass(parts, canopy, 2.61, 3.08, (142, 127, 105), (158, 150, 131))
    for piece in shapes(canopy):
        mitered_roof(parts, piece, (0.01, 1), 3.07, 4.10, (118, 116, 101))
    supports = []
    for e, n in ((117.68, 143.89), (119.42, 136.03), (121.0, 145.2), (120.9, 134.2)):
        column = Point(e, n).buffer(0.235, quad_segs=1)
        if canopy.buffer(-0.26).covers(column):
            mass(parts, column, base_level(field, column), 2.67, (130, 111, 92))
            supports.append(column)
    strip = Polygon(model["court_enu_m"]).difference(walls)
    parking(paving, field, strip, (0.267, 0.964), np.arange(-28, 29, 2.65))
    grade_surface(paving, field, canopy, CONCRETE)
    gates = [
        portal(parts, paving, field, vestibule, model["entry_hint_enu_m"], 2.41, 3.34)
    ]
    return walls, supports, gates


def record(parts, row, outline, wall, supports, gates, base):
    mesh = precedent.ordered_mesh(trimesh.util.concatenate(parts))
    occupied = [ring(region) for region in shapes(wall)]
    assert occupied
    result = dict(
        id=row["id"],
        name=row["name"],
        street_address=row["street_address"],
        footprint_enu_m=ring(outline),
        area_m2=round(outline.area, 3),
        ground_footprints_enu_m=occupied,
        support_collision_enu_m=[ring(s) for s in supports],
        base_z_m=round(float(mesh.bounds[0, 1]), 4),
        roof_z_m=round(float(mesh.bounds[1, 1]), 4),
        entrances=gates,
    )
    assert result["base_z_m"] < result["roof_z_m"] and base <= result["base_z_m"] + 0.8
    return mesh, result, wall, supports


def build(row, field, paving):
    outline = orient(Polygon(row["outline_enu_m"]))
    parts = []
    kind = row["kind"]
    builder = {"tower": tower, "raised": raised_hotel, "motel": lodge, "west": lodge}[
        kind
    ]
    wall, supports, gates = builder(parts, field, paving, row, outline)
    return record(
        parts, row, outline, wall, supports, gates, base_level(field, outline)
    )


def parking(parts, field, shape, axis, lengths):
    grade_surface(parts, field, shape, ASPHALT)
    p = shape.representative_point()
    patch, _, _ = hotel.transforms(
        {"roof_frame": {"origin_enu_m": p.coords[0], "axis": axis}}
    )
    for x in lengths:
        for low, high in ((-11, -6), (0.4, 5.3)):
            line = patch((x - 0.044, low, x + 0.044, high)).intersection(
                shape.buffer(-1.2)
            )
            grade_surface(parts, field, line, (178, 164, 126), 0.104)


def parking_replacements(field, spec, parts):
    parking(
        parts,
        field,
        Polygon(spec["river_west_parking_enu_m"]),
        (0.837, -0.548),
        np.arange(-20, 23, 2.66),
    )
    parking(
        parts,
        field,
        Polygon(spec["hayward_south_parking_enu_m"]),
        (0.277, 0.961),
        np.arange(-14, 17, 2.65),
    )

    east_lot = Polygon(spec["hayward_east_parking_enu_m"]).difference(
        Polygon(spec["models"][1]["outline_enu_m"])
    )
    parking(parts, field, east_lot, (0.277, 0.961), np.arange(-24, 25, 2.65))


def certify(spec, config, audit):
    path = fairmount.SCENE / config["asset_url"]
    assert digest(path) == config["asset_sha256"] == spec["source_presentation_sha256"]
    raw = trimesh.load(path, force="scene", process=False)
    for batch in spec["source_batches"]:
        node = batch["target"]
        assert audit["context_batches"][node] == batch["members"]
        matrix, mesh = raw.graph[node]
        assert np.array_equal(matrix, np.eye(4))
        triangles = raw.geometry[mesh].triangles
        lookup = {i: (a, b) for i, a, b in batch["verified_order"]}
        for r in batch["removals"]:
            a, b = r["triangles"]
            assert len(triangles) == r["source_triangle_count"]
            assert (a, b) == lookup[r["id"]]
            for j, point in r["source_vertices"]:
                assert (
                    np.linalg.norm(triangles[a:b].reshape(-1, 3)[j] - point) < 0.000002
                )
    return spec["source_ranges"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    # The common export helper invokes this site's builds before the first solid.
    spec = read(fairmount.ROOT / f"data/metadata/{PACKAGE}.json")

    def with_parking(row, field, paving):
        if row["id"] == spec["models"][0]["id"]:
            parking_replacements(field, spec, paving)
        return build(row, field, paving)

    fairmount.export_review(
        args,
        PACKAGE,
        GROUND,
        "franklin_riverfront_site",
        with_parking,
        source_removals=certify,
    )


if __name__ == "__main__":
    main()
