# SPDX-License-Identifier: Apache-2.0
"""Build the Womack Hall and connected Franklin Boulevard shop exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
from shapely.affinity import affine_transform
from shapely.geometry import LineString, Point, Polygon

path = Path(__file__).with_name("build-franklin-boulevard-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
franklin = module_from_spec(loader)
loader.loader.exec_module(franklin)

houses, chapter, design = franklin.houses, franklin.chapter, franklin.design
base, geometry, approaches = franklin.base, franklin.geometry, franklin.approaches
PACKAGE = "franklin-complex-exterior-review"
SPEC = houses.ROOT / "data/metadata/franklin-complex-exterior-review.json"
GLASS = (74, 97, 102)
PALE = (189, 191, 177)
CHARCOAL = (61, 66, 65)
SIDING = (86, 95, 100)
LIGHT_SIDING = (130, 130, 120)
GREEN_TILE = (66, 99, 83)
STONE = (125, 109, 93)
BRONZE = (103, 100, 80)


def cladding(add, x0, x1, depth, low, top, color):
    add(x0, x1, depth, depth + 0.076, low, top, color)
    seams = tuple(max(0, channel - 17) for channel in color)
    for z in np.arange(low + 0.19, top - 0.06, 0.19):
        add(x0, x1, depth + 0.073, depth + 0.081, z, z + 0.013, seams)


def housing(parts, field, row, edges, entry, door_edge, door_at, height):
    frame = franklin.frame(row)
    columns = []
    for local, width in row["canopy_columns"]:
        p = affine_transform(Point(local), frame).coords[0]
        grade = geometry.sample_ground(field, *p)
        head = height(p) - 0.13
        columns.append(approaches.supported_post(parts, p, grade - 0.15, head, CHARCOAL, width / 2))
        approaches.supported_post(parts, p, grade - 0.09, grade + 0.14, LIGHT_SIDING, width / 2 + 0.04)

    upper_lobby = tuple(tuple(p) for p in row["upper_lobby_face_enu_m"])
    for edge in [*edges, upper_lobby]:
        over_lobby = edge == upper_lobby
        span, add, outside, point, _, slab = chapter.setup_face(parts, *edge)
        if span < 2.10:
            continue
        grade = geometry.sample_ground(field, *point(span / 2, .12))
        eave = min(height(point(x, 0)) for x in (0.04, span / 2, span - .04))
        if not over_lobby:
            add(.025, span - .025, -.008, .036, grade - .12, grade + .30, STONE)
        if eave - grade < 5.35:
            if edge == door_edge:
                width = entry["width_m"]
                top = min(eave - .13, entry["threshold_z_m"] + 3.07)
                bottom = entry["threshold_z_m"] + 2.29
                if top - bottom >= .19:
                    radius = width * .40
                    theta = np.linspace(0, np.pi, 15)
                    arch = Polygon([(door_at + radius * np.cos(t), bottom + (top-bottom) * np.sin(t))
                                    for t in theta])
                    slab(arch, .06, .086, GLASS)
                    slab(arch.buffer(.037).difference(arch), .05, .099, PALE)
            openings = np.linspace(1.17, span - 1.17, max(1, round(span / 2.90)))
            for x in openings:
                if edge == door_edge and abs(x - door_at) <= entry["width_m"] / 2 + .94:
                    continue
                sill = grade + .75
                if eave - sill > .69:
                    chapter.prior.window(add, x, min(span * .35, 1.42), sill,
                                         min(sill + 1.06, eave - .24), PALE, GLASS, ribs=2)
            continue

        # The converted hotel has repeated paired openings with siding between the glazed bays.
        groups = max(1, round(span / (6.2 if abs(outside[1]) > .6 else 5.2)))
        pitch = span / groups
        for index in range(groups):
            center = pitch * (index + .5)
            if pitch > 3.55 and index % 2 == 0:
                left, right = center - pitch * .47, center + pitch * .47
                local_eave = min(height(point(x, 0)) for x in (left, right))
                bottom = grade + (4.85 if over_lobby else .29)
                cladding(add, left, right, .003, bottom, local_eave - .18,
                         SIDING if index % 4 == 0 else LIGHT_SIDING)
            for sill in (.88, 3.55, 6.18, 8.86):
                lower = grade + sill
                if (over_lobby and sill < 3.0) or lower + .8 > eave - .14:
                    continue
                offsets = (-.96, .96) if pitch > 3.9 else (0.0,)
                for offset in offsets:
                    x = center + offset
                    if edge == door_edge and sill < 1 and abs(x - door_at) < entry["width_m"] / 2 + .64:
                        continue
                    width = 1.36 if pitch > 3.9 else min(1.41, .60 * pitch)
                    if over_lobby and lower < height(point(x, .24)) + .15:
                        continue
                    chapter.prior.window(add, x, width, lower, min(eave - .16, lower + 1.26),
                                         PALE, GLASS, ribs=2)
                    if sill > 1:
                        add(x - .35, x + .35, .077, .104, lower - .259, lower - .078, CHARCOAL)
    return columns


def curved_awning(parts, point, outward, add, left, right, depth, lip, lift, material):
    origin = point(left, 0)
    d = np.linspace(0, depth, 8)
    levels = lip + lift * np.sqrt(np.clip(1 - (d / depth) ** 2, 0.0, 1.0))
    for inner, outer, za, zb in zip(d[:-1], d[1:], levels[:-1], levels[1:]):
        plan = Polygon([point(x, y) for x, y in (
            (left, inner), (right, inner), (right, outer), (left, outer)
        )])
        slope = (zb - za) / (outer - inner)

        def top(e, n):
            return za + slope * (((e, n) - origin) @ outward - inner)

        lower = zb - .16
        mesh = geometry.shell(plan, lower, top, BRONZE, material)
        underside = np.isclose(mesh.vertices[:, 1], lower, atol=.00001)
        mesh.vertices[underside, 1] = [top(e, -n) - .095 for e, _, n in mesh.vertices[underside]]
        parts.append(mesh)
        for x in np.linspace(left + .12, right - .12, max(2, round((right-left) / .62))):
            # Capped standing seams on each part of the curved metal cover.
            fold = Polygon([point(u, v) for u, v in (
                (x-.012, inner), (x+.012, inner), (x+.012, outer), (x-.012, outer)
            )])
            rib = geometry.shell(fold, lower, lambda e, n: top(e, n) + .030, BRONZE, BRONZE)
            ends = np.isclose(rib.vertices[:, 1], lower, atol=.00001)
            rib.vertices[ends, 1] = [top(e, -n) - .018 for e, _, n in rib.vertices[ends]]
            parts.append(rib)
    add(left, right, depth - .042, depth + .036, lip - .11, lip + .035, CHARCOAL)


def storefronts(parts, field, row, edges, entry, door_edge, door_at, height):
    for face in row["facades"]:
        edge = design.locate_face(edges, face["near_enu_m"], face["bearing"])
        span, add, outward, point, _, _ = chapter.setup_face(parts, *edge)
        line = LineString(edge)
        grade = geometry.sample_ground(field, *point(span / 2, .04))
        tile = GREEN_TILE if face["small_shops"] else STONE
        add(.02, span-.02, -.002, .042, grade - .15, grade + face["base_band_m"], tile)
        if face["small_shops"]:
            band = max(grade + 2.93, min(height(point(.1, 0)), height(point(span-.10, 0))) - .55)
            add(.025, span - .025, .008, .13, band, band + .47, CHARCOAL)
            for x in np.arange(.13, span-.1, .30):
                add(x, x + .022, .125, .143, band + .024, band + .446, BRONZE)
        for at, width, sill, high, ribs in face["windows"]:
            x = line.project(Point(at))
            width = min(width, 2 * min(x - .05, span - x - .05))
            if width < .27:
                raise ValueError(f"Window does not fit on {row['id']} near {at}.")
            eave = min(height(point(t, 0)) for t in (x - width / 2, x + width / 2)) - .21
            z = geometry.sample_ground(field, *point(x, .10))
            chapter.prior.window(add, x, width, z + sill, min(eave, z + high), CHARCOAL, GLASS, ribs=ribs)

        for start, end, depth, head, rise, tone in face["awnings"]:
            left, right = sorted(line.project(Point(p)) for p in (start, end))
            curved_awning(parts, point, outward, add, left, right, depth, grade + head, rise, tone)
            if right - left > 5.5:
                for x in np.linspace(left + .17, right - .17, max(2, round((right-left) / 3.3))):
                    add(x - .070, x + .070, -0.012, depth * .76,
                        grade + head - .11, grade + head + .028, CHARCOAL)
                    add(x - .085, x + .085, -0.09, .084,
                        grade + head - .58, grade + head, CHARCOAL)
    franklin.finish_roof(parts, field, row, height)
    return []


def elevations(parts, field, row, edges, entry, door_edge, door_at, height):
    detail = housing if row["type"] == "residence" else storefronts
    return detail(parts, field, row, edges, entry, door_edge, door_at, height)


def build(spec, manifest, config, field, graph):
    return houses.build(spec, manifest, config, field, graph, decorate=elevations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    houses.export_review(
        spec_path=SPEC,
        package=PACKAGE,
        key="franklin_complex_exterior_site",
        ground_node="franklin-complex-approaches",
        paving_node="franklin-complex-paving",
        builder=build,
        audit_path=args.audit,
        stage=args.stage,
    )


if __name__ == "__main__":
    main()
