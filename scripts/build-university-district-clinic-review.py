# SPDX-License-Identifier: Apache-2.0
"""Export the University District clinic, attached South Garage and North Building."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import intersects_xy, union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-university-district-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
district = module_from_spec(loader)
loader.loader.exec_module(district)
houses, chapter, base, design, geometry = (
    district.houses,
    district.chapter,
    district.base,
    district.design,
    district.geometry,
)
ROOT, SCENE = houses.ROOT, houses.SCENE
PACKAGE = "university-district-clinic-review"
KEY = "university_district_clinic_site"
GROUND = "university-district-clinic-approaches"
STONE = (203, 192, 165)
PIER = (220, 211, 186)
MASONRY = (174, 155, 124)
SPANDREL = (148, 108, 85)
SLATE = (168, 167, 148)
GLASS = (62, 89, 107)
TRIM = (145, 146, 137)
faces, slab = district.faces, district.slab


def ribbon(add, left, right, sill, head, pitch=1.24):
    if right - left > 0.45:
        chapter.prior.window(
            add,
            (left + right) / 2,
            right - left,
            sill,
            head,
            TRIM,
            GLASS,
            ribs=max(1, round((right - left) / pitch)),
        )


def equipment(parts, outline, datum, assets):
    for west, south, east, north, top in assets:
        area = box(west, south, east, north).intersection(outline.buffer(-0.2))
        if area.is_empty:
            raise ValueError("Roof equipment must intersect its supported roof.")
        slab(parts, area, datum - 0.12, top, SLATE, (191, 193, 178))
        slab(parts, area, top - 0.12, top + 0.045, PIER)
        edge = max(faces(area), key=lambda line: LineString(line).length)
        span, add, _, _, _, _ = chapter.setup_face(parts, *edge)
        for z in np.arange(max(datum + 0.5, top - 0.48), top - 0.1, 0.14):
            add(0.13, span - 0.13, 0.004, 0.025, z, z + 0.03, TRIM)


def roof_border(parts, outline, top, trim=STONE):
    lip = outline.difference(outline.buffer(-0.20, join_style="mitre"))
    slab(parts, lip, top - 0.08, top + 0.38, trim)


def clinic(parts, ground, field, row):
    upper = orient(Polygon(row["main_enu_m"]))
    low = union_all([Polygon(row["low_enu_m"]), Polygon(row["junction_enu_m"])]).buffer(
        0
    )
    outline = union_all([upper, low])
    assert outline.geom_type == "Polygon" and outline.is_valid
    recess = box(*row["entry_recess_enu_m"])
    lower = upper.difference(recess)
    road_overhang = low.intersection(box(*row["low_road_overhang_enu_m"]))
    low_wall = low.difference(road_overhang)
    floor = design.science.earlier.fit_base(field, outline)[0]
    top = row["roof_surface_z_m"]
    low_roof = row["low_roof_z_m"]
    slab(parts, lower, floor, 6.94, STONE)
    slab(parts, upper, 6.94, top, STONE, SLATE)
    slab(parts, low_wall, floor, low_roof, MASONRY, (145, 145, 132))
    slab(parts, road_overhang, 3.06, low_roof, MASONRY, (145, 145, 132))
    roof_border(parts, upper, top, PIER)
    equipment(parts, upper, top, row["equipment"])
    slab(parts, upper.intersection(recess), 6.71, 7.02, PIER)
    posts = []
    for east, north in row["support_centres_enu_m"]:
        foot = box(east - 0.27, north - 0.27, east + 0.27, north + 0.27)
        slab(parts, foot, geometry.sample_ground(field, east, north) - 0.26, 7.03, PIER)
        posts.append(foot)
    gate, door_edge, station = district.approach(
        parts, ground, faces(lower), field, row
    )
    for edge in faces(lower):
        span, add, _, _, _, _ = chapter.setup_face(parts, *edge)
        if span < 1.2:
            continue
        for z in (0.6, 4.08):
            add(0.04, span - 0.04, 0.009, 0.035, z - 0.34, z - 0.04, SPANDREL)
            if edge != door_edge or z > 2.5:
                ribbon(add, 0.52, span - 0.52, z, z + 1.30)
            else:
                ribbon(add, 0.52, station - 2.3, z, z + 1.30)
                ribbon(add, station + 2.3, span - 0.52, z, z + 1.30)
        if edge == door_edge:
            add(station - 2.28, station + 2.28, -0.12, 1.95, 1.45, 1.71, PIER)
            add(station - 2.28, station + 2.28, 1.86, 1.96, 1.42, 1.50, TRIM)
    for edge in faces(upper):
        span, add, _, _, _, _ = chapter.setup_face(parts, *edge)
        if span < 1.2:
            continue
        stations = np.linspace(0.46, span - 0.46, max(2, round(span / 7.8) + 1))
        for z in (8.94, 11.83, 17.95, 20.9):
            add(0.05, span - 0.05, 0.015, 0.092, z - 0.16, z, PIER)
        for station in stations:
            add(station - 0.23, station + 0.23, 0.015, 0.25, 6.94, top, PIER)
        for left, right in zip(stations[:-1], stations[1:]):
            ribbon(add, left + 0.32, right - 0.32, 7.32, 8.66)
            ribbon(add, left + 0.32, right - 0.32, 12.1, 17.7)
            ribbon(add, left + 0.32, right - 0.32, 19.25, 20.76)
    for edge in faces(low):
        span, add, _, plan, _, _ = chapter.setup_face(parts, *edge)
        if span > 3.4 and upper.distance(Point(plan(span / 2, 0.08))) > 0.45:
            for sill in (0.62, 4.12, 7.55):
                ribbon(add, 0.68, span - 0.68, sill, sill + 1.0)
    return outline, [lower, low_wall], posts, floor, gate


def office(parts, ground, field, row):
    outline = orient(Polygon(row["outline_enu_m"]))
    floor = design.science.earlier.fit_base(field, outline)[0]
    top = row["roof_surface_z_m"]
    slab(parts, outline, floor, top, MASONRY, (159, 157, 142))
    roof_border(parts, outline, top, MASONRY)
    equipment(parts, outline, top, row["equipment"])
    gate, door_edge, station = district.approach(
        parts, ground, faces(outline), field, row
    )
    for edge in faces(outline):
        span, add, outward, _, _, _ = chapter.setup_face(parts, *edge)
        if span < 1.8:
            continue
        for z in (0.25, 3.6, 6.88, 10.25, 13.60):
            add(0.015, span - 0.015, 0.005, 0.037, z - 0.13, z - 0.067, (179, 161, 127))
            if edge == door_edge and z < 2:
                ribbon(add, 1.4, station - 2.0, z, z + 1.28)
                ribbon(add, station + 2.0, span - 1.4, z, z + 1.28)
            else:
                ribbon(add, 1.25, span - 1.25, z, z + 1.28)
        if edge == door_edge:
            add(station - 2.64, station + 2.64, -0.15, 2.04, 1.45, 1.72, TRIM)
            for index in (0, 1):
                x = station + (2 * index - 1) * 2.13
                add(x - 0.14, x + 0.14, 1.68, 1.96, floor + 0.12, 1.45, STONE)
        if outward[0] > 0.6:
            for station_e in np.arange(3.0, span - 2.3, 7.4):
                add(station_e - 0.09, station_e + 0.09, 0.017, 0.053, 0.9, 1.15, TRIM)
    return outline, [outline], [], floor, gate


def garage(parts, ground, field, row):
    outline = orient(Polygon(row["outline_enu_m"]))
    floor, walls, posts, gate = district.deck(parts, field, row, outline, ground)
    link = box(*row["clinic_link_enu_m"])
    low, high = row["clinic_link_z_m"]
    slab(parts, link, low, high, STONE)
    for edge in faces(link):
        span, add, _, _, _, _ = chapter.setup_face(parts, *edge)
        ribbon(add, 0.23, span - 0.23, low + 0.46, high - 0.33)
    section = row["deck_sections"][0]
    datum = section["surface_z_m"]
    dx, dy = section["slope"]
    e0, n0 = outline.centroid.coords[0]
    clearance = outline.buffer(-0.6)
    for west, east in row["stall_rows_enu_m"]:
        for north in np.arange(25.4, 116.3, 2.66):
            stripe = box(west, north, east, north + 0.095)
            if clearance.covers(stripe):
                x, n = stripe.centroid.coords[0]
                z = datum + (x - e0) * dx + (n - n0) * dy
                slab(
                    parts, stripe, z + 0.007, z + 0.019, (190, 186, 162), slope=(dx, dy)
                )
    hint = Point(row["entrance"]["near_enu_m"])
    south = next(
        edge for edge in faces(outline) if LineString(edge).distance(hint) < 0.4
    )
    span, add, _, _, _, _ = chapter.setup_face(parts, *south)
    center = LineString(south).project(hint)
    for left, right in [(1.2, center - 2.45), (center + 2.45, span - 1.2)]:
        if right - left > 2.0:
            for a in np.arange(left, right - 1.25, 4.9):
                b = min(a + 4.45, right)
                add(a, b, 0.105, 0.167, floor + 0.26, floor + 2.07, GLASS)
                add(a, a + 0.09, 0.17, 0.212, floor + 0.20, floor + 2.11, TRIM)
    add(0.12, span - 0.12, -0.02, 0.65, floor + 2.17, floor + 2.39, STONE)
    return outline, walls, posts, floor, gate


def build(spec, manifest, config, field, graph):
    records, ground, solids, supports, entrances = [], [], [], [], []
    meshes = {}
    builders = {"clinic": clinic, "garage": garage, "office": office}
    for row in spec["models"]:
        parts = []
        area, walls, posts, floor, gate = builders[row["kind"]](
            parts, ground, field, row
        )
        assert area.is_valid and all(wall.is_valid for wall in walls)
        id = row["id"]
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.000012))
        meshes[id] = design.science.ordered_mesh(mesh)
        solids.extend(walls)
        supports.extend(posts)
        entrances.append(gate)
        records.append(
            {
                "id": id,
                "name": row["name"],
                "street_address": row["street_address"],
                "footprint_enu_m": base.ring(area),
                "ground_footprints_enu_m": [base.ring(wall) for wall in walls],
                "support_collision_enu_m": [base.ring(post) for post in posts],
                "area_m2": round(union_all(walls).area, 3),
                "base_z_m": round(float(floor), 4),
                "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
                "entrances": [gate],
            }
        )
    previous = union_all(
        [
            Polygon(record["footprint_enu_m"])
            for record in manifest["buildings"]
            if record["id"] in spec["source_ranges"]
        ]
    )
    count, distance = chapter.prior.nearby.shared.graduate.shared.check_routes(
        solids, supports, entrances, previous, manifest, graph, config, set(meshes)
    )
    return (
        meshes,
        records,
        design.science.ordered_mesh(trimesh.util.concatenate(ground)),
        count,
        distance,
    )


def source_ranges(spec, config, appearances):
    # The two source footprints touch. Pin their independently checked mesh
    # ranges, since buffered geographic selection also catches a few peer faces.
    source = SCENE / config["asset_url"]
    assert (
        design.tools.digest(source)
        == spec["source_presentation_model_sha256"]
        == config["asset_sha256"]
    )
    target = spec["source_batch"]
    original = trimesh.load(source, force="scene", process=False)
    transform, name = original.graph[target]
    assert np.array_equal(transform, np.eye(4))
    triangles = original.geometry[name].triangles
    records = {row["id"]: row for row in appearances["appearance_plan"]}
    ranges = spec["source_ranges"]
    remove = np.zeros(len(triangles), dtype=bool)
    patches = []
    candidates = np.zeros(len(triangles), dtype=bool)
    for id, (start, end) in ranges.items():
        assert id in appearances["context_batches"][target]
        assert 0 <= start < end <= len(triangles) and not remove[start:end].any()
        footprint = Polygon(records[id]["footprint_enu_m"]).buffer(0.29)
        matches = intersects_xy(footprint, triangles[:, :, 0], -triangles[:, :, 2]).all(
            axis=1
        )
        assert matches[start:end].all(), id
        remove[start:end] = True
        candidates |= matches
        body = triangles[start:end].reshape(-1, 3)
        patches.append(
            {
                "id": id,
                "target": target,
                "triangles": [start, end],
                "source_triangle_count": len(triangles),
                "source_vertices": [
                    [index, body[index].round(6).tolist()]
                    for index in (0, len(body) // 2, len(body) - 1)
                ],
            }
        )
    assert np.array_equal(candidates, remove)
    return patches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    spec = json.loads(
        (ROOT / "data/metadata/university-district-clinic-review.json").read_bytes()
    )
    manifest_path, config_path = SCENE / "manifest.json", SCENE / "presentation.json"
    manifest, config = [
        json.loads(file.read_bytes()) for file in (manifest_path, config_path)
    ]
    terrain = SCENE / manifest["heightfield_url"]
    digest = design.tools.digest
    assert digest(manifest_path) == spec["source_manifest_sha256"]
    assert digest(terrain) == spec["source_heightfield_sha256"]
    meshes, records, ground, count, nearest = build(
        spec,
        manifest,
        config,
        json.loads(terrain.read_bytes()),
        json.loads((SCENE / "navigation.json").read_bytes()),
    )
    appearances = json.loads(
        (ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    patches = source_ranges(spec, config, appearances)
    out = args.stage or SCENE / PACKAGE
    out.mkdir(parents=True, exist_ok=True)
    model, descriptor = out / "site.glb", out / "site.json"
    design.site.memorial.gerlinger.export(
        model, meshes, ground, GROUND, "university-district-clinic-paving"
    )
    bundle = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": digest(model),
        "buildings": records,
        "absorbed_ids": [],
        "split_buildings": spec["source_split"],
        "batch_removals": patches,
    }
    descriptor.write_text(
        json.dumps(bundle, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    sha = digest(descriptor)
    if args.stage is None:
        config[KEY] = {"url": f"{PACKAGE}/site.json", "sha256": sha}
        config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf8",
            newline="\n",
        )
    audit = {
        "buildings": records,
        "batch_removals": patches,
        "route_edges": count,
        "nearest_route_m": round(nearest, 4),
        "triangles": {id: len(mesh.faces) for id, mesh in meshes.items()},
        "glb_sha256": bundle["sha256"],
        "descriptor_sha256": sha,
    }
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(
        {
            key: audit[key]
            for key in ("route_edges", "nearest_route_m", "triangles", "glb_sha256")
        }
    )


if __name__ == "__main__":
    main()
