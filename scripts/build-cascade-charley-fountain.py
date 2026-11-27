# SPDX-License-Identifier: Apache-2.0
"""Build the dry Cascade Charley basin and its original mesh details."""

from importlib import import_module

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

site = import_module("build-east-thirteenth-east").site
CONCRETE = (157, 151, 134)
COPING = (177, 168, 146)
GROUT = (105, 111, 110)


def append_quad(vertices, colors, corners, color):
    for index in (0, 1, 2, 0, 2, 3):
        vertices.append(corners[index])
        colors.append((*color, 255))


def tiles(vertices, colors, origin, across, upward, width, depth, rng, repair=None):
    origin, across, upward = map(np.asarray, (origin, across, upward))
    pitch = 0.077
    for u in np.arange(0, width, pitch):
        for v in np.arange(0, depth, pitch):
            x0, x1 = u + 0.0022, min(u + pitch - 0.0022, width)
            y0, y1 = v + 0.0022, min(v + pitch - 0.0022, depth)
            if x1 <= x0 or y1 <= y0:
                continue
            tint = int(rng.integers(-9, 10))
            base = (126, 128, 118) if repair and repair(u, v) else (48, 83, 124)
            append_quad(
                vertices,
                colors,
                [
                    origin + across * x + upward * y
                    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
                ],
                [channel + tint for channel in base],
            )


def lining(shape, floor, top):
    west, south, east, north = shape.bounds
    width, depth = east - west, north - south
    vertices, color = [], []
    rng = np.random.default_rng(1991)
    tiles(
        vertices,
        color,
        (west, floor + 0.004, -south),
        (1, 0, 0),
        (0, 0, -1),
        width,
        depth,
        rng,
        repair=lambda u, v: (
            2.02 <= u <= 2.55 and v < 1.02 or 2.02 <= u <= 3.08 and v < 0.36
        ),
    )
    for origin, axis, length in [
        ((west, floor, -north + 0.003), (1, 0, 0), width),
        ((east, floor, -south - 0.003), (-1, 0, 0), width),
        ((west + 0.003, floor, -south), (0, 0, -1), depth),
        ((east - 0.003, floor, -north), (0, 0, 1), depth),
    ]:
        tiles(vertices, color, origin, axis, (0, 1, 0), length, top - floor, rng)
    mesh = trimesh.Trimesh(
        vertices, np.arange(len(vertices)).reshape((-1, 3)), process=False
    )
    mesh.visual.vertex_colors = np.asarray(color, dtype=np.uint8)
    return mesh


def stone(row, rng):
    e, n, z, radii = row
    rx, ry, rz = radii
    mesh = trimesh.creation.icosphere(subdivisions=1)
    perturb = rng.uniform(0.75, 1.18, len(mesh.vertices))
    mesh.vertices *= perturb[:, None] * [rx, rz, ry]
    mesh.vertices[:, 1] = np.maximum(mesh.vertices[:, 1], -rz * 0.36)
    mesh.apply_transform(
        trimesh.transformations.rotation_matrix(float(rng.uniform(-2, 2)), [0, 1, 0])
    )
    mesh.apply_translation([e, z - mesh.bounds[0, 1], -n])
    mesh.unmerge_vertices()
    tone = rng.integers(-10, 8, len(mesh.faces)).repeat(3)
    base = [114, 83, 57] if n < 64 else [92, 88, 77]
    mesh.visual.vertex_colors = np.column_stack(
        [tone + base[0], tone + base[1], tone + base[2], np.full(len(tone), 255)]
    )
    return mesh


def build_fountain(spec):
    basin = spec["basin"]
    outer = box(*basin["bounds_enu_m"])
    opening = box(*basin["opening_enu_m"])
    floor, rim = basin["floor_z_m"], basin["rim_z_m"]
    assert outer.contains(opening) and rim - floor > 0.20
    assert outer.area - opening.area > 3.0
    wall, tiles_mesh, stones = [], [], []
    site.solid(wall, opening, floor - 0.35, floor, GROUT)
    coping = outer.difference(opening)
    site.solid(wall, coping, floor - 0.38, rim - 0.067, CONCRETE)
    site.solid(wall, coping, rim - 0.067, rim, COPING)
    tiles_mesh.append(lining(opening, floor, rim - 0.068))

    rear_parts = []
    for index, (bounds, top) in enumerate(spec["rear_panels"]):
        shape = box(*bounds)
        tint = tuple(channel - 9 + (index * 7) % 18 for channel in CONCRETE)
        site.solid(wall, shape, floor - 0.34, top, tint)
        rear_parts.append(shape)

    def parts(key, body, top_color=CONCRETE):
        for bounds, z0, z1 in spec[key]:
            shape = box(*bounds)
            site.solid(body, shape, z0, z1, top_color)
            rear_parts.append(shape)

    parts("cascade_body", wall)
    parts("dark_cap", wall, (114, 81, 71))
    chute = spec["chute"]
    shape = Polygon(chute["outline_enu_m"])
    assert shape.is_valid
    floor_z = chute["bottom_z_m"] + 0.072
    site.solid(wall, shape, chute["bottom_z_m"], floor_z, (133, 123, 103))
    channel = Polygon(chute["channel_enu_m"])
    assert channel.is_valid and 0.12 < shape.intersection(channel).area < shape.area
    site.solid(wall, shape.difference(channel), floor_z, chute["lip_z_m"], COPING)
    rear_parts.append(shape)

    apron = Polygon(spec["rock_apron_enu_m"])
    assert apron.is_valid
    site.solid(stones, apron, 2.41, spec["rock_apron_z_m"], (141, 96, 82))
    apron_parts = [apron]
    rng = np.random.default_rng(5653)
    for row in spec["stones"]:
        e, n, z, (rx, ry, rz) = row
        assert max(rx, ry) < 0.55 and 0.09 < rz < 0.35
        center = Point(e, n)
        assert opening.covers(center) or apron.covers(center)
        mesh = stone(row, rng)
        stones.append(mesh)
        lo, hi = mesh.bounds
        projection = box(lo[0], -hi[2], hi[0], -lo[2])
        if not outer.covers(projection):
            apron_parts.append(projection)

    blockers = [
        outer,
        box(*unary_union(rear_parts).bounds),
        box(*unary_union(apron_parts).bounds),
    ]
    return wall, tiles_mesh, stones, blockers
