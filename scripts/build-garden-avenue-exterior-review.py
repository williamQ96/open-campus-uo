# SPDX-License-Identifier: Apache-2.0
"""Export the separately registered Garden Avenue exterior models."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import set_precision, union_all
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient
import trimesh

path = Path(__file__).with_name("build-east-campus-housing-exterior-review.py")
spec = spec_from_file_location(path.stem, path)
housing = module_from_spec(spec)
spec.loader.exec_module(housing)
design, approaches = housing.design, housing.approaches
base, geometry, chapter, shared = (
    housing.base,
    housing.geometry,
    housing.chapter,
    housing.shared,
)
SCENE, ROOT = housing.SCENE, housing.ROOT
PACKAGE = "garden-avenue-exterior-review"
KEY = "garden_avenue_exterior_site"
GROUND = "garden-avenue-approaches"
SPEC = ROOT / "data/metadata/garden-avenue-exterior-review.json"
CONCRETE = (156, 154, 138)
METAL = (78, 84, 77)
GLASS = (86, 117, 123)
DARK_WINDOW = (68, 85, 83)


def window(add, u, width, base_z, top, trim, ribs=1):
    chapter.prior.window(add, u, width, base_z, top, trim, GLASS, ribs=ribs)


def across_frame(row):
    origin = np.asarray(row["roof_frame"]["origin_enu_m"])
    u = np.asarray(row["roof_frame"]["axis"])
    u /= np.linalg.norm(u)
    v = np.asarray([-u[1], u[0]])
    return origin, u, v


def solar_modules(parts, roof, row, height):
    origin, u, v = across_frame(row)
    panels = 0
    for field in row["solar_fields"]:
        stations = np.linspace(field["first_u_m"], field["last_u_m"], field["columns"])
        for a in stations:
            for b in field["row_v_m"]:
                corners = [
                    origin + x * u + y * v
                    for x, y in (
                        (a - 0.45, b - 0.76),
                        (a + 0.45, b - 0.76),
                        (a + 0.45, b + 0.76),
                        (a - 0.45, b + 0.76),
                    )
                ]
                tile = Polygon(corners)
                assert roof.covers(tile), (row["id"], a, b)
                lower = min(height(p) for p in corners) - 0.12
                module = geometry.shell(
                    tile,
                    lower,
                    lambda e, n: height((e, n)) + 0.116,
                    (116, 123, 115),
                    (52, 68, 81),
                )
                skirt = np.isclose(module.vertices[:, 1], lower, rtol=0, atol=1e-6)
                module.vertices[skirt, 1] = [
                    height((e, -z)) + 0.051 for e, _, z in module.vertices[skirt]
                ]
                parts.append(module)
                panels += 1
    return panels


def window_bay(add, u, bottom, upper, trim):
    projection = 0.36
    half = 0.81
    add(u - half, u + half, -0.018, projection, bottom - 0.17, upper + 0.14, trim)

    def pane(left, right, recess, face, sill, head, color):
        add(left, right, projection + recess, projection + face, sill, head, color)

    window(
        pane,
        u,
        1.33,
        bottom,
        upper,
        trim,
        ribs=2,
    )
    add(
        u - half - 0.04,
        u + half + 0.04,
        0,
        projection + 0.08,
        upper + 0.12,
        upper + 0.22,
        trim,
    )


def office_bands(add, length, ground_z, top, tone):
    for low, high in ((0.72, 1.92), (3.69, 4.81)):
        if ground_z + high < top - 0.16:
            add(
                0.016,
                length - 0.016,
                -0.004,
                0.019,
                ground_z + low,
                ground_z + high,
                tone,
            )


def porch(parts, add, point, field, row, entry, u):
    kind = row["profile"]
    z = entry["threshold_z_m"]
    tone = row["trim_color"]
    supports = []
    if kind == "millrace":
        return supports
    half, depth = (2.25, 2.09) if kind == "three-level" else (1.74, 1.51)
    if kind == "solar-office":
        add(u - half, u + half, -0.012, 0.37, z + 2.9, z + 3.15, tone)
        return supports
    for x in (u - half + 0.13, u + half - 0.13):
        p = point(x, depth - 0.15)
        low = min(z - 0.14, geometry.sample_ground(field, *p) - 0.055)
        supports.append(approaches.supported_post(parts, p, low, z + 2.53, tone, 0.105))
    chapter.gabled_canopy(
        parts,
        point,
        u,
        half + 0.105,
        -0.018,
        depth + 0.13,
        z + 2.55,
        0.60 if kind == "three-level" else 0.36,
        row["roof_color"],
        tone,
    )
    return supports


def river_stair(parts, field, edges, entry, row, height):
    origin, u, v = across_frame(row)
    position = origin + 11.10 * u + 6.66 * v
    edge = design.locate_face(edges, position, entry["outward_degrees"])
    length, add, _, point, _, _ = chapter.setup_face(parts, *edge)
    foot = geometry.sample_ground(field, *point(6.4, 1.96))
    deck = foot + 2.83
    assert length > 8 and height(point(1.5, 0)) > deck + 2.11, row["id"]
    add(0.13, 2.08, -0.025, 1.92, deck - 0.15, deck, CONCRETE)
    design.neighbor.railing(add, 0.13, 2.08, 1.92, deck)
    design.neighbor.side_stair(add, 1.94, 1.92, foot, 2.83, reverse=True)
    return [
        approaches.supported_post(
            parts, point(x, 1.79), foot - 0.08, deck, CONCRETE, 0.15
        )
        for x in (0.31, 1.94)
    ]


def elevations(parts, field, row, edges, entry, door_edge, door_u, height):
    kind = row["profile"]
    tone = row["trim_color"]
    supports = []
    steps = {
        "three-level": 2.62,
        "millrace": 2.50,
        "solar-office": 3.02,
        "river-office": 2.96,
    }
    levels = 3 if kind == "three-level" else 2
    bay_mat = tuple(max(0, c - 24) for c in row["wall_color"])
    for edge in edges:
        length, add, _, point, _, _ = chapter.setup_face(parts, *edge)
        if length < 1.24:
            continue
        grade = geometry.sample_ground(field, *point(length / 2, 0))
        local_eave = min(height(point(q, 0)) for q in (0.01, length - 0.01)) - 0.15
        if kind == "river-office":
            office_bands(add, length, grade, local_eave, (131, 121, 104))
        elif kind == "millrace":
            for at in np.arange(0.14, length - 0.07, 0.27):
                head = height(point(at, 0)) - 0.18
                if head > grade + 2.94:
                    add(at, at + 0.013, -0.001, 0.018, grade + 2.8, head, bay_mat)
        else:
            for z in np.arange(grade + 0.30, local_eave - 0.09, 0.27):
                add(0.02, length - 0.02, -0.005, 0.010, z, z + 0.017, bay_mat)
        add(0.012, length - 0.012, 0, 0.036, grade - 0.095, grade + 0.18, CONCRETE)
        if length > 2.42:
            spacing = 4.55 if kind == "three-level" else 3.7
            count = max(1, round(length / spacing))
            for bay, u in enumerate((np.arange(count) + 0.5) * length / count):
                for floor in range(levels):
                    if floor == 0 and edge == door_edge and abs(u - door_u) < 1.52:
                        continue
                    width = min(
                        length / count * 0.69, 2.28 if kind == "solar-office" else 1.63
                    )
                    sill = (
                        grade
                        + (0.86 if kind == "millrace" else 0.80)
                        + floor * steps[kind]
                    )
                    upper = min(
                        sill + 1.31,
                        min(height(point(u + d, 0)) for d in (-width / 2, width / 2))
                        - 0.27,
                    )
                    if upper - sill < 0.68:
                        continue
                    if (
                        floor == 1
                        and kind == "millrace"
                        and edge == door_edge
                        and bay % 2 == 0
                    ):
                        window_bay(add, u, sill, upper, tone)
                    else:
                        window(
                            add,
                            u,
                            width,
                            sill,
                            upper,
                            tone,
                            ribs=2 if width > 1.84 else 1,
                        )
                if (
                    kind == "three-level"
                    and edge == door_edge
                    and 0.07 < u / length < 0.93
                ):
                    top = min(height(point(u, 0)), local_eave)
                    trim = min(1.41, length / count * 0.28)
                    add(
                        u - trim,
                        u - trim + 0.075,
                        0.018,
                        0.035,
                        grade + 3,
                        top - 0.07,
                        tone,
                    )
                    add(
                        u + trim - 0.075,
                        u + trim,
                        0.018,
                        0.035,
                        grade + 3,
                        top - 0.07,
                        tone,
                    )
        if edge != door_edge:
            continue
        z = entry["threshold_z_m"]
        if kind == "millrace":
            left, right = max(0.08, door_u - 2.18), min(length - 0.08, door_u + 2.18)
            depth = 0.93
            add(left, right, -0.01, depth, z - 0.14, z, CONCRETE)
            for low, high in ((left, door_u - 0.77), (door_u + 0.77, right)):
                if high - low > 0.28:
                    design.neighbor.railing(add, low, high, depth, z, tone)
        elif kind == "solar-office":
            for off in (-1.08, 1.08):
                u = door_u + off
                if 0.36 < u < length - 0.36:
                    add(u - 0.22, u + 0.22, 0.012, 0.105, z - 0.05, z + 5.05, tone)
            add(
                door_u - 0.82,
                door_u + 0.82,
                0.02,
                0.081,
                z + 2.29,
                z + 5.01,
                DARK_WINDOW,
            )
            for h in (z + 2.28, z + 3.66, z + 4.96):
                add(door_u - 0.83, door_u + 0.83, 0.082, 0.098, h, h + 0.082, tone)
        elif kind == "river-office":
            add(door_u - 1.45, door_u + 1.45, 0.015, 0.102, z + 0.06, z + 2.36, GLASS)
            for dx in (-1.46, -0.73, 0, 0.73, 1.46):
                add(
                    door_u + dx - 0.032,
                    door_u + dx + 0.032,
                    0.103,
                    0.126,
                    z + 0.06,
                    z + 2.39,
                    tone,
                )
            left = max(0.12, door_u - 7.08)
            right = door_u - 1.28
            if right - left > 1.9:
                a = point(left, 0.10)
                b = point(right, 0.10)
                direction = (b - a) / np.dot(b - a, b - a)
                toe = geometry.sample_ground(field, *a) + 0.055
                ramp = Polygon(
                    [
                        point(u, v)
                        for u, v in (
                            (left, 0.09),
                            (right, 0.09),
                            (right, 1.32),
                            (left, 1.32),
                        )
                    ]
                )
                parts.append(
                    geometry.shell(
                        ramp,
                        min(toe, z) - 0.16,
                        lambda e, n: toe
                        + (np.array([e, n]) - a) @ direction * (z - toe),
                        CONCRETE,
                        CONCRETE,
                    )
                )
                design.neighbor.railing(
                    add, left, right, 1.30, max(toe, z) - 0.08, METAL
                )
        supports.extend(porch(parts, add, point, field, row, entry, door_u))
    if kind == "river-office":
        supports.extend(river_stair(parts, field, edges, entry, row, height))
    return supports


def front_gables(parts, edges, row, gate, height):
    origin, along, across = across_frame(row)
    for offset in (-13.2, 13.2):
        near = origin + offset * along + 8.9 * across
        edge = design.locate_face(edges, near, gate["outward_degrees"])
        length, add, _, point, _, slab = chapter.setup_face(parts, *edge)
        u = LineString(edge).project(Point(near))
        half = min(1.62, u - 0.1, length - u - 0.1)
        if half < 0.7:
            raise ValueError(
                f"Front gable does not fit the mapped facade for {row['id']}."
            )
        top = height(point(u, 0)) - 0.26
        left, right = u - half, u + half
        profile = Polygon([(left, top), (u, top + 0.93), (right, top)])
        slab(profile, -0.032, 0.105, row["wall_color"])
        verge = Polygon(
            [
                (left - 0.065, top + 0.025),
                (u, top + 1.01),
                (right + 0.065, top + 0.025),
                (right, top - 0.047),
                (u, top + 0.87),
                (left, top - 0.047),
            ]
        )
        slab(verge, -0.031, 0.162, row["trim_color"])
        for edge_u in (left, right):
            add(
                edge_u - 0.043,
                edge_u + 0.043,
                0.018,
                0.102,
                top - 3.12,
                top,
                row["trim_color"],
            )


def build(spec, manifest, config, field, graph):
    baseline = {r["id"]: r for r in manifest["buildings"]}
    models, records, footprints, columns, entries, ground, solar = (
        {},
        [],
        [],
        [],
        [],
        [],
        {},
    )
    for row in spec["models"]:
        id = row["id"]
        plan = orient(set_precision(Polygon(row["footprint_enu_m"]), 0.002))
        roof = orient(
            set_precision(plan.buffer(row["eaves_m"], join_style="mitre"), 0.002)
        )
        assert plan.is_valid and roof.covers(plan), id
        floor, _ = design.science.earlier.fit_base(field, plan)
        pieces = []
        height = design.roof_sections(pieces, roof, plan, floor, row, grid=0.0001)
        solar[id] = solar_modules(pieces, roof, row, height)
        faces = list(shared.face_edges(plan))
        gate, edge, u = approaches.entry_stair(pieces, ground, faces, field, row, None)
        supports = elevations(pieces, field, row, faces, gate, edge, u, height)
        if row["profile"] == "three-level":
            front_gables(pieces, faces, row, gate, height)
        mesh = trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.000012))
        models[id] = design.science.ordered_mesh(mesh)
        footprints.append(plan)
        columns.extend(supports)
        entries.append(gate)
        records.append(
            {
                "id": id,
                "name": row["name"],
                "street_address": row["street_address"],
                "footprint_enu_m": base.ring(plan),
                "area_m2": round(plan.area, 3),
                "support_collision_enu_m": [base.ring(p) for p in supports],
                "base_z_m": round(floor, 4),
                "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
                "entrances": [gate],
            }
        )
    old = union_all([Polygon(baseline[id]["footprint_enu_m"]) for id in models])
    n, clear = chapter.prior.nearby.shared.graduate.shared.check_routes(
        footprints,
        columns,
        entries,
        old,
        manifest,
        graph,
        config,
        set(models),
    )
    paving = design.science.ordered_mesh(trimesh.util.concatenate(ground))
    return models, records, paving, n, clear, solar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    p, config_path = SCENE / "manifest.json", SCENE / "presentation.json"
    manifest, config = [json.loads(f.read_bytes()) for f in (p, config_path)]
    field_path = SCENE / manifest["heightfield_url"]
    for path, key in (
        (p, "source_manifest_sha256"),
        (field_path, "source_heightfield_sha256"),
    ):
        if design.tools.digest(path) != spec[key]:
            raise ValueError(f"Changed Garden Avenue registration source: {path.name}")
    meshes, records, ground, n, clear, solar = build(
        spec,
        manifest,
        config,
        json.loads(field_path.read_bytes()),
        json.loads((SCENE / "navigation.json").read_bytes()),
    )
    appearances = json.loads(
        (ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    targets = {
        id: target
        for target, ids in appearances["context_batches"].items()
        for id in ids
    }
    patches = shared.frohnmayer.source_removals(
        {"absorbed_batches": [{"id": id, "target": targets[id]} for id in meshes]},
        config,
        appearances,
    )
    out = args.stage or SCENE / PACKAGE
    out.mkdir(exist_ok=True, parents=True)
    model, descriptor = out / "site.glb", out / "site.json"
    design.site.memorial.gerlinger.export(
        model, meshes, ground, GROUND, "garden-avenue-paving"
    )
    bundle = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": design.tools.digest(model),
        "buildings": records,
        "absorbed_ids": [],
        "batch_removals": patches,
    }
    descriptor.write_text(
        json.dumps(bundle, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    digest = design.tools.digest(descriptor)
    if args.stage is None:
        config[KEY] = {"url": f"{PACKAGE}/site.json", "sha256": digest}
        config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf8",
            newline="\n",
        )
    audit = {
        "buildings": records,
        "route_edges": n,
        "nearest_route_m": round(clear, 4),
        "batch_removals": patches,
        "triangles": {id: len(mesh.faces) for id, mesh in meshes.items()},
        "solar_panels": solar,
        "glb_sha256": bundle["sha256"],
        "descriptor_sha256": digest,
    }
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(
        {
            k: audit[k]
            for k in (
                "route_edges",
                "nearest_route_m",
                "triangles",
                "solar_panels",
                "glb_sha256",
            )
        }
    )


if __name__ == "__main__":
    main()
