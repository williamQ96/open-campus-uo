# SPDX-License-Identifier: Apache-2.0
"""Build the local Ford/Arena scene review from pinned massing and DOGAMI evidence."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import shapely
import tifffile
import trimesh
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import split

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "apps/web-preview/public/scene"
FRONTAGE = ROOT / "data/metadata/ford-arena-frontage-review.json"
MODELS = {
    "context-b0066": "ford-alumni",
    "context-b0074": "matthew-knight-arena",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def wall_frame(frontage):
    a, b = np.array(frontage["facade_ends_enu_m"])
    width = float(np.linalg.norm(b - a))
    along = (b - a) / width
    outward = np.array([-along[1], along[0]])
    return a, along, outward, width


def export_mesh(mesh, node, name, path):
    scene = trimesh.Scene()
    scene.add_geometry(mesh, node_name=node, geom_name=name)

    def finish(document):
        document["asset"][
            "copyright"
        ] = "Open Campus contributors. Original model CC BY 4.0."
        document["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.05, "roughnessFactor": 0.85}}
        ]
        document["meshes"][0]["primitives"][0]["material"] = 0

    path.write_bytes(
        trimesh.exchange.gltf.export_glb(
            scene, include_normals=True, tree_postprocessor=finish
        )
    )


def facade_box(
    origin, along, outward, left, right, inside, outside, bottom, top, color
):
    position = (
        origin + along * ((left + right) / 2) + outward * ((inside + outside) / 2)
    )
    transform = np.eye(4)
    transform[:3, 0] = [along[0], 0, -along[1]]
    transform[:3, 2] = [-outward[0], 0, outward[1]]
    transform[:3, 3] = [position[0], (bottom + top) / 2, -position[1]]
    mesh = trimesh.creation.box(
        [right - left, top - bottom, outside - inside], transform
    )
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = [*color, 255]
    return mesh


def frontage_geometry(frontage, ground, footing):
    origin, along, outward, facade_width = wall_frame(frontage)
    center = frontage["door_along_m"]
    width = frontage["door_width_m"]
    anchor = origin + along * center
    threshold = ground(*anchor)
    parts = []

    def box(left, right, inside, outside, bottom, top, color):
        parts.append(
            facade_box(
                origin, along, outward, left, right, inside, outside, bottom, top, color
            )
        )

    vestibule = frontage.get("vestibule_depth_m")
    if vestibule:
        upper = frontage.get("upper_glazing_height_m", 4.55)
        box(0, facade_width, -vestibule, 0, footing, threshold + upper, [151, 156, 154])
        box(
            -0.2,
            facade_width + 0.2,
            -vestibule,
            1.3,
            threshold + 4.55,
            threshold + 5.18,
            [175, 180, 178],
        )
        if upper > 5.18:
            begin, end = 1.1, facade_width - 1.1
            box(
                begin,
                end,
                -0.018,
                0.05,
                threshold + 5.18,
                threshold + upper - 0.32,
                [56, 91, 98],
            )
            for x in np.linspace(begin, end, 12):
                box(
                    x - 0.075,
                    x + 0.075,
                    0.043,
                    0.17,
                    threshold + 5.18,
                    threshold + upper - 0.27,
                    [157, 166, 166],
                )
            for h in np.linspace(5.25, upper - 0.32, 5):
                box(
                    begin,
                    end,
                    0.043,
                    0.14,
                    threshold + h - 0.045,
                    threshold + h + 0.045,
                    [142, 151, 151],
                )
    else:
        box(
            center - width / 2 - 0.65,
            center + width / 2 + 0.65,
            -0.12,
            1.1,
            threshold + 3.32,
            threshold + 3.58,
            [158, 184, 179],
        )

    left, right = center - width / 2, center + width / 2
    box(left, right, -0.04, 0.09, threshold + 0.17, threshold + 3.28, [47, 81, 86])
    leaves = frontage["door_leaf_count"]
    for index, position in enumerate(np.linspace(left, right, leaves + 1)):
        box(
            position - 0.045,
            position + 0.045,
            0.087,
            0.16,
            threshold + 0.10,
            threshold + 3.32,
            [159, 166, 165],
        )
        if index < leaves:
            handle = position + (width / leaves) * (0.77 if index % 2 == 0 else 0.20)
            box(
                handle - 0.035,
                handle + 0.035,
                0.11,
                0.20,
                threshold + 0.85,
                threshold + 1.17,
                [184, 190, 186],
            )
    for height in [0.13, 2.42, 3.28]:
        box(
            left,
            right,
            0.087,
            0.16,
            threshold + height - 0.04,
            threshold + height + 0.04,
            [159, 166, 165],
        )
    return parts, {
        "gate": frontage["gate"],
        "position_enu_m": np.round(anchor, 4).tolist(),
        "outward_degrees": round(float(np.degrees(np.arctan2(*outward))), 3),
        "estimated": True,
    }


def steel_segment(parts, start, end, radius, color):
    mesh = trimesh.creation.cylinder(radius, segment=[start, end], sections=8)
    mesh.visual.vertex_colors = [*color, 255]
    parts.append(mesh)


def stair_rails(parts, flight, outward, tread_levels, detail):
    a, b = np.asarray(flight["top_enu_m"])
    run = flight["run_m"]
    rise = detail["top_above_tread_m"]
    bars = [detail["lower_above_tread_m"], rise]
    stations = np.linspace(
        0.11, run - 0.11, int(np.ceil(run / detail["post_max_spacing_m"])) + 1
    )
    station_treads = (stations / run * len(tread_levels)).astype(int)
    tread_columns = np.linspace(0, 1, len(tread_levels[0]))
    metal = [99, 116, 118]
    strips = []
    for fraction in detail["fractions"]:
        top = a + (b - a) * fraction
        line = [top + offset * outward for offset in stations]
        base = np.array(
            [
                np.interp(fraction, tread_columns, tread_levels[step]) - 0.012
                for step in station_treads
            ]
        )
        coordinates = np.c_[np.asarray(line)[:, 0], base, -np.asarray(line)[:, 1]]
        for p in coordinates:
            steel_segment(parts, p, p + [0, rise, 0], detail["post_radius_m"], metal)
        for height in bars:
            points = coordinates + [0, height, 0]
            for p, q in zip(points, points[1:]):
                steel_segment(parts, p, q, detail["rail_radius_m"], metal)
        strips.append(
            LineString(line).buffer(detail["post_radius_m"], cap_style="flat")
        )
    return strips


def low_wall(parts, a, b, width, height, ground, color):
    a, b = np.asarray(a), np.asarray(b)
    along = (b - a) / np.linalg.norm(b - a)
    normal = np.array([-along[1], along[0]]) * width / 2
    corners = np.array([a - normal, b - normal, b + normal, a + normal])
    bases = np.array([ground(*p) for p in corners])
    bottom = np.c_[corners[:, 0], bases - 0.065, -corners[:, 1]]
    top = bottom + [0, height + 0.065, 0]
    faces = [(4, 5, 6), (4, 6, 7), (2, 1, 0), (3, 2, 0)]
    for i in range(4):
        j = (i + 1) % 4
        faces.extend(((i, j, j + 4), (i, j + 4, i + 4)))
    mesh = trimesh.Trimesh(np.vstack((bottom, top)), faces, process=False)
    trimesh.repair.fix_normals(mesh)
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = [*color, 255]
    parts.append(mesh)
    return Polygon(corners)


def planter(parts, bed, ground, surface):
    outline = Polygon(bed["outline_enu_m"])
    height = bed["wall_height_m"]
    width = 0.18
    edges = list(outline.exterior.coords)
    obstacles = [
        low_wall(parts, a, b, width, height, ground, [154, 151, 141])
        for a, b in zip(edges, edges[1:])
    ]
    inner = outline.buffer(-width / 2)
    surface(inner, height - 0.085, [83, 77, 50])
    # Original stylized ornamental grasses, spaced in the rows visible in the
    # completed-project photos. Their sites and heights are approximate.
    heading = np.deg2rad(bed["row_bearing_deg"])
    along = np.array([np.cos(heading), np.sin(heading)])
    across = np.array([-along[1], along[0]])
    corners = np.asarray(inner.exterior.coords)
    bounds = np.c_[corners @ along, corners @ across]
    planting = inner.buffer(-0.14)
    rng = np.random.default_rng(564)
    vertices, colors = [], []
    for e in np.arange(bounds[:, 0].min() + 0.28, bounds[:, 0].max(), 0.69):
        for n in np.arange(
            bounds[:, 1].min() + 0.28, bounds[:, 1].max(), bed["row_pitch_m"]
        ):
            p = along * e + across * n
            if not planting.covers(Point(p)):
                continue
            h = ground(*p) + height - 0.092
            for angle in np.linspace(0, np.pi * 2, 10, endpoint=False):
                radial = np.array([np.cos(angle), np.sin(angle)])
                tangent = np.array([-radial[1], radial[0]])
                apex = p + radial * rng.uniform(0.16, 0.31)
                low, high = p - tangent * 0.032, p + tangent * 0.032
                vertices.extend(
                    [
                        [low[0], h, -low[1]],
                        [high[0], h, -high[1]],
                        [apex[0], h + rng.uniform(0.30, 0.51), -apex[1]],
                    ]
                )
                tone = int(rng.integers(-10, 11))
                colors.extend([[63 + tone, 94 + tone, 38 + tone, 255]] * 3)
    triangles = np.arange(len(vertices)).reshape(-1, 3)
    backs = triangles[:, ::-1] + len(vertices)
    blades = trimesh.Trimesh(
        vertices + vertices, np.vstack((triangles, backs)), process=False
    )
    blades.visual.vertex_colors = colors + colors
    parts.append(blades)
    return obstacles


def frontage_ground(frontages, ford, details, ground, spacing, grid_origin, output):
    parts = []
    paved_areas = []
    obstacles = {asset_id: [] for asset_id in MODELS}
    # The presentation's inferred lawn and paving sit as much as 7 cm above
    # the sampled ground. Keep the site apron and treads above those layers.
    apron_lift, tread_lift = 0.115, 0.15

    def surface(ring, lift, color):
        vertices = []
        low, high = np.asarray(ring.bounds).reshape(2, 2)
        start = np.floor((low - grid_origin) / spacing).astype(int)
        finish = np.ceil((high - grid_origin) / spacing).astype(int)
        # Clip to the same SW→NE triangles as the visible foundation. This
        # keeps the pavement offset constant when it crosses a grade break.
        for j in range(start[1], finish[1]):
            for i in range(start[0], finish[0]):
                x, n = grid_origin + spacing * np.array([i, j])
                sw, se = (x, n), (x + spacing, n)
                nw, ne = (x, n + spacing), (x + spacing, n + spacing)
                for cell in [Polygon([sw, se, ne]), Polygon([sw, ne, nw])]:
                    trimmed = cell.intersection(ring)
                    if trimmed.area < 1e-8:
                        continue
                    for tri in shapely.constrained_delaunay_triangles(trimmed).geoms:
                        corners = list(orient(tri, sign=1).exterior.coords)[:3]
                        vertices.extend(
                            (x, ground(x, n) + lift, -n) for x, n in corners
                        )
        mesh = trimesh.Trimesh(
            vertices=vertices,
            faces=np.arange(len(vertices)).reshape(-1, 3),
            process=False,
        )
        mesh.visual.vertex_colors = [*color, 255]
        parts.append(mesh)

    def apron(top, outward, depth):
        a, b = np.array(top)
        ring = Polygon([a, b, b + outward * depth, a + outward * depth])
        paved_areas.append(list(ring.exterior.coords)[:-1])
        surface(ring, apron_lift, [158, 156, 147])
        for fraction in (0.33, 0.68):
            offset = outward * depth * fraction
            stripe = LineString([a + offset, b + offset]).buffer(
                0.083, cap_style="flat"
            )
            surface(stripe, apron_lift + 0.004, [132, 133, 127])

    def tread_strip(top, outward, run, count, color):
        a, b = np.array(top)
        width = np.linalg.norm(b - a)
        columns = max(1, int(np.ceil(width)))
        vertices, faces, treads = [], [], []
        previous = None
        for k in range(count):
            start, end = k * run / count, (k + 1) * run / count
            start_line = [
                a + (b - a) * i / columns + outward * start for i in range(columns + 1)
            ]
            end_line = [p + outward * (end - start) for p in start_line]
            first = len(vertices)
            levels = [
                max(ground(*p), ground(*q)) + tread_lift
                for p, q in zip(start_line, end_line)
            ]
            treads.append(levels)
            for line in [start_line, end_line]:
                vertices.extend((p[0], level, -p[1]) for p, level in zip(line, levels))
            for i in range(columns):
                j = first + i
                forward = j + columns + 1
                faces.extend(((j, j + 1, forward + 1), (j, forward + 1, forward)))
                if previous is not None:
                    p = previous + i
                    faces.extend(((p, j, j + 1), (p, j + 1, p + 1)))
            previous = first + columns + 1
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        # Cross sections match the orientation of the plan's frontage segments.
        if np.median(mesh.face_normals[:, 1]) < 0:
            mesh.invert()
        mesh.update_faces(mesh.nondegenerate_faces(height=1e-6))
        mesh.remove_unreferenced_vertices()
        riser = np.abs(mesh.face_normals[:, 1]) < 0.45
        colors = np.tile([*color, 255], (len(mesh.faces), 1))
        colors[riser, :3] -= 27
        mesh.unmerge_vertices()
        mesh.visual.vertex_colors = np.repeat(colors, 3, axis=0)
        parts.append(mesh)
        return treads

    for frontage in frontages:
        origin, along, outward, _ = wall_frame(frontage)
        center, half = frontage["door_along_m"], frontage["door_width_m"] / 2 + 1
        flights = frontage.get("stair_flights", [])
        left, right = center - half, center + half
        if flights:
            stairs = np.concatenate([flight["top_enu_m"] for flight in flights])
            along_stairs = (stairs - origin) @ along
            left = min(left, float(along_stairs.min()) - 1.2)
            right = max(right, float(along_stairs.max()) + 1.2)
        endpoints = [origin + along * left, origin + along * right]
        apron(
            endpoints,
            outward,
            frontage.get("paved_apron_depth_m", frontage["landing_depth_m"]),
        )
        for flight in flights:
            levels = tread_strip(
                flight["top_enu_m"],
                outward,
                flight["run_m"],
                flight["tread_count"],
                [164, 162, 154],
            )
            obstacles["context-b0074"].extend(
                stair_rails(parts, flight, outward, levels, details["handrails"])
            )
    garden = Polygon(ford["garden_enu_m"])
    lawn = garden.buffer(-1.55, join_style="mitre")
    surface(lawn, 0.10, [86, 111, 60])
    surface(garden.difference(lawn), 0.12, [111, 132, 84])
    terrace = Polygon(ford["terrace_enu_m"])
    interior = terrace.buffer(-0.95, join_style="mitre")
    surface(interior, apron_lift, [157, 150, 136])
    surface(terrace.difference(interior), 0.15, [132, 126, 107])
    for bed in details["planters"]:
        obstacles[bed["owner"]].extend(planter(parts, bed, ground, surface))
    accent = details["arena_north_accent"]
    obstacles["context-b0074"].append(
        low_wall(
            parts,
            *accent["ends_enu_m"],
            accent["width_m"],
            accent["height_m"],
            ground,
            [233, 195, 27],
        )
    )
    filename = "frontage-ground.glb"
    export_mesh(
        trimesh.util.concatenate(parts),
        "ford-arena-frontage-ground",
        "frontage-ground",
        output / filename,
    )
    return {
        "url": f"ford-arena-review/{filename}",
        "sha256": sha(output / filename),
        "paved_areas_enu_m": [np.round(ring, 4).tolist() for ring in paved_areas],
    }, obstacles


def wall_solid(ring, bottom, top, color):
    ring = orient(ring, sign=-1)
    vertices = []
    for tri in shapely.constrained_delaunay_triangles(ring).geoms:
        xy = list(orient(tri, sign=1).exterior.coords)[:3]
        vertices.extend((x, top, -n) for x, n in xy)
        vertices.extend((x, bottom, -n) for x, n in reversed(xy))
    for a, b in zip(ring.exterior.coords, list(ring.exterior.coords)[1:]):
        a0, a1 = (a[0], bottom, -a[1]), (a[0], top, -a[1])
        b0, b1 = (b[0], bottom, -b[1]), (b[0], top, -b[1])
        vertices.extend((a0, a1, b1, a0, b1, b0))
    result = trimesh.Trimesh(
        vertices=vertices, faces=np.arange(len(vertices)).reshape(-1, 3), process=False
    )
    result.visual.vertex_colors = [*color, 255]
    return result


def ford_elevations(envelope, east, spec, ground):
    colors = envelope.visual.vertex_colors[envelope.faces[:, 0], :3]
    heights = envelope.vertices[envelope.faces, 1]
    bands = np.all(colors == [66, 111, 115], axis=1)
    fins = (
        np.all(colors == [111, 122, 124], axis=1)
        & (heights.min(axis=1) >= 4.58)
        & (heights.max(axis=1) <= 18.40)
    )
    envelope.update_faces(~(bands | fins))
    envelope.remove_unreferenced_vertices()
    parts = []

    def face(ends):
        a, u, v, w = wall_frame({"facade_ends_enu_m": ends})

        def box(left, right, inside, outside, bottom, top, color):
            parts.append(
                facade_box(a, u, v, left, right, inside, outside, bottom, top, color)
            )

        return a, u, v, w, box

    def glazing(box, left, right, bottom, top, rows, pitch, frame):
        box(left, right, -0.028, 0.08, bottom, top, [40, 73, 82])
        for t in np.linspace(left, right, max(1, round((right - left) / pitch)) + 1):
            box(t - 0.045, t + 0.045, 0.073, 0.16, bottom, top, frame)
        for h in [bottom + 0.04, *rows, top - 0.04]:
            if bottom < h < top:
                box(left, right, 0.078, 0.16, h - 0.038, h + 0.038, frame)

    datum = spec["reference_entry_local_z_m"]
    floors = datum + np.arange(1, 4) * spec["office_interfloor_m"]
    a, u, v, w, box = face(east["facade_ends_enu_m"])
    glass_end = w * 0.48
    glazing(box, 0.82, glass_end, 5.20, 17.59, floors, 1.24, [142, 156, 159])
    # The plaza curtain wall has deeper horizontal bands at the floor lines.
    for y in floors:
        box(0.82, glass_end, 0.09, 0.29, y - 0.115, y + 0.11, [167, 178, 178])
        box(0.82, glass_end, 0.17, 0.30, y - 0.18, y - 0.11, [107, 126, 130])
    for t in np.linspace(1.8, glass_end - 1.4, 7):
        box(t - 0.085, t + 0.085, 0.15, 0.55, 5.18, 17.48, [164, 174, 173])
    for y in floors:
        box(glass_end + 4.8, w - 3.1, -0.02, 0.065, y + 0.61, y + 1.28, [43, 67, 74])
        box(glass_end + 4.8, w - 3.1, 0.065, 0.23, y + 1.22, y + 1.35, [153, 165, 163])
    for x in [glass_end + 0.9, w - 1.1]:
        box(x - 0.28, x + 0.28, -0.02, 0.14, 4.26, 17.67, [154, 165, 163])

    # The two east door banks appear separately in the ground-floor drawing.
    # Only the larger bank is the review's interactive entrance.
    center = spec["east_secondary_door_along_m"]
    z = ground(*(a + u * center))
    glazing(
        box,
        center - 1.46,
        center + 1.46,
        z + 0.13,
        z + 3.16,
        [z + 2.42],
        1.35,
        [137, 148, 148],
    )
    box(center - 1.60, center + 1.60, -0.04, 0.92, z + 3.13, z + 3.29, [153, 168, 163])

    _, _, _, w, box = face(spec["west_screen_ends_enu_m"])
    framed = [134, 148, 150]
    for y in floors:
        glazing(box, 1.1, w - 2.2, y + 0.28, y + 2.95, [y + 2.29], 1.10, framed)
        box(1, w - 1.9, 0.10, 0.53, y + 2.95, y + 3.05, [144, 156, 155])
    for t in np.linspace(0.8, 13.2, 17):
        box(t - 0.067, t + 0.067, 0.09, 0.76, 4.82, 18.19, [119, 136, 137])
    for t in [14.2, 33.6, w - 0.85]:
        box(t - 0.24, t + 0.24, 0.00, 0.43, 4.42, 18.84, [156, 164, 162])

    _, _, _, w, box = face(spec["south_louver_ends_enu_m"])
    glazing(box, 1.04, w * 0.79, 4.34, 11.86, [7.41, 10.11], 1.35, [136, 147, 146])
    for y in np.arange(5.10, 11.74, 0.46):
        box(0.89, w * 0.8, 0.18, 0.96, y - 0.055, y + 0.055, [142, 156, 155])

    _, _, _, w, box = face(spec["north_bay_ends_enu_m"])
    for y in floors:
        glazing(box, 1.55, w * 0.73, y + 0.49, y + 2.61, [], 1.20, [156, 167, 165])
        box(1.45, w * 0.74, 0.07, 0.48, y + 2.6, y + 2.70, [151, 165, 166])
    _, _, _, w, box = face(spec["north_atrium_ends_enu_m"])
    glazing(box, 0.11, w - 0.11, 4.42, 19.76, floors, 1.08, [132, 151, 152])

    vertices = envelope.vertices[
        np.all(envelope.visual.vertex_colors[:, :3] == [86, 136, 133], axis=1)
    ]
    coords = vertices[:, [0, 2]] * [1, -1] - a
    along_roof, across_roof = coords @ u, coords @ v
    roof_y = float(vertices[:, 1].max())
    for t in np.linspace(along_roof.min() + 0.25, along_roof.max() - 0.25, 24):
        parts.append(
            facade_box(
                a,
                u,
                v,
                t - 0.045,
                t + 0.045,
                across_roof.min(),
                across_roof.max(),
                roof_y - 0.026,
                roof_y + 0.065,
                [150, 165, 163],
            )
        )
    return parts


def arena_superstructure(envelope, roof_outline, spec):
    a, b = np.array(spec["practice_cut_enu_m"])
    cut = LineString([a, b])
    pieces = list(split(roof_outline, cut).geoms)
    assert len(pieces) == 2, "The practice-court seam did not split the outline."
    main, practice = sorted(pieces, key=lambda polygon: -polygon.area)

    # Retain the concourse base and its north curtain wall. The older massing
    # shared one upper shell and north glazing recipe with the practice wing.
    colors = envelope.visual.vertex_colors[envelope.faces[:, 0], :3]
    highest = envelope.vertices[envelope.faces, 1].max(axis=1)
    podium = np.all(colors == [169, 174, 173], axis=1)
    podium_roof = np.all(colors == [227, 227, 215], axis=1) & (highest < 22)
    centers = envelope.triangles_center
    old_trim = np.all(colors == [66, 111, 115], axis=1) | np.all(
        colors == [194, 199, 194], axis=1
    )
    wing_trim = old_trim & shapely.contains_xy(
        practice.buffer(0.4), centers[:, 0], -centers[:, 2]
    )
    envelope.update_faces(~(podium | podium_roof | wing_trim))
    envelope.remove_unreferenced_vertices()
    x, y, _ = envelope.vertices.T
    roof = y >= 21.33
    band = np.interp(
        y[roof],
        [21.33, 28.46, 32.76],
        [
            0,
            spec["band_top_tilt_m_per_east_m"],
            spec["upper_roof_cap_tilt_m_per_east_m"],
        ],
    )
    envelope.vertices[roof, 1] += band * (x[roof] - 355)

    parts = [
        wall_solid(main, 7.16, 20.56, [169, 174, 173]),
        wall_solid(main, 20.56, 21.36, [227, 227, 215]),
        wall_solid(practice, 7.16, spec["practice_roof_z_m"], [156, 162, 160]),
        wall_solid(
            practice,
            spec["practice_roof_z_m"],
            spec["practice_roof_z_m"] + 0.32,
            [220, 220, 209],
        ),
    ]
    along = np.array([0.926, 0.378])
    outward = np.array([-along[1], along[0]])
    for center in spec["practice_roof_monitors_enu_m"]:
        roof = spec["practice_roof_z_m"] + 0.32
        parts.append(
            facade_box(
                np.array(center),
                along,
                outward,
                -7.4,
                7.4,
                -2.6,
                2.6,
                roof - 0.025,
                roof + 0.95,
                [136, 148, 146],
            )
        )
        parts.append(
            facade_box(
                np.array(center),
                along,
                outward,
                -7.5,
                7.5,
                -2.7,
                2.7,
                roof + 0.95,
                roof + 1.13,
                [206, 210, 200],
            )
        )
    for ring, training in [(main, False), (practice, True)]:
        edges = list(orient(ring, sign=-1).exterior.coords)
        for a, b in zip(edges, edges[1:]):
            if cut.distance(Point(np.mean([a, b], axis=0))) < 0.3:
                continue
            origin, along, outward, width = wall_frame({"facade_ends_enu_m": [a, b]})
            if width < 5:
                continue
            if not training and outward[1] > -0.48:
                if outward[1] > 0.51 and origin[1] > -65:
                    # Transoms remain inside each faceted panel so that the
                    # existing mullions lead across the curved north facade.
                    for height in (10.36, 12.94, 15.53):
                        parts.append(
                            facade_box(
                                origin,
                                along,
                                outward,
                                0.47,
                                width - 0.47,
                                0.13,
                                0.30,
                                height - 0.04,
                                height + 0.04,
                                [122, 142, 149],
                            )
                        )
                continue
            if not training:
                parts.append(
                    facade_box(
                        origin,
                        along,
                        outward,
                        0.22,
                        width - 0.22,
                        -0.035,
                        0.095,
                        7.3,
                        17.8,
                        [61, 96, 103],
                    )
                )
            top = spec["practice_roof_z_m"] - 0.4 if training else 17.9
            pitch = 1.1 if training else 2.05
            color = [128, 138, 136] if training else [173, 179, 176]
            for t in np.linspace(0.4, width - 0.4, int(width / pitch) + 1):
                parts.append(
                    facade_box(
                        origin,
                        along,
                        outward,
                        t - 0.065,
                        t + 0.065,
                        -0.035,
                        0.16,
                        7.27,
                        top,
                        color,
                    )
                )
    return parts


def export_massing(
    label, asset_id, outline, footing, output, frontages, ground, roof_outline, spec
):
    source = ROOT / f"assets/exterior-refinement/{label}-massing-review-2026-11-23.glb"
    imported = trimesh.load(source, force="scene", process=False)
    assert len(imported.geometry) == 1
    envelope = next(iter(imported.geometry.values()))
    colors = envelope.visual.vertex_attributes["color"].copy()
    envelope.visual = trimesh.visual.ColorVisuals(mesh=envelope, vertex_colors=colors)
    base = float(envelope.bounds[0, 1])
    face_vertices = []
    for a, b in zip(outline.exterior.coords, list(outline.exterior.coords)[1:]):
        a0, a1 = (a[0], footing, -a[1]), (a[0], base + 0.01, -a[1])
        b0, b1 = (b[0], footing, -b[1]), (b[0], base + 0.01, -b[1])
        face_vertices.extend((a0, a1, b1, a0, b1, b0))
    stem = trimesh.Trimesh(
        vertices=face_vertices,
        faces=np.arange(len(face_vertices)).reshape(-1, 3),
        process=False,
    )
    stem.visual.vertex_colors = [162, 156, 143, 255]
    if asset_id == "context-b0074":
        pieces = arena_superstructure(envelope, roof_outline, spec["arena_envelope"])
    else:
        pieces = ford_elevations(envelope, frontages[0], spec["ford_envelope"], ground)
    entrances = []
    for frontage in frontages:
        geometry, entry = frontage_geometry(frontage, ground, footing)
        pieces.extend(geometry)
        entrances.append(entry)
    merged = trimesh.util.concatenate([envelope, stem, *pieces])
    assert np.array_equal(
        merged.visual.vertex_colors[: len(envelope.vertices)],
        envelope.visual.vertex_colors,
    )

    filename = f"{label}-site.glb"
    file = output / filename
    export_mesh(merged, asset_id, label, file)
    return {
        "id": asset_id,
        "url": f"ford-arena-review/{filename}",
        "sha256": sha(file),
        "footprint_enu_m": list(outline.exterior.coords)[:-1],
        "base_z_m": round(base, 3),
        "roof_z_m": round(float(merged.bounds[1, 1]), 3),
        "footing_z_m": round(footing, 3),
        "entrances": entrances,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("terrain", type=Path)
    parser.add_argument("massing_audit", type=Path)
    args = parser.parse_args()
    manifest = read_json(SCENE / "manifest.json")
    presentation_path = SCENE / "presentation.json"
    presentation = read_json(presentation_path)
    height_path = SCENE / manifest["heightfield_url"]
    heightfield = read_json(height_path)
    spacing = heightfield["spacing_m"]
    x0, n0, origin_height = manifest["coordinate_frame"]["origin_projected_m"]
    audit = read_json(args.massing_audit)
    frontage_spec = read_json(FRONTAGE)
    frontages = {
        asset_id: [
            frontage_spec[asset_id],
            *frontage_spec[asset_id].get("other_frontages", []),
        ]
        for asset_id in MODELS
    }
    outlines = {
        asset_id: Polygon(audit[asset_id]["candidate_footprint_enu_m"])
        for asset_id in MODELS
    }
    roof_outlines = outlines.copy()
    for asset_id, front in frontages.items():
        for frontage in front:
            if depth := frontage.get("vestibule_depth_m"):
                start, along, outward, width = wall_frame(frontage)
                end = start + along * width
                extension = Polygon(
                    [start, end, end - outward * depth, start - outward * depth]
                )
                outlines[asset_id] = orient(
                    outlines[asset_id].union(extension), sign=-1
                )
    pair = shapely.union_all(list(outlines.values()))
    assert all(
        outline.is_valid and not outline.exterior.is_ccw
        for outline in outlines.values()
    )

    with tifffile.TiffFile(args.terrain) as source:
        raster = source.asarray()
        grid = source.geotiff_metadata
    assert grid["ProjectedCSTypeGeoKey"] == 3740 and tuple(
        grid["ModelPixelScale"][:2]
    ) == (1, 1)
    raster_west, raster_north = grid["ModelTiepoint"][3:5]
    east = heightfield["min_east_m"] + spacing * np.arange(heightfield["nx"])
    north = heightfield["min_north_m"] + spacing * np.arange(heightfield["ny"])
    # Include at least one unchanged node beyond each side of the transition.
    min_x, min_y, max_x, max_y = pair.buffer(34 + spacing + 0.01).bounds
    ix = np.flatnonzero((east >= min_x) & (east <= max_x))
    iy = np.flatnonzero((north >= min_y) & (north <= max_y))
    e, n = np.meshgrid(east[ix], north[iy])
    distance = shapely.distance(pair, shapely.points(e, n))
    blend = np.clip((34 - distance) / 26, 0, 1)
    blend = blend * blend * (3 - 2 * blend)

    # Sample the four neighboring 1 m pixel centers in the project's ENU frame.
    x = e + x0 - raster_west - 0.5
    y = raster_north - n - n0 - 0.5
    i, j = np.floor(x).astype(int), np.floor(y).astype(int)
    a, b = x - i, y - j
    assert (
        (i >= 0).all()
        and (j >= 0).all()
        and (i + 1 < raster.shape[1]).all()
        and (j + 1 < raster.shape[0]).all()
    )
    neighbors = np.array(
        [raster[j, i], raster[j, i + 1], raster[j + 1, i], raster[j + 1, i + 1]]
    )
    assert (np.isfinite(neighbors) & (neighbors > -100)).all()
    recent = (
        (neighbors[0] * (1 - a) + neighbors[1] * a) * (1 - b)
        + (neighbors[2] * (1 - a) + neighbors[3] * a) * b
    ) * 0.3048 - origin_height
    baseline = np.asarray(heightfield["heights_m"]).reshape(
        heightfield["ny"], heightfield["nx"]
    )[np.ix_(iy, ix)]
    delta = np.round((recent - baseline) * blend, 4)
    assert not (delta[[0, -1], :].any() or delta[:, [0, -1]].any())
    current = baseline + delta

    def ground(east, north):
        u, v = (east - e[0, 0]) / spacing, (north - n[0, 0]) / spacing
        col, row = int(u), int(v)
        a, b = u - col, v - row
        h00, h10 = current[row, col : col + 2]
        h01, h11 = current[row + 1, col : col + 2]
        return (
            h00 + (h10 - h00) * a + (h11 - h10) * b
            if a >= b
            else h00 + (h11 - h01) * a + (h01 - h00) * b
        )

    output = SCENE / "ford-arena-review"
    output.mkdir(exist_ok=True)
    buildings = []
    for asset_id, label in MODELS.items():
        mask = (
            shapely.distance(outlines[asset_id], shapely.points(e, n))
            <= spacing * 2**0.5
        )
        footing = (
            np.floor(
                (
                    min(
                        float(current[mask].min()), audit[asset_id]["bounds_gltf"][0][1]
                    )
                    - 0.25
                )
                * 100
            )
            / 100
        )
        entry = export_massing(
            label,
            asset_id,
            outlines[asset_id],
            footing,
            output,
            frontages[asset_id],
            ground,
            roof_outlines[asset_id],
            frontage_spec,
        )
        assert all(
            outlines[asset_id].boundary.distance(Point(door["position_enu_m"])) < 0.05
            for door in entry["entrances"]
        )
        buildings.append(entry)
    ground_descriptor, obstacles = frontage_ground(
        [item for group in frontages.values() for item in group],
        frontage_spec["ford_envelope"],
        frontage_spec["plaza_detail"],
        ground,
        spacing,
        np.array([heightfield["min_east_m"], heightfield["min_north_m"]]),
        output,
    )
    for entry in buildings:
        entry["collision_extra_enu_m"] = [
            np.round(ring.exterior.coords[:-1], 4).tolist()
            for ring in obstacles[entry["id"]]
        ]
        for door in entry["entrances"]:
            angle = np.deg2rad(door["outward_degrees"])
            approach = np.asarray(door["position_enu_m"]) + 2.5 * np.array(
                [np.sin(angle), np.cos(angle)]
            )
            assert all(
                ring.distance(Point(approach)) > 0.50 for ring in obstacles[entry["id"]]
            )
    navigation = read_json(SCENE / "navigation.json")
    nodes = navigation["nodes_enu_m"]
    obstacles_plus = shapely.union_all(
        [ring for group in obstacles.values() for ring in group]
    )
    path_clearance = min(
        obstacles_plus.distance(LineString([nodes[a], nodes[b]]))
        for a, b, *_ in navigation["edges"]
    )
    assert (
        path_clearance > 0.42
    ), f"Plaza obstacles reach the navigation graph ({path_clearance:.3f} m)."
    config = {
        "source_model_sha256": manifest["model"]["sha256"],
        "source_presentation_sha256": presentation["asset_sha256"],
        "source_landcover_sha256": presentation["landcover_sha256"],
        "source_heightfield_sha256": sha(height_path),
        "source_terrain_sha256": sha(args.terrain),
        "source_massing_audit_sha256": sha(args.massing_audit),
        "source_frontage_sha256": sha(FRONTAGE),
        "grade": {"column": int(ix[0]), "row": int(iy[0]), "deltas_m": delta.tolist()},
        "buildings": buildings,
        "frontage_ground": ground_descriptor,
    }
    site_path = output / "site.json"
    site_path.write_text(
        json.dumps(config, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n"
    )
    if "ford_arena_site" in presentation:
        descriptor = presentation["ford_arena_site"]
        assert descriptor["url"] == site_path.relative_to(SCENE).as_posix()
        digest = sha(site_path)
        if descriptor["sha256"] != digest:
            descriptor["sha256"] = digest
            presentation_path.write_text(
                json.dumps(presentation, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
                newline="\n",
            )
    print(
        f"{np.count_nonzero(delta)} adjusted ground vertices; delta {delta.min():+.3f} to {delta.max():+.3f} m"
    )
    print(
        f"{len(navigation['edges'])} route edges; plaza obstacle clearance {path_clearance:.3f} m"
    )
    for entry in buildings:
        print(entry["id"], entry["footing_z_m"], entry["sha256"])


if __name__ == "__main__":
    main()
