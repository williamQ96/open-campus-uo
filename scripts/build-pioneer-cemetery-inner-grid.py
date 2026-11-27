# SPDX-License-Identifier: Apache-2.0
"""Build screened interior plot edges, markers and exposed grass traces."""

import argparse
from hashlib import sha256
from importlib import import_module
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

cemetery = import_module("build-pioneer-cemetery-landscape-review")
PACKAGE = "pioneer-cemetery-inner-grid-review"
GROUND = "pioneer-inner-grid-grass"
DETAIL = "pioneer-inner-grid-stone"
PLANTS = "pioneer-inner-grid-shrubs"


def footprint(row):
    points = row["points_enu_m"]
    line = LineString([*points, points[0]] if row.get("closed") else points)
    return line.buffer(0.105, cap_style="flat", join_style="mitre")


def strip(row):
    return LineString(row["centerline_enu_m"]).buffer(
        row["width_m"] / 2, cap_style="flat"
    )


def tree_bases(base, metadata, source_sha):
    records = metadata / "context-trees-l2.json"
    assert sha256(records.read_text(encoding="utf-8").encode()).hexdigest() == source_sha
    dropped = {item["index"] for item in base["procedural_context_trees_to_remove"]}
    context = cemetery.read(records)["trees"]
    footprints = [
        Point(e, -south).buffer(min(0.29, 0.024 * row["standing_height_m"]))
        for row in context
        if row["index"] not in dropped
        for e, _, south in [row["origin_gltf_m"]]
    ]
    footprints.extend(
        Point(row["position_enu_m"]).buffer(0.071 * row["crown_radius_m"])
        for row in base["canopy_estimates"]
    )
    return unary_union(footprints)


def low_shrub(parts, field, row):
    e, n = row["position_enu_m"]
    sx, sn = row["spread_m"]
    height = row["height_m"]
    for i, (de, dn, scale) in enumerate(
        ((-0.25, -0.25, 0.73), (0.31, -0.16, 0.84), (0, 0, 1), (-0.18, 0.27, 0.81))
    ):
        x, y = e + de * sx, n + dn * sn
        z = cemetery.ground_height(field, x, y)
        color = ((96, 119, 73), (117, 133, 83), (102, 125, 77))[i % 3]
        cemetery.orb(
            parts, (x, y, z + height * scale * 0.57),
            (sx * 0.28, sn * 0.28, height * scale * 0.43),
            color,
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = cemetery.root / "data/metadata"
    scene = cemetery.scene
    spec = cemetery.read(metadata / "pioneer-cemetery-inner-grid.json")
    base = cemetery.read(metadata / f"{cemetery.PACKAGE}.json")
    descriptor_path = scene / cemetery.PACKAGE / "site.json"
    parent = cemetery.read(descriptor_path)
    manifest = cemetery.read(scene / "manifest.json")
    field_path = scene / manifest["heightfield_url"]
    pins = spec["pinned_sources"]
    assert cemetery.pin(descriptor_path) == spec["cemetery_descriptor_sha256"]
    assert cemetery.pin(scene / parent["url"]) == parent["sha256"]
    assert cemetery.pin(field_path) == pins["heightfield"]
    assert parent["source_presentation_sha256"] == pins["presentation"]
    assert manifest["model"]["sha256"] == pins["campus"]
    field = cemetery.read(field_path)

    detail, ground, plants = [], [], []
    parcel = Polygon(base["parcel"]["outline_enu_m"])
    main_paths = unary_union(cemetery.named_path_footprints(base))
    stems = tree_bases(base, metadata, spec["source_context_tree_metadata_sha256"])
    prior_sections = (base, base["perimeter_refinement"], base["northwest_refinement"])
    old_edges = unary_union(
        [footprint(row) for section in prior_sections for row in section["grave_plot_edges"]]
    )
    old_markers = [
        Point(row["position_enu_m"])
        for section in prior_sections
        for row in section["marker_estimates"]
    ]
    curbs = []
    for row in spec["curbs"]:
        line = LineString(row["points_enu_m"])
        shape = footprint(row)
        assert parcel.covers(shape) and main_paths.distance(shape) > 0.8, row["id"]
        assert all(shape.distance(o) > 0.22 for o in [old_edges, *curbs]), row["id"]
        assert all(shape.distance(o) > 0.38 for o in old_markers), row["id"]
        assert stems.distance(shape) > 0.07, row["id"]
        curbs.append(shape)
        cemetery.plot_curb(detail, field, line, (153, 146, 130))
    all_edges = unary_union([old_edges, *curbs])
    available = unary_union(
        [
            strip(base["northwest_refinement"]["short_grass_track"]),
            *(strip(row) for row in base["inner_alleys"]),
        ]
    )
    tracks = []
    for row in spec["tracks"]:
        trace = strip(row).difference(available)
        assert parcel.covers(trace) and main_paths.distance(trace) > 0.65, row["id"]
        assert all_edges.distance(trace) > 0.18, row["id"]
        assert stems.distance(trace) > 0.07, row["id"]
        cemetery.drape(ground, field, trace, (152, 154, 112), 0.079, 0.84)
        tracks.append(trace)
    trails = unary_union(tracks)

    obstacles, centers = [], list(old_markers)
    for i, row in enumerate(spec["markers"]):
        e, n = row["position_enu_m"]
        center = Point(e, n)
        width = row["width_m"] * 0.58
        depth = max(row["depth_m"] * 0.55, row["width_m"] * 0.5)
        # The model base is wider east–west, and the upright slab spans north–south.
        bounds = box(e - width, n - depth, e + width, n + depth)
        assert parcel.covers(bounds) and main_paths.distance(bounds) > 0.6, row["id"]
        assert all(center.distance(o) > 0.82 for o in centers), row["id"]
        assert all_edges.distance(bounds) > 0.002 and trails.distance(bounds) > 0.21, row["id"]
        assert stems.distance(bounds) > 0.07, row["id"]
        cemetery.marker(detail, field, row, len(old_markers) + i)
        centers.append(center)
        if row["height_m"] >= 0.9:
            obstacles.append(bounds.bounds)
    for row in spec["low_shrubs"]:
        center = Point(row["position_enu_m"])
        assert main_paths.distance(center) > 2.0 and trails.distance(center) > 0.7
        assert stems.distance(center) > 1.2
        low_shrub(plants, field, row)

    args.stage.mkdir(parents=True, exist_ok=True)
    asset, descriptor = (args.stage / file for file in ("site.glb", "site.json"))
    faces = cemetery.export(
        asset,
        (GROUND, ground, "landscape-surface"),
        (DETAIL, detail, "landscape-detail"),
        (PLANTS, plants, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    asset_sha = cemetery.pin(asset)
    cemetery.fairmount.write_json(
        descriptor,
        {
            "source_presentation_sha256": pins["presentation"],
            "source_base_model_sha256": pins["campus"],
            "source_heightfield_sha256": pins["heightfield"],
            "prerequisite_site_sha256": spec["cemetery_descriptor_sha256"],
            "url": f"{PACKAGE}/site.glb",
            "ground_node": GROUND,
            "sha256": asset_sha,
            "buildings": [],
            "closed_site_boxes_enu_m": obstacles,
        },
        compact=True,
    )
    report = {
        "curb_traces": len(curbs),
        "curb_length_m": round(sum(LineString(x["points_enu_m"]).length for x in spec["curbs"]), 2),
        "markers": len(spec["markers"]),
        "tracks": len(tracks),
        "track_length_m": round(sum(LineString(x["centerline_enu_m"]).length for x in spec["tracks"]), 2),
        "track_area_m2": round(sum(track.area for track in tracks), 2),
        "shrubs": len(spec["low_shrubs"]),
        "collisions": len(obstacles),
        "faces": faces,
        "asset_sha256": asset_sha,
        "descriptor_sha256": cemetery.pin(descriptor),
    }
    cemetery.fairmount.write_json(args.audit, report)
    print(report)


if __name__ == "__main__":
    main()
