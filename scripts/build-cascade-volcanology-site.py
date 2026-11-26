# SPDX-License-Identifier: Apache-2.0
"""Build the coordinated Cascade, Volcanology and courtyard exterior review."""

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import trimesh


def load_cascade_builder():
    source = Path(__file__).with_name("build-cascade-exterior-review.py")
    spec = importlib.util.spec_from_file_location("cascade_exterior", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cascade = load_cascade_builder()
SCENE = cascade.SCENE
CONFIG = cascade.ROOT / "data/metadata/cascade-volcanology-site.json"
OUTPUT = SCENE / "cascade-volcanology-review"
CASCADE_ID = "roof-f42d2ea3"
VOLCANOLOGY_ID = "roof-399a0551"
BATCH = "context-campus-1-2"
BRICK, SILL, METAL = (141, 82, 59), (185, 171, 146), (110, 111, 100)
ROOF, CREAM, GLASS, AWNING = (
    (188, 181, 161),
    (213, 201, 181),
    (55, 76, 78),
    (48, 117, 108),
)


def solid(plan, bottom, top, color, roof=None):
    return cascade.shell(plan, bottom, lambda e, n: top, color, roof or color)


def steel_bar(start, end, width, color):
    a, b = (np.array((e, z, -n)) for e, n, z in (start, end))
    transform = trimesh.geometry.align_vectors([0, 0, 1], b - a)
    transform[:3, 3] = (a + b) / 2
    piece = trimesh.creation.box([width, width, np.linalg.norm(b - a)], transform)
    piece.unmerge_vertices()
    piece.visual.vertex_colors = [*color, 255]
    return piece


def street_landing(parts, e, n, grade):
    for i in range(3):
        depth = 1.7 - i * 0.34
        parts.append(solid(box(e - 1.14, n - depth, e + 1.14, n), grade - 0.35,
                           grade + (i + 1) * 0.17, SILL))
    for x in (e - 1.06, e + 1.06):
        for y, z in ((n - 1.62, 0.16), (n - 0.94, 0.49), (n - 0.13, 0.49)):
            parts.append(steel_bar((x, y, grade + z), (x, y, grade + z + 0.79),
                                   0.045, (61, 57, 52)))
        for a, b in (
            ((x, n - 1.62, grade + 0.95), (x, n - 0.94, grade + 1.28)),
            ((x, n - 0.94, grade + 1.28), (x, n - 0.13, grade + 1.28)),
        ):
            parts.append(steel_bar(a, b, 0.048, (61, 57, 52)))


def double_hung_sash(rect, left, right, low, high, outward, columns):
    """Lay out a double-hung sash on a face in its local along-wall coordinates."""
    rect(left, right, low, high, GLASS, outward)
    for x in np.linspace(left, right, columns + 1):
        rect(x - 0.016, x + 0.016, low, high, CREAM, outward + 0.022)
    for i, z in enumerate(np.linspace(low, high, 7)):
        width = 0.027 if i == 3 else 0.016
        rect(left, right, z - width, z + width, CREAM, outward + 0.024)


def volcanology(spec, outline, field):
    base = spec["footing_z_m"]
    west, south, east, _ = outline.bounds
    main = outline.intersection(box(-260, 10, -210, 53.4))
    roof, parapet = spec["roof_z_m"], spec["parapet_z_m"]
    parts = [solid(main, base, roof, BRICK, ROOF)]
    parts.extend(
        solid(p, base, spec["bunker_roof_z_m"], BRICK, SILL)
        for p in cascade.sections(outline.difference(main))
    )
    parapet_ring = main.difference(main.buffer(-0.24, join_style="mitre"))
    parts.append(solid(parapet_ring, roof - 0.015, parapet, BRICK, SILL))
    penthouse = unary_union(
        [box(*spec[f"penthouse{part}_bounds_enu_m"]) for part in ("", "_wing")]
    )
    peak = spec["penthouse_roof_z_m"]
    parts.append(solid(penthouse, roof - 0.015, peak - 0.13, CREAM, ROOF))
    parts.append(
        solid(
            penthouse.buffer(0.115, join_style="mitre"), peak - 0.16, peak, METAL, ROOF
        )
    )

    def rect(x0, y0, x1, y1, low, high, color):
        parts.append(solid(box(x0, y0, x1, y1), low, high, color))

    def south_window(center, low, high, width=1.16, awning=False):
        left, right = center - width / 2, center + width / 2
        rect(
            left - 0.10,
            south - 0.085,
            right + 0.10,
            south + 0.015,
            low - 0.09,
            high + 0.12,
            SILL,
        )
        def on_wall(a, b, lower, upper, color, outward):
            rect(a, south - outward, b, south - outward + 0.024, lower, upper, color)

        double_hung_sash(on_wall, left, right, low, high, 0.118, 4)
        if awning:
            plane = box(left - 0.19, south - 0.63, right + 0.19, south + 0.005)
            parts.append(
                cascade.shell(
                    plane,
                    high - 0.22,
                    lambda e, n: high - 0.15 + 0.86 * (n - south + 0.63),
                    AWNING,
                    AWNING,
                )
            )

    for z in (4.95, 9.58, 12.07):
        ring = main.buffer(0.075, join_style="mitre").difference(
            main.buffer(-0.01, join_style="mitre")
        )
        parts.append(solid(ring, z, z + 0.16, SILL))
    for center in (-240.22, -238.40, -233.28, -231.47):
        south_window(center, 5.55, 7.10, awning=True)
        south_window(center, 9.8, 11.40, awning=True)
    x, _ = spec["south_door_enu_m"]
    grade = cascade.sample_ground(field, x, south - 0.55)
    street_landing(parts, x, south, grade)
    rect(x - 0.97, south - 0.156, x + 0.97, south + 0.04, grade + 0.50, 8.5, SILL)
    rect(
        x - 0.65,
        south - 0.203,
        x + 0.65,
        south + 0.01,
        grade + 0.51,
        grade + 2.99,
        GLASS,
    )
    rect(
        x - 0.035,
        south - 0.22,
        x + 0.035,
        south + 0.005,
        grade + 0.51,
        grade + 2.99,
        CREAM,
    )
    for height in (grade + 1.15, grade + 1.79, grade + 2.41, grade + 2.97):
        rect(x - 0.65, south - 0.23, x + 0.65, south, height - 0.028,
             height + 0.028, CREAM)
    for height in (8.12, 8.37):
        rect(x - 1.05, south - 0.29, x + 1.05, south, height, height + 0.11, SILL)
    for corner in (west, east):
        for i, height in enumerate(np.arange(5.13, 12.07, 0.28)):
            half = 0.14 if i % 2 else 0.25
            rect(corner - half, south - 0.032, corner + half, south + 0.015,
                 height, height + 0.21, (152, 93, 72))
    south_window(x, 9.6, 11.85, 1.38)
    pediment = box(x - 1.16, south - 0.18, x + 1.16, south + 0.05)
    for half in (
        pediment.intersection(box(x - 2, south - 1, x, south + 1)),
        pediment.intersection(box(x, south - 1, x + 2, south + 1)),
    ):
        parts.append(
            cascade.shell(
                half, 11.97, lambda e, n: 12.38 - 0.31 * abs(e - x), SILL, SILL
            )
        )
    penthouse_south = spec["penthouse_bounds_enu_m"][1]
    for x in (-240.12, -238.87, -237.61, -234.11, -232.89, -231.65, -230.42):
        rect(
            x - 0.45,
            penthouse_south - 0.052,
            x + 0.45,
            penthouse_south + 0.01,
            13.49,
            15.02,
            GLASS,
        )
        rect(
            x - 0.022,
            penthouse_south - 0.068,
            x + 0.022,
            penthouse_south,
            13.49,
            15.02,
            CREAM,
        )
    for x, direction in ((west, -1), (east, 1)):
        def side_wall(a, b, low, high, color, outward):
            inner, outer = sorted((x + direction * (outward - 0.024), x + direction * outward))
            rect(inner, a, outer, b, low, high, color)

        for n in (21.95, 25.75, 30.85, 35.12, 39.55, 43.92, 48.33):
            for low, high in ((5.76, 7.35), (9.58, 11.35)):
                rect(x - 0.065, n - 0.81, x + 0.065, n + 0.81, low, high + 0.09, SILL)
                double_hung_sash(side_wall, n - 0.65, n + 0.65, low + 0.12,
                                 high - 0.04, 0.09, 4 if low > 8 else 3)
            for side in (1, -1):
                n_edge = n + side * 0.96
                outer, inner = sorted((n_edge, n))
                band_e = x + direction * 0.15
                profile = box(min(x, band_e), outer, max(x, band_e), inner)
                parts.append(cascade.shell(
                    profile, 11.52, lambda e, y: 11.84 - 0.24 * abs(y - n), SILL, SILL
                ))
    return trimesh.util.concatenate(parts)


def bridge(spec, field):
    west, east = spec["west_east_m"], spec["east_east_m"]
    samples = spec["northings_m"]
    heights = spec["deck_z_m"]
    thickness = spec["deck_thickness_m"]
    parts = []
    for n0, n1, h0, h1 in zip(samples, samples[1:], heights, heights[1:]):

        def grade(e, n):
            return h0 + (h1 - h0) * (n - n0) / (n1 - n0)

        # Shell lofts the top on each measured height strip. Shift bottom vertices
        # in the mirror slope to maintain the same deck thickness throughout.
        deck = cascade.shell(
            box(west, n0, east, n1), min(h0, h1) - thickness, grade, SILL, ROOF
        )
        level = min(h0, h1) - thickness
        bottom = np.isclose(deck.vertices[:, 1], level)
        deck.vertices[bottom, 1] = (
            h0 - thickness + (h1 - h0) * (-deck.vertices[bottom, 2] - n0) / (n1 - n0)
        )
        parts.append(deck)
    arch = spec["arch"]
    a, b = arch["clear_south_m"], arch["clear_north_m"]
    c, d = arch["south_north_m"], arch["north_north_m"]
    w, e = arch["west_east_m"], arch["east_east_m"]
    spring = arch["spring_z_m"]
    half = (b - a) / 2
    curved = [
        (a + half * (1 - np.cos(t)), spring + arch["rise_m"] * np.sin(t))
        for t in np.linspace(0, np.pi, 25)
    ]
    hole = Polygon([(a, 0), (b, 0), *curved[::-1]])
    profile = box(
        c, min(cascade.sample_ground(field, w, y) for y in (c, d)) - 0.35, d, 6.62
    ).difference(hole)
    vertical = [[0, 1, 0, 0], [0, 0, -1, 0], [-1, 0, 0, 0], [0, 0, 0, 1]]
    parts.append(solid(profile, w, e, cascade.BRICK).apply_transform(vertical))
    tint = ((153, 99, 76), (128, 81, 65), (144, 91, 71))
    for i in range(25):
        angles = [np.pi * (i + 0.06) / 25, np.pi * (i + 0.94) / 25]
        points = [
            ((a + b) / 2 - (half + radial) * np.cos(t),
             spring + (arch["rise_m"] + radial) * np.sin(t))
            for radial, steps in ((0.0, angles), (0.27, angles[::-1]))
            for t in steps
        ]
        parts.append(solid(Polygon(points), w - 0.061, w + 0.01,
                           tint[i % len(tint)]).apply_transform(vertical))
    parts.append(solid(box(w, c, west + 0.14, d), 6.0, 6.58, cascade.BRICK, SILL))
    for n in (c + 0.34, d - 0.34):
        parts.append(solid(box(w - 0.03, n - 0.33, west + 0.14, n + 0.33),
                           6.56, 7.54, cascade.BRICK))
        parts.append(solid(box(w - 0.07, n - 0.37, west + 0.19, n + 0.37),
                           7.54, 7.64, SILL))
    for n in np.linspace(c + 0.73, d - 0.73, 20):
        parts.append(solid(box(w + 0.15, n - 0.017, w + 0.186, n + 0.017),
                           6.6, 7.46, (59, 58, 53)))
    parts.append(solid(box(w + 0.14, c + 0.65, w + 0.195, d - 0.65),
                       7.45, 7.51, (59, 58, 53)))

    def height(n):
        return float(np.interp(n, samples, heights))

    for x in (west + 0.08, east - 0.08):
        for start, end in zip(samples, samples[1:]):
            parts.append(
                cascade.shell(
                    box(x - 0.042, start, x + 0.042, end),
                    min(height(start), height(end)) + 0.89,
                    lambda e, n: height(n) + 1.01,
                    METAL,
                    METAL,
                )
            )
        for n in np.linspace(samples[0] + 0.23, samples[-1] - 0.25, 37):
            h = height(n)
            wide = 0.095 if abs(n - round(n / 3) * 3) < 0.38 else 0.029
            parts.append(
                solid(
                    box(x - wide, n - wide, x + wide, n + wide),
                    h - 0.03,
                    h + 0.97,
                    METAL,
                )
            )

    supports = [box(w, c, e, a), box(w, b, e, d)]
    return trimesh.util.concatenate(parts), supports


def paving(spec, field, buildings):
    outline = unary_union(
        [Polygon(spec[k]) for k in ("paving_enu_m", "street_paving_enu_m")]
    ).difference(unary_union(buildings))
    step = field["spacing_m"]
    x0, y0 = field["min_east_m"], field["min_north_m"]
    xmin, ymin, xmax, ymax = outline.bounds
    parts = []
    surface = []
    for i in range(int((xmin - x0) / step), int((xmax - x0) / step) + 1):
        for j in range(int((ymin - y0) / step), int((ymax - y0) / step) + 1):
            a, b = x0 + i * step, y0 + j * step
            triangles = [
                [(a, b), (a + step, b), (a + step, b + step)],
                [(a, b), (a + step, b + step), (a, b + step)],
            ]
            for triangle in triangles:
                for region in cascade.sections(outline.intersection(Polygon(triangle))):
                    for face in shapely.constrained_delaunay_triangles(region).geoms:
                        surface.extend(
                            (e, cascade.sample_ground(field, e, n) + 0.045, -n)
                            for e, n in list(orient(face).exterior.coords)[:3]
                        )
    mesh = trimesh.Trimesh(
        surface, np.arange(len(surface)).reshape((-1, 3)), process=False
    )
    mesh.visual.vertex_colors = [162, 153, 141, 255]
    parts.append(mesh)
    for bounds in spec["steps"]:
        region = box(*bounds)
        surface = max(cascade.sample_ground(field, *p) for p in region.exterior.coords)
        parts.append(
            solid(region, surface - 0.32, surface + 0.074, SILL, (182, 170, 150))
        )
    return trimesh.util.concatenate(parts)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("audit", type=Path)
    args = ap.parse_args()
    spec = json.loads(CONFIG.read_bytes())
    manifest_path = SCENE / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    presentation_path = SCENE / "presentation.json"
    presentation = json.loads(presentation_path.read_bytes())
    source = SCENE / presentation["asset_url"]
    assert (
        digest(source)
        == presentation["asset_sha256"]
        == spec["source_presentation_sha256"]
    )
    assert (
        digest(manifest_path) == spec["source_manifest_sha256"]
        and digest(cascade.OUTPUT) == spec["source_cascade_sha256"]
    )
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    audit_scene = trimesh.load(source, force="scene", process=False)
    _, geometry = audit_scene.graph[BATCH]
    mesh = audit_scene.geometry[geometry]
    old = next(b for b in manifest["buildings"] if b["id"] == VOLCANOLOGY_ID)
    old_outline = Polygon(old["footprint_enu_m"])
    centers = mesh.triangles_center
    selected = np.flatnonzero(
        shapely.contains_xy(old_outline.buffer(0.3), centers[:, 0], -centers[:, 2])
    )
    assert (
        np.array_equal(selected, np.arange(1172, 1608))
        and len(mesh.faces) == 4649
        and len(mesh.vertices) == 8909
    )
    volc = spec["volcanology"]
    cascade_spec = json.loads(cascade.SPEC.read_bytes())
    c_outline, v_outline = (
        Polygon(cascade_spec["walls_enu_m"]),
        Polygon(volc["walls_enu_m"]),
    )
    approach = LineString(spec["courtyard"]["approach_enu_m"])
    c_mesh = next(
        iter(
            trimesh.load(cascade.OUTPUT, force="scene", process=False).geometry.values()
        )
    )
    c_mesh.visual = trimesh.visual.ColorVisuals(
        mesh=c_mesh, vertex_colors=c_mesh.visual.vertex_attributes["color"].copy()
    )
    v_mesh = volcanology(volc, v_outline, field)
    elevated, supports = bridge(spec["bridge"], field)
    ground = paving(spec["courtyard"], field, [c_outline, v_outline, *supports])

    route_gap = min(g.distance(approach) for g in [v_outline, c_outline, *supports])
    candidate_route_intersections = [
        b["id"]
        for b in manifest["buildings"]
        if b["id"] not in (CASCADE_ID, VOLCANOLOGY_ID)
        and Polygon(b["footprint_enu_m"]).buffer(0).distance(approach) < 0.42
    ]
    assert (
        old_outline.distance(approach) < 0.42
        and route_gap > 0.42
        and not candidate_route_intersections
    ), (route_gap, candidate_route_intersections)
    old_cascade = next(b for b in manifest["buildings"] if b["id"] == CASCADE_ID)
    previous_collision = unary_union([old_outline, Polygon(old_cascade["footprint_enu_m"])])
    updated_collision = unary_union([c_outline, v_outline, *supports])
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    conflicts = []
    for i, (a, b, *_) in enumerate(graph["edges"]):
        route = LineString([graph["nodes_enu_m"][a], graph["nodes_enu_m"][b]])
        if updated_collision.distance(route) < 0.42 <= previous_collision.distance(route):
            conflicts.append(i)
    assert not conflicts, f"Cascade site route conflicts: {conflicts}"
    scene = trimesh.Scene()
    for name, piece in (
        (CASCADE_ID, c_mesh),
        (VOLCANOLOGY_ID, v_mesh),
        ("cascade-link", elevated),
        ("cascade-courtyard", ground),
    ):
        colors = piece.visual.vertex_colors.copy()
        srgb = colors[:, :3] / 255.0
        linear = np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)
        colors[:, :3] = np.round(linear * 255).astype(np.uint8)
        piece.visual.vertex_colors = colors
        scene.add_geometry(piece, node_name=name, geom_name=name)

    def mark(tree):
        tree["asset"]["copyright"] = (
            "Open Campus contributors. Original model CC BY 4.0."
        )
        tree["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.05, "roughnessFactor": 0.9}}
        ]
        extras = {
            CASCADE_ID: {"asset_kind": "building", "asset_id": CASCADE_ID},
            VOLCANOLOGY_ID: {"asset_kind": "building", "asset_id": VOLCANOLOGY_ID},
            "cascade-link": {"asset_kind": "site-structure"},
            "cascade-courtyard": {
                "asset_kind": "landscape-surface",
                "surface_layer": "courtyard",
            },
        }
        for node in tree["nodes"]:
            if node.get("name") in extras:
                node["extras"] = extras[node["name"]]
        for item in tree["meshes"]:
            item["primitives"][0]["material"] = 0

    OUTPUT.mkdir(exist_ok=True)
    file = OUTPUT / "site.glb"
    file.write_bytes(
        trimesh.exchange.gltf.export_glb(
            scene, include_normals=True, tree_postprocessor=mark
        )
    )
    reimport = trimesh.load(file, force="scene", process=False)
    assert set(reimport.graph.nodes_geometry) == {
        CASCADE_ID,
        VOLCANOLOGY_ID,
        "cascade-link",
        "cascade-courtyard",
    }
    data = {
        "source_presentation_sha256": digest(source),
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": digest(field_path),
        "url": "cascade-volcanology-review/site.glb",
        "sha256": digest(file),
        "volcanology_batch": {
            "name": BATCH,
            "vertex_count": 8909,
            "index_count": 4649 * 3,
            "remove_triangles": [1172, 1608],
        },
        "buildings": [
            {
                "id": CASCADE_ID,
                "footprint_enu_m": cascade_spec["walls_enu_m"],
                "roof_z_m": cascade_spec["tower_peak_z_m"],
                "support_collision_enu_m": [
                    list(p.exterior.coords)[:-1] for p in supports
                ],
                "entrances": [
                    {
                        "position_enu_m": cascade_spec["openings"]["south_door_enu_m"][
                            :2
                        ],
                        "outward_degrees": 180,
                        "gate": "cascade-courtyard",
                    }
                ],
            },
            {
                "id": VOLCANOLOGY_ID,
                "footprint_enu_m": volc["walls_enu_m"],
                "roof_z_m": volc["penthouse_roof_z_m"],
                "entrances": [
                    {
                        "position_enu_m": volc["south_door_enu_m"],
                        "outward_degrees": 180,
                        "gate": "volcanology-south",
                    }
                ],
            },
        ],
    }
    config = OUTPUT / "site.json"
    config.write_text(
        json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n"
    )
    site_digest = digest(config)
    if descriptor := presentation.get("cascade_volcanology_site"):
        assert descriptor["url"] == "cascade-volcanology-review/site.json"
        if descriptor["sha256"] != site_digest:
            descriptor["sha256"] = site_digest
            presentation_path.write_text(
                json.dumps(presentation, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
                newline="\n",
            )
    report = {
        "site_manifest_sha256": digest(config),
        "mesh_sha256": data["sha256"],
        "spec_sha256": digest(CONFIG),
        "asset_triangles": {
            name: len(reimport.geometry[reimport.graph[name][1]].faces)
            for name in reimport.graph.nodes_geometry
        },
        "old_volcanology_plan_area_m2": round(old_outline.area, 3),
        "new_volcanology_plan_area_m2": round(v_outline.area, 3),
        "old_approach_gap_m": round(old_outline.distance(approach), 3),
        "new_approach_gap_m": round(route_gap, 3),
        "route_edges": len(graph["edges"]),
        "new_route_conflicts": conflicts,
        "courtyard_route_enu_m": spec["courtyard"]["approach_enu_m"],
    }
    args.audit.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
