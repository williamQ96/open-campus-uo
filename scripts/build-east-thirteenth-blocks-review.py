# SPDX-License-Identifier: Apache-2.0
"""Export the Alder storefront row and East 13th–14th exteriors."""

import argparse
from importlib import import_module
from itertools import pairwise
import json
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient

northwest = import_module("build-northwest-blocks-review")
agate, fairmount, garden, hilyard, older, southwest = (
    northwest.agate,
    northwest.fairmount,
    northwest.garden,
    northwest.hilyard,
    northwest.older,
    northwest.southwest,
)
PACKAGE = "east-thirteenth-blocks-review"
PAVING = "east-thirteenth-blocks-paving"
GLASS = ((94, 120, 133), (112, 143, 151), (124, 145, 153), (106, 134, 145))
FRAME = (77, 94, 105)
STONE = (174, 163, 143)
METAL = (113, 126, 126)


def flat(parts, shape, bottom, top, sides, roof=None):
    for piece in fairmount.geometry.sections(shape):
        if piece.area > 0.012:
            agate.base.flat(parts, orient(piece), bottom, top, sides, roof)


def awning(parts, wall, world, spec):
    side, target, stations, level, color = spec
    (_, add, _, _, _, panel), left, right = northwest.frontage(
        parts, wall, world, side, target, stations
    )
    if right - left > 0.42:
        add(left, right, 0.017, 0.81, level - 0.07, level + 0.055, color)
        panel(orient(box(left, level - 0.14, right, level + 0.04)), 0.794, 0.84, color)


def entry_gate(parts, paving, row, wall, field, world):
    spec = row.get("entrance")
    if spec is None:
        return []
    edge, (_, add, normal, _, _, _) = hilyard.face_on(
        parts, wall, world, spec["side"], spec["near"]
    )
    position = edge.interpolate(edge.project(Point(world(*spec["near"]))))
    hilyard.potter.door(add, edge.project(position), spec["height"], spec["door"])
    bearing = float(np.degrees(np.arctan2(normal[0], normal[1])) % 360)
    gate = dict(
        gate=spec["gate"],
        bearing=bearing,
        threshold_z_m=spec["height"],
        width_m=1.13,
        distance_m=spec["distance"],
        stair_run_m=min(1.85, spec["distance"] * 0.46),
    )
    return [
        hilyard.frontages.estimated_entry(
            paving,
            {**row, "entry": gate, "entry_finish": "stone"},
            field,
            edge,
            position,
        )
    ]


def bands_top(parts, area, levels, tint):
    for _, (span, add, _, _, _, _) in fairmount.views(parts, area):
        if span < 0.35:
            continue
        for z in levels:
            add(0.02, span - 0.02, 0.007, 0.086, z - 0.062, z + 0.056, tint)


def railing(parts, shape, z, rail_height, tone):
    for _, (span, add, _, _, _, _) in fairmount.views(parts, shape):
        if span < 0.32:
            continue
        add(0, span, -0.025, 0.025, z + rail_height - 0.045, z + rail_height, tone)
        for u in np.linspace(0.017, span - 0.017, 2 + int(span / 0.85)):
            add(u - 0.022, u + 0.022, -0.029, 0.029, z, z + rail_height, tone)


def base_glazing(parts, row, shape, field, *, sides):
    for _, (span, add, normal, plan, _, _) in fairmount.views(parts, shape):
        if span < 0.85:
            continue
        side = max(hilyard.DIRECTION, key=lambda side: normal @ hilyard.DIRECTION[side])
        if side not in sides:
            continue
        count = max(1, round(span / (3.4 if row["treatment"] == "patterson" else 2.85)))
        z_top = row["podium_top"] - 0.44
        for i in range(count):
            left, right = i * span / count + 0.09, (i + 1) * span / count - 0.09
            middle = (left + right) / 2
            z = hilyard.grade(field, plan(middle, 0)) + 0.34
            if z_top - z > 1:
                hilyard.glazed(add, left, right, z, z_top, row["trim_color"])
            if right - left > 1.42:
                add(
                    left - 0.077,
                    left + 0.09,
                    0.024,
                    0.19,
                    z - 0.21,
                    z_top + 0.26,
                    STONE,
                )
        add(
            0.04,
            span - 0.04,
            0.008,
            0.17,
            z_top + 0.08,
            z_top + 0.24,
            row["trim_color"],
        )


def patterson_bays(parts, row, footprint, lower, upper, *, courtyard=False):
    west, _, _, north = footprint.bounds
    ring = orient(footprint, sign=-1 if courtyard else 1).exterior.coords
    for start, end in pairwise(ring):
        span, add, normal, plan, _, _ = fairmount.chapter.setup_face(parts, start, end)
        if span < 1.15:
            continue
        count = max(1, round(span / 3.13))
        width = span / count
        for j in range(count):
            u = (j + 0.5) * width
            e, n = plan(u, 0)
            warm = n >= north - 9.0 and e <= west + 12.6
            level_cap = lower if n < row["south_terrace_n"] - 0.1 else upper
            color = (
                (138, 88, 78)
                if warm
                else ((185, 177, 152) if j % 4 in (1, 2) else (154, 151, 137))
            )
            left, right = j * width + 0.018, (j + 1) * width - 0.017
            add(
                left,
                right,
                0.007,
                0.039,
                row["podium_top"] - 0.045,
                level_cap - 0.22,
                color,
            )
            for idx, floor in enumerate(row["levels_z_m"][1:]):
                top = min(floor + 2.27, level_cap - 0.21)
                if top - floor < 0.57:
                    continue
                glass_add = hilyard.elevate(add, 0.044)
                hilyard.older.framed(
                    glass_add,
                    u,
                    min(1.98, width * 0.69),
                    floor + 0.58,
                    top,
                    2,
                    (166, 167, 154),
                )
                if width > 2.2 and abs(normal[0]) > 0.93 and j % 3 == 1 and idx > 0:
                    hilyard.lintel(
                        add,
                        left + 0.22,
                        right - 0.22,
                        floor + 0.19,
                        0.43,
                        (168, 155, 130),
                    )
                    add(
                        left + 0.23,
                        right - 0.23,
                        0.389,
                        0.429,
                        floor + 0.96,
                        floor + 1.03,
                        FRAME,
                    )
                    for rib in np.arange(left + 0.25, right - 0.19, 0.23):
                        add(
                            rib,
                            rib + 0.018,
                            0.396,
                            0.416,
                            floor + 0.24,
                            floor + 0.98,
                            FRAME,
                        )


def mechanical(parts, row, roof, patch, high):
    for e, n, w, d, z in row.get("roof_bays", []):
        part = patch((e - w / 2, n - d / 2, e + w / 2, n + d / 2)).intersection(roof)
        for piece in fairmount.geometry.sections(part):
            if piece.area > 0.3:
                base = high(piece.representative_point())
                flat(parts, piece, base - 0.04, base + z, METAL, (176, 179, 167))


def patterson(parts, row, outline, field, paving, patch):
    podium = row["podium_top"]
    roof = row["roof_z"]
    low = row["south_deck"]
    cut = orient(Polygon(row["open_court"]))
    west, south, east, north = outline.bounds
    terrace = outline.intersection(
        box(west - 1, south - 1, east + 1, row["south_terrace_n"])
    )
    main = outline.difference(terrace)
    frame = orient(main.difference(cut))
    flat(parts, outline, row["base_z_m"], podium, (163, 154, 137), (174, 168, 151))
    flat(parts, terrace, podium - 0.012, low, (154, 145, 130), (172, 167, 147))
    flat(parts, frame, podium - 0.012, roof, row["wall_color"], row["roof_color"])
    flat(parts, cut, podium - 0.019, row["court_top"], STONE, (158, 151, 125))
    patterson_bays(parts, row, outline, low, roof)
    patterson_bays(
        parts, {**row, "south_terrace_n": south - 1}, cut, low, roof, courtyard=True
    )
    base_glazing(parts, row, outline, field, sides=("W", "N"))
    bands_top(parts, outline, [podium], row["trim_color"])
    bands_top(parts, main, [roof - 0.16], row["trim_color"])
    bands_top(parts, terrace, [low - 0.16], row["trim_color"])
    railing(parts, orient(terrace), low, 0.95, FRAME)
    mechanical(parts, row, outline, patch, lambda p: low if terrace.covers(p) else roof)
    planter = cut.intersection(box(-1003.8, -43.7, -999.25, -40.03)).buffer(-0.08)
    flat(
        parts,
        planter,
        row["court_top"],
        row["court_top"] + 0.31,
        (146, 141, 114),
        (119, 140, 94),
    )
    hilyard.edge_apron(paving, field, outline)
    return outline


def curtain_wall(parts, footprint, lower, upper):
    for _, (span, add, normal, _, _, _) in fairmount.views(parts, footprint):
        if span < 0.85:
            continue
        count = max(2, round(span / 1.62))
        width = span / count
        for j in range(count):
            left, right = width * j, width * (j + 1)
            add(left + 0.013, left + 0.051, 0.019, 0.100, lower, upper, FRAME)
            for i, z in enumerate(np.arange(lower + 0.07, upper - 0.38, 3.048)):
                top = min(z + 2.47, upper - 0.075)
                if top <= z + 0.09:
                    continue
                tint = GLASS[
                    (i + (j * 7) % 11 + int(abs(normal[0]) > 0.9)) % len(GLASS)
                ]
                add(left + 0.065, right - 0.046, 0.021, 0.039, z + 0.19, top, tint)
                add(left + 0.038, right - 0.015, 0.045, 0.077, top, top + 0.057, FRAME)
        add(span - 0.054, span - 0.013, 0.019, 0.100, lower, upper, FRAME)


def ellis(parts, row, outline, field, patch):
    podium, roof = row["podium_top"], row["roof_z"]
    court = box(*row["courtyard_east"]).intersection(outline)
    upper = orient(outline.difference(court))
    flat(parts, outline, row["base_z_m"], podium, (112, 125, 123), (165, 167, 151))
    flat(parts, upper, podium - 0.02, roof, row["wall_color"], row["roof_color"])
    base_glazing(parts, row, outline, field, sides=("N", "E", "S"))
    curtain_wall(parts, upper, podium, roof)
    bands_top(parts, outline, [podium - 0.068], row["trim_color"])
    railing(parts, orient(court), podium, 0.97, FRAME)
    pad = court.intersection(box(-788.5, -39.15, -764.2, -22.54)).buffer(-0.28)
    flat(parts, pad, podium - 0.018, podium + 0.045, (149, 147, 129), (149, 157, 117))
    railing(parts, upper, roof, 1.02, FRAME)
    mechanical(parts, row, upper, patch, lambda _: roof)
    pool = orient(box(*row["rooftop_pool"]).intersection(upper))
    flat(parts, pool, roof - 0.025, roof + 0.23, STONE, (99, 152, 161))
    return upper


def chapter_windows(parts, row, outline, roof):
    levels = row["levels_z_m"][1:]
    for _, (span, add, normal, _, _, _) in fairmount.views(parts, outline):
        if span < 0.85:
            continue
        count = max(1, round(span / (2.94 if abs(normal[0]) > 0.9 else 2.52)))
        width = span / count
        for j in range(count):
            lo, hi = j * width + 0.035, (j + 1) * width - 0.033
            tint = (
                (74, 91, 104)
                if j % 3 == 1
                else ((95, 108, 117) if j % 3 == 2 else (81, 99, 111))
            )
            add(lo, hi, 0.015, 0.029, levels[0] - 0.08, roof - 0.16, tint)
            for x in np.arange(lo + 0.04, hi - 0.04, 0.18):
                add(
                    x,
                    x + 0.02,
                    0.032,
                    0.046,
                    levels[0] - 0.06,
                    roof - 0.12,
                    (61, 77, 85),
                )
            for index, z in enumerate(levels):
                head = min(z + 2.19, roof - 0.15)
                if head - z < 0.83:
                    continue
                hilyard.older.framed(
                    hilyard.elevate(add, 0.049),
                    (lo + hi) / 2,
                    min(width * 0.72, 1.86),
                    z + 0.68,
                    head,
                    2,
                    (139, 158, 162) if (index + j) % 3 == 0 else (111, 133, 142),
                )


def chapter(parts, row, outline, field):
    podium, roof = row["podium_top"], row["roof_z"]
    flat(parts, outline, row["base_z_m"], podium, (107, 118, 115), STONE)
    flat(parts, outline, podium - 0.015, roof, row["wall_color"], row["roof_color"])
    base_glazing(parts, row, outline, field, sides=("N", "E", "W"))
    chapter_windows(parts, row, outline, roof)
    bands_top(parts, outline, [podium - 0.07, roof - 0.09], (103, 119, 123))
    railing(parts, outline, roof, 0.94, FRAME)
    for index, shell in enumerate(row["roof_lounge_sections"]):
        room = orient(Polygon(shell).intersection(outline).buffer(0))
        top = row["lounge_z"] if index == 0 else row["lounge_z"] - (index * 0.42)
        flat(parts, room, roof - 0.025, top, row["wall_color"], row["roof_color"])
        for _, (span, add, _, _, _, _) in fairmount.views(parts, room):
            if span >= 1.3:
                hilyard.glazed(
                    add, 0.14, span - 0.14, roof + 0.63, top - 0.38, (130, 153, 157)
                )
    for zone in ((-835.7, -38.4, -832.84, -28.8), (-834.9, -24.07, -832.15, -19.8)):
        pad = outline.intersection(box(*zone))
        flat(parts, pad, roof - 0.04, roof + 0.14, STONE, (111, 139, 91))
    return outline


def ordinary(parts, row, outline, field, paving, patch, world):
    roof = garden.roof_sections(
        parts,
        outline,
        outline.buffer(-row["eaves_m"], join_style="mitre"),
        row["base_z_m"],
        row,
        grid=0.0002,
    )
    wall = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
    southwest.pattern_facade(parts, row, wall, field, roof)
    if "stores" in row:
        northwest.storefronts(parts, row, wall, world)
    if "awning" in row:
        awning(parts, wall, world, row["awning"])
    for side, target, stations, levels, depth in row.get("galleries", []):
        (_, add, _, plan, _, _), left, right = northwest.frontage(
            parts, wall, world, side, target, stations
        )
        if right - left > 1.1:
            for z in levels:
                hilyard.balcony(
                    parts, add, plan, left, right, z, depth, row["trim_color"]
                )
    northwest.bands(parts, row, wall, roof)
    older.roof_equipment(parts, row, outline, roof, patch)
    return wall


def build(row, field, paving):
    style = row.get("treatment")
    if style is None:
        return hilyard.build(row, field, paving)
    patch, _, world = older.transforms(row)
    outline = orient(set_precision(Polygon(row["outline_enu_m"]), 0.002))
    wall = orient(outline.buffer(-row["eaves_m"], join_style="mitre"))
    parts = []
    if style == "patterson":
        patterson(parts, row, wall, field, paving, patch)
    elif style == "ellis":
        ellis(parts, row, wall, field, patch)
    elif style == "chapter":
        chapter(parts, row, wall, field)
    else:
        wall = ordinary(parts, row, outline, field, paving, patch, world)
    gates = entry_gate(parts, paving, row, wall, field, world)
    return agate.output(parts, row, outline, set_precision(wall, 0), [], gates)


def collision_reference(manifest, config):
    # The current 740/750 wall removes the overlap in the old batch footprint.
    # The runtime requires the same neighbor before it mounts this review.
    ident = "roof-a392e59a"
    receipt = config["northwest_blocks_site"]
    descriptor = fairmount.SCENE / receipt["url"]
    assert garden.tools.digest(descriptor) == receipt["sha256"]
    site = json.loads(descriptor.read_bytes())
    match = next(row for row in site["buildings"] if row["id"] == ident)
    assert len(match["ground_footprints_enu_m"]) == 1
    structures = [
        {**row, "footprint_enu_m": match["ground_footprints_enu_m"][0]}
        if row["id"] == ident
        else row
        for row in manifest["buildings"]
    ]
    return {**manifest, "buildings": structures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(),
        PACKAGE,
        PAVING,
        "east_thirteenth_blocks_site",
        build,
        collision_reference=collision_reference,
    )


if __name__ == "__main__":
    main()
