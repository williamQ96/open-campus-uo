# SPDX-License-Identifier: Apache-2.0
"""Stage the full-extent ground asset with dated elevation and site grade ties."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import struct

import numpy as np
from PIL import Image
from pyproj import Transformer
from scipy.ndimage import distance_transform_edt, gaussian_filter, map_coordinates
from shapely import contains_xy, make_valid, prepare, union_all
from shapely.geometry import LineString, Polygon, box, shape
from shapely.ops import transform
import tifffile

RELEASE = Path(__file__).resolve().parents[1]
SCENE = RELEASE / "apps/web-preview/public/scene"


def read(path):
    return json.loads(path.read_bytes())


def digest(raw):
    return sha256(raw).hexdigest()


def terrain(path, east, north, expected):
    assert digest(path.read_bytes()) == expected
    with tifffile.TiffFile(path) as source:
        tags = source.geotiff_metadata
        assert tags["ProjectedCSTypeGeoKey"] == 3740
        i, j, _, west, top, _ = tags["ModelTiepoint"]
        step_x, step_y, _ = tags["ModelPixelScale"]
        col = i + (east - west) / step_x - 0.5
        row = j + (top - north) / step_y - 0.5
        raw = source.asarray()
        raw[raw == float(source.pages[0].tags[42113].value)] = np.nan
        return map_coordinates(raw, [row, col], order=1, cval=np.nan) * 0.3048


def smoothstep(value):
    t = np.clip(value, 0, 1)
    return t**2 * (3 - 2 * t)


def buffered_lines(lines, x, y, padding):
    area = union_all(
        [LineString(points).buffer(width + padding) for points, width in lines]
    )
    prepare(area)
    return contains_xy(area, x, y)


def protected_vertices(grade_ties, field, x, y):
    spacing = field["spacing_m"]
    diagonal = spacing * np.sqrt(2)
    footprints = union_all(
        [
            make_valid(Polygon(record["footprint_enu_m"]))
            for record in grade_ties["buildings"]
        ]
    )
    building_ties = contains_xy(footprints.buffer(diagonal + 3), x, y)
    points = [
        ([[e, -s] for e, s in (item["position"], item["approach"])], 2.5)
        for item in grade_ties["entrances"]
    ]
    entrance_ties = buffered_lines(points, x, y, diagonal)
    graph = read(SCENE / "navigation.json")
    nodes = graph["nodes_enu_m"]
    corridor_ties = buffered_lines(
        [([nodes[a], nodes[b]], 1.2) for a, b, *_ in graph["edges"]]
        + [
            (road["centerline_enu_m"], road["width_m"] / 2)
            for road in grade_ties["roads"]
        ],
        x,
        y,
        diagonal,
    )
    support_ties = np.zeros(x.shape, bool)
    for key, coords in grade_ties["layers"].items():
        touched = np.zeros(x.size, bool)
        touched[coords] = True
        limit = 13 if key == "landscape-surface" else 11
        support_ties |= (
            distance_transform_edt(~touched.reshape(x.shape)) * spacing <= limit
        )
    ford = read(SCENE / "ford-arena-review/site.json")["grade"]
    left = x.min() + ford["column"] * spacing
    bottom = y.min() + ford["row"] * spacing
    right = left + (len(ford["deltas_m"][0]) - 1) * spacing
    top = bottom + (len(ford["deltas_m"]) - 1) * spacing
    ford_ties = contains_xy(box(left, bottom, right, top).buffer(diagonal), x, y)
    edge = (
        (x < x.min() + spacing)
        | (x > x.max() - spacing)
        | (y < y.min() + spacing)
        | (y > y.max() - spacing)
    )
    masks = {
        "buildings": building_ties,
        "entrances": entrance_ties,
        "corridors": corridor_ties,
        "surface_meshes": support_ties,
        "ford_arena": ford_ties,
        "scene_edge": edge,
    }
    return np.logical_or.reduce(list(masks.values())), masks, len(graph["edges"])


def water_area(inputs, origin, x, y):
    project = Transformer.from_crs(4326, 3740, always_xy=True)

    def project_local(lon, lat, _alt=None):
        east, north = project.transform(lon, lat)
        return east - origin[0], north - origin[1]

    mapped = []
    extent = box(x.min(), y.min(), x.max(), y.max())
    for source in read(inputs / "hydrography-sources.json"):
        raw = (inputs / source["file"]).read_bytes()
        assert digest(raw) == source["sha256"]
        mapped.extend(
            make_valid(
                transform(project_local, shape(record["geometry"]))
            ).intersection(extent)
            for record in json.loads(raw)["features"]
        )
    return union_all(mapped)


def terrestrial_palette(x, y, origin, water, building_ties):
    ref = read(RELEASE / "data/metadata/naip-2024-main-campus-reference.json")
    source = RELEASE / "data/reference-images" / ref["archive_file"]
    assert digest(source.read_bytes()) == ref["sha256"]
    with Image.open(source) as view:
        aerial = np.asarray(view.convert("RGB"), dtype=np.float32) / 255
    bounds = ref["export_response"]["extent"]
    col = (x + origin[0] - bounds["xmin"]) / (
        bounds["xmax"] - bounds["xmin"]
    ) * aerial.shape[1] - 0.5
    row = (bounds["ymax"] - y - origin[1]) / (
        bounds["ymax"] - bounds["ymin"]
    ) * aerial.shape[0] - 0.5
    red, green, blue = [
        map_coordinates(
            gaussian_filter(aerial[:, :, i], 2.4), [row, col], order=1, mode="nearest"
        )
        for i in range(3)
    ]
    # Original palette uses imagery only to estimate vegetation and light pavement weights.
    green_score = (2 * green - red - blue) / (red + green + blue + 0.035)
    vegetation = smoothstep((green_score - 0.017) / 0.096)
    vegetation[building_ties] *= 0.24
    brightness = (red + green + blue) / 3
    light_gray = (0.52, 0.52, 0.48)
    dark_gray = (0.33, 0.36, 0.35)
    meadow = (0.55, 0.67, 0.43)
    grove = (0.37, 0.51, 0.34)

    def blend(a, b, factor):
        return np.asarray(a) + (np.asarray(b) - a) * factor[:, :, None]

    stone = blend(dark_gray, light_gray, smoothstep((brightness - 0.19) / 0.40))
    plants = blend(grove, meadow, smoothstep((brightness - 0.12) / 0.32))
    colors = blend(stone, plants, vegetation)
    # Water vertices follow mapped shorelines. Blend shades inside the bank to show shallow edges.
    bank = distance_transform_edt(water) * (x[0, 1] - x[0, 0])
    water_colors = blend(
        (0.38, 0.58, 0.55), (0.26, 0.45, 0.46), smoothstep((bank - 4) / 56)
    )
    colors[water] = water_colors[water]
    return colors


def stage_glb(original, heights, colors):
    size = struct.unpack_from("<I", original, offset=12)[0]
    gltf = json.loads(original[20 : 20 + size])
    buffer = bytearray(original[28 + size :])
    mesh = gltf["meshes"][0]["primitives"][0]

    def read_attr(index, dtype):
        data = gltf["accessors"][index]
        view = gltf["bufferViews"][data["bufferView"]]
        columns = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[data["type"]]
        assert "byteStride" not in view
        return np.frombuffer(
            buffer,
            dtype,
            count=data["count"] * columns,
            offset=view.get("byteOffset", 0) + data.get("byteOffset", 0),
        ).reshape(-1, columns)

    positions_index = mesh["attributes"]["POSITION"]
    positions = read_attr(positions_index, "<f4")
    positions[:, 1] = heights.ravel() + 0.018
    accessor = gltf["accessors"][positions_index]
    accessor["min"] = positions.min(axis=0).astype(float).tolist()
    accessor["max"] = positions.max(axis=0).astype(float).tolist()
    inds = read_attr(mesh["indices"], "<u4").reshape(-1, 3)
    triangles = positions[inds]
    face_normals = np.cross(
        triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]
    )
    averaged = np.zeros_like(positions)
    for side in range(3):
        np.add.at(averaged, inds[:, side], face_normals)
    read_attr(mesh["attributes"]["NORMAL"], "<f4")[:] = (
        averaged / np.linalg.norm(averaged, axis=1)[:, None]
    )
    linear = np.where(
        colors <= 0.04045, colors / 12.92, ((colors + 0.055) / 1.055) ** 2.4
    )
    read_attr(mesh["attributes"]["COLOR_0"], "<f4")[:, :3] = linear.reshape(-1, 3)
    node = next(node for node in gltf["nodes"] if "mesh" in node)
    node["name"] = "Eugene terrain and land cover L2"
    node["extras"].update(
        {
            "surface_grain": 0.075,
            "status": "Dated terrain, mapped water and original land cover palette",
        }
    )
    json_bytes = json.dumps(gltf, separators=(",", ":")).encode()
    json_bytes += b" " * (-len(json_bytes) % 4)
    return (
        struct.pack("<4sII", b"glTF", 2, 28 + len(json_bytes) + len(buffer))
        + struct.pack("<I4s", len(json_bytes), b"JSON")
        + json_bytes
        + struct.pack("<I4s", len(buffer), b"BIN\x00")
        + buffer
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--inputs",
        type=Path,
        required=True,
        help="Runtime tie capture and NHD source extracts",
    )
    parser.add_argument(
        "--terrain",
        type=Path,
        required=True,
        help="DOGAMI GeoTIFFs and their source manifest",
    )
    parser.add_argument(
        "--stage",
        type=Path,
        required=True,
        help="Output directory for the GLB and audit",
    )
    args = parser.parse_args()
    manifest = read(SCENE / "manifest.json")
    legacy = read(SCENE / "presentation.json")
    field_path = SCENE / manifest["heightfield_url"]
    field = read(field_path)
    origin = manifest["coordinate_frame"]["origin_projected_m"]
    x, y = np.meshgrid(
        field["min_east_m"] + field["spacing_m"] * np.arange(field["nx"]),
        field["min_north_m"] + field["spacing_m"] * np.arange(field["ny"]),
    )
    original = np.asarray(field["heights_m"]).reshape(x.shape)
    grade_ties = read(args.inputs / "grade-ties.json")
    fixed, masks, graphs = protected_vertices(grade_ties, field, x, y)
    mapped = water_area(args.inputs, origin, x, y)
    water = contains_xy(mapped, x, y)
    archived = read(args.terrain / "manifest.json")
    assert archived["current_heightfield_sha256"] == digest(field_path.read_bytes())
    sources = archived["files"]
    latest_name = "willamette-2023-south-terrain.tif"
    other_name = "lane-county-2014-terrain.tif"
    latest, older = [
        terrain(
            args.terrain / name, x + origin[0], y + origin[1], sources[name]["sha256"]
        )
        - origin[2]
        for name in (latest_name, other_name)
    ]
    overlap = np.isfinite(latest) & np.isfinite(older) & ~water
    latest_bias = float(np.median((latest - older)[overlap]))
    recent = np.isfinite(latest)
    # Transition source datasets over four cells. Ground elevations near existing models stay tied.
    recent_weight = smoothstep(distance_transform_edt(recent) / 4)
    corrected = np.where(np.isfinite(older), older + latest_bias, latest)
    combined = np.where(
        recent, latest * recent_weight + corrected * (1 - recent_weight), corrected
    )
    valid = np.isfinite(combined)
    clipped = np.clip(np.where(valid, combined - original, 0), -1.2, 1.2)
    smoothed = gaussian_filter(clipped, 0.85) / np.maximum(
        gaussian_filter(valid.astype(float), 0.85), 0.1
    )
    limit = smoothstep(distance_transform_edt(~fixed) * field["spacing_m"] / 25)
    delta = np.round(np.clip(smoothed, -1.2, 1.2) * limit, 4)
    assert np.all(delta[fixed] == 0)
    target = original + delta
    colors = terrestrial_palette(x, y, origin, water, masks["buildings"])
    raw = (SCENE / legacy["landcover_url"]).read_bytes()
    assert digest(raw) == legacy["landcover_sha256"]
    asset = stage_glb(raw, target, colors)
    args.stage.mkdir(parents=True, exist_ok=True)
    (args.stage / "landcover.glb").write_bytes(asset)
    assert len(colors.ravel()) == 160801 * 3
    measurable = ~fixed & recent
    evidence = {
        "sha256": digest(asset),
        "bytes": len(asset),
        "vertices": int(original.size),
        "affected_vertices": int(np.count_nonzero(delta)),
        "changed_at_least_0_1m": int((abs(delta) >= 0.1).sum()),
        "protected_vertices": int(fixed.sum()),
        "grade_ties": {name: int(mask.sum()) for name, mask in masks.items()},
        "building_footprints": len(grade_ties["buildings"]),
        "entrance_pairs": len(grade_ties["entrances"]),
        "road_features": len(grade_ties["roads"]),
        "also_protected_route_edges": graphs,
        "water_vertices": int(water.sum()),
        "water_area_m2": round(mapped.area, 4),
        "fallback_surface_tie_m": round(latest_bias, 4),
        "delta_range_m": [float(delta.min()), float(delta.max())],
        "max_delta_difference_adjacent_m": float(
            max(abs(np.diff(delta, axis=0)).max(), abs(np.diff(delta, axis=1)).max())
        ),
        "job_source_residual_median_m": [
            round(float(np.median(abs(layer[measurable] - latest[measurable]))), 4)
            for layer in (original, target)
        ],
    }
    (args.stage / "stage-audit.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf8"
    )
    np.savez_compressed(
        args.stage / "stage-grid.npz",
        delta=delta,
        fixed=fixed,
        water=water,
        colors=colors.astype(np.float32),
    )
    pixels = (colors[::-1].clip(0, 1) * 255).astype(np.uint8)
    Image.fromarray(pixels).save(args.stage / "staged-palette.png")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
