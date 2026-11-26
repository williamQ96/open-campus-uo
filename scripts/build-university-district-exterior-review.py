# SPDX-License-Identifier: Apache-2.0
"""Build the retained Bushnell bridge, 770 E 11th and two University District garages."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import union_all
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-hilyard-west-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
prior = module_from_spec(loader)
loader.loader.exec_module(prior)
houses, chapter = prior.houses, prior.chapter
base, design, geometry, approaches = prior.base, prior.design, prior.geometry, prior.approaches
PACKAGE = "university-district-exterior-review"
CONCRETE = (167, 163, 149)
EDGES = (189, 185, 170)
SOFFIT = (124, 119, 104)
ASPHALT = (151, 149, 139)
GLASS = (75, 98, 100)
FRAME = (134, 136, 127)
CREAM = (205, 201, 183)
BRICK = (150, 125, 104)
DARK = (74, 77, 71)


def faces(area):
    return list(houses.shared.face_edges(orient(area)))


def slab(parts, footprint, bottom, top, wall, roof=None, slope=(0, 0)):
    start = len(parts)
    base.flat(parts, footprint, bottom, top, wall, roof)
    east, north = footprint.centroid.coords[0]
    dx, dy = slope
    for mesh in parts[start:]:
        mesh.vertices[:, 1] += (mesh.vertices[:, 0] - east) * dx - (
            mesh.vertices[:, 2] + north
        ) * dy


def band(add, left, right, low, high, *, spacing):
    if right - left < 0.7:
        return
    count = max(1, round((right - left) / spacing))
    chapter.prior.window(
        add, (left + right) / 2, right - left, low, high, FRAME, GLASS, ribs=count
    )


def approach(parts, ground, edges, field, row):
    return approaches.entry_stair(
        parts, ground, edges, field, row | {"door_color": DARK}, None,
    )


def academic(rows, field, row, outline, ground):
    main = Polygon(row["main_enu_m"])
    annex = Polygon(row["annex_enu_m"])
    floor = design.science.earlier.fit_base(field, outline)[0]
    upper = row["main_roof_z_m"]
    lower = row["annex_roof_z_m"]
    slab(rows, main, floor, upper, CREAM, (156, 150, 138), (0, -.009))
    slab(rows, annex, floor, lower, BRICK, (196, 196, 183))
    for area, top, rings in [(main, upper, row["main_equipment"]), (annex, lower, row["annex_equipment"])]:
        wall = area.difference(area.buffer(-.22, join_style="mitre"))
        slab(rows, wall, top - .05, top + .33, EDGES, slope=(0, -.009) if area is main else (0, 0))
        for west, south, east, north, z in rings:
            footprint = box(west, south, east, north)
            assert area.buffer(.02).covers(footprint)
            slab(rows, footprint, top - .33, z, CREAM, (171, 171, 158))
            slab(rows, footprint, z - .09, z + .12, EDGES)

    entry, entry_edge, center = approach(rows, ground, faces(main), field, row)
    for edge in faces(main):
        length, add, outward, _, _, _ = chapter.setup_face(rows, *edge)
        if length < 4:
            continue
        add(.08, length - .08, .004, .035, floor + .3, 7.82, BRICK)
        add(.05, length - .05, .015, .083, 7.78, 8.03, EDGES)
        if abs(outward[1]) < .3:
            cuts = [(2, length - 2)]
        else:
            cuts = [(1.4, length * .45), (length * .49, length - 1.4)]
        for low, high in [(4.02, 5.45), (8.93, 10.43), (12.55, 14.12)]:
            for left, right in cuts:
                band(add, left, right, low, high, spacing=1.38)
        if edge == entry_edge:
            ranges = [(1.7, center - 3.0), (center + 3.0, length - 1.7)]
            for left, right in ranges:
                band(add, left, right, .06, 1.61, spacing=1.65)
            add(center - 2.65, center + 2.65, -.05, 2.08, 1.99, 2.28, CREAM)
            for dx in [-2.23, 2.23]:
                add(center + dx - .09, center + dx + .09, 1.70, 1.88, floor + .15, 2.0, EDGES)
    for edge in faces(annex):
        length, add, _, _, _, _ = chapter.setup_face(rows, *edge)
        if length < 3.5 or main.distance(Point(np.mean(edge, axis=0))) < .06:
            continue
        add(.03, length - .03, .015, .072, lower - .32, lower, CREAM)
        for center in np.linspace(1.73, length - 1.73, max(2, round(length / 3.4))):
            band(add, center - .70, center + .70, -.10, 1.38, spacing=.85)

    bridge_parts, footings = [], []
    bridge = row["bridge"]
    bridge_box = union_all([box(*bridge["bounds_enu_m"]), box(*bridge["entry_return_enu_m"])])
    assert bridge_box.intersection(main).area > .25
    base.flat(bridge_parts, bridge_box, bridge["bottom_z_m"], bridge["bottom_z_m"] + .22, DARK)
    base.flat(bridge_parts, bridge_box, bridge["top_z_m"] - .20, bridge["top_z_m"], SOFFIT)
    for edge in faces(bridge_box):
        length, add, _, _, _, _ = chapter.setup_face(bridge_parts, *edge)
        if length > 6:
            add(.02, length - .02, -.033, .029, bridge["bottom_z_m"] + .19,
                bridge["top_z_m"] - .18, GLASS)
            for u in np.arange(.12, length, 1.25):
                add(u, min(u + .051, length), .019, .075, bridge["bottom_z_m"] + .17,
                    bridge["top_z_m"] - .16, DARK)
            top = bridge["top_z_m"] - .73
            add(.01, length - .01, .021, .086, top, top + .073, DARK)
        else:
            add(.01, length - .01, -.045, .035, bridge["bottom_z_m"] + .17,
                bridge["top_z_m"] - .16, SOFFIT)
    for east, north in bridge["columns_enu_m"]:
        p = (east, north)
        footprint = box(east - .19, north - .19, east + .19, north + .19)
        slab(bridge_parts, footprint, geometry.sample_ground(field, *p) - .18,
             bridge["bottom_z_m"] + .03, EDGES)
        footings.append(footprint)
    rows.extend(bridge_parts)
    return floor, [main, annex], footings, entry


def deck(rows, field, row, outline, ground):
    floor = design.science.earlier.fit_base(field, outline)[0]
    # Keep the roof crown and split-level break independently editable.
    sections = []
    for section in row["deck_sections"]:
        area = outline.intersection(box(*section["bounds_enu_m"]))
        if not area.is_empty:
            sections.append((area, section["surface_z_m"], tuple(section["slope"])))
    for area, surface, slope in sections:
        for depth in row["floor_offsets_m"]:
            top = surface - depth
            slab(rows, area, top - .29, top, SOFFIT, ASPHALT, slope)
        e0, n0 = area.centroid.coords[0]
        strip_clearance = area.buffer(-.38)
        for inset in (2.1, 5.85):
            for east in np.arange(area.bounds[0] + 3.0, area.bounds[2] - 1.2, 2.62):
                north = area.bounds[3] - inset
                stripe = box(east, north - 1.72, east + .095, north + 1.72)
                if strip_clearance.covers(stripe):
                    x, y = stripe.centroid.coords[0]
                    z = surface + (x - e0) * slope[0] + (y - n0) * slope[1]
                    slab(rows, stripe, z + .004, z + .014, (178, 173, 154), slope=slope)
    slab(rows, outline, floor - .25, floor + .29, SOFFIT)
    if "edge_pad_enu_m" in row:
        pad = outline.buffer(1.2, join_style="mitre").intersection(
            box(*row["edge_pad_enu_m"])
        )
        slab(ground, pad, floor - .47, floor + .12, (147, 151, 130))

    entry, entry_edge, center = approach(rows, ground, faces(outline), field, row)
    garage_type = row["street_address"].startswith("666")
    for edge in faces(outline):
        length, add, outward, position, _, _ = chapter.setup_face(rows, *edge)
        if length < .35:
            continue
        count = max(1, round(length / row["bay_m"]))
        for i in range(count):
            left, right = i * length / count, (i + 1) * length / count
            east, north = position((left + right) / 2, 0)
            area, surface, slope = min(
                sections, key=lambda section: section[0].distance(Point(east, north))
            )
            e0, n0 = area.centroid.coords[0]
            top = surface + (east - e0) * slope[0] + (north - n0) * slope[1]
            for depth in row["floor_offsets_m"]:
                z = top - depth
                add(left, right, -.11, .08, z - .30, z + .61, CONCRETE)
                add(left, right, .025, .105, z + .76, z + .83, FRAME)
            if garage_type and (outward[0] > .5 or outward[1] > .5):
                add(left, right, -.14, -.045, floor + .16, floor + 2.9, BRICK)
                if right - left > 2.7 and (edge != entry_edge or abs((left + right) / 2 - center) > 2.6):
                    band(add, left + .37, right - .37, floor + .55, floor + 2.52, spacing=1.2)
            elif edge != entry_edge or not left <= center <= right:
                add(left, right, -.105, .071, floor, floor + .87, CONCRETE)
            post = left + min(.17, (right - left) / 3)
            if right - left > .39:
                add(post - .13, post + .14, -.31, .12, floor, top + .78, EDGES)
        if garage_type and outward[1] > .78 and length > 5:
            add(.08, length - .08, -.04, .66, floor + 2.82, floor + 3.1, DARK)

    for core in row["cores"]:
        shape = outline.intersection(box(*core["bounds_enu_m"]))
        assert not shape.is_empty
        z = core["top_z_m"]
        slab(rows, shape, floor, z, CONCRETE, EDGES)
        for edge in faces(shape):
            length, add, _, _, _, _ = chapter.setup_face(rows, *edge)
            if length >= 1.05:
                for level in range(1, len(row["floor_offsets_m"]) - 1):
                    sill = floor + level * row["level_step_m"] + .69
                    if sill + .91 < z:
                        band(add, length * .31, length * .69, sill, sill + .89, spacing=1.0)
    return floor, [outline], [], entry


def build(spec, manifest, config, field, graph):
    originals = {b["id"]: b for b in manifest["buildings"]}
    meshes, records, occupied, supports, entries, ground = {}, [], [], [], [], []
    for row in spec["models"]:
        area = orient(Polygon(row["outline_enu_m"]))
        assert area.is_valid and area.area > 10, row["id"]
        pieces = []
        builder = academic if row["kind"] == "academic" else deck
        floor, cores, feet, gate = builder(pieces, field, row, area, ground)
        mesh = trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=.000012))
        id = row["id"]
        meshes[id] = design.science.ordered_mesh(mesh)
        occupied.extend(cores)
        supports.extend(feet)
        entries.append(gate)
        records.append({
            "id": id,
            "name": row["name"],
            "street_address": row["street_address"],
            "footprint_enu_m": base.ring(area),
            "ground_footprints_enu_m": [base.ring(ring) for ring in cores],
            "support_collision_enu_m": [base.ring(ring) for ring in feet],
            "base_z_m": round(floor, 4),
            "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
            "area_m2": round(sum(ring.area for ring in cores), 3),
            "entrances": [gate],
        })
    previous = union_all([Polygon(originals[id]["footprint_enu_m"]) for id in meshes])
    predecessor = json.loads(
        (houses.SCENE / config["hilyard_west_exterior_site"]["url"]).read_bytes()
    )
    neighbor_ids = {
        row["bridge"]["neighbor_id"] for row in spec["models"] if "bridge" in row
    }
    neighbors = {
        record["id"]: record for record in predecessor["buildings"]
        if record["id"] in neighbor_ids
    }
    assert set(neighbors) == neighbor_ids
    for row in spec["models"]:
        if "bridge" not in row:
            continue
        bridge = row["bridge"]
        neighbor = Polygon(neighbors[bridge["neighbor_id"]]["ground_footprints_enu_m"][0])
        assert box(*bridge["bounds_enu_m"]).intersection(neighbor).area > .25
    active_manifest = manifest | {
        "buildings": [
            record | {"footprint_enu_m": neighbors[record["id"]]["ground_footprints_enu_m"][0]}
            if record["id"] in neighbors else record
            for record in manifest["buildings"]
        ]
    }
    checked, clearance = chapter.prior.nearby.shared.graduate.shared.check_routes(
        occupied, supports, entries, previous, active_manifest, graph, config, set(meshes)
    )
    return meshes, records, design.science.ordered_mesh(trimesh.util.concatenate(ground)), checked, clearance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    houses.export_review(
        spec_path=houses.ROOT / "data/metadata/university-district-exterior-review.json",
        package=PACKAGE,
        key="university_district_exterior_site",
        ground_node="university-district-approaches",
        paving_node="university-district-paving",
        builder=build,
        audit_path=args.audit,
        stage=args.stage,
    )


if __name__ == "__main__":
    main()
