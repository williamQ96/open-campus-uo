# SPDX-License-Identifier: Apache-2.0
"""Build the ground-level Onyx Bridge path and its north garden approaches."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

onyx = import_module("build-onyx-green-walks")
wayfinding = import_module("build-northeast-campus-wayfinding")
site = onyx.site
PACKAGE = "onyx-bridge-underpass-review"
GROUND = "onyx-bridge-underpass"
METADATA = onyx.METADATA


def layout(spec):
    prior = onyx.route_coverage(site.read(METADATA / "onyx-green-walks.json"))
    host = site.read(site.scene / "northeast-science-review/site.json")
    obstacles = []
    for row in host["buildings"]:
        ground = row.get("ground_footprints_enu_m", [row["footprint_enu_m"]])
        for ring in [*ground, *row.get("support_collision_enu_m", [])]:
            obstacles.append(Polygon(ring))
    fixtures = site.read(site.scene / "northeast-campus-wayfinding-review/site.json")
    focus = box(-220, 109, -187, 160)
    obstacles.extend(
        box(*r)
        for r in fixtures["closed_site_boxes_enu_m"]
        if box(*r).intersects(focus)
    )
    hosts = unary_union(obstacles).buffer(0.055)
    way = site.read(METADATA / "northeast-campus-wayfinding.json")
    entry, _, old_beds, planter = wayfinding.onyx_footprints(way["onyx"], hosts)
    beds = [Polygon(row["outline_enu_m"]) for row in spec["beds"]]
    stops = unary_union([hosts, old_beds, planter, *beds])
    shapes = [
        LineString(onyx.path_points(row)).buffer(row["width_m"] / 2)
        for row in spec["paths"]
    ] + [Polygon(ring) for ring in spec["pavements"]]
    paving = unary_union(shapes).difference(stops.union(prior).union(entry))
    return paving, beds, stops, prior, entry


def route_coverage(spec):
    paving, _, _, _, entry = layout(spec)
    tail = LineString(onyx.path_points(spec["paths"][0])[-6:])
    return paving.union(tail.buffer(1.35).intersection(entry))


def grade(spec, field, prior, entry):
    options = []
    for row in spec["paths"]:
        path = np.asarray(row["stations"])
        points = path[:, :2]
        options.append(
            (LineString(points), onyx.north.longitudinal_grade(points, path[:, 2]))
        )

    def profile(east, north):
        point = Point(east, north)
        _, f = min(options, key=lambda row: row[0].distance(point))
        z = f(east, north)
        distance = entry.distance(point)
        if distance < 1.5:
            blend = 1.0 - distance / 1.5
            original = site.ground_height(field, east, north) + 0.105
            return z * (1 - blend) + original * blend
        distance = prior.distance(point)
        if distance < 0.55:
            blend = 1 - distance / 0.55
            return z * (1 - blend) + spec["paths"][0]["stations"][0][2] * blend
        return z

    return profile


def plant_beds(spec, beds, field):
    curbs, soil, plants, trees = [], [], [], []
    for i, (shape, row) in enumerate(zip(beds, spec["beds"], strict=True)):
        z = row["top_z_m"]
        inside = shape.buffer(-0.12)
        perimeter = shape.exterior
        bottom = (
            min(
                site.ground_height(field, *perimeter.interpolate(s).coords[0])
                for s in np.arange(0, perimeter.length, 0.40)
            )
            - 0.09
        )
        site.solid(curbs, shape.difference(inside), bottom, z, (153, 149, 131))
        site.solid(
            soil, inside, bottom, z - 0.065, (100, 107, 79) if i == 0 else (106, 99, 80)
        )
        if not i:
            continue
        west, south, east, north = inside.bounds
        for x in np.arange(west + 0.31, east, 0.79):
            for y in np.arange(south + 0.34, north, 0.83):
                if inside.buffer(-0.17).covers(Point(x, y)):
                    offset = z - 0.068 - site.ground_height(field, x, y)
                    onyx.planting.planted_crown(
                        plants, field, x, y, 0.28, 0.25, (x + y) * 1.2, base=offset
                    )
    for row in spec["trees"]:
        east, north = row["position_enu_m"]
        plant = next(
            i for i, shape in enumerate(beds) if shape.covers(Point(east, north))
        )
        base = spec["beds"][plant]["top_z_m"] - 0.065
        height, radius = row["height_m"], row["crown_radius_m"]
        site.cylinder_between(
            trees,
            (east, north, base),
            (east, north, base + height * 0.82),
            row["trunk_radius_m"],
            (92, 75, 58),
        )
        for x, y, z, scale, tint in [
            (-0.23, 0.24, 0.65, 0.69, (93, 116, 79)),
            (0.26, -0.17, 0.76, 0.66, (105, 124, 83)),
            (0.02, 0.06, 0.9, 0.48, (115, 133, 94)),
        ]:
            site.orb(
                trees,
                (east + x * radius, north + y * radius, base + z * height),
                (radius * scale, radius * scale, height * 0.16),
                tint,
            )
    return curbs, soil, plants, trees


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(METADATA / "onyx-bridge-underpass.json")
    for key, digest in spec["pins"].items():
        assert site.pin(site.scene / key / "site.json") == digest, key
    prior_desc = site.read(site.scene / onyx.PACKAGE / "site.json")
    rows = onyx.route_records(spec)
    known = {
        tuple(p)
        for r in prior_desc["walkable_ground"]["paths"]
        for p in onyx.north.stations(r)
    }
    for r in rows:
        assert tuple(r["anchor_enu_m"]) in known
        assert not known.intersection(map(tuple, r["points_enu_m"]))
        if "end_enu_m" in r:
            assert tuple(r["end_enu_m"]) in known
        known.update(map(tuple, r["points_enu_m"]))
    paving, beds, obstacles, prior, entry = layout(spec)
    blockers = [box(*shape.bounds) for shape in beds]
    covered = paving.union(prior).union(entry)
    lines = [LineString(onyx.path_points(row)) for row in spec["paths"]]
    solid = unary_union([*blockers, obstacles])
    for line in lines:
        assert line.difference(covered.buffer(0.065)).length < 0.01, line.wkt
        assert line.distance(solid) > 0.59, (line.distance(solid), line.wkt)
    _, field, _ = onyx.street.pinned_site(
        site.scene, site.read(METADATA / "east-thirteenth-east.json")
    )
    profile = grade(spec, field, prior, entry)
    ground, edges = [], []
    onyx.south.pave(ground, edges, paving, profile, field, (156, 151, 140))
    margin = paving.buffer(1.08).difference(
        paving.union(prior).union(entry).union(solid)
    )

    def margin_z(east, north):
        base = site.ground_height(field, east, north) + 0.035
        share = max(0.0, 1.0 - paving.distance(Point(east, north)) / 1.08)
        return base * (1 - share) + (profile(east, north) - 0.014) * share

    site.landscape.top_surface(ground, margin, margin_z, (109, 113, 93), cell=0.49)
    curbs, beds_mesh, plants, trees = plant_beds(spec, beds, field)
    args.stage.mkdir(parents=True, exist_ok=True)
    glb = args.stage / "site.glb"
    desc = args.stage / "site.json"
    faces = site.export(
        glb,
        (GROUND, ground, "landscape-surface"),
        ("onyx-bridge-walk-edges", edges, "landscape-detail"),
        ("onyx-bridge-garden-curbs", curbs, "landscape-detail"),
        ("onyx-bridge-garden-soil", beds_mesh, "landscape-vegetation"),
        ("onyx-bridge-understory", plants, "landscape-vegetation"),
        ("onyx-bridge-inventory-trees", trees, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    source = (
        "source_presentation_sha256",
        "source_base_model_sha256",
        "source_heightfield_sha256",
        "source_navigation_sha256",
    )
    site.fairmount.write_json(
        desc,
        {
            **{key: prior_desc[key] for key in source},
            "prerequisite_site_sha256": spec["pins"][onyx.PACKAGE],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(glb),
            "buildings": [],
            "closed_site_boxes_enu_m": [shape.bounds for shape in blockers],
            "walkable_ground": {"bounds_enu_m": [paving.bounds], "paths": rows},
        },
        compact=True,
    )
    stats = dict(
        paving_m2=round(paving.area, 3),
        shoulder_m2=round(margin.area, 3),
        beds_m2=round(sum(b.area for b in beds), 3),
        bridge_length_m=round(
            lines[0].intersection(box(-219, 117.2, -196, 132.2)).length, 3
        ),
        route_lengths_m=[round(line.length, 3) for line in lines],
        navigation_edges=sum(len(onyx.north.stations(row)) - 1 for row in rows),
        minimum_clearance_m=round(min(line.distance(solid) for line in lines), 3),
        faces=faces,
        asset_sha256=site.pin(glb),
        descriptor_sha256=site.pin(desc),
    )
    site.fairmount.write_json(args.audit, stats)
    print(stats)


if __name__ == "__main__":
    main()
