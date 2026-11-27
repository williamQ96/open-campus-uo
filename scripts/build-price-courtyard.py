# SPDX-License-Identifier: Apache-2.0
"""Build the exterior Price Science Commons courtyard and the public overlook."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

onyx = import_module("build-onyx-green-walks")
site = onyx.site
PACKAGE = "price-courtyard-review"
GROUND = "price-courtyard-terrace"
GLASS = "price-courtyard-glass"
METADATA = onyx.METADATA


def outlines(spec):
    predecessor = site.read(METADATA / "onyx-green-walks.json")
    previous = onyx.route_coverage(predecessor)
    court = Polygon(spec["court"])
    cut = box(*spec["cut_enu_m"])
    edge = court.buffer(0.13, join_style="mitre")
    link = LineString(onyx.north.stations(spec["overlook_path"])).buffer(1.07)
    apron = box(-197.8, 73.1, -189.99, 79.0)
    west_walk = box(-198.1, 78.8, -195.6, 101.8)
    north_walk = box(-197.65, 101.70, -190.06, 104.42)
    upper = unary_union([apron, link, west_walk, north_walk]).difference(
        edge.union(previous)
    )
    assert court.is_valid and cut.contains(court) and upper.is_valid
    return court, cut, edge, upper, previous


def route_coverage(spec):
    _, _, _, upper, _ = outlines(spec)
    return upper


def rim_rail(spec):
    rails, glass = [], []
    rim_z = spec["plaza_height_z_m"] + 0.012
    top = rim_z + spec["rail_height_m"]
    points = spec["rail_enu_m"]
    steel = (89, 96, 92)
    for i, (a, b) in enumerate(zip(points, points[1:])):
        line = LineString([a, b])
        bays = int(np.ceil(line.length / 1.55))
        dimensions = [
            line.interpolate(j / bays, normalized=True).coords[0]
            for j in range(bays + 1)
        ]
        site.cylinder_between(rails, (*a, top), (*b, top), 0.027, steel, sides=8)
        for east, north in dimensions if not i else dimensions[1:]:
            site.cylinder_between(
                rails, (east, north, rim_z), (east, north, top), 0.022, steel, sides=8
            )
        for c, d in zip(dimensions, dimensions[1:]):
            plot = LineString([c, d]).buffer(0.014, cap_style="flat")
            site.solid(glass, plot, rim_z + 0.058, top - 0.04, (160, 195, 190))
            colors = glass[-1].visual.vertex_colors.copy()
            colors[:, 3] = 58
            glass[-1].visual.vertex_colors = colors
    return rails, glass


def lower_court(spec, court, edge, field):
    floor, dirt, plants, walls, furniture = [], [], [], [], []
    stations = np.asarray(spec["floor_profile_north_z_m"])

    def floor_z(east, north):
        return float(np.interp(north, stations[:, 0], stations[:, 1]))

    gardens = [Polygon(ring) for ring in spec["beds"]]
    assert all(court.covers(shape) and shape.is_valid for shape in gardens)
    slabs = court.difference(unary_union(gardens))
    site.landscape.top_surface(floor, slabs, floor_z, (144, 145, 135), cell=0.44)
    site.solid(
        walls, edge.difference(court), -2.99, spec["plaza_height_z_m"], (154, 153, 141)
    )
    for index, garden in enumerate(gardens):

        def soil_z(east, north):
            return (
                floor_z(east, north)
                + 0.13
                + min(0.17, garden.boundary.distance(Point(east, north)) * 0.22)
            )

        site.landscape.top_surface(dirt, garden, soil_z, (98, 92, 71), cell=0.37)
        west, south, east, north = garden.bounds
        for x in np.arange(west + 0.27, east, 0.72):
            for y in np.arange(south + 0.26, north, 0.82):
                if garden.covers(Point(x, y)):
                    base = soil_z(x, y) - site.ground_height(field, x, y)
                    onyx.planting.planted_crown(
                        plants,
                        field,
                        x,
                        y,
                        0.23 + 0.008 * (index % 4),
                        0.27,
                        (x + y) * 0.57,
                        base=base,
                    )
    for index, (east, north) in enumerate(spec["plant_trees_enu_m"]):
        assert any(g.covers(Point(east, north)) for g in gardens)
        z = floor_z(east, north) + 0.22
        h = 1.47 + (index % 3) * 0.19
        site.cylinder_between(
            plants,
            (east, north, z),
            (east, north, z + h),
            0.045,
            (101, 82, 57),
            sides=7,
        )
        for offset, shoulder in ((-0.17, 0.60), (0.19, 0.83), (0.0, 1.05)):
            site.orb(
                plants,
                (east + offset, north, z + h * shoulder),
                (0.49, 0.42, 0.38),
                (111, 136, 76),
            )
    for east, north, long in ((-193.8, 93.95, 1.78), (-192.45, 82.24, 1.80)):
        z = floor_z(east, north)
        for x in (east - long * 0.34, east + long * 0.34):
            site.solid(
                furniture,
                box(x - 0.10, north - 0.19, x + 0.10, north + 0.19),
                z - 0.018,
                z + 0.43,
                (116, 117, 108),
            )
        for dy in (-0.14, -0.046, 0.046, 0.14):
            n = north + dy
            site.solid(
                furniture,
                box(east - long / 2, n - 0.041, east + long / 2, n + 0.041),
                z + 0.43,
                z + 0.475,
                (139, 100, 64),
            )
    return floor, dirt, plants, walls, furniture, sum(shape.area for shape in gardens)


def courtyard_glazing(spec):
    bay = spec["courtyard_face"]
    west, south, east, north = bay["bounds_enu_m"]
    sill, top = bay["vertical_m"]
    terrace = spec["plaza_height_z_m"]
    frames, infill = [], []
    color = (68, 77, 74)
    height_bands = [(sill, terrace), (terrace, top - 0.86), (top - 0.86, top)]
    stations = np.linspace(south, north, 15)
    for i, (z0, z1) in enumerate(height_bands):
        for j, (n0, n1) in enumerate(zip(stations, stations[1:])):
            tint = (j * 5 + i * 7) % 14
            glass = (48 + tint, 78 + tint, 77 + tint)
            site.solid(infill, box(west + 0.036, n0, east, n1), z0, z1, glass)
        site.solid(
            frames, box(west, south, east + 0.035, north), z0 - 0.029, z0 + 0.029, color
        )
    for n in stations:
        site.solid(
            frames,
            box(west - 0.015, n - 0.029, east + 0.031, n + 0.029),
            sill,
            top,
            color,
        )
    site.solid(
        frames,
        box(west - 0.02, south, east + 0.38, north),
        top - 0.07,
        top + 0.06,
        (153, 146, 127),
    )
    return frames, infill


def upper_replacement(spec, cut, edge, upper, previous, field):
    support, paving = [], []
    old = site.read(METADATA / "onyx-green-walks.json")
    _, prior_cascade, street, _, _ = onyx.scene_layout(old)
    previous_grade = onyx.grade_model(old, field, prior_cascade, street)
    target = spec["plaza_height_z_m"]
    retaining_lip = edge.buffer(0.15)

    def paved(east, north):
        pt = Point(east, north)
        blend = min(1.0, pt.distance(previous) / 1.35)
        return previous_grade(east, north) * (1 - blend) + target * blend

    def original(east, north):
        pt = Point(east, north)
        weight = min(1.0, cut.boundary.distance(pt) / 1.55)
        weight = max(weight, max(0.0, 1 - retaining_lip.distance(pt) / 0.65))
        legacy = site.ground_height(field, east, north) + 0.035
        fitted = (
            min(target - 0.02, previous_grade(east, north) - 0.012)
            if previous.covers(pt)
            else target - 0.012
        )
        return legacy * (1 - weight) + fitted * weight

    site.landscape.top_surface(paving, upper, paved, (163, 157, 146), cell=0.46)
    site.landscape.top_surface(
        support, cut.difference(edge.union(upper)), original, (155, 151, 139), cell=0.48
    )
    return paving, support


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--stage", type=Path, required=True)
    cli.add_argument("--audit", type=Path, required=True)
    args = cli.parse_args()
    spec = site.read(METADATA / "price-courtyard.json")
    prior_path = site.scene / onyx.PACKAGE / "site.json"
    assert site.pin(prior_path) == spec["pins"][onyx.PACKAGE]
    prior = site.read(prior_path)
    court, cut, edge, terrace, previous = outlines(spec)
    path = spec["overlook_path"]
    assert path["anchor_enu_m"] in [
        p for row in prior["walkable_ground"]["paths"] for p in row["points_enu_m"]
    ]
    line = LineString(onyx.north.stations(path))
    assert line.difference(terrace.union(previous).buffer(0.065)).length < 0.005
    assert line.distance(edge) > 1.30
    _, field, _ = onyx.street.pinned_site(
        site.scene, site.read(METADATA / "east-thirteenth-east.json")
    )
    paving, support = upper_replacement(spec, cut, edge, terrace, previous, field)
    floor, dirt, plants, walls, furniture, bed_area = lower_court(
        spec, court, edge, field
    )
    rails, glass = rim_rail(spec)
    face_frames, face_glass = courtyard_glazing(spec)
    args.stage.mkdir(parents=True, exist_ok=True)
    model = args.stage / "site.glb"
    desc = args.stage / "site.json"
    faces = site.export(
        model,
        (GROUND, paving, "landscape-surface"),
        ("price-courtyard-terrain-tie", support, "landscape-detail"),
        ("price-courtyard-floor", floor, "landscape-detail"),
        ("price-courtyard-retaining-walls", walls, "landscape-detail"),
        ("price-courtyard-planted-beds", dirt, "landscape-vegetation"),
        ("price-courtyard-planting", plants, "landscape-vegetation"),
        ("price-courtyard-wood-seating", furniture, "landscape-detail"),
        ("price-courtyard-rail", rails, "landscape-detail"),
        ("price-courtyard-pavilion-frames", face_frames, "landscape-detail"),
        ("price-courtyard-pavilion-glazing", face_glass, "landscape-detail"),
        (GLASS, glass, "landscape-detail"),
        surface_layer=GROUND,
        translucent_nodes={GLASS},
    )
    limits = [
        box(-197, 78.86, -189.87, 91.98),
        box(-195.95, 91.98, -189.87, 97.70),
        box(-197, 97.70, -189.87, 101.74),
    ]
    assert unary_union(limits).covers(court)
    keys = (
        "source_presentation_sha256",
        "source_base_model_sha256",
        "source_heightfield_sha256",
        "source_navigation_sha256",
    )
    site.fairmount.write_json(
        desc,
        {
            **{key: prior[key] for key in keys},
            "prerequisite_site_sha256": site.pin(prior_path),
            "terrain_cut_enu_m": spec["cut_enu_m"],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(model),
            "buildings": [],
            "closed_site_boxes_enu_m": [limit.bounds for limit in limits],
            "walkable_ground": {"bounds_enu_m": [terrace.bounds], "paths": [path]},
        },
        compact=True,
    )
    report = dict(
        terrace_m2=round(terrace.area, 3),
        lower_court_m2=round(court.area, 3),
        planted_m2=round(bed_area, 3),
        railing_m=round(LineString(spec["rail_enu_m"]).length, 3),
        routes_m=round(line.length, 3),
        faces=faces,
        asset_sha256=site.pin(model),
        descriptor_sha256=site.pin(desc),
    )
    site.fairmount.write_json(args.audit, report)
    print(report)


if __name__ == "__main__":
    main()
