# SPDX-License-Identifier: Apache-2.0
"""Build the two registered residential exteriors on the Women's Memorial Quad."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-gerlinger-site-review.py")
module_spec = spec_from_file_location(source.stem, source)
gerlinger = module_from_spec(module_spec)
module_spec.loader.exec_module(gerlinger)
tools = gerlinger.tools
museum = gerlinger.museum
geometry = gerlinger.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/womens-quad-site-review.json"
DIRECTORY = "womens-quad-review"
GROUND = "womens-quad-approaches"
GROUND_LAYER = "womens-quad-paving"

BRICK = (143, 84, 71)
BRICK_ARCH = (128, 73, 63)
SLATE = (114, 113, 108)
CREAM = (190, 182, 146)
CAST = (169, 160, 140)
PAVEMENT = (155, 152, 138)
GLASS = (58, 77, 78)
IRON = (69, 71, 62)
AWNING = (65, 112, 95)
WALL = gerlinger.surface
PRISM = gerlinger.prism


def span(axis, lo, hi, begin, end):
    return box(begin, lo, end, hi) if axis == "north" else box(lo, begin, hi, end)


def section_roof(parts, region, style, base):
    axis = style["axis"]
    profile = style["profile"]
    for (lo, bottom), (hi, top) in zip(profile, profile[1:]):
        patch = region.intersection(span(axis, lo, hi, -1000, 1000))

        def height(e, n):
            value = n if axis == "north" else e
            return bottom + (top - bottom) * (value - lo) / (hi - lo)

        WALL(parts, patch, base, height, BRICK, SLATE)


def dormers(parts, style):
    axis = style["axis"]
    cross, heights = zip(*style["profile"])
    for sign, centers in zip((-1, 1), style["dormers"]):
        outer = cross[0] + 0.94 if sign < 0 else cross[-1] - 0.94
        inner = outer - sign * 2.42
        roof = float(np.interp(inner, cross, heights)) + 0.24
        for i, position in enumerate(centers):
            width = 1.42 if i % 3 else 1.21
            near, far = sorted((outer, inner))
            local = span(axis, near, far, position - width / 2, position + width / 2)

            def cap(e, n):
                q = n if axis == "north" else e
                return roof - 0.16 + 0.34 * abs(q - outer) / (far - near)

            WALL(
                parts,
                local,
                float(np.interp(outer, cross, heights)) - 0.24,
                cap,
                CREAM,
                SLATE,
            )
            left, right = position - sign * width / 2, position + sign * width / 2
            if axis == "north":
                start, end = (right, outer), (left, outer)
            else:
                start, end = (outer, left), (outer, right)
            _, face = tools.face(parts, start, end)
            sill = roof - 1.33
            gerlinger.sash(
                face, width / 2, width - 0.32, sill, roof - 0.29, columns=3, rows=3
            )


def roofing(parts, plan, model, base):
    rest = plan
    for section in model["roof_sections"]:
        covered = rest.intersection(box(*section["bounds"]))
        assert covered.area > 10, section["name"]
        section_roof(parts, covered, section, base)
        dormers(parts, section)
        rest = rest.difference(covered)
    assert rest.area < 1.0
    PRISM(parts, rest, base, model["wall_eave_z_m"], BRICK, SLATE)


def parapet(parts, item, eave):
    facing, end = item["face"], item["end"]
    a, b = item["cross"]
    middle = (a + b) / 2
    left, right = a + 0.27 * (b - a), b - 0.27 * (b - a)
    top = item["peak_z_m"]
    axis = 2 if facing == "north" else 0
    normal = -1 if facing in ("north", "west") else 1
    at = end + normal * (0.042 if axis == 0 else -0.042)
    shape = Polygon(
        [
            (a, eave - 0.33),
            (a, eave + 0.29),
            (left - 0.29, top - 0.94),
            (left, top),
            (right, top),
            (right + 0.29, top - 0.94),
            (b, eave + 0.29),
            (b, eave - 0.33),
        ]
    )
    offset = normal * (1 if axis == 0 else -1)
    near, far = sorted((at, at - offset * 0.23))
    wall = geometry.shell(shape, near, lambda e, n: far, BRICK, BRICK)
    # The shell depth maps to east or north. Its two faces remain visible from the roof.
    rotate = (
        [[0, 1, 0, 0], [0, 0, -1, 0], [-1, 0, 0, 0], [0, 0, 0, 1]]
        if axis == 0
        else [[1, 0, 0, 0], [0, 0, -1, 0], [0, -1, 0, 0], [0, 0, 0, 1]]
    )
    wall.apply_transform(rotate)
    parts.append(wall)
    if axis == 0:
        start, finish = (end, a), (end, b)
        if facing == "west":
            start, finish = finish, start
    else:
        start, finish = (b, end), (a, end)
    width, face = tools.face(parts, start, finish)
    face(0.25 * width, 0.75 * width, 0.005, 0.21, top - 0.075, top + 0.12, CAST)
    for d in (-0.123, 0.123):
        u = (0.5 + d) * width
        face(u - 0.37, u + 0.37, 0.049, 0.096, top - 0.53, top - 0.19, CAST)
        for t in np.linspace(u - 0.30, u + 0.30, 6):
            face(t - 0.019, t + 0.019, 0.097, 0.15, top - 0.49, top - 0.24, IRON)
    z = (eave + top) / 2 - 0.24
    circle = Point(middle, z)
    museum.arch_panel(
        parts,
        circle.buffer(0.40, quad_segs=6),
        at + offset * 0.018,
        axis,
        normal,
        BRICK_ARCH,
    )
    museum.arch_panel(
        parts, circle.buffer(0.26, quad_segs=6), at + offset * 0.032, axis, normal, IRON
    )
    if item.get("rail_z_m"):
        rail_z = item["rail_z_m"]
        for level in (rail_z - 0.14, rail_z + 0.77):
            face(width * 0.23, width * 0.77, 0.74, 0.81, level, level + 0.085, IRON)
        face(width * 0.23, width * 0.77, 0.02, 0.81, rail_z - 0.18, rail_z - 0.09, IRON)
        for u in np.linspace(width * 0.24, width * 0.76, 15):
            face(u - 0.012, u + 0.012, 0.77, 0.81, rail_z - 0.11, rail_z + 0.79, IRON)


def entry_for(segment, model):
    found = [
        gate
        for gate in model["entrances"]
        if segment.distance(Point(gate["position_enu_m"])) < 0.01
    ]
    assert len(found) <= 1
    return found[0] if found else None


def opening(parts, start, end, gate, field):
    e, n = gate["position_enu_m"]
    a, b = np.array(start), np.array(end)
    direction = (b - a) / np.linalg.norm(b - a)
    outward = np.array((direction[1], -direction[0]))
    point = np.array((e, n))
    pos = float(np.linalg.norm(point - a))
    _, face = tools.face(parts, start, end)
    length = 3.0 if gate["gate"] == "susan-west-porch" else 4.6
    grade = float(geometry.sample_ground(field, *(point + outward * length)))
    threshold = grade + (0.27 if "west-porch" in gate["gate"] else 0.46)
    gerlinger.sash(
        face,
        pos,
        gate["width_m"],
        threshold + 0.03,
        threshold + 2.47,
        columns=2,
        rows=4,
    )
    if gate["gate"].startswith("hendricks-"):
        face(
            pos - 1.10,
            pos + 1.10,
            0.017,
            0.24,
            threshold + 2.56,
            threshold + 2.74,
            CREAM,
        )
        for side in (-1, 1):
            u = pos + side * 0.96
            face(u - 0.10, u + 0.10, 0.02, 0.17, threshold, threshold + 2.57, CREAM)
    deck = Polygon(
        [
            point + delta * direction + depth * outward
            for delta, depth in (
                (-1.28, -0.018),
                (1.28, -0.018),
                (1.28, length),
                (-1.28, length),
            )
        ]
    )

    def elevation(ee, nn):
        advance = float((np.array((ee, nn)) - point) @ outward)
        return threshold + (grade + 0.09 - threshold) * advance / length

    WALL(parts, deck, grade - 0.38, elevation, CAST, PAVEMENT)
    supports = []
    if gate["gate"] == "susan-west-porch":
        face(
            pos - 1.55,
            pos + 1.55,
            -0.04,
            1.22,
            threshold + 2.67,
            threshold + 2.96,
            CREAM,
        )
        for side in (-1, 1):
            u = pos + side * 1.21
            face(u - 0.12, u + 0.12, 1.02, 1.24, threshold, threshold + 2.71, CREAM)
            where = point + direction * (side * 1.21) + outward * 1.1
            supports.append(
                box(where[0] - 0.13, where[1] - 0.13, where[0] + 0.13, where[1] + 0.13)
            )
    else:
        for side in (-1, 1):
            p = point + side * 1.23 * direction
            end = p + outward * (length - 0.19)
            tools.beam(
                parts,
                (*p, elevation(*p) + 0.93),
                (*end, elevation(*end) + 0.93),
                0.045,
                IRON,
            )
            for u in np.arange(0.16, length - 0.12, 0.62):
                post = p + u * outward
                z = elevation(*post)
                tools.beam(parts, (*post, z), (*post, z + 0.94), 0.034, IRON)
    paving = Polygon(
        [
            point + delta * direction + depth * outward
            for delta, depth in (
                (-1.9, length - 0.19),
                (1.9, length - 0.19),
                (1.9, length + 2.75),
                (-1.9, length + 2.75),
            )
        ]
    )
    return supports, paving


def elevations(plan, roof_break):
    ring = list(orient(plan).exterior.coords)
    for a, b in zip(ring, ring[1:]):
        if roof_break is not None and min(a[1], b[1]) < roof_break < max(a[1], b[1]):
            weight = (roof_break - a[1]) / (b[1] - a[1])
            point = (a[0] + weight * (b[0] - a[0]), roof_break)
            yield a, point
            yield point, b
        else:
            yield a, b


def facades(parts, model, plan, field):
    base_eave = model["wall_eave_z_m"]
    refectory = -142.24 if model["id"] == "roof-e145c222" else None
    blocks, paving = [], []
    for a, b in elevations(plan, refectory):
        length = float(np.linalg.norm(np.array(b) - a))
        if length < 2.3:
            continue
        width, face = tools.face(parts, a, b)
        low_wing = refectory is not None and (a[1] + b[1]) / 2 >= refectory
        grade = float(geometry.sample_ground(field, *(np.array(a) + b) / 2))
        eave = (10.92 if min(a[1], b[1]) > -133 else 11.40) if low_wing else base_eave
        eave = min(eave, 15.66) if max(a[1], b[1]) >= -148.5 and not low_wing else eave
        lower = max(grade + 1.31, eave - (4.68 if low_wing else 6.75))
        face(0, width, -0.015, 0.135, eave - 0.43, eave - 0.20, CREAM)
        face(0, width, -0.022, 0.071, grade + 0.40, grade + 0.58, CAST)
        for z in np.arange(grade + 0.77, (eave + grade) / 2 - 0.04, 0.39):
            face(0, width, -0.01, 0.041, z, z + 0.05, BRICK_ARCH)
        gate = entry_for(LineString([a, b]), model)
        opening_at = (
            np.linalg.norm(np.array(gate["position_enu_m"]) - a) if gate else None
        )
        elements = max(1, round(width / 2.98))
        awnings = refectory is not None and max(a[1], b[1]) < -169.75
        vector = (np.array(b) - a) / width
        outward = np.array((vector[1], -vector[0]))
        for u in (np.arange(elements) + 0.5) * width / elements:
            if opening_at is None or abs(u - opening_at) >= 1.68:
                gerlinger.sash(face, u, 1.12, lower, lower + 1.62, columns=3, rows=4)
                face(
                    u - 0.7,
                    u + 0.7,
                    0.012,
                    0.114,
                    lower + 1.69,
                    lower + 1.82,
                    BRICK_ARCH,
                )
            if not low_wing:
                gerlinger.sash(
                    face, u, 1.23, eave - 3.05, eave - 1.12, columns=3, rows=4
                )
                if awnings:
                    left = np.array(a) + vector * (u - 0.73)
                    right = np.array(a) + vector * (u + 0.73)
                    canopy = Polygon(
                        [left, right, right + 0.69 * outward, left + 0.69 * outward]
                    )

                    def tilt(e, n):
                        return (
                            eave
                            - 1.06
                            - 0.72 * float((np.array((e, n)) - left) @ outward)
                        )

                    WALL(parts, canopy, eave - 1.61, tilt, AWNING, AWNING)
        if gate:
            supports, path = opening(parts, a, b, gate, field)
            blocks.extend(supports)
            paving.append(path)
    return blocks, paving


def build(spec, field):
    models, footprints, collision, paving, output, aliases = {}, {}, [], [], [], []
    for label in ("susan", "hendricks"):
        item = spec[label]
        key = item["id"]
        plan = Polygon(item["footprint_enu_m"])
        assert plan.is_valid
        base = round(
            min(
                geometry.sample_ground(field, *plan.exterior.interpolate(d).coords[0])
                for d in np.arange(0, plan.exterior.length, 0.37)
            )
            - 0.39,
            3,
        )
        meshes = []
        roofing(meshes, plan, item, base)
        supports, paths = facades(meshes, item, plan, field)
        for part in item["parapets"]:
            parapet(meshes, part, item["wall_eave_z_m"])
        mesh = trimesh.util.concatenate(meshes)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        models[key] = mesh
        footprints[key] = plan
        collision.extend(supports)
        paving.extend(paths)
        aliases.extend(slot["id"] for slot in item.get("absorbed_batches", []))
        for gate in item["entrances"]:
            assert plan.boundary.distance(Point(gate["position_enu_m"])) < 0.001
        output.append(
            {
                "id": key,
                "footprint_enu_m": item["footprint_enu_m"],
                "support_collision_enu_m": [
                    list(p.exterior.coords)[:-1] for p in supports
                ],
                "area_m2": round(plan.area, 2),
                "base_z_m": base,
                "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
                "entrances": item["entrances"],
            }
        )
    blocked = shapely.union_all([*footprints.values(), *collision])
    ground = tools.approaches(
        [{"outline": list(p.exterior.coords), "rgb": (166, 162, 148)} for p in paving],
        field,
        blocked,
    )
    return models, ground, blocked, footprints, output, aliases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    prior = {
        record["id"]: Polygon(record["footprint_enu_m"]).buffer(0)
        for record in manifest["buildings"]
    }
    models, ground, block, outlines, buildings, aliases = build(
        spec, json.loads(field_path.read_bytes())
    )
    covered_ids = {*models, *aliases}
    assert covered_ids <= set(config["replaces_building_ids"])
    intersections = {
        key: block.intersection(plan).area
        for key, plan in prior.items()
        if key not in covered_ids and block.intersection(plan).area > 0.02
    }
    assert not intersections, intersections
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    old = shapely.union_all([prior[key] for key in covered_ids])
    clearance = []
    for i, (a, b, *_) in enumerate(graph["edges"]):
        path = LineString([graph["nodes_enu_m"][a], graph["nodes_enu_m"][b]])
        if path.distance(block) < 0.42 <= path.distance(old):
            clearance.append(i)
    assert not clearance, clearance

    output = SCENE / DIRECTORY
    output.mkdir(exist_ok=True)
    model = output / "site.glb"
    gerlinger.export(model, models, ground, GROUND, GROUND_LAYER)
    appearances = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    batch_geometry = tools.load_builder("build-frohnmayer-exterior-review.py")
    omissions = batch_geometry.source_removals(spec["hendricks"], config, appearances)
    site = output / "site.json"
    descriptor = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": tools.digest(field_path),
        "url": f"{DIRECTORY}/site.glb",
        "sha256": tools.digest(model),
        "ground_node": GROUND,
        "absorbed_ids": aliases,
        "batch_removals": omissions,
        "buildings": buildings,
    }
    site.write_text(
        json.dumps(descriptor, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    config["womens_quad_site"] = {
        "url": f"{DIRECTORY}/site.json",
        "sha256": tools.digest(site),
    }
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    audit = {
        "model_sha256": tools.digest(model),
        "site_sha256": tools.digest(site),
        "footprint_m2": {key: round(p.area, 2) for key, p in outlines.items()},
        "triangles": {key: len(mesh.faces) for key, mesh in models.items()}
        | {GROUND: len(ground.faces)},
        "routed_edges": len(graph["edges"]),
        "new_conflicts": clearance,
        "superseded_triangles": sum(
            item["triangles"][1] - item["triangles"][0] for item in omissions
        ),
        "merged_overlap_m2": {
            key: round(prior[key].intersection(block).area, 2) for key in covered_ids
        },
    }
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
