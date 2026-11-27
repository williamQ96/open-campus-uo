# SPDX-License-Identifier: Apache-2.0
"""Fit the lower Science Walk extension and the inventoried Dawn redwood."""

from math import cos, sin, tau

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon, box


def walk_footprint(spec, old_cover, obstacles):
    return (
        LineString(spec["points_enu_m"])
        .buffer(spec["width_m"] / 2)
        .union(Polygon(spec["plaza_outline_enu_m"]))
        .difference(old_cover.union(obstacles))
    )


def redwood(parts, site, spec, obstacles):
    east, north = spec["enu_m"]
    z = spec["base_z_m"]
    height = spec["height_m"]
    radius = spec["trunk_radius_m"]
    crown = spec["crown_radius_m"]
    bark = (101, 73, 57)
    stem = [
        (0.00, 1.15),
        (0.12, 0.93),
        (0.39, 0.74),
        (0.68, 0.49),
        (0.88, 0.29),
        (0.97, 0.13),
    ]
    profile = [(0, -0.07)]
    profile.extend((radius * width, height * z) for z, width in stem)
    profile.append((0, height * 0.98))
    trunk = trimesh.creation.revolve(profile, sections=11)
    trunk.apply_transform(trimesh.transformations.rotation_matrix(-tau / 4, [1, 0, 0]))
    trunk.apply_translation([east, z, -north])
    trunk.visual.vertex_colors = [*bark, 255]
    parts.append(trunk)
    rng = np.random.default_rng(spec["object_id"])
    levels = [
        (0.32, 0.78, 3),
        (0.46, 1.00, 4),
        (0.59, 0.88, 5),
        (0.72, 0.68, 4),
        (0.84, 0.46, 3),
        (0.91, 0.26, 3),
    ]
    for level, scale, branches in levels:
        phase = rng.uniform(0, tau)
        for i in range(branches):
            angle = phase + tau * i / branches
            reach = crown * scale * rng.uniform(0.86, 1.0)
            x, y = reach * cos(angle), reach * sin(angle)
            level_z = z + level * height + rng.uniform(-0.42, 0.42)
            site.cylinder_between(
                parts,
                (east, north, level_z + 0.35),
                (east + 0.66 * x, north + 0.66 * y, level_z - 0.20),
                radius * scale * 0.32,
                bark,
                sides=6,
            )
            for along, breadth, lift in [(0.32, 0.36, 0.45), (0.67, 0.29, -0.13)]:
                shade = int(rng.integers(-7, 9))
                center = Point(east + along * x, north + along * y)
                lobe = min(reach * breadth, obstacles.distance(center) - 0.15)
                assert lobe > 0.25
                site.orb(
                    parts,
                    (center.x, center.y, level_z + lift),
                    (lobe, lobe, 0.75 + 0.72 * scale),
                    (83 + shade, 107 + shade, 68 + shade),
                )
    site.orb(
        parts,
        (east + 0.11, north - 0.16, z + 0.947 * height),
        (0.87, 0.79, height * 0.053),
        (100, 120, 77),
    )
    margin = radius * 1.18
    return box(east - margin, north - margin, east + margin, north + margin)


def graded_margin(paving, old, blockers, spec):
    tree = spec["tree"]
    root_zone = Point(tree["enu_m"]).buffer(tree["ground_mound_radius_m"])
    margin = paving.buffer(spec["shoulder_width_m"]).union(root_zone)
    return margin.difference(paving.union(old).union(blockers))


def make_extension(south, field, spec, old_cover, old_profile, east_profile, obstacles):
    site = south.site
    paving = walk_footprint(spec, old_cover, obstacles)
    walk, edges, trees = [], [], []

    def grade(east, north):
        distance = old_cover.distance(Point(east, north))
        fraction = min(1, distance / 0.48)
        return (
            old_profile(east, north) * (1 - fraction)
            + east_profile(east, north) * fraction
        )

    south.pave(walk, edges, paving, grade, field, (159, 154, 143))
    tree = spec["tree"]
    center = Point(tree["enu_m"])
    radius = tree["ground_mound_radius_m"]
    margin = graded_margin(paving, old_cover, obstacles, spec)

    def margin_grade(east, north):
        point = Point(east, north)
        base = site.ground_height(field, east, north) + 0.021
        fraction = max(0, 1 - paving.distance(point) / spec["shoulder_width_m"])
        path_height = grade(east, north) - 0.007
        bank = base + max(0, path_height - base) * fraction
        root_share = max(0, 1 - center.distance(point) / radius)
        root_share *= root_share * (3 - 2 * root_share)
        mound = base + (tree["base_z_m"] - base) * root_share
        return max(bank, mound)

    site.landscape.top_surface(walk, margin, margin_grade, (117, 119, 94), cell=0.53)
    tree_collision = redwood(trees, site, tree, obstacles)
    return walk, edges, trees, tree_collision, paving, margin
