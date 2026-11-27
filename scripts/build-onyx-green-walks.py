# SPDX-License-Identifier: Apache-2.0
"""Build the Onyx Green surface links and the two established planting islands."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

north = import_module("build-cascade-courtyard-north")
planting = import_module("build-hedco-courtyard-landscape")
south = north.south
street = south.east
site = north.site
PACKAGE = "onyx-green-walks-review"
GROUND = "onyx-green-walks"
METADATA = site.root / "data/metadata"


def path_points(row):
    return [station[:2] for station in row["stations"]]


def scene_layout(spec):
    manifest = site.read(site.scene / "manifest.json")
    hosts = [
        site.read(site.scene / name / "site.json")
        for name in ("northeast-science-review", "cascade-volcanology-review")
    ]
    replaced = {row["id"] for host in hosts for row in host["buildings"]} | {
        alias for host in hosts for alias in host.get("absorbed_ids", [])
    }
    rows = [
        *(row for row in manifest["buildings"] if row["id"] not in replaced),
        *(row for host in hosts for row in host["buildings"]),
    ]
    focus = box(*spec["extent_enu_m"]).buffer(3)
    buildings = [
        outline
        for row in rows
        for ring in [row["footprint_enu_m"], *row.get("support_collision_enu_m", [])]
        if (outline := Polygon(ring).buffer(0)).intersects(focus)
    ]
    reserved = [Polygon(ring) for ring in spec["reserved_enu_m"]]
    islands = [Polygon(row["outline_enu_m"]) for row in spec["islands"]]
    assert all(shape.is_valid for shape in [*islands, *reserved])
    closed = unary_union([*buildings, *reserved]).buffer(0.055)
    previous = north.route_coverage(
        site.read(METADATA / "cascade-courtyard-north.json")
    )
    road = site.read(METADATA / "east-thirteenth-east.json")
    sidewalk = street.band(road["sidewalk_north"]).union(
        street.west.surface(road["extra_walks"])
    )
    walk = unary_union(
        [
            LineString(path_points(row)).buffer(row["width_m"] / 2)
            for row in spec["paths"]
        ]
        + [Polygon(ring) for ring in spec["plaza_polygons_enu_m"]]
    ).difference(unary_union([previous, sidewalk, closed, *islands]))
    return walk, previous, sidewalk, closed, islands


def route_coverage(spec):
    walk, _, sidewalk, _, _ = scene_layout(spec)
    street_connection = next(
        row for row in spec["paths"] if row.get("closes_on_existing_node")
    )
    approach = LineString(path_points(street_connection)[-3:])
    tie = approach.buffer(street_connection["width_m"] / 2).intersection(sidewalk)
    return walk.union(tie)


def grade_model(spec, field, previous, street_paving):
    models = [
        (LineString(path_points(row)), np.asarray(row["stations"])[:, 2])
        for row in spec["paths"]
    ]
    profiles = []
    for axis, heights in models:
        path = np.asarray(axis.coords)
        distances = np.r_[0.0, np.linalg.norm(np.diff(path, axis=0), axis=1).cumsum()]
        profiles.append((axis, heights, distances))
    prior = site.read(METADATA / "science-walk-east.json")
    prior_grade = north.longitudinal_grade(
        prior["points_enu_m"], prior["elevations_z_m"]
    )

    def profile(e, n):
        point = Point(e, n)
        axis, heights, distances = min(profiles, key=lambda row: row[0].distance(point))
        fitted = float(np.interp(axis.project(point), distances, heights))
        distance = street_paving.distance(point)
        if distance < 5.5:
            fraction = distance / 5.5
            weight = 1 - fraction * fraction * (3 - 2 * fraction)
            return (
                fitted * (1 - weight)
                + (site.ground_height(field, e, n) + 0.108) * weight
            )
        distance = previous.distance(point)
        if distance < 0.50:
            weight = 1 - distance / 0.50
            return fitted * (1 - weight) + prior_grade(e, n) * weight
        return fitted

    return profile


def grade_shoulders(
    parts, path, reserved, previous, street_paving, islands, height, field
):
    margin = path.buffer(1.10).difference(
        unary_union([path, reserved, previous, street_paving, *islands])
    )

    def profile(e, n):
        ground = site.ground_height(field, e, n) + 0.022
        blend = max(0.0, 1 - path.distance(Point(e, n)) / 1.10)
        return ground + (height(e, n) - 0.013 - ground) * blend

    site.landscape.top_surface(parts, margin, profile, (112, 118, 100), cell=0.55)
    return margin.area


def make_island(borders, beds, bushes, shape, row, field, seed):
    z = row["top_z_m"]
    inside = shape.buffer(-0.16)
    assert not inside.is_empty
    perimeter = shape.exterior
    bottom = (
        min(
            site.ground_height(field, *perimeter.interpolate(distance).coords[0])
            for distance in np.arange(0, perimeter.length, 0.32)
        )
        - 0.10
    )
    site.solid(borders, shape.difference(inside), bottom, z, (171, 167, 149))
    site.solid(beds, inside, bottom, z - 0.063, (96, 99, 77))
    rng = np.random.default_rng(seed)
    w, s, e, n = inside.bounds
    positions = [
        (x, y)
        for x in np.arange(w + 0.41, e, 1.06)
        for y in np.arange(s + 0.45, n, 1.14)
        if inside.buffer(-0.20).covers(Point(x, y))
    ]
    count = 0
    for index, (x, y) in enumerate(positions):
        radius = min(
            inside.boundary.distance(Point(x, y)) - 0.06, rng.uniform(0.34, 0.54)
        )
        if radius >= 0.17:
            count += 1
            base = z - 0.063 - site.ground_height(field, x, y)
            planting.planted_crown(
                bushes,
                field,
                x,
                y,
                radius,
                0.27 + 0.18 * rng.random(),
                index + seed,
                base=base,
            )
    return count


def route_records(spec):
    records = []
    for row in spec["paths"]:
        anchor, *points = path_points(row)
        record = dict(anchor_enu_m=anchor, points_enu_m=points)
        if row.get("closes_on_existing_node"):
            record["end_enu_m"] = points.pop()
        records.append(record)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(METADATA / "onyx-green-walks.json")
    for name, digest in spec["pins"].items():
        assert site.pin(site.scene / name / "site.json") == digest, name
    records = route_records(spec)
    priors = [
        site.read(site.scene / key / "site.json")
        for key in (street.PACKAGE, south.PACKAGE, north.PACKAGE)
    ]
    known = {
        tuple(point)
        for prior in priors
        for path in prior["walkable_ground"]["paths"]
        for point in north.stations(path)
    }
    for record in records:
        assert tuple(record["anchor_enu_m"]) in known
        assert not known.intersection(map(tuple, record["points_enu_m"]))
        if "end_enu_m" in record:
            assert tuple(record["end_enu_m"]) in known
        known.update(map(tuple, record["points_enu_m"]))
    path, previous, sidewalk, obstacles, islands = scene_layout(spec)
    coverage = path.union(previous).union(sidewalk)
    collision = []
    for shape in islands:
        west, lower, east, upper = shape.bounds
        stations = np.linspace(lower, upper, 7)
        collision.extend(
            box(*shape.intersection(box(west, a, east, b)).bounds)
            for a, b in zip(stations, stations[1:])
        )
    blocked = unary_union([obstacles, *collision])
    lines = [LineString(path_points(row)) for row in spec["paths"]]
    for line in lines:
        assert line.difference(coverage.buffer(0.07)).length <= 0.005, line.wkt
        assert line.distance(blocked) >= 0.55, (line.wkt, line.distance(blocked))

    _, field, _ = street.pinned_site(
        site.scene, site.read(METADATA / "east-thirteenth-east.json")
    )
    profile = grade_model(spec, field, previous, sidewalk)
    ground, edges, borders, beds, bushes = [], [], [], [], []
    south.pave(ground, edges, path, profile, field, (162, 156, 144))
    margin_area = grade_shoulders(
        ground, path, obstacles, previous, sidewalk, islands, profile, field
    )
    crowns = sum(
        make_island(borders, beds, bushes, shape, row, field, seed=623 + i)
        for i, (shape, row) in enumerate(zip(islands, spec["islands"], strict=True))
    )
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    desc = args.stage / "site.json"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        ("onyx-green-paving-edges", edges, "landscape-detail"),
        ("onyx-green-island-curbs", borders, "landscape-detail"),
        ("onyx-green-island-soil", beds, "landscape-vegetation"),
        ("onyx-green-island-planting", bushes, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    keys = (
        "source_presentation_sha256",
        "source_base_model_sha256",
        "source_heightfield_sha256",
        "source_navigation_sha256",
    )
    west, lower, east, upper = path.bounds
    assert upper - lower < 140
    site.fairmount.write_json(
        desc,
        {
            **{key: priors[0][key] for key in keys},
            "prerequisite_site_sha256": spec["pins"][north.PACKAGE],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(glb),
            "buildings": [],
            "closed_site_boxes_enu_m": [shape.bounds for shape in collision],
            "walkable_ground": {
                "bounds_enu_m": [(west, lower, east, 67.0), (west, 67.0, east, upper)],
                "paths": records,
            },
        },
        compact=True,
    )
    result = dict(
        walk_paving_m2=round(path.area, 3),
        shoulder_m2=round(margin_area, 3),
        islands_m2=round(sum(shape.area for shape in islands), 3),
        vegetation_clusters=crowns,
        route_edges=sum(len(north.stations(record)) - 1 for record in records),
        path_lengths_m=[round(line.length, 3) for line in lines],
        minimum_clearance_m=round(min(line.distance(blocked) for line in lines), 3),
        faces=faces,
        asset_sha256=site.pin(glb),
        descriptor_sha256=site.pin(desc),
    )
    site.fairmount.write_json(args.audit, result)
    print(result)


if __name__ == "__main__":
    main()
