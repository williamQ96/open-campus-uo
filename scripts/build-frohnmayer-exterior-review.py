# SPDX-License-Identifier: Apache-2.0
"""Build the Frohnmayer Music Building exterior and courtyard development review."""

import argparse
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "apps/web-preview/public/scene"
SPEC = ROOT / "data/metadata/frohnmayer-exterior-review.json"
DIRECTORY = "frohnmayer-exterior-review"
OUTPUT = SCENE / DIRECTORY
GROUND = "frohnmayer-approaches"
tools_path = Path(__file__).with_name("build-athletic-exterior-review.py")
tools_spec = spec_from_file_location(tools_path.stem, tools_path)
tools = module_from_spec(tools_spec)
tools_spec.loader.exec_module(tools)
geometry = tools.geometry

BRICK = (157, 98, 81)
SIDING = (188, 179, 160)
DARK = (107, 96, 87)
MATERIALS = {
    "brick": BRICK,
    "siding": SIDING,
    "tar": (125, 112, 105),
    "silver": (183, 179, 167),
    "green": (137, 144, 112),
    "dark": DARK,
}
STONE = (201, 183, 155)
CREAM = (208, 196, 170)
GLASS = (79, 106, 112)
MAROON = (118, 62, 65)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def build_roofs(spec, outline, bottom):
    parts = []
    built = Polygon()
    for zone in spec["roof_zones"]:
        region = outline.intersection(box(*zone["bounds_enu_m"])).difference(built)
        assert region.area > 1, zone["name"]
        top = zone["height_z_m"]
        wall, roof = MATERIALS[zone["wall"]], MATERIALS[zone["roof"]]
        if zone["name"].startswith("Beall"):
            eave, ridge = 20.82, top
            span = [
                (-507.1, -502.4, eave, ridge),
                (-502.4, -495.9, ridge, ridge),
                (-495.9, -490.24, ridge, eave),
            ]
            for lo, hi, h0, h1 in span:
                for piece in geometry.sections(
                    region.intersection(box(-640, lo, -550, hi))
                ):

                    def height(e, n):
                        return h0 + (h1 - h0) * (n - lo) / (hi - lo)

                    parts.append(geometry.shell(piece, bottom, height, wall, roof))
        elif zone["name"].startswith("1921"):
            crest = -604.1
            for left, right in ((-630, crest), (crest, -580)):
                for piece in geometry.sections(
                    region.intersection(box(left, -550, right, -500))
                ):

                    def height(e, n):
                        return top - 0.46 * abs(e - crest)

                    parts.append(geometry.shell(piece, bottom, height, wall, roof))
        else:
            tools.flat(parts, region, bottom, top, wall, roof)
        built = built.union(region)
    remainder = outline.difference(built)
    tools.flat(parts, remainder, bottom, 17.78, BRICK, MATERIALS["silver"])
    assert outline.symmetric_difference(built.union(remainder)).area < 0.01
    return parts, remainder.area


def face_window(add, left, width, low, high, divisions=2):
    add(left - 0.1, left + width + 0.1, 0.015, 0.081, low - 0.10, high + 0.09, STONE)
    add(left, left + width, 0.079, 0.105, low, high, GLASS)
    for u in np.linspace(left, left + width, divisions + 1):
        add(u - 0.034, u + 0.034, 0.092, 0.146, low, high, CREAM)
    add(
        left,
        left + width,
        0.092,
        0.149,
        (low + high) / 2 - 0.035,
        (low + high) / 2 + 0.035,
        CREAM,
    )


def face_panel(e, polygon, color):
    points = []
    for tri in shapely.constrained_delaunay_triangles(polygon).geoms:
        for n, up in list(orient(tri).exterior.coords)[:3]:
            points.append((e, up, -n))
    mesh = trimesh.Trimesh(points, np.arange(len(points)).reshape(-1, 3), process=False)
    if mesh.face_normals[0, 0] > 0:
        mesh.invert()
    mesh.visual.vertex_colors = [*color, 255]
    return mesh


def facade_arch(parts, x, n, foot, width, spring, color):
    radius = width / 2
    half = np.linspace(0, np.pi, 19)
    arc = [(n + radius * np.cos(a), spring + radius * np.sin(a)) for a in half]
    figure = Polygon([(n - radius, foot), (n + radius, foot), *arc])
    ring = figure.buffer(0.14, join_style="mitre").difference(figure)
    parts.append(face_panel(x - 0.028, ring, (172, 113, 94)))
    parts.append(face_panel(x - 0.046, figure, color))


def beall_front(parts, spec, outline, field):
    entry = spec["entrances"][0]
    e, n = entry["position_enu_m"]
    _, add = tools.face(parts, (e, n + 7.1), (e, n - 7.1))
    grade = geometry.sample_ground(field, e - 1.4, n)
    upper = 21.36
    add(0, 14.2, -0.1, 0.40, upper - 0.13, upper + 0.11, STONE)
    add(0.55, 13.65, -0.01, 0.24, grade + 4.3, grade + 4.61, STONE)
    pediment = Polygon([(n - 7.1, upper), (n + 7.1, upper), (n, 24.25)])
    parts.append(face_panel(e - 0.31, pediment, STONE))
    for here, there in ((n - 7.1, n), (n, n + 7.1)):
        za, zb = (upper, 24.25) if here < n else (24.25, upper)
        tools.beam(parts, (e - 0.34, here, za), (e - 0.34, there, zb), 0.23, CREAM)
    _, door_face = tools.face(parts, (e - 0.34, n + 7.1), (e - 0.34, n - 7.1))
    for delta in (-3.3, 0, 3.3):
        facade_arch(parts, e - 0.34, n + delta, grade + 0.18, 2.23, grade + 2.63, DARK)
        left = 7.1 - delta - 0.76
        face_window(door_face, left, 1.52, grade + 0.35, grade + 2.54, divisions=2)
    for start in (2.05, 10.55):
        face_window(add, start, 1.55, grade + 5.47, grade + 7.19, divisions=3)
    add(6.33, 7.87, 0.05, 0.44, grade + 5.25, grade + 8.09, STONE)
    for y in (grade + 5.27, grade + 7.89):
        add(6.2, 8, 0.05, 0.52, y, y + 0.16, CREAM)
    for side in (0.42, 13.3):
        for y in np.arange(grade + 0.2, upper - 0.45, 0.47):
            add(side, side + 0.43, 0.0, 0.22, y, y + 0.29, BRICK)
    court = spec["beall_forecourt"]
    west = e - court["landing_depth_m"]
    half = court["landing_half_width_m"]
    center = court["central_flight_width_m"] / 2
    side = court["side_flight_width_m"]
    solid = outline.buffer(-0.015)
    bottom = min(geometry.sample_ground(field, west - 2.3, n), grade) - 0.35
    landing = box(west, n - half, e, n + half).difference(solid)
    tools.flat(parts, landing, bottom, grade + 0.70, STONE)
    for i in range(4):
        run = (4 - i) * 0.51
        top = grade + 0.08 + i * 0.155
        flights = (
            box(west - run, n - center, west, n + center),
            box(e - side, n - half - run, e, n - half),
            box(e - side, n + half, e, n + half + run),
        )
        for flight in flights:
            tools.flat(parts, flight.difference(solid), bottom, top, STONE)
    for offset in (-half + 0.18, -center - 0.26, center + 0.26, half - 0.18):
        unbroken = LineString([(west + 0.08, n + offset), (e - 0.40, n + offset)])
        tools.flat(parts, unbroken.buffer(0.085, cap_style="flat"), grade + 0.68,
                   grade + 0.79, CREAM)


def recent_facades(parts, spec, outline, field):
    e, n = spec["entrances"][1]["position_enu_m"]
    grade = geometry.sample_ground(field, e, n - 0.8)
    _, add = tools.face(parts, (e - 4.8, n), (e + 4.8, n))
    add(0, 9.6, 0.0, 0.09, 20.07, 20.54, CREAM)
    for u in (1.3, 6.88):
        face_window(add, u, 1.38, grade + 0.78, grade + 2.35)
        face_window(add, u, 1.38, grade + 4.23, grade + 6.1)
    add(3.42, 6.19, 0.0, 0.12, grade, grade + 6.1, STONE)
    _, entry_face = tools.face(parts, (e - 4.8, n - 0.10), (e + 4.8, n - 0.10))
    face_window(entry_face, 4.03, 1.59, grade + 0.10, grade + 2.65)
    face_window(entry_face, 4.03, 1.58, grade + 3.92, grade + 5.89)
    for a, b in zip(
        orient(outline).exterior.coords, list(orient(outline).exterior.coords)[1:]
    ):
        length = np.linalg.norm(np.subtract(a, b))
        west_wall = min(a[0], b[0]) < -609 and max(a[1], b[1]) < -551
        if west_wall and length > 17:
            _, band = tools.face(parts, a, b)
            band(0.04, length - 0.04, 0.00, 0.102, 19.88, 20.57, CREAM)
            for u in np.arange(2.5, length - 2.0, 4.46):
                for floor in (14.84, 17.84):
                    face_window(band, u - 1.20, 2.93, floor, floor + 1.55, divisions=4)
                    along = np.subtract(b, a) / length
                    out = np.array((along[1], -along[0]))
                    v = np.asarray(a) + along * (u - 1.4)
                    w = v + along * 3.33
                    points = [v, w, w + out * 0.83, v + out * 0.83]
                    roof = Polygon(points)
                    base = floor + 1.64
                    for piece in geometry.sections(roof):

                        def slope(x, y):
                            return (
                                base
                                + 0.16
                                + 0.48 * (1 - np.dot(np.array([x, y]) - v, out) / 0.83)
                            )

                        parts.append(geometry.shell(piece, base, slope, MAROON, MAROON))
        historic_west = min(a[0], b[0]) < -609.1 and -544 < min(a[1], b[1]) < -510
        if historic_west and length > 28:
            _, timber = tools.face(parts, a, b)
            for x in np.arange(2.35, length - 1.9, 3.42):
                for y in (14.37, 17.52):
                    face_window(timber, x, 1.65, y, y + 2.02, divisions=3)
                    timber(x - 0.10, x + 1.75, 0.01, 0.32, y + 2.03, y + 2.31, MAROON)
            for z in np.arange(13.65, 20.05, 0.33):
                timber(0.02, length - 0.03, 0.0, 0.021, z, z + 0.032, CREAM)
        rehearsal = min(a[1], b[1]) > -465.65 and length > 8
        if rehearsal:
            _, light = tools.face(parts, a, b)
            face_window(
                light,
                0.34,
                length - 0.68,
                21.27,
                23.55,
                divisions=max(2, round(length / 1.10)),
            )
            light(0.05, length - 0.05, 0.02, 0.22, 24.35, 24.7, DARK)
            if min(a[1], b[1]) > -441.7:
                start = length * 0.30
                face_window(light, start, length * 0.47, 15.58, 20.66, divisions=6)
                light(
                    start - 0.15,
                    start + length * 0.47 + 0.15,
                    0.033,
                    0.26,
                    15.31,
                    15.59,
                    DARK,
                )
        academic = (
            min(a[0], b[0]) > -577
            and min(a[1], b[1]) >= -534
            and max(a[1], b[1]) <= -518.78
        )
        if academic and length > 7:
            _, academic_side = tools.face(parts, a, b)
            academic_side(0.01, length - 0.01, 0.03, 0.18, 24.53, 25.07, DARK)
            for x in np.arange(0.8, length - 1.37, 2.36):
                for floor in (18.66, 21.65):
                    face_window(academic_side, x, 1.57, floor, floor + 1.90)
    # Glass monitors visible over the lower garden roof of the east teaching wing.
    for e1, e2, n0 in (
        (-566.5, -555.4, -551.4),
        (-566.5, -555.4, -546.8),
        (-566.5, -555.4, -537.0),
        (-567, -555.5, -515.7),
    ):
        stand = box(e1, n0 - 0.5, e2, n0 + 0.5)
        tools.flat(parts, stand.intersection(outline), 17.53, 18.19, STONE, GLASS)


def landscape(outline, field):
    court = Polygon(outline.interiors[0])
    paving = LineString(
        [(-593.9, -541.9), (-587.1, -533.4), (-579.6, -532.3), (-569.2, -527.2)]
    ).buffer(1.50, quad_segs=4)
    across = LineString(
        [(-596.4, -533.6), (-589.5, -526.5), (-584.1, -518.2), (-582.9, -510.6)]
    ).buffer(1.44, quad_segs=4)
    paths = paving.union(across).intersection(court)
    ground = tools.approaches(
        [{"outline": list(court.exterior.coords), "rgb": [126, 142, 101]}], field, paths
    )
    ground_path = tools.approaches(
        [
            {"outline": list(p.exterior.coords), "rgb": [170, 159, 140]}
            for p in geometry.sections(paths)
        ],
        field,
        outline,
    )
    approach_entries = [
        {
            "outline": [
                [-624.0, -504.7],
                [-611.9, -504.9],
                [-611.8, -493.7],
                [-623.2, -493.8],
            ],
            "rgb": [164, 155, 141],
        },
        {
            "outline": [
                [-608.0, -597.7],
                [-598.4, -597.7],
                [-598.5, -588.9],
                [-607.9, -588.9],
            ],
            "rgb": [164, 155, 141],
        },
    ]
    approaches = tools.approaches(approach_entries, field, outline)
    ground = trimesh.util.concatenate((ground, ground_path, approaches))
    ground.apply_translation((0, 0.035, 0))
    return ground, paths.area


def source_removals(spec, config, appearances):
    path = SCENE / config["asset_url"]
    source = trimesh.load(path, force="scene", process=False)
    records = {row["id"]: row for row in appearances["appearance_plan"]}
    removals = []
    for item in spec["absorbed_batches"]:
        id, target = item["id"], item["target"]
        transform, mesh_name = source.graph[target]
        assert np.array_equal(transform, np.eye(4))
        mesh = source.geometry[mesh_name]
        members = appearances["context_batches"][target]
        plan = Polygon(records[id]["footprint_enu_m"]).buffer(0.29)
        assert id in members
        assert not any(
            plan.intersects(Polygon(records[peer]["footprint_enu_m"]))
            for peer in members
            if peer != id
        )
        corners = mesh.triangles
        contains = shapely.intersects_xy(plan, corners[:, :, 0], -corners[:, :, 2])
        matches = np.flatnonzero(contains.all(axis=1))
        assert len(matches) and np.array_equal(
            matches, np.arange(matches[0], matches[-1] + 1)
        )
        body = corners[matches]
        anchors = [
            [i, np.round(body[i // 3, i % 3], 6).tolist()]
            for i in (0, len(body) * 3 // 2, len(body) * 3 - 1)
        ]
        removals.append(
            {
                **item,
                "triangles": [int(matches[0]), int(matches[-1] + 1)],
                "source_triangle_count": len(mesh.faces),
                "source_vertices": anchors,
            }
        )
    return removals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    manifest_path = SCENE / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    assert digest(manifest_path) == spec["sources"]["scene_manifest_sha256"]
    assert (
        digest(SCENE / config["asset_url"])
        == config["asset_sha256"]
        == spec["source_presentation_sha256"]
    )
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    outline = Polygon(spec["outer_enu_m"], [spec["courtyard_enu_m"]])
    assert outline.is_valid and len(outline.interiors) == 1
    sample = [
        geometry.sample_ground(field, *ring.interpolate(d).coords[0])
        for ring in (outline.exterior, *outline.interiors)
        for d in np.arange(0, ring.length, 0.42)
    ]
    footing = round(min(sample) - 0.39, 3)
    target = spec["id"]
    absorbed = [item["id"] for item in spec["absorbed_batches"]]
    prior = {
        r["id"]: Polygon(r["footprint_enu_m"]).buffer(0) for r in manifest["buildings"]
    }
    assert not any(
        outline.intersection(plan).area > 0.02
        for id, plan in prior.items()
        if id not in (target, *absorbed)
    )
    for gate in spec["entrances"]:
        assert outline.boundary.distance(Point(gate["position_enu_m"])) < 0.002
    parts, residual = build_roofs(spec, outline, footing)
    beall_front(parts, spec, outline, field)
    recent_facades(parts, spec, outline, field)
    building = trimesh.util.concatenate(parts)
    building.update_faces(building.nondegenerate_faces(height=0.00005))
    ground, paths = landscape(outline, field)
    stage = trimesh.Scene()
    for key, mesh in ((target, building), (GROUND, ground)):
        colors = mesh.visual.vertex_colors.copy()
        srgb = colors[:, :3].astype(float) / 255
        linear = np.where(
            srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4
        )
        colors[:, :3] = np.round(linear * 255).astype(np.uint8)
        mesh.visual.vertex_colors = colors
        stage.add_geometry(mesh, node_name=key, geom_name=key)

    def mark(tree):
        tree["asset"]["copyright"] = (
            "Open Campus contributors. Original geometry CC BY 4.0."
        )
        tree["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.03, "roughnessFactor": 0.87}}
        ]
        for node in tree["nodes"]:
            if node.get("name") == target:
                node["extras"] = {"asset_kind": "building", "asset_id": target}
            elif node.get("name") == GROUND:
                node["extras"] = {
                    "asset_kind": "landscape-surface",
                    "surface_layer": "music-paving",
                }
        for mesh in tree["meshes"]:
            mesh["primitives"][0]["material"] = 0

    OUTPUT.mkdir(exist_ok=True)
    glb = OUTPUT / "site.glb"
    glb.write_bytes(
        trimesh.exchange.gltf.export_glb(
            stage, include_normals=True, tree_postprocessor=mark
        )
    )
    exported = trimesh.load(glb, force="scene", process=False)
    assert np.allclose(stage.bounds, exported.bounds, atol=0.00006)
    assert set(exported.graph.nodes_geometry) == {target, GROUND}
    appearance = json.loads(
        (ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    replacements = source_removals(spec, config, appearance)
    site = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": digest(field_path),
        "url": f"{DIRECTORY}/site.glb",
        "sha256": digest(glb),
        "ground_node": GROUND,
        "absorbed_ids": absorbed,
        "batch_removals": replacements,
        "building": {
            "id": target,
            "footprint_enu_m": spec["outer_enu_m"],
            "footprint_holes_enu_m": [spec["courtyard_enu_m"]],
            "area_m2": round(outline.area, 2),
            "base_z_m": footing,
            "roof_z_m": round(float(building.bounds[1, 1]), 4),
            "entrances": spec["entrances"],
        },
    }
    site_path = OUTPUT / "site.json"
    site_path.write_text(
        json.dumps(site, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n"
    )
    config["frohnmayer_site"] = {
        "url": f"{DIRECTORY}/site.json",
        "sha256": digest(site_path),
    }
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    old = shapely.union_all([prior[id] for id in (target, *absorbed)])
    conflicts = []
    for i, (a, b, *_) in enumerate(graph["edges"]):
        line = LineString([graph["nodes_enu_m"][a], graph["nodes_enu_m"][b]])
        if line.distance(outline) < 0.42 and line.distance(old) >= 0.42:
            conflicts.append(i)
    audit = {
        "footprint_m2": round(outline.area, 2),
        "courtyard_m2": round(Polygon(outline.interiors[0]).area, 2),
        "courtyard_paths_m2": round(paths, 2),
        "old_overlap_with_courtyard_m2": round(
            Polygon(outline.interiors[0]).intersection(old).area, 2
        ),
        "roof_zone_count": len(spec["roof_zones"]),
        "fallback_roof_m2": round(residual, 2),
        "building_triangles": len(building.faces),
        "ground_triangles": len(ground.faces),
        "base_z_m": footing,
        "footing_samples": len(sample),
        "minimum_footing_cover_m": round(min(sample) - footing, 3),
        "route_edges": len(graph["edges"]),
        "new_route_conflicts": conflicts,
        "omitted_triangle_counts": {
            r["id"]: r["triangles"][1] - r["triangles"][0] for r in replacements
        },
        "asset_sha256": digest(glb),
        "site_sha256": digest(site_path),
    }
    assert not conflicts and audit["minimum_footing_cover_m"] > 0
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
