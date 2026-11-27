# SPDX-License-Identifier: Apache-2.0
"""Rebuild the Walnut Path crossing and return its legacy roof range to history."""

import argparse
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import trimesh

shared = import_module("build-bardell-buckingham-review")
fairmount, garden, hilyard = shared.fairmount, shared.garden, shared.hilyard
geometry = fairmount.geometry
PACKAGE = "walnut-path-bridge-review"
GROUND = "walnut-path-detail"
WALK = "walnut-path-walkable"


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def rounded(values):
    return [round(float(x), 6) for x in values]


def bridge_mesh(spec, field, parts, deck):
    span = spec["alignment"]
    a, b = np.asarray(span["north_enu_m"]), np.asarray(span["south_enu_m"])
    distance = float(np.linalg.norm(b - a))
    along = (b - a) / distance
    cross = np.array([-along[1], along[0]])
    z = span["deck_height_m"]
    width = span["width_m"] / 2
    tread, rail = span["stone_color"], span["rail_color"]

    def quad(lo, hi, left, right):
        return orient(
            Polygon(
                [
                    a + s * along + t * cross
                    for s, t in ((lo, left), (hi, left), (hi, right), (lo, right))
                ]
            )
        )

    def surface(lo, hi, narrow, wide, begin, end):
        shape = orient(
            Polygon(
                [
                    a + lo * along - narrow * cross,
                    a + hi * along - wide * cross,
                    a + hi * along + wide * cross,
                    a + lo * along + narrow * cross,
                ]
            )
        )

        def top(e, n):
            d = (np.array([e, n]) - a) @ along
            return np.interp(d, (lo, hi), (begin, end))

        low = min(begin, end) - 0.32
        block = geometry.shell(shape, low, top, (155, 153, 131), tread)
        block.update_faces(block.face_normals[:, 1] > 0.5)
        block.remove_unreferenced_vertices()
        deck.append(block)
        parts.append(
            geometry.shell(
                shape,
                min(
                    low,
                    min(hilyard.grade(field, p) for p in shape.exterior.coords) - 0.09,
                ),
                lambda e, n: top(e, n) - 0.025,
                (149, 146, 129),
                tread,
            )
        )
        return shape

    deck_plan = quad(0, distance, -width, width)
    slab = geometry.shell(deck_plan, z - 0.43, lambda *_: z, (147, 146, 129), tread)
    is_top = slab.face_normals[:, 1] > 0.5
    cap = slab.copy()
    cap.update_faces(is_top)
    cap.remove_unreferenced_vertices()
    deck.append(cap)
    slab.update_faces(~is_top)
    slab.remove_unreferenced_vertices()
    parts.append(slab)
    walks = [deck_plan]
    for side in (-1, 1):
        run = span["north_ramp_m"] if side < 0 else span["south_ramp_m"]
        bank = a if side < 0 else b
        stop = bank + side * along * run
        average = (
            max(hilyard.grade(field, stop + t * cross) for t in (-1.55, 0, 1.55))
            + 0.047
        )
        tip = max(z - 0.12, average + 0.30)
        if side < 0:
            walks.extend(
                [
                    surface(-run, -0.5 * run, 1.55, 2.66, average, tip),
                    surface(-0.5 * run, 0, 2.66, width, tip, z),
                ]
            )
        else:
            walks.extend(
                [
                    surface(distance, distance + 0.5 * run, width, 2.66, z, tip),
                    surface(
                        distance + 0.5 * run, distance + run, 2.66, 1.55, tip, average
                    ),
                ]
            )
        support = (
            quad(-0.6, 1.4, -width - 0.14, width + 0.14)
            if side < 0
            else quad(distance - 1.4, distance + 0.6, -width - 0.14, width + 0.14)
        )
        floor = min(hilyard.grade(field, p) for p in support.exterior.coords) - 0.20
        parts.append(
            geometry.shell(
                support, floor, lambda *_: z - 0.20, (147, 146, 130), (164, 161, 141)
            )
        )
    boxes = []
    for side in (-1, 1):
        edge = side * (width - 0.13)
        for level, half in ((z + 0.26, 0.034), (z + 0.70, 0.036), (z + 1.10, 0.045)):
            band = quad(0.02, distance - 0.02, edge - half, edge + half)
            parts.append(
                geometry.shell(
                    band, level - 0.035, lambda *_: level + 0.026, rail, rail
                )
            )
        for station in np.linspace(0.30, distance - 0.30, 19):
            pier = quad(station - 0.05, station + 0.05, edge - 0.048, edge + 0.048)
            parts.append(
                geometry.shell(pier, z - 0.055, lambda *_: z + 1.12, rail, rail)
            )
        for lo, hi in zip(
            np.linspace(0, distance, 9)[:-1], np.linspace(0, distance, 9)[1:]
        ):
            boxes.append(rounded(quad(lo, hi, edge - 0.055, edge + 0.055).bounds))
    return walks, boxes


def trail(parts, walks, path, field, width):
    keep = unary_union(walks)
    route = LineString([path["anchor_enu_m"], *path["points_enu_m"]])
    points = list(route.coords)

    def top(e, n):
        return hilyard.grade(field, (e, n)) + 0.051

    for a, b in zip(points[:-1], points[1:]):
        hydro = LineString([a, b]).buffer(width / 2, cap_style="flat").difference(keep)
        for strip in geometry.sections(hydro):
            if strip.area > 0.05:
                low = min(top(*p) for p in strip.exterior.coords) - 0.10
                surface = geometry.shell(
                    orient(strip), low, top, (144, 143, 125), (169, 167, 147)
                )
                surface.update_faces(surface.face_normals[:, 1] > 0.02)
                surface.remove_unreferenced_vertices()
                parts.append(surface)
    return route


def export(args):
    src = fairmount.SCENE
    spec = read(fairmount.ROOT / f"data/metadata/{PACKAGE}.json")
    m_path = src / "manifest.json"
    manifest = read(m_path)
    field_path = src / manifest["heightfield_url"]
    field = read(field_path)
    config = read(src / "presentation.json")
    assert digest(m_path) == spec["source_manifest_sha256"]
    assert digest(field_path) == spec["source_heightfield_sha256"]
    assert digest(src / "navigation.json") == spec["source_navigation_sha256"]
    audit = read(fairmount.ROOT / "data/metadata/campus-expansion-audit.json")
    removals = garden.shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, audit
    )
    parts, deck = [], []
    walks, boxes = bridge_mesh(spec, field, parts, deck)
    path = spec["path"]
    route = trail(parts, walks, path, field, spec["alignment"]["trail_width_m"])
    exclusion = spec["legacy_scene_id"]
    assert all(
        route.distance(Polygon(row["footprint_enu_m"]).buffer(0)) > 0.53
        for row in manifest["buildings"]
        if row["id"] != exclusion
    )
    assert min(route.distance(box(*bound)) for bound in boxes) > 1.4
    assert route.distance(Point(spec["axis_enu_m"][0])) < 0.9
    assert route.distance(Point(spec["axis_enu_m"][1])) < 0.9
    coords = rounded(unary_union(walks).bounds)
    scene = trimesh.Scene()
    for name, group, kind in (
        (GROUND, parts, "landscape-detail"),
        (WALK, deck, "landscape-surface"),
    ):
        mesh = garden.science.ordered_mesh(trimesh.util.concatenate(group))
        mesh.metadata.update(asset_id=name, asset_kind=kind, context_haze_weight=0.38)
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    out = args.stage
    out.mkdir(parents=True, exist_ok=True)
    model = out / "site.glb"
    model.write_bytes(trimesh.exchange.gltf.export_glb(scene))
    data = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=spec["source_heightfield_sha256"],
        source_navigation_sha256=spec["source_navigation_sha256"],
        ground_node=GROUND,
        url=f"{PACKAGE}/site.glb",
        sha256=digest(model),
        buildings=[],
        absorbed_ids=[exclusion],
        batch_removals=removals,
        closed_site_boxes_enu_m=boxes,
        walkable_ground=dict(
            bounds_enu_m=[coords],
            anchor_enu_m=path["anchor_enu_m"],
            points_enu_m=path["points_enu_m"],
        ),
    )
    descriptor = out / "site.json"
    fairmount.write_json(descriptor, data, compact=True)
    print(
        f"Deck and slopes {unary_union(walks).area:.3f} m²; path {route.length:.3f} m; {len(boxes)} rail collision sections"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, type=Path)
    export(parser.parse_args())


if __name__ == "__main__":
    main()
