# SPDX-License-Identifier: Apache-2.0
"""Export the four Villard Street and two Garden Avenue residential exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import difference, intersection, make_valid, set_precision, union_all
from shapely.affinity import affine_transform
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh


module_path = Path(__file__).with_name("build-chapter-house-exterior-review.py")
loader = spec_from_file_location(module_path.stem, module_path)
chapter = module_from_spec(loader)
loader.loader.exec_module(chapter)

ROOT, SCENE = chapter.ROOT, chapter.SCENE
base, geometry, tools = chapter.base, chapter.geometry, chapter.tools
neighbor, residential = chapter.neighbor, chapter.residential
science, shared, site = chapter.science, chapter.shared, chapter.site
SPEC = ROOT / "data/metadata/villard-garden-exterior-review.json"
DIRECTORY = "villard-garden-exterior-review"
GROUND = "villard-garden-approaches"
GLASS = (76, 105, 112)
LIGHT = (224, 218, 194)
DARK = (70, 72, 67)
CONCRETE = (155, 151, 135)
BRICK = (145, 92, 72)


def roof_sections(parts, outline, wall, floor, row, *, grid=None):
    origin = np.array(row["roof_frame"]["origin_enu_m"])
    along = np.array(row["roof_frame"]["axis"], dtype=float)
    along /= np.linalg.norm(along)
    across = np.array([-along[1], along[0]])
    local = affine_transform(
        outline, [*along, *across, -along @ origin, -across @ origin]
    )
    world = [along[0], across[0], along[1], across[1], *origin]
    candidates = []
    raised = row.get("raised_wall_enu_m")
    wall_levels = [(wall, floor)]
    if raised:
        footprint = set_precision(Polygon(raised), 0.002)
        if not footprint.is_valid or not outline.covers(footprint):
            raise ValueError(f"Raised wall exceeds its roof outline on {row['id']}.")
        wall_levels.append((footprint.difference(wall), row["raised_wall_bottom_z_m"]))

    def polygonal(shape):
        # A fixed-precision overlay requires a single input dimension.
        if grid is not None and shape.geom_type == "GeometryCollection":
            return union_all(list(geometry.sections(shape)), grid_size=grid)
        return shape

    for zone in row["roof_zones"]:
        layer = intersection(local, box(*zone["bounds_m"]), grid_size=grid)
        planes = [chapter.form(form) for form in zone["planes"]]
        for plane in planes:
            area = layer
            for other in planes:
                if plane is not other:
                    area = intersection(
                        area, chapter.half_plane(local.bounds, plane - other), grid_size=grid
                    )
            if area.area > 0.012:
                candidates.append(
                    (polygonal(area), plane, zone.get("roof_color", row["roof_color"]))
                )

    regions = []
    for index, (candidate, plane, color) in enumerate(candidates):
        area = candidate
        # Intersecting gables join where their planes meet. A plane hidden
        # beneath a crossing roof is trimmed from both the cap and the wall.
        for other_index, (other_area, other, _) in enumerate(candidates):
            if index == other_index or not area.intersects(other_area):
                continue
            diff = plane - other
            if np.allclose(diff, 0, atol=1e-7, rtol=0):
                if other_index < index:
                    area = difference(polygonal(area), polygonal(other_area), grid_size=grid)
            else:
                above = chapter.half_plane(local.bounds, diff)
                covered = intersection(other_area, above, grid_size=grid)
                area = difference(polygonal(area), polygonal(covered), grid_size=grid)
        converted = affine_transform(area, world)
        if not converted.is_valid:
            converted = make_valid(converted)
        converted = set_precision(converted, 0.002)
        for region in geometry.sections(converted):
            if region.area < 0.012:
                continue
            roof_slope = plane[0] * along + plane[1] * across
            offset = plane[2] - roof_slope @ origin

            def roof(e, n):
                return roof_slope @ (e, n) + offset

            bottom = min(roof(*p) for p in region.exterior.coords) - 0.25
            cap = geometry.shell(
                region, bottom, roof, row["trim_color"], color
            )
            lower = np.isclose(cap.vertices[:, 1], bottom, atol=1e-6)
            cap.vertices[lower, 1] = (
                cap.vertices[lower][:, (0, 2)] @ (roof_slope * [1, -1]) + offset - 0.15
            )
            parts.append(cap)
            for footprint, level in wall_levels:
                for shell in geometry.sections(region.intersection(footprint)):
                    if shell.area >= 0.012:
                        if raised and min(roof(*p) for p in shell.exterior.coords) - 0.15 <= level:
                            raise ValueError(f"Wall top below its floor on {row['id']}.")
                        parts.append(
                            geometry.shell(
                                shell,
                                level,
                                lambda e, n: roof(e, n) - 0.15,
                                row["wall_color"],
                                row["wall_color"],
                            )
                        )
            regions.append((region, roof_slope, offset))
    coverage = union_all([region for region, _, _ in regions])
    missing = outline.difference(coverage)
    if missing.area > 0.06:
        raise ValueError(
            f"Roof zones leave {missing.area:.3f} m² uncovered for {row['id']} at {missing.bounds}."
        )

    def height_at(point):
        query = Point(point)
        near = [
            (slope, offset) for p, slope, offset in regions if p.distance(query) < 0.012
        ]
        if not near:
            _, slope, offset = min(regions, key=lambda x: x[0].distance(query))
            near = [(slope, offset)]
        return max(slope @ point + offset for slope, offset in near)

    return height_at


def locate_face(edges, near, bearing):
    direction = np.array([np.sin(np.deg2rad(bearing)), np.cos(np.deg2rad(bearing))])
    matched = [
        (a, b)
        for a, b in edges
        if LineString((a, b)).length > 2.1 and neighbor.bearing(a, b) @ direction > 0.96
    ]
    return min(matched, key=lambda edge: LineString(edge).distance(Point(near)))


def fascia_details(parts, edges, row, field, height, entry):
    supports = []
    door_edge = locate_face(edges, entry["position_enu_m"], entry["outward_degrees"])
    authored = {
        locate_face(edges, face["near_enu_m"], face["outward_degrees"]): face
        for face in row["facades"]
    }
    assert len(authored) == len(row["facades"]), row["id"]
    for edge in edges:
        a, b = edge
        length, add, _, plan, _, _ = chapter.setup_face(parts, a, b)
        if length < 1.28:
            continue
        edge_line = LineString(edge)
        z0 = min(geometry.sample_ground(field, *p) for p in edge)
        top = min(height(p) for p in edge) - 0.2
        face = authored.get(edge)
        if face is None and length > 3.3 and top - z0 > 2.35:
            for fraction in np.linspace(0.22, 0.78, max(2, round(length / 4.3))):
                u = fraction * length
                z = geometry.sample_ground(field, *plan(u, 0)) + 0.97
                chapter.prior.window(
                    add,
                    u,
                    min(1.22, length * 0.19),
                    z,
                    min(z + 1.02, top - 0.12),
                    row["trim_color"],
                    GLASS,
                    ribs=1,
                )
        if row["siding"] == "lap" and top > z0 + 0.55:
            for level in np.arange(z0 + 0.42, top, row["siding_spacing_m"]):
                add(
                    0.06,
                    length - 0.06,
                    -0.009,
                    0.013,
                    level,
                    level + 0.016,
                    row["siding_color"],
                )
        if row["siding"] == "vertical":
            for u in np.arange(0.24, length - 0.16, row["siding_spacing_m"]):
                crown = height(plan(u, 0)) - 0.23
                if crown > z0 + 0.46:
                    add(
                        u - 0.014,
                        u + 0.014,
                        -0.006,
                        0.018,
                        z0 + 0.29,
                        crown,
                        row["siding_color"],
                    )
        if face:
            for offset, sill, width, tall, depth, eave, rise in face.get(
                "window_bays", []
            ):
                u = offset * length
                half = width / 2 + 0.5
                add(
                    u - half,
                    u + half,
                    -0.025,
                    depth,
                    sill - 0.56,
                    eave,
                    row["wall_color"],
                )
                add(
                    u - half,
                    u + half,
                    0,
                    depth + 0.068,
                    sill - 0.57,
                    sill - 0.45,
                    row["trim_color"],
                )
                chapter.gabled_canopy(
                    parts,
                    plan,
                    u,
                    half + 0.13,
                    -0.33,
                    depth + 0.14,
                    eave,
                    rise,
                    row["roof_color"],
                    row["trim_color"],
                )

                def on_bay(left, right, inner, outer, low, high, color):
                    add(left, right, depth + inner, depth + outer, low, high, color)

                chapter.prior.window(
                    on_bay,
                    u,
                    width,
                    sill,
                    sill + tall,
                    row["trim_color"],
                    GLASS,
                    ribs=2,
                )
            for offset, sill, width, tall in face.get("windows", []):
                assert min(offset, 1 - offset) * length >= width / 2, (row["id"], face)
                chapter.prior.window(
                    add,
                    offset * length,
                    width,
                    sill,
                    sill + tall,
                    row["trim_color"],
                    GLASS,
                    ribs=2 if width > 1.65 else 1,
                )
            for offset, sill, width, tall in face.get("garage_doors", []):
                u = offset * length
                add(
                    u - width / 2 - 0.075,
                    u + width / 2 + 0.075,
                    0.012,
                    0.061,
                    sill,
                    sill + tall + 0.08,
                    row["trim_color"],
                )
                for z in np.linspace(sill, sill + tall, 6)[:-1]:
                    add(
                        u - width / 2,
                        u + width / 2,
                        0.04,
                        0.081,
                        z + 0.017,
                        z + tall / 5,
                        row["garage_color"],
                    )
            for offset, sill, width, depth in face.get("galleries", []):
                u = offset * length
                add(
                    u - width / 2,
                    u + width / 2,
                    -0.02,
                    depth,
                    sill - 0.17,
                    sill,
                    row["trim_color"],
                )
                neighbor.railing(add, u - width / 2, u + width / 2, depth, sill, DARK)
                for p in (u - width / 2, u + width / 2):
                    add(p - 0.035, p + 0.035, 0, depth, sill + 0.87, sill + 0.94, DARK)
            for start, depth, foot, rise, reverse in face.get("stairs", []):
                neighbor.side_stair(add, start * length, depth, foot, rise, reverse)
        if edge != door_edge:
            continue
        u = edge_line.project(Point(entry["position_enu_m"]))
        sill = entry["threshold_z_m"]
        neighbor.door(add, u, sill, row["door_color"])
        if "porch" not in row:
            continue
        half_width, projection, rise, post = row["porch"]
        z = sill + 2.42
        if rise > 0:
            chapter.gabled_canopy(
                parts,
                plan,
                u,
                half_width,
                -0.09,
                projection,
                z,
                rise,
                row["roof_color"],
                row["trim_color"],
            )
        else:
            add(
                u - half_width,
                u + half_width,
                -0.02,
                projection,
                z,
                z + 0.16,
                row["trim_color"],
            )
        if post:
            for offset in (-half_width + 0.09, half_width - 0.09):
                x = u + offset
                foot = geometry.sample_ground(field, *plan(x, projection - 0.13))
                add(
                    x - 0.053,
                    x + 0.053,
                    projection - 0.19,
                    projection - 0.085,
                    foot,
                    z,
                    row["trim_color"],
                )
                supports.append(
                    Point(plan(x, projection - 0.14)).buffer(0.080, quad_segs=2)
                )
    for e, n, width, depth, peak in row.get("chimneys", []):
        height_z = height((e, n))
        plan = box(e - width / 2, n - depth / 2, e + width / 2, n + depth / 2)
        parts.append(
            geometry.shell(plan, height_z - 0.40, lambda e, n: peak, BRICK, CONCRETE)
        )
    for e, n, width, depth in row.get("skylights", []):
        for inset, thickness, color in ((0, 0.09, LIGHT), (0.045, 0.115, GLASS)):
            plan = box(
                e - width / 2 + inset,
                n - depth / 2 + inset,
                e + width / 2 - inset,
                n + depth / 2 - inset,
            )
            bottom = min(height(p) for p in plan.exterior.coords) - 0.03
            parts.append(
                geometry.shell(
                    plan, bottom, lambda e, n: height((e, n)) + thickness, color, color
                )
            )
    return supports


def build(spec, manifest, config, field, graph):
    models, records, ground, plans, supports, entries = {}, [], [], [], [], []
    for row in spec["models"]:
        outline = orient(set_precision(Polygon(row["outline"]), 0.002))
        wall = orient(outline.buffer(-row["eave_projection_m"], join_style="mitre"))
        floor, _ = science.earlier.fit_base(field, outline)
        pieces = []
        height = roof_sections(pieces, outline, wall, floor, row)
        edges = [tuple(map(tuple, edge)) for edge in shared.face_edges(wall)]
        gate = residential.entrance(ground, field, edges, row["entrance"])
        attached = fascia_details(pieces, edges, row, field, height, gate)
        mesh = trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.000012))
        id = row["id"]
        models[id] = science.ordered_mesh(mesh)
        plans.append(wall)
        supports.extend(attached)
        entries.append(gate)
        records.append(
            {
                "id": id,
                "name": row["name"],
                "street_address": row["street_address"],
                "footprint_enu_m": base.ring(wall),
                "area_m2": round(wall.area, 3),
                "support_collision_enu_m": [base.ring(p) for p in attached],
                "entrances": [gate],
                "base_z_m": round(floor, 4),
                "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
            }
        )
    for a, b in spec["source_split"].items():
        index = {row["id"]: i for i, row in enumerate(records)}
        assert plans[index[a]].distance(plans[index[b]]) > 0.75, (a, b)
    retired = set(spec["source_split"].values())
    former = union_all(
        [
            Polygon(row["footprint_enu_m"]).buffer(0)
            for row in manifest["buildings"]
            if row["id"] in retired
        ]
    )
    count, clearance = chapter.prior.nearby.shared.graduate.shared.check_routes(
        plans, supports, entries, former, manifest, graph, config, set(models)
    )
    ground_mesh = science.ordered_mesh(trimesh.util.concatenate(ground))
    return models, records, ground_mesh, count, clearance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--spec", type=Path, default=SPEC)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_bytes())
    manifest_path, config_path = SCENE / "manifest.json", SCENE / "presentation.json"
    manifest, config = [
        json.loads(path.read_bytes()) for path in (manifest_path, config_path)
    ]
    terrain = SCENE / manifest["heightfield_url"]
    if (
        tools.digest(manifest_path) != spec["source_manifest_sha256"]
        or tools.digest(terrain) != spec["source_heightfield_sha256"]
    ):
        raise ValueError(
            "The Villard and Garden exteriors require the registered scene and terrain."
        )
    models, records, ground, edges, clearance = build(
        spec,
        manifest,
        config,
        json.loads(terrain.read_bytes()),
        json.loads((SCENE / "navigation.json").read_bytes()),
    )
    appearances = json.loads(
        (ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    patches = shared.frohnmayer.source_removals(
        {"absorbed_batches": spec["source_ranges"]}, config, appearances
    )
    output = args.stage or SCENE / DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    model, descriptor = output / "site.glb", output / "site.json"
    site.memorial.gerlinger.export(
        model, models, ground, GROUND, "villard-garden-paving"
    )
    package = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{DIRECTORY}/site.glb",
        "sha256": tools.digest(model),
        "buildings": records,
        "absorbed_ids": [],
        "split_buildings": spec["source_split"],
        "batch_removals": patches,
    }
    descriptor.write_text(
        json.dumps(package, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    if args.stage is None:
        config["villard_garden_exterior_site"] = {
            "url": f"{DIRECTORY}/site.json",
            "sha256": tools.digest(descriptor),
        }
        config_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf8",
            newline="\n",
        )
    audit = {
        "buildings": records,
        "route_edges": edges,
        "nearest_route_m": round(clearance, 4),
        "triangles": {key: len(mesh.faces) for key, mesh in models.items()},
        "batch_removals": patches,
        "split_buildings": spec["source_split"],
        "glb_sha256": package["sha256"],
        "descriptor_sha256": tools.digest(descriptor),
    }
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(
        {
            k: audit[k]
            for k in ("route_edges", "nearest_route_m", "triangles", "glb_sha256")
        }
    )


if __name__ == "__main__":
    main()
