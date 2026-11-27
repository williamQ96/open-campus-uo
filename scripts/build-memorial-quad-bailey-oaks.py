# SPDX-License-Identifier: Apache-2.0
"""Geometry and root protection for the registered Bailey memorial oak rows."""

from importlib import import_module

import numpy as np
from shapely.geometry import Point, box
from shapely.ops import unary_union
import trimesh

pilot = import_module("build-pilot-trees-l2")
terrain = import_module("build-hamilton-dunes-review")
SPEC = pilot.source.ROOT / "data/metadata/memorial-quad-bailey-oaks.json"
NAMES = ("bailey-oak-wood", "bailey-oak-crowns", "bailey-oak-soil")


def roots(spec):
    return unary_union(
        [
            Point(*tree["position_enu_m"]).buffer(
                tree["trunk_radius_m"] + 0.57, quad_segs=8
            )
            for tree in spec["trees"]
        ]
    )


def collision_boxes(spec):
    return [
        [
            round(e - radius, 3),
            round(n - radius, 3),
            round(e + radius, 3),
            round(n + radius, 3),
        ]
        for tree in spec["trees"]
        for e, n in [tree["position_enu_m"]]
        for radius in [tree["trunk_radius_m"]]
    ]


def branches_and_leaves(spec, field):
    wood, crowns = [], []
    for tree in spec["trees"]:
        e, n = tree["position_enu_m"]
        height = tree["standing_height_m"]
        radius = 0.5 * tree["reported_spread_m"]
        trunk = tree["trunk_radius_m"]
        upright = tree["crown_form"] == "upright"
        base = terrain.absolute_grade(field, e, n) + 0.071
        phase = tree["id"] * 2.399963
        bark = pilot.vertex_palette((108, 90, 71))
        leaves = np.array((97, 125, 72) if upright else (104, 131, 78))

        def axis(z):
            return e + z * trunk * 0.7 * np.cos(phase), n, base + z * height

        trunk_profile = (
            (0, 0.29, 1, 0.72),
            (0.29, 0.68, 0.72, 0.37),
            (0.68, 0.92, 0.37, 0.1),
        )
        for lower, upper, base_radius, top_radius in trunk_profile:
            pilot.branch(
                wood, axis(lower), axis(upper),
                trunk * base_radius, trunk * top_radius, bark, sections=9,
            )
        sections = (
            ((0.50, 0.58), (0.64, 0.66), (0.77, 0.53), (0.88, 0.35))
            if upright
            else ((0.48, 0.58), (0.62, 0.70), (0.75, 0.53), (0.87, 0.32))
        )
        for ring, (z, reach) in enumerate(sections):
            for j in range(5):
                angle = phase + j * 2 * np.pi / 5 + ring * 0.54
                scale = reach * (0.78 + 0.13 * np.cos(angle + ring))
                x = e + radius * scale * np.cos(angle)
                y = n + radius * scale * np.sin(angle)
                zd = base + height * (z + 0.035 * np.cos(j * 2.1))
                pilot.branch(
                    wood,
                    axis(z - 0.17),
                    (x, y, zd - height * 0.05),
                    trunk * (0.31 - ring * 0.042),
                    trunk * 0.065,
                    bark,
                    sections=7,
                )
                lobes = (radius * 0.38, height * 0.112, radius * 0.38)
                crowns.append(
                    pilot.leaf_lobe(
                        (x, zd, -y), lobes, angle, leaves + (j % 3 - 1) * 5, top=True
                    )
                )
        crowns.append(
            pilot.leaf_lobe(
                (e, base + height * 0.938, -n),
                (radius * 0.24, height * 0.062, radius * 0.27),
                phase,
                leaves + 7,
                top=True,
            )
        )
    return trimesh.util.concatenate(wood), trimesh.util.concatenate(crowns)
