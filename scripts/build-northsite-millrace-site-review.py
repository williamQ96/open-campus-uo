# SPDX-License-Identifier: Apache-2.0
"""Export the registered Fine Arts Studios and 1600 Millrace exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

loader = spec_from_file_location(
    "science_site", Path(__file__).with_name("build-northeast-science-site-review.py")
)
science = module_from_spec(loader)
loader.loader.exec_module(science)
prior, site, tools = science.prior, science.site, science.tools
flat, union, ring = science.flat, science.union, science.ring
geometry, shared = science.geometry, science.shared
SCENE = science.SCENE
SPEC = geometry.ROOT / "data/metadata/northsite-millrace-site-review.json"
DIRECTORY = "northsite-millrace-review"
GROUND = "northsite-millrace-grounds"

PLY = (130, 103, 77)
PLANK = (159, 128, 93)
TIMBER = (144, 98, 60)
TRIM = (181, 155, 120)
GLASS = (74, 105, 105)
GLASS_PALE = (104, 133, 139)
BLUE = (76, 109, 134)
BLUE_DARK = (58, 83, 106)
CREAM = (205, 200, 178)
SAND = (176, 159, 132)
ROOF = (156, 143, 116)
WHITE_ROOF = (190, 190, 173)
METAL = (164, 163, 151)
BRICK = (161, 104, 81)
DARK_BRICK = (110, 93, 80)
CONCRETE = (174, 166, 150)
PAVING = (172, 166, 146)
LAWN = (148, 158, 111)


def skylight(parts, center, ridge_n, ridge_z, top):
    width = 6.35
    left, right = center - width * 0.5, center + width * 0.5
    outline = box(left, ridge_n, right, ridge_n + 3.12)

    def zinc(e, n):
        return (
            ridge_z - (ridge_z - top(e, ridge_n + 3.12) - 0.13) * (n - ridge_n) / 3.12
        )

    bottom = top(center, ridge_n) - 0.03
    site.surface(parts, outline, bottom, zinc, CREAM, WHITE_ROOF)
    length, add = tools.face(parts, (left, ridge_n), (right, ridge_n))
    prior.curtain(add, length, bottom + 0.16, ridge_z - 0.145, 8, 2, offset=0.028)
    for z in (bottom + 0.076, ridge_z - 0.094):
        add(0.06, length - 0.06, 0.017, 0.10, z, z + 0.048, CREAM)


def studio_walls(parts, outline, top, gates, datum):
    for a, b in shared.face_edges(outline):
        length, add = tools.face(parts, a, b)
        if length < 1.20:
            continue
        edge = LineString((a, b))
        panels = max(1, round(length / 1.28))
        pitch = length / panels
        for index in range(panels):
            u = pitch * (index + 0.5)
            p, q = edge.interpolate(u - pitch * 0.44), edge.interpolate(
                u + pitch * 0.44
            )
            z = min(top(p.x, p.y), top(q.x, q.y)) - 0.23
            add(u - 0.022, u + 0.022, 0.008, 0.039, datum + 0.16, z, PLANK)
            if (
                index % 2 == 1
                and z > datum + 2.28
                and prior.clear_of_entry(edge, u, pitch * 0.45, gates)
            ):
                prior.window(add, u, pitch * 0.74, z - 0.83, z - 0.11, TRIM, GLASS, 2)
        for station in np.linspace(
            0.16, length - 0.16, max(2, round(length / 2.54) + 1)
        ):
            p = edge.interpolate(station)
            add(
                station - 0.049,
                station + 0.049,
                0.014,
                0.123,
                datum + 0.07,
                top(p.x, p.y) - 0.16,
                TRIM,
            )
    prior.painted_doors(parts, shared.face_edges(outline), gates, TRIM, GLASS)


def passage(parts, field, bounds):
    x, y, X, Y = bounds
    middle = (x + X) * 0.5
    grade = geometry.sample_ground(field, middle, (y + Y) * 0.5)
    top = grade + 2.79
    flat(parts, box(x, y, X, Y), top - 0.167, top, TRIM, METAL)
    for e in (x + 0.21, X - 0.21):
        tools.beam(parts, (e, y, top - 0.16), (e, Y, top - 0.16), 0.17, TIMBER)
    feet = []
    for e in (x + 0.20, X - 0.20):
        for n in (y + 1.26, (y + Y) * 0.5, Y - 1.21):
            ground = geometry.sample_ground(field, e, n)
            support = box(e - 0.11, n - 0.11, e + 0.11, n + 0.11)
            flat(parts, support, ground - 0.13, top - 0.16, TIMBER)
            feet.append(support)
    return feet


def kiln(parts, field, row):
    projection = orient(Polygon(row["footprint_enu_m"]))
    west, south, east, north = projection.bounds
    ridge, peak = row["ridge_e"], row["ridge_z"]
    for left, right, eave, gradient in (
        (west - 0.08, ridge, row["eave_w"], (peak - row["eave_w"]) / (ridge - west)),
        (ridge, east + 0.08, row["eave_e"], -(peak - row["eave_e"]) / (east - ridge)),
    ):
        roof = projection.intersection(box(left, south - 0.04, right, north + 0.04))
        science.earlier.roof_layer(
            parts,
            roof,
            lambda e, n: peak + (e - ridge) * gradient,
            0.14,
            0.0,
            TIMBER,
            ROOF,
        )
    feet = []
    for e, n in row["poles"]:
        p = Point(e, n)
        assert projection.buffer(0.005).covers(p), (e, n)
        soil = geometry.sample_ground(field, e, n)
        level = (
            peak - (peak - row["eave_w"]) * abs(e - ridge) / (ridge - west)
            if e < ridge
            else (peak - (peak - row["eave_e"]) * abs(e - ridge) / (east - ridge))
        )
        pad = box(e - 0.16, n - 0.16, e + 0.16, n + 0.16)
        flat(parts, pad, soil - 0.086, soil + 0.11, CONCRETE)
        flat(parts, pad.buffer(-0.06, join_style=2), soil + 0.095, level - 0.12, TIMBER)
        tools.beam(
            parts, (e, n, level - 0.78), (e, n + 0.69, level - 0.17), 0.13, TIMBER
        )
        feet.append(pad)
    for n in (321.1, 327.25, 334.1, 340.75):
        a, b = -5.27, 4.20
        tools.beam(parts, (a, n, 1.80), (b, n, 1.80), 0.165, TIMBER)
        tools.beam(parts, (a, n, 1.80), (ridge, n, peak - 0.24), 0.146, TIMBER)
        tools.beam(parts, (b, n, 1.80), (ridge, n, peak - 0.24), 0.146, TIMBER)
    return feet


def studio(parts, field, row, outline, entries, floor, datum):
    primary = orient(Polygon(row["main_roof_enu_m"]))
    levels = row["levels"]
    station, height = levels["anchor"]

    def roof(e, n):
        return height + 0.230 * (n - station)

    site.surface(parts, primary, floor, lambda e, n: roof(e, n) - 0.11, PLY, ROOF)
    overhang = primary.buffer(0.25, join_style=2)
    for section in row["annexes_enu_m"]:
        overhang = overhang.difference(Polygon(section))
    science.earlier.roof_layer(parts, overhang, roof, 0.13, 0, TRIM, ROOF)
    for center in levels["monitors"]:
        skylight(parts, center, *levels["ridge"], roof)
    studio_walls(parts, primary, roof, entries, datum)
    for polygon in row["annexes_enu_m"]:
        annex = orient(Polygon(polygon))
        roof_z = 2.53 if annex.centroid.x < -18 else 2.72
        flat(parts, annex, floor, roof_z, PLY, WHITE_ROOF)
        flat(
            parts,
            annex.buffer(0.09, join_style=2),
            roof_z - 0.13,
            roof_z + 0.068,
            TRIM,
            WHITE_ROOF,
        )
        studio_walls(parts, annex, lambda e, n: roof_z, entries, datum)
    feet = []
    if "canopy" in levels:
        feet.extend(passage(parts, field, levels["canopy"]))
    if "kiln" in row:
        feet.extend(kiln(parts, field, row["kiln"]))
    return feet


def office_glass(parts, a, b, datum, top, entry):
    length, add = tools.face(parts, a, b)
    if length < 0.22:
        return
    edge = LineString((a, b))
    panels = max(1, round(length / 1.12))
    entry_point = Point(entry["position_enu_m"])
    for floor, z in enumerate(np.linspace(datum + 0.51, top - 0.20, 8)[:-1]):
        upper = datum + 0.51 + (top - datum - 0.71) * (floor + 1) / 7
        for index in range(panels):
            u0 = index * length / panels
            u1 = (index + 1) * length / panels
            if upper < datum + 2.73 and not prior.clear_of_entry(
                edge, (u0 + u1) * 0.5, (u1 - u0) * 0.5, [entry]
            ):
                continue
            add(
                u0 + 0.013,
                u1 - 0.012,
                0.016,
                0.068,
                z + 0.012,
                upper - 0.021,
                BLUE if (floor + index) % 4 else BLUE_DARK,
            )
        add(0.012, length - 0.012, 0.066, 0.109, upper - 0.029, upper + 0.038, METAL)
    for u in np.linspace(0.033, length - 0.033, panels + 1):
        add(u - 0.019, u + 0.019, 0.065, 0.113, datum + 0.49, top - 0.16, CREAM)
    if edge.distance(entry_point) < 0.026:
        add(0.011, length - 0.011, 0.086, 0.20, datum + 2.53, datum + 2.93, CREAM)


def office(parts, row, outline, gates, floor, datum):
    levels = row["levels"]
    main, parapet, top = (levels[k] for k in ("main", "parapet", "rotunda"))
    flat(parts, outline, floor, main, SAND, WHITE_ROOF)
    rotunda = outline.intersection(box(*levels["rotunda_range"]))
    flat(parts, rotunda, main - 0.092, top, METAL, WHITE_ROOF)
    for a, b in shared.face_edges(outline):
        length, add = tools.face(parts, a, b)
        edge = LineString((a, b))
        if length < 0.28:
            continue
        midpoint = edge.interpolate(0.5, normalized=True)
        curved = rotunda.buffer(0.005).covers(midpoint)
        top_band = top if curved else parapet
        add(0.024, length - 0.024, -0.077, 0.071, main - 0.04, top_band, CREAM)
        if curved:
            office_glass(parts, a, b, datum, top, gates[0])
            continue
        bays = max(1, round(length / 3.27))
        pitch = length / bays
        step = (main - datum - 0.19) / 3
        for story in range(3):
            z = datum + 0.19 + step * story
            add(0.016, length - 0.016, 0.009, 0.061, z + 0.09, z + 0.46, DARK_BRICK)
            add(
                0.022,
                length - 0.022,
                0.02,
                0.072,
                z + step * 0.57,
                z + step * 0.92,
                BRICK,
            )
            add(
                0.022,
                length - 0.022,
                0.03,
                0.09,
                z + step * 0.92,
                z + step - 0.017,
                CREAM,
            )
            for i in range(bays):
                u = (i + 0.5) * pitch
                if story or prior.clear_of_entry(edge, u, pitch * 0.34, gates):
                    prior.window(
                        add, u, pitch * 0.68, z + 0.73, z + step * 0.71, CREAM, BLUE, 2
                    )
    for x, y, X, Y, z in row["equipment"]:
        flat(
            parts,
            box(x, y, X, Y).intersection(outline),
            main - 0.048,
            z,
            SAND,
            WHITE_ROOF,
        )
    prior.painted_doors(parts, shared.face_edges(outline), gates, CREAM, BLUE)
    return []


def build(spec, manifest, config, field, graph):
    meshes, buildings, ground, solids, supports, gates, pads = (
        {},
        {},
        [],
        [],
        [],
        [],
        [],
    )
    for code, row in spec["models"].items():
        outline = orient(Polygon(row["footprint_enu_m"]))
        floor, datum = science.earlier.fit_base(field, outline)
        parts, entries, feet = [], [], []
        for entry in row["entrances"]:
            assert (
                outline.boundary.distance(Point(entry["position_enu_m"])) < 0.006
            ), entry
            gate, path, obstructions = shared.site_entry(ground, field, entry)
            entries.append(gate)
            feet.extend(obstructions)
            pads.append(path)
        if code == "750":
            feet.extend(office(parts, row, outline, entries, floor, datum))
        else:
            feet.extend(studio(parts, field, row, outline, entries, floor, datum))
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        id = row["id"]
        meshes[id] = science.ordered_mesh(mesh)
        buildings[id] = dict(
            id=id,
            name=row["name"],
            campus_id=row["campus_id"],
            footprint_enu_m=ring(outline),
            ground_footprints_enu_m=[ring(outline)],
            support_collision_enu_m=[ring(p) for p in feet],
            entrances=entries,
            base_z_m=round(floor, 4),
            roof_z_m=round(float(mesh.bounds[1, 1]), 4),
            area_m2=round(outline.area, 3),
        )
        soles = [outline]
        solids.extend(soles)
        supports.extend(feet)
        gates.extend(entries)
    known = set(meshes)
    baseline = union(
        [
            Polygon(row["footprint_enu_m"]).buffer(0)
            for row in manifest["buildings"]
            if row["id"] in known
        ]
    )
    edges, clearance = prior.nearby.shared.graduate.shared.check_routes(
        solids, supports, gates, baseline, manifest, graph, config, known
    )
    blocked = union([*solids, *supports])
    walks = []
    for path in spec["paths"]:
        strip = LineString(path["line"]).buffer(
            path["width_m"] / 2, cap_style=2, join_style=2
        )
        walks.append(strip)
    walk_surface = union([*walks, *pads])
    lawn = Polygon(spec["office_entry_lawn_enu_m"])
    prior.nearby.add_paths(ground, field, lawn, union([blocked, walk_surface]), LAWN)
    prior.nearby.add_paths(ground, field, walk_surface, blocked, PAVING)
    return (
        meshes,
        list(buildings.values()),
        science.ordered_mesh(trimesh.util.concatenate(ground)),
        edges,
        clearance,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest_path = SCENE / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    assert tools.digest(manifest_path) == spec["sources"]["scene_manifest_sha256"]
    assert tools.digest(field_path) == spec["sources"]["heightfield_sha256"]
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, buildings, ground, edges, clearance = build(
        spec, manifest, config, field, graph
    )
    appearances = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, appearances
    )
    output = args.stage if args.stage else SCENE / DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    model = output / "site.glb"
    site.memorial.gerlinger.export(
        model, meshes, ground, GROUND, "northsite-millrace-paving"
    )
    descriptor = output / "site.json"
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        ground_node=GROUND,
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(model),
        buildings=buildings,
        absorbed_ids=[],
        batch_removals=removals,
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    if args.stage is None:
        config["northsite_millrace_site"] = dict(
            url=f"{DIRECTORY}/site.json", sha256=tools.digest(descriptor)
        )
        config_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf8",
            newline="\n",
        )
    audit = dict(
        buildings=buildings,
        route_edges=edges,
        nearest_route_m=round(clearance, 3),
        triangles={id: len(mesh.faces) for id, mesh in meshes.items()},
        batch_removals=removals,
        glb_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(
        json.dumps(
            {
                key: audit[key]
                for key in ("route_edges", "nearest_route_m", "triangles", "glb_sha256")
            }
        )
    )


if __name__ == "__main__":
    main()
