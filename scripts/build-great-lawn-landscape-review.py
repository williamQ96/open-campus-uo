# SPDX-License-Identifier: Apache-2.0
"""Export the photographed Great Lawn oak court and its western approaches."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.affinity import scale
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

site = import_module("build-pioneer-cemetery-landscape-review")
hamilton = site.landscape

PACKAGE = "great-lawn-landscape-review"
GROUND = "great-lawn-oak-court"
FURNISHINGS = "great-lawn-oak-furnishings"
PLANTS = "great-lawn-oak-planting"
PAD_LIFT = 0.184
AGGREGATE = (139, 139, 130)
CONCRETE = (184, 182, 169)
MULCH = (104, 78, 57)


def notch_wall(parts, field, seat):
    east, north = seat["position_enu_m"]
    radius = seat["radius_m"]
    ratio = seat["axis_ratio"]
    half = seat["width_m"] / 2
    start, end = seat["start_end_deg"]

    def arc(start_angle, end_angle, segments):
        angles = np.deg2rad(np.linspace(start_angle, end_angle, segments + 1))
        rings = [
            np.column_stack(
                [east + r * np.cos(angles), north + ratio * r * np.sin(angles)]
            )
            for r in (radius + half, radius - half)
        ]
        return Polygon(np.concatenate([rings[0], rings[1][::-1]]))

    def cap_height(x, y):
        angle = np.rad2deg(np.arctan2((y - north) / ratio, x - east))
        ramp = np.clip(min(angle - start, end - angle) / 49, 0, 1)
        seat_height = 0.035 + (seat["seat_height_m"] - 0.035) * ramp
        return site.ground_height(field, x, y) + PAD_LIFT + seat_height

    bottom = site.ground_height(field, east, north) - 0.21
    joints = np.linspace(start, end, 5)
    for i, (a, b) in enumerate(zip(joints, joints[1:])):
        plan = arc(a + (0.14 if i else 0), b - 0.14, 12)
        parts.append(
            site.geometry.shell(plan, bottom, cap_height, (163, 161, 151), CONCRETE)
        )
    intervals = np.linspace(start + 15, end - 15, 11)
    boxes = [arc(a, b, 5).bounds for a, b in zip(intervals, intervals[1:])]
    return arc(start, end, 48), boxes


def build_planting(parts, field, beds, tree):
    e, n = tree["position_enu_m"]
    z = site.ground_height(field, e, n)
    h, radius = tree["height_m"], tree["crown_radius_m"]
    bark = (89, 79, 66)
    site.cylinder_between(
        parts,
        (e, n, z + 0.10),
        (e + 0.04, n + 0.01, z + h * 0.81),
        0.048,
        bark,
        sides=8,
    )
    rng = np.random.default_rng(273)
    for k, rise in enumerate((0.43, 0.51, 0.55, 0.62, 0.68, 0.74, 0.81, 0.91)):
        a = k * 2.399963
        reach = radius * min(0.67, 1.5 * (1 - rise))
        x, y = e + reach * np.cos(a), n + reach * np.sin(a)
        tip = (x, y, z + h * rise)
        site.cylinder_between(
            parts,
            (e + 0.025, n, z + h * (rise - 0.19)),
            tip,
            0.019,
            bark,
            sides=6,
        )
        for j in range(4):
            du, dv = rng.uniform(-0.18, 0.18, 2)
            size = rng.uniform(0.17, 0.24)
            site.orb(
                parts,
                (x + du, y + dv, tip[2] + 0.05 + 0.035 * j),
                (size, size * 0.85, size * 0.56),
                (73 + 6 * j, 88 + 5 * j, 55 + 2 * j),
            )
    for shift, lean in ((-0.39, 0.03), (0.43, 0.08)):
        site.cylinder_between(
            parts,
            (e + shift, n + 0.07, z + 0.14),
            (e + shift + lean, n + 0.07, z + 2.04),
            0.032,
            (150, 121, 83),
            sides=7,
        )
        site.cylinder_between(
            parts,
            (e + shift * 0.85, n + 0.07, z + 1.52),
            (e, n, z + 1.52),
            0.012,
            (76, 73, 55),
            sides=5,
        )

    counts = {"tufts": 0, "shrubs": 0}
    for piece in site.geometry.sections(beds):
        min_e, min_n, max_e, max_n = piece.bounds
        plantable = piece.buffer(-0.36)
        for east in np.arange(min_e, max_e, 0.78):
            for north in np.arange(min_n, max_n, 0.73):
                x, y = np.array([east, north]) + rng.uniform(-0.26, 0.26, 2)
                if not plantable.covers(Point(x, y)):
                    continue
                ground = site.ground_height(field, x, y) + PAD_LIFT
                if rng.random() < 0.24:
                    counts["shrubs"] += 1
                    for k in range(5):
                        a = k * 2.399963
                        height = rng.uniform(0.20, 0.44)
                        u, v = x + 0.17 * np.cos(a), y + 0.14 * np.sin(a)
                        tip = (u, v, ground + height)
                        site.cylinder_between(
                            parts, (x, y, ground), tip, 0.012, (92, 89, 62), sides=5
                        )
                        site.orb(
                            parts, tip, (0.18, 0.14, 0.092), (111, 124 - 6 * k, 70)
                        )
                else:
                    counts["tufts"] += 1
                    for k in range(9):
                        a = rng.uniform(0, 1) + k * 2.399963
                        height = rng.uniform(0.10, 0.34)
                        dx, dy = height * 0.60 * np.cos(a), height * 0.60 * np.sin(a)
                        site.cylinder_between(
                            parts,
                            (x, y, ground),
                            (x + dx, y + dy, ground + height),
                            0.010,
                            (127 + 4 * (k % 3), 132, 76),
                            sides=4,
                        )
    return counts


def globe_lamp(parts, field, location):
    e, n = location
    z = site.ground_height(field, e, n) + PAD_LIFT
    plan = Point(e, n)
    green = (54, 75, 60)
    for radius, low, high in (
        (0.20, -0.04, 0.07),
        (0.144, 0.07, 0.31),
        (0.059, 0.31, 2.77),
        (0.091, 2.77, 2.85),
    ):
        parts.append(
            hamilton.cap(plan.buffer(radius, quad_segs=5), z + low, z + high, green)
        )
    site.orb(parts, (e, n, z + 3.01), (0.159, 0.159, 0.19), (224, 223, 208), 2)
    site.orb(parts, (e, n, z + 3.208), (0.043, 0.043, 0.043), (156, 154, 124))
    return plan.buffer(0.20).bounds


def check_paths(graph, paths, paving, obstacles):
    available = set(map(tuple, graph["nodes_enu_m"]))
    edges, minimum = 0, float("inf")
    for i, path in enumerate(paths):
        tail = [path["end_enu_m"]] if "end_enu_m" in path else []
        assert all(tuple(p) in available for p in [path["anchor_enu_m"], *tail])
        points = [path["anchor_enu_m"], *path["points_enu_m"], *tail]
        edges += len(points) - 1
        assert all(
            0.05 < span < 20 for span in np.linalg.norm(np.diff(points, axis=0), axis=1)
        )
        # The first edge ties into the existing Agate road without painting a crossing.
        line = LineString(points[1:] if i == 0 else points)
        assert line.difference(paving.buffer(0.13)).length < 0.20, line.wkt
        minimum = min(minimum, line.distance(obstacles))
        available.update(map(tuple, path["points_enu_m"]))
    assert minimum > 0.44, minimum
    return edges, minimum


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(site.root / f"data/metadata/{PACKAGE}.json")
    source = site.read(site.root / "data/metadata/hamilton-dunes-review.json")
    manifest = site.read(site.scene / "manifest.json")
    config = site.read(site.scene / "presentation.json")
    field_path = site.scene / manifest["heightfield_url"]
    nav = site.scene / "navigation.json"
    predecessor = site.scene / config["hamilton_dunes_site"]["url"]
    pins = spec["pins"]
    assert pins == {
        "presentation": config["asset_sha256"],
        "model": manifest["model"]["sha256"],
        "heightfield": site.pin(field_path),
        "navigation": site.pin(nav),
        "hamilton_descriptor": site.pin(predecessor),
        "hamilton_glb": site.pin(site.scene / site.read(predecessor)["url"]),
    }
    assert config["hamilton_dunes_site"]["sha256"] == pins["hamilton_descriptor"]
    field = site.read(field_path)
    previous = hamilton.park_paving(
        source,
        Polygon(source["lawn_enu_m"]).intersection(box(0, -133.6, 500, 500)),
        LineString(source["visit_route"]["points_enu_m"]),
        box(*source["sand_enu_m"]),
        Polygon(source["support_enu_m"]),
    )
    new_paths = unary_union(
        [LineString(path).buffer(1.12, quad_segs=7) for path in spec["entry_paths"]]
    ).difference(previous)
    seat = spec["seat"]
    center = Point(*seat["position_enu_m"])
    pad = scale(center.buffer(1, quad_segs=28), *seat["pad_radii_m"])
    pad = pad.difference(previous)
    tree = seat["tree"]
    trunk = Point(*tree["position_enu_m"])
    pit = trunk.buffer(tree["pit_radius_m"], quad_segs=18)
    beds = unary_union(
        [Polygon(bed).buffer(-0.46).buffer(0.46, quad_segs=7) for bed in spec["beds"]]
    ).difference(unary_union([pad, new_paths, previous]))
    paving, details, planting = [], [], []
    for shape, color in (
        (new_paths.difference(pad), hamilton.PAVING),
        (pad.difference(pit), AGGREGATE),
        (pit.union(beds), MULCH),
    ):
        site.drape(paving, field, shape, color, PAD_LIFT, 0.63)
    seat_plan, collision = notch_wall(details, field, seat)
    assert pad.covers(seat_plan) and pad.covers(pit)
    collision.append(trunk.buffer(0.25).bounds)
    assert beds.covers(Point(*spec["lamp_enu_m"]))
    collision.append(globe_lamp(details, field, spec["lamp_enu_m"]))
    counts = build_planting(planting, field, beds, tree)
    paths = spec["routes"]
    edges, clearance = check_paths(
        site.read(nav),
        paths,
        unary_union([previous, new_paths, pad.difference(pit)]),
        unary_union([box(*b) for b in collision]),
    )
    assert len(collision) <= 16
    bounds = unary_union([pad, beds, new_paths]).bounds

    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    faces = site.export(
        glb,
        (GROUND, paving, "landscape-surface"),
        (FURNISHINGS, details, "landscape-detail"),
        (PLANTS, planting, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    descriptor = args.stage / "site.json"
    site.fairmount.write_json(
        descriptor,
        dict(
            source_presentation_sha256=pins["presentation"],
            source_base_model_sha256=pins["model"],
            source_heightfield_sha256=pins["heightfield"],
            source_navigation_sha256=pins["navigation"],
            ground_node=GROUND,
            url=f"{PACKAGE}/site.glb",
            sha256=site.pin(glb),
            buildings=[],
            closed_site_boxes_enu_m=[
                [round(value, 4) for value in b] for b in collision
            ],
            walkable_ground={
                "paths": paths,
                "bounds_enu_m": [
                    [round(x, 3) for x in box(*bounds).buffer(0.10).bounds]
                ],
            },
        ),
        compact=True,
    )
    metrics = dict(
        seat_plan_m2=round(seat_plan.area, 2),
        pad_m2=round(pad.area, 2),
        new_paving_m2=round(new_paths.difference(pad).area, 2),
        planted_m2=round(beds.area, 2),
        plants=counts,
        edges=edges,
        minimum_obstacle_clearance_m=round(clearance, 3),
        faces=faces,
        asset_sha256=site.pin(glb),
        descriptor_sha256=site.pin(descriptor),
    )
    site.fairmount.write_json(args.audit, metrics)
    print(metrics)


if __name__ == "__main__":
    main()
