# SPDX-License-Identifier: Apache-2.0
"""Build the Normal Gate and southern approach within the Dads' Gates site."""

from importlib import import_module

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

site = import_module("build-pioneer-cemetery-landscape-review")
IRON = (55, 59, 54)
GREEN_POST = (44, 83, 63)
CONCRETE = (176, 173, 158)
ASPHALT = (119, 122, 113)


def arbor(parts, field, spec):
    e, n = spec["position_enu_m"]
    half = spec["width_m"] / 2
    depth = spec["depth_m"] / 2
    spring = spec["spring_height_m"]
    rise = spec["arch_rise_m"]
    base = site.ground_height(field, e, n)
    angle = np.deg2rad(spec["angle_degrees"])
    axis = np.array((np.cos(angle), np.sin(angle)))
    normal = np.array((-axis[1], axis[0]))

    def at(u, v, h):
        return (*(np.array((e, n)) + axis * u + normal * v), base + h)

    def trace(points, v, width=0.018, color=IRON):
        world = [at(u, v, h) for u, h in points]
        for a, b in zip(world, world[1:]):
            site.beam(parts, a, b, width, color)

    for v in (-depth, depth):
        for inset in (0.0, 0.135):
            radius = half - inset
            arc = [
                (radius * np.cos(t), spring + (rise - inset) * np.sin(t))
                for t in np.linspace(0, np.pi, 27)
            ]
            trace([(radius, -0.08), *arc, (-radius, -0.08)], v, 0.022)
        for u in (-half, half):
            trace([(u, -0.03), (u, 0.08)], v, 0.072)

    for side in (-1, 1):
        for h in (0.34, 0.64, 0.94, 1.23, 1.53, 1.76):
            scroll = [
                (side * (half - 0.073 + 0.069 * np.sin(1.52 * np.pi * t)), h + t * 0.23)
                for t in np.linspace(-0.52, 0.51, 10)
            ]
            for v in (-depth, depth):
                trace(scroll, v, 0.014)
            site.beam(
                parts,
                at(side * half, -depth, h),
                at(side * half, depth, h),
                0.021,
                IRON,
            )
        for v in (-depth, depth):
            for a in np.linspace(0.27, 1.18, 4):
                curve = [
                    (
                        side * ((half - 0.072) * np.cos(a + t * 0.08)),
                        spring
                        + (rise - 0.052) * np.sin(a + t * 0.08)
                        + 0.039 * np.sin(2 * np.pi * t),
                    )
                    for t in np.linspace(-1, 1, 12)
                ]
                trace(curve, v, 0.014)

    for h in (1.74, 1.94):
        trace(
            [
                (u, h + 0.26 * (1 - (u / 0.92) ** 2))
                for u in np.linspace(-0.92, 0.92, 21)
            ],
            -depth,
            0.016,
        )
    site.text_strokes(
        parts,
        "NORMAL 85",
        lambda x, z: at(x, -depth, 1.765 + z + 0.26 * (1 - (x / 0.92) ** 2)),
        0.136,
        0.146,
        IRON,
    )
    crown = spec["crest_height_m"]
    site.cylinder_between(
        parts,
        at(0, 0, -0.12),
        at(0, 0, spring + rise - 0.025),
        0.056,
        GREEN_POST,
        sides=10,
    )
    trace([(0, spring + rise - 0.03), (0, crown)], 0.0, 0.025)
    for side in (-1, 1):
        scroll = [
            (
                side * (0.194 * np.sin(t / 2)),
                crown - 0.24 + 0.129 * np.sin(t) - 0.18 * (1 - np.cos(t)),
            )
            for t in np.linspace(0, 1.75 * np.pi, 23)
        ]
        trace(scroll, 0.0, 0.016)

    return Polygon(
        [
            at(u, v, 0)[:2]
            for u, v in [(-half, -depth), (half, -depth), (half, depth), (-half, depth)]
        ]
    )


def landscape(ground, details, plants, field, spec, buildings, northern_ground):
    new_paving = unary_union(
        [
            LineString(row["centerline_enu_m"]).buffer(
                row["width_m"] / 2, cap_style="flat"
            )
            for row in spec["paths"]
        ]
    ).difference(buildings.union(northern_ground))
    drive = Polygon(spec["service_drive_enu_m"]).difference(
        unary_union([new_paving, buildings, northern_ground])
    )
    site.drape(ground, field, drive, ASPHALT, 0.094, 0.90)
    site.drape(ground, field, new_paving, CONCRETE, 0.098, 0.82)
    curbs = LineString(spec["service_drive_enu_m"][1:8]).buffer(0.079, cap_style="flat")
    site.drape(details, field, curbs.difference(new_paving), (161, 108, 91), 0.14, 0.80)
    planted = unary_union([Polygon(row) for row in spec["beds_enu_m"]]).difference(
        unary_union([buildings, northern_ground, new_paving, drive]).buffer(0.15)
    )
    site.drape(details, field, planted, (113, 87, 65), 0.069, 0.72)
    for k, shape in enumerate(
        planted.geoms if hasattr(planted, "geoms") else [planted]
    ):
        if shape.area < 1:
            continue
        x0, y0, x1, y1 = shape.bounds
        for i, x in enumerate(np.arange(x0 + 0.40, x1, 0.89)):
            for j, y in enumerate(np.arange(y0 + 0.35 + (i % 2) * 0.19, y1, 0.82)):
                if shape.contains(Point(x, y)):
                    z = site.ground_height(field, x, y)
                    r = 0.27 + ((i + j + k) % 4) * 0.032
                    site.orb(
                        plants,
                        (x, y, z + 0.16),
                        (r, r * 0.85, r + 0.12),
                        (77, 100 + k * 5, 61),
                    )
    for i, tree in enumerate(spec["class_trees"]):
        assert Point(tree["position_enu_m"]).distance(new_paving.union(drive)) > 0.58
        site.canopy(plants, field, tree, i)
    return drive, new_paving
