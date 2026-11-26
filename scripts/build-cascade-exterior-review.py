# SPDX-License-Identifier: Apache-2.0
"""Export the original local Cascade Hall review model and its placement audit."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "apps/web-preview/public/scene"
SPEC = ROOT / "data/metadata/cascade-exterior-review.json"
OUTPUT = ROOT / "assets/exterior-refinement/cascade-hall-massing-review-2026-11-23.glb"
BRICK = (124, 80, 67)
STONE = (177, 164, 148)
METAL = (155, 158, 151)
FLAT_ROOF = (188, 185, 174)
DARK_GLASS = (59, 77, 82)


def shell(outline, bottom, top, wall_color, roof_color):
    """Make one closed prism whose roof is planar within its supplied outline."""
    outline = orient(outline)
    vertices, colors = [], []

    def triangle(points, heights, color):
        vertices.extend((e, z, -n) for (e, n), z in zip(points, heights))
        colors.extend([color] * 3)

    for item in shapely.constrained_delaunay_triangles(outline).geoms:
        corners = list(orient(item).exterior.coords)[:3]
        triangle(corners, [top(*p) for p in corners], roof_color)
        triangle(corners[::-1], [bottom] * 3, wall_color)
    for ring in (outline.exterior, *outline.interiors):
        for a, b in zip(ring.coords, list(ring.coords)[1:]):
            triangle((a, b, b), (bottom, bottom, top(*b)), wall_color)
            triangle((a, b, a), (bottom, top(*b), top(*a)), wall_color)
    vertex_array = np.asarray(vertices)
    faces = np.arange(len(vertices)).reshape(-1, 3)
    check = trimesh.Trimesh(vertex_array, faces, process=True)
    if not check.is_volume:
        raise ValueError("Invalid closed Cascade mesh section")
    mesh = trimesh.Trimesh(vertex_array, faces, process=False)
    mesh.visual.vertex_colors = np.column_stack([np.asarray(colors), np.full(len(vertices), 255)])
    return mesh


def sections(region):
    return [
        item for item in shapely.get_parts(region)
        if item.geom_type == "Polygon" and item.area > 1e-5
    ]


def structure(spec, outline, field):
    base = spec["footing_z_m"]
    flat = spec["main_roof_z_m"]
    south = spec["south_roof"]
    cut = south["north_break_m"]
    south_plan = outline.intersection(box(-300, 70, -210, cut))
    upper_plan = outline.difference(south_plan)
    pieces = []

    def south_height(e, n):
        return south["eave_z_m"] + (n - south["eave_north_m"]) * south["rise_per_m"]

    def add(region, lower, upper, wall=BRICK, roof=METAL):
        for p in sections(region):
            pieces.append(shell(p, lower, upper, wall, roof))

    add(south_plan, base, south_height)
    add(upper_plan, base, lambda e, n: flat, roof=FLAT_ROOF)

    # LiDAR resolves pitched perimeter strips around the flat central roof.
    for name, parallel_north in (("north", False), ("east", True), ("west", True)):
        slope = spec[f"{name}_roof"]
        ridge = slope["ridge_east_m" if parallel_north else "ridge_north_m"]
        half = slope["half_width_m"]
        span = (84.45, 102.0) if name == "east" else (88.1, 102.0)
        for left, right in ((ridge - half, ridge), (ridge, ridge + half)):
            strip = box(left, span[0], right, span[1]) if parallel_north else box(-247.0, left, -218.28, right)

            def height(e, n):
                offset = abs((e if parallel_north else n) - ridge)
                return flat + (slope["ridge_z_m"] - flat) * (1 - offset / half)

            add(upper_plan.intersection(strip), flat - 0.012, height, METAL, METAL)

    for left, right, low, high, peak in spec["south_gables"]:
        middle = (left + right) / 2
        for lo, hi in ((left, middle), (middle, right)):
            body = box(lo, low, hi, high)

            def gable(e, n):
                side = 1 - abs(e - middle) / ((right - left) / 2)
                return max(south_height(e, n) + 0.09, south_height(e, low) + (peak - south_height(e, low)) * side)

            add(body.intersection(south_plan), south_height(0, low) - 0.08, gable, STONE)

    for e, n, width, depth, z in spec["roof_monitors"]:
        top = box(e - width / 2, n - depth / 2, e + width / 2, n + depth / 2)
        add(top.intersection(upper_plan), flat - 0.04, lambda e, n: z, STONE)

    tower = orient(Polygon(spec["tower_enu_m"]))
    if not outline.buffer(0.01).covers(tower):
        raise ValueError("Tower plan should sit inside the main model envelope")
    eave, peak = spec["tower_eave_z_m"], spec["tower_peak_z_m"]
    add(tower, base + 0.04, lambda e, n: eave)
    apex = tuple(tower.centroid.coords)[0]
    for a, b in zip(tower.exterior.coords, list(tower.exterior.coords)[1:]):
        facet = Polygon([a, b, apex])
        add(facet, eave - 0.012, lambda e, n: peak if (e, n) == apex else eave + 0.02, METAL, METAL)

    # Stone belt courses follow the material divisions visible in the courtyard photos.
    ring = list(orient(outline).exterior.coords)
    wall_edges = [LineString([a, b]) for a, b in zip(ring, ring[1:])]
    for edge in wall_edges:
        if edge.length < 2.3 or edge.distance(tower) < 0.28:
            continue
        a, b = edge.coords
        trim = edge.buffer(0.085, cap_style="flat").difference(outline.buffer(-0.02))
        for z in (2.95, 6.5, 10.25):
            if z < min(south_height(*a), south_height(*b)) - 0.28 or min(a[1], b[1]) > cut:
                add(trim, z, lambda e, n: z + 0.16, STONE, STONE)

    def opening(e, n, width, lower, upper, door=False):
        point = Point(e, n)
        edge = min(wall_edges, key=point.distance)
        if edge.distance(point) > 0.002:
            raise ValueError("Cascade opening must lie on the authored wall line")
        center = edge.project(point)
        left = edge.interpolate(center - width / 2)
        right = edge.interpolate(center + width / 2)
        segment = LineString([left, right])
        frame = segment.buffer(0.095, cap_style="square").difference(outline.buffer(-0.015))
        inside = LineString([segment.interpolate(0.075), segment.interpolate(width - 0.075)])
        glazing = inside.buffer(0.108, cap_style="flat").difference(outline.buffer(-0.013))
        add(frame, lower, lambda e, n: upper, STONE, STONE)
        add(glazing, lower + 0.095, lambda e, n: upper - 0.095, DARK_GLASS, DARK_GLASS)
        stile = LineString([edge.interpolate(center - 0.027), edge.interpolate(center + 0.027)])
        divider = stile.buffer(0.132, cap_style="flat").difference(outline.buffer(-0.02))
        add(divider, lower + 0.10, lambda e, n: upper - 0.10, BRICK, BRICK)
        if door:
            transom = segment.buffer(0.12, cap_style="flat").difference(outline.buffer(-0.02))
            add(transom, upper - 0.55, lambda e, n: upper - 0.47, BRICK, BRICK)

    for floor, lower, upper in (("first", 3.35, 5.45), ("second", 6.95, 9.25)):
        for e, n, width in spec["openings"][f"{floor}_windows_enu_m"]:
            opening(e, n, width, lower, upper)
    e, n, width = spec["openings"]["south_door_enu_m"]
    door_base = sample_ground(field, e, n - 0.2) + 0.045
    opening(e, n, width, door_base, door_base + 2.82, door=True)

    tower_ring = list(tower.exterior.coords)
    for index in (2, 3, 4, 5):
        a, b = tower_ring[index:index + 2]
        edge = LineString([a, b])
        pane = LineString([edge.interpolate(0.23, normalized=True), edge.interpolate(0.77, normalized=True)])
        projection = pane.buffer(0.048, cap_style="flat").difference(tower.buffer(-0.015))
        add(projection, 15.2, lambda e, n: 19.85, DARK_GLASS, DARK_GLASS)
        for z in (16.7, 18.25):
            add(projection.buffer(0.019), z, lambda e, n: z + 0.09, BRICK, BRICK)

    return trimesh.util.concatenate(pieces)


def sample_ground(field, e, n):
    u = (e - field["min_east_m"]) / field["spacing_m"]
    v = (n - field["min_north_m"]) / field["spacing_m"]
    i, j = int(u), int(v)
    a, b = u - i, v - j
    heights = field["heights_m"]
    index = j * field["nx"] + i
    h00, h10 = heights[index:index + 2]
    h01, h11 = heights[index + field["nx"]:index + field["nx"] + 2]
    if a >= b:
        return h00 + (h10 - h00) * a + (h11 - h10) * b
    return h00 + (h11 - h01) * a + (h01 - h00) * b


def placement(manifest, field, outline, previous, spec):
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    nodes = graph["nodes_enu_m"]
    edges = [LineString([nodes[a], nodes[b]]) for a, b, *_ in graph["edges"]]
    perimeter = outline.exterior
    locations = [perimeter.interpolate(m) for m in np.arange(0, perimeter.length, 0.25)]
    covers = [sample_ground(field, p.x, p.y) - spec["footing_z_m"] for p in locations]
    neighbors = []
    e, n, _ = spec["openings"]["south_door_enu_m"]
    courtyard = Point(-246.5, 69.5)
    approach = LineString([courtyard, (e, n - 0.55)])
    for record in manifest["buildings"]:
        if record["id"] == previous["id"]:
            continue
        polygon = Polygon(record["footprint_enu_m"]).buffer(0)
        gap = polygon.distance(outline)
        if gap < 12:
            neighbors.append({"id": record["id"], "name": record.get("name"), "gap_m": round(gap, 3),
                              "overlap_m2": round(polygon.intersection(outline).area, 3),
                              "straight_courtyard_approach_gap_m": round(polygon.distance(approach), 3)})
    old_buffer, new_buffer = previous["polygon"].buffer(0.42), outline.buffer(0.42)
    route_conflicts = [index for index, edge in enumerate(edges) if edge.intersects(new_buffer) and not edge.intersects(old_buffer)]
    return {"perimeter_sample_count": len(covers), "runtime_ground_cover_min_m": round(min(covers), 3),
            "runtime_ground_cover_max_m": round(max(covers), 3), "neighbors_within_12m": sorted(neighbors, key=lambda n: n["gap_m"]),
            "min_navigation_gap_m": round(min(outline.distance(edge) for edge in edges), 3),
            "new_navigation_conflicts_at_player_radius": route_conflicts,
            "courtyard_control_outside": not outline.covers(courtyard),
            "approach_ground_z_m": round(sample_ground(field, e, n - 0.2), 3)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path, help="Output JSON for placement and reimport evidence")
    args = parser.parse_args()
    spec_data = SPEC.read_bytes()
    spec = json.loads(spec_data)
    manifest_data = (SCENE / "manifest.json").read_bytes()
    if sha256(manifest_data).hexdigest() != spec["scene_manifest_sha256"]:
        raise ValueError("Scene manifest changed; recheck Cascade model placement")
    manifest = json.loads(manifest_data)
    field_data = (SCENE / manifest["heightfield_url"]).read_bytes()
    field = json.loads(field_data)
    old = next(b for b in manifest["buildings"] if b["id"] == spec["asset_id"])
    previous = {**old, "polygon": Polygon(old["footprint_enu_m"]).buffer(0)}
    outline = Polygon(spec["walls_enu_m"])
    assert outline.is_valid and outline.area > 1000
    mesh = structure(spec, outline, field)
    scene = trimesh.Scene()
    scene.add_geometry(mesh, node_name=spec["asset_id"], geom_name="Cascade Hall exterior review")

    def mark(document):
        document["asset"]["copyright"] = "Open Campus contributors. Original model CC BY 4.0."
        document["materials"] = [{"pbrMetallicRoughness": {"metallicFactor": 0.02, "roughnessFactor": 0.9}}]
        document["meshes"][0]["primitives"][0]["material"] = 0
        document["nodes"][1]["extras"] = {"asset_kind": "building", "asset_id": spec["asset_id"]}

    payload = trimesh.exchange.gltf.export_glb(scene, include_normals=True, tree_postprocessor=mark)
    OUTPUT.write_bytes(payload)
    result = trimesh.load(OUTPUT, force="scene", process=False)
    assert spec["asset_id"] in result.graph.nodes_geometry and np.allclose(result.bounds, mesh.bounds, atol=2e-5)
    audit = {
        "asset_id": old["id"], "spec_sha256": sha256(spec_data).hexdigest(), "glb_sha256": sha256(payload).hexdigest(),
        "heightfield_sha256": sha256(field_data).hexdigest(),
        "vertices": len(mesh.vertices), "triangles": len(mesh.faces), "bounds_gltf_m": np.round(result.bounds, 3).tolist(),
        "old_footprint_area_m2": round(previous["polygon"].area, 2), "candidate_wall_plan_area_m2": round(outline.area, 2),
        **placement(manifest, field, outline, previous, spec),
    }
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
