# SPDX-License-Identifier: Apache-2.0
"""Export the surveyed east court and its stair connection to Memorial Quad."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

green = import_module("build-southwest-campus-green")
site = green.site
PACKAGE = "plc-east-court-review"
GROUND = "plc-east-court-paving"
HOST = "plc-lokey-tykeson-review"
BUILDING = "roof-8f611273"
CONCRETE = (171, 167, 153)
STONE = (150, 144, 130)
PAVERS = (146, 126, 103)
SOIL = (112, 95, 72)


def predecessor():
    descriptor = site.read(site.scene / HOST / "site.json")
    return next(row for row in descriptor["buildings"] if row["id"] == BUILDING)


def stair_and_wall(spec):
    west, south, east, north = spec["stair"]["bounds_enu_m"]
    return box(west, south, east, north), box(west - 0.19, -138.34, west + 0.04, south)


def court_shapes(spec, building):
    blockers = unary_union(
        [
            Polygon(ring)
            for ring in [
                *building["ground_footprints_enu_m"],
                *building["support_collision_enu_m"],
            ]
        ]
    )
    beds = [box(*row["bounds_enu_m"]) for row in spec["beds"]]
    stairs, wall = stair_and_wall(spec)
    occupied = unary_union([blockers, *beds, wall])
    upper = Polygon(spec["upper_enu_m"]).difference(occupied)
    lower = Polygon(spec["outer_walk_enu_m"]).difference(occupied)
    return upper, lower, stairs, beds, wall, blockers


def paving_footprint(spec):
    upper, lower, stairs, _, _, _ = court_shapes(spec, predecessor())
    return unary_union([upper, lower, stairs])


def upper_elevation(field, spec, gates):
    def elevation(e, n):
        height = spec["upper_z_m"] + (-131.4 - n) * 0.003
        # Tie into the existing portal landings over the north shoulder.
        for gate in gates:
            east, _ = gate["position_enu_m"]
            weight = np.clip((n + 132.8) / 4.1, 0, 1) * np.clip(
                (4.8 - abs(e - east)) / 3.0, 0, 1
            )
            landing = max(
                gate["threshold_z_m"] - 0.018,
                site.ground_height(field, e, n) + 0.092,
            )
            height -= weight * max(0, height - landing)
        # The existing seat's support datum differs from the new terrace.
        bench = np.clip((2.10 - abs(e + 581)) / 1.36, 0, 1) * np.clip(
            (1.45 - abs(n + 131)) / 1.13, 0, 1
        )
        return float(height - bench * max(0, height - 4.71))

    return elevation


def tread_surfaces(parts, field, profile, spec):
    west, south, east, north = spec["stair"]["bounds_enu_m"]
    count = spec["stair"]["treads"]
    stations = np.linspace(west, east, count + 1)
    shell = site.landscape.geometry.shell
    for index, (a, b) in enumerate(zip(stations, stations[1:])):
        fraction = 1 - index / count

        def tread(e, n):
            low = site.ground_height(field, east, n) + 0.102
            return low + fraction * (profile(west, n) - low)

        # Small panels follow the existing north–south tilt across the flight.
        for y0, y1 in zip(
            np.linspace(south, north, 9)[:-1], np.linspace(south, north, 9)[1:]
        ):
            parts.append(shell(box(a, y0, b, y1), 3.78, tread, STONE, CONCRETE))


def render(spec, field, building):
    upper, lower, stairs, beds, wall, _ = court_shapes(spec, building)
    gates = [g for g in building["entrances"] if g["gate"].startswith("plc-court")]
    height = upper_elevation(field, spec, gates)
    inset = box(*spec["pavers_enu_m"]).intersection(upper)
    ground, details, plants = [], [], []
    top = site.landscape.top_surface
    top(ground, upper.difference(inset), height, CONCRETE, cell=0.72)
    top(ground, inset, height, PAVERS, cell=0.62)
    site.drape(ground, field, lower, CONCRETE, 0.102, 0.68)
    tread_surfaces(ground, field, height, spec)
    site.solid(details, wall, 4.0, spec["upper_z_m"] + 0.22, STONE)

    for bed in beds:
        inner = bed.buffer(-0.13, join_style="mitre")
        x, y = bed.centroid.coords[0]
        floor = height(x, y)
        site.solid(details, bed.difference(inner), floor - 0.12, floor + 0.17, STONE)
        site.solid(details, inner, floor - 0.07, floor + 0.09, SOIL)
    pedestal = spec["pedestal"]
    e, n = pedestal["center_enu_m"]
    floor = height(e, n) + 0.09
    base = Point(e, n).buffer(pedestal["radius_m"], quad_segs=10)
    assert beds[1].covers(base)
    site.solid(details, base, floor - 0.03, floor + pedestal["height_m"], (172, 164, 146))
    for bed in beds:
        west, south, east, north = bed.bounds
        for x in np.arange(west + 0.40, east - 0.26, 0.76):
            for y in np.arange(south + 0.40, north - 0.26, 0.74):
                if Point(x, y).distance(base) < 0.53:
                    continue
                z = height(x, y)
                site.orb(plants, (x, y, z + 0.24), (0.33, 0.31, 0.23), (96, 116, 73))
    for index, tree in enumerate(spec["trees"]):
        x, y = tree["position_enu_m"]
        assert any(bed.covers(Point(x, y)) for bed in beds)
        grove = []
        site.canopy(grove, field, tree, index)
        lift = height(x, y) + 0.09 - site.ground_height(field, x, y)
        for mesh in grove:
            mesh.apply_translation([0, lift, 0])
        plants.extend(grove)
    return ground, details, plants


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(site.root / "data/metadata/plc-east-court.json")
    _, field, _ = green.east.pinned_site(site.scene, spec)
    quad = site.scene / "paving-corridors-l2/surfaces.json"
    assert site.pin(quad) == spec["pins"]["quad"]
    building = predecessor()
    upper, lower, stairs, beds, wall, blockers = court_shapes(spec, building)
    paving = unary_union([upper, lower, stairs])
    obstacles = unary_union([*beds, wall, blockers])
    routes = spec["routes"]
    patch = site.read(quad)["quad_routes"]
    edges, lengths = green.west.check_routes(
        {"nodes_enu_m": patch["nodes"]}, routes, paving, obstacles
    )
    for route in routes:
        end = [route["end_enu_m"]] if "end_enu_m" in route else []
        line = LineString([route["anchor_enu_m"], *route["points_enu_m"], *end])
        assert line.difference(paving.buffer(0.13)).length < 0.001, line.wkt

    ground, details, plants = render(spec, field, building)
    args.stage.mkdir(parents=True, exist_ok=True)
    asset, descriptor = (args.stage / file for file in ("site.glb", "site.json"))
    faces = site.export(
        asset,
        (GROUND, ground, "landscape-surface"),
        ("plc-east-court-details", details, "landscape-detail"),
        ("plc-east-court-plants", plants, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    pins = spec["pins"]
    site.fairmount.write_json(
        descriptor,
        {
            "source_presentation_sha256": pins["presentation"],
            "source_base_model_sha256": pins["model"],
            "source_heightfield_sha256": pins["heightfield"],
            "source_navigation_sha256": pins["navigation"],
            "source_quad_sha256": pins["quad"],
            "prerequisite_site_sha256": pins["sites"][HOST],
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(asset),
            "ground_node": GROUND,
            "walkable_ground": {"bounds_enu_m": [spec["extent"]], "paths": routes},
            "closed_site_boxes_enu_m": [shape.bounds for shape in [*beds, wall]],
            "buildings": [],
        },
        compact=True,
    )
    audit = {
        "paving_m2": round(paving.area, 2),
        "beds_m2": round(sum(bed.area for bed in beds), 2),
        "pavers_m2": round(upper.intersection(box(*spec["pavers_enu_m"])).area, 2),
        "trees": [tree["id"] for tree in spec["trees"]],
        "stair_treads": spec["stair"]["treads"],
        "route_edges": edges,
        "route_lengths_m": lengths,
        "faces": faces,
        "asset_sha256": site.pin(asset),
        "descriptor_sha256": site.pin(descriptor),
    }
    site.fairmount.write_json(args.audit, audit)
    print(audit)


if __name__ == "__main__":
    main()
