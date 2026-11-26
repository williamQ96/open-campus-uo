# SPDX-License-Identifier: Apache-2.0
"""Build the registered Lawrence, Pacific and Columbia Hall exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-allen-site-review.py")
loader = spec_from_file_location(source.stem, source)
allen = module_from_spec(loader)
loader.loader.exec_module(allen)
tools, geometry, memorial = allen.tools, allen.geometry, allen.memorial
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/lawrence-science-site-review.json"
DIRECTORY = "lawrence-science-review"
GROUND = "lawrence-science-approaches"
MODELS = ("lawrence", "pacific", "columbia")
flat, surface = allen.flat, allen.surface
BRICK = (154, 103, 83)
BRICK_LIGHT = (174, 120, 95)
OCHRE = (180, 169, 148)
CLADDING = (174, 173, 157)
CAP = (192, 185, 160)
ROOF = (157, 155, 140)
ROOF_LIGHT = (173, 170, 151)
SHADOW = (110, 109, 96)
STEEL = (99, 106, 99)
PAVING = (159, 157, 145)
SKINS = {"brick": BRICK, "ochre": OCHRE, "cladding": CLADDING}


def outline(model):
    return orient(
        Polygon(model["footprint_enu_m"], model.get("footprint_holes_enu_m", []))
    )


def roof_volumes(parts, model, plan, base):
    remaining, regions = plan, []
    for zone in model["roof_sections"]:
        region = remaining.intersection(box(*zone["bounds"]))
        assert region.area > 4, zone["name"]
        remaining = remaining.difference(region)

        def height(e, n, zone=zone):
            return allen.membrane(zone, n)

        skin = zone["skin"]
        surface(parts, region, base, height, SKINS[skin], ROOF)
        rim = region.difference(region.buffer(-0.17, join_style="mitre"))
        low = min(height(0, n) for n in region.bounds[1::2])
        surface(
            parts, rim, low - 0.10, lambda e, n: height(e, n) + 0.15, SKINS[skin], CAP
        )
        regions.append((region, height, skin))
    z = model["default_roof_z_m"]
    flat(parts, remaining, base, z, BRICK, ROOF_LIGHT)
    regions.append((remaining, lambda e, n: z, "brick"))
    return regions


def slabs(parts, name):
    if name == "lawrence":
        for bounds, lo, hi in (
            ((-323.04, 126.82, -307.45, 136.38), 21.54, 25.66),
            ((-309.59, 190.29, -305.90, 200.33), 17.01, 23.12),
            ((-321.35, 180.41, -317.62, 187.59), 21.58, 23.02),
        ):
            flat(parts, box(*bounds), lo, hi, CLADDING, ROOF_LIGHT)
        for e in (-358.3, -352.8, -347.4, -340.7, -333.4, -326.8):
            flat(
                parts, box(e - 0.47, 140.13, e + 0.47, 141.27), 16.35, 17.09, STEEL, CAP
            )
        for n in range(152, 189, 6):
            flat(
                parts,
                box(-308.34, n - 0.60, -306.19, n + 0.63),
                21.74,
                22.65,
                STEEL,
                CAP,
            )
    elif name == "pacific":
        flat(
            parts, box(-270.80, 60.21, -268.10, 142.02), 17.25, 19.51, OCHRE, ROOF_LIGHT
        )
        for e, n, k in (
            (-279.52, 131.39, 23.64),
            (-272.44, 133.11, 24.91),
            (-267.80, 131.62, 22.63),
            (-277.10, 139.66, 21.80),
        ):
            flat(
                parts, box(e - 1.20, n - 1.05, e + 1.22, n + 1.29), 17.27, k, OCHRE, CAP
            )
        for n in range(65, 109, 7):
            flat(
                parts,
                box(-275.03, n - 0.55, -273.70, n + 0.49),
                17.25,
                18.01,
                STEEL,
                CAP,
            )
    else:
        for e, n, floor in (
            (-288.41, 30.37, 9.08),
            (-284.28, 38.34, 9.12),
            (-265.53, 28.22, 12.82),
            (-259.32, 37.44, 12.86),
        ):
            flat(
                parts,
                box(e - 0.67, n - 0.47, e + 0.67, n + 0.64),
                floor,
                floor + 0.73,
                STEEL,
                CAP,
            )


def face_spans(a, b, regions):
    edge = LineString((a, b))
    start = np.asarray(a)
    for area, height, skin in regions:
        for segment in shapely.get_parts(edge.intersection(area)):
            if segment.geom_type != "LineString" or segment.length < 0.18:
                continue
            start2, end2 = sorted(
                [segment.coords[0], segment.coords[-1]],
                key=lambda pt: float(np.linalg.norm(np.asarray(pt) - start)),
            )
            yield start2, end2, height, skin


def facade(parts, name, a, b, roof, skin, base, gate):
    length, add = tools.face(parts, a, b)
    eave = (roof(*a) + roof(*b)) / 2
    color = SKINS[skin]
    if gate:
        threshold = gate["threshold_z_m"]
        center = float(np.linalg.norm(np.array(gate["position_enu_m"]) - a))
        delta = min(2.32, center - 0.08, length - center - 0.08)
        left, right = center - delta, center + delta
        allen.doors(add, center, gate["width_m"], threshold)
        if delta > 1.18:
            high = min(eave - 0.62, threshold + 7.78)
            allen.windows(
                add, left, right, threshold + 2.44, high, 4, skin == "cladding"
            )
            add(
                left - 0.08,
                right + 0.08,
                0.094,
                0.96,
                threshold + 2.41,
                threshold + 2.61,
                CAP,
            )
        else:
            high = threshold + 2.65
    else:
        left, right, high = 0, 0, -99

    if skin == "brick":
        for z in np.arange(base + 1.05, eave - 0.22, 2.96):
            if z >= high or not gate:
                add(0, length, 0.011, 0.084, z, z + 0.063, BRICK_LIGHT)
    else:
        for u in np.arange(2.63, length - 0.16, 2.63):
            if not gate or not left < u < right:
                add(
                    u - 0.014, u + 0.014, 0.012, 0.035, base + 0.34, eave - 0.34, SHADOW
                )
    if length < 2.45:
        return
    rows = np.arange(4.34, eave - 2.0, 3.18)
    count = max(1, round(length / (2.69 if skin == "cladding" else 2.85)))
    step = length / count
    for z in rows:
        if skin == "cladding" and length > 6:
            add(0, length, 0.002, 0.045, z - 0.27, z - 0.16, color)
        for u in (np.arange(count) + 0.5) * step:
            if gate and left - 0.70 < u < right + 0.70 and z < high + 0.40:
                continue
            wing = step * (0.40 if skin == "cladding" else 0.27)
            height = 1.96 if name == "lawrence" and skin == "cladding" else 1.55
            add(
                u - wing - 0.08,
                u + wing + 0.08,
                0.041,
                0.095,
                z - 0.075,
                z + height + 0.12,
                BRICK_LIGHT if skin == "brick" else CAP,
            )
            allen.windows(
                add, u - wing, u + wing, z, z + height, 3 if skin == "cladding" else 2
            )
            add(
                u - wing - 0.10,
                u + wing + 0.10,
                0.062,
                0.195,
                z - 0.135,
                z - 0.056,
                CAP,
            )
    if name == "lawrence" and skin == "brick":
        for t in (0.20, length - 0.20):
            for z in np.arange(base + 1, eave - 0.32, 0.41):
                add(t - 0.15, t + 0.15, 0.007, 0.072, z, z + 0.066, BRICK_LIGHT)


def facades(parts, name, plan, regions, base, entries):
    for ring in (plan.exterior, *plan.interiors):
        for a, b in zip(ring.coords, list(ring.coords)[1:]):
            for c, d, height, skin in face_spans(a, b, regions):
                segment = LineString((c, d))
                gate = next(
                    (
                        gate
                        for gate in entries
                        if segment.distance(Point(gate["position_enu_m"])) < 0.002
                    ),
                    None,
                )
                if name == "columbia" and c[1] == d[1] == 19.21:
                    length, add = tools.face(parts, c, d)
                    add(0, length, 0.009, 0.093, base, 5.23, (152, 154, 144))
                facade(parts, name, c, d, height, skin, base, gate)


def columbia_extensions(parts, model, field):
    e0, n0, e1, n1 = model["loggia_bounds"]
    flat(parts, box(e0, n0, e1, n1), 6.54, 7.53, BRICK, ROOF_LIGHT)
    flat(parts, box(e0 - 0.07, n0 - 0.27, e1, n0 + 0.27), 6.45, 6.66, CAP)
    posts = []
    for e in (-292.42, -289.16, -281.06, -276.71, -272.03):
        post = box(e - 0.17, n0 + 0.16, e + 0.17, n0 + 0.53)
        z = geometry.sample_ground(field, e, n0 + 0.32)
        flat(parts, post, z - 0.23, 6.59, CAP)
        posts.append(post)
    bridge = box(*model["bridge_bounds"])
    flat(parts, bridge, 6.14, 10.61, OCHRE, ROOF_LIGHT)
    lo, south, hi, north = bridge.bounds
    for a, b in (((lo, north), (lo, south)), ((hi, south), (hi, north))):
        length, add = tools.face(parts, a, b)
        add(0, length, 0.008, 0.19, 6.13, 6.42, CAP)
        allen.windows(add, 0.41, length - 0.43, 7.07, 9.81, 5)
    return posts


def site_entry(parts, field, gate):
    e, n = gate["position_enu_m"]
    angle = np.deg2rad(gate["outward_degrees"])
    outward = np.array((np.sin(angle), np.cos(angle)))
    tangent = np.array((outward[1], -outward[0]))
    anchor = np.array([e, n])
    run = 1.99 if gate["gate"] == "pacific-west" else 1.21
    width = gate["width_m"] / 2 + 0.43
    rise = 0.45 if gate["gate"] == "pacific-west" else 0.12

    def walk(inner, outer):
        return Polygon(
            [
                anchor + outward * lng + tangent * w
                for lng, w in (
                    (inner, -width),
                    (outer, -width),
                    (outer, width),
                    (inner, width),
                )
            ]
        )

    toe = geometry.sample_ground(field, *(anchor + outward * run))
    steps = 3 if rise > 0.20 else 1
    for i, reach in enumerate(np.linspace(run, 0.57 if steps > 1 else run, steps)):
        flat(
            parts, walk(-0.017, reach), toe - 0.52, toe + (i + 1) * rise / steps, PAVING
        )
    return (
        walk(-0.017, run) if steps > 1 else None,
        walk(run - 0.056, gate["approach_distance_m"] + 1.20),
        gate | {"threshold_z_m": round(float(toe + rise), 3)},
    )


def courtyard(parts, field, model):
    open_air = Polygon(model["footprint_holes_enu_m"][0])
    paths = open_air.intersection(
        shapely.union_all(
            [box(-347.0, 149.02, -343.88, 178.42), box(-347.0, 149.04, -312.50, 151.82)]
        )
    )
    planter = box(-342.29, 156.13, -332.70, 166.83)
    z = min(
        geometry.sample_ground(field, e, n)
        for e, n in list(planter.exterior.coords)[:-1]
    )
    wall = planter.difference(planter.buffer(-0.21))
    flat(parts, wall, z - 0.22, z + 0.48, BRICK, CAP)
    for x, y, size in (
        (-340.74, 158.70, 0.84),
        (-335.53, 162.80, 1.28),
        (-339.43, 165.17, 0.99),
    ):
        foliage = trimesh.creation.icosphere(subdivisions=1)
        foliage.apply_scale([size, size * 0.64, size * 0.87])
        foliage.apply_translation([x, geometry.sample_ground(field, x, y) + 0.72, -y])
        foliage.visual.vertex_colors = [100, 120, 79, 255]
        parts.append(foliage)
    return list(geometry.sections(paths)), [planter]


def build(spec, manifest, field, graph):
    records, meshes, grounds, pavers, solids = [], {}, [], [], []
    projections = {}
    for name in MODELS:
        model = spec[name]
        key = model["id"]
        plan = outline(model)
        assert plan.is_valid
        minimum = min(
            geometry.sample_ground(field, *plan.exterior.interpolate(s).coords[0])
            for s in np.arange(0, plan.exterior.length, 0.56)
        )
        base = round(minimum - 0.54, 3)
        parts, entries, collision = [], [], []
        roofs = roof_volumes(parts, model, plan, base)
        slabs(parts, name)
        for gate in model["entrances"]:
            assert plan.exterior.distance(Point(gate["position_enu_m"])) < 0.001
            blocker, path, entry = site_entry(grounds, field, gate)
            if blocker is not None:
                collision.append(blocker)
            pavers.append(path)
            entries.append(entry)
        facades(parts, name, plan, roofs, base, entries)
        if name == "lawrence":
            paths, structures = courtyard(grounds, field, model)
            pavers.extend(paths)
            collision.extend(structures)
        if name == "columbia":
            collision.extend(columbia_extensions(parts, model, field))
            projections["columbia-bridge"] = model["bridge_bounds"]
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        meshes[key] = mesh
        solids.extend([plan, *collision])
        record = {
            "id": key,
            "footprint_enu_m": model["footprint_enu_m"],
            "footprint_holes_enu_m": model.get("footprint_holes_enu_m", []),
            "area_m2": round(plan.area, 2),
            "base_z_m": base,
            "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
            "support_collision_enu_m": [
                list(s.exterior.coords)[:-1] for s in collision
            ],
            "entrances": entries,
        }
        if "name" in model:
            record.update(name=model["name"], campus_id=model["campus_id"])
        records.append(record)
    block = shapely.union_all(solids)
    alias = spec["absorbed_batches"][0]["id"]
    replace = {spec["lawrence"]["id"], alias}
    source = {
        b["id"]: Polygon(b["footprint_enu_m"]).buffer(0) for b in manifest["buildings"]
    }
    old = shapely.union_all([source[k] for k in replace])
    overlap = {
        k: round(block.intersection(p).area, 3)
        for k, p in source.items()
        if k not in replace and block.intersection(p).area > 0.02
    }
    assert not overlap, overlap
    for row in records:
        for gate in row["entrances"]:
            e, n = gate["position_enu_m"]
            angle = np.deg2rad(gate["outward_degrees"])
            reach = gate["approach_distance_m"]
            assert 0 < reach < 5
            point = Point(e + reach * np.sin(angle), n + reach * np.cos(angle))
            assert block.distance(point) >= 0.5, gate["gate"]
    conflicts = []
    for index, (a, b, *_) in enumerate(graph["edges"]):
        edge = LineString([graph["nodes_enu_m"][a], graph["nodes_enu_m"][b]])
        if edge.distance(block) < 0.42 <= edge.distance(old):
            conflicts.append(index)
    assert not conflicts, conflicts
    pavement = tools.approaches(
        [{"outline": list(p.exterior.coords), "rgb": PAVING} for p in pavers],
        field,
        block,
    )
    return (
        records,
        meshes,
        trimesh.util.concatenate([*grounds, pavement]),
        {
            "route_edges": len(graph["edges"]),
            "new_conflicts": conflicts,
            "footprint_m2": {row["id"]: row["area_m2"] for row in records},
            "columbia_bridge_min_ground_clearance_m": round(
                6.14
                - max(
                    geometry.sample_ground(field, e, n)
                    for e, n in list(
                        box(*projections["columbia-bridge"]).exterior.coords
                    )[:-1]
                ),
                3,
            ),
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    records, models, ground, audit = build(
        spec, manifest, json.loads(field_path.read_bytes()), graph
    )
    appearances = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    batch_builder = tools.load_builder("build-frohnmayer-exterior-review.py")
    removals = batch_builder.source_removals(spec, config, appearances)
    out = SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    memorial.gerlinger.export(glb, models, ground, GROUND, "science-approaches")
    descriptor = out / "site.json"
    descriptor.write_text(
        json.dumps(
            {
                "source_presentation_sha256": config["asset_sha256"],
                "source_base_model_sha256": manifest["model"]["sha256"],
                "source_heightfield_sha256": tools.digest(field_path),
                "url": f"{DIRECTORY}/site.glb",
                "sha256": tools.digest(glb),
                "ground_node": GROUND,
                "buildings": records,
                "absorbed_ids": [r["id"] for r in removals],
                "batch_removals": removals,
                "identity_moves": {
                    spec[k]["prior_name_id"]: spec[k]["id"]
                    for k in ("pacific", "columbia")
                },
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf8",
        newline="\n",
    )
    config["lawrence_science_site"] = {
        "url": f"{DIRECTORY}/site.json",
        "sha256": tools.digest(descriptor),
    }
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit.update(
        model_sha256=tools.digest(glb),
        descriptor_sha256=tools.digest(descriptor),
        triangles={k: len(v.faces) for k, v in models.items()}
        | {GROUND: len(ground.faces)},
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
