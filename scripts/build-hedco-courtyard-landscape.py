# SPDX-License-Identifier: Apache-2.0
"""Refine the open HEDCO courtyard surfaces, planting and furnishings."""

import argparse
from importlib import import_module
from math import cos, radians, sin
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

site = import_module("build-pioneer-cemetery-landscape-review")
PACKAGE = "hedco-courtyard-landscape-review"
GROUND = "hedco-landscape-courtyard-paving"
FIXTURES = "hedco-landscape-courtyard-fixtures"
PLANTS = "hedco-landscape-courtyard-planting"
LIFT = 0.108
CONCRETE = (177, 169, 151)
MASONRY = (160, 152, 133)
METAL = (50, 75, 60)


def host(spec, metadata):
    descriptor = site.scene / "hedco-exterior-review/site.json"
    geometry = site.scene / "hedco-exterior-review/site.glb"
    input_file = metadata / "hedco-site-review.json"
    pins = spec["pins"]
    assert site.pin(descriptor) == pins["hedco_descriptor_sha256"]
    assert site.pin(geometry) == pins["hedco_model_sha256"]
    assert site.pin(input_file) == pins["hedco_site_input_sha256"]
    building = site.read(descriptor)
    original = site.read(input_file)["courtyard"]
    manifest = site.read(site.scene / "manifest.json")
    heightfield = site.scene / manifest["heightfield_url"]
    assert site.pin(heightfield) == building["source_heightfield_sha256"]
    wall = Polygon(building["building"]["footprint_enu_m"])
    posts = unary_union(
        [Polygon(ring) for ring in building["building"]["support_collision_enu_m"]]
    )
    ground = box(*original["bounds"]).union(box(*original["west_paving"])).difference(wall)
    return site.read(heightfield), building, wall.union(posts), ground


def follow_grade(parts, field, shape, bottom, top, color):
    for piece in site.landscape.geometry.sections(shape):
        mesh = site.landscape.cap(piece, bottom, top, color)
        mesh.vertices[:, 1] += [
            site.ground_height(field, east, -south) for east, _, south in mesh.vertices
        ]
        parts.append(mesh)


def bench(parts, field, row):
    e, n = row["center"]
    angle = radians(row["orientation_deg"])
    axis = (cos(angle), sin(angle))
    cross = (-axis[1], axis[0])
    h = site.ground_height(field, e, n) + LIFT
    wood = (159, 145, 115)
    support = (92, 99, 82)

    def slab(u, v, length, width, low, high, color):
        origin = (e + u * axis[0] + v * cross[0], n + u * axis[1] + v * cross[1])
        points = [
            (origin[0] + du * axis[0] + dv * cross[0], origin[1] + du * axis[1] + dv * cross[1])
            for du, dv in ((-length / 2, -width / 2), (length / 2, -width / 2),
                           (length / 2, width / 2), (-length / 2, width / 2))
        ]
        site.solid(parts, Polygon(points), h + low, h + high, color)

    for u in (-0.67, 0.67):
        for v in (-0.198, 0.198):
            slab(u, v, 0.067, 0.073, -0.045, 0.87 if v > 0 else 0.56, support)
        slab(u, 0, 0.078, 0.46, 0.398, 0.44, support)
    for i in range(5):
        slab(0, -0.2 + i * 0.098, 1.76, 0.081, 0.432, 0.48, wood)
    for z in (0.58, 0.686, 0.792):
        slab(0, 0.218, 1.76, 0.058, z, z + 0.077, wood)
    if row["orientation_deg"] == 90:
        return box(e - 0.26, n - 0.9, e + 0.26, n + 0.9)
    return box(e - 0.9, n - 0.26, e + 0.9, n + 0.26)


def lamp(parts, field, e, n):
    z = site.ground_height(field, e, n) + LIFT
    for start, end, r in [(-0.048, 0.135, 0.135), (0.04, 0.57, 0.092), (0.25, 3.36, 0.054)]:
        site.cylinder_between(parts, (e, n, z + start), (e, n, z + end), r, METAL, sides=10)
    site.orb(parts, (e, n, z + 3.57), (0.137, 0.137, 0.241), (207, 217, 193))
    site.orb(parts, (e, n, z + 3.76), (0.146, 0.146, 0.053), METAL)
    return box(e - 0.14, n - 0.14, e + 0.14, n + 0.14)


def planted_crown(parts, field, e, n, spread, height, phase, base=0.125):
    z = site.ground_height(field, e, n) + base
    palette = [(93, 117, 72), (112, 131, 83), (124, 134, 83)]
    for i in range(3):
        angle = phase + i * 2.399963
        a, b = e + cos(angle) * spread * 0.32, n + sin(angle) * spread * 0.3
        site.orb(parts, (a, b, z + height * 0.54), (spread * 0.58, spread * 0.51, height * 0.55), palette[i])


def build(spec, metadata, stage, audit):
    field, parent, blocked, base = host(spec, metadata)
    beds = [box(*item) for item in spec["east_planters"]]
    turf = Polygon(spec["lawn_enu_m"])
    garden = Polygon(spec["low_south_garden_enu_m"]).intersection(base)
    walk = base.difference(unary_union([turf, garden, *beds]))
    assert all(g.is_valid and base.buffer(0.02).covers(g) for g in [turf, garden, *beds])
    slabs, fixtures, plants, solids = [], [], [], []
    site.drape(slabs, field, turf, (113, 139, 88), LIFT, 0.85)
    site.drape(slabs, field, garden, (124, 107, 83), LIFT + 0.008, 0.65)
    site.drape(slabs, field, walk, CONCRETE, LIFT, 0.83)
    e0, n0, e1, n1 = walk.bounds
    seams = [
        LineString([(e, n0), (e, n1)]) for e in np.arange(-684.4, e1, 2.32)
    ] + [
        LineString([(e0, n), (e1, n)]) for n in np.arange(-463.1, n1, 2.37)
    ]
    joints = unary_union(seams).buffer(0.014).intersection(walk.buffer(-0.045))
    site.drape(fixtures, field, joints, (158, 152, 139), LIFT + 0.008, 0.61)

    for i, bed in enumerate(beds):
        soil = bed.buffer(-0.12, join_style="mitre")
        follow_grade(fixtures, field, bed.difference(soil), LIFT - 0.04, LIFT + 0.525, MASONRY)
        site.drape(slabs, field, soil, (111, 95, 74), LIFT + 0.397, 0.5)
        e0, n0, e1, n1 = soil.bounds
        for j, north in enumerate(np.arange(n0 + 0.45, n1 - 0.3, 0.92)):
            if (i + j) % 5 != 2:
                planted_crown(plants, field, (e0 + e1) / 2, north, 0.39, 0.25 + 0.075 * (j % 3), j + i, base=LIFT + 0.397)
        solids.append(bed.bounds)

    stone_rim = garden.difference(garden.buffer(-0.145, join_style="mitre"))
    follow_grade(fixtures, field, stone_rim, LIFT - 0.026, LIFT + 0.188, MASONRY)
    parapet = spec["west_parapet"]
    barrier = LineString(parapet["line_enu_m"]).buffer(parapet["width_m"] / 2, cap_style="flat")
    follow_grade(fixtures, field, barrier, -0.34, LIFT + parapet["above_walk_m"], (149, 146, 130))
    follow_grade(fixtures, field, barrier.buffer(0.027, join_style="mitre"), LIFT + parapet["above_walk_m"] - 0.07, LIFT + parapet["above_walk_m"] + 0.035, (166, 158, 139))
    solids.append(barrier.bounds)
    for row in spec["benches"]:
        solids.append(bench(fixtures, field, row).bounds)
    for e, n in spec["lamps"]:
        solids.append(lamp(fixtures, field, e, n).bounds)
    for i, (e, n, spread) in enumerate(spec["south_plant_groups"]):
        assert garden.buffer(-spread * 0.78).covers(Point(e, n)), (e, n)
        planted_crown(plants, field, e, n, spread, 0.36 + 0.085 * (i % 4), 0.8 * i)
    tree = spec["reference"]["trees"]["trees"][0]
    tree_position = (tree["e"], tree["n"])
    assert tree["TreeNumber"] == 4597 and garden.contains(Point(*tree_position))
    site.canopy(plants, field, {"position_enu_m": tree_position, "height_m": tree["Height"] * 0.3048, "crown_radius_m": tree["Spread"] * 0.1524, "form": "rounded"}, 0)
    no_go = unary_union([blocked, *(box(*bounds) for bounds in solids)])
    minimum = float("inf")
    for row in spec["reference_walks_enu_m"]:
        line = LineString(row)
        off = line.difference(walk.buffer(0.13)).length
        assert off < 0.01, (off, line.difference(walk.buffer(0.13)).wkt)
        minimum = min(minimum, line.distance(no_go))
    assert minimum > 0.50, minimum

    stage.mkdir(parents=True, exist_ok=True)
    glb, desc = stage / "site.glb", stage / "site.json"
    faces = site.export(glb, (GROUND, slabs, "landscape-surface"), (FIXTURES, fixtures, "landscape-detail"),
                        (PLANTS, plants, "landscape-vegetation"), surface_layer=GROUND)
    site.fairmount.write_json(
        desc,
        {
            "source_presentation_sha256": parent["source_presentation_sha256"],
            "source_base_model_sha256": parent["source_base_model_sha256"],
            "source_heightfield_sha256": parent["source_heightfield_sha256"],
            "prerequisite_site_sha256": spec["pins"]["hedco_descriptor_sha256"],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(glb),
            "buildings": [],
            "closed_site_boxes_enu_m": solids,
        },
        compact=True,
    )
    report = {
        "lawn_m2": round(turf.area, 2),
        "walk_m2": round(walk.area, 2),
        "raised_planter_m2": round(sum(b.area for b in beds), 2),
        "south_garden_m2": round(garden.area, 2),
        "west_parapet_length_m": round(LineString(parapet["line_enu_m"]).length, 2),
        "lamps": len(spec["lamps"]),
        "benches": len(spec["benches"]),
        "fixture_boxes": len(solids),
        "reference_walk_min_clearance_m": round(minimum, 3),
        "faces": faces,
        "asset_sha256": site.pin(glb),
        "descriptor_sha256": site.pin(desc),
    }
    site.fairmount.write_json(audit, report)
    print(report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    build(site.read(metadata / "hedco-courtyard-landscape.json"), metadata, args.stage, args.audit)


if __name__ == "__main__":
    main()
