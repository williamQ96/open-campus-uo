# SPDX-License-Identifier: Apache-2.0
"""Rebuild the documented paths and landmarks in Eugene Pioneer Cemetery."""

import argparse
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
import trimesh

landscape = import_module("build-hamilton-dunes-review")
frontage = import_module("build-onyx-university-frontages-review")
fairmount = landscape.fairmount
geometry = landscape.geometry
beam = fairmount.beam
root, scene = fairmount.ROOT, fairmount.SCENE

PACKAGE = "pioneer-cemetery-landscape-review"
GROUND = "pioneer-cemetery-paving"
STAIR = "pioneer-cemetery-east-stairs"
DETAILS = "pioneer-cemetery-monuments"
CANOPY = "pioneer-cemetery-canopy"

GRAVEL = (166, 152, 119)
SHOULDER = (137, 135, 104)
CONCRETE = (179, 170, 148)
STONE = (137, 134, 120)
STONE_DARK = (104, 105, 92)
IRON = (81, 77, 65)
MARBLE = (162, 168, 160)
SOIL = (119, 103, 82)
GLYPHS = {
    **frontage.GLYPHS,
    "B": (
        ((0, 0), (0, 1), (0.77, 1), (0.98, 0.83), (0.71, 0.55), (0, 0.55)),
        ((0.71, 0.55), (1, 0.34), (0.86, 0), (0, 0)),
    ),
    "C": (
        (
            (0.92, 0.92),
            (0.71, 1),
            (0.24, 1),
            (0, 0.77),
            (0, 0.23),
            (0.25, 0),
            (0.75, 0),
            (1, 0.17),
        ),
    ),
    "F": (((0, 0), (0, 1), (1, 1)), ((0, 0.53), (0.82, 0.53))),
    "G": (
        (
            (0.96, 0.86),
            (0.78, 1),
            (0.25, 1),
            (0, 0.77),
            (0, 0.24),
            (0.25, 0),
            (1, 0),
            (1, 0.44),
            (0.58, 0.44),
        ),
    ),
    "K": (((0, 0), (0, 1)), ((1, 1), (0, 0.45), (1, 0))),
    "L": (((0, 1), (0, 0), (1, 0)),),
    "M": (((0, 0), (0, 1), (0.5, 0.43), (1, 1), (1, 0)),),
    "P": (((0, 0), (0, 1), (0.78, 1), (1, 0.80), (0.78, 0.56), (0, 0.56)),),
    "2": (((0, 0.78), (0.20, 1), (0.79, 1), (1, 0.75), (0.86, 0.50), (0, 0), (1, 0)),),
    "7": (((0, 1), (1, 1), (0.32, 0)),),
    "8": (
        (
            (0.82, 0.5),
            (1, 0.70),
            (0.83, 1),
            (0.18, 1),
            (0, 0.70),
            (0.18, 0.5),
            (0.82, 0.5),
            (1, 0.30),
            (0.82, 0),
            (0.18, 0),
            (0, 0.30),
            (0.18, 0.5),
        ),
    ),
    ".": (((0.52, 0), (0.52, 0.085)),),
}


def read(path):
    return json.loads(path.read_bytes())


def pin(path):
    return sha256(path.read_bytes()).hexdigest()


def ground_height(field, e, n):
    return landscape.absolute_grade(field, e, n)


def solid(parts, shape, bottom, top, color):
    parts.append(landscape.cap(shape, bottom, top, color))


def flat_box(parts, e, n, width, depth, bottom, top, color):
    solid(
        parts,
        box(e - width / 2, n - depth / 2, e + width / 2, n + depth / 2),
        bottom,
        top,
        color,
    )


def drape(parts, field, shape, color, lift, cell):
    landscape.top_surface(
        parts, shape, lambda e, n: ground_height(field, e, n) + lift, color, cell=cell
    )


def named_paths(parts, field, spec):
    centerlines = [
        (LineString(row["centerline_enu_m"]), row["width_m"]) for row in spec["roads"]
    ]
    bases = [line.buffer(width / 2, cap_style="flat") for line, width in centerlines]
    paving = unary_union(bases)
    areas = Polygon(spec["parcel"]["outline_enu_m"])
    shoulders = paving.buffer(0.43).difference(paving).intersection(areas)
    drape(parts, field, paving, GRAVEL, 0.082, 2.0)
    drape(parts, field, shoulders, SHOULDER, 0.058, 2.0)
    return paving


def stairs(paved, parts, field, spec):
    center = spec["north_m"]
    stop, start = spec["top_east_m"], spec["bottom_east_m"]
    half = spec["width_m"] / 2
    taper = 0.05
    lower_profile = ground_height(field, start + 0.05, center) + 0.049
    upper_profile = ground_height(field, stop, center) + 0.082
    rise = (upper_profile - lower_profile) / spec["treads"]
    supports = []
    cuts = np.linspace(start, stop, spec["treads"] + 1)
    for i, (a, b) in enumerate(zip(cuts, cuts[1:])):
        land = box(b - 0.008, center - half, a + 0.004, center + half)
        z = max(lower_profile + (i + 1) * rise, ground_height(field, b, center) + taper)
        support = min(ground_height(field, a, center), z) - 0.30
        solid(paved, land, support, z, CONCRETE if i % 3 else (174, 166, 144))
        if i in (0, 3, 7, spec["treads"] - 1):
            supports.append((a, z))
    for e in (start, stop):
        land = box(
            e - 0.72 if e == stop else e,
            center - half,
            e if e == stop else e + 0.75,
            center + half,
        )
        drape(paved, field, land, CONCRETE, 0.10 if e == stop else 0.056, 0.50)
    for sign in (-1, 1):
        north = center + sign * (half - 0.06)
        post_caps = [(e, north, z + spec["rail_height_m"]) for e, z in supports]
        for cap, (_, height) in zip(post_caps, supports):
            beam(parts, (cap[0], cap[1], height - 0.025), cap, 0.025, IRON)
        for a, b in zip(post_caps, post_caps[1:]):
            beam(parts, a, b, 0.029, IRON)
            beam(
                parts, (a[0], a[1], a[2] - 0.30), (b[0], b[1], b[2] - 0.30), 0.017, IRON
            )
    return rise


def walls(parts, field, spans):
    colors = [STONE_DARK, (114, 113, 103), (125, 120, 107), (121, 120, 106)]
    for first, last in spans:
        a, b = np.asarray(first), np.asarray(last)
        vector = b - a
        length = np.linalg.norm(vector)
        unit = vector / length
        for i in range(int(np.ceil(length / 3.0))):
            here = a + unit * i * 3.0
            end = a + unit * min(length, (i + 1) * 3.0)
            ground = ground_height(field, *(0.5 * (here + end)))
            solid(
                parts,
                landscape.rect_on(here, end, 0.36),
                ground - 0.28,
                ground + 0.43,
                colors[(i + 1) % len(colors)],
            )
            for level in (0.10, 0.25, 0.40):
                normal = unit[::-1] * [1, -1] * 0.182
                start, finish = here + normal, end + normal
                beam(
                    parts,
                    (*start, ground + level),
                    (*finish, ground + level),
                    0.013,
                    (80, 81, 72),
                )
            solid(
                parts,
                landscape.rect_on(here, end, 0.397),
                ground + 0.425,
                ground + 0.51,
                (139, 137, 121),
            )


def text_strokes(parts, title, point, glyph_width, height, color):
    step = glyph_width * 1.23
    for i, letter in enumerate(title):
        at = (i - (len(title) - 1) / 2) * step - glyph_width / 2
        if letter == " ":
            continue
        for stroke in GLYPHS[letter]:
            points = [point(at + x * glyph_width, y * height) for x, y in stroke]
            for a, b in zip(points, points[1:]):
                beam(parts, a, b, height * 0.065, color)


def identification_sign(parts, paving, field, info):
    e, n = info["position_enu_m"]
    w, d, h = (info[k] for k in ("width_m", "depth_m", "height_m"))
    z = ground_height(field, e, n)
    bed = Point(e, n).buffer(1.37, quad_segs=10)
    drape(paving, field, bed, SOIL, 0.069, 0.65)
    flat_box(parts, e, n, w + 0.11, d + 0.16, z - 0.12, z + 0.13, STONE_DARK)
    flat_box(parts, e, n, w, d, z + 0.12, z + h - 0.105, STONE)
    flat_box(parts, e, n, w + 0.13, d + 0.18, z + h - 0.105, z + h, CONCRETE)
    face_n = n - d / 2 - 0.027
    flat_box(
        parts, e, face_n, w * 0.705, 0.054, z + 0.205, z + h - 0.218, (196, 189, 168)
    )
    for y in (0.24, 0.48, 0.71):
        for a, b in (
            (e - w / 2 + 0.018, e - w * 0.36),
            (e + w * 0.36, e + w / 2 - 0.018),
        ):
            beam(
                parts,
                (a, n - d / 2 - 0.005, z + y),
                (b, n - d / 2 - 0.005, z + y),
                0.009,
                STONE_DARK,
            )
    for title, base, width, height in (
        ("I.O.O.F.", 0.665, 0.047, 0.059),
        ("EUGENE PIONEER", 0.511, 0.063, 0.093),
        ("CEMETERY", 0.37, 0.076, 0.098),
        ("1872", 0.262, 0.059, 0.065),
    ):
        text_strokes(
            parts,
            title,
            lambda x, y: (e + x, face_n - 0.030, z + base + y),
            width,
            height,
            (58, 62, 56),
        )
    return bed


def cylinder_between(parts, a, b, radius, color, *, sides=11):
    start, end = np.asarray(a), np.asarray(b)
    # The common beam helper emits coordinates in the right GLB axes.
    mesh = trimesh.creation.cylinder(
        radius=radius, segment=[start, end], sections=sides
    )
    mesh.vertices = mesh.vertices[:, [0, 2, 1]] * [1, 1, -1]
    mesh.visual.vertex_colors = np.tile((*color, 255), (len(mesh.vertices), 1))
    parts.append(mesh)


def orb(parts, p, scales, color, subdivisions=1):
    mesh = trimesh.creation.icosphere(subdivisions=subdivisions, radius=1)
    mesh.vertices = mesh.vertices * np.asarray(scales)[[0, 2, 1]] + [p[0], p[2], -p[1]]
    mesh.visual.vertex_colors = np.tile((*color, 255), (len(mesh.vertices), 1))
    parts.append(mesh)


def memorial(parts, field, info):
    e, n = info["position_enu_m"]
    z = ground_height(field, e, n)
    h = info["height_m"]
    for w, y0, y1, shade in (
        (2.64, -0.10, 0.58, STONE_DARK),
        (2.22, 0.57, 0.91, MARBLE),
        (1.86, 0.90, 1.16, (147, 156, 151)),
        (1.61, 1.15, 1.40, MARBLE),
        (1.37, 1.38, 4.56, (151, 159, 152)),
        (1.69, 4.54, 4.80, MARBLE),
        (1.52, 4.79, 5.05, MARBLE),
        (1.12, 5.04, 5.35, (155, 162, 154)),
    ):
        flat_box(parts, e, n, w, w * 0.93, z + y0, z + y1, shade)
    # The historic figure is read at walking distance as part of the monument.
    v = z + 5.34
    for d in (-0.15, 0.15):
        cylinder_between(
            parts,
            (e, n + d, v + 0.061),
            (e + 0.05, n + d * 0.75, v + 0.94),
            0.126,
            MARBLE,
            sides=9,
        )
        orb(parts, (e - 0.08, n + d, v + 0.11), (0.23, 0.115, 0.10), MARBLE)
    orb(parts, (e + 0.03, n, v + 1.26), (0.255, 0.345, 0.49), MARBLE, 2)
    for d in (-0.31, 0.31):
        cylinder_between(
            parts,
            (e + 0.015, n + d, v + 1.47),
            (e - 0.30, n + d * 0.86, v + 1.09),
            0.095,
            MARBLE,
        )
        cylinder_between(
            parts,
            (e - 0.30, n + d * 0.86, v + 1.09),
            (e - 0.39, n + d * 0.50, v + 1.27),
            0.079,
            MARBLE,
        )
    orb(parts, (e - 0.028, n, v + 1.88), (0.184, 0.157, 0.231), MARBLE, 2)
    orb(parts, (e - 0.045, n, z + h - 0.089), (0.216, 0.176, 0.089), MARBLE)


def rose(parts, field, row, index):
    e, n = row["position_enu_m"]
    r = row["radius_m"]
    z = ground_height(field, e, n)
    rng = np.random.default_rng(492 + index)
    foliage = [(76, 107, 63), (93, 119, 77), (115, 134, 83)]
    for i in range(12):
        angle = i * 2.39996
        distance = r * (rng.uniform(0.29, 0.89))
        x, y = e + distance * np.cos(angle), n + distance * np.sin(angle)
        top = z + (r - 0.42 * distance) * rng.uniform(0.84, 1.16)
        cylinder_between(
            parts, (e, n, z + 0.06), (x, y, top - 0.12), 0.018, (99, 101, 64), sides=5
        )
        orb(parts, (x, y, top), (0.255, 0.235, 0.205), foliage[i % 3])
        if i % 3 == 1:
            orb(
                parts,
                (x - 0.035, y, top + 0.17),
                (0.056, 0.05, 0.044),
                row["flower_color"],
            )


def marker(parts, field, row, index):
    e, n = row["position_enu_m"]
    width, depth, height = (row[key] for key in ("width_m", "depth_m", "height_m"))
    z = ground_height(field, e, n)
    stone = ((169, 165, 149), (185, 182, 164), (137, 140, 131), (161, 157, 143))[
        index % 4
    ]
    flat_box(parts, e, n, width * 1.16, depth * 1.1, z - 0.11, z + 0.13, STONE_DARK)
    if row["silhouette"] == "low":
        slab = box(
            e - depth * 0.37, n - width * 0.43, e + depth * 0.37, n + width * 0.43
        )
        tilt = 0.11 / max(depth, 0.19)
        parts.append(
            geometry.shell(
                slab, z + 0.125, lambda x, _: z + height + tilt * (x - e), stone, stone
            )
        )
        return
    _, _, _, _, _, face = fairmount.chapter.setup_face(
        parts, (e, n - width / 2), (e, n + width / 2)
    )
    profile = Polygon(
        [
            (width * x, z + y * height)
            for x, y in (
                (0.08, 0.13),
                (0.92, 0.13),
                (0.92, 0.83),
                (0.79, 0.96),
                (0.50, 1),
                (0.21, 0.96),
                (0.08, 0.83),
            )
        ]
    )
    face(profile, -depth * 0.34, depth * 0.34, stone)


def canopy(parts, field, tree, index):
    e, n = tree["position_enu_m"]
    h = tree["height_m"]
    r = tree["crown_radius_m"]
    z = ground_height(field, e, n)
    phase = index * 2.399963
    bark = (91, 78, 64)
    foliage = ((72, 91, 67), (89, 107, 76), (101, 117, 80), (78, 98, 76))
    if tree["form"] == "rounded":
        cylinder_between(
            parts, (e, n, z - 0.08), (e, n, z + h * 0.73), r * 0.071, bark, sides=8
        )
        for i, height in enumerate((0.69, 0.70, 0.74, 0.77, 0.87)):
            reach = 0.44 * r if i < 4 else 0.075 * r
            x = e + reach * np.cos(phase + i * 1.57)
            y = n + reach * np.sin(phase + i * 1.57)
            cylinder_between(
                parts,
                (e, n, z + h * 0.38),
                (x, y, z + h * height),
                r * 0.036,
                bark,
                sides=6,
            )
            orb(
                parts,
                (x, y, z + h * height),
                (r * 0.66, r * 0.62, h * 0.12),
                foliage[i % 4],
            )
        return
    cylinder_between(
        parts, (e, n, z - 0.11), (e, n, z + h * 0.92), r * 0.091, bark, sides=8
    )
    vertices, faces, colors = [], [], []
    # Broad lower whorls and shorter upper branches give the canopy its taper.
    for i, (low, high, extent) in enumerate(
        (
            (0.31, 0.70, 1),
            (0.44, 0.79, 0.88),
            (0.56, 0.89, 0.71),
            (0.68, 0.96, 0.53),
            (0.80, 1, 0.36),
        )
    ):
        pattern = phase + i * 0.49
        for j in range(10):
            a, b = pattern + j * np.pi / 5, pattern + (j + 1) * np.pi / 5
            x = e + extent * r * np.cos(a) * (0.88 if j % 2 else 1)
            y = n + extent * r * np.sin(a) * (0.88 if j % 2 else 1)
            u = e + extent * r * np.cos(b) * (1 if j % 2 else 0.88)
            v = n + extent * r * np.sin(b) * (1 if j % 2 else 0.88)
            base = len(vertices)
            vertices.extend(
                (
                    (x, z + h * low, -y),
                    (u, z + h * low, -v),
                    (e, z + h * high, -n),
                    (e, z + h * (low - 0.045), -n),
                )
            )
            faces.extend(((base, base + 1, base + 2), (base + 1, base, base + 3)))
            shade = foliage[(i + (index + j) % 3) % 4]
            colors.extend([(*shade, 255)] * 4)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.visual.vertex_colors = np.asarray(colors, dtype=np.uint8)
    parts.append(mesh)


def export(path, *items):
    model = trimesh.Scene()
    for name, parts, kind in items:
        mesh = landscape.ordered_mesh(trimesh.util.concatenate(parts))
        colors = mesh.visual.vertex_colors.copy()
        srgb = colors[:, :3] / 255
        linear = np.where(
            srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4
        )
        colors[:, :3] = (linear * 255).round().astype(np.uint8)
        mesh.visual.vertex_colors = colors
        mesh.metadata.update(asset_id=name, asset_kind=kind)
        if name == GROUND:
            mesh.metadata["surface_layer"] = GROUND
        model.add_geometry(mesh, node_name=name, geom_name=name)

    def style(tree):
        tree["asset"]["copyright"] = (
            "Open Campus contributors. Original geometry CC BY 4.0."
        )
        tree["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.012, "roughnessFactor": 0.93}}
        ]
        for mesh in tree["meshes"]:
            mesh["primitives"][0]["material"] = 0

    path.write_bytes(
        trimesh.exchange.gltf.export_glb(
            model, include_normals=True, tree_postprocessor=style
        )
    )
    return {name: len(obj.faces) for name, obj in model.geometry.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    spec = read(root / f"data/metadata/{PACKAGE}.json")
    manifest = read(scene / "manifest.json")
    config = read(scene / "presentation.json")
    field_path = scene / manifest["heightfield_url"]
    field = read(field_path)
    pinned = spec["pinned_sources"]
    assert (
        config["asset_sha256"],
        manifest["model"]["sha256"],
        pin(field_path),
        pin(scene / "navigation.json"),
    ) == tuple(
        pinned[k] for k in ("presentation", "campus", "heightfield", "navigation")
    )
    nav = read(scene / "navigation.json")
    route = spec["walkable_ground"]
    assert route["anchor_enu_m"] in nav["nodes_enu_m"]
    assert all(
        0.05 < a < 20
        for a in np.linalg.norm(
            np.diff([route["anchor_enu_m"], *route["points_enu_m"]], axis=0), axis=1
        )
    )
    ground, details, treads, trees = [], [], [], []
    site = named_paths(ground, field, spec)
    rise = stairs(treads, details, field, spec["east_stair"])
    walls(details, field, spec["southern_walls"])
    bed = identification_sign(details, ground, field, spec["southeast_sign"])
    memorial(details, field, spec["gar_monument"])
    for i, row in enumerate(spec["heritage_rose_positions"]):
        rose(details, field, row, i)
    for i, row in enumerate(spec["marker_estimates"]):
        marker(details, field, row, i)
        assert site.distance(Point(row["position_enu_m"])) > 0.6
    for i, row in enumerate(spec["canopy_estimates"]):
        canopy(trees, field, row, i)
        assert site.distance(Point(row["position_enu_m"])) >= 1.1
    assert not site.intersects(bed)
    for row in spec["heritage_rose_positions"]:
        assert not site.contains(Point(row["position_enu_m"]))
    args.stage.mkdir(parents=True, exist_ok=True)
    asset = args.stage / "site.glb"
    faces = export(
        asset,
        (GROUND, ground, "landscape-surface"),
        (STAIR, treads, "landscape-surface"),
        (DETAILS, details, "landscape-detail"),
        (CANOPY, trees, "landscape-vegetation"),
    )
    stair = spec["east_stair"]
    rail_boxes = []
    for side in (-1, 1):
        n = stair["north_m"] + side * (stair["width_m"] / 2 - 0.06)
        rail_boxes.append(
            [
                stair["top_east_m"] - 0.01,
                n - 0.037,
                stair["bottom_east_m"] + 0.01,
                n + 0.037,
            ]
        )
    landmarks = [
        box(e - r, n - r, e + r, n + r).bounds
        for e, n, r in (
            (*spec["gar_monument"]["position_enu_m"], 1.30),
            (*spec["southeast_sign"]["position_enu_m"], 0.43),
        )
    ]
    payload = {
        "source_presentation_sha256": pinned["presentation"],
        "source_base_model_sha256": pinned["campus"],
        "source_heightfield_sha256": pinned["heightfield"],
        "source_navigation_sha256": pinned["navigation"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": pin(asset),
        "buildings": [],
        "walkable_ground": route,
        "context_trees": spec["procedural_context_trees_to_remove"],
        "closed_site_boxes_enu_m": [*rail_boxes, *landmarks],
    }
    descriptor = args.stage / "site.json"
    fairmount.write_json(descriptor, payload, compact=True)
    audit = {
        "path_count": len(spec["roads"]),
        "path_area_m2": round(site.area, 2),
        "path_centerline_m": round(
            sum(LineString(x["centerline_enu_m"]).length for x in spec["roads"]), 2
        ),
        "stair_treads": stair["treads"],
        "nominal_rise_m": round(rise, 4),
        "registered_rose_clusters": len(spec["heritage_rose_positions"]),
        "registered_canopy_estimates": len(spec["canopy_estimates"]),
        "aerial_marker_estimates": len(spec["marker_estimates"]),
        "removed_procedural_tree_indices": [
            x["index"] for x in payload["context_trees"]
        ],
        "faces": faces,
        "asset_sha256": pin(asset),
        "descriptor_sha256": pin(descriptor),
    }
    fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
