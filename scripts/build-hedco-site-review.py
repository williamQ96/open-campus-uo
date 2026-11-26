# SPDX-License-Identifier: Apache-2.0
"""Generate the georeferenced HEDCO exterior and evidence for the local preview."""

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh


def import_builder(filename):
    file = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(file.stem, file)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    return builder


geometry = import_builder("build-cascade-exterior-review.py")
facade_box = import_builder("build-ford-arena-review.py").facade_box
SCENE = geometry.SCENE
SPEC = geometry.ROOT / "data/metadata/hedco-site-review.json"
OUTPUT = SCENE / "hedco-exterior-review"
BRICK = (149, 86, 66)
WOOD = (174, 119, 76)
STONE = (180, 168, 151)
METAL = (114, 125, 126)
GLASS = (53, 81, 93)
ROOF = (116, 96, 83)


def volume(plan, bottom, top, wall, roof=None):
    return geometry.shell(plan, bottom, lambda e, n: top, wall, roof or wall)


def hip(roof):
    west, south, east, north = roof["bounds"]
    eave = roof["eave_z_m"]
    rise = roof["ridge_z_m"] - eave
    corners = [(west, south), (east, south), (east, north), (west, north)]
    if roof["axis"] == "e":
        half = (north - south) / 2
        a, b = (west + half, south + half), (east - half, south + half)
        facets = [
            [corners[0], corners[1], b, a],
            [corners[1], corners[2], b],
            [corners[2], corners[3], a, b],
            [corners[3], corners[0], a],
        ]
    else:
        half = (east - west) / 2
        a, b = roof.get(
            "ridge_enu_m", ((west + half, south + half), (west + half, north - half))
        )
        facets = [
            [corners[0], corners[1], a],
            [corners[1], corners[2], b, a],
            [corners[2], corners[3], b],
            [corners[3], corners[0], a, b],
        ]

    def height(e, n):
        return eave + rise * min(
            (e - west) / (a[0] - west),
            (east - e) / (east - b[0]),
            (n - south) / (a[1] - south),
            (north - n) / (north - b[1]),
        )

    parts = [
        geometry.shell(Polygon(points), eave - 0.19, height, METAL, ROOF)
        for points in facets
    ]
    return parts


def building(spec, outline, field):
    base = spec["footing_z_m"]
    east_eave = next(
        roof["eave_z_m"] for roof in spec["roofs"] if roof["name"] == "east wing"
    )
    north = outline.intersection(box(-710, -415.44, -630, -390))
    east = outline.intersection(box(-658.0, -464.12, -638, -415.44))
    south = outline.intersection(box(-677, -486, -642, -463.7))
    residual = outline.difference(north.union(east).union(south))
    parts = []
    for region, height, trim in [
        (north, 15.76, (166, 174, 170)),
        (east, east_eave, BRICK),
        (south, 20.46, BRICK),
        (residual, 15.76, STONE),
    ]:
        for polygon in geometry.sections(region):
            parts.append(volume(polygon, base, height, BRICK, trim))
    parts.extend(piece for roof in spec["roofs"] for piece in hip(roof))

    def rect(x0, y0, x1, y1, low, high, color):
        parts.append(volume(box(x0, y0, x1, y1), low, high, color))

    def panel(a, b, direction, left, right, inside, outside, bottom, top, color):
        parts.append(
            facade_box(
                np.array(a),
                np.array(b),
                np.array(direction),
                left,
                right,
                inside,
                outside,
                bottom,
                top,
                color,
            )
        )

    # The courtyard elevations use wider wood-clad modules and steel glazing frames.
    inner_faces = [
        ((-680.71, -414.92), (1, 0), (0, -1), 22.95, 15.54, 2),
        ((-657.6, -460.8), (0, 1), (-1, 0), 45.65, east_eave - 0.13, 3),
        ((-680.72, -429.55), (0, 1), (1, 0), 14.48, 15.57, 2),
        ((-671.15, -460.9), (1, 0), (0, 1), 13.1, 20.0, 3),
    ]
    court_ground = 7.93
    for start, along, outward, width, eave, floors in inner_faces:

        def span(a, b, c, d, h, k, color):
            panel(start, along, outward, a, b, c, d, h, k, color)

        span(0.08, width - 0.08, 0.01, 0.075, court_ground + 0.12, eave - 0.14, WOOD)
        pane_count = max(2, int(width / 3.15))
        step = width / pane_count
        for floor in range(floors):
            lower = court_ground + 0.12 + floor * 3.86
            upper = min(eave - 0.22, lower + (3.5 if floor == 0 else 3.27))
            span(0, width, 0.075, 0.20, lower, lower + 0.15, METAL)
            for bay in range(pane_count):
                left = step * bay + 0.3
                right = left + step * (0.79 if floor == 0 else 0.60)
                span(left, right, 0.07, 0.13, lower + 0.19, upper, GLASS)
                for point in (left, (left + right) / 2, right):
                    span(
                        point - 0.025,
                        point + 0.025,
                        0.12,
                        0.17,
                        lower + 0.16,
                        upper,
                        METAL,
                    )
                span(left, right, 0.13, 0.18, lower + 1.73, lower + 1.78, METAL)
                if floor:
                    for z in np.linspace(upper - 0.48, upper - 0.06, 4):
                        span(left - 0.18, right + 0.18, 0.17, 0.57, z, z + 0.035, STONE)
        span(0, width, 0.04, 0.28, eave - 0.16, eave + 0.045, METAL)

    # Brick outer elevations. The tall east elevation has a continuous clerestory above piers.
    outer = [
        ((-641.08, -457.4), (0, 1), (1, 0), 39.25, 3),
        ((-671.98, -479.74), (1, 0), (0, -1), 26.84, 3),
        ((-697.05, -429.3), (0, 1), (-1, 0), 26.4, 2),
        ((-681.8, -398.62), (1, 0), (0, 1), 27.32, 2),
        ((-644.6, -479.4), (0, 1), (1, 0), 20.9, 3),
        ((-672.41, -479.4), (0, 1), (-1, 0), 15.85, 3),
    ]
    for start, along, outward, width, floors in outer:

        def span(a, b, c, d, h, k, color):
            panel(start, along, outward, a, b, c, d, h, k, color)

        for level in range(2):
            low, high = 9.18 + level * 3.86, 11.92 + level * 3.86
            for center in np.linspace(1.6, width - 1.6, max(3, int(width / 2.85))):
                if start[0] == -672.41 and abs(start[1] + center + 471.082) < 1.75:
                    continue
                span(
                    center - 0.53,
                    center + 0.53,
                    0.016,
                    0.079,
                    low - 0.13,
                    high + 0.16,
                    STONE,
                )
                span(center - 0.38, center + 0.38, 0.074, 0.099, low, high, GLASS)
                span(
                    center - 0.40,
                    center + 0.40,
                    0.099,
                    0.143,
                    low + 1.23,
                    low + 1.29,
                    METAL,
                )
        if floors == 3:
            top = east_eave - 0.12 if start[0] == -641.08 else 20.02
            span(0.25, width - 0.25, 0.018, 0.095, 17.08, top, GLASS)
            for x in np.linspace(0.28, width - 0.28, max(4, int(width / 1.22) + 1)):
                span(x - 0.025, x + 0.025, 0.096, 0.148, 17.0, top + 0.03, METAL)
            span(0, width, 0.09, 0.18, 17.02, 17.2, STONE)

    # The east entry is a low two-storey glazed volume at the clock tower.
    for start, along, normal, width in [
        ((-645, -413.85), (0, 1), (1, 0), 11.5),
        ((-653.95, -402.2), (1, 0), (0, 1), 8.9),
    ]:
        for x in np.linspace(0.14, width - 0.12, int(width / 1.42) + 1):
            panel(
                start,
                along,
                normal,
                x - 0.031,
                x + 0.031,
                0.077,
                0.18,
                8.8,
                15.58,
                METAL,
            )
        panel(start, along, normal, 0, width, 0.012, 0.073, 8.85, 15.54, GLASS)
        for y in (9.15, 11.62, 13.78, 15.5):
            panel(start, along, normal, 0, width, 0.073, 0.18, y, y + 0.065, METAL)

    tower = spec["tower_bounds_enu_m"]
    roof = spec["tower_z_m"]
    rect(*tower, base, roof, BRICK)
    x = tower[2]
    n = (tower[1] + tower[3]) / 2
    rect(x - 0.02, n - 1.43, x + 0.065, n + 1.43, roof - 3.08, roof - 0.23, STONE)
    center_z = roof - 1.63
    for angle in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        p = (n + 1.12 * np.sin(angle), center_z + 1.12 * np.cos(angle))
        rect(
            x + 0.064,
            p[0] - 0.028,
            x + 0.094,
            p[0] + 0.028,
            p[1] - 0.068,
            p[1] + 0.068,
            METAL,
        )
    for tip in [(n - 0.63, center_z + 0.31), (n + 0.10, center_z + 0.92)]:
        path = LineString([(n, center_z), tip]).buffer(0.042, cap_style="flat")
        piece = volume(path, x + 0.067, x + 0.110, (47, 50, 49))
        piece.apply_transform(
            [[0, 1, 0, 0], [0, 0, -1, 0], [-1, 0, 0, 0], [0, 0, 0, 1]]
        )
        parts.append(piece)

    for door in spec["entrances"]:
        e, n = door["position_enu_m"]
        eastward = 1 if door["outward_degrees"] == 90 else -1
        half = door["width_m"] / 2
        ground = geometry.sample_ground(field, e + 0.2 * eastward, n)
        for low, high, near, far, color in [
            (ground + 0.045, ground + 2.85, 0.07, 0.126, GLASS),
            (ground + 2.85, ground + 3.02, 0.085, 0.20, METAL),
        ]:
            panel(
                (e, n), (0, 1), (eastward, 0), -half, half, near, far, low, high, color
            )
        for offset in (-half, -half / 2, 0, half / 2, half):
            panel(
                (e, n),
                (0, 1),
                (eastward, 0),
                offset - 0.035,
                offset + 0.035,
                0.12,
                0.205,
                ground + 0.06,
                ground + 2.9,
                METAL,
            )
        panel(
            (e, n),
            (0, 1),
            (eastward, 0),
            -half - 0.48,
            half + 0.48,
            -0.08,
            1.9,
            ground + 3.10,
            ground + 3.34,
            METAL,
        )

    # Skylight bars form the short elevated panel at the north ridge.
    rect(-669.7, -405.75, -664.15, -404.7, 19.31, 19.9, METAL)
    rect(-669.62, -405.70, -664.22, -404.76, 19.87, 19.98, (105, 144, 152))
    for x in np.linspace(-669.56, -664.32, 6):
        rect(x - 0.035, -405.74, x + 0.035, -404.73, 19.89, 20.04, STONE)
    for walk in spec["courtyard"]["covered_walks"]:
        top = walk["top_z_m"]
        rect(*walk["roof"], top - 0.25, top, METAL)
        for e, n in walk["posts"]:
            post_base = geometry.sample_ground(field, e, n) - 0.05
            rect(e - 0.10, n - 0.10, e + 0.10, n + 0.10, post_base, top - 0.17, METAL)
    return trimesh.util.concatenate(parts)


def courtyard(spec, outline, field):
    ground = box(*spec["bounds"]).union(box(*spec["west_paving"])).difference(outline)
    lawn = box(*spec["lawn"])
    garden = box(*spec["south_garden"])
    layers = [
        (ground.difference(lawn.union(garden)), (179, 169, 152)),
        (lawn, (108, 133, 83)),
        (garden, (128, 137, 92)),
    ]
    step = field["spacing_m"]
    e0, n0 = field["min_east_m"], field["min_north_m"]
    a, b, c, d = ground.bounds
    result = []
    for plan, color in layers:
        vertices = []
        for i in range(int((a - e0) / step), int((c - e0) / step) + 1):
            for j in range(int((b - n0) / step), int((d - n0) / step) + 1):
                x, y = e0 + i * step, n0 + j * step
                for tri in [
                    Polygon([(x, y), (x + step, y), (x + step, y + step)]),
                    Polygon([(x, y), (x + step, y + step), (x, y + step)]),
                ]:
                    clipped = plan.intersection(tri)
                    if clipped.area <= 1e-5:
                        continue
                    for region in geometry.sections(clipped):
                        for facet in shapely.constrained_delaunay_triangles(
                            region
                        ).geoms:
                            vertices.extend(
                                (e, geometry.sample_ground(field, e, n) + 0.085, -n)
                                for e, n in list(orient(facet).exterior.coords)[:3]
                            )
        mesh = trimesh.Trimesh(
            vertices, np.arange(len(vertices)).reshape(-1, 3), process=False
        )
        mesh.visual.vertex_colors = [*color, 255]
        result.append(mesh)
    return trimesh.util.concatenate(result)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("audit", type=Path)
    args = ap.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest_path = SCENE / "manifest.json"
    config_path = SCENE / "presentation.json"
    manifest = json.loads(manifest_path.read_bytes())
    config = json.loads(config_path.read_bytes())
    assert (
        digest(manifest_path) == spec["source_manifest_sha256"]
        and config["asset_sha256"] == spec["source_presentation_sha256"]
    )
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    old = Polygon(
        next(r for r in manifest["buildings"] if r["id"] == spec["asset_id"])[
            "footprint_enu_m"
        ]
    )
    outline = Polygon(spec["walls_enu_m"]).union(box(*spec["tower_bounds_enu_m"]))
    assert outline.is_valid and not outline.covers(Point(-669, -431))
    mesh = building(spec, outline, field)
    patch = courtyard(spec["courtyard"], outline, field)
    stage = trimesh.Scene()
    for name, part in [(spec["asset_id"], mesh), ("hedco-courtyard", patch)]:
        stage.add_geometry(part, node_name=name, geom_name=name)

    def mark(tree):
        tree["asset"]["copyright"] = (
            "Open Campus contributors. Original geometry CC BY 4.0."
        )
        tree["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.03, "roughnessFactor": 0.87}}
        ]
        for node in tree["nodes"]:
            if node.get("name") == spec["asset_id"]:
                node["extras"] = {
                    "asset_kind": "building",
                    "asset_id": spec["asset_id"],
                }
            if node.get("name") == "hedco-courtyard":
                node["extras"] = {
                    "asset_kind": "landscape-surface",
                    "surface_layer": "hedco-paving",
                }
        for m in tree["meshes"]:
            m["primitives"][0]["material"] = 0

    OUTPUT.mkdir(exist_ok=True)
    file = OUTPUT / "site.glb"
    file.write_bytes(
        trimesh.exchange.gltf.export_glb(
            stage, include_normals=True, tree_postprocessor=mark
        )
    )
    loaded = trimesh.load(file, force="scene", process=False)
    assert set(loaded.graph.nodes_geometry) == {
        spec["asset_id"],
        "hedco-courtyard",
    } and np.allclose(loaded.bounds, stage.bounds, atol=0.00005)
    nav = json.loads((SCENE / "navigation.json").read_bytes())
    lines = [
        LineString([nav["nodes_enu_m"][a], nav["nodes_enu_m"][b]])
        for a, b, *_ in nav["edges"]
    ]
    supports = [
        box(e - 0.1, n - 0.1, e + 0.1, n + 0.1)
        for walk in spec["courtyard"]["covered_walks"]
        for e, n in walk["posts"]
    ]
    collision_plan = shapely.union_all([outline, *supports])
    collisions = [
        i
        for i, line in enumerate(lines)
        if line.distance(collision_plan) < 0.42 and line.distance(old) >= 0.42
    ]
    assert not collisions, f"HEDCO route conflicts: {collisions}"
    gaps = {}
    for item in spec["entrances"]:
        e, n = item["position_enu_m"]
        face = Point(e, n)
        assert face.distance(outline.boundary) < 0.005
        approach = Point(e + (2.5 if item["outward_degrees"] == 90 else -2.5), n)
        gaps[item["gate"]] = round(outline.distance(approach), 3)
    side = outline.exterior
    rests = [side.interpolate(distance) for distance in np.arange(0, side.length, 0.35)]
    footing = min(
        geometry.sample_ground(field, p.x, p.y) - spec["footing_z_m"] for p in rests
    )
    data = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": digest(field_path),
        "url": "hedco-exterior-review/site.glb",
        "sha256": digest(file),
        "ground_node": "hedco-courtyard",
        "building": {
            "id": spec["asset_id"],
            "footprint_enu_m": list(outline.exterior.coords)[:-1],
            "support_collision_enu_m": [
                list(support.exterior.coords)[:-1] for support in supports
            ],
            "base_z_m": spec["footing_z_m"],
            "roof_z_m": spec["tower_z_m"],
            "entrances": spec["entrances"],
        },
    }
    output = OUTPUT / "site.json"
    output.write_text(
        json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n"
    )
    if entry := config.get("hedco_site_review"):
        assert entry["url"] == "hedco-exterior-review/site.json"
        if entry["sha256"] != digest(output):
            entry["sha256"] = digest(output)
            config_path.write_text(
                json.dumps(config, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
                newline="\n",
            )
    audit = {
        "model_sha256": digest(file),
        "site_sha256": digest(output),
        "building_triangles": len(mesh.faces),
        "courtyard_triangles": len(patch.faces),
        "candidate_area_m2": round(outline.area, 2),
        "former_area_m2": round(old.area, 2),
        "ground_samples": len(rests),
        "route_edges": len(lines),
        "covered_walk_posts": len(supports),
        "minimum_footing_cover_m": round(footing, 3),
        "new_route_conflicts": collisions,
        "approach_gap_m": gaps,
        "bounds_gltf_m": np.round(loaded.bounds, 3).tolist(),
    }
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
